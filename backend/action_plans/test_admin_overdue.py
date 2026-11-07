"""El admin muestra vencimiento operativo; el cierre conserva el histórico."""
from copy import deepcopy
from datetime import date
from unittest.mock import patch

from django.contrib import admin
from django.test import RequestFactory, TestCase

from action_plans.admin import OverdueFilter, PlanActionAdmin
from action_plans.models import PlanAction
from action_plans.services import close_plan
from action_plans import tests as fixtures


class AdminOverdueTests(TestCase):
    setUpTestData = classmethod(fixtures.PlanTests.setUpTestData.__func__)
    setUp = fixtures.PlanTests.setUp
    plan = fixtures.PlanTests.plan
    action = fixtures.PlanTests.action
    ready_plan = fixtures.PlanTests.ready_plan

    def filtered(self, user=None):
        request = RequestFactory().get("/admin/action_plans/planaction/?overdue=yes")
        request.user = user or self.agent
        model_admin = PlanActionAdmin(PlanAction, admin.site)
        query = model_admin.get_queryset(request)
        filter_ = OverdueFilter(request, {"overdue": ["yes"]}, PlanAction, model_admin)
        return filter_.queryset(request, query)

    def test_active_states_and_action_states_match_operational_column(self):
        expected = set()
        for status in ("draft", "in_progress", "in_review"):
            if status == "draft":
                plan = self.plan()
                overdue = self.action(plan)
            else:
                plan, _, overdue = self.ready_plan()
                if status == "in_review":
                    plan.status = status
                    plan.save()
            expected.add(overdue.pk)
            self.action(plan, due_date=date(2026, 12, 1))
            self.action(plan, due_date=date(2026, 10, 23))
            self.action(plan, status="completed", completed_on=date(2026, 10, 22), evidence="Realizada")
            self.action(plan, status="cancelled")
            expected.add(self.action(plan, status="in_progress").pk)
        self.assertSetEqual(set(self.filtered().values_list("pk", flat=True)), expected)
        model_admin = PlanActionAdmin(PlanAction, admin.site)
        for action in PlanAction.objects.select_related("plan"):
            self.assertEqual(model_admin.overdue(action), action.pk in expected)
        self.assertFalse(self.filtered(self.other).exists())

    def test_final_plans_leave_queue_without_changing_snapshot(self):
        for status in ("closed", "cancelled"):
            with self.subTest(status=status):
                plan, _, overdue = self.ready_plan()
                future = self.action(plan, due_date=date(2026, 12, 1))
                closed = close_plan(plan_id=plan.pk, actor=self.agent, notes="Fin", status=status)
                snapshot = deepcopy(closed.closure_evaluation)
                self.assertTrue(snapshot["action_overdue"][str(overdue.pk)])
                self.assertFalse(snapshot["action_overdue"][str(future.pk)])
                for day in (date(2026, 10, 23), date(2027, 1, 1)):
                    with patch("django.utils.timezone.localdate", return_value=day):
                        self.assertFalse(self.filtered().filter(plan=closed).exists())
                        model_admin = PlanActionAdmin(PlanAction, admin.site)
                        for action in PlanAction.objects.filter(plan=closed).select_related("plan"):
                            self.assertFalse(model_admin.overdue(action))
                            self.assertEqual(action.is_overdue, snapshot["action_overdue"][str(action.pk)])
                closed.refresh_from_db()
                self.assertEqual(closed.closure_evaluation, snapshot)
