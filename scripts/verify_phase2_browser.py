"""Verificación opcional con Playwright y SQLite temporal; no toca la base local.

Ejecutar con un Python que tenga Playwright y Chromium instalados:
    python scripts/verify_phase2_browser.py
Requiere .venv/bin/python y frontend/dist ya compilado.
"""
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
import urllib.request

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / ".venv/bin/python"
ARTIFACTS = ROOT / "docs/screenshots"
ARTIFACTS.mkdir(exist_ok=True)

SEED = '''
import json, os
from datetime import date
from django.contrib.auth import get_user_model
from django.core.management import call_command
from sellers.models import Seller
from quality.models import QualityMetric, ThresholdPolicy
from action_plans.models import ImprovementPlan, PlanMetric, PlanAction
from io import StringIO
User = get_user_model()
agent = User.objects.create_user(username="agente_demo", first_name="Pablo", password=os.environ["SAP_QA_PASSWORD"])
other = User.objects.create_user(username="agente_ajeno", password=os.environ["SAP_QA_PASSWORD"])
for user in (agent, other):
    call_command("configure_plan_agent", username=user.username, stdout=StringIO())
agent.is_staff = False
agent.save()
call_command("seed_demo", owner=agent.username, stdout=StringIO())
seller = Seller.objects.create(name="Tienda Ficticia Envíos", reference="SAP-FASE2-DEMO", owner=agent)
policy = ThresholdPolicy.objects.get(code="incidents", version=1)
metric = QualityMetric.objects.create(seller=seller, policy=policy, channel="demo-es", period_start="2026-07-01", period_end="2026-07-31", order_count=100, value=6)
for i, title in enumerate(["Mejorar la preparación de envíos", "Revisar las incidencias recurrentes", "Documentar el control de embalaje"]):
    plan = ImprovementPlan.objects.create(seller=seller, title=title, problem="Incidencias de una muestra ficticia del 6%", root_cause="Embalaje insuficiente", evidence="100 pedidos ficticios", objective="Reducir al 3%", period_start="2026-07-01", period_end="2026-07-31", responsible=agent, created_by=agent, due_date="2026-12-31", next_review_on="2026-10-23")
    PlanMetric.objects.create(plan=plan, baseline=metric, target_value=3)
    PlanAction.objects.create(plan=plan, description=title, kind="corrective", responsible="Equipo ficticio de logística", due_date="2026-10-22" if i == 0 else "2026-10-25")
    plan.status = "in_progress"
    plan.save()
print(json.dumps({"seller": seller.pk, "metric": metric.pk}))
'''


