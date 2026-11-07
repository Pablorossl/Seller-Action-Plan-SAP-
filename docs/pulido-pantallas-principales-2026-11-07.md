# Pulido de pantallas principales

Fecha: 07/11/2026. Base inspeccionada: `b0de624`, árbol limpio al comenzar. Trabajo local sin commits, pushes ni despliegues.

## Inspección previa al producto

Se revisaron los cinco informes solicitados: navegación segura, responsive, foco/teclado, contraste/semántica y sistema visual. Sigue disponible la auditoría en `/tmp/sap-ux-audit-20261107/AUDITORIA-UX-UI-SAP.md`; se consultaron sus hallazgos UX08–13, UX15–17, UX23–26 y UX29 y las referencias E01–E18/E21. Las mejoras ya resueltas no se presentan como problemas nuevos.

Se inspeccionaron las páginas React, componentes y estilos compartidos, los contratos de resumen y paginación y los verificadores anteriores. No hay AGENTS.md aplicable. La reproducción previa usa Chromium con una SQLite temporal nueva, demo oficial y agentes/vendedores ficticios. El volumen adicional se crea mediante la API real con CSRF: dieciséis borradores y doce acciones válidas, suficientes para páginas parciales y resúmenes truncados. No se utilizan cuentas ni conexiones reales.

El recorrido incluye dashboard, directorio/página 2/búsqueda vacía, ficha con y sin observaciones e historial, listado/página 2/por revisar, detalle activo/borrador, edición/validación/éxito, acciones, revisión, finalización y cierres alcanzado e incumplido; además carga retenida y error 503 deliberado con recuperación. Se capturan escritorio 1440 × 900, tablet 768 × 1024 y móvil 375 × 812. El verificador guarda texto, estilos computados y capturas en `artifacts/screen-polish/before/screens/`.

## Problemas reproducidos y criterio de intervención

| Pantalla | Problema real / causa | Mejora acotada |
| --- | --- | --- |
| Dashboard | Vendedores asignados y totales generales preceden a vencimientos/revisiones. En móvil, el bloque lima antecede a las revisiones pendientes. | Orden operativo en DOM: vencidas, por revisar, pendientes, abiertos y totales; revisiones antes del contexto de calidad. No cambia números, criterios ni orden de prioridades. |
| Dashboard con volumen | El contador muestra todas las prioridades/revisiones pero las listas solo diez/cinco; el límite no se lee junto al resumen. | Mostrar «Mostrando N de total» con los tamaños reales de los arrays y los contadores recibidos. Conservar los enlaces a planes, sin prometer una cola completa. |
| Directorio | El contador de planes abiertos aparece después de identificador/agente, aunque es la señal operativa de la fila. El vacío con filtro solo invita a probar otra búsqueda. | Adelantar la columna de planes abiertos conservando todos los campos y acciones; ofrecer restablecer filtros con foco devuelto a la búsqueda. |
| Paginación compartida | «Página 2» no informa rango ni total; una lista vacía muestra «Página 1». | Mostrar rango y páginas usando count/results y los tamaños de página del contrato existente (20/50); vacío explícito. Conservar foco de paginación, botones y sus estados. |
| Ficha de vendedor | «Indicadores de calidad» y la evolución del plan no explican suficientemente que son fuentes diferentes. La condición para crear solo se conoce al leer el vacío o entrar al formulario. | Aclarar observaciones del vendedor frente a revisiones del plan; advertencia junto al CTA cuando la consulta actual devuelve cero, sin deshabilitar acceso ni inferir datos cuando hay carga/error. |
| Lista de planes | Solo fecha objetivo; omite próxima revisión, próxima acción y recuento pendiente que ya entrega la API. Un vacío usa la misma invitación genérica. | Agrupar seguimiento en columna identificada, separar fechas y mantener todos los datos previos. Mostrar fuentes textuales y acción contextual al plan. Reinicio de filtros sin eliminar restricciones de cartera/contexto. |
| Detalle activo/borrador | Finalizar es el botón principal; el trabajo diario requiere bajar a las secciones. | Llevar al encabezado la acción ya existente pertinente (acción en borrador, revisión en seguimiento), con idénticos permisos; finalización secundaria y explícita. Sin duplicar controles con el mismo nombre. |
| Edición | El título es genérico; la identidad del plan solo aparece por ID y dentro de los campos. La banda superior parece un asistente, pero no permite saltar. | Mantener ID/volver y añadir título/vendedor al contexto; índice de tres botones que enfoca sus encabezados sin cambiar hash ni desmontar formulario. Sigue siendo un formulario continuo. |
| Validación | El resumen muestra `due_date`, `metrics`, `target_value` y `detail`. | Traducir claves conocidas y conservar íntegros los mensajes del servidor, índices y errores desconocidos. Mantener alert, foco, valores y asociaciones de campo. |
| Revisiones | La valoración humana aparece como badge sin calificador frente a la evaluación medida; ayuda con jerga técnica. | Etiquetar valoración del agente y explicar su diferencia con el resultado calculado, sin cambiar selección inicial, payload ni evaluación. Ayuda de objetivos en lenguaje operativo. |
| Éxito | El mismo mensaje genérico aparece para plan, acción, indicador, revisión y cierre. | Confirmaciones concretas por operación conservando role=status, foco y respuesta autoritativa. |

