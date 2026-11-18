"""Chromium, Django y SQLite temporal. Ejecutar tras compilar React."""
from secrets import token_urlsafe
from tempfile import TemporaryDirectory
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import verify_login


def prepare(manage):
    # Ejercita el orden real de actualización, con un vendedor y un plan previos.
    manage("migrate", "auth")
    manage("migrate", "action_plans")
    manage("shell", "-c", """import os
from django.contrib.auth import get_user_model
from django.core.management import call_command
user = get_user_model().objects.create_user(username='evaluador', password=os.environ['SAP_QA_PASSWORD'])
call_command('configure_plan_agent', username=user.username, interface_only=True)
call_command('seed_plan_demo', owner=user.username)
""")
    manage("migrate", "--noinput")


def verify(base, password):
    with sync_playwright() as runner:
        browser = runner.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))

        def login(username, secret):
            page.goto(base + "/")
            page.get_by_label("Nombre de usuario").fill(username)
            page.get_by_label("Contraseña", exact=True).fill(secret)
            page.get_by_role("button", name="Iniciar sesión").click()
            page.wait_for_url(base + "/dashboard/")
            expect(page.get_by_role("heading", name="Prioridades de la semana")).to_be_visible()

        def logout():
            page.get_by_role("button", name="Cerrar sesión").click()
            page.wait_for_url(base + "/accounts/login/")

        login("admin", password)
        assert context.request.get(base + "/api/plans/").json()["count"] == 1
        page.get_by_role("link", name="Gestión de usuarios").click()
        page.get_by_role("button", name="Crear agente").click()
        page.get_by_label("Nombre de usuario").fill("nuevo")
        secret = token_urlsafe(25)
        page.get_by_label("Contraseña inicial").fill(secret)
        page.get_by_role("button", name="Guardar agente").click()
        expect(page.get_by_role("heading", name="Tiendas de nuevo")).to_be_visible()
        page.get_by_label("Asignar una tienda").select_option(index=1)
        page.get_by_role("button", name="Asignar a nuevo").click()
        expect(page.get_by_role("button", name="Retirar")).to_be_visible()
        logout()
        login("nuevo", secret)
        guide = page.get_by_role("dialog")
        expect(guide).to_contain_text("Paso 1 de 4")
        guide.get_by_text("Siguiente").click()
        expect(guide).to_contain_text("Tus tiendas asignadas")
        guide.get_by_text("Atrás").click()
        for _ in range(3):
            guide.get_by_text("Siguiente").click()
        guide.get_by_text("Finalizar").click()
        expect(guide).to_have_count(0)
        logout()
        login("nuevo", secret)
        expect(guide).to_have_count(0)
        expect(page.get_by_role("link", name="Gestión de usuarios")).to_have_count(0)
        assert context.request.get(base + "/api/plans/").json()["count"] == 0
        assert context.request.get(base + "/api/sellers/").json()["count"] == 1
        page.get_by_role("button", name="Guía de SAP").click()
        guide.get_by_text("Omitir guía").click()
        expect(guide).to_have_count(0)
        context.clear_cookies()
        page.get_by_role("link", name="Vendedores", exact=True).click()
        page.wait_for_url("**/accounts/login/?next=*")
        assert not errors, errors
        browser.close()
        print("Correcto: migración con historial, login, alta, asignación, aislamiento, guía y sesión caducada.")


if __name__ == "__main__":
    with TemporaryDirectory() as temp:
        verify_login.OUT = Path(temp)
        verify_login.main(prepare=prepare, browser_check=verify)
