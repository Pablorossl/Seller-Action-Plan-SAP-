"""Comprobación de sólo lectura de Neon y del servidor local; nunca migra ni siembra.

python scripts/check_neon.py --base-url http://127.0.0.1:8000
No acredita la pertenencia de las conexiones a un proyecto/rama de la cuenta.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, parse_qs
from urllib.request import urlopen

import environ
import psycopg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    local_env = root / ".env"
    environ.Env.read_env(local_env if local_env.is_file() else root / ".env.local")
    primary = os.environ.get("DATABASE_URL", "")
    # También permite diagnosticar las URLs manuales previas, sin cambiar el archivo.
    direct = os.environ.get("DATABASE_URL_UNPOOLED") or primary
    primary_is_pooled = "-pooler" in (urlsplit(primary).hostname or "")
    pooled = primary if primary_is_pooled else os.environ.get("DATABASE_URL_POOLED", "")
    report = {"read_only": True, "project_and_branch_verified": False, "connections": {}}
    complete = True
    for name, value in (("direct", direct), ("pooled", pooled)):
        parsed = urlsplit(value)
        valid = (parsed.scheme in ("postgres", "postgresql") and parsed.hostname
            and parsed.hostname.endswith(".neon.tech")
            and ("-pooler" in parsed.hostname) == (name == "pooled")
            and parse_qs(parsed.query).get("sslmode", [""])[0] in ("require", "verify-ca", "verify-full"))
        if not valid:
            report["connections"][name] = {"ok": False, "error": "Missing or invalid Neon URL with TLS"}
            complete = False
            continue
        try:
            with psycopg.connect(value, connect_timeout=10) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SET TRANSACTION READ ONLY")
                    cursor.execute("SELECT 1")
                    assert cursor.fetchone()[0] == 1
                    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('django_migrations', 'auth_user', 'django_session', 'sellers_seller', 'action_plans_improvementplan') ORDER BY tablename")
                    tables = [row[0] for row in cursor.fetchall()]
                    report["connections"][name] = {
                        "ok": True, "select_1": True, "tls": connection.pgconn.ssl_in_use,
                        "sap_tables_found": tables,
                    }
                    if len(tables) != 5 or not connection.pgconn.ssl_in_use:
                        complete = False
        except psycopg.Error as error:
            # Algunos mensajes del driver incluyen detalles de conexión. No imprimirlos.
            report["connections"][name] = {"ok": False, "error": type(error).__name__, "sqlstate": error.sqlstate}
            complete = False
    report["http"] = {}
    for path in ("/accounts/login/", "/healthz/", "/api/plans/"):
        try:
            with urlopen(args.base_url.rstrip("/") + path, timeout=15) as response:
                status = response.status
        except HTTPError as error:
            status = error.code
        except URLError:
            status = "unreachable"
        report["http"][path] = status
        if status != (403 if path == "/api/plans/" else 200):
            complete = False
    report["read_only_checks_passed"] = complete
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if complete else 1)


if __name__ == "__main__":
    main()
