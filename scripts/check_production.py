"""Comprueba los ajustes de producción con valores ficticios; no conecta a PostgreSQL."""
import os
from pathlib import Path
import secrets
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
environment = os.environ.copy()
environment.update({
    "DJANGO_DEBUG": "False",
    "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
    "DJANGO_ALLOWED_HOSTS": "sap.example.invalid",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "https://sap.example.invalid",
    "DATABASE_URL": "postgresql://placeholder:placeholder@127.0.0.1:5432/sap?sslmode=require",
    "DJANGO_TRUST_PROXY": "True",
})
print("Comprobación estática con configuración ficticia; no valida un despliegue ni una conexión PostgreSQL.", flush=True)
subprocess.run([sys.executable, "manage.py", "check", "--deploy", "--fail-level", "WARNING"],
    cwd=root / "backend", env=environment, check=True)
