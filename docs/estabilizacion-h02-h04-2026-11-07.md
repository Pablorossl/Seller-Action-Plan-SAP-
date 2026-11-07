# Estabilización H02 y H04 — 07/11/2026

Base: `main`, `d53e447`, árbol limpio antes de intervenir. Cambios locales sin
commit, push ni despliegue. No se usan bases locales del usuario ni producción.

## H02

`api()` ocultaba fallos de `response.json()` devolviendo `{}`. Ahora rechaza
cuerpos ilegibles con un `ApiError` recuperable y el estado HTTP recibido.
No expone HTML ni detalles internos de parseo. Los errores HTTP conservan sus
campos JSON; los errores de red conservan estado 0 y las cancelaciones se propagan.
HTTP 204 devuelve `null` sin leer el cuerpo, compatible con DELETE de vendedores.
No se añaden reintentos ni se modifican cookies, credenciales, CSRF o idempotencia.

Los consumidores reales son `useResource`, `useMutation` y las cargas auxiliares
de `PlanForm`. Ya capturan rechazos; `Resource` muestra `ErrorState` con recarga
y los formularios conservan `FormError`. `getAllPages` no tiene consumidores de
producto y ya rechaza fallos de JSON; no se modifica.

Pruebas Node cubren JSON correcto, JSON malformado, HTML, cuerpo 200 vacío,
204, 400 con validación, 403, 404, 409, 500, red, cancelaciones y ausencia de
reintentos de escritura. El recorrido Chromium inyecta JSON corrupto y HTML en
`/api/overview/`, comprueba el error del Dashboard y recupera con recarga manual.

## H04

