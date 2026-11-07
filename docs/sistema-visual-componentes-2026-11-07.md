# Sistema visual y componentes compartidos

Fecha: 07/11/2026. Base: `2cd676a`, árbol limpio al empezar. Trabajo local sin commits, pushes ni despliegues.

## Inventario previo a modificar el producto

Se revisaron los cuatro informes de navegación segura, responsive, foco/teclado y contraste indicados en la solicitud. También la auditoría disponible en `/tmp/sap-ux-audit-20261107/AUDITORIA-UX-UI-SAP.md`, especialmente UX14, UX18, UX28 y UX30 y las referencias E05, E11–E14 y E17–E18. Sus pruebas históricas no se presentan como resultados de esta fase.

Se inspeccionaron `styles.css` completo, `components/ui.jsx`, `UnsavedChanges.jsx`, `main.jsx`, `Workspace.jsx`, `PlanForm.jsx`, `PlanDetail.jsx`, la selección de resultados y los verificadores anteriores. No hay AGENTS.md aplicable en el repositorio ni sus directorios superiores.

| Inconsistencia comprobada en código | Criterio de corrección |
| --- | --- |
| Botón «Rectificar revisión» sin clase, frente a las demás acciones secundarias compactas. | Reutilizar `.button.secondary.compact` y mantener exactamente permisos, texto y callback. |
| Tabla comparativa con texto base de 12 px, override de 11 px en `.plan-content` hasta 1250 px y de 10 px en `.modal`; metadatos de 9 px en tablet. | Tipografía operativa compartida y densidad compacta explícita por contexto, sin eliminar columnas ni scroll local. |
| Tablas, toolbars y paneles usan 18/21/22/23/25/28 px sin una escala compartida. | Escala pequeña de espaciado; un único margen interior de superficie, adaptable a móvil. Conservar estructuras especiales como timeline y grids. |
| `.panel`, `.stat`, `.stepper`, formularios y diálogos repiten radios/bordes ligeramente distintos. | Tokens de superficie/control; conservar la distinción de la tarjeta destacada, cierre neutro y diálogo modal. |
| Ayudas, etiquetas, badges, paginación y botones de la misma función oscilan entre 9–12 px; el picker reduce además su paginación a 28 px. | Texto operativo de 13 px, apoyo de 12 px; botones regulares/compactos con mínimos propios y coherentes. No aumentar indiscriminadamente logotipo ni números destacados. |
| `.error-state` y `.form-error` comunican errores con distintos tonos, rellenos y radios; éxito e información duplican la estructura visual. | Base CSS compartida de mensajes con variantes semánticas explícitas; conservar alert/status, foco y acciones. La confirmación conserva checkbox y texto de consecuencias. |
| Anillo de foco repetido en dos grupos; colores principales/secundarios de controles escritos de forma literal. | Consolidar tokens sin cambiar los contrastes validados ni el anillo interior de tabla. |
| Tamaño H1 de 25 px en tablet sube a 27 px en móvil; títulos de panel secundarios cambian con reglas particulares. | Jerarquía tipográfica compartida, conservando títulos compactos de panel lateral y título de diálogo diferenciados. |

Los componentes existentes `ScrollableTable`, `Field`, `FormActions`, `Modal`, `Empty`, `Loading`, `ErrorState`, `Badge`, `PlanStatus` y `PlanResult` ya resuelven responsabilidades concretas: se reutilizan. No se crea una biblioteca paralela ni una abstracción Button que sustituya enlaces y botones nativos. Búsquedas, filtros, selección de registros, acciones, estados administrativos y resultados conservan sus comportamientos y semánticas diferentes.

## Base visual y decisiones

Se mantiene DM Sans con sus alternativas del sistema, verde principal, fondo de página, navegación oscura, tarjeta lima y colores de las etiquetas previamente validados. No se cambia la arquitectura ni se añade ninguna dependencia.

