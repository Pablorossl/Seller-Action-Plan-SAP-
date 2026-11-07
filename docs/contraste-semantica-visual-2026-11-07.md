# Contraste y semántica visual

Fecha: 07/11/2026. Base inspeccionada: `0e7f596`, árbol limpio al inicio. Cambios locales; sin commits, push ni despliegues.

## Inspección y problemas reproducidos

Antes de modificar el producto se revisaron los informes de [navegación segura](ux-fase-1-navegacion-segura-2026-11-07.md), [responsive](ux-fase-2-responsive-2026-11-07.md) y [foco/teclado](accesibilidad-foco-teclado-2026-11-07.md), incluidos los resultados anteriores de axe-core: 109 apariciones de nodos con `color-contrast` entre diez estados, no 109 problemas independientes.

Está disponible la [auditoría UX/UI del 7 de noviembre](/tmp/sap-ux-audit-20261107/AUDITORIA-UX-UI-SAP.md). Se consultaron UX04/UX06 y las capturas de contraste, listados y cierre incumplido. Se inspeccionaron los estilos y componentes actuales, los serializadores y la selección de resultados de evaluación/cierre. La reproducción actual previa incluye 33 estados en Chromium con datos ficticios y [mediciones propias](../artifacts/ux-contrast/before/contrast/measurements.json).

| Problema | Ubicación y causa |
| --- | --- |
| Texto secundario poco contrastado | Descripciones, cabeceras, pie, instrucciones, marcadores de sección, fases pendientes, etiquetas de indicadores y campos de solo lectura; colores claros aplicados sobre blanco o fondos muy claros. |
| Placeholders demasiado claros | `#97a190` sobre blanco: 2,69:1. No bastaba con corregir las alertas de los textos permanentes. |
| Límites de campos difíciles de identificar | Bordes de input/textarea/select y buscador muy próximos al fondo. Los campos vacíos necesitan un límite reconocible. |
| Cerrado parecía equivalente a cumplido | `.badge-closed` compartía el verde de `achieved`, `completed` y `ok`. El panel de cierre tenía fondo/borde verde y se usaban flechas ascendentes en contextos administrativos. El contraste del badge ya era válido; el problema era su significado. |
| El listado no permitía contrastar estado y resultado | Mostraba el estado sin el resultado, aunque `closure_evaluation` ya está presente en la API de resumen. |
| Resultado no registrado tratado de forma poco robusta | La ficha accedía directamente a `closure_evaluation.result`; un histórico incompleto podía quedarse sin texto útil. La evaluación normalizada del detalle tampoco debe usarse para reconstruir un resultado histórico ausente. |
| Textos vacíos incompatibles con un plan finalizado | En planes ficticios cancelados sin registros, los paneles invitaban a activar, añadir acciones o registrar revisiones pese a no poder editarse. Se ajustó únicamente la descripción del estado vacío. |

Durante la ampliación de fixtures y del análisis WCAG 2.2 se detectó también `target-size` en enlaces de plan/vendedor de algunas filas. Se añadió una altura mínima de 24 px a esos enlaces existentes y se repitió el análisis, sin eliminar información ni acciones.

## Criterios y método de medición

Como referencia se utilizaron [WCAG 2.2, contraste de texto 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): 4,5:1 para texto normal y 3:1 para texto grande. Para la información visual necesaria para reconocer campos y estados de foco, se utilizó [contraste no textual 1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html), con 3:1 frente a colores adyacentes. El significado se comunica también mediante palabras, conforme a la referencia de [uso del color 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html).

Se obtuvieron estilos computados y fondos de los elementos renderizados, componiendo transparencias CSS y calculando luminancia relativa sRGB. Se midieron texto, placeholders, bordes de campos y anillos de foco. Los umbrales se comparan sin redondear; los valores de las tablas se redondean solo para lectura. Los controles deshabilitados se consideran la excepción aplicable, no se presentan como texto activo aprobado. Los bordes decorativos de paneles no se oscurecieron indiscriminadamente.