Reproducido con el filtro real: incluía acciones de planes cerrados/cancelados
usando la fecha actual, incluso cuando la instantánea conservaba `false`.
El filtro excluye `FINAL_STATUSES`; la columna se denomina «Vencida (operativa)»
y usa la misma semántica. No se modifica el modelo, el cierre ni las instantáneas.
Véase [distinción funcional](dominio.md#vencimiento-operativo-e-histórico).

Las pruebas instancian el filtro y ModelAdmin sobre su queryset limitado a la
cartera. Cubren borrador, progreso, revisión, acciones pendientes/en progreso,
completadas/canceladas, fechas pasada/hoy/futura, ambos estados finales,
coherencia de columna y filtro, aislamiento y conservación histórica en 2027.
La suite existente protege evaluación, cierres antiguos, permisos y concurrencia.

## Preparación UX/UI

| Zona | Ubicación actual | Precaución |
| --- | --- | --- |
| Dashboard | `Workspace.jsx`, `Dashboard` | Contrato overview, prioridades, error y recarga |
| Directorio | `Workspace.jsx`, `Sellers` | Búsqueda, paginación y cartera |
| Detalle de vendedor | `Workspace.jsx`, `SellerDetail` | Varias cargas independientes, indicadores y planes |
| Listado de planes | `Workspace.jsx`, `Plans`, `PlanTable` | Filtros URL, estados y permisos |
| Creación/edición | `PlanForm.jsx` | Picker paginado, validación, revisión e idempotencia |
| Acciones y seguimiento | `PlanDetail.jsx` | Diálogos, estados terminales, evidencia y fechas |
| Evaluación y cierre | `PlanDetail.jsx` | Permiso de cierre, confirmación y lectura histórica |
| Navegación | `main.jsx` | Rutas hash, sesión inicial, CSRF y foco |
| Estilos/responsive | `styles.css` | CSS global compartido y breakpoints |

`PlanDetail.jsx` tiene 986 líneas; `Workspace.jsx`, 821; `PlanForm.jsx`, 493;
`styles.css`, 2033. `components/ui.jsx` comparte campos, modales, errores,
paginación y hooks. El sistema visual usa variables CSS y clases globales;
no hay aislamiento de estilos por componente. La lógica de negocio autoritativa
reside en Django, con reglas y servicios separados de vistas/serializadores.

Textos y presentación de tarjetas/encabezados aislados permiten cambios acotados.
Campos, modales, tablas compartidas y estilos globales tienen mayor alcance.
No hace falta una reescritura previa. Antes o durante un rediseño grande conviene
extraer secciones y formularios de los dos archivos grandes en pasos separados,
preservando callbacks de recarga, revisiones, idempotencia, foco y permisos.
Repetir Node, build, suite Django/PostgreSQL y recorrido Chromium tras cada bloque.
La cobertura visual no sustituye pruebas específicas de accesibilidad y más
anchos de pantalla en la siguiente fase; el recorrido actual comprueba 390 px.

La arquitectura admite nuevos componentes/rutas en React, acciones de ViewSet y
serializadores, servicios de dominio, filtros y permisos explícitos. Nuevos
modelos requieren migraciones y restricciones justificadas. Preservar siempre
`visible_sellers`/`visible_plans`, validación del dominio, transacciones,
control de revisiones e instantáneas históricas. No se implementan extensiones.

## Alcance académico

Guía oficial consultada íntegramente mediante Google Drive el 07/11/2026:
[FS Proyecto Final - Máster en Desarrollo Full Stack](https://docs.google.com/document/d/1KhmvNgC4g9WI8suPOBjGFcUCQeA8rVPkoVS53fYLOkQ/edit).
Se conservan Django con modelos/vistas/plantillas, autenticación, persistencia,
React con datos reales, documentación y estructura de despliegue. Rúbrica
30/15/15/15/15/10; aprobado 7/10, sin asignar nota. El vídeo (máximo cinco minutos),
el expediente y la confirmación docente siguen fuera del alcance. La publicación
vigente y el acceso docente a entregables no se revalidan con estas pruebas locales.

## Validación ejecutada

Evidencias locales en `artifacts/h02-h04/` (artefactos ignorados por Git).

| Comprobación | Resultado | Evidencia |
| --- | --- | --- |
| Node 22, pruebas del cliente | 12/12 | `javascript-tests.log` |
| Build Vite 7.3.7 / React 19.3.1 | Correcto | `vercel-package.log` |
| Django 5.2.18 / DRF 3.18.3, SQLite | 116 descubiertas: 107 pasan, 9 omitidas por requerir PostgreSQL | `sqlite-tests.log` |
| PostgreSQL local 14.24, suite completa | 116/116, incluida concurrencia | `postgres-tests.log` |
| Migraciones nuevas y comprobación de modelos | Sin divergencias | `migrations-fresh.log`, `model-drift.log`, `migrations-check.log` |
| System/deploy checks | Sin incidencias nuevas; se conserva el silencio documentado de axes.W006 | `production-check.log`, `release-repeat.log` |
| Chromium, flujo integral y recuperación H02 | Correcto; cero errores JS y respuestas críticas | `browser/browser-result.json` |
| Reinicios PostgreSQL/Gunicorn y release local repetido | Persistencia conservada | `result.json` |
| Copia y restauración en otra base temporal | Snapshots idénticos | `result.json` |
| Paquete Vercel aislado, plantillas, estáticos, HTTPS/hosts | Correcto, sin despliegue | `vercel-package.log` |
| Dependencias Python y whitespace Git | `pip check` y `git diff --check` correctos | Salida de ejecución |

Incidencias de ejecución resueltas: la invocación inicial de Django desde la raíz
descubrió cero tests y se repitió correctamente desde `backend`; un system check
coincidió con la regeneración de `dist` y se repitió después sin avisos; esbuild
fue bloqueado por el sandbox al instalar y el empaquetado se repitió con la
autorización de ejecución externa. No se atribuyen esos intentos a pruebas aprobadas.
Las reproducciones previas fallaron como se esperaba antes de aplicar las correcciones.

No se detectan regresiones relacionadas. PostgreSQL 18/Neon y el despliegue público
no se prueban en esta intervención; PostgreSQL se valida exclusivamente en la
infraestructura local aislada existente. No hay migraciones nuevas, cambios de
datos de usuario, dependencias nuevas ni rediseño. Veredicto técnico: listo para UX/UI;
mantener pendientes los entregables académicos externos y la revisión de publicación
cuando se autorice publicar estos cambios.
