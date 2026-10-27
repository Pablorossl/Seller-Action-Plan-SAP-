"""Contrato HTTP de la Fase 2; reutiliza las fixtures de dominio de Fase 1."""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Permission
from django.test import Client, TestCase
from django.utils import timezone

from action_plans import tests as phase1
from action_plans.models import ImprovementPlan, PlanAction, PlanMetric, PlanReview
from sellers.models import Seller
from quality.models import QualityMetric, ThresholdPolicy


class PlanApiTests(TestCase):
    setUpTestData = classmethod(phase1.PlanTests.setUpTestData.__func__)
    setUp = phase1.PlanTests.setUp
    plan = phase1.PlanTests.plan
    action = phase1.PlanTests.action
    ready_plan = phase1.PlanTests.ready_plan
    review = phase1.PlanTests.review

    def login(self, user=None):
        self.client.force_login(user or self.agent)

    def payload(self, **changes):
        return dict(seller=self.seller.pk, title="Plan desde React", problem="Incidencias del 6%",
            period_start="2026-07-01", period_end="2026-07-31", root_cause="Embalaje insuficiente",
            evidence="Muestra ficticia", objective="Reducir al 3%", responsible=self.agent.pk,
            due_date="2026-12-31", metrics=[{"baseline": self.baseline.pk, "target_value": "3"}]) | changes

    def post(self, path, data):
        return self.client.post(path, data, content_type="application/json")

    def patch(self, path, data):
        return self.client.patch(path, data, content_type="application/json")

    def test_authentication_workspace_and_dashboard(self):
        self.assertEqual(self.client.get("/dashboard/").status_code, 302)
        self.assertEqual(self.client.get("/api/overview/").status_code, 403)
        self.login(self.outsider)
        self.assertEqual(self.client.get("/api/plans/").status_code, 403)
        self.login()
        session = self.client.get("/api/workspace/").json()
        self.assertEqual(session["id"], self.agent.pk)
        self.assertTrue(session["csrf_token"])
        self.assertTrue(session["permissions"]["add_improvementplan"])
        self.assertEqual(self.client.get("/api/overview/").json()["counts"]["sellers"], 1)

    def test_scoped_lists_details_search_and_pagination(self):
        self.login()
        own = self.plan()
        hidden = self.plan(seller=self.hidden, title="Secreto")
        self.assertEqual(self.client.get("/api/plans/").json()["count"], 1)
        self.assertEqual(self.client.get(f"/api/plans/{hidden.pk}/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/sellers/{self.hidden.pk}/").status_code, 404)
        self.assertEqual(self.client.get(f"/api/plans/{own.pk}/").status_code, 200)
        self.assertEqual(self.client.get("/api/plans/?search=envíos").json()["count"], 1)
        self.assertEqual(self.client.get("/api/plans/?seller=invalid").status_code, 400)
        Seller.objects.bulk_create([Seller(name=f"Demo {i}", reference=f"DEMO-{i}", owner=self.agent) for i in range(105)])
        first = self.client.get("/api/sellers/").json()
        self.assertEqual(first["count"], 106)
        self.assertEqual(len(first["results"]), 50)
        self.assertTrue(first["next"])
        self.assertEqual(self.client.get("/api/sellers/?search=PLAN-1").json()["count"], 1)
        self.assertEqual(self.client.get("/api/sellers/?active_plans=1").json()["count"], 1)
        self.assertEqual(self.client.get(f"/api/metrics/?seller={self.hidden.pk}").json()["count"], 0)

    def test_foreign_relations_and_atomic_create(self):
        self.login()
        for changes in [dict(seller=self.hidden.pk), dict(responsible=self.other.pk),
            dict(metrics=[{"baseline": self.baseline.pk, "target_value": "7"}]),
            dict(metrics=[]), dict(due_date="2026-01-01"), dict(title=""), dict(status="closed")]:
            with self.subTest(changes=changes):
                self.assertEqual(self.post("/api/plans/", self.payload(**changes)).status_code, 400)
                self.assertEqual(ImprovementPlan.objects.count(), 0)
        data = self.payload(metrics=[{"baseline": self.baseline.pk, "target_value": "3"}, {"baseline": self.baseline.pk, "target_value": "2"}])
        response = self.post("/api/plans/", data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("metrics", response.json())
        self.assertEqual(ImprovementPlan.objects.count(), 0)
        self.assertEqual(PlanMetric.objects.count(), 0)

    def test_full_api_acceptance_flow_and_persistence(self):
        self.login()
        created = self.post("/api/plans/", self.payload(created_by=self.other.pk))
        self.assertEqual(created.status_code, 201, created.content)
        data = created.json()
        pk, metric = data["id"], data["metrics"][0]["id"]
        path = f"/api/plans/{pk}/"
        self.assertEqual(ImprovementPlan.objects.get(pk=pk).created_by, self.agent)
        self.assertEqual(self.patch(path, {"status": "in_progress"}).status_code, 400)
        for kind in ["corrective", "preventive"]:
            response = self.post(path + "actions/", dict(description="Revisar embalajes", kind=kind, responsible="Logística", due_date="2026-10-23"))
            self.assertEqual(response.status_code, 201, response.content)
        action = response.json()["actions"][0]["id"]
        self.assertEqual(self.patch(path, {"status": "in_progress", "title": "Plan actualizado"}).status_code, 200)
        response = self.patch(path + f"actions/{action}/", dict(status="completed", completed_on="2026-10-23", evidence="Protocolo aplicado"))
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["evaluation"]["result"], "not_evaluable")
        for month, end, observed, achieved in [(8, 31, "4.5", False), (9, 30, "3", True)]:
            response = self.post(path + "reviews/", dict(plan_metric=metric, reviewed_on="2026-10-23", value=observed,
                period_start=f"2026-{month:02d}-01", period_end=f"2026-{month:02d}-{end}", order_count=100,
                comments="Revisión ficticia", assessment="on_track", recorded_by=self.other.pk))
            self.assertEqual(response.status_code, 201, response.content)
            self.assertEqual(response.json()["evaluation"]["metrics"][0]["achieved"], achieved)
        response = self.post(path + "close/", {"notes": "Objetivo alcanzado, se mantiene control preventivo.", "confirm": True})
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["closure_evaluation"]["result"], "achieved")
        self.assertEqual(PlanReview.objects.filter(recorded_by=self.agent).count(), 2)
        self.assertEqual(PlanAction.objects.filter(plan_id=pk).count(), 2)
        self.client.logout()
        self.login()
        persisted = self.client.get(path).json()
        self.assertEqual(persisted["status"], "closed")
        self.assertEqual(persisted["evaluation"]["metrics"][0]["current"], "3.00")
        self.assertEqual(len(persisted["reviews"]), 2)
        self.assertEqual(self.patch(path, {"title": "Modificar histórico"}).status_code, 400)
        self.assertEqual(self.patch(path + f"actions/{action}/", {"notes": "Cambiar"}).status_code, 400)
        self.assertEqual(self.post(path + "close/", {"notes": "Otra vez", "confirm": True}).status_code, 400)

    def test_actions_reviews_and_close_deny_foreign_objects(self):
        plan, metric, action = self.ready_plan()
        self.login(self.other)
        path = f"/api/plans/{plan.pk}/"
        self.assertEqual(self.patch(path, {"title": "Ajeno"}).status_code, 404)
        self.assertEqual(self.post(path + "actions/", {}).status_code, 404)
        self.assertEqual(self.patch(path + f"actions/{action.pk}/", {}).status_code, 404)
        self.assertEqual(self.post(path + "reviews/", {}).status_code, 404)
        self.assertEqual(self.post(path + "close/", {"notes": "Ajeno", "confirm": True}).status_code, 404)
        plan.refresh_from_db()
        self.assertEqual(plan.status, "in_progress")

    def test_explicit_permissions_are_enforced(self):
        plan, _, action = self.ready_plan()
        self.agent.user_permissions.clear()
        self.agent.user_permissions.add(Permission.objects.get(codename="view_improvementplan"))
        self.login()
        path = f"/api/plans/{plan.pk}/"
        self.assertEqual(self.client.get(path).status_code, 200)
        self.assertEqual(self.post("/api/plans/", self.payload()).status_code, 403)
        self.assertEqual(self.patch(path, {"title": "Sin permiso"}).status_code, 403)
        self.assertEqual(self.post(path + "actions/", {}).status_code, 403)
        self.assertEqual(self.patch(path + f"actions/{action.pk}/", {}).status_code, 403)
        self.assertEqual(self.post(path + "reviews/", {}).status_code, 403)
        self.assertEqual(self.post(path + "close/", {"notes": "Sin permiso", "confirm": True}).status_code, 403)

    def test_validation_errors_and_immutable_relations(self):
        self.login()
        plan, metric, action = self.ready_plan()
        second = self.plan()
        another_metric = PlanMetric.objects.create(plan=second, baseline=self.baseline, target_value=Decimal("2"))
        path = f"/api/plans/{plan.pk}/"
        response = self.patch(path + f"actions/{action.pk}/", {"status": "completed"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("completed_on", response.json())
        response = self.post(path + "reviews/", dict(plan_metric=another_metric.pk, reviewed_on="2026-10-23", value="3", period_start="2026-09-01", period_end="2026-09-30", comments="Prueba", assessment="on_track"))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.post(path + "close/", {"notes": "No confirmado"}).status_code, 400)
        self.assertEqual(self.post(path + "close/", {"notes": "", "confirm": True}).status_code, 400)
        self.assertEqual(self.patch(path, {"seller": self.hidden.pk}).status_code, 400)
        self.assertEqual(self.patch(path, {"status": "closed"}).status_code, 400)
        self.assertEqual(self.client.delete(path).status_code, 405)

    def test_dashboard_deadlines_counts_and_final_plan_exclusion(self):
        self.login()
        plan, metric, action = self.ready_plan()
        today = timezone.localdate()
        plan.next_review_on = today
        plan.save()
        self.action(plan, due_date=today)
        self.action(plan, due_date=today + timedelta(days=7))
        self.action(plan, due_date=today + timedelta(days=8))
        self.action(self.plan(seller=self.hidden))
        response = self.client.get("/api/overview/")
        self.assertEqual(response.status_code, 200, response.content)
        data = response.json()
        self.assertEqual(data["counts"]["pending_actions"], 4)
        self.assertEqual(data["counts"]["overdue_actions"], 1)
        self.assertEqual(data["counts"]["needs_review"], 1)
        self.assertEqual(data["priorities_count"], 3)
        self.assertEqual(data["counts"]["sellers_with_deviations"], 1)
        self.post(f"/api/plans/{plan.pk}/close/", {"notes": "Cierre documentado con pendientes", "confirm": True})
        data = self.client.get("/api/overview/").json()
        self.assertEqual(data["counts"]["pending_actions"], 0)
        self.assertEqual(data["counts"]["closed_plans"], 1)

    def test_csrf_for_all_write_operations(self):
        plan, _, action = self.ready_plan()
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.agent)
        paths = ["/api/plans/", f"/api/plans/{plan.pk}/actions/", f"/api/plans/{plan.pk}/reviews/", f"/api/plans/{plan.pk}/close/"]
        for path in paths:
            self.assertEqual(client.post(path, {}, content_type="application/json").status_code, 403)
        for path in [f"/api/plans/{plan.pk}/", f"/api/plans/{plan.pk}/actions/{action.pk}/"]:
            self.assertEqual(client.patch(path, {}, content_type="application/json").status_code, 403)
        token = client.get("/api/workspace/").json()["csrf_token"]
        response = client.post("/api/plans/", self.payload(), content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201, response.content)

    def test_multiple_metrics_and_draft_target_editing(self):
        self.login()
        policy = ThresholdPolicy.objects.create(code="acceptance", unit="percent", operator="lt", alarm=99, suspension=98)
        baseline = QualityMetric.objects.create(seller=self.seller, policy=policy, channel="demo-es",
            period_start="2026-07-01", period_end="2026-07-31", order_count=100, value=97)
        data = self.payload(metrics=[{"baseline": self.baseline.pk, "target_value": "3"}, {"baseline": baseline.pk, "target_value": "99"}])
        response = self.post("/api/plans/", data)
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(len(response.json()["metrics"]), 2)
        plan = ImprovementPlan.objects.get(pk=response.json()["id"])
        metric = plan.metrics.get(baseline=self.baseline)
        path = f"/api/plans/{plan.pk}/metrics/{metric.pk}/"
        self.assertEqual(self.patch(path, {"target_value": "2"}).status_code, 200)
        self.action(plan)
        self.patch(f"/api/plans/{plan.pk}/", {"status": "in_progress"})
        self.assertEqual(self.patch(path, {"target_value": "1"}).status_code, 400)
        metric.refresh_from_db()
        self.assertEqual(metric.target_value, Decimal("2"))
        self.login(self.other)
        self.assertEqual(self.patch(path, {"target_value": "1"}).status_code, 404)

    def test_existing_draft_can_receive_metrics_without_admin(self):
        self.login()
        plan = self.plan()
        path = f"/api/plans/{plan.pk}/metrics/"
        response = self.post(path, {"baseline": self.baseline.pk, "target_value": "3"})
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(self.post(path, {"baseline": self.baseline.pk, "target_value": "2"}).status_code, 400)
        self.assertEqual(plan.metrics.count(), 1)

    def test_latest_metrics_and_missing_indicators(self):
        self.login()
        QualityMetric.objects.create(seller=self.seller, policy=self.policy, channel="demo-es",
            period_start="2026-08-01", period_end="2026-08-31", order_count=100, value=3)
        response = self.client.get(f"/api/metrics/?seller={self.seller.pk}&latest=1").json()
        self.assertEqual(response["count"], 1)
        self.assertEqual(response["results"][0]["classification"], "ok")
        self.assertEqual(self.client.get("/api/overview/").json()["counts"]["sellers_with_deviations"], 0)
        missing = self.client.get(f"/api/sellers/{self.seller.pk}/").json()["missing_indicators"]
        self.assertEqual(len(missing), 6)
        self.assertNotIn("incidents", [m["code"] for m in missing])
