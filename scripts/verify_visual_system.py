"""Componentes reales y regresiones en PostgreSQL/TLS temporales, solo datos ficticios.

python3 scripts/verify_visual_system.py --artifacts artifacts/visual-system/final
Requiere el mismo entorno de QA que verify_contrast.py. No publica ni despliega.
"""
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

import verify_phase3
from verify_accessibility import AXE
from verify_contrast import extra_fixtures, run_all as regression_flows


STYLES = """() => {
  const selectors = ['.panel','.stat','.stepper','.panel-heading','.toolbar',
    'th','td','td small','.badge','.field label','.field small','.field input',
    '.field select','.field textarea','.button','.search-box','.search-box input',
    '.search-box button','.pagination','.info-note','.confirmation','.form-error',
    '.error-state','.success-notice','.empty','.loading','.modal'];
  return Object.fromEntries(selectors.map(selector => [selector,
    [...document.querySelectorAll(selector)].filter(e => e.getClientRects().length && !e.closest('[inert]')).map(e => {
      const s = getComputedStyle(e);
      return {text: e.textContent.trim().slice(0,65), font: s.fontSize, weight:s.fontWeight,
        padding:s.padding, radius:s.borderRadius, border:s.borderColor,
        color:s.color, background:s.backgroundColor, minHeight:s.minHeight};
    })]));
}"""


def visual_flow(*, base, username, password, artifacts, local_tls=False, strict=True, **unused):
    artifacts = Path(artifacts) / 'components'
    artifacts.mkdir(parents=True, exist_ok=True)
    records, errors, scans = [], [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=local_tls, locale='es-ES')
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(base + '/accounts/login/')
        page.get_by_label('Nombre de usuario').fill(username)
        page.get_by_label('Contraseña', exact=True).fill(password)
        page.get_by_role('button', name='Iniciar sesión').click()
        expect(page.get_by_role('heading', name='Prioridades de la semana')).to_be_visible()
        plans = context.request.get(base + '/api/plans/').json()['results']
        active = next(plan for plan in plans if plan['status'] == 'in_progress')

        def go(path):
            page.goto(base + '/dashboard/#' + path)
            expect(page.locator('main h1')).to_be_visible()
            expect(page.locator('main .loading')).to_have_count(0)
            page.wait_for_load_state('networkidle')

        def record(name):
            styles = page.evaluate(STYLES)
            width = page.viewport_size['width']
            if strict:
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'), name
                for selector in ['th', 'td small', '.badge', '.field label', '.field small', '.pagination']:
                    assert all(float(item['font'][:-2]) >= 12 for item in styles[selector]), (name, selector, styles[selector])
                for item in styles['.button']:
                    assert float(item['minHeight'][:-2]) >= 36, (name, item)
                for item in styles['.panel'] + styles['.stat'] + styles['.stepper']:
                    assert item['radius'] == '10px', (name, item)
                # Short identifiers beside avatars should fit on one line;
                # natural wrapping remains available for multiword/long names.
                assert page.locator('td .person').evaluate_all('''items => items.every(e =>
                    [...e.childNodes].filter(n => n.nodeType === Node.TEXT_NODE && n.textContent.trim() &&
                        !/\\s/.test(n.textContent.trim()) && n.textContent.trim().length <= 20)
                    .every(n => {const r = document.createRange(); r.selectNodeContents(n);
                        return r.getClientRects().length <= 1;}))'''), (name, 'Short identifier split across lines')
                if name in ['rectification', 'empty', 'loading', 'error']:
                    assert AXE.exists(), 'Falta axe-core en el entorno de QA'
                    page.add_script_tag(path=str(AXE))
                    scan = page.evaluate('''async () => {
                        const r = await axe.run(document, {runOnly: {type:'tag',
                            values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                        return {version:axe.version, violations:r.violations, incomplete:r.incomplete};
                    }''')
                    scans.append({'screen': name, 'viewport': page.viewport_size, **scan})
                    (artifacts / 'axe.json').write_text(json.dumps(scans, ensure_ascii=False, indent=2))
                    assert not scan['violations'], (name, scan['violations'])
            page.screenshot(path=str(artifacts / f'{name}-{width}.png'),
                            full_page=page.get_by_role('dialog').count() == 0)
            records.append({'screen': name, 'viewport': page.viewport_size, 'styles': styles})
            (artifacts / 'measurements.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))

        for width, height in [(1440, 900), (768, 1024), (375, 812)]:
            page.set_viewport_size({'width': width, 'height': height})
            go('/'); record('dashboard')
            go('/plans'); record('plans')
            go(f"/plans/{active['id']}"); record('detail')
            rectify = page.get_by_role('button', name='Rectificar revisión #').first
            expect(rectify).to_be_visible()
            if strict:
                expect(rectify).to_have_class('button secondary compact')
            rectify.click(); record('rectification')
            page.keyboard.press('Escape')
            page.get_by_role('button', name='Editar plan', exact=True).click()
            record('edit')
            page.get_by_role('button', name='Cancelar', exact=True).click()
            for screen, label in [('action', 'Añadir acción'), ('review', 'Registrar revisión'), ('close', 'Finalizar plan')]:
                page.get_by_role('button', name=label, exact=True).click()
                record(screen)
                if strict and screen == 'close':
                    expect(page.locator('dialog .table-region')).to_have_class('table-region table-compact')
                    expect(page.locator('dialog th').first).to_have_css('font-size', '12px')
                    expect(page.locator('dialog td').first).to_have_css('font-size', '13px')
                page.keyboard.press('Escape')
                expect(page.get_by_role('dialog')).to_have_count(0)
            go('/sellers')
            page.get_by_role('search').get_by_role('textbox').fill('SIN-COINCIDENCIAS-QA-VISUAL-91827')
            page.get_by_role('button', name='Buscar', exact=True).click()
            expect(page.locator('.empty')).to_be_visible()
            record('empty')
            held = []
            page.route('**/api/overview/', lambda route: held.append(route))
            page.goto(base + '/dashboard/#/')
            expect(page.locator('main .loading')).to_be_visible()
            expect(page.locator('main .loading')).to_have_attribute('role', 'status')
            record('loading')
            # A deliberate QA failure exercises the recoverable error component.
            assert len(held) == 1
            held[0].fulfill(status=503, json={'detail': 'Error ficticio de QA visual'})
            expect(page.locator('.error-state')).to_be_visible()
            if strict:
                message = page.locator('.error-state strong').bounding_box()
                retry = page.get_by_role('button', name='Volver a intentar').bounding_box()
                assert retry['y'] >= message['y'] + message['height'], 'Retry action overlaps the message line'
            record('error')
            page.unroute('**/api/overview/')
            page.get_by_role('button', name='Volver a intentar').click()
            expect(page.get_by_role('heading', name='Prioridades de la semana')).to_be_visible()
            print(f'Componentes {width}x{height}: OK (strict={strict})', flush=True)
        assert not errors, errors
        report = {'browser': browser.version, 'strict': strict, 'screens': len(records),
                  'axe_scans': len(scans), 'page_errors': errors}
        (artifacts / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
        browser.close()
    return report


def run_all(**args):
    return {'components': visual_flow(**args), **regression_flows(**args)}


if __name__ == '__main__':
    verify_phase3.SEED += extra_fixtures('evaluador_qa') + '''
from sellers.models import Seller
u=get_user_model().objects.get(username="evaluador_qa")
Seller.objects.bulk_create([Seller(name=f"ZZ Ficticio Teclado {i}",reference=f"KEY-QA-{i}",owner=u) for i in range(55)])
'''
    verify_phase3.run_flow = run_all
    verify_phase3.main()
