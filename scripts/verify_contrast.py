"""Contraste, estado/resultado y regresión completa con PostgreSQL temporal.

python3 scripts/verify_contrast.py --artifacts artifacts/ux-contrast/final
Axe se instala solo en QA; SAP_AXE_PATH admite otra ruta.
"""
import json,os
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import verify_phase3
from verify_accessibility import keyboard_flow,AXE
from verify_unsaved_changes import navigation_flow
from verify_responsive import responsive_flow
from verify_browser import run_flow as full_flow

MEASURE=Path(__file__).with_name('measure_contrast.js').read_text()

def extra_fixtures(username):
    # Valid cancellation through the service, then a separate legacy fixture
    # with a missing recorded result, matching old snapshots supported by API.
    return f'''
from action_plans.models import ImprovementPlan
from action_plans.services import close_plan
u=get_user_model().objects.get(username={username!r})
template=ImprovementPlan.objects.filter(status="in_progress",created_by=u).first()
for title,legacy in [("QA VISUAL: cancelación no evaluable",False),("QA VISUAL: histórico sin resultado",True)]:
    if ImprovementPlan.objects.filter(title=title,created_by=u).exists(): continue
    fields={{name:getattr(template,name) for name in ["seller","problem","period_start","period_end","root_cause","evidence","objective","responsible","created_by","due_date"]}}
    plan=ImprovementPlan.objects.create(title=title,**fields)
    close_plan(plan_id=plan.pk,actor=u,status="cancelled",notes="Datos exclusivamente ficticios de QA visual.")
    if legacy: ImprovementPlan.objects.filter(pk=plan.pk).update(closure_evaluation={{"schema_version":0}})
'''