| Base compartida | Aplicación y motivo |
| --- | --- |
| Espaciado 4, 8, 12, 16, 20, 24, 32 y 40 px | Tokens `--space-*`; se aplican gradualmente a componentes comunes. No se sustituyen medidas propias de iconos, timeline, columnas o límites del viewport por una retícula rígida. |
| Interior de superficie de 24 px; 16 px hasta 760 px | `--surface-padding` alinea cabeceras, tablas, toolbars, listas y formularios. Se conservan las reglas de reflow y el menú compacto hasta 900 px. |
| Texto de controles/contenido operativo de 13 px y apoyo de 12 px | Aumenta lectura en tablas, formularios, badges y metadatos. Se retiran overrides que reducían la lectura según pantalla o contenedor. Se conserva cuerpo de 14 px, H2 de 17 px y título de diálogo de 20/18 px. H1 móvil hereda 25 px de tablet, evitando el salto inverso de 25 a 27. |
| Pesos 550 para acciones y 650 para títulos | Variables sobre los pesos ya utilizados; no cambia la fuente ni se impone otra jerarquía de marca. |
| Radios de control 6 px, superficie 10 px y diálogo 12 px | Paneles, estadísticas y banda de fases comparten radio; el diálogo sigue siendo una superficie modal diferenciada. Avatares, iconos y puntos conservan su geometría. |
| Botones regulares de al menos 40 px, compactos de al menos 36 px | Las dos densidades conservan funciones distintas. Se elimina la reducción de la paginación del picker a 28 px. Campos de `Field` y filtros tienen mínimo de 40 px; textarea conserva altura por filas. Los botones de icono existentes conservan su variante de 32 px. |
| Tabla regular y tabla compacta explícita | `ScrollableTable` admite `compact=false`. La comparación de finalización pasa `compact`: reduce relleno de 16 a 12 px y mantiene cuerpo de 13 px/cabeceras de 12 px. La comparación del detalle usa la variante regular. No depende de selectores globales de diálogo o de un ancho de pantalla para disminuir el texto. |
| Mensajes compartidos | `.form-error`, `.error-state`, `.success-notice`, `.info-note` y `.confirmation` comparten caja, radio, ritmo y tokens por significado. Los errores de campo mantienen texto rojo, estado inválido y asociación accesible; un error de recurso sigue ofreciendo reintento. Alertas, estados de éxito y confirmación nativa no se intercambian. |
| Anillo de foco con token único | Se conserva color, grosor y offsets validados, incluido el anillo interior de las tablas. |

Se reutilizan `Field`, `FormActions`, `Modal`, `Empty`, `Loading`, `Badge`, `PlanStatus` y `PlanResult`; se ajusta su presentación común mediante CSS. No se crean componentes React para envolver únicamente una clase. El único cambio de interfaz de componente es la variante opcional `compact` de `ScrollableTable`.

«Rectificar revisión» utiliza ahora el botón secundario compacto, con `type="button"`, manteniendo las mismas condiciones de permiso y el mismo callback. La distinción `PlanStatus`/`PlanResult`, la fuente histórica `closure_evaluation` y todos los textos de resultado se conservan. Cierre/Cancelación siguen neutros; verde de éxito de guardado y verde de objetivo alcanzado conservan significados distintos y texto explícito.

## Archivos modificados

| Archivo | Cambio |
| --- | --- |
| `frontend/src/styles.css` | Tokens, tipografía, espaciado, superficies, controles y caja común de mensajes; eliminación de overrides de tablas y botones del picker y reglas responsive redundantes. |
| `frontend/src/components/ui.jsx` | Variante opcional `compact` de `ScrollableTable`, conservando observación del overflow, nombre, instrucciones, semántica y foco. |
| `frontend/src/pages/PlanDetail.jsx` | Variante compacta en la comparación del diálogo y estilo del botón de rectificación. |
| `scripts/verify_visual_system.py` (nuevo) | Aserciones de legibilidad, densidad, superficies, overflow y recuperación; capturas/estilos computados de componentes reales; integra las regresiones anteriores en PostgreSQL temporal. |
| Este informe (nuevo) | Inventario previo, decisiones, evidencias, resultados y límites. |

No se modifican backend, modelos, migraciones, reglas de negocio, contratos, rutas, hooks de navegación/guardado ni dependencias. Autenticación/CSRF, revisiones, idempotencia, permisos, aislamiento, persistencia, evaluación y cierre se preservan.

## Método de comprobación y contraste

Antes de editar el producto se compiló la base y se capturaron 33 estados con Chromium sobre SQLite temporal nueva, cuentas ficticias y la demo oficial. Un runner local en `/tmp/sap-visual-baseline.py` crea y elimina servidor/base temporales; no reutiliza la conexión configurada. Las capturas previas están en `artifacts/visual-system/before/components/`.

La validación final usa el nuevo verificador sobre PostgreSQL temporal/TLS local. Las fixtures añaden históricos sin resultado/no evaluables y 55 vendedores ficticios para la paginación. Por ello los contadores y algunas filas difieren del antes: las capturas son representativas, no una comparación pixel a pixel de datos idénticos. Los cierres usan el servicio real; la ausencia histórica de resultado se simula exclusivamente en QA. La carga retenida y los errores 503 se provocan solo en el navegador de QA.

