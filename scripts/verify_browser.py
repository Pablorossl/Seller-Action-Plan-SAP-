"""Recorrido real de evaluación. Requiere Playwright/Chromium sólo en QA.

Uso público (escribe exclusivamente en una cuenta ficticia autorizada):
python scripts/verify_browser.py --url https://DOMINIO --username evaluador \
  --other-username otro_agente --seller-reference SAP-DEMO-PLAN --allow-writes
Solicita las contraseñas de forma privada; verifica el certificado público.
"""
import argparse
from datetime import date, timedelta
from getpass import getpass
import json
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from playwright.sync_api import sync_playwright, expect


def run_flow(*, base, username, password, other_username, other_password,
             seller_reference, artifacts, local_tls=False):
    artifacts = Path(artifacts)
    artifacts.mkdir(parents=True, exist_ok=True)
    title = f"QA: reducir incidencias 6% → 3% ({uuid4().hex[:8]})"
    today = date.today().isoformat()
    due = (date.today() + timedelta(days=30)).isoformat()
    errors, failed_responses = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1060}, locale="es-ES",
            timezone_id="Europe/Madrid", ignore_https_errors=local_tls)
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("response", lambda response: failed_responses.append(f"{response.status} {urlsplit(response.url).path}")
            if response.status >= 500 or ("/static/" in response.url and response.status >= 400) else None)
        page.goto(base + "/dashboard/")
        expect(page.get_by_role("button", name="Entrar en mi espacio")).to_be_visible()
        page.screenshot(path=str(artifacts / "login.png"), full_page=True)
        page.get_by_label("Nombre de usuario").fill(username)
        page.get_by_label("Contraseña").fill(password)
        page.get_by_role("button", name="Entrar en mi espacio").click()
        expect(page.get_by_role("heading", name="Prioridades de la semana")).to_be_visible()
        page.screenshot(path=str(artifacts / "dashboard.png"), full_page=True)
        cookies = {cookie["name"]: cookie for cookie in context.cookies()}
        assert cookies["sessionid"]["secure"] and cookies["sessionid"]["httpOnly"]
        assert cookies["csrftoken"]["secure"]
        health_response = context.request.get(base + "/healthz/")
        assert health_response.status == 200
        assert health_response.json() == {"status": "ok"}
        workspace = context.request.get(base + "/api/workspace/").json()
        assert workspace["permissions"]["close_improvementplan"]
        page.get_by_role("link", name="Vendedores", exact=True).click()
        page.get_by_label("Buscar por nombre o identificador…").fill(seller_reference)
        page.get_by_role("button", name="Buscar", exact=True).click()
        seller_link = page.get_by_role("link", name="Tienda Ficticia Envíos", exact=True)
        try:
            expect(seller_link).to_be_visible(timeout=10000)
        except AssertionError:
            page.screenshot(path=str(artifacts / "failure.png"), full_page=True)
            (artifacts / "failure.txt").write_text(page.locator("body").inner_text())
            raise
        seller_link.click()
        expect(page.get_by_text("6 %", exact=True)).to_be_visible()
        page.screenshot(path=str(artifacts / "vendedor.png"), full_page=True)
        page.locator("section").filter(has=page.get_by_role("heading", name="Indicadores de calidad")).screenshot(path=str(artifacts / "indicadores.png"))
        page.get_by_role("link", name="Crear plan", exact=True).click()
        for label, value in {"Título del plan": title, "Problema identificado": "Incidencias del 6% en pedidos ficticios.",
            "Causa raíz": "Embalaje insuficiente.", "Evidencia del diagnóstico": "100 pedidos ficticios.",
            "Objetivo de mejora": "Alcanzar el 3% de incidencias."}.items():
            page.get_by_label(label, exact=False).fill(value)
        page.get_by_label("Objetivo · %").fill("7")
        page.get_by_label("Fecha objetivo del plan").fill(due)
        page.get_by_label("Próxima revisión").fill(today)
        page.get_by_label("Objetivo · %").fill("3")
        page.screenshot(path=str(artifacts / "formulario-plan.png"), full_page=True)
        page.get_by_label("Objetivo · %").fill("7")
        page.get_by_role("button", name="Crear borrador").click()
        expect(page.get_by_role("alert")).to_contain_text("El objetivo debe mejorar")
        expect(page.get_by_label("Título del plan")).to_have_value(title)
        page.get_by_label("Objetivo · %").fill("3")
        page.get_by_role("button", name="Crear borrador").click()
        expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()
        plan_url = page.url
        plan_id = int(urlsplit(plan_url).fragment.split("/")[-1])
        page.screenshot(path=str(artifacts / "detalle-plan.png"), full_page=True)
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
            dialog.get_by_label("Fecha límite").fill(today)
            dialog.get_by_role("button", name="Añadir acción").click()
            expect(dialog).not_to_be_visible()
        page.get_by_role("button", name="Activar plan").click()
        expect(page.get_by_role("button", name="Pasar a revisión")).to_be_visible()
        page.get_by_role("button", name="Pasar a revisión").click()
        expect(page.get_by_role("button", name="Continuar en progreso")).to_be_visible()
        page.get_by_role("button", name="Editar acción: Revisar preparación").click()
        dialog = page.get_by_role("dialog")
        dialog.get_by_label("Estado", exact=False).select_option("completed")
        dialog.get_by_label("Fecha de finalización").fill(today)
        dialog.get_by_label("Evidencia de ejecución").fill("Protocolo aplicado a una muestra ficticia.")
        dialog.screenshot(path=str(artifacts / "accion.png"))
        dialog.get_by_role("button", name="Guardar acción").click()
        expect(dialog).not_to_be_visible()
        for observed, start, end in [("4.5", "2026-08-01", "2026-08-31"), ("3", "2026-09-01", "2026-09-30")]:
            page.get_by_role("button", name="Registrar revisión").click()
            dialog = page.get_by_role("dialog")
            dialog.get_by_label("Valor observado").fill(observed)
            dialog.get_by_label("Pedidos del periodo").fill("100")
            dialog.get_by_label("Inicio del periodo medido").fill(start)
            dialog.get_by_label("Fin del periodo medido").fill(end)
            dialog.get_by_label("Fecha de revisión").fill(today)
            dialog.get_by_label("Evolución y evidencias").fill("Mejora observada en la muestra ficticia.")
            dialog.get_by_role("button", name="Guardar revisión").click()
            expect(dialog).not_to_be_visible()
        expect(page.get_by_text("Objetivo alcanzado", exact=True).first).to_be_visible()
        page.screenshot(path=str(artifacts / "revisiones.png"), full_page=True)
        page.locator("section").filter(has=page.get_by_role("heading", name="Revisiones y evolución")).screenshot(path=str(artifacts / "historial-revisiones.png"))
        page.locator("section").filter(has=page.get_by_role("heading", name="Diagnóstico y objetivos")).screenshot(path=str(artifacts / "evaluacion.png"))
        page.get_by_role("button", name="Finalizar plan", exact=True).click()
        dialog = page.get_by_role("dialog")
        dialog.get_by_label("Resultado y razones").fill("Incidencias reducidas al 3%. Acción preventiva pendiente conservada.")
        dialog.get_by_role("checkbox").check()
        dialog.screenshot(path=str(artifacts / "confirmacion-cierre.png"))
        dialog.get_by_role("button", name="Confirmar finalización").click()
        expect(dialog).not_to_be_visible()
        page.reload()
        expect(page.get_by_role("heading", name="Resultado y cierre")).to_be_visible()
        expect(page.get_by_role("button", name="Finalizar plan", exact=True)).to_have_count(0)
        detail_url = base + f"/api/plans/{plan_id}/"
        detail = context.request.get(detail_url).json()
        assert detail["status"] == "closed" and len(detail["actions"]) == 2 and len(detail["reviews"]) == 2
        assert detail["closure_evaluation"]["result"] == "achieved"
        assert context.request.patch(detail_url, data={"title": "Sin CSRF"}).status == 403
        page.screenshot(path=str(artifacts / "cierre.png"), full_page=True)
        page.locator("section").filter(has=page.get_by_role("heading", name="Resultado y cierre")).screenshot(path=str(artifacts / "resultado-cierre.png"))
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Desbordamiento móvil"
        page.screenshot(path=str(artifacts / "movil.png"), full_page=True)
        page.set_viewport_size({"width": 1440, "height": 1060})
        page.get_by_role("link", name="Planes de mejora", exact=True).click()
        expect(page.get_by_role("heading", name="Planes de mejora", exact=True)).to_be_visible()
        expect(page.get_by_role("link", name=title, exact=True)).to_be_visible()
        page.screenshot(path=str(artifacts / "planes.png"), full_page=True)
        page.get_by_role("link", name="Vendedores", exact=True).click()
        expect(page.get_by_role("heading", name="Vendedores", exact=True)).to_be_visible()
        expect(page.get_by_role("link", name="Tienda Ficticia Envíos", exact=True)).to_be_visible()
        page.screenshot(path=str(artifacts / "vendedores.png"), full_page=True)
        # Evidencia de consumo real: guardar sólo datos de negocio ficticios,
        # nunca el token CSRF ni cookies/cabeceras de autenticación.
        (artifacts / "react-django.json").write_text(json.dumps({
            "endpoint": f"/api/plans/{plan_id}/", "status": detail["status"],
            "evaluation": detail["closure_evaluation"],
        }, indent=2, ensure_ascii=False) + "\n")
        other = browser.new_context(ignore_https_errors=local_tls)
        other_page = other.new_page()
        other_page.goto(base + "/accounts/login/")
        other_page.get_by_label("Nombre de usuario").fill(other_username)
        other_page.get_by_label("Contraseña").fill(other_password)
        other_page.get_by_role("button", name="Entrar en mi espacio").click()
        expect(other_page.get_by_role("heading", name="Prioridades de la semana")).to_be_visible()
        assert other.request.get(detail_url).status == 404
        token = other.request.get(base + "/api/workspace/").json()["csrf_token"]
        assert other.request.post(detail_url + "close/", data={"notes": "Ajeno", "confirm": True}, headers={"X-CSRFToken": token, "Referer": base + "/dashboard/"}).status == 404
        other_page.goto(plan_url)
        expect(other_page.get_by_role("alert")).to_contain_text("No se encuentra este registro")
        page.get_by_role("button", name="Cerrar sesión").click()
        expect(page.get_by_role("button", name="Entrar en mi espacio")).to_be_visible()
        assert context.request.get(detail_url).status == 403
        assert not errors and not failed_responses, (errors, failed_responses)
        browser.close()
    report = {"url": base, "environment": "local TLS de prueba" if local_tls else "public",
        "plan_id": plan_id, "flow": "6 → 4.5 → 3", "status": "closed", "result": "achieved",
        "reload": True, "logout": True, "csrf": True, "other_agent_denied": True, "mobile_width": 390,
        "page_errors": errors, "critical_responses": failed_responses}
    (artifacts / "browser-result.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, ensure_ascii=False), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--other-username", required=True)
    parser.add_argument("--seller-reference", default="SAP-DEMO-PLAN")
    parser.add_argument("--artifacts", default="artifacts/public-browser")
    parser.add_argument("--allow-writes", action="store_true")
    args = parser.parse_args()
    parsed = urlsplit(args.url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.path not in ("", "/") or parsed.username or parsed.query or parsed.fragment:
        parser.error("Indica un origen HTTPS sin ruta ni credenciales.")
    if not args.allow_writes:
        parser.error("El recorrido crea un plan ficticio. Requiere --allow-writes en una cuenta de evaluación autorizada.")
    run_flow(base=args.url.rstrip("/"), username=args.username, password=getpass("Contraseña del evaluador: "),
        other_username=args.other_username, other_password=getpass("Contraseña del agente ajeno: "),
        seller_reference=args.seller_reference, artifacts=args.artifacts)


if __name__ == "__main__":
    main()
