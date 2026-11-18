from importlib import import_module
from secrets import token_urlsafe
from types import SimpleNamespace

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase

from action_plans import test_api
from action_plans.models import ImprovementPlan


class WorkspaceTests(TestCase):
    setUpTestData = classmethod(test_api.PlanApiTests.setUpTestData.__func__)
    payload = test_api.PlanApiTests.payload
    post = test_api.PlanApiTests.post
    patch = test_api.PlanApiTests.patch

    def setUp(self):
        test_api.PlanApiTests.setUp(self)
        self.password = token_urlsafe(30)
        self.agent.username = "evaluador"
        self.agent.set_password(self.password)
        self.agent.save()
        self.admin.username = "platform-root"
        self.admin.save()
        self.other_password = token_urlsafe(30)
        self.other.set_password(self.other_password)
        self.other.save()
        self.other_hash = self.other.password
        self.old_hash = self.agent.password
        self.agent_id = self.agent.pk
        self.migrate_identity()

    def migrate_identity(self):
        migrate = import_module("sellers.migrations.0002_workspace_accounts").promote_evaluator
        migrate(apps, SimpleNamespace(connection=connection))

    def login(self, username, password):
        result = self.client.post("/accounts/login/", {"username": username, "password": password, "next": "/"})
        self.assertRedirects(result, "/dashboard/", fetch_redirect_response=False)

    def test_migrated_account_and_unchanged_agent(self):
        self.migrate_identity()
        self.agent.refresh_from_db()
        self.assertEqual((self.agent.pk, self.agent.username, self.agent.password), (self.agent_id, "admin", self.old_hash))
        self.assertEqual(self.seller.owner_id, self.agent.pk)
        self.assertFalse(get_user_model().objects.filter(username="evaluador").exists())
        self.login("admin", self.password)
        profile = self.client.get("/api/workspace/").json()
        self.assertEqual(profile["role"], "ADMIN")
        self.assertFalse(profile["onboarding_pending"])
        self.assertEqual(self.client.get("/admin/login/")["Location"], "/dashboard/")
        self.assertEqual(self.client.get("/api/sellers/").json()["count"], 1)
        self.assertEqual(self.client.get("/api/users/").json()["sellers"][0]["owner_id"], self.other.pk)
        self.client.logout()
        self.other.refresh_from_db()
        self.assertEqual(self.other.password, self.other_hash)
        self.assertEqual(self.hidden.owner_id, self.other.pk)
        self.login(self.other.username, self.other_password)
        self.assertEqual(self.client.get("/api/workspace/").json()["role"], "AGENT")

    def test_lifecycle_assignments_and_private_history(self):
        self.login("admin", self.password)
        data = self.payload(responsible=self.agent.pk)
        result = self.post("/api/plans/", data)
        self.assertEqual(result.status_code, 201, result.content)
        original = result.json()["id"]
        self.assertEqual(ImprovementPlan.objects.get(pk=original).created_by_id, self.agent.pk)
        password = token_urlsafe(30)
        result = self.post("/api/users/", {"username": "new-agent", "password": password})
        self.assertEqual(result.status_code, 201, result.content)
        pk = result.json()["id"]
        self.assertNotIn("password", result.json())
        user = get_user_model().objects.get(pk=pk)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff or user.is_superuser)
        url = f"/api/assignments/{self.seller.pk}/"
        transfer = {"owner": pk, "previous_owner": self.agent.pk}
        self.assertEqual(self.patch(url, transfer).status_code, 200)
        self.assertEqual(self.patch(url, transfer).status_code, 409)
        self.client.logout()
        self.login(user.username, password)
        self.assertTrue(self.client.get("/api/workspace/").json()["onboarding_pending"])
        self.assertEqual(self.post("/api/onboarding/complete/", {}).status_code, 204)
        self.assertEqual(self.client.get(f"/api/sellers/{self.hidden.pk}/").status_code, 404)
        self.assertEqual(self.client.get("/api/plans/").json()["count"], 0)
        self.assertEqual(self.client.get("/api/sellers/").json()["results"][0]["open_plans"], 0)
        self.assertEqual(self.client.get("/api/overview/").json()["counts"]["open_plans"], 0)
        self.assertEqual(self.client.get(f"/api/plans/{original}/").status_code, 404)
        self.assertEqual(self.patch(f"/api/plans/{original}/", {"title": "Privado"}).status_code, 404)
        self.assertEqual(self.post(f"/api/plans/{original}/actions/", {}).status_code, 404)
        self.assertEqual(self.client.delete(f"/api/plans/{original}/").status_code, 405)
        self.assertEqual(self.client.get("/api/users/").status_code, 403)
        self.assertEqual(self.post("/api/users/", {}).status_code, 403)
        self.assertEqual(self.patch(f"/api/users/{pk}/", {"role": "ADMIN"}).status_code, 403)
        self.assertEqual(self.patch(url, transfer).status_code, 403)
        result = self.post("/api/plans/", self.payload(responsible=pk, created_by=self.agent.pk))
        self.assertEqual(result.status_code, 201, result.content)
        own = result.json()["id"]
        self.assertEqual(ImprovementPlan.objects.get(pk=own).created_by_id, pk)
        self.client.logout()
        self.login(user.username, password)
        self.assertFalse(self.client.get("/api/workspace/").json()["onboarding_pending"])
        self.assertEqual(self.client.get(f"/api/plans/{own}/").status_code, 200)
        self.client.logout()
        self.login("admin", self.password)
        self.assertEqual(self.patch(url, {"owner": None, "previous_owner": pk}).status_code, 200)
        self.assertEqual(self.patch(url, {"owner": self.agent.pk, "previous_owner": None}).status_code, 200)
        self.assertEqual(self.client.get("/api/plans/").json()["results"][0]["id"], original)
        self.assertEqual(self.client.get(f"/api/plans/{own}/").status_code, 404)
        result = self.patch(f"/api/users/{pk}/", {"first_name": "Mar", "is_active": False})
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.json()["is_active"])
        self.client.logout()
        result = self.client.post("/accounts/login/", {"username": user.username, "password": password})
        self.assertTrue(result.context["form"].errors)
        self.assertEqual(self.client.get("/api/workspace/")["X-SAP-Session"], "expired")

    def test_invalid_credentials_and_privilege_fields_rejected_atomically(self):
        self.login("admin", self.password)
        for data in ({"username": "new", "password": "123"}, {"username": "admin", "password": self.password},
                     {"username": "new", "password": self.password, "role": "ADMIN"}):
            self.assertEqual(self.post("/api/users/", data).status_code, 400)
        self.assertFalse(get_user_model().objects.filter(username="new").exists())
