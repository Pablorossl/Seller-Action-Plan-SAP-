"""QA UX/UI integral con PostgreSQL/TLS temporales y datos ficticios.

python3 scripts/verify_ux_closure.py --artifacts artifacts/qa-ux-cierre/final
Repite las suites anteriores y caracteriza filtros, conflictos y acceso Django.
No publica, no usa DATABASE_URL configuradas y no implementa persistencia de filtros.
"""
import json
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from playwright.sync_api import expect, sync_playwright

import verify_phase3
from verify_accessibility import AXE
from verify_contrast import MEASURE, extra_fixtures
from verify_screen_polish import run_all as existing_flows

SIZES = [(1440, 900), (768, 1024), (375, 812), (320, 568), (430, 932), (1024, 768)]


def closure_flow(*, base, username, password, other_username, other_password,
                 artifacts, local_tls=False, auth_only=False, enforce_accessibility=True, **unused):
    assert urlsplit(base).hostname in ['127.0.0.1', 'localhost'], 'Solo se admite el servidor local ficticio de QA'
    artifacts = Path(artifacts) / 'closure'
    artifacts.mkdir(parents=True, exist_ok=True)
    scans, records, filters, conflicts, pending, errors = [], [], [], [], [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)

        def new_page(width=1440, height=900):
            context = browser.new_context(ignore_https_errors=local_tls, locale='es-ES', timezone_id='Europe/Madrid',
                                          viewport={'width': width, 'height': height})
            page = context.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            return context, page

        def capture(page, name, scan=True):
            data = page.evaluate(MEASURE)
            data.update(screen=name, hash=page.evaluate('location.hash'),
                        content=page.locator('dialog[open]').last.inner_text() if page.get_by_role('dialog').count()
                        else page.locator('main').inner_text())
            if page.locator('.auth-eyebrow').count():
                data['django_styles'] = page.evaluate('''() => Object.fromEntries(
                  ['.auth-eyebrow','main p','footer p','input:not([type=hidden])','main','body'].map(selector=>{
                    const e=document.querySelector(selector); if(!e)return [selector,null];const s=getComputedStyle(e);
                    return [selector,{color:s.color,background:s.backgroundColor,border:s.borderTopColor,font:s.fontSize}];
                  }))''')
                if enforce_accessibility:
                    assert not [m for m in data['boundaries'] if m['ratio'] < 3], (name, data['boundaries'])
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), (name, data['viewport'])
            records.append(data)
            width = page.viewport_size['width']
            page.screenshot(path=str(artifacts / f'{name}-{width}.png'), full_page=page.get_by_role('dialog').count() == 0)
            (artifacts/'observations.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
            if scan:
                assert AXE.exists(), 'Falta axe-core en el entorno QA'
                page.add_script_tag(path=str(AXE))
                result = page.evaluate('''async () => {const r=await axe.run(document,{runOnly:{type:'tag',
                    values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                    return {version:axe.version,violations:r.violations,incomplete:r.incomplete};}''')
                scans.append({'screen': name, 'width': width, **result})
                (artifacts/'axe.json').write_text(json.dumps(scans, ensure_ascii=False, indent=2))
                if enforce_accessibility:
                    assert not result['violations'], (name, result['violations'])

        def login(page, who=username, secret=password):
            page.get_by_label('Nombre de usuario').fill(who)
            page.get_by_label('Contraseña', exact=True).fill(secret)
            page.get_by_role('button', name='Iniciar sesión').click()
            expect(page.get_by_role('heading', name='Prioridades de la semana')).to_be_visible()

        # Include the Django entry pages, which previous axe flows did not scan.
        for width, height in SIZES:
            context, page = new_page(width, height)
            page.goto(base+'/accounts/login/')
            assert context.request.get(base+'/api/workspace/').status == 403
            capture(page, 'django-login')
            if width == 1440:
                page.get_by_label('Nombre de usuario').fill('ausente_qa_cierre')
                page.get_by_label('Contraseña', exact=True).fill('Credencial incorrecta exclusivamente ficticia')
                page.get_by_role('button', name='Iniciar sesión').click()
                expect(page.locator('.errorlist')).to_be_visible()
                assert context.request.get(base+'/api/workspace/').status == 403
                capture(page, 'django-login-error')
            login(page)
            page.goto(base+'/')
            expect(page.get_by_role('heading', name='Tu espacio de trabajo')).to_be_visible()
            assert page.locator('.seller-list li').count() >= 55
            capture(page, 'django-portal')
            context.close()
        if not auth_only:
            context, page = new_page()
            page.goto(base+'/accounts/login/'); login(page)
            workspace = context.request.get(base+'/api/workspace/').json()
            headers = {'X-CSRFToken': workspace['csrf_token'], 'Referer': base+'/dashboard/'}

            def get(path):
                response = context.request.get(base+path)
                assert response.status == 200, (path, response.status)
                return response.json()

            plans, data = [], get('/api/plans/')
            while True:
                plans += data['results']
                if not data['next']:
                    break
                data = context.request.get(data['next']).json()
            active = get(f"/api/plans/{next(p for p in plans if p['status']=='in_progress' and p['seller_reference']=='SAP-EVAL-ACTIVO')['id']}/")
            # Standalone probes may start with just the official demo.
            for index in range(max(0, 21-len(plans))):
                payload = {key: active[key] for key in ['seller','title','problem','period_start','period_end',
                           'root_cause','evidence','objective','responsible','due_date']}
                payload.update(title=f'QA CIERRE: borrador ficticio {index}',
                               metrics=[{'baseline':active['metrics'][0]['baseline']['id'],'target_value':'3'}])
                response = context.request.post(base+'/api/plans/', data=payload,
                    headers=headers|{'Idempotency-Key':str(uuid4())})
                assert response.status == 201, response.text()
                plans.append(response.json())
            draft = next(p for p in plans if p['status']=='draft' and p['title'].startswith(('QA PULIDO:', 'QA CIERRE:')))

            def go(path, title=None):
                page.goto(base+'/dashboard/?qa-closure='+uuid4().hex+'#'+path)
                if title:
                    expect(page.locator('main h1')).to_have_text(title)
                else:
                    expect(page.locator('main h1')).to_be_visible()
                expect(page.locator('main .loading')).to_have_count(0)
                page.wait_for_load_state('networkidle')

            def list_state():
                return {'search':page.get_by_role('textbox').input_value(),
                        'filter':page.locator('.filter-label select').input_value(),
                        'pagination':page.locator('.pagination-status').inner_text(),
                        'hash':page.evaluate('location.hash')}

            def observe_return(name, before, after, width):
                fields = ['search','filter','pagination']
                filters.append({'case':name,'viewport':width,'expected':'Conservar búsqueda/filtro/página al regresar',
                                'before':before,'after':after,'preserved':all(before[k]==after[k] for k in fields),
                                'impact':'Hay que repetir la selección; no se pierden registros guardados.'})
                (artifacts/'filters.json').write_text(json.dumps(filters, ensure_ascii=False, indent=2))

            def discard():
                warning = page.get_by_role('dialog', name='Cambios sin guardar', exact=True)
                expect(warning).to_be_visible()
                warning.get_by_role('button', name='Descartar los cambios y abandonar').click()
                expect(page.get_by_role('dialog')).to_have_count(0)

            for width, height in SIZES[:3]:
                page.set_viewport_size({'width':width,'height':height})
                go('/sellers','Vendedores')
                page.get_by_role('textbox').fill('SAP-EVAL-ACTIVO')
                page.get_by_role('button', name='Buscar', exact=True).click()
                page.locator('.filter-label select').select_option('1')
                expect(page.locator('tbody tr')).to_have_count(1)
                before = list_state(); capture(page,'sellers-selection',False)
                page.locator('.table-title').click()
                expect(page.locator('main h1')).to_have_text(active['seller_name'])
                page.get_by_role('link', name='Volver a vendedores').click()
                expect(page.locator('main h1')).to_have_text('Vendedores')
                expect(page.locator('tbody tr')).to_have_count(50)
                after = list_state(); capture(page,'sellers-return')
                observe_return('Vendedores: volver desde ficha',before,after,width)

                page.get_by_role('textbox').fill('KEY-QA')
                page.get_by_role('button', name='Buscar', exact=True).click()
                page.locator('.filter-label select').select_option('0')
                expect(page.locator('tbody tr')).to_have_count(50)
                page.get_by_role('button', name='Siguiente', exact=True).click()
                expect(page.locator('.pagination-status')).to_contain_text('Página 2')
                before = list_state(); capture(page,'sellers-page2-selection',False)
                page.locator('.table-title').first.click()
                expect(page.locator('.back-link')).to_be_visible()
                page.go_back()
                expect(page.locator('main h1')).to_have_text('Vendedores')
                expect(page.locator('tbody tr')).to_have_count(50)
                after = list_state(); capture(page,'sellers-history-return',False)
                observe_return('Vendedores: Atrás desde página 2',before,after,width)

                go('/plans','Planes de mejora')
                page.get_by_role('textbox').fill(draft['title'])
                page.get_by_role('button',name='Buscar',exact=True).click()
                page.locator('.filter-label select').select_option('draft')
                # DRF searches by terms/contains: e.g. fixture "1" also matches
                # "10". Pick the exact title without assuming a single result.
                exact_draft = page.get_by_role('link',name=draft['title'],exact=True)
                expect(exact_draft).to_be_visible()
                before = list_state(); capture(page,'plans-selection',False)
                exact_draft.click()
                expect(page.locator('main h1')).to_have_text(draft['title'])
                page.get_by_role('link', name='Volver a planes').click()
                expect(page.locator('main h1')).to_have_text('Planes de mejora')
                expect(page.locator('tbody tr')).to_have_count(20)
                after = list_state(); capture(page,'plans-return')
                observe_return('Planes: volver desde detalle filtrado',before,after,width)

                page.get_by_role('button',name='Siguiente',exact=True).click()
                expect(page.locator('.pagination-status')).to_contain_text('Página 2')
                before = list_state(); capture(page,'plans-page2-selection',False)
                page.locator('.table-title').first.click()
                expect(page.locator('.back-link')).to_be_visible()
                page.go_back()
                expect(page.locator('main h1')).to_have_text('Planes de mejora')
                expect(page.locator('tbody tr')).to_have_count(20)
                after = list_state(); capture(page,'plans-history-return',False)
                observe_return('Planes: Atrás desde página 2',before,after,width)
                assert page.get_by_role('dialog').count() == 0

                go(f"/plans/{active['id']}",active['title'])
                server_before = get(f"/api/plans/{active['id']}/")
                page.get_by_role('button',name='Editar plan',exact=True).click()
                local_title = f'QA CIERRE: texto local pendiente {width}'
                page.get_by_label('Título del plan').fill(local_title)
                response = context.request.patch(base+f"/api/plans/{active['id']}/",headers=headers,
                    data={'revision':server_before['revision'],'objective':server_before['objective']+' Cambio concurrente ficticio.'})
                assert response.status == 200, response.text()
                page.get_by_role('button',name='Guardar cambios',exact=True).click()
                expect(page.get_by_role('alert')).to_contain_text('El registro ha cambiado')
                # The API's detail can match ApiError.message verbatim. Announce
                # that instruction once, without dropping distinct field errors.
                expect(page.get_by_role('alert')).to_have_text(
                    'El registro ha cambiado. Recarga sus datos y revisa tus cambios antes de guardarlos.')
                expect(page.get_by_role('alert')).to_be_focused()
                expect(page.get_by_label('Título del plan')).to_have_value(local_title)
                assert get(f"/api/plans/{active['id']}/")['title'] == server_before['title']
                capture(page,'real-conflict-409')
                page.get_by_role('link',name='Volver al plan').click()
                warning = page.get_by_role('dialog',name='Cambios sin guardar',exact=True)
                warning.get_by_role('button',name='Continuar editando').click()
                expect(page.get_by_label('Título del plan')).to_have_value(local_title)
                page.get_by_role('button',name='Cancelar',exact=True).click(); discard()
                page.reload()
                expect(page.locator('main h1')).to_have_text(server_before['title'])
                latest = get(f"/api/plans/{active['id']}/")
                assert latest['objective'].endswith('Cambio concurrente ficticio.')
                response = context.request.patch(base+f"/api/plans/{active['id']}/",headers=headers,
                    data={'revision':latest['revision'],'objective':server_before['objective']})
                assert response.status == 200
                conflicts.append({'viewport':width,'status':409,'local_values_retained':True,
                                  'server_title_not_overwritten':True,'guard_after_error':True,
                                  'latest_version_after_reload':True,'guided_recovery_available':False,
                                  'conflict_instruction_rendered_once':True})
                page.get_by_role('button',name='Registrar revisión',exact=True).click()
                expect(page.get_by_label('Valoración del agente')).to_have_value('on_track')
                capture(page,'assessment-default')
                page.keyboard.press('Escape')
                go('/plans/new')
                picker = page.locator('.record-picker').filter(has=page.locator('legend').filter(has_text='Responsable del seguimiento'))
                expect(picker.locator('.picker-options button')).to_have_count(1)
                pending.append({'viewport':width,'responsible_options':1,'search_and_pagination_present':True,
                                'assessment_default':'on_track','guided_409_recovery':False})
                capture(page,'single-responsible-picker')
                page.goto(base+'/dashboard/#/plans/999999999')
                # This route has an error component instead of a page heading.
                expect(page.get_by_role('alert')).to_contain_text('No se encuentra este registro')
                capture(page,'missing-plan')
                print(f'OK: cierre QA {width}x{height}; filtros caracterizados, conflicto real y pendientes revisados',flush=True)
            other, other_page = new_page(375,812)
            other_page.goto(base+'/accounts/login/'); login(other_page,other_username,other_password)
            expect(other_page.get_by_role('heading',name='Todo al día')).to_be_visible()
            capture(other_page,'empty-portfolio-dashboard')
            other_page.goto(base+'/dashboard/#/sellers')
            expect(other_page.get_by_role('heading',name='Aún no tienes vendedores asignados')).to_be_visible()
            capture(other_page,'empty-portfolio-sellers')
            assert other.request.get(base+f"/api/plans/{active['id']}/").status == 404
            context.close(); other.close()
        assert not errors, errors
        report = {'browser':browser.version,'states':len(records),'axe_scans':len(scans),'page_errors':errors,
                  'auth_only':auth_only,'filters':filters,'real_conflicts':conflicts,'pending':pending,
                  'violations':sorted({v['id'] for s in scans for v in s['violations']})}
        (artifacts/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        browser.close()
    return report


def run_all(**args):
    return {**existing_flows(**args), 'closure':closure_flow(**args)}


if __name__ == '__main__':
    verify_phase3.SEED += extra_fixtures('evaluador_qa') + '''
from sellers.models import Seller
u=get_user_model().objects.get(username="evaluador_qa")
Seller.objects.bulk_create([Seller(name=f"ZZ Ficticio Teclado {i}",reference=f"KEY-QA-{i}",owner=u) for i in range(55)])
'''
    verify_phase3.run_flow = run_all
    verify_phase3.main()
