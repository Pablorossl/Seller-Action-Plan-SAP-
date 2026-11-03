"""El calendario posterior no reescribe la situación conservada al finalizar."""
from copy import deepcopy
from datetime import date
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from action_plans.models import ImprovementPlan
from action_plans.services import close_plan, evaluate_plan
from action_plans.tests import PlanTests


class ClosureHistoryTests(TestCase):
    setUpTestData = classmethod(PlanTests.setUpTestData.__func__)
    setUp = PlanTests.setUp
    plan = PlanTests.plan
    action = PlanTests.action
    ready_plan = PlanTests.ready_plan

    def test_open_calendar_and_closed_snapshot_for_closed_and_cancelled(self):
        for status in ("closed", "cancelled"):
            with self.subTest(status=status):
                plan, _, action = self.ready_plan()
                action.due_date = date(2026, 10, 24)
                action.save()
                self.assertFalse(action.is_overdue)
                with patch("django.utils.timezone.localdate", return_value=date(2026, 10, 25)):
                    self.assertTrue(action.is_overdue)
                    self.assertEqual(evaluate_plan(plan)["overdue_actions"], 1)
                overdue = self.action(plan, due_date=date(2026, 10, 22))
                today = self.action(plan, due_date=date(2026, 10, 23))
                self.assertTrue(overdue.is_overdue)
                self.assertFalse(today.is_overdue)
                closed = close_plan(plan_id=plan.pk, actor=self.agent, notes="Fin", status=status)
                snapshot = deepcopy(closed.closure_evaluation)
                with patch("django.utils.timezone.localdate", return_value=date(2027, 1, 1)):
                    client = APIClient(); client.force_authenticate(self.agent)
                    response = client.get(f"/api/plans/{plan.pk}/")
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.data["evaluation"], snapshot)
                    flags = {item["id"]: item["is_overdue"] for item in response.data["actions"]}
                    self.assertFalse(flags[action.pk])
                    self.assertTrue(flags[overdue.pk])
                    self.assertFalse(flags[today.pk])
                    self.assertEqual(response.data["evaluation"]["overdue_actions"], 1)
                    client.force_authenticate(self.other)
                    self.assertEqual(client.get(f"/api/plans/{plan.pk}/").status_code, 404)
                closed.refresh_from_db()
                self.assertEqual(closed.closure_evaluation, snapshot)

    def test_legacy_snapshot_missing_detail_and_totals_remains_untouched(self):
        plan, _, _ = self.ready_plan()
        close_plan(plan_id=plan.pk, actor=self.agent, notes="Fin")
        for snapshot in ({"result": "not_evaluable", "overdue_actions": 1}, {"result": "not_evaluable"}):
            ImprovementPlan.objects.filter(pk=plan.pk).update(closure_evaluation=snapshot)
            with patch("django.utils.timezone.localdate", return_value=date(2027, 1, 1)):
                client = APIClient(); client.force_authenticate(self.agent)
                data = client.get(f"/api/plans/{plan.pk}/").data
                self.assertEqual(data["evaluation"]["overdue_actions"], snapshot.get("overdue_actions"))
                self.assertIsNone(data["actions"][0]["is_overdue"])
                self.assertIsNone(data["evaluation"]["actions"]["completed"])
            plan.refresh_from_db()
            self.assertEqual(plan.closure_evaluation, snapshot)
