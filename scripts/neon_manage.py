"""Comandos Django explícitos sobre la URL directa de Neon, sin mostrar secretos.

Desde la raíz con el venv: python scripts/neon_manage.py migrate --plan
No modifica DATABASE_URL en disco ni cambia la conexión pooled de la aplicación.
"""
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit, parse_qs

import environ


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python scripts/neon_manage.py <comando Django> [opciones]")
    root = Path(__file__).resolve().parents[1]
    local_env = root / ".env"
    environ.Env.read_env(local_env if local_env.is_file() else root / ".env.local")
    direct = os.environ.get("DATABASE_URL_UNPOOLED", "")
    try:
        parsed = urlsplit(direct)
        tls = parse_qs(parsed.query).get("sslmode", [""])[0]
        valid = (parsed.scheme in ("postgres", "postgresql") and parsed.hostname
            and "-pooler" not in parsed.hostname and tls in ("require", "verify-ca", "verify-full"))
    except ValueError:
        valid = False
    if not valid:
        raise SystemExit("Configura DATABASE_URL_UNPOOLED con la URL directa PostgreSQL y TLS de Neon. Ejecuta neon env pull.")
    # El entorno del hijo prevalece sobre los .env que lee Django.
    result = subprocess.run([sys.executable, "manage.py", *sys.argv[1:]],
        cwd=root / "backend", env=os.environ | {"DATABASE_URL": direct})
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
