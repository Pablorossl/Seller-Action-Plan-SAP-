"""Regresiones de concurrencia lógica, reintentos y consultas de la interfaz."""
from io import StringIO
from uuid import uuid4

from django.core.management import call_command, CommandError
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext

from action_plans import tests as phase1
from action_plans.test_api import PlanApiTests
from action_plans.models import ImprovementPlan, PlanAction, PlanMetric, PlanReview
from action_plans.concurrency import RevisionConflict
from sellers.models import Seller
from quality.models import QualityMetric


class ReliabilityTests(TestCase):
    setUpTestData = classmethod(phase1.PlanTests.setUpTestData.__func__)
    setUp = phase1.PlanTests.setUp
    plan = phase1.PlanTests.plan
    action = phase1.PlanTests.action
    ready_plan = phase1.PlanTests.ready_plan
    review = phase1.PlanTests.review
    payload = PlanApiTests.payload

    def test_stale_instances_cannot_overwrite_plan_action_or_target(self):
        plan = self.plan()
        metric = PlanMetric.objects.create(plan=plan, baseline=self.baseline, target_value=3)
        action = self.action(plan)
        for obj, field, first, second in [(plan, "title", "Primera edición", "Segunda edición"),
                (action, "notes", "Primera evidencia", "Otra evidencia"), (metric, "target_value", 2, 1)]:
            stale = type(obj).objects.get(pk=obj.pk)
            setattr(obj, field, first)
            obj.save()
            setattr(stale, field, second)
            with self.assertRaises(RevisionConflict):
                stale.save()
            current = type(obj).objects.get(pk=obj.pk)
            self.assertEqual(getattr(current, field), first)
            self.assertEqual(current.revision, 2)

    def test_api_revision_conflict_and_recovery(self):
        plan, metric, action = self.ready_plan()
        self.client.force_login(self.agent)
        for path, payload, revision in [
            (f"/api/plans/{plan.pk}/", {"title": "Editado"}, plan.revision),
            (f"/api/plans/{plan.pk}/actions/{action.pk}/", {"notes": "Editado"}, action.revision),
        ]:
            response = self.client.patch(path, payload | {"revision": revision}, content_type="application/json")
            self.assertEqual(response.status_code, 200, response.content)
            stale = self.client.patch(path, payload | {"revision": revision}, content_type="application/json")
            self.assertEqual(stale.status_code, 409)
        response = self.client.post(f"/api/plans/{plan.pk}/close/", {"notes": "Cerrar", "confirm": True, "revision": plan.revision}, content_type="application/json")
        self.assertEqual(response.status_code, 409)
        plan.refresh_from_db()
        self.assertEqual(plan.status, "in_progress")

    def test_creation_retries_do_not_duplicate_and_changed_payload_conflicts(self):
        self.client.force_login(self.agent)
        key = str(uuid4())
        path = "/api/plans/"
        created = self.client.post(path, self.payload(), content_type="application/json", HTTP_IDEMPOTENCY_KEY=key)
        self.assertEqual(created.status_code, 201, created.content)
        repeated = self.client.post(path, self.payload(), content_type="application/json", HTTP_IDEMPOTENCY_KEY=key)
        self.assertEqual(repeated.status_code, 200, repeated.content)
        self.assertEqual(created.json()["id"], repeated.json()["id"])
        self.assertEqual(ImprovementPlan.objects.count(), 1)
        conflict = self.client.post(path, self.payload(title="Otro"), content_type="application/json", HTTP_IDEMPOTENCY_KEY=key)
        self.assertEqual(conflict.status_code, 409)
        path = f"/api/plans/{created.json()['id']}/actions/"
        data = dict(description="Acción", kind="corrective", responsible="Equipo ficticio", due_date="2026-10-23")
        key = str(uuid4())
        for expected in (201, 200):
            response = self.client.post(path, data, content_type="application/json", HTTP_IDEMPOTENCY_KEY=key)
            self.assertEqual(response.status_code, expected, response.content)
        self.assertEqual(PlanAction.objects.count(), 1)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(path, data, content_type="application/json", HTTP_IDEMPOTENCY_KEY=key).status_code, 404)

    def test_bad_creation_does_not_consume_idempotency_key(self):
        self.client.force_login(self.agent)
        key = str(uuid4())
        invalid = self.payload(metrics=[{"baseline": self.baseline.pk, "target_value": 8}])
        self.assertEqual(self.client.post("/api/plans/", invalid, content_type="application/json", HTTP_IDEMPOTENCY_KEY=key).status_code, 400)
        self.assertEqual(ImprovementPlan.objects.count(), 0)
        self.assertEqual(self.client.post("/api/plans/", self.payload(), content_type="application/json", HTTP_IDEMPOTENCY_KEY=key).status_code, 201)

    def test_public_demo_is_explicit_repeatable_and_has_no_admin(self):
        self.agent.is_staff = False
        self.agent.save()
        with override_settings(DEBUG=False, SAP_DEMO_MODE=False), self.assertRaises(CommandError):
            call_command("seed_evaluation_demo", owner=self.agent.username, confirm_fictitious=True)
        with override_settings(DEBUG=False, SAP_DEMO_MODE=True):
            with self.assertRaises(CommandError):
                call_command("seed_evaluation_demo", owner=self.agent.username)
            call_command("seed_evaluation_demo", owner=self.agent.username, confirm_fictitious=True, stdout=StringIO())
            models = (Seller, QualityMetric, ImprovementPlan, PlanAction, PlanMetric, PlanReview)
            counts = [model.objects.count() for model in models]
            call_command("seed_evaluation_demo", owner=self.agent.username, confirm_fictitious=True, stdout=StringIO())
            self.assertEqual(counts, [model.objects.count() for model in models])
        results = set(ImprovementPlan.objects.filter(status="closed").values_list("closure_evaluation__result", flat=True))
        self.assertEqual(results, {"achieved", "not_achieved"})
        self.agent.refresh_from_db()
        self.assertFalse(self.agent.is_staff or self.agent.is_superuser)
        with self.assertRaises(CommandError):
            call_command("create_demo_agent", username=self.agent.username, stdout=StringIO())

    def test_dashboard_and_directory_have_bounded_query_counts(self):
        self.client.force_login(self.agent)
        self.ready_plan()
        paths = ("/api/overview/", "/api/sellers/", "/api/plans/")
        def counts():
            results = []
            for path in paths:
                with CaptureQueriesContext(connection) as queries:
                    response = self.client.get(path)
                    self.assertEqual(response.status_code, 200, response.content)
                results.append(len(queries))
            return results
        before = counts()
        # Fixtures conocidas: bulk_create se limita a esta prueba de volumen.
        sellers = Seller.objects.bulk_create([Seller(name=f"Ficticio {i}", reference=f"LOAD-{i}", owner=self.agent) for i in range(120)])
        QualityMetric.objects.bulk_create([QualityMetric(seller=s, policy=self.policy, channel="demo-es", period_start="2026-07-01", period_end="2026-07-31", order_count=100, value=6) for s in sellers])
        after = counts()
        self.assertEqual(before, after)
        self.assertLess(max(after), 30)
