import os
from pathlib import Path
import secrets
import subprocess
import sys
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import OperationalError
from django.test import Client, TestCase, override_settings


class ProductionTests(TestCase):
    def test_health_checks_database_without_disclosing_details(self):
        response = self.client.get("/healthz/")
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertIn("no-store", response["Cache-Control"])
        with patch("config.views.connection.cursor", side_effect=OperationalError("private-database-secret")):
            response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})
        self.assertNotIn(b"private", response.content)

    @override_settings(SECURE_SSL_REDIRECT=True, SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
        SESSION_COOKIE_SECURE=True, CSRF_COOKIE_SECURE=True, SECURE_HSTS_SECONDS=31536000)
    def test_https_redirect_proxy_headers_and_secure_session(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://testserver/accounts/login/")
        response = self.client.get("/accounts/login/", HTTP_X_FORWARDED_PROTO="https")
        self.assertEqual(response.status_code, 200)
        self.assertIn("max-age=31536000", response["Strict-Transport-Security"])
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertTrue(response.cookies["csrftoken"]["secure"])
        user = get_user_model().objects.create_user(username="secure-agent", password="test-only-secure-password")
        response = self.client.post("/accounts/login/", {"username": user.username, "password": "test-only-secure-password"}, HTTP_X_FORWARDED_PROTO="https")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.cookies["sessionid"]["secure"])
        self.assertTrue(response.cookies["sessionid"]["httponly"])
        self.assertEqual(response.cookies["sessionid"]["samesite"], "Lax")
        self.assertEqual(self.client.get("/accounts/logout/", secure=True).status_code, 405)

    def test_login_lockout_cannot_be_bypassed_with_cookies_or_user_agent(self):
        user = get_user_model().objects.create_user(username="limited-agent", password="test-only-secure-password")
        for i in range(5):
            response = Client().post("/accounts/login/", {"username": user.username, "password": "incorrect"}, HTTP_USER_AGENT=f"Rotated-{i}", HTTP_X_FORWARDED_FOR=f"192.0.2.{i}")
        self.assertEqual(response.status_code, 429)
        response = Client().post("/accounts/login/", {"username": user.username, "password": "test-only-secure-password"}, HTTP_USER_AGENT="new-agent")
        self.assertEqual(response.status_code, 429)
        self.assertNotIn(b"limited-agent", response.content)
        from axes.models import AccessAttempt
        for attempt in AccessAttempt.objects.filter(username=user.username):
            self.assertIsNone(attempt.ip_address)
            self.assertNotIn("incorrect", attempt.post_data)
            self.assertNotIn("test-only-secure-password", attempt.post_data)

    def test_production_settings_fail_closed(self):
        root = Path(__file__).resolve().parents[2]
        environment = os.environ | {
            "DJANGO_DEBUG": "False", "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
            "DJANGO_ALLOWED_HOSTS": "sap.example.invalid", "RENDER_EXTERNAL_HOSTNAME": "",
            "DJANGO_CSRF_TRUSTED_ORIGINS": "https://sap.example.invalid",
            "DATABASE_URL": "postgresql://placeholder:placeholder@127.0.0.1:1/sap?sslmode=require",
        }
        for invalid in [
            {"DJANGO_SECRET_KEY": "short"}, {"DATABASE_URL": ""}, {"DJANGO_ALLOWED_HOSTS": "*"},
            {"DJANGO_ALLOWED_HOSTS": ""}, {"DJANGO_CSRF_TRUSTED_ORIGINS": "http://sap.example.invalid"},
            {"DATABASE_URL": "postgresql://placeholder:placeholder@127.0.0.1:1/sap?sslmode=disable"},
        ]:
            result = subprocess.run([sys.executable, "manage.py", "check", "--deploy"], cwd=root / "backend", env=environment | invalid, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn(environment["DJANGO_SECRET_KEY"], result.stderr)

    @override_settings(DEBUG=False)
    def test_unknown_url_does_not_expose_debug_details(self):
        response = self.client.get("/missing-private-route/")
        self.assertEqual(response.status_code, 404)
        self.assertNotIn(b"DJANGO_SETTINGS_MODULE", response.content)
