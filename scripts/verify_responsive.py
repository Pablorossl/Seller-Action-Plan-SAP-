"""Responsive real con datos ficticios y regresión de fase 1.

python3 scripts/verify_responsive.py --artifacts artifacts/ux-phase2/isolated
Reutiliza el clúster PostgreSQL temporal/TLS de verify_phase3; nunca usa producción.
"""
import json
from pathlib import Path
from uuid import uuid4
from playwright.sync_api import sync_playwright, expect
import verify_phase3
from verify_browser import run_flow as full_flow
from verify_unsaved_changes import navigation_flow

SIZES = [(320, 568), (375, 812), (430, 932), (768, 1024), (1024, 768), (1440, 900)]
LAYOUT = r'''() => {
 const root = document.documentElement;
 const visible = e => {const r=e.getBoundingClientRect();return r.width && r.height && getComputedStyle(e).visibility !== 'hidden';};
 const tables = [...document.querySelectorAll('.table-wrap')].filter(visible).map(e => ({
   width:e.clientWidth, scroll:e.scrollWidth, label:e.getAttribute('aria-label'), left:e.getBoundingClientRect().left
 }));
 const outliers = [...document.querySelectorAll('body *')].filter(visible).filter(e => {
   if(e.closest('.table-wrap') || e.closest('.sidebar:not(.is-open)') && innerWidth<=760) return false;
   const r=e.getBoundingClientRect(); return r.right>innerWidth+1 || r.left < -1;
 }).map(e => ({tag:e.tagName, cls:typeof e.className==='string'?e.className:'svg',text:e.textContent.trim().slice(0,65),
   left:Math.round(e.getBoundingClientRect().left),right:Math.round(e.getBoundingClientRect().right)})).slice(0,25);
 const dialogs = [...document.querySelectorAll('dialog[open]')].map(e => {
   const r=e.getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:e.clientWidth,scroll:e.scrollWidth};
 });
 const clipped = [...document.querySelectorAll('.panel,.focus-panel,.record-picker,.stat')].filter(visible)
   .filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>({cls:e.className,width:e.clientWidth,scroll:e.scrollWidth}));
 const hiddenHeaders = [...document.querySelectorAll('th .sr-only')].map(e=>({
   right:e.getBoundingClientRect().right,containingBlock:e.offsetParent?.className || e.offsetParent?.tagName
 }));
 return {viewport:innerWidth, width:root.scrollWidth, height:innerHeight, tables, dialogs, outliers, clipped, hiddenHeaders};
}'''