No se ocultó texto, se retiró foco ni se desactivó ninguna regla de axe para eliminar alertas. Se conservaron tamaños tipográficos, estructura general, paleta de identidad y comportamiento de interacción.

## Combinaciones corregidas y valores medidos

Colores en hexadecimal, contraste expresado como razón `:1`. [Mediciones finales completas](../artifacts/ux-contrast/final/browser/contrast/measurements.json).

| Uso | Antes: texto / fondo | Antes | Después: texto / fondo | Después |
| --- | --- | ---: | --- | ---: |
| Descripción y texto secundario sobre página | `#697973 / #f5f7f6` | 4,26 | `#53665c / #f5f7f6` | **5,70** |
| Eyebrow sobre página | `#718077 / #f5f7f6` | 3,86 | `#56685e / #f5f7f6` | **5,52** |
| Cabeceras de tabla | `#748278 / #fafbf9` | 3,89 | `#52645a / #fafbf9` | **6,08** |
| Pie | `#839084 / #f5f7f6` | 3,10 | `#53665c / #f5f7f6` | **5,70** |
| Instrucciones | `#6a795f / #f7f9f4` | 4,39 | `#526447 / #f7f9f4` | **6,05** |
| Número de sección | `#829771 / #f2f6ed` | 2,90 | `#51683e / #f2f6ed` | **5,64** |
| Campo de solo lectura | `#708167 / #f5f7f3` | 3,88 | `#536849 / #f5f7f3` | **5,66** |
| Fase pendiente, texto | `#8b968c / #ffffff` | 3,07 | `#59685b / #ffffff` | **5,91** |
| Fase pendiente, número | `#8a9485 / #f2f4ef` | 2,85 | `#59664f / #f2f4ef` | **5,52** |
| Número sobre verde claro del formulario | `#4d7535 / #e3efd7` | 4,498 | `#45672f / #e3efd7` | **5,44** |
| Etiqueta de indicador | `#667a5d / #f4f6f1` | 4,28 | `#4e6248 / #f4f6f1` | **6,10** |
| Título secundario de diagnóstico | `#74816d / #ffffff` | 4,11 | `#56664c / #ffffff` | **6,18** |
| Enlace de vuelta | `#64776d / #f5f7f6` | 4,43 | `#52655b / #f5f7f6` | **5,79** |
| Placeholder sobre blanco | `#97a190 / #ffffff` | 2,69 | `#53665c / #ffffff` | **6,14** |
| Borde de campo sobre blanco | `#dce4da / #ffffff` | 1,30 | `#748278 / #ffffff` | **4,03** |

El menor contraste de los bordes de campo muestreados frente a sus dos fondos adyacentes fue **3,74:1**. Los controles de búsqueda usan el mismo borde accesible; los marcadores de obligatorio también se oscurecieron.

Se verificaron además combinaciones conservadas o relacionadas con la semántica:

| Elemento / estado | Primer plano / fondo | Contraste |
| --- | --- | ---: |
| Título grande | `#1c302d / #f5f7f6` | **12,93** |
| Cerrado/Cancelado, neutro nuevo | `#445861 / #edf1f4` | **6,57** |
| Objetivo alcanzado | `#456c35 / #eaf5e5` | **5,42** |
| Objetivo no alcanzado | `#99641f / #fff1e0` | **4,51**; valor sin redondear ≈4,506 |
| No evaluable / sin resultado registrado | `#637068 / #f1f3f2` | **4,65** |
| Botón principal normal | `#ffffff / #146952` | **6,62** |
| Botón principal hover | `#ffffff / #10563f` | **8,66** |
| Botón secundario normal | `#345348 / #ffffff` | **8,48** |
| Anillo de foco principal sobre página | `#277fbc / #f5f7f6` | **4,03** |
| Anillo de foco en navegación oscura | `#277fbc / #142f2e` | **3,29** |

