"""Verifica build y paquete Django aislado, sin cuenta Vercel ni conexión a una BD.

Usar el Python del venv y Node 22: python scripts/verify_vercel.py
No invoca Vercel CLI ni publica. PostgreSQL ficticio deliberadamente inaccesible.
"""
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

PROBE = r'''
import re
from pathlib import Path
from config.wsgi import application
from django.conf import settings
from django.db import connection
from django.template.loader import get_template
from django.test import Client

assert callable(application)
assert connection.connection is None, "WSGI no debe abrir PostgreSQL al importar"
assert not settings.DEBUG
assert settings.DATABASES["default"]["CONN_MAX_AGE"] == 0
assert settings.DATABASES["default"]["DISABLE_SERVER_SIDE_CURSORS"]
assert settings.DATABASES["default"]["OPTIONS"]["sslmode"] == "require"
assert settings.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
assert not settings.USE_X_FORWARDED_HOST
assert not (settings.ROOT_DIR / "frontend").exists()
assert not (settings.BASE_DIR / "db.sqlite3").exists()
for name in ("base.html", "home.html", "registration/login.html", "registration/locked_out.html", "index.html"):
    get_template(name)
html = get_template("index.html").render()
assets = re.findall(r'(?:src|href)="(/static/react/assets/[^\"]+)"', html)
assert len(assets) >= 2, "Faltan JS/CSS compilados en index.html"
client = Client(HTTP_HOST="sap.example.invalid", HTTP_X_FORWARDED_PROTO="https")
response = client.get("/accounts/login/")
assert response.status_code == 200
assert response.cookies["csrftoken"]["secure"]
assert "max-age=" in response["Strict-Transport-Security"]
assert client.get("/dashboard/").status_code == 302
assert client.get("/api/plans/").status_code == 403
for path in (*assets, "/static/sap/auth.css", "/static/admin/css/base.css"):
    assert (Path(settings.STATIC_ROOT) / path.removeprefix("/static/")).is_file(), path
    response = client.get(path)
    assert response.status_code == 200, path
    if response.streaming:
        assert b"".join(response.streaming_content), path
assert not (Path(settings.STATIC_ROOT) / "react/index.html").exists()
assert client.get("/static/react/index.html").status_code == 404
assert client.get("/accounts/login/", HTTP_HOST="untrusted.example.invalid").status_code == 400
assert client.get("/accounts/login/", HTTP_X_FORWARDED_PROTO="http").status_code == 301
assert client.get("/healthz/", HTTP_X_FORWARDED_PROTO="http").status_code == 301
assert connection.connection is None, "Las comprobaciones no necesitan SQL"
print("OK: paquete backend aislado, WSGI sin SQL, plantillas, JS/CSS, rutas, HTTPS y hosts.")
'''


def main():
    environment = os.environ | {
        "VERCEL": "1", "VERCEL_ENV": "production", "DJANGO_DEBUG": "False",
        "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
        "DJANGO_ALLOWED_HOSTS": "sap.example.invalid",
        "DJANGO_CSRF_TRUSTED_ORIGINS": "https://sap.example.invalid",
        "DATABASE_URL": "postgresql://placeholder:placeholder@127.0.0.1:1/sap?sslmode=require",
        "SAP_DEMO_MODE": "False", "DJANGO_TRUST_PROXY": "False",
    }
    print("Validación LOCAL del build y los archivos; no es un despliegue Vercel.", flush=True)
    subprocess.run([sys.executable, "build_vercel.py"], cwd=ROOT / "backend", env=environment, check=True)
    with tempfile.TemporaryDirectory(prefix="sap-vercel-package-") as temporary:
        backend = Path(temporary) / "backend"
        shutil.copytree(ROOT / "backend", backend, ignore=shutil.ignore_patterns(
            "*.sqlite3", "*.sqlite3-*", "staticfiles", "__pycache__", ".env*", ".vercel", ".venv"))
        subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"], cwd=backend, env=environment, check=True)
        subprocess.run([sys.executable, "-c", PROBE], cwd=backend, env=environment, check=True)


if __name__ == "__main__":
    main()
