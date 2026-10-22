from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from rest_framework.test import APIClient

from quality.models import QualityMetric, ThresholdPolicy
from sellers.models import AGENT_GROUP, Seller


class AccessAndFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.agent = User.objects.create_user(username="agent", password="test-password-for-tests-only")
        cls.other = User.objects.create_user(username="other")
        cls.admin = User.objects.create_superuser(username="admin", password="test-admin-password-only")
        cls.outsider = User.objects.create_user(username="outsider")
        group = Group.objects.create(name=AGENT_GROUP)
        cls.agent.groups.add(group)
        cls.other.groups.add(group)
        cls.seller = Seller.objects.create(name="Visible", reference="VISIBLE", owner=cls.agent)
        cls.hidden = Seller.objects.create(name="Privada", reference="PRIVATE", owner=cls.other)
        policy = ThresholdPolicy.objects.create(code="acceptance", unit="percent", operator="lt", alarm=99, suspension=98)
        for seller in [cls.seller, cls.hidden]:
            QualityMetric.objects.create(seller=seller, policy=policy, channel="demo-es",
                period_start=date(2026, 9, 1), period_end=date(2026, 9, 30), order_count=30, value=Decimal("98.50"))

    def setUp(self):
        self.api = APIClient()

    def test_anonymous_and_wrong_role_are_denied(self):
        for endpoint in ["/api/", "/api/sellers/", "/api/metrics/"]:
            self.assertEqual(self.api.get(endpoint).status_code, 403)
        self.api.force_login(self.outsider)
        self.assertEqual(self.api.get("/api/sellers/").status_code, 403)

    def test_agent_sees_only_assigned_sellers_and_metrics(self):
        self.api.force_login(self.agent)
        response = self.api.get("/api/sellers/")
        self.assertEqual([row["id"] for row in response.json()["results"]], [self.seller.pk])
        self.assertIn("no-store", response["Cache-Control"])
        metrics = self.api.get("/api/metrics/").json()["results"]
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["classification"], "alarm")
        self.assertEqual(self.api.get(f"/api/sellers/{self.hidden.pk}/").status_code, 404)
        self.assertEqual(self.api.get(f"/api/metrics/{self.hidden.metrics.first().pk}/").status_code, 404)

    def test_admin_sees_all_records(self):
        self.api.force_login(self.admin)
        self.assertEqual(self.api.get("/api/sellers/").json()["count"], 2)
        self.assertEqual(self.api.get("/api/metrics/").json()["count"], 2)

    def test_staff_model_permissions_cannot_bypass_domain_admin_restriction(self):
        from django.contrib.auth.models import Permission

        self.agent.is_staff = True
        self.agent.save()
        self.agent.user_permissions.add(*Permission.objects.filter(content_type__app_label__in=["sellers", "quality"]))
        self.api.force_login(self.agent)
        self.assertEqual(self.api.get("/admin/sellers/seller/").status_code, 403)
        self.assertEqual(self.api.get("/admin/quality/qualitymetric/").status_code, 403)
        self.assertEqual(self.api.get("/admin/quality/thresholdpolicy/").status_code, 403)

    def test_seller_crud_persists_and_validates(self):
        self.api.force_login(self.agent)
        response = self.api.post("/api/sellers/", {"name": "Nueva", "reference": "NEW", "owner": self.other.pk})
        self.assertEqual(response.status_code, 201)
        seller = Seller.objects.get(pk=response.json()["id"])
        self.assertEqual(seller.owner, self.agent)
        url = f"/api/sellers/{seller.pk}/"
        self.assertEqual(self.api.patch(url, {"name": "Editada"}).status_code, 200)
        seller.refresh_from_db()
        self.assertEqual(seller.name, "Editada")
        self.assertEqual(self.api.post("/api/sellers/", {"name": "", "reference": "NEW"}).status_code, 400)
        self.assertEqual(self.api.delete(url).status_code, 204)
        self.assertFalse(Seller.objects.filter(pk=seller.pk).exists())

    def test_cross_owner_writes_and_historical_deletion_are_blocked(self):
        self.api.force_login(self.agent)
        url = f"/api/sellers/{self.hidden.pk}/"
        self.assertEqual(self.api.patch(url, {"name": "Intrusión"}).status_code, 404)
        self.assertEqual(self.api.delete(url).status_code, 404)
        self.assertEqual(self.api.delete(f"/api/sellers/{self.seller.pk}/").status_code, 409)
        self.assertEqual(self.api.post("/api/metrics/", {}).status_code, 405)

    def test_session_login_logout_html_and_password_hash(self):
        self.assertNotEqual(self.agent.password, "test-password-for-tests-only")
        self.assertTrue(self.agent.check_password("test-password-for-tests-only"))
        self.assertEqual(self.api.get("/").status_code, 302)
        response = self.api.post("/accounts/login/", {"username": "agent", "password": "test-password-for-tests-only"})
        self.assertEqual(response.status_code, 302)
        response = self.api.get("/")
        self.assertTemplateUsed(response, "home.html")
        self.assertContains(response, "Visible")
        self.assertNotContains(response, "Privada")
        self.assertEqual(self.api.get("/accounts/logout/").status_code, 405)
        self.assertEqual(self.api.post("/accounts/logout/").status_code, 302)
        self.assertEqual(self.api.get("/api/sellers/").status_code, 403)

    def test_csrf_required_for_login_and_authenticated_mutations(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertEqual(client.post("/accounts/login/", {"username": "agent", "password": "test-password-for-tests-only"}).status_code, 403)
        client.get("/accounts/login/")
        token = client.cookies["csrftoken"].value
        response = client.post("/accounts/login/", {"username": "agent", "password": "test-password-for-tests-only"}, HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(client.post("/api/sellers/", {"name": "CSRF", "reference": "CSRF"}).status_code, 403)
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post("/api/sellers/", {"name": "CSRF", "reference": "CSRF"}, HTTP_X_CSRFTOKEN=token).status_code, 201)

    def test_templates_escape_untrusted_seller_names(self):
        self.seller.name = '<script>alert("xss")</script>'
        self.seller.save()
        self.api.force_login(self.agent)
        response = self.api.get("/")
        self.assertContains(response, "&lt;script&gt;")
        self.assertNotContains(response, '<script>alert("xss")</script>')
