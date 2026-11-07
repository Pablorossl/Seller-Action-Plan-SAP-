# Fase UX 2 — responsive y desbordamientos

Fecha: 07/11/2026. Base inspeccionada: `00b31a9`, con la fase 1 incorporada y árbol limpio al inicio. Cambios locales; sin commits, push ni despliegues.

## Referencias e inspección previa

Se revisó el [informe de fase 1](ux-fase-1-navegacion-segura-2026-11-07.md) antes de cambiar código. También está disponible la [auditoría UX/UI del 7 de noviembre](/tmp/sap-ux-audit-20261107/AUDITORIA-UX-UI-SAP.md), con sus capturas E03/E05–E08/E12–E14/E23 y registros en `evidence/`. Se consultaron sus hallazgos de desbordamiento, contención de `.sr-only`, tablas y navegación tablet. Sus cifras históricas no sustituyen las mediciones actuales.

Se inspeccionaron `styles.css`, componentes compartidos, `main.jsx`, `Workspace.jsx`, `PlanForm.jsx` y `PlanDetail.jsx`. Antes de modificar el producto se recorrieron dashboard, vendedores, ficha, planes, creación, detalle, edición, indicadores, acciones, revisiones, rectificación, finalización, cierre histórico, aviso de cambios pendientes y menú. La base de pruebas se creó aparte, con agentes y datos ficticios, sin utilizar la conexión real del proyecto.

## Problemas reproducidos y causas

| Problema | Causa comprobada / corrección |
| --- | --- |
| Desplazamiento horizontal de todo el documento en dashboard, vendedores, ficha y planes | Los encabezados accesibles `.sr-only` estaban posicionados absolutamente sin un contenedor de posicionamiento local. Aunque la tabla tenía `overflow-x:auto`, el posicionamiento escapaba a su contención. `.table-wrap` ahora establece `position:relative`. Se conservan los encabezados accesibles. |
| Columnas y acciones fuera del primer encuadre sin indicación clara | Las tablas complejas necesitan más ancho que el móvil. Se conserva el scroll local y se añade una indicación visible y asociada a la región solo cuando hay desbordamiento. Se verifica acceso real a la columna final. |
| Tarjetas y textos demasiado comprimidos en móvil | Tres tarjetas de estadísticas por fila y dos columnas en el bloque secundario dejaban poco espacio; algunos contenedores flex/grid conservaban mínimos intrínsecos. Se usan dos estadísticas por fila y una columna secundaria en móvil, con mínimos de contenido ajustados. No se cambia el orden ni se eliminan datos. |
| Paginación, acciones y textos largos susceptibles de recorte | Grupos flex sin salto de línea y botones con `white-space:nowrap`; mínimos de hijos y palabras/URLs largas. Se permite envolver las acciones, paginación y textos en sus contenedores. Los botones de Buscar mantienen su ancho legible. |
| Tablet vertical desaprovechada | A 768 px la barra fija de 200 px dejaba solo 568 px para el contenido. La navegación compacta pasa a activarse hasta 900 px; en 1024/1440 px sigue visible la barra lateral. |
| Opciones inferiores del menú difíciles de alcanzar en ventanas bajas | La barra fija no tenía desplazamiento vertical propio. Ahora permite recorrer todas las opciones, incluido Cerrar sesión, sin depender de la altura de la página. |
| Menú superpuesto sin una salida contextual clara | Se añade fondo de cierre, Escape, foco inicial en navegación y devolución del foco al botón. El contenido de fondo queda inerte mientras está abierto; no se modifica el router ni la protección de cambios pendientes. |
| Diálogos largos y contenido variable | Se explicitan scroll vertical interno, límite de altura con `dvh` y alternativa `vh`, ajuste de textos y acciones. Las tablas del cierre conservan su desplazamiento local. |

Medición del documento con el contenido cargado, en píxeles CSS. Los valores de “antes” proceden de la nueva reproducción, no de la auditoría histórica:

