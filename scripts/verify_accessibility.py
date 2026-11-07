"""Recorridos de teclado reales, foco y regresiones sobre PostgreSQL temporal.

python3 scripts/verify_accessibility.py --artifacts artifacts/ux-keyboard/isolated
SAP_AXE_PATH puede apuntar a axe.min.js instalado solo en el entorno de QA.
"""
import json
import os
from datetime import date, timedelta
from uuid import uuid4
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import verify_phase3
from verify_responsive import responsive_flow
from verify_unsaved_changes import navigation_flow
from verify_browser import run_flow as full_flow

AXE = Path(os.environ.get('SAP_AXE_PATH','/tmp/sap-accessibility-tools/node_modules/axe-core/axe.min.js'))


def keyboard_flow(*,base,username,password,artifacts,local_tls=False,strict=True,**unused):
    artifacts=Path(artifacts)/'keyboard';artifacts.mkdir(parents=True,exist_ok=True)
    checks=[]; observations=[];errors=[];scans=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        context=browser.new_context(ignore_https_errors=local_tls,locale='es-ES',viewport={'width':1440,'height':900})
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        def tab_to(locator,backwards=False,limit=240):
            for _ in range(limit):
                if locator.count()==1 and locator.evaluate('(e)=>e===document.activeElement'):return
                page.keyboard.press('Shift+Tab' if backwards else 'Tab')
            raise AssertionError('Control no alcanzable mediante Tab: '+str(locator))
        def activate(locator,key='Enter'):
            tab_to(locator);page.keyboard.press(key)
        def type_text(locator,text):
            tab_to(locator);page.keyboard.press('Control+A');page.keyboard.insert_text(text)
        def type_date(locator,value):
            # Use native date segments and arrow keys only; never assign a DOM
            # value or dispatch a synthetic change to bypass React/validation.
            tab_to(locator)
            for _ in range(4):page.keyboard.press('ArrowLeft')
            for _ in range(3):
                page.keyboard.press('ArrowUp');page.keyboard.press('ArrowRight')
            for _ in range(4):page.keyboard.press('ArrowLeft')
            before=locator.input_value().split('-')
            assert len(before)==3,(value,before)
            page.keyboard.press('ArrowUp')
            changed=locator.input_value().split('-')
            page.keyboard.press('ArrowDown')
            if changed[2]!=before[2]:order=[2,1,0]
            elif changed[1]!=before[1]:order=[1,2,0]
            else:order=[0,1,2]
            target=value.split('-')
            for index in order:
                current=locator.input_value().split('-')
                difference=int(target[index])-int(current[index])
                for _ in range(abs(difference)):
                    page.keyboard.press('ArrowUp' if difference>0 else 'ArrowDown')
                page.keyboard.press('ArrowRight')
            assert locator.input_value()==value,(locator.input_value(),value)
        def snapshot(name):
            state=page.evaluate('''() => {const e=document.activeElement,r=e.getBoundingClientRect();return {
                tag:e.tagName,id:e.id,text:e.textContent.trim().slice(0,100),name:e.getAttribute('aria-label'),
                outline:getComputedStyle(e).outline,visible:!!(r.width&&r.height),top:r.top,bottom:r.bottom};}''')
            observations.append({'screen':name,'focus':state,'url_hash':page.evaluate('location.hash')})
            page.screenshot(path=str(artifacts/(name+'.png')))
            return state
        def check(name):
            checks.append(name);print(('OK: ' if strict else 'BEFORE: ')+name,flush=True)
        def scan(name):
            if not AXE.exists():return
            page.add_script_tag(path=str(AXE))
            result=page.evaluate('''async () => { const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});
                return {version:axe.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,
                  nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))})),incomplete:r.incomplete.map(v=>v.id)}; }''')
            scans.append({'screen':name,**result})
            (artifacts/'axe.json').write_text(json.dumps(scans,ensure_ascii=False,indent=2))
        def go(route):
            page.goto(base+'/dashboard/#'+route)
            expect(page.locator('main .loading')).to_have_count(0)
            page.wait_for_load_state('networkidle')
        page.goto(base+'/accounts/login/')
        type_text(page.get_by_label('Nombre de usuario'),username)
        type_text(page.get_by_label('Contraseña'),password)
        activate(page.get_by_role('button',name='Entrar en mi espacio'))
        expect(page.get_by_role('heading',name='Prioridades de la semana')).to_be_visible()
        scan('dashboard')
        activate(page.get_by_role('link',name='Vendedores',exact=True))
        expect(page.locator('main h1')).to_have_text('Vendedores')
        if strict:expect(page.locator('main h1')).to_be_focused()
        snapshot('route-sellers')
        activate(page.get_by_role('button',name='Siguiente',exact=True),'Space')
        expect(page.get_by_text('Página 2',exact=True)).to_be_visible()
        if strict:expect(page.get_by_text('Página 2',exact=True)).to_be_focused()
        snapshot('pagination')
        check('Navegación de ruta y paginación con Tab/Enter/Espacio')
        type_text(page.get_by_label('Buscar por nombre o identificador…'),'SAP-EVAL-ACTIVO')
        page.keyboard.press('Enter')
        expect(page.get_by_role('link',name='Tienda Ficticia Activo',exact=True)).to_be_visible()
        if strict:expect(page.get_by_label('Buscar por nombre o identificador…')).to_be_focused()
        activate(page.get_by_role('button',name='Limpiar búsqueda'),'Space')
        if strict:expect(page.get_by_label('Buscar por nombre o identificador…')).to_be_focused()
        snapshot('clear-search')
        type_text(page.get_by_label('Buscar por nombre o identificador…'),'SAP-EVAL-ACTIVO');page.keyboard.press('Enter')
        activate(page.get_by_role('link',name='Tienda Ficticia Activo',exact=True))
        expect(page.locator('main h1')).to_have_text('Tienda Ficticia Activo')
        scan('seller')
        history=page.get_by_role('button',name='Historial y resultados',exact=True)
        activate(history,'Space')
        observations.append({'screen':'seller-history','aria_pressed':history.get_attribute('aria-pressed')})
        if strict:expect(history).to_have_attribute('aria-pressed','true')
        activate(page.get_by_role('button',name='Planes activos',exact=False))
        activate(page.get_by_role('link',name='Dashboard',exact=True))
        expect(page.get_by_role('heading',name='Prioridades de la semana')).to_be_visible()
        activate(page.get_by_role('button',name='Acciones vencidas',exact=False),'Space')
        if strict:expect(page.get_by_role('heading',name='Prioridades de la semana')).to_be_focused()
        snapshot('overdue-priorities')
        priority=page.locator('.priority-item').first
        activate(priority)
        expect(page.locator('.action-item.highlight')).to_be_visible()
        if strict:
            expect(page.locator('.action-item.highlight')).to_be_focused()
            box=page.locator('.action-item.highlight').bounding_box()
            assert box['y']>=0 and box['y']<900,box
        snapshot('priority-target')
        check('Estados de historial y acceso contextual desde prioridades')
        activate(page.get_by_role('button',name='Registrar revisión',exact=True),'Space')
        dialog=page.get_by_role('dialog',name='Registrar revisión',exact=True)
        expect(dialog).to_be_visible()
        snapshot('review-open')
        for key in ['Shift+Tab']*3+['Tab']*26:
            page.keyboard.press(key)
            contained=page.evaluate('document.activeElement.closest("dialog[open]")!==null')
            if not contained:observations.append({'screen':'dialog-tab-boundary','key':key,'focus':page.evaluate('document.activeElement.tagName')})
            if strict:assert contained
        page.keyboard.press('Escape')
        expect(page.get_by_role('button',name='Registrar revisión',exact=True)).to_be_focused()
        check('Diálogo nativo: Tab/Shift+Tab contenidos y Escape restaura el foco')
        activate(page.get_by_role('button',name='Rectificar revisión',exact=False).first)
        scan('correction')
        type_text(page.get_by_label('Motivo de rectificación'),'Razón ficticia conservada con teclado')
        page.keyboard.press('Escape')
        expect(page.get_by_role('button',name='Continuar editando')).to_be_focused()
        scan('unsaved-warning')
        page.keyboard.press('Space')
        expect(page.get_by_label('Motivo de rectificación')).to_have_value('Razón ficticia conservada con teclado')
        page.keyboard.press('Escape')
        activate(page.get_by_role('button',name='Descartar los cambios y abandonar'))
        expect(page.get_by_role('dialog')).to_have_count(0)
        check('Aviso anidado accesible: continuar y descartar conservan las decisiones')
        activate(page.get_by_role('button',name='Editar plan',exact=True))
        expect(page.get_by_role('heading',name='Editar diagnóstico y seguimiento')).to_be_focused()
        scan('edit')
        unassociated=page.locator('.picker-label').evaluate_all('(es)=>es.filter(e=>e.tagName==="LABEL"&&!e.control).map(e=>e.textContent)')
        observations.append({'screen':'record-picker','unassociated_labels':unassociated})
        if strict:
            assert not unassociated
            expect(page.get_by_role('group',name='Responsable del seguimiento',exact=False)).to_have_count(1)
        activate(page.get_by_role('button',name='Cancelar',exact=True))
        expect(page.get_by_role('button',name='Editar plan',exact=True)).to_be_focused()
        check('Edición: entrada y cancelación limpias mantienen identidad y foco')
        if strict:
            # Create, edit, act, review, evaluate and close using keys only.
            activate(page.get_by_role('link',name='Vendedores',exact=True))
            type_text(page.get_by_label('Buscar por nombre o identificador…'),'SAP-DEMO-PLAN');page.keyboard.press('Enter')
            activate(page.get_by_role('link',name='Tienda Ficticia Envíos',exact=True))
            activate(page.get_by_role('link',name='Crear plan',exact=True))
            expect(page.get_by_label('Título del plan')).to_be_visible()
            expect(page.locator('main h1')).to_be_focused()
            scan('create')
            title='QA teclado '+uuid4().hex[:6]
            for label,text in [('Título del plan',title),('Problema identificado','Incidencias ficticias del seis por ciento.'),
                               ('Causa raíz','Embalaje ficticio insuficiente.'),('Evidencia del diagnóstico','Cien pedidos ficticios.'),
                               ('Objetivo de mejora','Reducir las incidencias ficticias al tres por ciento.')]:
                type_text(page.get_by_label(label,exact=False),text)
            type_text(page.get_by_label('Objetivo · %'),'7')
            due=(date.today()+timedelta(days=30)).isoformat()
            type_date(page.get_by_label('Fecha objetivo del plan'),due)
            activate(page.get_by_role('button',name='Crear borrador'),'Space')
            expect(page.get_by_role('alert')).to_be_focused()
            expect(page.get_by_label('Título del plan')).to_have_value(title)
            target=page.get_by_label('Objetivo · %')
            expect(target).to_have_attribute('aria-invalid','true')
            described=target.get_attribute('aria-describedby')
            assert described and page.locator('[id="'+described+'"]').inner_text()
            snapshot('creation-validation');scan('creation-validation')
            type_text(target,'3')
            activate(page.get_by_role('button',name='Crear borrador'))
            expect(page.locator('main h1')).to_have_text(title)
            expect(page.locator('main h1')).to_be_focused()
            plan_url=page.url
            check('Crear con teclado: pickers etiquetados, fechas nativas y error asociado sin pérdida de valores')
            activate(page.get_by_role('button',name='Editar plan',exact=True))
            type_text(page.get_by_label('Título del plan'),title+' editado')
            activate(page.get_by_role('link',name='Volver al plan',exact=False))
            warning=page.get_by_role('dialog',name='Cambios sin guardar',exact=True)
            description_id=warning.get_attribute('aria-describedby')
            assert description_id and 'perderás' in page.locator('[id="'+description_id+'"]').inner_text()
            page.keyboard.press('Space')
            expect(page.get_by_label('Título del plan')).to_have_value(title+' editado')
            activate(page.get_by_role('button',name='Guardar cambios',exact=True))
            expect(page.locator('main h1')).to_have_text(title+' editado')
            expect(page.get_by_role('button',name='Editar plan',exact=True)).to_be_focused()
            assert page.url==plan_url
            check('Volver/continuar/guardar con teclado conserva ID, datos y restauración del foco')
            activate(page.get_by_role('button',name='Añadir acción',exact=True),'Space')
            expect(page.get_by_role('heading',name='Añadir acción',exact=True)).to_be_focused()
            type_text(page.get_by_label('Descripción de la acción'),'Acción ficticia registrada con teclado')
            type_text(page.get_by_label('Persona o equipo responsable'),'Equipo ficticio de teclado')
            type_date(page.get_by_label('Fecha límite'),due)
            action_pattern='**/api/plans/*/actions/'
            def held_action(route):
                expect(page.get_by_role('button',name='Cancelar',exact=True)).to_be_disabled()
                snapshot('action-busy')
                page.keyboard.press('Tab')
                assert page.evaluate('document.activeElement.closest("dialog[open]")!==null')
                page.keyboard.press('Escape')
                expect(page.get_by_role('dialog',name='Añadir acción',exact=True)).to_be_visible()
                response=route.fetch()
                route.fulfill(response=response)
            page.route(action_pattern,held_action)
            activate(page.get_by_role('dialog').get_by_role('button',name='Añadir acción',exact=True))
            expect(page.get_by_role('dialog')).to_have_count(0)
            page.unroute(action_pattern,held_action)
            expect(page.get_by_role('button',name='Añadir acción',exact=True)).to_be_focused()
            activate(page.get_by_role('button',name='Activar plan',exact=True),'Space')
            expect(page.get_by_role('button',name='Pasar a revisión')).to_be_visible()
            expect(page.locator('main h1')).to_be_focused()
            check('Acción guardada y activación: foco lógico después de desaparecer el control de transición')
            activate(page.get_by_role('button',name='Registrar revisión',exact=True))
            type_text(page.get_by_label('Valor observado'),'101')
            type_text(page.get_by_label('Pedidos del periodo'),'100')
            type_date(page.get_by_label('Inicio del periodo medido'),'2026-09-01')
            type_date(page.get_by_label('Fin del periodo medido'),'2026-09-30')
            type_text(page.get_by_label('Evolución y evidencias'),'Objetivo alcanzado en cien pedidos ficticios mediante teclado.')
            activate(page.get_by_role('button',name='Guardar revisión',exact=True),'Space')
            expect(page.get_by_role('alert')).to_be_focused()
            value_field=page.get_by_label('Valor observado')
            descriptions=value_field.get_attribute('aria-describedby').split()
            assert len(descriptions)==2
            assert all(page.locator('[id="'+identifier+'"]').inner_text() for identifier in descriptions)
            expect(page.get_by_label('Evolución y evidencias')).to_have_value('Objetivo alcanzado en cien pedidos ficticios mediante teclado.')
            type_text(value_field,'3')
            activate(page.get_by_role('button',name='Guardar revisión',exact=True),'Space')
            expect(page.get_by_role('dialog')).to_have_count(0)
            expect(page.get_by_role('button',name='Registrar revisión',exact=True)).to_be_focused()
            expect(page.get_by_text('Objetivo alcanzado',exact=True).first).to_be_visible()
            activate(page.get_by_role('button',name='Rectificar revisión',exact=False).first)
            type_text(page.get_by_label('Motivo de rectificación'),'Error ficticio de teclado para comprobar mensajes')
            # A real backend validation error on the correction reason.
            type_text(page.get_by_label('Motivo de rectificación'),' ')
            activate(page.get_by_role('button',name='Guardar revisión',exact=True))
            expect(page.get_by_role('alert')).to_be_focused()
            reason=page.get_by_label('Motivo de rectificación')
            expect(reason).to_have_attribute('aria-invalid','true')
            assert reason.get_attribute('aria-describedby')
            page.keyboard.press('Escape')
            activate(page.get_by_role('button',name='Descartar los cambios y abandonar'))
            check('Revisión/evaluación y rectificación: teclado, mensajes de campo y conservación del histórico')
            activate(page.get_by_role('button',name='Finalizar plan',exact=True),'Space')
            scan('close')
            type_text(page.get_by_label('Resultado y razones de la finalización'),'Cierre ficticio con objetivo alcanzado, acción documentada pendiente.')
            activate(page.get_by_role('checkbox'),'Space')
            activate(page.get_by_role('button',name='Confirmar finalización',exact=True))
            expect(page.get_by_role('heading',name='Resultado y cierre')).to_be_visible()
            expect(page.locator('main h1')).to_be_focused()
            snapshot('closed-fallback')
            scan('closed')
            check('Finalizar con teclado: checkbox, guardado y foco alternativo si desaparece el abridor')
            page.set_viewport_size({'width':375,'height':812})
            activate(page.get_by_role('button',name='Mostrar navegación'),'Space')
            expect(page.get_by_role('button',name='Ocultar navegación')).to_have_attribute('aria-expanded','true')
            activate(page.get_by_role('link',name='Saltar al contenido'))
            expect(page.locator('main')).to_be_focused()
            expect(page.locator('main')).not_to_have_attribute('inert','')
            activate(page.get_by_role('button',name='Mostrar navegación'))
            page.keyboard.press('Escape')
            expect(page.get_by_role('button',name='Mostrar navegación')).to_be_focused()
            activate(page.get_by_role('button',name='Mostrar navegación'))
            activate(page.get_by_role('link',name='Vendedores',exact=True))
            expect(page.locator('main h1')).to_be_focused()
            region=page.get_by_role('region',name='Directorio de vendedores',exact=True)
            tab_to(region)
            assert region.evaluate('(e)=>getComputedStyle(e).outlineStyle')=='solid'
            assert region.evaluate('(e)=>Number.parseFloat(getComputedStyle(e).outlineOffset)')<0
            page.keyboard.press('ArrowRight')
            page.wait_for_function('(e)=>e.scrollLeft>0',arg=region.element_handle())
            snapshot('mobile-table-focus')
            first_link=region.locator('tbody tr').first.locator('td').last.get_by_role('link')
            activate(first_link)
            expect(page.locator('main h1')).to_be_focused()
            scan('mobile-seller')
            check('Menú compacto, salto al contenido y tabla local con foco visible: solo teclado')
            page.set_viewport_size({'width':768,'height':1024})
            activate(page.get_by_role('button',name='Mostrar navegación'),'Space')
            page.keyboard.press('Escape')
            expect(page.get_by_role('button',name='Mostrar navegación')).to_be_focused()
            check('Tablet: apertura/cierre del menú con Espacio/Escape y foco restaurado')
            critical={'button-name','link-name','label','select-name','aria-valid-attr','aria-valid-attr-value',
                      'aria-required-attr','aria-required-children','aria-required-parent','aria-input-field-name','nested-interactive'}
            failures=[(s['screen'],v['id']) for s in scans for v in s['violations'] if v['id'] in critical]
            assert not failures,failures
        if not strict:
            page.set_viewport_size({'width':375,'height':812})
            activate(page.get_by_role('button',name='Mostrar navegación'),'Space')
            activate(page.get_by_role('link',name='Saltar al contenido'),key='Enter')
            observations.append({'screen':'skip-open-menu','main_inert':page.locator('main').get_attribute('inert'),
                                 'focus':page.evaluate('document.activeElement.textContent.trim()')})
        assert not errors,errors
        report={'strict':strict,'browser':browser.version,'checks':checks,'count':len(checks),'observations':observations,
                'page_errors':errors,'axe_available':AXE.exists(),'screen_reader':None}
        (artifacts/'result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        browser.close()
    return report


def run_all(**args):
    return {'keyboard':keyboard_flow(**args),'phase1':navigation_flow(**args),'responsive':responsive_flow(**args),'full_flow':full_flow(**args)}


if __name__=='__main__':
    verify_phase3.SEED += '''
from sellers.models import Seller
u = get_user_model().objects.get(username="evaluador_qa")
Seller.objects.bulk_create([Seller(name=f"ZZ Ficticio Teclado {i}", reference=f"KEY-QA-{i}", owner=u) for i in range(55)])
'''
    verify_phase3.run_flow=run_all
    verify_phase3.main()