El anillo sigue siendo visible y la tabla mantiene su anillo interior. Los mensajes de error, advertencia, éxito e información, las etiquetas de acciones/indicadores y los campos se incluyeron en las muestras/axe. El verde de “acción completada” expresa ejecución y el de “guardado correcto” expresa éxito de la operación; ninguno se utiliza para deducir el cumplimiento del plan.

## Representación final de estado y resultado

Se reutilizan dos componentes pequeños:

- **`PlanStatus`** muestra “Estado” y el estado administrativo. Cerrado y Cancelado son neutros; los demás estados conservan sus etiquetas.
- **`PlanResult`** muestra “Evaluación actual” para un plan abierto o “Resultado al cierre” para uno finalizado, seguido del resultado explícito suministrado por la API.

| Datos disponibles | Presentación |
| --- | --- |
| `status=closed`, snapshot `result=achieved` | **Estado: Cerrado · Resultado al cierre: Objetivo alcanzado** |
| `status=closed`, snapshot `result=not_achieved` | **Estado: Cerrado · Resultado al cierre: Objetivo no alcanzado** |
| Snapshot `result=not_evaluable` | **Resultado al cierre: No evaluable** |
| Snapshot sin resultado o código desconocido | **Resultado al cierre: Sin resultado registrado** |
| Plan abierto con evaluación en detalle | **Evaluación actual:** el resultado recibido, sin inferir cierre ni cumplimiento. |

La separación aparece en la tabla compartida de planes —incluido dashboard—, el historial del vendedor, la cabecera del detalle, el panel de cierre y el contexto lateral. La cabecera permite ver el resultado también en móvil antes de recorrer las tablas. El diálogo de finalización identifica la evaluación actual y explica que cerrar no implica alcanzar objetivos. Los paneles vacíos de planes finalizados describen registros ausentes y no invitan a editar/activar.

El resultado final se lee **exclusivamente de `closure_evaluation`**. Si falta, no se reconstruye desde métricas, acciones, estados, valoraciones del agente ni una evaluación actual diferente. “No evaluable” y “sin resultado registrado” son situaciones distintas. No se inventa una categoría de “pendiente” que el contrato no suministra.

**Límite de la API existente:** el resumen de planes abiertos no incluye `evaluation`; por ello el listado no inventa su resultado actual ni realiza peticiones adicionales por fila. El detalle sí presenta la evaluación que recibe. No se añadieron campos ni endpoints.

La comparación por indicador conserva sus datos y significado. Los cálculos, reglas de cierre, instantáneas, permisos y persistencia no se modifican.

## Archivos modificados

| Archivo | Cambio |
| --- | --- |
| `frontend/src/styles.css` | Contrastes de texto/controles, estado final neutro, panel de cierre neutro, agrupación de etiquetas y altura mínima de enlaces afectados. |
| `frontend/src/components/ui.jsx` | Componentes `PlanStatus` y `PlanResult`; sin cambios en guard, foco o envío. |
| `frontend/src/services/planPresentation.js` (nuevo) | Selección pura del resultado y su fuente; fallback explícito sin inferencias. |
| `frontend/src/pages/Workspace.jsx` | Estado y resultado en listados/historial, icono y texto administrativo del contador de cierres. |
| `frontend/src/pages/PlanDetail.jsx` | Estado/resultado en cabecera, cierre y lateral; aclaración al finalizar y textos vacíos coherentes. |
| `frontend/src/services/planPresentation.test.js` (nuevo) | Ocho tests significativos sobre resultado, snapshots ausentes/desconocidos, cancelación y ausencia de mutación. |
| `frontend/package.json` | Incorpora esos tests a `npm test`; sin dependencias nuevas. |
| `scripts/measure_contrast.js` (nuevo) | Medición de colores computados, composición y relaciones de contraste. |
| `scripts/verify_contrast.py` (nuevo) | Casos reales, fixtures ficticias, axe, mediciones, capturas y ejecución conjunta de las regresiones. |
| Este informe | Evidencias, valores, resultados y límites. |