No se cambia una pantalla por preferencia estética: se reutilizan paleta, tipografía, superficies, badges, Field, ScrollableTable y diálogo existentes. Carga/error y cierre histórico se inspeccionan aunque sus estructuras no necesitan otra presentación. No se añade un score, una cola de tareas, filtros nuevos, datos ni una barra adhesiva de diálogo. La conservación del contexto de búsqueda entre rutas y la simplificación del selector con una sola opción se documentan como trabajo separado de interacción; no se altera el router ni la selección autorizada en esta fase.

## Cambios realizados

**Dashboard.** Los seis contadores mantienen datos y destinos. Se ordenan en el DOM por trabajo operativo: vencidas, por revisar, pendientes, abiertos, vendedores y cerrados. La sección Por revisar precede al bloque de contexto de calidad tanto visualmente como en el recorrido de teclado. Los arrays y contadores del servidor alimentan «Mostrando N de total». No se cambian los límites diez/cinco, los criterios ni la ordenación de acciones. El enlace de continuación sigue llevando a planes abiertos, sin prometer una cola de prioridades nueva.

**Directorio y ficha.** Se adelanta Planes abiertos y se conservan identificador, agente, registro y Ver ficha. El vacío filtrado permite restablecer búsqueda/filtro/página y devuelve el foco al input. La ficha identifica las observaciones del vendedor y los resultados propios de los planes como fuentes separadas. Cuando la consulta de indicadores devuelve cero se añade la condición de observación inicial junto a Crear plan; el enlace sigue disponible y la validación sigue siendo del servidor. Ni la carga ni el error se presentan como ausencia de datos; la ayuda invita también a consultar el histórico.

**Listado de planes.** La tabla compartida añade Próximo seguimiento con revisión, recuento pendiente, próxima acción y plazo de esa acción, suministrados por el resumen. El enlace de acción usa el destino contextual existente y enfoca la acción concreta. La fecha objetivo del plan conserva su propia columna. En finalizados se indica Seguimiento finalizado; estado y resultado histórico mantienen sus componentes separados. No se inventa una evaluación actual para resúmenes abiertos, cuyo contrato no la incluye. La selección contextual de vendedor se explica con acceso a su ficha; quitar filtro nombra vendedor/revisión. Restablecer búsqueda y estado conserva esa selección contextual y el foco.

**Detalle y seguimiento.** En borrador se traslada al encabezado Añadir acción cuando el permiso ya la permitía; en seguimiento se traslada Registrar revisión. Sus controles no se duplican: la otra operación permanece en su sección. Finalizar plan pasa a secundario, conservando permiso, diálogo, motivo y confirmación irreversible. La evaluación recibida aparece también junto a la identidad del plan; no se infiere del estado. Las revisiones califican su badge como Valoración del agente y el formulario explica que no sustituye el resultado medido. Se conserva el valor inicial de valoración y todo el histórico.

