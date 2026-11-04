"""Contrato de identidad y sesión del acceso real, con CSRF y proxy HTTPS."""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client, TestCase, override_settings

from sellers.models import AGENT_GROUP


@override_settings(
    DEBUG=False, ALLOWED_HOSTS=["sap.example.invalid"],
    CSRF_TRUSTED_ORIGINS=["https://sap.example.invalid"],
    SECURE_SSL_REDIRECT=True,
    SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
    SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True,
)
class AuthenticationIdentityTests(TestCase):
    password = "test-only-assigned-agent-password"
    origin = "https://sap.example.invalid"

    @classmethod
    def setUpTestData(cls):
        cls.agent = get_user_model().objects.create_user(
            username="assigned-agent", email="agent@example.invalid", password=cls.password,
        )
        cls.agent.groups.add(Group.objects.create(name=AGENT_GROUP))

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True, HTTP_HOST="sap.example.invalid",
            HTTP_X_FORWARDED_PROTO="https")
        self.client.get("/accounts/login/")

    def login(self, username, password, **extra):
        return self.client.post("/accounts/login/", {
            "username": username, "password": password,
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value, **extra,
        }, HTTP_ORIGIN=self.origin)

    def test_email_and_missing_user_are_rejected_without_disclosing_account_existence(self):
        # ModelBackend usa username: ni un email de contacto ni una identidad
        # ausente en la BD equivalen al nombre de usuario asignado.
        errors = []
        for username, password in [
            (self.agent.email, self.password),
            ("missing@example.invalid", self.password),
            (self.agent.username, "incorrect-test-password"),
        ]:
            with self.subTest(username=username):
                response = self.login(username, password)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].non_field_errors())
                errors.append(list(response.context["form"].non_field_errors()))
                self.assertNotIn("sessionid", response.cookies)
                self.assertNotContains(response, password)
                self.assertEqual(self.client.get("/api/workspace/").status_code, 403)
        self.assertEqual(errors[0], errors[1])
        self.assertEqual(errors[1], errors[2])
        response = self.login(self.agent.username, self.password)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/dashboard/")
        self.assertEqual(self.client.get("/api/workspace/").json()["username"], self.agent.username)

    def test_next_root_session_reuse_and_logout_revocation(self):
        response = self.login(self.agent.username, self.password, next="/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")
        self.assertContains(self.client.get("/"), "Tu espacio de trabajo")
        session = response.cookies["sessionid"]
        self.assertTrue(session["secure"])
        self.assertTrue(session["httponly"])
        self.assertEqual(session["samesite"], "Lax")
        restored = Client(enforce_csrf_checks=True, HTTP_HOST="sap.example.invalid",
            HTTP_X_FORWARDED_PROTO="https")
        restored.cookies["sessionid"] = session.value
        response = restored.get("/api/workspace/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], self.agent.username)
        response = self.client.post("/accounts/logout/", {
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
        }, HTTP_ORIGIN=self.origin)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/accounts/login/")
        # El servidor invalida la sesión; conservar la cookie anterior no da acceso.
        self.assertEqual(restored.get("/api/workspace/").status_code, 403)
        self.assertEqual(restored.get("/dashboard/").status_code, 302)