def contrast_flow(*,base,username,password,artifacts,local_tls=False,strict=True,**unused):
    artifacts=Path(artifacts)/'contrast';artifacts.mkdir(parents=True,exist_ok=True)
    samples=[];scans=[];errors=[];semantics=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        context=browser.new_context(ignore_https_errors=local_tls,locale='es-ES',viewport={'width':1440,'height':900})
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(base+'/accounts/login/')
        page.get_by_label('Nombre de usuario').fill(username);page.get_by_label('Contraseña', exact=True).fill(password)
        page.get_by_role('button',name='Iniciar sesión').click()
        expect(page.get_by_role('heading',name='Prioridades de la semana')).to_be_visible()
        plans=context.request.get(base+'/api/plans/').json()['results']
        good=next(p for p in plans if p['status']=='closed' and p['closure_evaluation'].get('result')=='achieved')
        bad=next(p for p in plans if p['status']=='closed' and p['closure_evaluation'].get('result')=='not_achieved')
        active=next(p for p in plans if p['status']=='in_progress')
        pending=next(p for p in plans if p['title']=='QA VISUAL: cancelación no evaluable') if strict else None
        legacy=next(p for p in plans if p['title']=='QA VISUAL: histórico sin resultado') if strict else None
        detail_url=base+f"/api/plans/{bad['id']}/"
        before=context.request.get(detail_url).json()['closure_evaluation']
        def record(name,scan=True):
            measure=page.evaluate(MEASURE)
            measure['screen']=name; samples.append(measure)
            page.screenshot(path=str(artifacts/(name+'.png')))
            (artifacts/'measurements.json').write_text(json.dumps(samples,ensure_ascii=False,indent=2))
            if scan and AXE.exists():
                page.add_script_tag(path=str(AXE))
                result=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                    return {version:axe.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),incomplete:r.incomplete.map(v=>v.id)};}''')
                scans.append({'screen':name,**result})
                (artifacts/'axe.json').write_text(json.dumps(scans,ensure_ascii=False,indent=2))
            if strict:
                assert not [(m['selector'],m['ratio']) for m in measure['text'] if m['ratio']<m['minimum']],(name,measure['text'])
                assert not [m for m in measure['placeholders'] if m['ratio']<4.5],(name,measure['placeholders'])
                assert not [m for m in measure['boundaries'] if m['ratio']<3],(name,measure['boundaries'])
            return measure
        def go(path,title=None):
            page.goto(base+'/dashboard/#'+path)
            if title:expect(page.locator('main h1')).to_have_text(title)
            expect(page.locator('main .loading')).to_have_count(0)
            page.wait_for_load_state('networkidle')
        for width,height in [(1440,900),(768,1024),(375,812)]:
            page.set_viewport_size({'width':width,'height':height})
            go('/')
            expect(page.get_by_role('heading',name='Prioridades de la semana')).to_be_visible()
            record(f'dashboard-{width}')
            go('/sellers','Vendedores');record(f'sellers-{width}')
            go('/plans','Planes de mejora');record(f'plans-{width}')
            if strict:
                for plan,result in [(good,'Objetivo alcanzado'),(bad,'Objetivo no alcanzado'),(pending,'No evaluable'),(legacy,'Sin resultado registrado')]:
                    row=page.locator('tbody tr').filter(has=page.get_by_role('link',name=plan['title'],exact=True))
                    expect(row.get_by_text('Cerrado' if plan['status']=='closed' else 'Cancelado',exact=True)).to_be_visible()
                    expect(row.get_by_text(result,exact=True)).to_be_visible()
                    expect(row.get_by_text('Resultado al cierre',exact=True)).to_be_visible()
                metric=context.request.get(base+f"/api/metrics/?seller={active['seller']}").json()['results'][0]
                go(f"/plans/new?seller={active['seller']}&metric={metric['id']}","Cada mejora empieza con un plan")
                record(f'create-{width}')
                if width==1440:
                    primary=page.get_by_role('button',name='Crear borrador',exact=True)
                    primary.hover();record('primary-hover',False)
                    for _ in range(160):
                        if primary.evaluate('(e)=>e===document.activeElement'):break
                        page.keyboard.press('Tab')
                    expect(primary).to_be_focused()
                    m=record('primary-focus',False)
                    assert 'solid' in m['focus']['outline'] and m['focus']['ratio']>=3,m['focus']
                    page.get_by_role('button',name='Cancelar',exact=True).hover();record('secondary-hover',False)
                    nav=page.get_by_role('link',name='Dashboard',exact=True)
                    for _ in range(200):
                        if nav.evaluate('(e)=>e===document.activeElement'):break
                        page.keyboard.press('Tab')
                    expect(nav).to_be_focused()
                    m=record('navigation-focus',False)
                    assert 'solid' in m['focus']['outline'] and m['focus']['ratio']>=3,m['focus']
                page.get_by_role('button',name='Cancelar',exact=True).click()
                for name,plan in [('good',good),('bad',bad)]:
                    seller=context.request.get(base+f"/api/sellers/{plan['seller']}/").json()
                    go(f"/sellers/{seller['id']}",seller['name'])
                    page.get_by_role('button',name='Historial y resultados',exact=True).click()
                    expect(page.get_by_role('link',name=plan['title'],exact=True)).to_be_visible()
                    record(f'history-{name}-{width}')
            cases=[('achieved',good),('not-achieved',bad)]
            if strict:cases += [('not-evaluable',pending),('legacy',legacy)]
            for name,plan in cases+[('active',active)]:
                go(f"/plans/{plan['id']}",plan['title']);record(f'{name}-{width}')
                semantics.append({'screen':name,'viewport':width,'header':page.locator('.heading-actions').inner_text(),
                    'panel':page.locator('.closure-panel').inner_text() if name!='active' else None,
                    'closed_bg':page.locator('.heading-actions .badge-closed,.heading-actions .badge-cancelled').evaluate('(e)=>getComputedStyle(e).backgroundColor') if name!='active' else None})
                if strict and name!='active':
                    expect(page.locator('.heading-actions').get_by_text('Estado',exact=True)).to_be_visible()
                    label={'achieved':'Objetivo alcanzado','not-achieved':'Objetivo no alcanzado','not-evaluable':'No evaluable','legacy':'Sin resultado registrado'}[name]
                    expect(page.locator('.closure-panel').get_by_text(label,exact=True)).to_be_visible()
                    expect(page.locator('.page-heading').get_by_text(label,exact=True)).to_be_visible()
                    if name in ['legacy','not-evaluable']:
                        expect(page.get_by_role('heading',name='Sin acciones registradas',exact=True)).to_be_visible()
                        expect(page.get_by_role('heading',name='Sin revisiones registradas',exact=True)).to_be_visible()
                        assert 'antes de activarse' not in page.locator('main').inner_text()
            page.get_by_role('button',name='Editar plan',exact=True).click();record(f'edit-{width}')
            if strict:
                page.get_by_label('Fecha objetivo del plan').fill('2026-01-01')
                page.get_by_role('button',name='Guardar cambios',exact=True).click()
                expect(page.get_by_role('alert')).to_be_focused();record(f'validation-{width}')
                page.get_by_label('Fecha objetivo del plan').fill(active['due_date'])
            page.get_by_role('button',name='Cancelar',exact=True).click()
            for name,button in [('action','Añadir acción'),('review','Registrar revisión'),('close','Finalizar plan')]:
                page.get_by_role('button',name=button,exact=True).click();record(f'{name}-{width}')
                page.keyboard.press('Escape');expect(page.get_by_role('dialog')).to_have_count(0)
            page.get_by_role('button',name='Editar plan',exact=True).click()
            page.get_by_label('Título del plan').fill('Texto ficticio pendiente de contraste')
            page.get_by_role('button',name='Cancelar',exact=True).click();record(f'warning-{width}')
            page.get_by_role('button',name='Descartar los cambios y abandonar').click()
            if strict:
                def failed_overview(route):route.fulfill(status=503,json={'detail':'Fallo ficticio controlado para medir el mensaje'})
                page.route('**/api/overview/',failed_overview)
                go('/')
                expect(page.locator('.error-state')).to_be_visible();record(f'error-{width}')
                page.unroute('**/api/overview/',failed_overview)
                page.get_by_role('button',name='Volver a intentar').click()
                expect(page.get_by_role('heading',name='Prioridades de la semana')).to_be_visible()
            print(('OK' if strict else 'BEFORE')+f': contrast and semantic states {width}x{height}',flush=True)
        assert before==context.request.get(detail_url).json()['closure_evaluation'],'La instantánea de cierre ha cambiado'
        if strict:
            assert AXE.exists(),'Falta axe-core en el entorno de QA'
            assert not [(s['screen'],v['id']) for s in scans for v in s['violations']],scans
        assert not errors,errors
        report={'browser':browser.version,'strict':strict,'screens':len(samples),'axe_scans':len(scans),'page_errors':errors,
            'violations':sorted({v['id'] for s in scans for v in s['violations']}),'semantics':semantics,'closure_snapshot_unchanged':True}
        (artifacts/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        browser.close()
    return report


def run_all(**args):
    return {'contrast':contrast_flow(**args),'keyboard':keyboard_flow(**args),'phase1':navigation_flow(**args),
            'responsive':responsive_flow(**args),'full_flow':full_flow(**args)}


if __name__=='__main__':
    verify_phase3.SEED+=extra_fixtures('evaluador_qa')+'''
from sellers.models import Seller
u=get_user_model().objects.get(username="evaluador_qa")
Seller.objects.bulk_create([Seller(name=f"ZZ Ficticio Teclado {i}",reference=f"KEY-QA-{i}",owner=u) for i in range(55)])
'''
    verify_phase3.run_flow=run_all
    verify_phase3.main()
