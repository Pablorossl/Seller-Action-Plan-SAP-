from datetime import date, datetime, timedelta, timezone as datetime_timezone
from decimal import Decimal
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from action_plans.models import ActionStatus, ImprovementPlan, PlanAction, PlanMetric, PlanReview, PlanStatus
from action_plans.services import close_plan, evaluate_metric, evaluate_plan, plans_with_history, visible_plans
from quality.models import QualityMetric, ThresholdPolicy
from sellers.models import AGENT_GROUP, Seller


class PlanTests(TestCase):
    def setUp(self):
        # Los datos ficticios son de 2026; el test no depende del día de ejecución.
        clock = patch("django.utils.timezone.now", return_value=datetime(2026, 10, 23, 12, tzinfo=datetime_timezone.utc))
        clock.start()
        self.addCleanup(clock.stop)

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.agent = User.objects.create_user(username="plan_agent")
        cls.other = User.objects.create_user(username="other_agent")
        cls.outsider = User.objects.create_user(username="outsider", is_staff=True)
        cls.admin = User.objects.create_superuser(username="admin", password="test-only-password")
        for user in (cls.agent, cls.other):
            call_command("configure_plan_agent", username=user.username, stdout=StringIO())
        cls.agent.refresh_from_db()
        cls.other.refresh_from_db()
        cls.seller = Seller.objects.create(name="Tienda Ficticia", reference="PLAN-1", owner=cls.agent)
        cls.hidden = Seller.objects.create(name="Tienda Ajena Secreta", reference="PLAN-2", owner=cls.other)
        cls.policy = ThresholdPolicy.objects.create(code="incidents", unit="percent", operator="gte", alarm=4, suspension=5)
        cls.baseline = QualityMetric.objects.create(seller=cls.seller, policy=cls.policy, channel="demo-es",
            period_start=date(2026, 7, 1), period_end=date(2026, 7, 31), order_count=100, value=Decimal("6"))

    def plan(self, **changes):
        data = dict(seller=self.seller, title="Mejora de envíos", problem="Incidencias del 6%.",
            period_start=date(2026, 7, 1), period_end=date(2026, 7, 31), root_cause="Embalaje insuficiente.",
            evidence="Muestra ficticia de 100 pedidos.", objective="Reducir las incidencias al 3%.",
            responsible=self.agent, created_by=self.agent, due_date=date(2026, 12, 31))
        return ImprovementPlan.objects.create(**(data | changes))

    def action(self, plan, **changes):
        return PlanAction.objects.create(**(dict(plan=plan, description="Revisar todos los embalajes.", kind="corrective",
            responsible="Equipo ficticio de logística", due_date=date(2026, 8, 20)) | changes))

    def ready_plan(self):
        plan = self.plan()
        metric = PlanMetric.objects.create(plan=plan, baseline=self.baseline, target_value=Decimal("3"))
        action = self.action(plan)
        plan.status = PlanStatus.IN_PROGRESS
        plan.save()
        return plan, metric, action

    def review(self, metric, **changes):
        return PlanReview.objects.create(**(dict(plan_metric=metric, recorded_by=self.agent, reviewed_on=date(2026, 9, 1),
            value=Decimal("4.5"), period_start=date(2026, 8, 1), period_end=date(2026, 8, 31), order_count=100,
            comments="Disminuyen las incidencias en la muestra ficticia.", assessment="on_track") | changes))

    def test_valid_plan_persists_and_seller_can_have_several_plans(self):
        plan = self.plan()
        plan.refresh_from_db()
        self.assertEqual(plan.seller, self.seller)
        self.assertEqual(plan.status, PlanStatus.DRAFT)
        self.plan(title="Segundo plan")
        self.assertEqual(self.seller.plans.count(), 2)

    def test_invalid_plan_data_and_missing_foreign_keys(self):
        cases = [dict(title=""), dict(root_cause=""), dict(seller_id=999999, seller=None),
            dict(status="unknown"), dict(period_end=date(2026, 6, 1)), dict(due_date=date(2026, 7, 1)),
            dict(next_review_on=date(2026, 6, 1)), dict(responsible_id=99999, responsible=None)]
        for changes in cases:
            # No se pasa a la vez la instancia y su id a Django.
            data = dict(seller=self.seller, title="Plan", problem="Problema", period_start=date(2026, 7, 1),
                period_end=date(2026, 7, 31), root_cause="Causa", evidence="Evidencia", objective="Objetivo",
                responsible=self.agent, created_by=self.agent, due_date=date(2026, 12, 31))
            data.update(changes)
            if "seller_id" in changes:
                data.pop("seller")
            if "responsible_id" in changes:
                data.pop("responsible")
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                ImprovementPlan.objects.create(**data)

    def test_activation_requires_metrics_and_actions_and_valid_transitions(self):
        plan = self.plan()
        plan.status = PlanStatus.IN_PROGRESS
        with self.assertRaises(ValidationError):
            plan.save()
        PlanMetric.objects.create(plan=ImprovementPlan.objects.get(pk=plan.pk), baseline=self.baseline, target_value=3)
        with self.assertRaises(ValidationError):
            plan.save()
        self.action(ImprovementPlan.objects.get(pk=plan.pk))
        plan.save()
        plan.status = PlanStatus.DRAFT
        with self.assertRaises(ValidationError):
            plan.save()
        plan.status = PlanStatus.IN_REVIEW
        plan.save()
        self.assertTrue(plan.needs_review)

    def test_several_actions_completion_and_deadlines(self):
        plan, metric, action = self.ready_plan()
        preventive = self.action(plan, kind="preventive", description="Auditar las recogidas.")
        self.assertEqual(plan.actions.count(), 2)
        self.assertTrue(action.is_overdue)
        action.status = ActionStatus.COMPLETED
        with self.assertRaises(ValidationError):
            action.save()
        action.completed_on = date(2026, 8, 20)
        action.evidence = "Lista ficticia de comprobación."
        action.save()
        action.refresh_from_db()
        self.assertFalse(action.is_overdue)
        self.assertTrue(preventive.is_overdue)
        # Completar tareas no aporta una medición del objetivo.
        self.assertEqual(evaluate_plan(plan)["result"], "not_evaluable")
        action.status = ActionStatus.PENDING
        action.completed_on = None
        with self.assertRaises(ValidationError):
            action.save()

    def test_action_boundary_dates_and_cancelled_actions(self):
        plan = self.plan()
        today = timezone.localdate()
        action = self.action(plan, due_date=today)
        self.assertFalse(action.is_overdue)
        action.due_date = today - timedelta(days=1)
        self.assertTrue(action.is_overdue)
        action.status = ActionStatus.CANCELLED
        action.save()
        self.assertFalse(action.is_overdue)
        for changes in [dict(due_date=date(2026, 7, 1)), dict(due_date=date(2027, 1, 1)),
            dict(status="invented"), dict(completed_on=today),
            dict(status=ActionStatus.COMPLETED, completed_on=today + timedelta(days=1), evidence="Prueba")]:
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                self.action(plan, **changes)

    def test_successive_reviews_keep_history_and_latest_measurement(self):
        plan, metric, action = self.ready_plan()
        first = self.review(metric)
        result = evaluate_metric(metric)
        self.assertTrue(result["improved"])
        self.assertFalse(result["achieved"])
        second = self.review(metric, period_start=date(2026, 9, 1), period_end=date(2026, 9, 30),
            reviewed_on=date(2026, 10, 1), value=Decimal("3"))
        self.assertEqual(metric.reviews.count(), 2)
        first.refresh_from_db()
        self.assertEqual(first.value, Decimal("4.5"))
        self.assertTrue(evaluate_metric(metric)["achieved"])
        self.assertEqual(evaluate_metric(metric)["review_id"], second.pk)
        first.value = Decimal("2")
        with self.assertRaises(ValidationError):
            first.save()
        # Insertar después una medición anterior no cambia el resultado actual.
        self.review(metric, period_start=date(2026, 8, 2), period_end=date(2026, 9, 1), reviewed_on=date(2026, 9, 2), value=5)
        self.assertEqual(evaluate_metric(metric)["review_id"], second.pk)

    def test_reviews_validate_ranges_dates_duplicates_and_missing_fk(self):
        plan, metric, action = self.ready_plan()
        for changes in [dict(value=Decimal("-1")), dict(value=Decimal("101")),
            dict(period_start=date(2026, 9, 1)), dict(reviewed_on=date(2026, 8, 1)),
            dict(period_end=date(2026, 7, 31)), dict(reviewed_on=timezone.localdate() + timedelta(days=1)),
            dict(plan_metric=None, plan_metric_id=99999)]:
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                self.review(metric, **changes)
        self.review(metric)
        with self.assertRaises(ValidationError):
            self.review(metric)

    def test_missing_data_insufficient_volume_and_nonmonthly_periods_are_not_evaluable(self):
        for changes in [dict(value=None), dict(order_count=None), dict(order_count=29),
            dict(period_start=date(2026, 8, 25))]:
            with self.subTest(changes=changes):
                plan, metric, action = self.ready_plan()
                self.review(metric, **changes)
                result = evaluate_metric(metric)
                self.assertIsNone(result["achieved"])
                self.assertIsNone(result["improved"])
                self.assertEqual(evaluate_plan(plan)["result"], "not_evaluable")

    def test_increasing_and_decreasing_indicators_and_multiple_metrics(self):
        plan, incidents, action = self.ready_plan()
        for code, unit, operator, alarm, suspension, initial, target, current in [
            ("tracking", "percent", "lt", 91, 90, 85, 95, 95),
            ("response_hours", "hours", "gte", 20, 24, 26, 15, 15),
            ("nps", "percent", "lt", 65, None, -10, 65, 65),
        ]:
            policy = ThresholdPolicy.objects.create(code=code, unit=unit, operator=operator, alarm=alarm,
                suspension=suspension, is_mqc=suspension is not None, minimum_orders=30 if suspension else 0)
            baseline = QualityMetric.objects.create(seller=self.seller, policy=policy, channel="demo-es",
                period_start=plan.period_start, period_end=plan.period_end, order_count=100, value=initial)
            metric = PlanMetric.objects.create(plan=plan, baseline=baseline, target_value=target)
            self.review(metric, value=current, order_count=30)
            self.assertTrue(evaluate_metric(metric)["improved"])
            self.assertTrue(evaluate_metric(metric)["achieved"])
        self.review(incidents, value=3)
        self.assertEqual(evaluate_plan(plan)["result"], "achieved")
        self.assertEqual(len(evaluate_plan(plan)["metrics"]), 4)

    def test_target_direction_duplicate_seller_period_and_parent_integrity(self):
        plan = self.plan()
        for target in [6, 7, -1, 101]:
            with self.subTest(target=target), self.assertRaises(ValidationError):
                PlanMetric.objects.create(plan=plan, baseline=self.baseline, target_value=target)
        metric = PlanMetric.objects.create(plan=plan, baseline=self.baseline, target_value=3)
        with self.assertRaises(ValidationError):
            PlanMetric.objects.create(plan=plan, baseline=self.baseline, target_value=2)
        other = self.plan(seller=self.hidden)
        with self.assertRaises(ValidationError):
            PlanMetric.objects.create(plan=other, baseline=self.baseline, target_value=3)
        metric.plan = other
        with self.assertRaises(ValidationError):
            metric.save()
        action = self.action(plan)
        action.plan = other
        with self.assertRaises(ValidationError):
            action.save()
        plan.seller = self.hidden
        with self.assertRaises(ValidationError):
            plan.save()

    def test_baseline_and_target_are_preserved_after_reviews(self):
        plan, metric, action = self.ready_plan()
        self.review(metric)
        metric.target_value = Decimal("2")
        with self.assertRaises(ValidationError):
            metric.save()
        self.baseline.value = Decimal("8")
        with self.assertRaises(ValidationError):
            self.baseline.save()

    def test_plan_deadline_changes_respect_existing_actions(self):
        plan, metric, action = self.ready_plan()
        plan.due_date = date(2026, 8, 1)
        with self.assertRaises(ValidationError):
            plan.save()

    def test_close_records_measured_result_and_preserves_history(self):
        plan, metric, action = self.ready_plan()
        self.review(metric)
        self.review(metric, period_start=date(2026, 9, 1), period_end=date(2026, 9, 30),
            reviewed_on=date(2026, 10, 1), value=3)
        closed = close_plan(plan_id=plan.pk, actor=self.agent, notes="Objetivo alcanzado; se mantiene el control preventivo.")
        closed.refresh_from_db()
        self.assertEqual(closed.status, PlanStatus.CLOSED)
        self.assertIsNotNone(closed.closed_at)
        self.assertEqual(closed.closure_evaluation["result"], "achieved")
        self.assertEqual(metric.reviews.count(), 2)
        self.assertEqual(closed.closure_evaluation["actions"]["pending"], 1)
        self.assertFalse(closed.needs_review)
        for obj in [closed, action, metric]:
            with self.subTest(model=type(obj).__name__), self.assertRaises(ValidationError):
                obj.save()
        with self.assertRaises(ValidationError):
            self.review(metric, period_end=date(2026, 9, 30), reviewed_on=date(2026, 10, 1))

    def test_close_without_achieving_goal_requires_reason(self):
        plan, metric, action = self.ready_plan()
        self.review(metric)
        with self.assertRaises(ValidationError):
            close_plan(plan_id=plan.pk, actor=self.agent, notes=" ")
        plan.refresh_from_db()
        self.assertEqual(plan.status, PlanStatus.IN_PROGRESS)
        closed = close_plan(plan_id=plan.pk, actor=self.agent, notes="Mejora parcial; se acuerda un nuevo plan.")
        self.assertEqual(closed.closure_evaluation["result"], "not_achieved")

    def test_cancel_draft_and_close_without_measurement(self):
        plan = self.plan()
        closed = close_plan(plan_id=plan.pk, actor=self.agent, status=PlanStatus.CANCELLED, notes="Registro duplicado justificado.")
        self.assertEqual(closed.closure_evaluation["result"], "not_evaluable")
        plan, metric, action = self.ready_plan()
        closed = close_plan(plan_id=plan.pk, actor=self.agent, notes="Sin datos al terminar el seguimiento.")
        self.assertEqual(closed.closure_evaluation["result"], "not_evaluable")

    def test_service_requires_close_permission_and_seller_ownership(self):
        plan, metric, action = self.ready_plan()
        with self.assertRaises(ImprovementPlan.DoesNotExist):
            close_plan(plan_id=plan.pk, actor=self.other, notes="Intento ajeno")
        with self.assertRaises(PermissionDenied):
            close_plan(plan_id=plan.pk, actor=self.outsider, notes="Sin permiso")
        self.agent.user_permissions.remove(Permission.objects.get(codename="close_improvementplan"))
        actor = get_user_model().objects.get(pk=self.agent.pk)
        with self.assertRaises(PermissionDenied):
            close_plan(plan_id=plan.pk, actor=actor, notes="Sin permiso de cierre")

    def test_review_dates_and_result_prefetch_avoid_n_plus_one(self):
        plan, metric, action = self.ready_plan()
        self.review(metric)
        plan.next_review_on = timezone.localdate()
        plan.save()
        with self.assertNumQueries(4):
            plans = list(plans_with_history(ImprovementPlan.objects.filter(pk=plan.pk)))
            self.assertTrue(plans[0].needs_review)
            self.assertEqual(evaluate_plan(plans[0])["result"], "not_achieved")

    def test_database_constraints_and_protected_references(self):
        from django.db.models.deletion import ProtectedError

        plan, metric, action = self.ready_plan()
        self.review(metric)
        for model, pk, changes in [(ImprovementPlan, plan.pk, {"status": "unknown"}),
            (ImprovementPlan, plan.pk, {"status": "closed"}), (PlanAction, action.pk, {"status": "completed"}),
            (PlanReview, metric.reviews.first().pk, {"period_end": date(2026, 7, 1)})]:
            with self.subTest(model=model.__name__), self.assertRaises(IntegrityError), transaction.atomic():
                model.objects.filter(pk=pk).update(**changes)
        for obj in [self.seller, plan, metric, self.baseline]:
            with self.subTest(obj=type(obj).__name__), self.assertRaises(ProtectedError):
                obj.delete()

    def test_admin_scopes_lists_details_and_foreign_key_choices(self):
        plan, metric, action = self.ready_plan()
        review = self.review(metric)
        self.client.force_login(self.other)
        for model, obj in [("improvementplan", plan), ("planmetric", metric), ("planaction", action), ("planreview", review)]:
            response = self.client.get(reverse(f"admin:action_plans_{model}_changelist"))
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, plan.title)
            response = self.client.get(reverse(f"admin:action_plans_{model}_change", args=[obj.pk]))
            self.assertNotEqual(response.status_code, 200)
        self.assertEqual(self.client.post(reverse("admin:action_plans_improvementplan_close", args=[plan.pk]),
            {"status": "closed", "notes": "Ajeno"}).status_code, 404)
        response = self.client.get(reverse("admin:action_plans_planmetric_add"))
        self.assertNotContains(response, plan.title)
        self.client.force_login(self.agent)
        response = self.client.get(reverse("admin:action_plans_improvementplan_changelist"))
        self.assertContains(response, plan.title)
        self.assertNotContains(response, self.hidden.name)

    def test_admin_denies_anonymous_wrong_role_and_staff_without_permissions(self):
        url = reverse("admin:action_plans_improvementplan_changelist")
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.force_login(self.outsider)
        self.assertEqual(self.client.get(url).status_code, 403)
        self.outsider.user_permissions.add(*Permission.objects.filter(content_type__app_label="action_plans"))
        self.assertEqual(self.client.get(url).status_code, 403)
        no_permissions = get_user_model().objects.create_user(username="only_staff", is_staff=True)
        no_permissions.groups.add(Group.objects.get(name=AGENT_GROUP))
        self.client.force_login(no_permissions)
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_full_acceptance_flow_through_admin_forms(self):
        self.client.force_login(self.agent)
        response = self.client.post(reverse("admin:action_plans_improvementplan_add"), {
            "seller": self.seller.pk, "title": "Plan desde Admin", "problem": "Incidencias 6%", "period_start": "2026-07-01",
            "period_end": "2026-07-31", "root_cause": "Recogidas tardías y embalajes sin revisión.", "evidence": "Muestra ficticia",
            "objective": "Reducir al 3%", "responsible": self.agent.pk, "due_date": "2026-12-31", "status": "draft",
            "created_by": self.other.pk, "_save": "Guardar",
        })
        self.assertEqual(response.status_code, 302, response.context and response.context["adminform"].form.errors)
        plan = ImprovementPlan.objects.get(title="Plan desde Admin")
        self.assertEqual(plan.created_by, self.agent)
        response = self.client.post(reverse("admin:action_plans_planmetric_add"), {
            "plan": plan.pk, "baseline": self.baseline.pk, "target_value": "3", "_save": "Guardar"})
        self.assertEqual(response.status_code, 302)
        metric = plan.metrics.get()
        for kind in ["corrective", "preventive"]:
            response = self.client.post(reverse("admin:action_plans_planaction_add"), {"plan": plan.pk, "description": f"Control {kind}",
                "kind": kind, "responsible": "Equipo ficticio", "due_date": "2026-10-30", "status": "pending", "_save": "Guardar"})
            self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse("admin:action_plans_improvementplan_change", args=[plan.pk]), {
            "seller": self.seller.pk, "title": plan.title, "problem": plan.problem,
            "period_start": "2026-07-01", "period_end": "2026-07-31", "root_cause": plan.root_cause,
            "evidence": plan.evidence, "objective": plan.objective, "responsible": self.agent.pk,
            "due_date": "2026-12-31", "status": "in_progress", "_save": "Guardar",
        })
        self.assertEqual(response.status_code, 302)
        plan.refresh_from_db()
        self.assertEqual(plan.status, PlanStatus.IN_PROGRESS)
        action = plan.actions.first()
        response = self.client.post(reverse("admin:action_plans_planaction_change", args=[action.pk]), {
            "plan": plan.pk, "description": action.description, "kind": action.kind, "responsible": action.responsible,
            "due_date": "2026-10-30", "status": "completed", "completed_on": "2026-10-01", "evidence": "Control aplicado.", "_save": "Guardar"})
        self.assertEqual(response.status_code, 302)
        for start, end, reviewed, value in [("2026-08-01", "2026-08-31", "2026-09-01", "4.5"),
            ("2026-09-01", "2026-09-30", "2026-10-01", "3")]:
            response = self.client.post(reverse("admin:action_plans_planreview_add"), {
                "plan_metric": metric.pk, "reviewed_on": reviewed, "period_start": start, "period_end": end,
                "value": value, "order_count": "100", "comments": "Evolución ficticia.", "assessment": "on_track",
                "recorded_by": self.other.pk, "_save": "Guardar"})
            self.assertEqual(response.status_code, 302, response.context and response.context["adminform"].form.errors)
        self.assertEqual(metric.reviews.count(), 2)
        self.assertTrue(all(row.recorded_by == self.agent for row in metric.reviews.all()))
        url = reverse("admin:action_plans_improvementplan_change", args=[plan.pk])
        self.assertContains(self.client.get(url), "alcanzado")
        history_url = reverse("admin:action_plans_planreview_changelist")
        history = self.client.get(history_url, {"plan_metric__plan__id__exact": plan.pk})
        self.assertEqual(history.status_code, 200)
        self.assertEqual(history.context["cl"].result_count, 2)
        response = self.client.post(reverse("admin:action_plans_improvementplan_close", args=[plan.pk]), {
            "status": "closed", "notes": "Objetivo alcanzado. Auditoría preventiva pendiente documentada."})
        self.assertEqual(response.status_code, 302)
        plan.refresh_from_db()
        self.assertEqual(plan.closure_evaluation["result"], "achieved")
        self.assertEqual(plan.actions.get(pk=action.pk).status, ActionStatus.COMPLETED)
        self.assertContains(self.client.get(url), "alcanzado")
        review = metric.reviews.first()
        self.assertEqual(self.client.post(reverse("admin:action_plans_planreview_change", args=[review.pk]), {}).status_code, 403)

    def test_admin_rejects_forged_foreign_keys_status_and_close_without_permission(self):
        plan, metric, action = self.ready_plan()
        self.client.force_login(self.other)
        response = self.client.post(reverse("admin:action_plans_planmetric_add"), {"plan": plan.pk, "baseline": self.baseline.pk, "target_value": "3"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["adminform"].form.errors)
        self.assertEqual(plan.metrics.count(), 1)
        self.agent.user_permissions.remove(Permission.objects.get(codename="close_improvementplan"))
        self.client.force_login(self.agent)
        self.assertEqual(self.client.post(reverse("admin:action_plans_improvementplan_close", args=[plan.pk]), {"notes": "No autorizado", "status": "closed"}).status_code, 403)
        response = self.client.post(reverse("admin:action_plans_improvementplan_change", args=[plan.pk]), {
            "seller": self.seller.pk, "title": plan.title, "problem": plan.problem,
            "period_start": "2026-07-01", "period_end": "2026-07-31", "root_cause": plan.root_cause,
            "evidence": plan.evidence, "objective": plan.objective, "responsible": self.agent.pk,
            "due_date": "2026-12-31", "status": "closed", "closed_at": "2026-10-23", "closure_notes": "Cierre falsificado",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.context["adminform"].form.errors)
        plan.refresh_from_db()
        self.assertEqual(plan.status, PlanStatus.IN_PROGRESS)

    def test_admin_close_requires_csrf_and_preserves_plan_on_failure(self):
        from django.test import Client

        plan, metric, action = self.ready_plan()
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.agent)
        url = reverse("admin:action_plans_improvementplan_close", args=[plan.pk])
        self.assertEqual(client.post(url, {"status": "closed", "notes": "Sin CSRF"}).status_code, 403)
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        token = client.cookies["csrftoken"].value
        response = client.post(url, {"status": "closed", "notes": "Con CSRF"}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 302)

    @override_settings(DEBUG=True)
    def test_demo_is_idempotent_and_demonstrates_acceptance_case(self):
        for _ in range(2):
            call_command("seed_plan_demo", owner=self.agent.username, stdout=StringIO())
        plan = ImprovementPlan.objects.get(seller__reference="SAP-DEMO-PLAN")
        self.assertEqual(plan.status, PlanStatus.CLOSED)
        self.assertEqual(plan.actions.count(), 2)
        self.assertEqual(plan.metrics.get().reviews.count(), 2)
        self.assertEqual(plan.closure_evaluation["result"], "achieved")
        with self.assertRaises(CommandError):
            call_command("seed_plan_demo", owner=self.other.username, stdout=StringIO())

    @override_settings(DEBUG=False)
    def test_demo_is_blocked_in_production(self):
        with self.assertRaises(CommandError):
            call_command("seed_plan_demo", owner=self.agent.username)