Las combinaciones que cambian se revisaron en el CSS y capturas y se recalcularon mediante luminancia relativa sRGB; además el recorrido de contraste mide estilos computados y fondos compuestos del navegador. Los umbrales se comparan sin redondear: 4,5:1 para texto normal y 3:1 para información gráfica necesaria. Los bordes decorativos de superficies no se equiparan al borde necesario de un campo.

| Combinación revisada | Color / fondo | Ratio |
| --- | --- | ---: |
| Error de recurso unificado con error de formulario | `#99432c / #fff1eb` | 5,96:1 |
| Información y confirmación | `#526447 / #f7f9f4` | 6,05:1 |
| Éxito de guardado | `#4b6b3f / #ebf5e6` | 5,39:1 |
| Apoyo sobre blanco | `#53665c / #ffffff` | 6,14:1 |
| Cabecera de tabla | `#52645a / #fafbf9` | 6,08:1 |
| Foco sobre información | `#277fbc / #f7f9f4` | 4,09:1 |

Se conservan los colores de borde de campos, foco, placeholders y badges de la fase anterior. La mayor tipografía no se utiliza para justificar bajar umbrales de contraste. No se ha desactivado ninguna regla de axe.

La revisión de capturas de la primera candidata detectó que el aumento tipográfico dejaba alguna celda de responsable demasiado estrecha y partía la última letra de un nombre corto. Se añade un mínimo de `10rem` exclusivamente a `td .person`: no afecta al sidebar ni a agrupaciones fuera de tabla. Se conserva el ajuste de textos largos y el scroll local. La validación final se repite sobre esta corrección; la candidata previa no sustituye los resultados finales.

La revisión posterior del error de recurso también mostró que el botón de reintento heredaba presentación en línea y compartía la última línea de la frase en móvil. Se presenta debajo del mensaje, con separación común, y una aserción geométrica comprueba esa relación. No cambia la petición ni el comportamiento del reintento.

## Pruebas reproducibles

Desde la raíz, con Node 22 en PATH, dependencias locales de QA y axe-core disponible en `/tmp/sap-accessibility-tools/node_modules/axe-core/axe.min.js` (o `SAP_AXE_PATH`):

```sh
npm test
npm run build
python3 scripts/verify_visual_system.py --artifacts artifacts/visual-system/final
git diff --check
```

El verificador ejecuta la suite Django, las comprobaciones de esquema, Chromium y los recorridos previos; crea su propio clúster PostgreSQL y servidor TLS y elimina los recursos al finalizar. Sustituye explícitamente la conexión del usuario. `release-repeat` comprueba únicamente el script local de migraciones/estáticos en QA: no publica ni despliega. La herramienta axe es de QA, no una dependencia nueva del producto.

Las aserciones nuevas comprueban texto de apoyo legible, mínimos de acciones, superficies coherentes, overflow del documento, la densidad explícita del diálogo, recuperación de un error y que un identificador corto junto a su avatar no se parta en varias líneas. No sustituyen la revisión visual ni se contabilizan como tests Django. Los análisis axe añadidos cubren rectificación, búsqueda vacía, carga y error en los tres tamaños principales.

La regresión integrada se ejecutó con PostgreSQL y terminó correctamente en `artifacts/visual-system/final/`. Después del último ajuste exclusivamente CSS del botón de reintento se recompiló y se repitieron los recorridos de componentes y contraste sobre SQLite temporal nueva, mediante `python3 /tmp/sap-visual-baseline.py after`; sus evidencias están en `artifacts/visual-system/final-visual/`. La suite Django, el recorrido Full Stack/PostgreSQL y las regresiones generales no se ejecutaron otra vez después de esa última declaración CSS; sus resultados corresponden a la ejecución integrada indicada. No cambió código JavaScript ni backend entre ambas.

## Resultados ejecutados

