"""Pulido de pantallas y regresiones con datos ficticios y PostgreSQL temporal.

python3 scripts/verify_screen_polish.py --artifacts artifacts/screen-polish/final
La reproducción previa llama screen_flow(strict=False) sobre SQLite temporal.
"""
import json
from pathlib import Path
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright

import verify_phase3
from verify_accessibility import AXE
from verify_contrast import MEASURE, extra_fixtures
from verify_visual_system import run_all as regression_flows


def screen_flow(*, base, username, password, artifacts, local_tls=False, strict=True, **unused):
    artifacts = Path(artifacts) / 'screens'
    artifacts.mkdir(parents=True, exist_ok=True)
    records, scans, errors, checks = [], [], [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=local_tls, locale='es-ES', timezone_id='Europe/Madrid')
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base + '/accounts/login/')
        page.get_by_label('Nombre de usuario').fill(username)
        page.get_by_label('Contraseña', exact=True).fill(password)
        page.get_by_role('button', name='Iniciar sesión').click()
        expect(page.get_by_role('heading', name='Prioridades de la semana')).to_be_visible()
        user = context.request.get(base + '/api/workspace/').json()

        def get(path):
            response = context.request.get(base + path)
            assert response.ok, (path, response.status)
            return response.json()

        def all_plans():
            data, result = get('/api/plans/'), []
            while True:
                result += data['results']
                if not data['next']:
                    return result
                data = context.request.get(data['next']).json()

        plans = all_plans()
        # Earlier responsive regressions deliberately replace this fixture's
        # title/objective with long strings. Select by stable seller identity.
        active = get('/api/plans/' + str(next(p for p in plans if p['status'] == 'in_progress' and p['seller_reference'] == 'SAP-EVAL-ACTIVO')['id']) + '/')
        if not active['title'].startswith('DEMO:'):
            response = context.request.patch(base + f"/api/plans/{active['id']}/", headers={
                'X-CSRFToken': user['csrf_token'], 'Referer': base + '/dashboard/'}, data={
                    'revision': active['revision'], 'title': 'DEMO: mejorar incidencias con acciones pendientes',
                    'objective': 'Reducir las incidencias al 3%.'})
            assert response.status == 200, response.text()
            active = response.json()
        good = next(p for p in plans if p['status'] == 'closed' and p['closure_evaluation'].get('result') == 'achieved')
        bad = next(p for p in plans if p['status'] == 'closed' and p['closure_evaluation'].get('result') == 'not_achieved')
        no_data = get('/api/sellers/?search=KEY-QA-0')['results'][0]
        fields = ['seller', 'title', 'problem', 'period_start', 'period_end', 'root_cause', 'evidence',
                  'objective', 'responsible', 'due_date']

        def post(path, data):
            response = context.request.post(base + path, data=data, headers={
                'X-CSRFToken': user['csrf_token'], 'Idempotency-Key': str(uuid4()), 'Referer': base + '/dashboard/'})
            assert response.status == 201, (path, response.status, response.text())
            return response.json()

        # Fixture volume uses the actual API, validation, permissions and CSRF.
        created = []
        for i in range(16):
            payload = {key: active[key] for key in fields}
            payload.update(title=f'QA PULIDO: plan ficticio {i:02}',
                           next_review_on=user['today'] if i < 6 else None,
                           metrics=[{'baseline': active['metrics'][0]['baseline']['id'], 'target_value': '3'}])
            created.append(post('/api/plans/', payload))
        for i in range(12):
            post(f"/api/plans/{active['id']}/actions/", {'description': f'QA PULIDO: acción prioritaria {i:02}',
                 'kind': 'corrective', 'responsible': 'Equipo ficticio de QA', 'due_date': user['today'], 'status': 'pending'})
        snapshot = get(f"/api/plans/{bad['id']}/")['closure_evaluation']

        def go(path):
            # Force a fresh document even if this hash was already open before
            # fixture writes; otherwise the first dashboard keeps its old data.
            page.goto(base + '/dashboard/?qa-polish=' + uuid4().hex + '#' + path)
            expect(page.locator('main h1')).to_be_visible()
            expect(page.locator('main .loading')).to_have_count(0)
            page.wait_for_load_state('networkidle')

        def record(name):
            width = page.viewport_size['width']
            data = page.evaluate(MEASURE)
            data.update(screen=name, content=page.locator('dialog[open]').last.inner_text()
                        if page.get_by_role('dialog').count() else page.locator('main').inner_text())
            records.append(data)
            page.screenshot(path=str(artifacts / f'{name}-{width}.png'),
                            full_page=page.get_by_role('dialog').count() == 0)
            (artifacts / 'observations.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
            if strict:
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), name
                assert not [m for m in data['text'] if m['ratio'] < m['minimum']], (name, data['text'])
                assert not [m for m in data['boundaries'] if m['ratio'] < 3], (name, data['boundaries'])
                assert not [m for m in data['placeholders'] if m['ratio'] < 4.5], (name, data['placeholders'])
                assert AXE.exists()
                page.add_script_tag(path=str(AXE))
                scan = page.evaluate('''async () => {const r=await axe.run(document,{runOnly:{type:'tag',
                    values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                    return {version:axe.version,violations:r.violations,incomplete:r.incomplete};}''')
                scans.append({'screen': name, 'width': width, **scan})
                (artifacts / 'axe.json').write_text(json.dumps(scans, ensure_ascii=False, indent=2))
                assert not scan['violations'], (name, scan['violations'])

        def tab_to(locator, key='Enter'):
            for _ in range(250):
                if locator.evaluate('(e)=>e===document.activeElement'):
                    page.keyboard.press(key)
                    return
                page.keyboard.press('Tab')
            raise AssertionError('Control no alcanzable con teclado: ' + str(locator))

        for width, height in [(1440, 900), (768, 1024), (375, 812)]:
            page.set_viewport_size({'width': width, 'height': height})
            go('/'); record('dashboard-volume')
            if strict:
                overview = get('/api/overview/')
                expect(page.locator('#prioridades')).to_contain_text(f"Mostrando {len(overview['priorities'])} de {overview['priorities_count']}")
                expect(page.locator('.review-panel')).to_contain_text(f"Mostrando {len(overview['reviews'])} de {overview['reviews_count']}")
                expect(page.locator('.stats-grid .stat').first).to_contain_text('Acciones vencidas')
            go('/sellers'); record('sellers')
            tab_to(page.get_by_role('button', name='Siguiente', exact=True), 'Space')
            expect(page.locator('.pagination-status')).to_contain_text('Página 2')
            if strict:
                expect(page.locator('.pagination-status')).to_be_focused()
                expect(page.locator('.pagination')).to_contain_text('51–')
            record('sellers-page2')
            page.get_by_role('textbox').fill('SIN-COINCIDENCIAS-PULIDO-QA')
            page.get_by_role('button', name='Buscar', exact=True).click()
            expect(page.locator('.empty')).to_be_visible(); record('sellers-empty')
            if strict:
                tab_to(page.get_by_role('button', name='Restablecer filtros', exact=True), 'Space')
                expect(page.get_by_role('textbox')).to_have_value('')
                expect(page.get_by_role('textbox')).to_be_focused()
                expect(page.locator('tbody tr')).to_have_count(50)
            go(f"/sellers/{active['seller']}"); record('seller')
            page.get_by_role('button', name='Historial y resultados', exact=True).click()
            expect(page.get_by_role('button', name='Historial y resultados')).to_have_attribute('aria-pressed', 'true')
            record('seller-history')
            go(f"/sellers/{no_data['id']}")
            expect(page.get_by_role('heading', name='Sin indicadores disponibles')).to_be_visible()
            record('seller-no-data')
            if strict:
                expect(page.locator('.page-heading')).to_contain_text('observación inicial')
            go('/plans'); record('plans')
            page.get_by_role('button', name='Siguiente', exact=True).click()
            expect(page.locator('.pagination-status')).to_contain_text('Página 2'); record('plans-page2')
            go(f"/plans?review=due"); record('plans-due')
            if strict:
                go(f"/plans?seller={active['seller']}")
                page.get_by_role('textbox').fill('SIN-COINCIDENCIAS-PULIDO-QA')
                page.get_by_role('button', name='Buscar', exact=True).click()
                expect(page.locator('.empty')).to_be_visible(); record('plans-context-empty')
                tab_to(page.get_by_role('button', name='Restablecer búsqueda y estado'), 'Space')
                expect(page.get_by_role('textbox')).to_have_value('')
                expect(page.get_by_role('textbox')).to_be_focused()
                expect(page.locator('tbody tr').first).to_contain_text(active['seller_name'])
                page.get_by_role('textbox').fill(active['title'])
                page.get_by_role('button', name='Buscar', exact=True).click()
                expect(page.get_by_role('link', name=active['title'], exact=True)).to_be_visible()
                record('plans-followup')
                summary = get(f"/api/plans/?seller={active['seller']}&search=" + active['title'])['results']
                next_action = next(p for p in summary if p['id'] == active['id'])['next_action']
                assert next_action is not None
                tab_to(page.get_by_role('link', name='Próxima acción: ' + next_action['description'], exact=True))
                expect(page.locator(f"#action-{next_action['id']}")).to_be_focused()
                record('followup-action-target')
            go(f"/plans/{active['id']}"); record('plan-active')
            if strict:
                expect(page.locator('.heading-actions .button.primary')).to_have_text('Registrar revisión')
                expect(page.get_by_role('button', name='Finalizar plan', exact=True)).to_have_class('button secondary')
            for screen, label in [('action', 'Añadir acción'), ('review', 'Registrar revisión'), ('close', 'Finalizar plan')]:
                tab_to(page.get_by_role('button', name=label, exact=True), 'Space')
                expect(page.get_by_role('dialog')).to_be_visible(); record(screen)
                page.keyboard.press('Escape'); expect(page.get_by_role('dialog')).to_have_count(0)
                expect(page.get_by_role('button', name=label, exact=True)).to_be_focused()
            page.get_by_role('button', name='Editar plan', exact=True).click(); record('edit')
            if strict:
                expect(page.locator('.page-heading')).to_contain_text(active['title'])
                url = page.url
                page.get_by_label('Título del plan').fill(active['title'] + ' · Cambio ficticio sin guardar')
                tab_to(page.get_by_role('button', name='3 Responsable y plazos', exact=True), 'Space')
                expect(page.get_by_role('heading', name='Organizar el seguimiento')).to_be_focused()
                expect(page.get_by_label('Título del plan')).to_have_value(active['title'] + ' · Cambio ficticio sin guardar')
                expect(page.get_by_role('dialog')).to_have_count(0)
                assert page.url == url
                page.get_by_label('Título del plan').fill(active['title'])
            page.get_by_label('Fecha objetivo del plan').fill('2026-01-01')
            page.get_by_role('button', name='Guardar cambios', exact=True).click()
            expect(page.get_by_role('alert')).to_be_focused(); record('validation')
            if strict:
                expect(page.get_by_role('alert')).to_contain_text('Fecha objetivo del plan')
                expect(page.get_by_role('alert')).not_to_contain_text('due_date')
            page.get_by_label('Fecha objetivo del plan').fill(active['due_date'])
            page.get_by_role('button', name='Cancelar', exact=True).click()
            if width == 1440:
                page.get_by_role('button', name='Editar plan', exact=True).click()
                page.get_by_label('Objetivo de mejora').fill(active['objective'] + ' Comprobación ficticia de guardado.')
                page.get_by_role('button', name='Guardar cambios', exact=True).click()
                expect(page.locator('.success-notice')).to_be_visible(); record('success')
            go(f"/plans/{created[0]['id']}"); record('plan-draft')
            if strict:
                expect(page.locator('.heading-actions .button.primary')).to_have_text('Añadir acción')
            for screen, plan in [('closed-achieved', good), ('closed-not-achieved', bad)]:
                go(f"/plans/{plan['id']}"); record(screen)
            held = []
            page.route('**/api/overview/', lambda route: held.append(route))
            page.goto(base + '/dashboard/#/')
            expect(page.locator('main .loading')).to_be_visible(); record('loading')
            assert len(held) == 1
            held[0].fulfill(status=503, json={'detail': 'Error ficticio de lectura'})
            expect(page.locator('.error-state')).to_be_visible(); record('error')
            page.unroute('**/api/overview/')
            tab_to(page.get_by_role('button', name='Volver a intentar'), 'Space')
            expect(page.get_by_role('heading', name='Prioridades de la semana')).to_be_visible()
            checks.append(f'{width}x{height}: pantallas, mensajes, teclado y recuperación')
            print('OK:', checks[-1], flush=True)
        assert get(f"/api/plans/{bad['id']}/")['closure_evaluation'] == snapshot
        assert not errors, errors
        report = {'browser': browser.version, 'strict': strict, 'states': len(records), 'axe_scans': len(scans),
                  'checks': checks, 'page_errors': errors, 'snapshot_unchanged': True}
        (artifacts / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        browser.close()
    return report


def run_all(**args):
    # Extra volume belongs to the dedicated flow, after the legacy fixtures' tests.
    return {**regression_flows(**args), 'polish': screen_flow(**args)}


if __name__ == '__main__':
    verify_phase3.SEED += extra_fixtures('evaluador_qa') + '''
from sellers.models import Seller
u=get_user_model().objects.get(username="evaluador_qa")
Seller.objects.bulk_create([Seller(name=f"ZZ Ficticio Teclado {i}",reference=f"KEY-QA-{i}",owner=u) for i in range(55)])
'''
    verify_phase3.run_flow = run_all
    verify_phase3.main()