| Viewport | Máximo ancho del documento antes | Máximo después, incluidos textos largos |
| --- | ---: | ---: |
| 320 × 568 | 754 | **320** |
| 375 × 812 | 754 | **375** |
| 430 × 932 | 754 | **430** |
| 768 × 1024 | 961 | **768** |
| 1024 × 768 | 1024 | **1024** |
| 1440 × 900 | 1440 | **1440** |

En 320/375/430 px el directorio llegaba a 726 px y la ficha a 541 px; a 768 px el directorio llegaba a 933 px. No se ha usado `overflow-x:hidden` en el documento para esconder el defecto. Las tablas siguen pudiendo ser más anchas que su región, de forma intencionada y utilizable.

## Decisiones de implementación

**Tablas.** El componente reutilizable `ScrollableTable` conserva todas las columnas, enlaces, datos, semántica de tabla y foco por teclado. Usa nombres de región específicos, una indicación de desplazamiento y `aria-describedby` cuando es necesario. `ResizeObserver` comprueba el ancho del contenedor y de la tabla. La región limita su propio scroll horizontal y evita propagarlo a la página. En el navegador se probaron flechas, rueda horizontal y apertura de los enlaces de la última columna. No se sustituyen las tablas por tarjetas ni se ocultan columnas.

**Formularios y diálogos.** Se mantienen los campos, sus validaciones y los flujos de guardado. Los grupos de botones pueden pasar a otra línea; los diálogos caben en el viewport y permiten llegar a Cancelar mediante scroll interno. Las URLs y palabras largas se parten visualmente sin alterar los datos. No se modifican los valores iniciales ni la comparación de cambios de fase 1.

**Navegación.** El breakpoint de 900 px libera ancho en tablet vertical. La cabecera compacta permanece accesible al desplazar la página. El menú tiene scroll propio, fondo de cierre y Escape; al cerrarlo vuelve el foco al control de apertura. Al regresar a escritorio se desactiva el estado compacto abierto. Los diálogos nativos tienen prioridad: Escape en un aviso no cierra el menú que está detrás. El guard de fase 1 continúa decidiendo si una navegación con cambios puede realizarse.

La composición de escritorio, colores, tipografías, contenidos, orden de las pantallas y reglas de negocio se conservan. No se realiza una unificación visual general.

## Archivos modificados

| Archivo | Cambio |
| --- | --- |
| `frontend/src/styles.css` | Contención local de tablas, mínimos flex/grid, wrapping de textos/acciones/paginación, columnas móviles, navegación compacta y altura/scroll de diálogos. |
| `frontend/src/components/ui.jsx` | Nuevo contenedor `ScrollableTable` con indicación condicional accesible. |
| `frontend/src/pages/Workspace.jsx` | Usa el contenedor en planes, desviaciones, vendedores e indicadores de la ficha. |
| `frontend/src/pages/PlanDetail.jsx` | Usa el contenedor en la comparación/evaluación, incluida la finalización. No cambia los formularios ni el guard de fase 1. |
| `frontend/src/main.jsx` | Manejo de apertura/cierre/foco del menú compacto, fondo e inercia del contenido. Rutas y navegación protegida conservadas. |
| `scripts/verify_responsive.py` (nuevo) | Mediciones, capturas, interacción real, valores largos, validación, reflow y ejecución conjunta de fase 1/Full Stack sobre PostgreSQL temporal. |
| Este informe | Evidencias, decisiones, resultados y límites. |

No se modifican `PlanForm.jsx`, el proveedor/hook de fase 1, cliente API, Django, DRF, autenticación, CSRF, permisos, modelos, migraciones, control de revisiones, idempotencia, evaluación o cierre.

## Pruebas ejecutadas

Con Node 22 en PATH y las dependencias locales de QA:

```sh
npm test
npm run build
python3 scripts/verify_responsive.py --artifacts artifacts/ux-phase2/isolated
```

El último comando reutiliza el verificador aislado existente: clúster PostgreSQL temporal con TLS local, cuentas ficticias, migraciones, suite Django, Gunicorn y Chromium. La conexión temporal se proporciona explícitamente; no se prueba ni modifica Neon/producción. Al terminar se detienen los procesos y se elimina el clúster. La repetición del script local de release únicamente comprueba migraciones y estáticos dentro del entorno de QA; no despliega.

