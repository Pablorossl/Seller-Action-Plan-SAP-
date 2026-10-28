"""Sólo PostgreSQL: conexiones independientes y transacciones reales."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless
from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import connection, connections, transaction, OperationalError
from django.test import TransactionTestCase, Client

from action_plans import tests as phase1
from action_plans.models import ImprovementPlan, PlanAction, PlanReview
from action_plans.services import close_plan, evaluate_plan
from action_plans.test_api import PlanApiTests


@skipUnless(connection.vendor == "postgresql", "Requiere PostgreSQL; SQLite no acredita bloqueos de fila.")
class ConcurrencyTests(TransactionTestCase):
    plan = phase1.PlanTests.plan
    action = phase1.PlanTests.action
    ready_plan = phase1.PlanTests.ready_plan
    review = phase1.PlanTests.review
    payload = PlanApiTests.payload

    def setUp(self):
        phase1.PlanTests.setUp(self)
        phase1.PlanTests.setUpTestData.__func__(type(self))

    def concurrent(self, *operations):
        barrier = Barrier(len(operations))
        def run(operation):
            connections.close_all()
            try:
                barrier.wait(timeout=10)
                return operation()
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=len(operations)) as pool:
            futures = [pool.submit(run, operation) for operation in operations]
            return [future.result(timeout=20) for future in futures]

    def test_same_plan_cannot_be_closed_twice(self):
        plan, _, _ = self.ready_plan()
        def close():
            try:
                actor = get_user_model().objects.get(pk=self.agent.pk)
                close_plan(plan_id=plan.pk, actor=actor, notes="Cierre concurrente ficticio")
                return "closed"
            except ValidationError:
                return "rejected"
        self.assertCountEqual(self.concurrent(close, close), ["closed", "rejected"])
        plan.refresh_from_db()
        self.assertEqual(plan.status, "closed")
        self.assertEqual(plan.revision, 3)
        self.assertTrue(plan.closure_evaluation)

    def test_simultaneous_creation_retries_store_only_one_plan_and_action(self):
        clients = [Client(), Client()]
        for client in clients:
            client.force_login(self.agent)
        key = str(uuid4())
        def create(client):
            return lambda: client.post("/api/plans/", self.payload(), content_type="application/json", HTTP_IDEMPOTENCY_KEY=key).status_code
        self.assertCountEqual(self.concurrent(*(create(client) for client in clients)), [201, 200])
        self.assertEqual(ImprovementPlan.objects.count(), 1)
        plan = ImprovementPlan.objects.get()
        key = str(uuid4())
        def action(client):
            return lambda: client.post(f"/api/plans/{plan.pk}/actions/", dict(description="Una sola acción", kind="corrective", responsible="Equipo", due_date="2026-10-23"), content_type="application/json", HTTP_IDEMPOTENCY_KEY=key).status_code
        self.assertCountEqual(self.concurrent(*(action(client) for client in clients)), [201, 200])
        self.assertEqual(PlanAction.objects.count(), 1)

    def test_simultaneous_plan_edits_reject_stale_browser_revision(self):
        plan = self.plan()
        clients = [Client(), Client()]
        for client in clients:
            client.force_login(self.agent)
        def edit(client, title):
            return lambda: client.patch(f"/api/plans/{plan.pk}/", {"title": title, "revision": plan.revision}, content_type="application/json").status_code
        self.assertCountEqual(self.concurrent(edit(clients[0], "Uno"), edit(clients[1], "Dos")), [200, 409])
        plan.refresh_from_db()
        self.assertEqual(plan.revision, 2)

    def test_distinct_reviews_are_both_preserved(self):
        plan, metric, _ = self.ready_plan()
        def first():
            return self.review(metric).pk
        def second():
            return self.review(metric, period_start="2026-09-01", period_end="2026-09-30", reviewed_on="2026-10-01", value=3).pk
        ids = self.concurrent(first, second)
        self.assertEqual(len(set(ids)), 2)
        self.assertEqual(PlanReview.objects.count(), 2)
        self.assertEqual(evaluate_plan(plan)["result"], "achieved")

    def test_repeated_review_is_stored_once(self):
        _, metric, _ = self.ready_plan()
        def review():
            try:
                self.review(metric)
                return "created"
            except ValidationError:
                return "rejected"
        self.assertCountEqual(self.concurrent(review, review), ["created", "rejected"])
        self.assertEqual(PlanReview.objects.count(), 1)

    def test_stale_action_cannot_overwrite_a_concurrent_change(self):
        _, _, action = self.ready_plan()
        first = PlanAction.objects.get(pk=action.pk)
        second = PlanAction.objects.get(pk=action.pk)
        def edit(instance, text):
            def operation():
                instance.notes = text
                try:
                    instance.save()
                    return "saved"
                except ValidationError:
                    return "rejected"
            return operation
        self.assertCountEqual(self.concurrent(edit(first, "Uno"), edit(second, "Dos")), ["saved", "rejected"])
        action.refresh_from_db()
        self.assertEqual(action.revision, 2)

    def test_review_racing_with_close_matches_the_closure_snapshot(self):
        plan, metric, _ = self.ready_plan()
        def review():
            try:
                self.review(metric)
                return "created"
            except ValidationError:
                return "rejected"
        def close():
            actor = get_user_model().objects.get(pk=self.agent.pk)
            close_plan(plan_id=plan.pk, actor=actor, notes="Cierre concurrente")
            return "closed"
        reviewed, closed = self.concurrent(review, close)
        plan.refresh_from_db()
        self.assertEqual(closed, "closed")
        self.assertEqual(PlanReview.objects.count(), int(reviewed == "created"))
        self.assertEqual(plan.closure_evaluation, evaluate_plan(plan))

    def test_lock_is_real_and_reassignment_revokes_next_write(self):
        plan, _, _ = self.ready_plan()
        def try_lock():
            connections.close_all()
            try:
                with transaction.atomic():
                    ImprovementPlan.objects.select_for_update(nowait=True).get(pk=plan.pk)
            except OperationalError:
                return "locked"
            finally:
                connections.close_all()
            return "unlocked"
        with transaction.atomic():
            ImprovementPlan.objects.select_for_update().get(pk=plan.pk)
            with ThreadPoolExecutor(max_workers=1) as pool:
                self.assertEqual(pool.submit(try_lock).result(timeout=10), "locked")
        self.seller.owner = self.other
        self.seller.save()
        client = Client()
        client.force_login(self.agent)
        self.assertEqual(client.patch(f"/api/plans/{plan.pk}/", {"title": "No autorizado"}, content_type="application/json").status_code, 404)
