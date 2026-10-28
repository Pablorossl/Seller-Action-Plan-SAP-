"""QA aislada: PostgreSQL local, TLS de prueba, Gunicorn, navegador y restauración.

python3 scripts/verify_phase3.py
Requiere PostgreSQL (binarios en PATH o --pg-bin), OpenSSL, Playwright/Chromium,
.venv y frontend/dist. Nunca conecta a bases configuradas por el usuario.
"""
import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import ssl
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

from verify_browser import run_flow

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"

SEED = '''
import os
from django.contrib.auth import get_user_model
from django.core.management import call_command
from io import StringIO
for username in ("evaluador_qa", "ajeno_qa"):
    user = get_user_model().objects.create_user(username=username, password=os.environ["SAP_QA_PASSWORD"])
    call_command("configure_plan_agent", username=username, interface_only=True, stdout=StringIO())
call_command("seed_evaluation_demo", owner="evaluador_qa", confirm_fictitious=True, stdout=StringIO())
'''

SNAPSHOT = '''
import hashlib, json
from django.apps import apps
from django.core.serializers.json import DjangoJSONEncoder
labels = ["auth.User", "auth.Group", "auth.Permission", "sellers.Seller", "quality.ThresholdPolicy", "quality.QualityMetric", "action_plans.ImprovementPlan", "action_plans.PlanMetric", "action_plans.PlanAction", "action_plans.PlanReview", "auth.User_groups", "auth.User_user_permissions", "auth.Group_permissions"]
snapshot = {}
for label in labels:
    if label.count("_") and label.startswith("auth."):
        model_name, relation = label.split(".")[1].split("_", 1)
        model = getattr(apps.get_model("auth", model_name), relation).through
    else:
        model = apps.get_model(label)
    rows = list(model.objects.order_by("pk").values())
    payload = json.dumps(rows, sort_keys=True, cls=DjangoJSONEncoder).encode()
    snapshot[label] = {"count": len(rows), "sha256": hashlib.sha256(payload).hexdigest()}
print(json.dumps(snapshot, sort_keys=True))
'''

BENCHMARK = '''
import json, time, statistics
from django.contrib.auth import get_user_model
from django.test import Client
from django.db import connection
from django.test.utils import CaptureQueriesContext
from sellers.models import Seller
from quality.models import QualityMetric, ThresholdPolicy
user = get_user_model().objects.get(username="evaluador_qa")
policies = list(ThresholdPolicy.objects.all())
# Datos exclusivamente ficticios, conocidos y aislados de la base del usuario.
sellers = Seller.objects.bulk_create([Seller(name=f"Tienda Ficticia Volumen {i}", reference=f"QA-VOLUME-{i}", owner=user) for i in range(120)])
QualityMetric.objects.bulk_create([QualityMetric(seller=seller, policy=policy, channel="ficticio-es", period_start="2026-07-01", period_end="2026-07-31", order_count=100, value=6 if policy.code=="incidents" else 99 if policy.unit=="percent" else 12) for seller in sellers for policy in policies])
client = Client(HTTP_HOST="localhost")
client.force_login(user)
result = {}
for path in ("/api/overview/", "/api/sellers/", "/api/plans/", "/api/plans/?status=open"):
    timings = []
    for i in range(5):
        with CaptureQueriesContext(connection) as queries:
            start = time.perf_counter()
            response = client.get(path, secure=True)
            timings.append((time.perf_counter()-start)*1000)
            assert response.status_code == 200, response.content
    result[path] = {"queries": len(queries), "median_ms": round(statistics.median(timings), 2), "max_ms": round(max(timings), 2)}
result["sellers"] = Seller.objects.count()
result["observations"] = QualityMetric.objects.count()
print(json.dumps(result))
'''