| Verificación | Resultado y evidencia |
| --- | --- |
| JavaScript existente | **18/18**, doce casos API y seis de navegación/comparación. [Log](../artifacts/ux-phase2/js-tests.log). |
| Compilación | **Correcta**, 35 módulos. [Log](../artifacts/ux-phase2/build.log). |
| Django/PostgreSQL | **116/116**, sin omisiones, PostgreSQL local 14.24. Incluye concurrencia, CSRF, permisos, idempotencia, revisión y cierre histórico. [Log](../artifacts/ux-phase2/isolated/postgres-tests.log). |
| Responsive Chromium | **128 estados medidos y capturados**, todos sin desbordamiento accidental del documento ni recorte horizontal de los paneles comprobados; diálogos dentro del viewport. [Resultado](../artifacts/ux-phase2/isolated/browser/responsive/result.json), [mediciones](../artifacts/ux-phase2/isolated/browser/responsive/measurements.json). |
| Interacciones responsive | En los seis tamaños: tablas con teclado/ratón y enlaces finales, apertura/cancelación de diálogos, guardado real de acciones, error real de validación conservando valores y continuar/descartar edición. Menú compacto con acceso a logout y Escape en móvil/tablet. |
| Caso adicional del menú y fase 1 | Navegar desde edición con cambios mediante el menú, continuar, cerrar el fondo y recuperar el formulario con sus valores y foco: **correcto** en 320/375/430/768 px. Ejecución adicional con SQLite ficticia aislada; [resultado adicional](../artifacts/ux-phase2/after/responsive/result.json). El mismo caso queda incorporado al verificador reproducible. |
| Regresión completa de fase 1 | **20/20 grupos**, cero errores JavaScript. [Resultado](../artifacts/ux-phase2/isolated/browser/navigation/result.json). |
| Recorrido Full Stack | **Correcto**: login, consultas, crear/validar/editar, acciones, activar, revisar 6 → 4,5 → 3, evaluar, cerrar, recargar y logout. Incluye recuperación H02, rechazo CSRF y cartera ajena. [Resultado](../artifacts/ux-phase2/isolated/browser/browser-result.json). |
| Persistencia | **Correcta** tras reiniciar PostgreSQL/Gunicorn, repetir el script local y restaurar una copia en otra base temporal con comparación de instantáneas. [Resultado integrado](../artifacts/ux-phase2/isolated/result.json). |
| Diferencias | `git diff --check`: **correcto**. |

Los 128 estados son combinaciones de pantalla/viewport, no 128 tests unitarios independientes. Incluyen título guardado de 200 caracteres, URL larga, descripción de acción de más de 500 caracteres y responsable de 158 caracteres. Las escrituras se hacen exclusivamente sobre planes ficticios aislados. Las capturas se revisaron visualmente además de las aserciones.

### Preservación de fase 1

Se repitieron todos sus casos: Volver al plan con Enter/mismo ID/foco, cancelar limpio, continuar conservando texto, Escape del aviso, descartar sin escritura, guardar sin advertencia posterior, errores 400/503 conservando valores, precargas limpias, doble envío, clave de reintento, cierre X/Cancelar/Escape, revisión/rectificación/finalización, Atrás/Adelante, aviso nativo real de recarga y cierre de sesión con CSRF sin doble advertencia. Además se comprueba continuar/descartar en los seis tamaños y la interacción con el menú nuevo. No se detectaron regresiones de fase 1.

## Navegador, tamaños y zoom

Navegador realmente ejecutado: **Chromium 151.0.7922.34 headless**, con teclado y ratón automatizados. Se comprobaron **320 × 568, 375 × 812, 430 × 932, 768 × 1024, 1024 × 768 y 1440 × 900**.