No se modifican backend, modelos, migraciones, contratos API, rutas, autenticación/CSRF, revisión, idempotencia, guard de cambios, evaluación ni cierre. No se realizan commits, push o despliegues.

## Pruebas ejecutadas

Con Node 22 en PATH, dependencias locales de QA y axe disponible en el directorio temporal ya utilizado:

```sh
npm test
npm run build
python3 scripts/verify_contrast.py --artifacts artifacts/ux-contrast/final
```

El verificador crea un clúster PostgreSQL temporal, TLS local, usuarios y datos ficticios. Además de los dos cierres de la demo, se crea una cancelación válida no evaluable mediante el servicio de cierre y una fixture histórica separada sin resultado, simulada solo en la base temporal. No se altera información real ni la lógica del modelo. Se conservan los mismos datos de cierre después de visitar las pantallas; las pruebas unitarias también comprueban que presentar no modifica el plan.

| Comprobación final | Resultado | Evidencia |
| --- | --- | --- |
| JavaScript | **26/26**, incluidos ocho nuevos | [Log](../artifacts/ux-contrast/js-tests.log) |
| Build Vite | **Correcto**, 37 módulos | [Log](../artifacts/ux-contrast/build.log) |
| Contraste/semántica | **58 estados y variantes**, mediciones dentro de los umbrales aplicados; casos cumplido, incumplido, no evaluable y ausente | [Resultado](../artifacts/ux-contrast/final/browser/contrast/result.json), [mediciones](../artifacts/ux-contrast/final/browser/contrast/measurements.json) |
| axe-core | **54 análisis, cero infracciones**, con etiquetas WCAG 2.0/2.1 A/AA y 2.2 AA; sin reglas desactivadas | [Resultado completo](../artifacts/ux-contrast/final/browser/contrast/axe.json) |
| Teclado/foco | **12 grupos superados**, más sus diez análisis axe sin infracciones | [Resultado](../artifacts/ux-contrast/final/browser/keyboard/result.json), [axe](../artifacts/ux-contrast/final/browser/keyboard/axe.json) |
| Navegación segura | **20/20 grupos** | [Resultado](../artifacts/ux-contrast/final/browser/navigation/result.json) |
| Responsive | **128 estados**, sin desbordamiento accidental en los recorridos medidos | [Resultado](../artifacts/ux-contrast/final/browser/responsive/result.json) |
| Django/PostgreSQL | **116/116**, sin omisiones | [Log](../artifacts/ux-contrast/final/postgres-tests.log) |
| Full Stack | **Correcto**: crear, editar, acciones, revisar, evaluar, cerrar, recargar, CSRF, cartera ajena, logout y recuperación H02 | [Resultado](../artifacts/ux-contrast/final/browser/browser-result.json) |
| Persistencia | **Correcta** tras reiniciar PostgreSQL/Gunicorn y backup/restauración en otra base temporal | [Resultado integrado](../artifacts/ux-contrast/final/result.json) |
| Diferencias | `git diff --check`: **correcto** | Revisión local |

No se suman estados de navegador, apariciones de axe o ejecuciones repetidas como si fueran tests unitarios independientes. Se interrumpió una ejecución intermedia para incorporar el ajuste de enlaces y se repitió la validación; esa ejecución incompleta no se presenta como superada.

## Revisión visual, herramientas y regresiones

Herramientas efectivamente utilizadas: **Chromium 151.0.7922.34 headless**, Playwright, **axe-core 4.14.0**, medición propia de luminancia sobre estilos computados, Node 22 y PostgreSQL local 14.24. La herramienta axe permanece fuera de las dependencias del producto.