| Comprobación | Resultado | Evidencia |
| --- | --- | --- |
| JavaScript con Node 22 | **26/26**, cero fallos | [Log](../artifacts/visual-system/js-tests.log) |
| Compilación Vite final | **Correcta**, 37 módulos | [Log](../artifacts/visual-system/build.log) |
| Componentes, revisión final | **33 estados**, cero errores de página; tres tamaños principales | [Resultado](../artifacts/visual-system/final-visual/components/result.json), [estilos computados](../artifacts/visual-system/final-visual/components/measurements.json) |
| Contraste/semántica, revisión final | **58 estados/variantes**, todas las muestras cumplen los umbrales aplicados, snapshot conservado | [Resultado](../artifacts/visual-system/final-visual/contrast/result.json), [mediciones](../artifacts/visual-system/final-visual/contrast/measurements.json) |
| axe-core 4.14.0, revisión final | **12 análisis de componentes + 54 de contraste**, cero infracciones detectadas, sin reglas desactivadas | [Componentes](../artifacts/visual-system/final-visual/components/axe.json), [contraste](../artifacts/visual-system/final-visual/contrast/axe.json) |
| Teclado/foco, ejecución integrada | **12 grupos**, cero errores de página; sus **10 análisis axe** sin infracciones | [Resultado](../artifacts/visual-system/final/browser/keyboard/result.json), [axe](../artifacts/visual-system/final/browser/keyboard/axe.json) |
| Navegación segura, ejecución integrada | **20/20 grupos**, incluido `beforeunload` nativo real | [Resultado](../artifacts/visual-system/final/browser/navigation/result.json) |
| Responsive, ejecución integrada | **128 estados**, seis tamaños y reflow; cero errores de página | [Resultado](../artifacts/visual-system/final/browser/responsive/result.json), [mediciones](../artifacts/visual-system/final/browser/responsive/measurements.json) |
| Django/PostgreSQL temporal | **116/116**, sin omisiones, PostgreSQL 14.24 | [Log](../artifacts/visual-system/final/postgres-tests.log) |
| Esquema/configuración | Migraciones nuevas y pendientes, ausencia de deriva, configuración de producción: **correctas** | [Resultado integrado y logs asociados](../artifacts/visual-system/final/result.json) |
| Full Stack y seguridad | **Correctos**: creación a cierre, recarga, CSRF, aislamiento, logout y recuperación de errores | [Resultado](../artifacts/visual-system/final/browser/browser-result.json) |
| Persistencia/recuperación | **Correcta** tras reinicios de PostgreSQL/Gunicorn, repetición local del script y backup/restauración independiente | [Resultado integrado](../artifacts/visual-system/final/result.json) |
| Higiene de diferencias | `git diff --check`: **correcto** | Revisión local final |

Los estados de navegador, grupos de aserciones, análisis axe y tests unitarios son medidas distintas; no se suman ni se multiplican por las ejecuciones repetidas. La primera candidata completa se conserva en `artifacts/visual-system/candidate-1/`; no se cuenta como prueba adicional de la versión final.

En las mediciones finales el menor contraste de texto normal muestreado fue **4,50559:1** y el menor contraste de límite de campo frente a sus fondos fue **3,74141:1**. La primera combinación corresponde al badge de objetivo no alcanzado ya existente, cuya paleta se conserva. El margen reducido de ese badge aconseja volver a medir si cambia su color o fondo.

## Resultados de regresión y revisión visual

En la ejecución integrada se conserva:

- **Navegación segura:** Volver al plan/ID, cancelación limpia, continuar/descartar, cambios revertidos, errores 400/503 con valores retenidos, Atrás/Adelante, recarga rechazada con aviso nativo, Cancelar/X/Escape y logout con CSRF. Se conserva un único envío y la clave de reintento.
- **Teclado:** foco de ruta/paginación/prioridades, etiquetas de pickers, ayudas y errores asociados, Tab/Shift+Tab contenidos en diálogos normales/anidados y durante guardado, foco restaurado o destino alternativo, salto al contenido y menú compacto con Espacio/Escape.
- **Responsive:** 320 × 568, 375 × 812, 430 × 932, 768 × 1024, 1024 × 768 y 1440 × 900; contenidos largos y reflow de 720 × 450 y 360 × 225. Sin ensanchamiento accidental del documento en los estados medidos. Se accede a tablas mediante flechas y desplazamiento local y se abren sus acciones finales. El zoom nativo headless no cambió el viewport, por lo que no se declara probado.
- **Estado/resultado:** cierres alcanzado/incumplido, cancelación no evaluable y snapshot sin resultado; lectura explícita y neutra del estado administrativo, sin reconstruir datos históricos. La instantánea de cierre permanece igual tras consultar las pantallas.
- **Full Stack:** login, consultas, creación, validación real, edición, acción, activación, revisiones 6 → 4,5 → 3, evaluación, cierre alcanzado y recarga; cartera ajena rechazada, CSRF, logout y recuperación ante JSON/HTML inválidos. Persistencia tras reinicios y restauración en otra base temporal.