**Formulario continuo.** La edición añade título y vendedor junto al ID. El índice se anuncia como navegación de secciones y contiene botones nativos con texto visible. Cada botón enfoca un H2 y lo desplaza al encuadre con margen para la cabecera. No cambia el hash, no invoca el router, no desmonta el formulario ni lo convierte en un wizard. La ayuda de objetivos explica la dirección de mejora sin mencionar la implementación. Se mantienen los campos y el selector de responsables completo.

**Mensajes y paginación.** Un formateador puro traduce claves conocidas, conserva errores anidados/índices, permite nombres de campo propios de cada contexto y mantiene todos los textos del servidor. Los errores generales no muestran prefijos como `detail`. Las claves desconocidas tienen fallback legible, sin descartarse. No se traduce el contrato ni se modifica ApiError. Las confirmaciones de plan, indicador, acción, revisión, rectificación, transición y cierre identifican la operación y mantienen role=status. La paginación presenta rango real, total y páginas; el vacío indica 0 registros/Sin páginas. Los botones, las URLs de paginación del servidor y su foco de retorno siguen funcionando.

Los tamaños de página se comprobaron en los contratos actuales: vendedores/observaciones 50; planes/responsables 20. Se pasa 20 explícitamente en listado de planes, planes del vendedor y picker de responsables. Se calculan los rangos con el tamaño conocido y la longitud recibida, no con el tamaño de la última página parcial. No hay peticiones adicionales por fila ni una descarga completa del listado en el producto.

## Archivos modificados

| Archivo | Cambio |
| --- | --- |
| `frontend/src/pages/Workspace.jsx` | Jerarquía de dashboard/directorio, límites de resúmenes, próxima tarea/fechas, contexto de filtros, vacíos y fuentes de la ficha. |
| `frontend/src/pages/PlanDetail.jsx` | Acciones principales por contexto con permisos previos, evaluación en cabecera, valoración humana explícita y confirmaciones concretas. |
| `frontend/src/pages/PlanForm.jsx` | Identidad en edición, índice de secciones con foco, ayuda operativa y tamaño de página de responsables. |
| `frontend/src/components/ui.jsx` | Paginación compartida, SearchBox controlable compatible con sus usos locales y formateador de errores con etiquetas contextuales. |
| `frontend/src/services/uiPresentation.js` (nuevo) | Formateo puro de errores y cálculo de rango/páginas. |
| `frontend/src/services/uiPresentation.test.js` (nuevo) | Nueve tests de errores anidados/desconocidos/contextuales y páginas parciales/vacías. |
| `frontend/package.json` | Incorpora la nueva suite JavaScript; no añade dependencias. |
| `frontend/src/styles.css` | Composición mínima con tokens existentes: índice, contexto, valoración y columna de seguimiento. |
| `scripts/verify_screen_polish.py` (nuevo) | Recorrido específico, fixtures por API, teclado, contraste, axe y capturas; integra las regresiones anteriores en PostgreSQL temporal. |
| `scripts/verify_accessibility.py` | Actualiza únicamente el texto esperado de Página 2 a Página 2 de 2, conservando la aserción de foco. |
| `scripts/measure_contrast.js` | Incluye los nuevos contextos de texto en las muestras computadas. |
| Este informe (nuevo) | Inspección previa, motivos, decisiones, pruebas, evidencias y límites. |

No se modifican backend, modelos, migraciones, servicios de negocio, endpoints, contratos, autenticación/CSRF, rutas, guard de datos pendientes, revisión/idempotencia ni dependencias. Se consultó también `docs/trazabilidad-requisitos.md`: Django/DRF, React integrado y los elementos académicos existentes se conservan. No se certifica la evaluación académica ni se regeneran memoria, vídeo, presentación o publicación.

## QA y contraste

