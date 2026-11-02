"""Build nativo Django: React empaquetado; sin conexiones ni escrituras a la BD."""
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    backend = Path(__file__).resolve().parent
    frontend = backend.parent / "frontend"
    if not (frontend / "package-lock.json").is_file():
        raise SystemExit("Activa 'Include source files outside of the Root Directory in the Build Step' en Vercel.")
    subprocess.run(["npm", "ci", "--include=dev", "--no-audit", "--no-fund"], cwd=frontend, check=True)
    subprocess.run(["npm", "run", "build"], cwd=frontend, check=True)
    source = frontend / "dist"
    if not (source / "index.html").is_file() or not (source / "assets").is_dir():
        raise SystemExit("El build de React no ha generado index.html y assets/.")
    destination = backend / "frontend_dist"
    # Sólo se sustituye el artefacto generado, nunca datos ni archivos fuente.
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    subprocess.run([sys.executable, "manage.py", "check", "--deploy", "--fail-level", "WARNING"], cwd=backend, check=True)
    # El preset Django de Vercel ejecuta collectstatic y publica STATIC_ROOT en CDN.
    # Migraciones y semillas son operaciones manuales separadas desde Ubuntu.
    print("React preparado en backend/frontend_dist. Build sin migraciones ni semillas.")


if __name__ == "__main__":
    main()