def main():
    password = secrets.token_urlsafe(24)
    with tempfile.TemporaryDirectory(prefix="sap-browser-") as tmp:
        env = os.environ | {"DATABASE_URL": f"sqlite:///{tmp}/qa.sqlite3", "DJANGO_DEBUG": "True", "DJANGO_ALLOWED_HOSTS": "127.0.0.1,localhost,testserver", "SAP_QA_PASSWORD": password}
        subprocess.run([str(PYTHON), "manage.py", "migrate", "--noinput"], cwd=ROOT / "backend", env=env, check=True, stdout=subprocess.DEVNULL)
        result = subprocess.run([str(PYTHON), "manage.py", "shell", "-c", SEED], cwd=ROOT / "backend", env=env, check=True, capture_output=True, text=True)
        json.loads(result.stdout.strip().splitlines()[-1])  # Verificar que terminó la carga.
        log = open(Path(tmp) / "server.log", "w+")
        server = subprocess.Popen([str(PYTHON), "manage.py", "runserver", "127.0.0.1:8765", "--noreload"], cwd=ROOT / "backend", env=env, stdout=log, stderr=log)
        try:
            for _ in range(100):
                if server.poll() is not None:
                    log.seek(0)
                    raise RuntimeError(log.read())
                try:
                    urllib.request.urlopen("http://127.0.0.1:8765/accounts/login/")
                    break
                except OSError:
                    time.sleep(.1)
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context(viewport={"width": 1440, "height": 1060}, locale="es-ES", timezone_id="Europe/Madrid")
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                base = "http://127.0.0.1:8765"
                page.goto(base + "/dashboard/")
                page.get_by_label("Nombre de usuario").fill("agente_demo")
                page.get_by_label("Contraseña").fill(password)
                page.get_by_role("button", name="Entrar en mi espacio").click()
                expect(page.get_by_role("heading", name="Hola, Pablo")).to_be_visible()
                expect(page.get_by_role("heading", name="Prioridades de la semana")).to_be_visible()
                page.evaluate("window.scrollTo(0, 0)")
                page.screenshot(path=str(ARTIFACTS / "fase-2-dashboard.png"), full_page=True)
                page.get_by_role("link", name="Vendedores", exact=True).click()
                page.get_by_label("Buscar por nombre o identificador…").fill("SAP-FASE2-DEMO")
                page.get_by_role("button", name="Buscar", exact=True).click()
                page.get_by_role("link", name="Tienda Ficticia Envíos", exact=True).click()
                expect(page.get_by_role("heading", name="Tienda Ficticia Envíos", exact=True)).to_be_visible()
                expect(page.get_by_text("6 %", exact=True)).to_be_visible()
                page.evaluate("window.scrollTo(0, 0)")
                page.screenshot(path=str(ARTIFACTS / "fase-2-vendedor.png"), full_page=True)
                page.get_by_role("link", name="Crear plan", exact=True).click()
                expect(page.get_by_role("heading", name="Cada mejora empieza con un plan")).to_be_visible()
                for label, text in {"Título del plan": "Reducir incidencias del 6% al 3%", "Problema identificado": "Incidencias del 6% en los pedidos ficticios.", "Causa raíz": "Embalaje insuficiente.", "Evidencia del diagnóstico": "100 pedidos de prueba.", "Objetivo de mejora": "Alcanzar el 3% de incidencias."}.items():
                    page.get_by_label(label, exact=False).fill(text)
                page.get_by_label("Objetivo · %").fill("7")
                page.get_by_label("Fecha objetivo del plan").fill("2026-12-31")
                page.get_by_label("Próxima revisión").fill("2026-10-23")
                page.get_by_role("button", name="Crear borrador").click()
                expect(page.get_by_role("alert")).to_contain_text("El objetivo debe mejorar")
                expect(page.get_by_label("Título del plan")).to_have_value("Reducir incidencias del 6% al 3%")
                page.get_by_label("Objetivo · %").fill("3")
                page.get_by_role("button", name="Crear borrador").click()
                expect(page.get_by_role("heading", name="Reducir incidencias del 6% al 3%", exact=True)).to_be_visible()
                plan_url = page.url
                page.get_by_role("button", name="Editar plan", exact=True).click()
                page.get_by_label("Causa raíz").fill("Embalaje insuficiente y falta de control previo.")
                page.get_by_role("button", name="Guardar cambios").click()
                expect(page.get_by_text("Embalaje insuficiente y falta de control previo.", exact=True)).to_be_visible()
                for description, kind in [("Revisar preparación y expedición de pedidos", "corrective"), ("Control previo de incidencias recurrentes", "preventive")]:
                    page.get_by_role("button", name="Añadir acción").click()
                    dialog = page.get_by_role("dialog")
                    dialog.get_by_label("Descripción de la acción").fill(description)
                    dialog.get_by_label("Tipo", exact=False).select_option(kind)
                    dialog.get_by_label("Persona o equipo responsable").fill("Equipo ficticio de logística")
                    dialog.get_by_label("Fecha límite").fill("2026-10-23")
                    dialog.get_by_role("button", name="Añadir acción").click()
                    expect(dialog).not_to_be_visible()
                page.get_by_role("button", name="Activar plan").click()
                expect(page.get_by_role("button", name="Pasar a revisión")).to_be_visible()
                page.get_by_role("button", name="Editar acción: Revisar preparación").click()
                dialog = page.get_by_role("dialog")
                dialog.get_by_label("Estado", exact=False).select_option("completed")
                dialog.get_by_label("Fecha de finalización").fill("2026-10-23")
                dialog.get_by_label("Evidencia de ejecución").fill("Protocolo revisado y aplicado a la muestra ficticia.")
                dialog.get_by_role("button", name="Guardar acción").click()
                expect(dialog).not_to_be_visible()
                for observed, start, end in [("4.5", "2026-08-01", "2026-08-31"), ("3", "2026-09-01", "2026-09-30")]:
                    page.get_by_role("button", name="Registrar revisión").click()
                    dialog = page.get_by_role("dialog")
                    dialog.get_by_label("Valor observado").fill(observed)
                    dialog.get_by_label("Pedidos del periodo").fill("100")
                    dialog.get_by_label("Inicio del periodo medido").fill(start)
                    dialog.get_by_label("Fin del periodo medido").fill(end)
                    dialog.get_by_label("Fecha de revisión").fill("2026-10-23")
                    dialog.get_by_label("Evolución y evidencias").fill("Mejora observada en la muestra ficticia.")
                    dialog.get_by_role("button", name="Guardar revisión").click()
                    expect(dialog).not_to_be_visible()
                expect(page.get_by_text("Objetivo alcanzado", exact=True).first).to_be_visible()
                page.evaluate("window.scrollTo(0, 0)")
                page.screenshot(path=str(ARTIFACTS / "fase-2-plan.png"), full_page=True)
                page.get_by_role("button", name="Finalizar plan", exact=True).click()
                dialog = page.get_by_role("dialog")
                dialog.get_by_label("Resultado y razones").fill("Incidencias reducidas al 3%. Se conserva una acción preventiva pendiente.")
                dialog.get_by_role("checkbox").check()
                dialog.get_by_role("button", name="Confirmar finalización").click()
                expect(dialog).not_to_be_visible()
                expect(page.get_by_role("heading", name="Resultado y cierre")).to_be_visible()
                page.reload()
                expect(page.get_by_role("heading", name="Resultado y cierre")).to_be_visible()
                expect(page.get_by_text("Incidencias reducidas al 3%.", exact=False)).to_be_visible()
                expect(page.get_by_role("button", name="Finalizar plan", exact=True)).to_have_count(0)
                page.evaluate("window.scrollTo(0, 0)")
                page.screenshot(path=str(ARTIFACTS / "fase-2-cierre.png"), full_page=True)
                # Sin desbordamientos globales, navegación y modal accesibles en móvil.
                page.set_viewport_size({"width": 390, "height": 844})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Desbordamiento móvil"
                page.evaluate("window.scrollTo(0, 0)")
                page.screenshot(path=str(ARTIFACTS / "fase-2-movil.png"), full_page=True)
                page.get_by_role("button", name="Mostrar navegación").click()
                page.get_by_role("link", name="Vendedores", exact=True).click()
                expect(page.get_by_role("heading", name="Vendedores", exact=True)).to_be_visible()
                page.get_by_label("Buscar por nombre o identificador…").fill("NO-EXISTE")
                page.get_by_role("button", name="Buscar", exact=True).click()
                expect(page.get_by_role("heading", name="No se encontraron vendedores")).to_be_visible()
                # La denegación procede del backend real, con otra sesión autorizada.
                other = browser.new_context(viewport={"width": 1280, "height": 900})
                other_page = other.new_page()
                other_page.goto(base + "/accounts/login/")
                other_page.get_by_label("Nombre de usuario").fill("agente_ajeno")
                other_page.get_by_label("Contraseña").fill(password)
                other_page.get_by_role("button", name="Entrar en mi espacio").click()
                other_page.goto(plan_url)
                expect(other_page.get_by_role("alert")).to_contain_text("No se encuentra este registro")
                # Estados transitorios del frontend, aislados del flujo persistido anterior.
                page.set_viewport_size({"width": 1440, "height": 1060})
                page.route("**/api/sellers/?*", lambda route: route.abort())
                page.goto(base + "/dashboard/#/sellers")
                page.reload()
                expect(page.get_by_role("alert")).to_contain_text("No se pudo conectar")
                page.unroute("**/api/sellers/?*")
                page.get_by_role("button", name="Volver a intentar").click()
                expect(page.get_by_role("link", name="Tienda Ficticia Envíos", exact=True)).to_be_visible()
                page.route("**/api/plans/?*", lambda route: route.fulfill(status=403, content_type="application/json", body='{"detail":"Permission denied"}'))
                page.goto(base + "/dashboard/#/plans")
                expect(page.get_by_role("alert")).to_contain_text("Tu sesión ha caducado o no tienes permiso")
                page.unroute("**/api/plans/?*")
                pending = []
                page.route("**/api/overview/", lambda route: pending.append(route))
                page.goto(base + "/dashboard/#/")
                expect(page.get_by_role("status")).to_contain_text("Cargando información")
                page.wait_for_timeout(200)
                for route in pending:
                    route.continue_()
                page.unroute("**/api/overview/")
                expect(page.get_by_role("heading", name="Prioridades de la semana")).to_be_visible()
                assert not errors, errors
                browser.close()
                print("OK: login, dashboard, búsqueda, ficha, validación conservando datos, plan, dos acciones, finalización de acción, revisiones 6 → 4,5 → 3, cierre, recarga, móvil, aislamiento, vacío, red y 403.")
                print(f"Capturas: {ARTIFACTS}")
        finally:
            server.terminate()
            server.wait(timeout=10)
            log.close()


if __name__ == "__main__":
    main()
