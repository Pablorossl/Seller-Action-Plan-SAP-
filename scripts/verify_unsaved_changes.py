"""QA de fase UX 1: PostgreSQL temporal, React/Django y Chromium reales.

python3 scripts/verify_unsaved_changes.py --artifacts artifacts/ux-phase1/isolated
Reutiliza el entorno TLS, suite Django, restauración y recorrido completo de
verify_phase3. No acepta una URL externa ni usa DATABASE_URL del usuario.
"""
import json
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright, expect
import verify_phase3
from verify_browser import run_flow as full_flow


def navigation_flow(**args):
    base = args['base']
    artifacts = Path(args['artifacts']) / 'navigation'
    artifacts.mkdir(parents=True, exist_ok=True)
    checks, errors, native = [], [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=args['local_tls'], locale='es-ES',
                                      viewport={'width': 1440, 'height': 1060})
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        def native_dialog(dialog):
            native.append(dialog.type)
            dialog.dismiss()
        page.on('dialog', native_dialog)
        def check(name):
            checks.append(name)
            print('OK:', name, flush=True)
        def warning():
            dialog = page.get_by_role('dialog', name='Cambios sin guardar', exact=True)
            expect(dialog).to_be_visible()
            expect(dialog).to_have_count(1)
            expect(dialog.get_by_role('button', name='Continuar editando')).to_be_focused()
            return dialog
        def stay():
            warning().get_by_role('button', name='Continuar editando').click()
            expect(page.get_by_role('dialog', name='Cambios sin guardar', exact=True)).to_have_count(0)
        def discard():
            warning().get_by_role('button', name='Descartar los cambios y abandonar').click()
            expect(page.get_by_role('dialog', name='Cambios sin guardar', exact=True)).to_have_count(0)
        def edit():
            page.get_by_role('button', name='Editar plan', exact=True).click()
            expect(page.get_by_role('heading', name='Editar diagnóstico y seguimiento')).to_be_focused()
        def back_link():
            return page.get_by_role('link', name='Volver al plan', exact=False)
        page.goto(base + '/accounts/login/')
        page.get_by_label('Nombre de usuario').fill(args['username'])
        page.get_by_label('Contraseña', exact=True).fill(args['password'])
        page.get_by_role('button', name='Iniciar sesión').click()
        expect(page.get_by_role('heading', name='Prioridades de la semana')).to_be_visible()
        sellers = context.request.get(base + '/api/sellers/?search=' + args['seller_reference']).json()['results']
        seller = next(s for s in sellers if s['reference'] == args['seller_reference'])
        metrics = context.request.get(base + f"/api/metrics/?seller={seller['id']}").json()['results']
        metric = next(m for m in metrics if m['code'] == 'incidents')
        creation = f"#/plans/new?seller={seller['id']}&metric={metric['id']}"
        page.goto(base + '/dashboard/' + creation)
        expect(page.get_by_label('Título del plan')).to_be_visible()
        expect(page.get_by_label('Inicio del periodo de referencia')).to_have_value(metric['period_start'])
        page.get_by_role('button', name='Cancelar', exact=True).click()
        expect(page.get_by_role('heading', name=seller['name'], exact=True)).to_be_visible()
        expect(page.get_by_role('dialog')).to_have_count(0)
        check('Precarga asíncrona de vendedor/indicador: cancelar sin advertencia')
        page.goto(base + '/dashboard/' + creation)
        page.get_by_label('Título del plan').fill('BORRADOR FICTICIO CONSERVADO')
        page.get_by_role('link', name='Vendedores', exact=True).click()
        stay()
        expect(page.get_by_label('Título del plan')).to_have_value('BORRADOR FICTICIO CONSERVADO')
        page.screenshot(path=str(artifacts / 'creation-retained.png'), full_page=True)
        check('Crear: navegación lateral rechazada conserva valores')
        # Native browser mechanism (a synthetic event is also checked below).
        page.evaluate('location.reload()')
        page.wait_for_timeout(200)
        expect(page.get_by_label('Título del plan')).to_have_value('BORRADOR FICTICIO CONSERVADO')
        assert native == ['beforeunload'], native
        check('Recarga real rechazada mediante beforeunload nativo conserva valores')
        # Real history traversal; no new route should mount before the decision.
        page.evaluate('history.back()')
        stay()
        expect(page.get_by_label('Título del plan')).to_have_value('BORRADOR FICTICIO CONSERVADO')
        assert page.url.endswith(creation)
        page.evaluate('history.back()')
        discard()
        expect(page.get_by_role('heading', name=seller['name'], exact=True)).to_be_visible()
        page.evaluate('history.forward()')
        expect(page.get_by_label('Título del plan')).to_have_value('')
        check('Atrás: continuar/restaurar URL, descartar y Adelante sin borrador residual')
        title = 'QA Fase 1: navegación y conservación de texto ficticio'
        for label, value in {'Título del plan': title, 'Problema identificado': 'Incidencias ficticias 6%.',
            'Causa raíz': 'Embalaje ficticio.', 'Evidencia del diagnóstico': '100 pedidos ficticios.',
            'Objetivo de mejora': 'Reducir al 3%.'}.items():
            page.get_by_label(label, exact=False).fill(value)
        page.get_by_label('Objetivo · %').fill('7')
        page.get_by_label('Fecha objetivo del plan').fill((date.today() + timedelta(days=30)).isoformat())
        page.get_by_role('button', name='Crear borrador').click()
        expect(page.get_by_role('alert')).to_contain_text('El objetivo debe mejorar')
        expect(page.get_by_label('Título del plan')).to_have_value(title)
        page.get_by_role('button', name='Cancelar', exact=True).click()
        stay()
        expect(page.get_by_label('Objetivo · %')).to_have_value('7')
        check('Validación Django fallida conserva los valores y la protección')
        page.get_by_label('Objetivo · %').fill('3')
        posts = []
        page.on('request', lambda r: posts.append(r.url) if r.method == 'POST' and r.url == base + '/api/plans/' else None)
        page.locator('form.plan-form').evaluate('(form) => { form.requestSubmit(); form.requestSubmit(); }')
        expect(page.get_by_role('heading', name=title, exact=True)).to_be_visible()
        assert len(posts) == 1, posts
        pid = int(page.url.split('#/plans/')[1])
        plan_url = page.url
        detail_url = base + f'/api/plans/{pid}/'
        check('Crear correctamente: un único POST frente a doble envío y navegación sin aviso')
        edit()
        back_link().focus()
        page.keyboard.press('Enter')
        expect(page.get_by_role('heading', name=title, exact=True)).to_be_visible()
        expect(page.get_by_role('button', name='Editar plan', exact=True)).to_be_focused()
        assert page.url == plan_url
        check('Volver al plan con teclado sale de edición, conserva ID y restaura foco')
        edit()
        page.get_by_role('button', name='Cancelar', exact=True).click()
        expect(page.get_by_role('button', name='Editar plan', exact=True)).to_be_focused()
        check('Cancelar edición limpia no avisa y devuelve el foco')
        edit()
        page.get_by_label('Título del plan').fill(title + ' modificado')
        back_link().click()
        warning().screenshot(path=str(artifacts / 'unsaved-warning.png'))
        stay()
        expect(page.get_by_label('Título del plan')).to_have_value(title + ' modificado')
        expect(back_link()).to_be_focused()
        back_link().click()
        page.keyboard.press('Escape')
        expect(page.get_by_label('Título del plan')).to_have_value(title + ' modificado')
        back_link().click()
        discard()
        expect(page.get_by_role('heading', name=title, exact=True)).to_be_visible()
        assert context.request.get(detail_url).json()['title'] == title
        check('Volver con cambios: continuar/Escape conserva; descartar no escribe en la API')
        edit()
        page.get_by_label('Título del plan').fill(title + ' temporal')
        page.get_by_label('Título del plan').fill(title)
        page.get_by_role('button', name='Cancelar', exact=True).click()
        expect(page.get_by_role('button', name='Editar plan', exact=True)).to_be_focused()
        check('Modificar y revertir a valores iniciales no avisa')
        edit()
        page.get_by_label('Título del plan').fill(title + ' guardado')
        patches = []
        def fail_save(route):
            patches.append(route.request)
            route.fulfill(status=503, content_type='application/json', body='{"detail":"Fallo simulado de QA"}')
        page.route('**/api/plans/' + str(pid) + '/', fail_save)
        page.get_by_role('button', name='Guardar cambios', exact=True).click()
        expect(page.get_by_role('alert')).to_be_visible()
        expect(page.get_by_label('Título del plan')).to_have_value(title + ' guardado')
        page.get_by_role('button', name='Cancelar', exact=True).click()
        stay()
        page.unroute('**/api/plans/' + str(pid) + '/', fail_save)
        check('Error de guardado HTTP 503 conserva texto y guardia')
        # Hold the request to inspect busy exits and the mutation lock.
        def save_slowly(route):
            assert page.get_by_role('button', name='Cancelar', exact=True).is_disabled()
            back_link().evaluate('(link) => link.click()')
            page.get_by_role('link', name='Vendedores', exact=True).evaluate('(link) => link.click()')
            expect(page.get_by_label('Título del plan')).to_have_value(title + ' guardado')
            expect(page.get_by_role('dialog')).to_have_count(0)
            response = route.fetch()
            route.fulfill(response=response)
        page.route('**/api/plans/' + str(pid) + '/', save_slowly)
        writes = []
        page.on('request', lambda r: writes.append(r) if r.method == 'PATCH' and r.url == detail_url else None)
        page.locator('form.plan-form').evaluate('(form) => { form.requestSubmit(); form.requestSubmit(); }')
        expect(page.get_by_role('heading', name=title + ' guardado', exact=True)).to_be_visible()
        assert len(writes) == 1
        # Idempotency key remains the same when retrying identical failed data.
        assert patches[0].headers['idempotency-key'] == writes[0].headers['idempotency-key']
        page.unroute('**/api/plans/' + str(pid) + '/', save_slowly)
        expect(page.get_by_role('button', name='Editar plan', exact=True)).to_be_focused()
        assert not page.evaluate('''() => { const e = new Event('beforeunload', {cancelable:true}); window.dispatchEvent(e); return e.defaultPrevented; }''')
        check('Guardar edición: un PATCH, clave de reintento preservada, foco y guardia limpia')
        # Modal-specific baselines and each supported close affordance.
        opener = page.get_by_role('button', name='Añadir acción', exact=True)
        opener.click()
        page.keyboard.press('Escape')
        expect(page.get_by_role('dialog')).to_have_count(0)
        expect(opener).to_be_focused()
        opener.click()
        page.get_by_label('Descripción de la acción').fill('Acción ficticia sin guardar')
        for exit_kind in ('cancel', 'cross', 'escape'):
            dialog = page.get_by_role('dialog', name='Añadir acción', exact=True)
            if exit_kind == 'cancel': dialog.get_by_role('button', name='Cancelar', exact=True).click()
            elif exit_kind == 'cross': dialog.get_by_role('button', name='Cerrar formulario').click()
            else: page.keyboard.press('Escape')
            stay()
            expect(page.get_by_label('Descripción de la acción')).to_have_value('Acción ficticia sin guardar')
        page.keyboard.press('Escape')
        discard()
        expect(page.get_by_role('dialog')).to_have_count(0)
        expect(opener).to_be_focused()
        assert context.request.get(detail_url).json()['actions'] == []
        check('Acción: Escape limpio; Cancelar/X/Escape con cambios; foco y descarte sin escritura')
        # Existing metric and creation modal have different initial values.
        page.get_by_role('button', name='Editar objetivo', exact=False).click()
        target = page.get_by_label('Valor objetivo')
        initial = target.input_value()
        target.fill('2')
        page.keyboard.press('Escape')
        stay()
        target.fill(initial)
        page.keyboard.press('Escape')
        expect(page.get_by_role('dialog')).to_have_count(0)
        page.get_by_role('button', name='Añadir indicador', exact=True).click()
        page.get_by_role('button', name='Cancelar', exact=True).click()
        expect(page.get_by_role('dialog')).to_have_count(0)
        check('Objetivo existente revertido y añadir indicador vacío no generan falsos avisos')
        for trigger, label in [('Registrar revisión', 'Evolución y evidencias'), ('Finalizar plan', 'Resultado y razones')]:
            page.get_by_role('button', name=trigger, exact=True).click()
            page.keyboard.press('Escape')
            expect(page.get_by_role('dialog')).to_have_count(0)
            page.get_by_role('button', name=trigger, exact=True).click()
            page.get_by_label(label, exact=False).fill('Texto ficticio conservado')
            page.keyboard.press('Escape')
            stay()
            expect(page.get_by_label(label, exact=False)).to_have_value('Texto ficticio conservado')
            page.keyboard.press('Escape')
            discard()
            expect(page.get_by_role('dialog')).to_have_count(0)
        check('Revisión y finalización: cierre limpio y protección de sus textos')
        # History while a modal is open must keep it mounted on rejection.
        opener.click()
        page.get_by_label('Descripción de la acción').fill('Acción ante Atrás')
        page.evaluate('history.back()')
        stay()
        expect(page.get_by_label('Descripción de la acción')).to_have_value('Acción ante Atrás')
        page.keyboard.press('Escape')
        discard()
        check('Atrás con diálogo abierto conserva formulario y URL al continuar')
        # Rectification initial values are prefilled, correction reason starts blank.
        review_seller = context.request.get(base + '/api/sellers/?search=SAP-EVAL-ACTIVO').json()['results'][0]
        active = context.request.get(base + f"/api/plans/?seller={review_seller['id']}&status=open").json()['results'][0]
        page.goto(base + f"/dashboard/#/plans/{active['id']}")
        page.get_by_role('button', name='Rectificar', exact=False).first.click()
        page.keyboard.press('Escape')
        expect(page.get_by_role('dialog')).to_have_count(0)
        page.get_by_role('button', name='Rectificar', exact=False).first.click()
        page.get_by_label('Motivo de rectificación').fill('Razón ficticia pendiente')
        page.keyboard.press('Escape')
        stay()
        expect(page.get_by_label('Motivo de rectificación')).to_have_value('Razón ficticia pendiente')
        page.keyboard.press('Escape')
        discard()
        check('Rectificación precargada: limpia sin aviso, motivo modificado protegido')
        active_url = base + f"/api/plans/{active['id']}/"
        previous_reviews = context.request.get(active_url).json()['reviews']
        page.get_by_role('button', name='Rectificar', exact=False).first.click()
        page.get_by_label('Motivo de rectificación').fill('Rectificación ficticia para verificar guardado y bloqueo')
        correction_requests = []
        def save_correction(route):
            correction_requests.append(route.request)
            expect(page.get_by_label('Motivo de rectificación')).to_be_disabled()
            page.keyboard.press('Escape')
            expect(page.get_by_role('dialog', name='Rectificar revisión', exact=True)).to_be_visible()
            expect(page.get_by_role('dialog', name='Cambios sin guardar', exact=True)).to_have_count(0)
            response = route.fetch()
            route.fulfill(response=response)
        page.route('**/api/plans/' + str(active['id']) + '/reviews/', save_correction)
        page.locator('dialog form').evaluate('(form) => { form.requestSubmit(); form.requestSubmit(); }')
        expect(page.get_by_role('dialog')).to_have_count(0)
        assert len(correction_requests) == 1
        page.unroute('**/api/plans/' + str(active['id']) + '/reviews/', save_correction)
        saved_reviews = context.request.get(active_url).json()['reviews']
        assert len(saved_reviews) == len(previous_reviews) + 1
        for old in previous_reviews:
            saved = next(review for review in saved_reviews if review['id'] == old['id'])
            assert all(saved[field] == old[field] for field in ('value', 'comments', 'period_start', 'period_end'))
        assert not page.evaluate('''() => { const e = new Event('beforeunload', {cancelable:true}); window.dispatchEvent(e); return e.defaultPrevented; }''')
        check('Rectificación: motivo bloqueado al guardar, Escape no abandona, un POST e histórico conservado')
        page.set_viewport_size({'width': 390, 'height': 844})
        edit()
        page.get_by_label('Título del plan').fill('Edición ficticia móvil')
        back_link().click()
        assert warning().get_by_role('button').evaluate_all('''buttons => buttons.every(button => {
            const rect = button.getBoundingClientRect();
            return rect.left >= 0 && rect.right <= innerWidth;
        })'''), 'Los botones de decisión deben caber en el viewport móvil'
        warning().screenshot(path=str(artifacts / 'mobile-warning.png'))
        stay()
        expect(page.get_by_label('Título del plan')).to_have_value('Edición ficticia móvil')
        page.get_by_role('button', name='Cancelar', exact=True).click()
        discard()
        check('Móvil 390px: advertencia operable, continuar conserva y cancelar descarta')
        page.set_viewport_size({'width': 1440, 'height': 1060})
        edit()
        page.get_by_label('Título del plan').fill('Edición antes de salir de sesión')
        page.get_by_role('button', name='Cerrar sesión').click()
        stay()
        expect(page.get_by_label('Título del plan')).to_have_value('Edición antes de salir de sesión')
        page.get_by_role('button', name='Cerrar sesión').click()
        discard()
        expect(page.get_by_role('button', name='Iniciar sesión')).to_be_visible()
        assert native == ['beforeunload'], native
        check('Cerrar sesión: continuar conserva; descartar envía logout con CSRF sin doble advertencia')
        assert not errors, errors
        browser.close()
    report = {'checks': checks, 'count': len(checks), 'page_errors': errors,
              'native_dialogs': native, 'plan_id': pid, 'environment': 'isolated PostgreSQL and TLS'}
    (artifacts / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return report


def run_all(**args):
    navigation = navigation_flow(**args)
    full = full_flow(**args)
    return {'navigation': navigation, 'full_flow': full}


if __name__ == '__main__':
    verify_phase3.run_flow = run_all
    verify_phase3.main()