Comandos desde la raíz con Node 22 en PATH, Python de QA con Playwright, venv Django, PostgreSQL local, OpenSSL y axe-core disponible mediante SAP_AXE_PATH o la ruta temporal de QA ya utilizada:

```sh
npm test
npm run build
python3 scripts/verify_screen_polish.py --artifacts artifacts/screen-polish/final
git diff --check
```

La reproducción y comprobación dirigida se ejecutan con `/tmp/sap-screen-polish-dev.py before|after`, que crea y elimina una SQLite, cuenta ficticia y servidor local nuevos. La validación integrada utiliza `verify_phase3` con PostgreSQL y TLS temporales: sobrescribe explícitamente la conexión configurada, ejecuta Django y las regresiones y elimina el clúster/servidor al finalizar. El volumen de esta fase se crea después de las regresiones anteriores para no alterar sus fixtures. `release-repeat` solo ejecuta migraciones/estáticos dentro de QA; no despliega.

Durante QA se detectó `label-content-name-mismatch` en la primera versión del índice: se corrigió usando su texto nativo y un espacio visible entre número y etiqueta, sin forzar otro nombre ARIA. Se corrigieron también selectores/sincronización y dos supuestos del nuevo verificador: una entrada obligatoria añade * al nombre accesible, y la próxima acción debe consultarse en el resumen (el detalle no garantiza ese campo prefetched). Los intentos incompletos no se presentan como superados ni como defectos nuevos del backend.

Se inspeccionan manualmente las capturas, los colores computados y la relación texto/fondo; la medición usa luminancia relativa sRGB y compara valores sin redondear. Se mantienen los umbrales de referencia de 4,5:1 para texto normal y 3:1 para información gráfica necesaria. No se introducen colores nuevos ni se reduce contraste para ganar jerarquía.

| Contexto nuevo o reubicado | Texto / fondo | Ratio medido |
| --- | --- | ---: |
| Límite del resumen / valoración del agente | `#53665c / #ffffff` | 6,14:1 |
| Condición de creación junto al CTA | `#53665c / #f5f7f6` | 5,70:1 |
| Seguimiento en tabla | `#1c302d / #ffffff` | 13,91:1 |
| Seguimiento sobre hover de fila | `#1c302d / #fcfdfb` | 13,63:1 |
| Enlace de próxima acción | `#146952 / #ffffff` | 6,62:1 |
| Botones del índice | `#4c6546 / #ffffff` | 6,45:1 |
| Número de sección | `#45672f / #e3efd7` | 5,44:1 |
| Identidad en edición | `#183831 / #f5f7f6` | 11,84:1 |

La inspección visual complementa estas mediciones; no se confunde una lectura DOM con un estudio de comprensión de usuarios. No se desactivan reglas de axe y se conserva su salida incomplete.

La revisión integrada del contexto de vendedor detectó también `link-in-text-block` en «Ver su ficha»: aunque contrastaba con el fondo, su color era demasiado próximo al texto contiguo para distinguir el enlace sin otra señal. Se añadió subrayado permanente, manteniendo la paleta. Se vuelve a ejecutar el estado afectado y el recorrido completo; ese intento no se cuenta como validación final.

La primera integración completó las regresiones y el Full Stack, pero se detuvo al buscar la fixture por el título que la prueba de textos largos había modificado. Se corrigió el verificador para seleccionar por identidad estable de vendedor y preparar de nuevo un título legible exclusivamente en esa base ficticia, mediante la API y su revisión. Se conserva ese intento en `artifacts/screen-polish/integration-incomplete/`; no se presenta como validación integrada terminada. No fue una regresión del producto.

## Resultados finales ejecutados

Todos los resultados de esta tabla corresponden a la compilación final, incluido el subrayado del enlace contextual. La ejecución integrada terminó con código 0, reinicios/restauración comprobados y recursos temporales eliminados. La comprobación dirigida anterior está en `artifacts/screen-polish/after/`; no sustituye ni se suma a la integrada.