def free_port():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pg-bin", default=None)
    parser.add_argument("--artifacts", default="artifacts/phase3")
    args = parser.parse_args()
    pg_bin = Path(args.pg_bin or subprocess.check_output(["pg_config", "--bindir"], text=True).strip())
    artifacts = (ROOT / args.artifacts).resolve()
    artifacts.mkdir(parents=True, exist_ok=True)
    if not (ROOT / "frontend/dist/index.html").exists():
        raise SystemExit("Compila React antes de ejecutar QA.")
    with tempfile.TemporaryDirectory(prefix="sap-phase3-") as temporary:
        tmp = Path(temporary)
        data = tmp / "pgdata"
        cert, key = tmp / "tls.crt", tmp / "tls.key"
        pgport, webport = free_port(), free_port()
        url = f"https://127.0.0.1:{webport}"
        environment = os.environ | {
            "PATH": str(ROOT / ".venv/bin") + os.pathsep + os.environ["PATH"],
            "DJANGO_DEBUG": "False", "DJANGO_SECRET_KEY": secrets.token_urlsafe(64),
            "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1,testserver", "DJANGO_CSRF_TRUSTED_ORIGINS": url,
            "DJANGO_TRUST_PROXY": "False", "RENDER_EXTERNAL_HOSTNAME": "", "SAP_DEMO_MODE": "True",
            "DATABASE_URL": f"postgresql://sap_qa@127.0.0.1:{pgport}/sap_verification?sslmode=require",
            "SAP_QA_PASSWORD": secrets.token_urlsafe(28), "PYTHONUNBUFFERED": "1",
        }
        pg_env = environment | {"PGHOST": "127.0.0.1", "PGPORT": str(pgport), "PGUSER": "sap_qa", "PGSSLMODE": "require"}
        # No incluir contraseñas/URL en los comandos impresos ni en los logs.
        def run(command, name, env=environment, cwd=ROOT):
            print(name, flush=True)
            with (artifacts / f"{name}.log").open("w") as log:
                result = subprocess.run([str(item) for item in command], cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT)
            if result.returncode:
                raise RuntimeError(f"Falló {name}; consulta {artifacts / (name + '.log')}")

        def manage(*arguments, name, env=environment):
            run([PYTHON, "manage.py", *arguments], name, env, ROOT / "backend")

        def shell(code, env=environment):
            result = subprocess.run([str(PYTHON), "manage.py", "shell", "-c", code], cwd=ROOT / "backend", env=env, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(result.stderr)
            return json.loads(result.stdout.strip().splitlines()[-1])

        pg_started = False
        server = None
        server_log = None
        try:
            run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1", "-keyout", key, "-out", cert,
                "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"], "local-certificate")
            key.chmod(0o600)
            run([pg_bin / "initdb", "-D", data, "-A", "trust", "-U", "sap_qa", "--no-locale", "--encoding=UTF8"], "postgres-init")
            # Todos los sockets y los datos quedan bajo el directorio privado temporal.
            pg_options = f"-h 127.0.0.1 -p {pgport} -k {tmp} -c ssl=on -c ssl_cert_file={cert} -c ssl_key_file={key}"
            pg_start = [pg_bin / "pg_ctl", "-D", data, "-l", artifacts / "postgres-server.log", "-o", pg_options, "-w", "start"]
            run(pg_start, "postgres-start")
            pg_started = True
            run([pg_bin / "createdb", "sap_verification"], "database-create", pg_env)
            manage("migrate", "--noinput", name="migrations-fresh")
            manage("makemigrations", "--check", "--dry-run", name="model-drift")
            manage("migrate", "--check", name="migrations-check")
            manage("test", "--verbosity", "2", name="postgres-tests", env=environment | {"DJANGO_DEBUG": "True"})
            manage("check", "--deploy", "--fail-level", "WARNING", name="production-check")
            manage("collectstatic", "--noinput", name="collectstatic")
            manage("shell", "-c", SEED, name="seed-evaluation")
            initial = shell(SNAPSHOT)
            manage("seed_evaluation_demo", "--owner", "evaluador_qa", "--confirm-fictitious", name="seed-repeat")
            assert initial == shell(SNAPSHOT), "La demo no es idempotente"
            tls = ssl.create_default_context(cafile=str(cert))

            def start_web():
                nonlocal server, server_log
                server_log = (artifacts / "gunicorn.log").open("a")
                server = subprocess.Popen([str(PYTHON), "-m", "gunicorn", "config.wsgi:application", "--config", "gunicorn.conf.py",
                    "--bind", f"127.0.0.1:{webport}", "--certfile", str(cert), "--keyfile", str(key)], cwd=ROOT / "backend", env=environment,
                    stdout=server_log, stderr=subprocess.STDOUT)
                for _ in range(100):
                    if server.poll() is not None:
                        raise RuntimeError("Gunicorn no arrancó; consulta gunicorn.log")
                    try:
                        with urllib.request.urlopen(url + "/healthz/", context=tls, timeout=2) as response:
                            assert response.status == 200
                        return
                    except OSError:
                        time.sleep(.1)
                raise RuntimeError("Gunicorn no responde")

            def stop_web():
                nonlocal server, server_log
                if server:
                    server.terminate()
                    server.wait(timeout=15)
                    server = None
                if server_log:
                    server_log.close()
                    server_log = None

            start_web()
            browser = run_flow(base=url, username="evaluador_qa", password=environment["SAP_QA_PASSWORD"],
                other_username="ajeno_qa", other_password=environment["SAP_QA_PASSWORD"], seller_reference="SAP-DEMO-PLAN",
                artifacts=artifacts / "browser", local_tls=True)
            before = shell(SNAPSHOT)
            run([pg_bin / "pg_ctl", "-D", data, "-m", "fast", "-w", "stop"], "postgres-stop")
            pg_started = False
            try:
                urllib.request.urlopen(url + "/healthz/", context=tls, timeout=10)
                raise AssertionError("Readiness debe fallar sin PostgreSQL")
            except urllib.error.HTTPError as error:
                assert error.code == 503
            run(pg_start, "postgres-restart")
            pg_started = True
            assert before == shell(SNAPSHOT), "Pérdida de datos después de reiniciar PostgreSQL"
            stop_web()
            manage("collectstatic", "--noinput", name="collectstatic-repeat")
            run(["bash", "scripts/release.sh"], "release-repeat")
            start_web()
            assert before == shell(SNAPSHOT), "Pérdida de datos después de reiniciar Gunicorn"
            backup = tmp / "sap.dump"
            run([pg_bin / "pg_dump", "--format=custom", "--no-owner", "--no-acl", "--file", backup, "sap_verification"], "backup", pg_env)
            run([pg_bin / "createdb", "sap_restoration"], "restore-database-create", pg_env)
            run([pg_bin / "pg_restore", "--exit-on-error", "--single-transaction", "--no-owner", "--no-acl", "--dbname", "sap_restoration", backup], "restore", pg_env)
            restored_env = environment | {"DATABASE_URL": environment["DATABASE_URL"].replace("/sap_verification?", "/sap_restoration?")}
            assert before == shell(SNAPSHOT, restored_env), "La restauración no coincide con los datos originales"
            manage("migrate", "--check", name="restored-migrations", env=restored_env)
            benchmark = shell(BENCHMARK)
            stop_web()
            report = {"environment": "local isolated; not a public deployment", "database": subprocess.check_output([str(pg_bin / "postgres"), "--version"], text=True).strip(),
                "browser": browser, "postgres_restart_persistence": True, "gunicorn_restart_persistence": True,
                "release_repeat_persistence": True, "backup_restored_separately": True, "snapshot": before, "benchmark": benchmark}
            (artifacts / "result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
            print(json.dumps({key: value for key, value in report.items() if key != "snapshot"}, ensure_ascii=False), flush=True)
        finally:
            if server:
                server.terminate()
                server.wait(timeout=15)
            if server_log:
                server_log.close()
            if pg_started:
                subprocess.run([str(pg_bin / "pg_ctl"), "-D", str(data), "-m", "fast", "-w", "stop"], stdout=subprocess.DEVNULL, check=True)
        print(f"QA terminada; recursos temporales eliminados. Evidencia: {artifacts}", flush=True)


if __name__ == "__main__":
    main()