def responsive_flow(*, base, username, password, artifacts, local_tls=False, strict=True, **unused):
    artifacts = Path(artifacts) / 'responsive'
    artifacts.mkdir(parents=True, exist_ok=True)
    records, checks, errors = [], [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=local_tls, locale='es-ES')
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(base + '/accounts/login/')
        page.get_by_label('Nombre de usuario').fill(username)
        page.get_by_label('Contraseña', exact=True).fill(password)
        page.get_by_role('button', name='Iniciar sesión').click()
        expect(page.get_by_role('heading', name='Prioridades de la semana')).to_be_visible()
        sellers = context.request.get(base + '/api/sellers/').json()['results']
        seller = next(s for s in sellers if s['reference'] == 'SAP-EVAL-ACTIVO')
        active = context.request.get(base + f"/api/plans/?seller={seller['id']}&status=open").json()['results'][0]
        baseline = context.request.get(base + f"/api/metrics/?seller={seller['id']}").json()['results'][0]
        closed = context.request.get(base + '/api/plans/?status=closed').json()['results'][0]
        def record(name, capture=True):
            data = page.evaluate(LAYOUT)
            data.update(screen=name, size=f'{page.viewport_size["width"]}x{page.viewport_size["height"]}')
            records.append(data)
            # Persist intermediate measurements too, so failures remain reviewable.
            (artifacts / 'measurements.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
            if capture: page.screenshot(path=str(artifacts / f'{name}-{data["size"]}.png'))
            if strict:
                assert data['width'] <= data['viewport'] + 1, (name, data)
                assert not data['clipped'], (name, data['clipped'])
                for d in data['dialogs']:
                    assert d['left'] >= 0 and d['right'] <= data['viewport']+1 and d['top'] >= 0 and d['bottom'] <= data['height']+1, (name, d)
                    assert d['scroll'] <= d['width']+1, (name, 'dialog horizontal overflow', d)
            return data
        def interact_tables():
            for region in page.locator('.table-wrap').all():
                hint=region.locator('..').locator('.table-scroll-hint')
                if region.evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'):
                    expect(hint).not_to_be_visible()
                    continue
                region.scroll_into_view_if_needed()
                expect(hint).to_be_visible()
                assert region.get_attribute('aria-describedby') == hint.get_attribute('id')
                region.focus()
                page.keyboard.press('ArrowRight')
                page.wait_for_function('(e)=>e.scrollLeft>0',arg=region.element_handle())
                region.hover()
                page.wait_for_timeout(200)
                page.mouse.wheel(1600,0)
                try:
                    page.wait_for_function('(e)=>e.scrollLeft>=e.scrollWidth-e.clientWidth-2',arg=region.element_handle(),timeout=2000)
                except Exception:
                    print('Scroll diagnostic:',region.evaluate('(e)=>({left:e.scrollLeft,width:e.clientWidth,scroll:e.scrollWidth,rect:e.getBoundingClientRect().toJSON()})'),flush=True)
                    page.screenshot(path=str(artifacts/'table-scroll-failure.png'))
                    raise
                assert page.evaluate('window.scrollX') == 0
                region.evaluate('(e)=>e.scrollLeft=0')
        def go(route):
            page.goto(base + '/dashboard/#' + route)
            if route == '/': expect(page.get_by_role('heading', name='Prioridades de la semana')).to_be_visible()
            elif route == '/sellers': expect(page.locator('main h1')).to_have_text('Vendedores')
            elif route.startswith('/sellers/'): expect(page.locator('main h1')).to_have_text(seller['name'])
            elif route == '/plans': expect(page.locator('main h1')).to_have_text('Planes de mejora')
            elif route.startswith('/plans/new'): expect(page.get_by_label('Título del plan')).to_be_visible()
            elif route == f"/plans/{active['id']}": expect(page.locator('main h1')).to_have_text(active['title'])
            elif route == f"/plans/{closed['id']}": expect(page.locator('main h1')).to_have_text(closed['title'])
            expect(page.locator('main .loading')).to_have_count(0)
            page.wait_for_load_state('networkidle')
        def clean_close():
            page.keyboard.press('Escape')
            expect(page.get_by_role('dialog')).to_have_count(0)
        for width, height in SIZES:
            page.set_viewport_size({'width':width,'height':height})
            for name, route in [('dashboard','/'), ('sellers','/sellers'), ('seller',f"/sellers/{seller['id']}"),
                ('plans','/plans'), ('create',f"/plans/new?seller={seller['id']}&metric={baseline['id']}"),
                ('detail',f"/plans/{active['id']}"), ('closed',f"/plans/{closed['id']}")]:
                go(route)
                record(name)
                if strict:
                    interact_tables()
                    if name in ('sellers','plans'):
                        row=page.locator('.table-wrap tbody tr').first
                        title=row.locator('.table-title').inner_text()
                        row.locator('td').last.get_by_role('link').click()
                        expect(page.locator('main h1')).to_have_text(title)
                        go(route)
            go(f"/plans/{active['id']}")
            page.get_by_role('button', name='Editar plan', exact=True).click()
            record('edit')
            page.get_by_role('link', name='Volver al plan', exact=False).click()
            expect(page.get_by_role('button', name='Editar plan', exact=True)).to_be_focused()
            for name, trigger in [('action','Añadir acción'), ('metric','Añadir indicador'), ('review','Registrar revisión'),
                                   ('correction','Rectificar revisión'), ('close','Finalizar plan')]:
                page.get_by_role('button', name=trigger, exact=False).first.click()
                record(name)
                if strict:
                    dialog = page.get_by_role('dialog')
                    # Exercise the bottom controls: browser must scroll within the dialog.
                    cancel = dialog.get_by_role('button', name='Cancelar', exact=True)
                    cancel.scroll_into_view_if_needed()
                    assert cancel.bounding_box()['x'] >= 0
                    cancel.click()
                    expect(page.get_by_role('dialog')).to_have_count(0)
                else: clean_close()
            if strict:
                page.get_by_role('button',name='Añadir acción',exact=True).click()
                description=f'Acción ficticia {uuid4().hex[:6]} guardada desde {width}x{height}'
                page.get_by_label('Descripción de la acción').fill(description)
                page.get_by_label('Persona o equipo responsable').fill('Equipo ficticio responsive')
                page.get_by_label('Fecha límite').fill(active['due_date'])
                page.get_by_role('dialog').get_by_role('button',name='Añadir acción',exact=True).click()
                expect(page.get_by_role('dialog')).to_have_count(0)
                expect(page.get_by_role('heading',name=description,exact=True)).to_be_visible()
                page.get_by_role('button',name='Editar plan',exact=True).click()
                page.get_by_label('Fecha objetivo del plan').fill('2026-01-01')
                page.get_by_role('button',name='Guardar cambios',exact=True).click()
                expect(page.get_by_role('alert')).to_be_visible()
                expect(page.get_by_label('Fecha objetivo del plan')).to_have_value('2026-01-01')
                record('validation')
                page.get_by_label('Fecha objetivo del plan').fill(active['due_date'])
                page.get_by_role('button',name='Cancelar',exact=True).click()
                expect(page.get_by_role('dialog')).to_have_count(0)
            page.get_by_role('button', name='Editar plan', exact=True).click()
            page.get_by_label('Título del plan').fill('Texto ficticio pendiente responsive')
            page.get_by_role('link', name='Volver al plan', exact=False).click()
            record('warning')
            page.get_by_role('button', name='Continuar editando', exact=True).click()
            expect(page.get_by_label('Título del plan')).to_have_value('Texto ficticio pendiente responsive')
            page.get_by_role('button', name='Cancelar', exact=True).click()
            page.get_by_role('button', name='Descartar los cambios y abandonar').click()
            go('/sellers')
            if page.get_by_role('button', name='Mostrar navegación').is_visible():
                page.get_by_role('button', name='Mostrar navegación').click()
                record('navigation')
                if strict:
                    logout = page.get_by_role('button', name='Cerrar sesión')
                    logout.scroll_into_view_if_needed()
                    box=logout.bounding_box()
                    assert box['y']>=0 and box['y']+box['height']<=height+1, box
                    page.keyboard.press('Escape')
                    expect(page.get_by_role('button', name='Mostrar navegación')).to_be_focused()
                    expect(page.locator('.sidebar')).not_to_be_visible()
                    page.get_by_role('button', name='Mostrar navegación').click()
                page.get_by_role('link', name='Dashboard', exact=True).click()
                expect(page.get_by_role('heading', name='Prioridades de la semana')).to_be_visible()
                if strict:
                    go(f"/plans/{active['id']}")
                    page.get_by_role('button',name='Editar plan',exact=True).click()
                    page.get_by_label('Título del plan').fill('Texto ficticio protegido tras menú compacto')
                    page.get_by_role('button',name='Mostrar navegación').click()
                    page.get_by_role('link',name='Vendedores',exact=True).click()
                    warning=page.get_by_role('dialog',name='Cambios sin guardar',exact=True)
                    expect(warning).to_have_count(1)
                    warning.get_by_role('button',name='Continuar editando').click()
                    page.mouse.click(width-8,height-8)
                    expect(page.get_by_role('button',name='Mostrar navegación')).to_be_focused()
                    expect(page.locator('main')).not_to_have_attribute('inert','')
                    expect(page.get_by_label('Título del plan')).to_have_value('Texto ficticio protegido tras menú compacto')
                    page.get_by_role('button',name='Cancelar',exact=True).click()
                    page.get_by_role('button',name='Descartar los cambios y abandonar').click()
            checks.append(f'{width}x{height}: screens, forms, dialogs, navigation and phase1 cancel/retain/discard')
            print('OK' if strict else 'BASELINE', checks[-1], flush=True)
        if strict:
            # Real saved fixture values, not fake product responses. Only the
            # dedicated fictitious plan is changed in the isolated database.
            workspace=context.request.get(base+'/api/workspace/').json()
            headers={'X-CSRFToken':workspace['csrf_token'],'Referer':base+'/dashboard/','Idempotency-Key':str(uuid4())}
            detail=context.request.get(base+f"/api/plans/{active['id']}/").json()
            response=context.request.patch(base+f"/api/plans/{active['id']}/",headers=headers,
                data={'revision':detail['revision'],'title':'PlanFicticio'+('L'*188),'objective':'https://ficticio.invalid/'+('evidencia'*70)})
            assert response.status==200,response.text()
            active=response.json()
            response=context.request.post(base+f"/api/plans/{active['id']}/actions/",headers=headers|{'Idempotency-Key':str(uuid4())},
                data={'description':'AcciónFicticia'+('A'*500),'kind':'corrective','responsible':'EquipoFicticio'+('R'*145),'due_date':active['due_date'],
                      'notes':'https://ficticio.invalid/'+('n'*500)})
            assert response.status in (200,201),response.text()
            for width,height in SIZES:
                page.set_viewport_size({'width':width,'height':height})
                go('/')
                record('long-dashboard')
                go('/plans')
                record('long-plans')
                interact_tables()
                go(f"/plans/{active['id']}")
                record('long-detail')
                page.get_by_role('button',name='Editar acción: AcciónFicticia',exact=False).click()
                expect(page.get_by_label('Descripción de la acción')).to_have_value('AcciónFicticia'+('A'*500))
                record('long-action')
                page.get_by_role('button',name='Cancelar',exact=True).click()
                expect(page.get_by_role('dialog')).to_have_count(0)
            checks.append('Long saved title, URL, action description and responsible: all six sizes')
            page.set_viewport_size({'width':1440,'height':900})
            go('/')
            zoom_before=page.evaluate('innerWidth')
            page.keyboard.press('Control+Equal')
            page.keyboard.press('Control+Equal')
            zoom_after=page.evaluate('innerWidth')
            page.keyboard.press('Control+0')
            for factor,width,height in [(200,720,450),(400,360,225)]:
                page.set_viewport_size({'width':width,'height':height})
                for name,route in [('dashboard','/'),('create',f"/plans/new?seller={seller['id']}&metric={baseline['id']}"),
                                    ('detail',f"/plans/{active['id']}")]:
                    go(route)
                    record(f'reflow-{factor}-{name}')
                page.get_by_role('button',name='Finalizar plan',exact=True).click()
                record(f'reflow-{factor}-close')
                page.get_by_role('button',name='Cancelar',exact=True).click()
                page.get_by_role('button',name='Mostrar navegación').click()
                page.get_by_role('button',name='Cerrar sesión').scroll_into_view_if_needed()
                record(f'reflow-{factor}-navigation')
                page.keyboard.press('Escape')
                expect(page.get_by_role('button',name='Mostrar navegación')).to_be_focused()
            checks.append('Reflow equivalent to 200% and 400% from 1440x900; native zoom recorded separately')
        assert not errors, errors
        report={'strict':strict,'browser':browser.version,'sizes':SIZES,'checks':checks,'states':len(records),'page_errors':errors,
                'native_zoom_css_viewport_changed':zoom_after!=zoom_before if strict else None,
                'zoom_reflow_viewports':[[720,450],[360,225]] if strict else []}
        (artifacts/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        browser.close()
    return report


def run_all(**args):
    return {'responsive':responsive_flow(**args), 'phase1':navigation_flow(**args), 'full_flow':full_flow(**args)}


if __name__ == '__main__':
    verify_phase3.run_flow = run_all
    verify_phase3.main()