La revisión visual inspeccionó capturas de escritorio, tablet y móvil, incluyendo tablas/listado, tarjetas de dashboard, edición con errores, rectificación, finalización, foco de tabla, estado vacío y error recuperable. El botón de reintento final queda debajo de su mensaje y los identificadores cortos de responsable permanecen en una línea. Se mantienen visibles las instrucciones de desplazamiento y los resultados textuales. No es una prueba de comprensión con usuarios finales ni una sesión de teclado físico: las teclas se envían con Playwright a Chromium real.

## Capturas y evidencias

- Listado: [antes](../artifacts/visual-system/before/components/plans-1440.png) / [después](../artifacts/visual-system/final-visual/components/plans-1440.png).
- Dashboard: [antes](../artifacts/visual-system/before/components/dashboard-1440.png) / [después](../artifacts/visual-system/final-visual/components/dashboard-1440.png).
- Detalle y botón de rectificación: [antes](../artifacts/visual-system/before/components/detail-1440.png) / [después](../artifacts/visual-system/final-visual/components/detail-1440.png).
- Error recuperable móvil: [antes](../artifacts/visual-system/before/components/error-375.png) / [después](../artifacts/visual-system/final-visual/components/error-375.png).
- [Rectificación móvil](../artifacts/visual-system/final-visual/components/rectification-375.png), [finalización móvil](../artifacts/visual-system/final-visual/components/close-375.png), [edición tablet](../artifacts/visual-system/final-visual/components/edit-768.png), [búsqueda vacía tablet](../artifacts/visual-system/final-visual/components/empty-768.png).
- [Foco de tabla móvil](../artifacts/visual-system/final/browser/keyboard/mobile-table-focus.png), [error de validación tablet](../artifacts/visual-system/final-visual/contrast/validation-768.png), [aviso de cambios móvil](../artifacts/visual-system/final-visual/contrast/warning-375.png).

Las capturas `components/` finales son de página completa salvo los diálogos, que muestran el viewport para evitar una composición engañosa del backdrop al capturar una página larga. Las capturas `contrast/` y de teclado corresponden al viewport. Las capturas previas se tomaron a página completa; no se presentan como comparaciones exactas de píxeles ni de contenido idéntico. Los JSON de mediciones y axe acompañan a las imágenes.

## Límites y riesgos pendientes

No se declara conformidad WCAG completa. Se conserva la salida `incomplete` de axe; las mediciones y revisión visual complementan el análisis automático sin convertirlo en una certificación. Se revisan muestras y recorridos concretos, no cada combinación posible de datos, permisos o tecnología de asistencia.

Chromium headless y viewports emulados no sustituyen Firefox, Safari, dispositivos físicos, teclado virtual, lectores de pantalla ni zoom nativo con interfaz. Esas comprobaciones no se han ejecutado. El reflow equivalente a 200/400 % se registra por separado del zoom nativo. Se mantienen las limitaciones de `beforeunload` del navegador y la ausencia de persistencia de borradores.

El texto de apoyo crece y algunas filas/diálogos ocupan más altura. Se mantiene scroll local y se verifica acceso a columnas y acciones finales. El pulido de cada pantalla, la priorización del dashboard, filtros persistentes, traducción de nombres técnicos de errores y simplificación de selectores quedan para fases posteriores. No se introducen barras adhesivas de diálogo ni se modifican reglas o valores iniciales de formularios.

La tipografía de marca/navegación conserva algunas medidas pequeñas existentes: no se ha ampliado indiscriminadamente el sistema entero. La carga externa de DM Sans y su fallback siguen como estaban; no se ha autoalojado la fuente ni cambiado su proveedor.

Los artefactos están ignorados por Git y disponibles localmente; `/tmp` y los informes de auditoría originales no son almacenamiento permanente. La validación usa PostgreSQL local 14.24 y no certifica otra versión, producción o disponibilidad pública. No se regeneran entregables académicos ni se realiza publicación alguna.

Las entradas `incomplete` de contraste incluyen `color-contrast` y `th-has-data-cells`; se conservan para revisión contextual, sin marcarlas automáticamente como resueltas. En los doce análisis nuevos de componentes no quedaron entradas `incomplete`. Cero infracciones detectadas no equivale a ausencia universal de barreras.

## Veredicto

**LISTO PARA LA SIGUIENTE FASE**, dentro del alcance local probado. Los patrones compartidos tienen una base visual coherente, la tabla compacta mantiene la lectura y las acciones de rectificación/reintento se integran en sus jerarquías. No quedan fallos bloqueantes detectados de esta intervención. Se conservan la identidad, los datos y las mejoras anteriores en los recorridos indicados. El veredicto no certifica conformidad WCAG completa ni validación en producción u otros navegadores.
