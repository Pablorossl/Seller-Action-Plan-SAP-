"""Exercise the local app against Neon, including persistence across a restart.

Run after neon deploy, npm run db:migrate and npm run build:
    .venv/bin/python scripts/verify_neon_e2e.py --allow-writes
Creates a temporary agent and seller, then removes only those test records.
Starts npm start on port 8000; that port must be free. Never prints credentials.
"""
import argparse
from http.cookiejar import CookieJar
import json
import os
from pathlib import Path
import re
import secrets
import signal
import socket
import subprocess
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPCookieProcessor, Request, build_opener
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
BASE = "http://127.0.0.1:8000"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-writes", action="store_true", required=True)
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts/neon-setup-e2e.json")
    args = parser.parse_args()
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", 8000)) == 0:
            parser.error("Port 8000 must be free so this check can restart its own server.")

    sys.path.insert(0, str(ROOT / "backend"))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django
    django.setup()
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import Group
    from django.contrib.sessions.models import Session
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    from sellers.models import AGENT_GROUP, Seller
    import psycopg

    primary = os.environ.get("DATABASE_URL", "")
    direct = os.environ.get("DATABASE_URL_UNPOOLED", "")
    app_url, migration_url = urlsplit(primary), urlsplit(direct)
    if (not settings.DEBUG or not app_url.hostname or not migration_url.hostname
            or not app_url.hostname.endswith(".neon.tech")
            or "-pooler" not in app_url.hostname
            or "-pooler" in migration_url.hostname
            or app_url.hostname.replace("-pooler", "") != migration_url.hostname
            or (app_url.path, app_url.username) != (migration_url.path, migration_url.username)):
        parser.error("Requires local DEBUG and matching pooled/direct Neon URLs from neon deploy.")
    executor = MigrationExecutor(connection)
    if executor.migration_plan(executor.loader.graph.leaf_nodes()):
        parser.error("Apply pending migrations with npm run db:migrate first.")

    cookies = CookieJar()
    client = build_opener(HTTPCookieProcessor(cookies))
    report = {"service": "postgres", "branch": os.environ.get("NEON_BRANCH"), "checks": {}}
    checks = report["checks"]
    user = seller_id = server = None
    group, created_group = Group.objects.get_or_create(name=AGENT_GROUP)
    username = "neon_e2e_" + uuid4().hex[:16]
    password = secrets.token_urlsafe(32)

    def request(path, data=None, method=None, form=False):
        headers = {"Referer": BASE + "/dashboard/"}
        body = None
        if data is not None:
            body = (urlencode(data) if form else json.dumps(data)).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
        if data is not None or method in ("POST", "PUT", "PATCH", "DELETE"):
            token = next((cookie.value for cookie in cookies if cookie.name == "csrftoken"), "")
            headers["X-CSRFToken"] = token
        with client.open(Request(BASE + path, data=body, headers=headers, method=method), timeout=30) as response:
            return response.status, response.read()

    def stop():
        nonlocal server
        if server is not None:
            os.killpg(server.pid, signal.SIGTERM)
            server.wait(timeout=15)
            server = None

    def start(log):
        nonlocal server
        server = subprocess.Popen(["npm", "start", "--", "--noreload"], cwd=ROOT,
            stdout=log, stderr=log, start_new_session=True)
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if server.poll() is not None:
                raise RuntimeError("npm start exited; inspect the local server configuration.")
            try:
                status, body = request("/healthz/")
                assert status == 200 and json.loads(body) == {"status": "ok"}
                return
            except (URLError, OSError):
                time.sleep(0.2)
        raise RuntimeError("App did not become ready within 30 seconds.")

    try:
        user = get_user_model().objects.create_user(username=username, password=password)
        user.groups.add(group)
        with tempfile.TemporaryFile() as log:
            start(log)
            checks["health_http_200"] = True
            request("/accounts/login/")
            status, html = request("/accounts/login/", {"username": username, "password": password,
                "csrfmiddlewaretoken": next(c.value for c in cookies if c.name == "csrftoken")}, form=True)
            assert status == 200 and any(c.name == "sessionid" for c in cookies)
            status, html = request("/dashboard/")
            assert status == 200
            assets = re.findall(r'(?:src|href)="(/static/react/assets/[^\"]+)"', html.decode())
            assert assets, "Dashboard must serve the built React app."
            for asset in assets:
                assert request(asset)[0] == 200
            checks["login_dashboard_and_react_assets"] = True
            assert request("/api/workspace/")[0] == 200
            status, body = request("/api/sellers/", {"name": "Temporary Neon E2E seller", "reference": username})
            assert status == 201
            seller_id = json.loads(body)["id"]
            path = f"/api/sellers/{seller_id}/"
            updated_name = "Temporary Neon E2E seller updated"
            status, body = request(path, {"name": updated_name}, method="PATCH")
            assert status == 200 and json.loads(body)["name"] == updated_name
            checks["api_create_201_and_update_200"] = True
            with psycopg.connect(direct, connect_timeout=10) as direct_connection:
                assert direct_connection.pgconn.ssl_in_use
                with direct_connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM sellers_seller WHERE id = %s", (seller_id,))
                    assert cursor.fetchone() == (updated_name,)
            checks["independent_direct_connection_confirms_write_and_tls"] = True
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                assert connection.connection.pgconn.ssl_in_use
            checks["pooled_connection_tls"] = True
            stop()
            start(log)
            status, body = request(path)
            assert status == 200 and json.loads(body)["name"] == updated_name
            checks["session_and_data_survive_app_restart"] = True
            assert request(path, method="DELETE")[0] == 204
            try:
                request(path)
                raise AssertionError("Deleted seller is still visible.")
            except HTTPError as error:
                assert error.code == 404
            checks["api_delete_204_then_404"] = True
            assert request("/accounts/logout/", {}, method="POST")[0] == 200
            try:
                request("/api/sellers/")
                raise AssertionError("API remained accessible after logout.")
            except HTTPError as error:
                assert error.code == 403
            checks["logout_and_anonymous_403"] = True
    finally:
        try:
            stop()
        finally:
            if seller_id is not None:
                Seller.objects.filter(pk=seller_id, owner=user).delete()
            for cookie in cookies:
                if cookie.name == "sessionid":
                    Session.objects.filter(session_key=cookie.value).delete()
            if user is not None:
                user.delete()
            if created_group and not group.user_set.exists():
                group.delete()
            connection.close()
    checks["temporary_records_cleaned"] = True
    report["passed"] = True
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
