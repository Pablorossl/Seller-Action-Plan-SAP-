"""Regresiones de seguridad para producción y funciones serverless."""
import os
from pathlib import Path
import secrets
import subprocess
import sys

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase, override_settings


class VercelSettingsTests(SimpleTestCase):
    def test_vercel_rejects_unsafe_settings_without_using_local_env(self):
        environment = os.environ | {
            "VERCEL": "1", "VERCEL_ENV": "production", "DJANGO_DEBUG": "False",
            "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
            "DJANGO_ALLOWED_HOSTS": "sap.example.invalid",
            "DJANGO_CSRF_TRUSTED_ORIGINS": "https://sap.example.invalid",
            "DATABASE_URL": "postgresql://placeholder:placeholder@127.0.0.1:1/sap?sslmode=require",
        }
        invalid_settings = [
            {"DJANGO_SECRET_KEY": None}, {"DJANGO_ALLOWED_HOSTS": None}, {"DATABASE_URL": None},
            {"DJANGO_DEBUG": "True"}, {"VERCEL_ENV": "preview", "DJANGO_DEBUG": "True"},
            {"DATABASE_URL": "sqlite:///db.sqlite3"},
            {"DATABASE_URL": "postgresql://placeholder:placeholder@127.0.0.1:1/sap?sslmode=disable"},
            {"DJANGO_ALLOWED_HOSTS": ".vercel.app"}, {"DJANGO_ALLOWED_HOSTS": "*.vercel.app"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://*.vercel.app"},
            {"DJANGO_SECRET_KEY": "django-insecure-" + secrets.token_urlsafe(64)},
        ]
        for invalid in invalid_settings:
            with self.subTest(invalid=list(invalid)):
                env = {key: value for key, value in (environment | invalid).items() if value is not None}
                result = subprocess.run([sys.executable, "manage.py", "check", "--deploy"],
                    cwd=Path(__file__).resolve().parents[1], env=env, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn(environment["DJANGO_SECRET_KEY"], result.stderr)


@override_settings(DEBUG=False, ALLOWED_HOSTS=["sap.example.invalid"],
    CSRF_TRUSTED_ORIGINS=["https://sap.example.invalid"], SECURE_SSL_REDIRECT=True,
    SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
    SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True)
class ProxyCsrfTests(TestCase):
    def test_real_csrf_login_and_logout_behind_https_proxy(self):
        user = get_user_model().objects.create_user(username="vercel-agent", password="test-only-secure-password")
        client = Client(enforce_csrf_checks=True, HTTP_HOST="sap.example.invalid", HTTP_X_FORWARDED_PROTO="https")
        self.assertEqual(client.get("/accounts/login/").status_code, 200)
        payload = {"username": user.username, "password": "test-only-secure-password"}
        self.assertEqual(client.post("/accounts/login/", payload, HTTP_ORIGIN="https://sap.example.invalid").status_code, 403)
        payload["csrfmiddlewaretoken"] = client.cookies["csrftoken"].value
        self.assertEqual(client.post("/accounts/login/", payload, HTTP_ORIGIN="https://untrusted.example.invalid").status_code, 403)
        response = client.post("/accounts/login/", payload, HTTP_ORIGIN="https://sap.example.invalid")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/dashboard/")
        self.assertTrue(response.cookies["sessionid"]["secure"])
        self.assertTrue(response.cookies["sessionid"]["httponly"])
        self.assertEqual(client.get("/dashboard/").status_code, 200)
        self.assertEqual(client.get("/api/plans/").status_code, 403)  # Usuario sin grupo/permisos.
        self.assertEqual(client.post("/accounts/logout/", HTTP_ORIGIN="https://sap.example.invalid").status_code, 403)
        response = client.post("/accounts/logout/", {"csrfmiddlewaretoken": client.cookies["csrftoken"].value},
            HTTP_ORIGIN="https://sap.example.invalid")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(client.get("/dashboard/").status_code, 302)
