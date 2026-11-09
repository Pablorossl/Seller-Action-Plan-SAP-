"""Login UI and real Django sessions in Chromium, using disposable SQLite only.

Run after npm run build: python3 scripts/verify_login.py
Requires Playwright/Chromium in the QA interpreter and .venv for Django.
Screenshots and a report go to artifacts/login-redesign; no production access.
"""
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import tempfile
import time
import urllib.request

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/login-redesign"
PYTHON = ROOT / ".venv/bin/python"
SIZES = [(2560, 1440), (1920, 1080), (1440, 900), (1366, 768),
         (1366, 650), (1280, 720), (1280, 600),
         (1024, 768), (768, 1024), (600, 800), (390, 844), (375, 667),
         (320, 568), (844, 390)]


def run_browser(base, password):
    report = {"sizes": [], "checks": [], "contrast": [], "page_errors": [], "console_errors": [], "asset_errors": []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        context = browser.new_context(viewport={"width": 1440, "height": 900}, locale="es-ES")
        page = context.new_page()
        page.on("pageerror", lambda error: report["page_errors"].append(str(error)))
        page.on("console", lambda message: report["console_errors"].append(message.text)
                if message.type == "error" else None)
        page.on("response", lambda response: report["asset_errors"].append(response.url)
                if "/static/" in response.url and response.status >= 400 else None)
        page.goto(base + "/accounts/login/")
        expect(page.get_by_label("Nombre de usuario")).to_be_focused()
        measure = (ROOT / "scripts/measure_contrast.js").read_text().replace(
            "const selectors=[", "const selectors=['.login-brand-name','.login-brand-name small',"
            "'h1','.login-heading > p:last-child',"
            "'.login-field label','.login-hint','.login-help',"
            "'.login-submit','.login-password-toggle','.login-error','.login-field-error',")

        def contrast(name):
            sample = page.evaluate(measure)
            assert all(item["ratio"] >= item["minimum"] for item in sample["text"]), sample
            assert all(item["ratio"] >= 3 for item in sample["boundaries"]), sample
            if "solid" in sample["focus"]["outline"]:
                assert sample["focus"]["ratio"] >= 3, sample["focus"]
            report["contrast"].append({"state": name, **sample})

        contrast("default-and-focus")
        for width, height in SIZES:
            page.set_viewport_size({"width": width, "height": height})
            metrics = page.evaluate("""() => ({width: innerWidth,
                scrollWidth: document.documentElement.scrollWidth,
                scrollHeight: document.documentElement.scrollHeight,
                cardWidth: document.querySelector('.login-content').getBoundingClientRect().width,
                formWidth: document.querySelector('#login-form').getBoundingClientRect().width})""")
            assert metrics["scrollWidth"] <= width, metrics
            assert metrics["cardWidth"] <= 440, metrics
            assert metrics["formWidth"] <= 400, metrics
            if height >= 568:
                assert metrics["scrollHeight"] <= height, metrics
            expect(page.get_by_role("button", name="Iniciar sesión", exact=True)).to_be_visible()
            page.screenshot(path=str(OUT / f"login-{width}x{height}.png"), full_page=True)
            report["sizes"].append(metrics | {"height": height})
        report["checks"].append("complete login without vertical scroll from 568px high; card at most 440px wide")

        page.set_viewport_size({"width": 1440, "height": 900})
        username = page.get_by_label("Nombre de usuario")
        password_field = page.get_by_label("Contraseña", exact=True)
        submit = page.get_by_role("button", name="Iniciar sesión", exact=True)
        username.focus()
        assert username.evaluate("e => getComputedStyle(e).outlineColor") == "rgb(20, 105, 82)"

        # Force Chromium's autofill pseudo state to inspect the real CSS/UA
        # cascade. This tests appearance, not a saved password manager profile.
        cdp = context.new_cdp_session(page)
        cdp.send("DOM.enable")
        cdp.send("CSS.enable")
        root = cdp.send("DOM.getDocument")["root"]["nodeId"]
        for field in ("#id_username", "#id_password"):
            node = cdp.send("DOM.querySelector", {"nodeId": root, "selector": field})["nodeId"]
            cdp.send("CSS.forcePseudoState", {"nodeId": node, "forcedPseudoClasses": ["autofill"]})
            appearance = page.locator(field).evaluate("""e => ({autofilled: e.matches(':autofill'),
                shadow: getComputedStyle(e).boxShadow, text: getComputedStyle(e).webkitTextFillColor})""")
            assert appearance["autofilled"], appearance
            assert "rgb(255, 255, 255)" in appearance["shadow"] and "inset" in appearance["shadow"], appearance
            assert appearance["text"] == "rgb(24, 56, 49)", appearance
            cdp.send("CSS.forcePseudoState", {"nodeId": node, "forcedPseudoClasses": []})
        cdp.detach()
        report["checks"].append("green focus and white autofill appearance in Chromium's CSS/UA cascade")
        username.focus()
        page.keyboard.press("Tab")
        expect(password_field).to_be_focused()
        password_field.fill("temporary-value")
        page.keyboard.press("Tab")
        expect(page.get_by_role("button", name="Mostrar contraseña")).to_be_focused()
        page.keyboard.press("Space")
        expect(password_field).to_have_attribute("type", "text")
        expect(password_field).to_have_value("temporary-value")
        page.keyboard.press("Space")
        expect(password_field).to_have_attribute("type", "password")
        page.keyboard.press("Tab")
        expect(submit).to_be_focused()
        submit.hover()
        contrast("submit-hover-and-keyboard-focus")
        submit.click()
        expect(username).to_be_focused()  # Native required validation.
        report["checks"].append("keyboard, password visibility and native required validation")

        username.fill("login_qa")
        password_field.fill("incorrect-test-password")
        submit.click()
        expect(page.locator("#login-errors")).to_be_visible()
        expect(page.locator("#login-errors")).to_be_focused()
        expect(username).to_have_value("login_qa")
        expect(password_field).to_have_value("")
        expect(password_field).to_have_attribute("aria-invalid", "true")
        contrast("invalid-credentials")
        page.screenshot(path=str(OUT / "invalid-credentials.png"), full_page=True)
        page.set_viewport_size({"width": 320, "height": 568})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(OUT / "invalid-credentials-mobile.png"), full_page=True)
        report["checks"].append("real invalid credentials, preserved username, cleared password and error focus")

        # Bypass browser constraints to exercise Django's field-level response.
        page.reload()
        username.fill("login_qa")
        password_field.evaluate("input => input.required = false")
        submit.click()
        expect(page.locator("#password-errors")).to_be_visible()
        expect(password_field).to_be_focused()
        assert "password-errors" in password_field.get_attribute("aria-describedby").split()
        report["checks"].append("Django required field error linked to the field and focused")

        # Hold a real POST to inspect pending state and prevent duplicate submits.
        page.reload()
        username.fill("login_qa")
        password_field.fill("incorrect-test-password")
        held = []
        page.route("**/accounts/login/", lambda route: held.append(route))
        submit.click()
        expect(page.locator("#login-form")).to_have_attribute("aria-busy", "true")
        expect(page.locator(".login-submit")).to_be_disabled()
        expect(password_field).to_have_attribute("readonly", "")
        contrast("loading")
        page.locator("#login-form").evaluate("form => form.requestSubmit()")
        assert len(held) == 1
        page.screenshot(path=str(OUT / "loading-mobile.png"), full_page=True)
        held[0].continue_()
        expect(page.locator("#login-errors")).to_be_visible()
        page.unroute("**/accounts/login/")
        report["checks"].append("real delayed POST, loading, disabled controls and duplicate prevention")

        # Network/service failures are injected only in the test browser.
        for name, handler, text in [
            ("connection", lambda route: route.abort("connectionfailed"), "Comprueba tu conexión"),
            ("service", lambda route: route.fulfill(status=503, body="Unavailable"), "no está disponible"),
        ]:
            page.reload()
            username.fill("login_qa")
            password_field.fill(password)
            page.route("**/accounts/login/", handler)
            submit.click()
            expect(page.locator("#login-errors")).to_contain_text(text)
            expect(page.locator("#login-errors")).to_be_focused()
            expect(submit).to_be_enabled()
            expect(password_field).to_have_value(password)
            page.screenshot(path=str(OUT / f"{name}-error.png"), full_page=True)
            page.unroute("**/accounts/login/")
        report["checks"].append("connection and service failures, retry enabled without losing input")

        page.reload()
        username.fill("login_qa")
        password_field.fill(password)
        page.locator('[name="csrfmiddlewaretoken"]').evaluate("input => input.value = ''")
        submit.click()
        expect(page.locator("#login-errors")).to_contain_text("Recarga esta página")
        report["checks"].append("real CSRF rejection")

        page.goto(base + "/accounts/login/?next=/dashboard/%23/sellers")
        username.fill("login_qa")
        password_field.fill(password)
        password_field.press("Enter")
        page.wait_for_url(base + "/dashboard/#/sellers")
        expect(page.get_by_role("heading", name="Vendedores", exact=True)).to_be_visible()
        identity = context.request.get(base + "/api/workspace/").json()
        assert identity["username"] == "login_qa"
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_function("""() => Math.abs(
            document.querySelector('.sidebar').getBoundingClientRect().right -
            document.querySelector('.main-shell').getBoundingClientRect().left) < 1""")
        page.screenshot(path=str(OUT / "authenticated-workspace.png"), full_page=True)
        page.get_by_role("button", name="Cerrar sesión", exact=True).click()
        page.wait_for_url(base + "/accounts/login/")
        assert context.request.get(base + "/api/workspace/").status == 403
        report["checks"].append("real login with Enter, next including hash, role access and logout revocation")

        page.emulate_media(reduced_motion="reduce")
        assert page.locator(".login-spinner").evaluate("e => getComputedStyle(e).animationName") == "none"
        assert username.evaluate("e => getComputedStyle(e).transitionDuration") == "0s"
        report["checks"].append("prefers-reduced-motion")
        report["checks"].append("computed WCAG AA text, control boundaries and focus contrast")

        # Test the persistent Axes lockout through five real failed submissions.
        for attempt in range(5):
            username.fill("locked_qa")
            password_field.fill("incorrect-test-password")
            with page.expect_response(lambda r: r.request.method == "POST" and "/accounts/login/" in r.url) as result:
                submit.click()
            expect(page.locator("#login-errors")).to_be_visible()
            if attempt < 4:
                expect(password_field).to_have_value("")
                assert result.value.status == 200
            else:
                assert result.value.status == 429
                expect(page.locator("#login-errors")).to_contain_text("Espera 15 minutos")
        report["checks"].append("real Axes lockout and 429 feedback")

        native = browser.new_context(java_script_enabled=False, locale="es-ES")
        plain = native.new_page()
        plain.goto(base + "/accounts/login/?next=/")
        expect(plain.get_by_role("button", name="Mostrar contraseña")).to_have_count(0)
        plain.get_by_label("Nombre de usuario").fill("login_qa")
        plain.get_by_label("Contraseña", exact=True).fill("incorrect-test-password")
        plain.get_by_role("button", name="Iniciar sesión", exact=True).click()
        expect(plain.locator("#login-errors")).to_be_visible()
        expect(plain.get_by_label("Nombre de usuario")).to_have_value("login_qa")
        plain.get_by_label("Contraseña", exact=True).fill(password)
        plain.get_by_role("button", name="Iniciar sesión", exact=True).click()
        plain.wait_for_url(base + "/")
        expect(plain.get_by_role("heading", name="Tu espacio de trabajo")).to_be_visible()
        report["checks"].append("native login without JavaScript, validation and next=/ portal")
        plain.goto(base + "/accounts/login/")
        plain.get_by_label("Nombre de usuario").fill("locked_qa")
        plain.get_by_label("Contraseña", exact=True).fill(password)
        plain.get_by_role("button", name="Iniciar sesión", exact=True).click()
        expect(plain.get_by_role("heading", name="Acceso temporalmente limitado")).to_be_visible()
        expect(plain.get_by_role("link", name="Volver al acceso")).to_be_visible()
        expect(plain.locator(".login-brand")).to_be_visible()
        plain.screenshot(path=str(OUT / "native-locked-out.png"), full_page=True)
        report["checks"].append("native 429 lockout with shared login design")
        native.close()
        browser.close()
    assert not report["page_errors"], report["page_errors"]
    assert not report["asset_errors"], report["asset_errors"]
    expected_failures = ("status of 403", "status of 429", "status of 503", "net::ERR_CONNECTION_FAILED")
    unexpected_console = [error for error in report["console_errors"]
                          if not any(expected in error for expected in expected_failures)]
    assert not unexpected_console, unexpected_console
    (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"OK: {len(SIZES)} viewports; {len(report['checks'])} login checks; no JS/asset errors. {OUT}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sap-login-qa-") as temp:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        password = secrets.token_urlsafe(24)
        environment = os.environ | {
            "DATABASE_URL": "sqlite:///" + temp + "/qa.sqlite3", "DJANGO_DEBUG": "True",
            "DJANGO_SECRET_KEY": secrets.token_urlsafe(64), "DJANGO_ALLOWED_HOSTS": "127.0.0.1,localhost",
            "DJANGO_CSRF_TRUSTED_ORIGINS": base, "VERCEL": "0", "DJANGO_TRUST_PROXY": "False",
            "SAP_QA_PASSWORD": password,
        }
        with (OUT / "server.log").open("w") as log:
            def manage(*args):
                subprocess.run([str(PYTHON), "backend/manage.py", *args], cwd=ROOT, env=environment,
                               stdout=log, stderr=subprocess.STDOUT, check=True)
            manage("migrate", "--noinput")
            manage("shell", "-c", """import os
from django.contrib.auth import get_user_model
from django.core.management import call_command
for username in ('login_qa', 'locked_qa'):
    get_user_model().objects.create_user(username=username, password=os.environ['SAP_QA_PASSWORD'])
    call_command('configure_plan_agent', username=username, interface_only=True)
""")
            server = subprocess.Popen([str(PYTHON), "backend/manage.py", "runserver",
                f"127.0.0.1:{port}", "--noreload"], cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
            try:
                for _ in range(100):
                    try:
                        urllib.request.urlopen(base + "/accounts/login/", timeout=1)
                        break
                    except OSError:
                        time.sleep(.1)
                else:
                    raise RuntimeError(f"Django did not start; see {OUT / 'server.log'}")
                run_browser(base, password)
            finally:
                server.terminate()
                server.wait(timeout=10)


if __name__ == "__main__":
    main()
