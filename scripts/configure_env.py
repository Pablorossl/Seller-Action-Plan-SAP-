"""Genera configuración local sin mostrar secretos ni sobrescribir un .env existente."""
from pathlib import Path
import secrets

root = Path(__file__).resolve().parent.parent
destination = root / ".env"
if destination.exists():
    print(".env ya existe; se conserva sin cambios.")
else:
    content = (root / ".env.example").read_text(encoding="utf-8")
    content = content.replace("DJANGO_SECRET_KEY=\n", f"DJANGO_SECRET_KEY={secrets.token_urlsafe(64)}\n")
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(content)
    destination.chmod(0o600)
    print(".env local creado con una clave aleatoria. No lo versiones ni lo reutilices en producción.")