| Comprobación | Resultado | Evidencia |
| --- | --- | --- |
| JavaScript con Node 22 | **35/35**, incluidos nueve nuevos; cero fallos | [Log](../artifacts/screen-polish/js-tests.log) |
| Compilación Vite | **Correcta**, 38 módulos | [Log](../artifacts/screen-polish/build.log) |
| Django/PostgreSQL | **116/116**, sin omisiones, PostgreSQL 14.24 | [Log](../artifacts/screen-polish/final/postgres-tests.log) |
| Esquema y configuración | Migraciones nuevas/pendientes, ausencia de deriva y comprobación de producción: **correctas** | [Resultado integrado y logs asociados](../artifacts/screen-polish/final/result.json) |
| Pantallas de esta fase | **73 estados**, 1440 × 900 / 768 × 1024 / 375 × 812; cero errores de página, snapshot de cierre conservado | [Resultado](../artifacts/screen-polish/final/browser/screens/result.json), [observaciones y mediciones](../artifacts/screen-polish/final/browser/screens/observations.json) |
| axe de esta fase | **73 análisis**, cero infracciones detectadas | [Salida completa](../artifacts/screen-polish/final/browser/screens/axe.json) |
| Sistema visual compartido | **33 estados**, cero errores de página; **12 análisis axe** sin infracciones | [Resultado](../artifacts/screen-polish/final/browser/components/result.json), [axe](../artifacts/screen-polish/final/browser/components/axe.json) |
| Contraste/semántica | **58 estados/variantes**, muestras dentro de los umbrales aplicados; **54 análisis axe** sin infracciones | [Resultado](../artifacts/screen-polish/final/browser/contrast/result.json), [mediciones](../artifacts/screen-polish/final/browser/contrast/measurements.json), [axe](../artifacts/screen-polish/final/browser/contrast/axe.json) |
| Foco/teclado | **12 grupos**, cero errores de página; **10 análisis axe** sin infracciones | [Resultado y foco observado](../artifacts/screen-polish/final/browser/keyboard/result.json), [axe](../artifacts/screen-polish/final/browser/keyboard/axe.json) |
| Navegación segura | **20/20 grupos**, incluido aviso nativo de recarga | [Resultado](../artifacts/screen-polish/final/browser/navigation/result.json) |
| Responsive | **128 estados**, seis tamaños, textos largos y reflow; cero errores de página | [Resultado](../artifacts/screen-polish/final/browser/responsive/result.json), [mediciones](../artifacts/screen-polish/final/browser/responsive/measurements.json) |
| Full Stack | Creación a cierre alcanzado, recarga, CSRF, cartera ajena, logout y recuperación JSON/HTML: **correctos** | [Resultado](../artifacts/screen-polish/final/browser/browser-result.json) |
| Persistencia/recuperación | **Correctas** tras reiniciar PostgreSQL/Gunicorn, repetir el script local y restaurar backup en otra base temporal | [Resultado integrado](../artifacts/screen-polish/final/result.json) |
| Diferencias | `git diff --check`: **correcto** | Revisión local final |

Se ejecutaron **149 análisis axe** en la integración final (73 + 12 + 54 + 10), con cero infracciones detectadas y sin reglas desactivadas. No son 149 pantallas distintas ni tests unitarios. Las entradas incomplete conservan `color-contrast` y, en las muestras históricas sin métricas, `th-has-data-cells`; no se declaran resueltas universalmente por no aparecer como violations. No se suman ejecuciones repetidas o incompletas como pruebas adicionales superadas.

Herramientas utilizadas: Chromium **151.0.7922.34** headless, Playwright, axe-core **4.14.0**, Node 22, Django del venv y PostgreSQL local **14.24**. No se ha conectado a Neon ni producción. La confirmación específica de edición se verificó también leyendo el texto capturado tras el guardado real: «Plan actualizado correctamente. El histórico se conserva.»

## Alcance de las regresiones

Se repiten las suites anteriores completas mediante su composición existente:

- Navegación segura: volver/cancelar con el mismo ID, continuar/descartar, reversión de valores, errores reales e inyectados con valores conservados, un envío/clave de reintento, Atrás/Adelante, recarga nativa, diálogos y logout con CSRF.
- Teclado: destino de ruta/prioridad/paginación, limpiar búsqueda, selector e historial, Tab/Shift+Tab, foco ocupado/restaurado/alternativo, aviso anidado, menú compacto y tabla con flechas/acción final.
- Responsive: seis viewports de 320 a 1440 px, contenido largo y reflow de 720 × 450 y 360 × 225. Tablas con scroll local y últimas acciones, formularios y diálogos accesibles sin ocultar columnas.
- Sistema visual/contraste: variantes de tabla, mínimos de lectura/acciones, superficies, errores, placeholders, foco y semántica de cierres alcanzado/incumplido, no evaluable y sin resultado registrado.
- Full Stack: login, consulta, creación, validación, edición, acción, activación, revisión/rectificación, evaluación, cierre, recarga, CSRF, cartera ajena rechazada y logout. Persistencia tras reinicios y backup/restauración independiente.

El recorrido nuevo añade comprobaciones por teclado del índice con un título pendiente (URL y valores intactos), restablecer filtros con foco en búsqueda, preservación del vendedor al restablecer un listado contextual y apertura de la próxima acción con el foco en su artículo. Comprueba título/CTA en edición, primaria contextual y cierre secundario, evaluación/valoración con fuente explícita, error real traducido conservando campos y éxito real. La preparación de datos y algunas búsquedas usan ratón/fill; no se presenta todo ese recorrido como una sesión exclusivamente de teclado. La suite dedicada anterior sí recorre sus controles con teclas.

No quedan regresiones funcionales detectadas en los recorridos ejecutados. La revisión final de capturas comprobó la acción primaria en móvil, el cierre neutro incumplido, el enlace contextual subrayado y las instrucciones del formulario, además del recorrido previo de desktop/tablet/móvil.

## Capturas y evidencias

- Dashboard con volumen: [antes escritorio](../artifacts/screen-polish/before/screens/dashboard-volume-1440.png) / [después escritorio](../artifacts/screen-polish/final/browser/screens/dashboard-volume-1440.png), [antes móvil](../artifacts/screen-polish/before/screens/dashboard-volume-375.png) / [después móvil](../artifacts/screen-polish/final/browser/screens/dashboard-volume-375.png).
- Directorio: [antes](../artifacts/screen-polish/before/screens/sellers-1440.png) / [después](../artifacts/screen-polish/final/browser/screens/sellers-1440.png). Página parcial móvil: [antes](../artifacts/screen-polish/before/screens/sellers-page2-375.png) / [después](../artifacts/screen-polish/final/browser/screens/sellers-page2-375.png).
- Ficha sin observaciones: [antes tablet](../artifacts/screen-polish/before/screens/seller-no-data-768.png) / [después tablet](../artifacts/screen-polish/final/browser/screens/seller-no-data-768.png).
- Listado, segunda página móvil: [antes](../artifacts/screen-polish/before/screens/plans-page2-375.png) / [después](../artifacts/screen-polish/final/browser/screens/plans-page2-375.png). [Seguimiento y próxima acción](../artifacts/screen-polish/final/browser/screens/plans-followup-1440.png), [vacío contextual y enlace subrayado](../artifacts/screen-polish/final/browser/screens/plans-context-empty-768.png).
- Edición: [antes tablet](../artifacts/screen-polish/before/screens/edit-768.png) / [después tablet](../artifacts/screen-polish/final/browser/screens/edit-768.png). Validación móvil: [antes](../artifacts/screen-polish/before/screens/validation-375.png) / [después](../artifacts/screen-polish/final/browser/screens/validation-375.png).
- Detalle/acción principal: [antes](../artifacts/screen-polish/before/screens/plan-active-1440.png) / [después](../artifacts/screen-polish/final/browser/screens/plan-active-1440.png), [cabecera móvil final](../artifacts/screen-polish/final/browser/contrast/active-375.png).
- [Revisión móvil](../artifacts/screen-polish/final/browser/screens/review-375.png), [finalización móvil](../artifacts/screen-polish/final/browser/screens/close-375.png), [cierre incumplido neutro](../artifacts/screen-polish/final/browser/contrast/not-achieved-1440.png), [éxito específico](../artifacts/screen-polish/final/browser/screens/success-1440.png).
- [Foco de tabla móvil](../artifacts/screen-polish/final/browser/keyboard/mobile-table-focus.png), [aviso de cambios pendientes](../artifacts/screen-polish/final/browser/navigation/mobile-warning.png), [recuperación de error móvil](../artifacts/screen-polish/final/browser/screens/error-375.png).