La revisión visual se hizo sobre capturas de la aplicación real con datos ficticios. Se contrastaron los dos planes cerrados, la lectura de etiquetas sin depender de sus colores, la visibilidad del resultado en móvil, los estados desconocidos y los mensajes vacíos. No fue un estudio de comprensión con usuarios finales.

El recorrido específico de contraste cubre **1440 × 900, 768 × 1024 y 375 × 812**, incluyendo hover, foco, instrucciones, diálogos, aviso de cambios, validación real y un error 503 deliberado con recuperación. La regresión responsive repite **320 × 568, 375 × 812, 430 × 932, 768 × 1024, 1024 × 768 y 1440 × 900**, además de reflow 720 × 450 y 360 × 225.

Se conservan Volver al plan/ID, cambios pendientes/continuar/descartar, campos tras errores 400/503, guardado/idempotencia, Atrás/Adelante, aviso nativo al rechazar recarga, X/Escape, foco dentro del diálogo incluso ocupado, restauración del foco, menú compacto, tablas con scroll local y sus acciones. No se detectan regresiones funcionales pendientes en las suites y recorridos ejecutados.

## Capturas disponibles

- Plan cerrado incumplido: [antes](../artifacts/ux-contrast/before/contrast/not-achieved-1440.png) / [después](../artifacts/ux-contrast/final/browser/contrast/not-achieved-1440.png).
- Listado: [antes](../artifacts/ux-contrast/before/contrast/plans-1440.png) / [después](../artifacts/ux-contrast/final/browser/contrast/plans-1440.png).
- [Cerrado cumplido](../artifacts/ux-contrast/final/browser/contrast/achieved-1440.png), [cerrado incumplido en móvil](../artifacts/ux-contrast/final/browser/contrast/not-achieved-375.png).
- [Cancelado no evaluable](../artifacts/ux-contrast/final/browser/contrast/not-evaluable-768.png), [histórico sin resultado](../artifacts/ux-contrast/final/browser/contrast/legacy-1440.png).
- [Validación](../artifacts/ux-contrast/final/browser/contrast/validation-375.png), [aviso de cambios](../artifacts/ux-contrast/final/browser/contrast/warning-375.png), [foco en navegación oscura](../artifacts/ux-contrast/final/browser/contrast/navigation-focus.png).

Los artefactos están ignorados por Git y disponibles localmente. Las capturas corresponden al viewport, no se presentan como pantallas completas de página. Las cuentas de QA de la reproducción previa y de la ejecución final son distintas.

## Límites y riesgos pendientes

No se declara conformidad WCAG completa. Los análisis automáticos y las muestras de colores no cubren cada combinación de contenido, permiso, dispositivo o tecnología de asistencia. Las entradas `incomplete` de axe se conservan en el JSON para revisión; cero infracciones detectadas no equivale a ausencia universal de barreras.

No se han validado Firefox, Safari, dispositivos físicos, lectores de pantalla, zoom nativo con interfaz ni todas las preferencias de presentación del sistema. El reflow emulado no sustituye el zoom nativo, que no cambió el viewport en el entorno headless. Los controles nativos pueden variar según navegador/sistema; los elementos decorativos y estados deshabilitados no se presentan como controles activos evaluados.

Se preservan tipografía y tamaños actuales: esta fase no es un rediseño ni una unificación completa del sistema visual. Los resultados antiguos sin dato continúan sin dato y así se muestran; la API de resumen de abiertos mantiene la limitación indicada. No se ha probado producción, otro servidor PostgreSQL ni la disponibilidad pública, y no se regeneran los entregables académicos.

## Veredicto

**LISTO PARA LA SIGUIENTE FASE.** En el alcance probado mejora el contraste, el cierre administrativo se distingue del cumplimiento y los datos ausentes no se reconstruyen. Los dos cierres exigidos se verificaron con datos ficticios reales y las regresiones anteriores pasan. El veredicto no certifica conformidad global WCAG ni despliegue público.