Se intentó zoom mediante `Ctrl++`: en este Chromium headless no cambió el viewport CSS. **No se presenta el zoom nativo como validado.** Se comprobó adicionalmente reflow en **720 × 450** y **360 × 225**, equivalentes al espacio CSS disponible al 200 % y 400 % desde 1440 × 900. Dashboard, creación, detalle, cierre y navegación permanecen operables, con scroll vertical local cuando corresponde. Esta equivalencia no sustituye una prueba manual del zoom de un navegador con interfaz.

## Evidencias antes y después

- [Galería comparativa](../artifacts/ux-phase2/galeria.html): móvil, tablet, escritorio, tablas, formularios y diálogos.
- [Mediciones previas](../artifacts/ux-phase2/before/responsive/measurements.json): 87 estados con el contenido cargado y capturas asociadas.
- Dashboard 320: [antes](../artifacts/ux-phase2/before/responsive/dashboard-320x568.png) / [después](../artifacts/ux-phase2/isolated/browser/responsive/dashboard-320x568.png).
- Directorio 320: [antes](../artifacts/ux-phase2/before/responsive/sellers-320x568.png) / [después](../artifacts/ux-phase2/isolated/browser/responsive/sellers-320x568.png).
- Ficha 768: [antes](../artifacts/ux-phase2/before/responsive/seller-768x1024.png) / [después](../artifacts/ux-phase2/isolated/browser/responsive/seller-768x1024.png).
- [Creación 320](../artifacts/ux-phase2/isolated/browser/responsive/create-320x568.png), [cierre 320](../artifacts/ux-phase2/isolated/browser/responsive/close-320x568.png), [error de validación 375](../artifacts/ux-phase2/isolated/browser/responsive/validation-375x812.png).
- [Texto largo 430](../artifacts/ux-phase2/isolated/browser/responsive/long-detail-430x932.png), [diálogo con texto largo 320](../artifacts/ux-phase2/isolated/browser/responsive/long-action-320x568.png), [menú con reflow 400 %](../artifacts/ux-phase2/isolated/browser/responsive/reflow-400-navigation-360x225.png).

Las capturas son del viewport indicado; no se confunden con capturas completas de página. Las cuentas ficticias de las reproducciones previa y final son distintas. Los artefactos están ignorados por Git y disponibles localmente.

## Regresiones, limitaciones y riesgos pendientes

No se detectaron regresiones funcionales pendientes en las suites y recorridos ejecutados. Durante la preparación de QA se corrigieron una captura prematura de carga tras cambiar el hash, la sincronización de la animación de scroll del teclado antes de la rueda y un campo obligatorio omitido en la fixture de acción larga; no eran fallos del producto ni se contabilizan los intentos fallidos como verificaciones superadas.

No se han probado Firefox, Safari, dispositivos físicos, teclado virtual, orientación de un dispositivo real, lectores de pantalla ni zoom nativo con interfaz. La altura dinámica usa `dvh` con alternativa `vh`; el comportamiento ante teclado virtual queda pendiente en dispositivo real. La fase 2 no constituye una certificación WCAG ni resuelve los hallazgos de contraste, escala tipográfica o pulido visual de la auditoría.

La navegación compacta y los diálogos superponen contenido de forma intencionada mientras están abiertos; disponen de cierre y desplazamiento accesibles en los recorridos probados. Las tablas complejas conservan scroll local intencional. `beforeunload` mantiene las limitaciones del navegador documentadas en fase 1.

Django/DRF, React/API real, seguridad, aislamiento, revisión/idempotencia, persistencia y evaluación/cierre se han revalidado en el entorno indicado. No se certifican disponibilidad pública, requisitos docentes externos, memoria/vídeo/defensa, otra versión de PostgreSQL ni funcionamiento en producción. No se han regenerado los entregables académicos ni publicado estos cambios.

## Veredicto

**LISTO PARA FASE 3.** En los seis tamaños obligatorios las pantallas y funciones comprobadas son operables sin ensanchar accidentalmente la página; los datos y acciones de tablas siguen accesibles mediante scroll local. La fase 1, el flujo Full Stack y la integridad de persistencia pasan su regresión. Las limitaciones de navegador/dispositivo y zoom quedan explícitas, sin atribuirles resultados no ejecutados.