Las capturas `screens/` son de página completa salvo diálogos, que muestran el viewport. `contrast/` y teclado muestran el viewport. Se capturaron 64 estados previos y 73 finales: los nueve adicionales verifican el vacío contextual y el enlace de seguimiento por tamaño. Los datos finales incluyen también las escrituras y casos largos de las regresiones anteriores; se prepara de nuevo el título legible de la fixture por API, pero algunos contadores/filas difieren. Son comparaciones representativas, no imágenes de píxeles/contenidos idénticos. Los hallazgos y capturas históricas de la auditoría se consultaron como referencia, sin atribuir sus verificaciones a esta fase.

## Límites y riesgos pendientes

No se declara conformidad WCAG completa. Chromium headless, axe y mediciones de muestras no cubren todas las tecnologías de asistencia ni combinaciones de contenido/permisos. Las entradas incomplete se conservan; cero infracciones detectadas no equivale a ausencia universal de barreras. No se han probado lectores de pantalla, Firefox, Safari, dispositivos físicos, teclado virtual ni zoom nativo con interfaz. El reflow CSS equivalente a 200/400 % se separa del zoom nativo, que no cambió el viewport en este entorno.

Los listados aún conservan búsqueda/filtro/página en estado local: al salir y volver hay que repetir la selección. No se serializa ese estado en la URL ni se modifica el router/guard en esta fase. Restablecer filtros es una mejora del listado actual, no una solución de persistencia de contexto. El picker de responsable sigue completo aunque solo exista una opción; una simplificación posterior deberá respetar autorización, precarga y foco. La recuperación guiada de conflictos 409 sigue pendiente; se conservan mensajes y valores, sin recargar o sobrescribir automáticamente.

La columna de seguimiento puede aumentar el ancho local de la tabla; se mantiene la indicación de scroll y se verifica su acceso. El dashboard sigue siendo un resumen de diez acciones/cinco revisiones, ahora explícito, no una cola completa. La cabecera y las acciones de diálogos largos conservan el scroll interno existente; no se añade una barra adhesiva. Las tipografías de marca y la carga externa de DM Sans permanecen como estaban.

Los tamaños de página de presentación deben actualizarse si cambia el contrato del servidor. La advertencia de observación inicial usa solo el resultado de la consulta visible; no bloquea crear ni infiere que una carga/error o una observación futura equivalgan a ausencia global de datos. Los badges conservan texto además de color y el resultado final sigue leyendo la instantánea registrada, con fallback explícito si falta.

El entorno es local con PostgreSQL 14.24; no certifica producción, otra versión, disponibilidad pública ni todas las combinaciones de permisos. La trazabilidad académica se conserva, pero no se revalida la guía externa ni se certifica la entrega/evaluación docente. No se regeneran memoria/vídeo ni se publican cambios. Los artefactos están ignorados por Git y disponibles localmente; la auditoría original y el runner de reproducción en `/tmp` no constituyen almacenamiento permanente.

## Veredicto

**LISTO PARA QA INTEGRAL**, en el alcance local probado. Las pantallas aclaran prioridades, fuentes, fechas, tareas disponibles y mensajes usando el sistema visual existente; las regresiones anteriores y el recorrido integrado pasan sobre la versión final. No quedan defectos bloqueantes detectados de esta intervención. Los límites de navegadores, lectores de pantalla, contexto persistente y validación pública permanecen explícitos; el veredicto no certifica conformidad WCAG completa ni evaluación académica.
