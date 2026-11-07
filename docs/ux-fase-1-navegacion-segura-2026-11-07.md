# Fase UX 1 — navegación segura y cambios sin guardar

Fecha: 07/11/2026. Base: `5988e73`. Correcciones locales; sin commits, push ni despliegues.

## Referencia e investigación

La auditoría solicitada sí está disponible: [informe del 7 de noviembre](/tmp/sap-ux-audit-20261107/AUDITORIA-UX-UI-SAP.md), con capturas y registros en su directorio `evidence/`. Se consultaron especialmente E10 (edición y vuelta sin salida), E12–E14 (diálogos), `extra-audit.json` y el alcance académico del informe. No se atribuyen sus verificaciones históricas a esta intervención.

Antes de modificar código se inspeccionaron `PlanDetail.jsx`, `PlanForm.jsx`, `Workspace.jsx`, `main.jsx`, los componentes compartidos, el cliente API y los verificadores existentes. Se reprodujeron en Chromium los dos defectos sobre la copia ficticia aislada de la auditoría, además de la pérdida de una acción al pulsar Escape. [Registro previo](../artifacts/ux-phase1/before.json) y [captura previa](../artifacts/ux-phase1/before-return.png).

Los formularios de datos editables son creación/edición de plan y los diálogos de indicador/objetivo, acción, revisión/rectificación y finalización. Las búsquedas, filtros, pestañas y paginación de `Workspace.jsx` consultan datos: no representan cambios de negocio pendientes de guardar y no reciben una advertencia. El login Django y la administración Django no se convierten en editores React ni se modifican.

## Causas raíz

1. **Volver al plan:** el detalle activa `editing` en estado local, sin cambiar de ruta. El enlace del editor apunta al hash que ya está abierto. No dispara una transición que cambie `editing`, por lo que permanece el formulario. El guardado sí abandonaba la edición mediante `done`, pero no había una cancelación equivalente.
2. **Pérdida de texto:** los formularios solo almacenaban sus valores en estado local. Cancelar, X y Escape desmontaban inmediatamente el diálogo; `hashchange` cambiaba la ruta y la clave del contenedor desmontaba la página. No existía comparación con los valores iniciales ni una decisión previa al desmontaje. Tampoco había protección de recarga/salida del documento.

Se detectó además que el motivo de rectificación estaba fuera del `fieldset` deshabilitado durante el envío: permitía introducir texto nuevo mientras se guardaba. Se bloquea también ese campo durante la petición, sin cambiar su validación ni el payload.

## Solución implementada

- El editor recibe una cancelación explícita que desactiva `editing`. «Volver al plan» y Cancelar regresan al detalle del mismo ID; guardar conserva la respuesta autoritativa de Django. Al salir de edición o guardar se restaura el foco al botón Editar plan. Entrar en edición lleva el foco al encabezado.
- Un hook compara instantáneas de los valores editables con su estado inicial. Incluye textos, fechas, responsable, vendedor, indicadores/objetivos y los campos propios de cada diálogo; normaliza IDs numéricos frente a sus representaciones en selects. No utiliza un simple indicador de “campo tocado”. Revertir los valores iniciales elimina la advertencia.
- La precarga asíncrona del indicador y sus fechas forma parte de la línea base de creación. El formulario espera esa precarga antes de permitir editar, evitando falsos cambios y sobrescrituras de entradas mientras llega la respuesta. Los datos de presentación de los pickers y sus búsquedas no se comparan como cambios de negocio.
- Un único aviso compartido ofrece **Continuar editando** y **Descartar los cambios y abandonar**. El foco inicial queda en continuar. Escape y X del aviso equivalen a continuar; los formularios permanecen montados y conservan sus valores hasta decidir.
- Los enlaces de rutas hash se comprueban antes de navegar. Las entradas de historial conservan índices para restaurar Atrás/Adelante rechazados sin sobrescribir el destino ni desmontar el editor. Se conserva el formato de todas las rutas públicas. La confirmación pendiente se comparte y evita diálogos duplicados.
- Cancelar, X y Escape de cada formulario usan la misma decisión. El cierre de sesión mantiene su POST con CSRF y utiliza esa confirmación antes de enviar. Las salidas del documento, recarga y cierre de pestaña utilizan `beforeunload` y el mensaje nativo del navegador.
- Las salidas internas quedan bloqueadas durante una escritura. Se mantiene el bloqueo de doble envío y la clave de idempotencia del hook existente. Un fallo de validación o guardado no limpia valores ni desactiva la protección. El guardado correcto sí permite navegar sin advertencia.
- El aviso usa los estilos existentes, con ajuste de línea exclusivamente en sus botones para que ambas opciones sean visibles en móvil. No se hace un rediseño general.

No se introduce autosave, localStorage, almacenamiento de borradores, dependencias ni cambios en backend, contratos, modelos, migraciones o reglas de negocio.

## Archivos modificados y añadidos

| Archivo | Cambio |
| --- | --- |
| `frontend/src/pages/PlanDetail.jsx` | Cancelación explícita, foco, protección de cada diálogo y bloqueo del motivo de rectificación durante el envío. |
| `frontend/src/pages/PlanForm.jsx` | Cancelar/volver, instantánea de valores, precarga inicial y limpieza tras guardar. |
| `frontend/src/main.jsx` | Integra el proveedor y la navegación protegida conservando rutas hash. |
| `frontend/src/components/UnsavedChanges.jsx` (nuevo) | Hook, registro del formulario activo, aviso único, salida nativa y cierre de sesión protegido. |
| `frontend/src/components/ui.jsx` | Foco inicial configurable después de abrir el diálogo nativo; conserva la restauración previa del foco. |
| `frontend/src/services/navigation.js` (nuevo) | Comparación de valores y navegación hash con restauración del historial. |
| `frontend/src/styles.css` | Ajuste de línea limitado a los botones del aviso. |
| `frontend/src/services/navigation.test.js` (nuevo) | Seis pruebas JavaScript de comparación, rutas, historial y decisión pendiente. |
| `frontend/package.json` | Ejecuta las dos suites JavaScript directamente con Node, con resultados de cada caso visibles. |
| `scripts/verify_unsaved_changes.py` (nuevo) | Veinte grupos de comprobaciones Chromium y reutilización del verificador aislado Full Stack existente. |
| Este informe | Causas, cambios, evidencias, resultados y límites. |

`Workspace.jsx` se inspeccionó y no necesita modificaciones para esta fase. Los scripts previos de pruebas, el cliente API y el hook de mutación se conservan.

## Pruebas y resultados

Comandos reproducibles desde la raíz, usando Node 22 en PATH y las dependencias locales de QA:

```sh
npm test
npm run build
python3 scripts/verify_unsaved_changes.py --artifacts artifacts/ux-phase1/isolated
```

El último comando crea un clúster PostgreSQL temporal, cuentas y datos ficticios, TLS local y Gunicorn. Usa el Python del venv para Django y Playwright/Chromium del Python de QA. Sustituye explícitamente la conexión configurada por la conexión temporal; no ejecuta las pruebas sobre Neon ni bases reales. Detiene servidores y elimina el clúster al terminar. El paso `release-repeat` ejecuta el script local de migración/estáticos del verificador, sin publicar ni desplegar.

| Comprobación | Resultado | Evidencia |
| --- | --- | --- |
| JavaScript | **18/18**: doce casos API existentes y seis nuevos; cero fallos. | [Log](../artifacts/ux-phase1/js-tests.log) |
| Build Vite | **Correcto**, 35 módulos; cero errores. | [Log](../artifacts/ux-phase1/build.log) |
| Django/PostgreSQL | **116/116**, sin omisiones; incluye concurrencia, permisos, validación, CSRF, revisiones, idempotencia, evaluación y cierres. PostgreSQL local 14.24. | [Log](../artifacts/ux-phase1/isolated/postgres-tests.log) |
| Esquema/configuración | Migraciones desde cero, ausencia de deriva de modelos, migraciones pendientes y comprobación de producción: **correctas**. | Logs en [directorio aislado](../artifacts/ux-phase1/isolated/) |
| Chromium, fase 1 | **20/20 grupos**, cero errores JavaScript. Escritorio 1440 px y móvil emulado 390 px. | [Resultado](../artifacts/ux-phase1/isolated/browser/navigation/result.json) |
| Chromium, recorrido completo | **Correcto**: login, consultas, creación, error real de objetivo, edición, acciones, activación, revisiones 6 → 4,5 → 3, evaluación, cierre y recarga; recuperación ante JSON/HTML inválido, CSRF y acceso ajeno rechazados, logout. | [Resultado](../artifacts/ux-phase1/isolated/browser/browser-result.json) |
| Persistencia y recuperación | **Correctas** tras reiniciar PostgreSQL y Gunicorn, repetir el script local y restaurar un backup en otra base temporal; comparación de instantáneas. | [Resultado integrado](../artifacts/ux-phase1/isolated/result.json) |
| Revisión de diferencias | `git diff --check`: **correcto**. | Revisión local |

Los veinte grupos comprueban múltiples aserciones, no equivalen a veinte pruebas unitarias adicionales de Django. No se suman cifras entre ejecuciones repetidas.

### Cobertura específica en Chromium

1. Precarga de vendedor/indicador limpia y cancelación contextual sin aviso.
2. Salida lateral de creación: continuar conserva los valores.
3. Recarga real rechazada mediante aviso nativo: conserva los valores.
4. Atrás rechazado/restauración de URL, Atrás con descarte y Adelante sin borrador residual.
5. Validación real de Django fallida: conserva valores y protección.
6. Crear correctamente ante dos `requestSubmit`: un único POST y detalle sin aviso.
7. Volver al plan con Enter: salida, mismo ID y foco restaurado.
8. Cancelar edición limpia sin advertencia.
9. Volver con cambios: continuar y Escape conservan; descartar no escribe en API.
10. Modificar y revertir los valores iniciales no avisa.
11. Error de guardado 503 inyectado: conserva texto y protección.
12. Guardar edición: un único PATCH, misma clave al reintentar datos idénticos, foco, guardia limpia y salidas bloqueadas mientras se guarda.
13. Acción: cierre limpio y Cancelar/X/Escape con cambios; restauración del foco y descarte sin escritura.
14. Objetivo existente revertido y diálogo de nuevo indicador vacío sin falsos avisos.
15. Revisión y finalización con y sin texto pendiente.
16. Atrás con un diálogo abierto conserva formulario y URL al continuar.
17. Rectificación precargada limpia y motivo modificado protegido.
18. Rectificación guardada: motivo bloqueado durante el envío, Escape no abandona, un POST y revisiones originales conservadas.
19. Aviso móvil: ambos botones completamente dentro del viewport, continuar conserva y cancelar descarta.
20. Cerrar sesión: continuar conserva; descartar envía el POST con CSRF, sin segunda advertencia nativa.

Capturas: [aviso escritorio](../artifacts/ux-phase1/isolated/browser/navigation/unsaved-warning.png), [aviso móvil](../artifacts/ux-phase1/isolated/browser/navigation/mobile-warning.png), [creación conservada](../artifacts/ux-phase1/isolated/browser/navigation/creation-retained.png). Las capturas se revisaron visualmente además de las aserciones automatizadas.

## Regresiones y correcciones durante QA

No se detectan regresiones funcionales pendientes en los recorridos y suites ejecutados. La primera versión del aviso no enfocaba continuar al abrir el diálogo; se corrigió enfocando después de `showModal()`. La revisión visual móvil detectó opciones parcialmente fuera del aviso; se corrigió con el ajuste específico y una aserción geométrica. También se corrigió una selección ambigua de fixture en el propio verificador de rectificación. Los intentos fallidos intermedios no se presentan como pruebas superadas.

Los demás hallazgos de la auditoría —desbordamiento de otras pantallas, contraste, contexto de listados, foco general de navegación y otras prioridades— permanecen fuera de esta fase. La comprobación móvil del recorrido completo corresponde a la pantalla que prueba el script, no certifica toda la aplicación sin desbordamiento.

## Requisitos del TFG y límites

Se usa como referencia la [trazabilidad local](trazabilidad-requisitos.md) y la auditoría disponible; no se ha vuelto a consultar la guía externa ni se certifica una evaluación académica.

| Área | Verificación realizada en esta fase | Límite |
| --- | --- | --- |
| Django/DRF, modelos, vistas, plantillas y autenticación | Suite completa, login/logout reales, migraciones y comprobaciones de configuración. | No se rediseña ni valida visualmente toda la administración Django. |
| React integrado con backend real | Crear, editar, acciones, revisiones, rectificación, evaluación y cierre mediante la API real, con recarga y persistencia. | Los fallos 503 y cuerpos inválidos son inyecciones deliberadas de QA; el producto no usa datos simulados. |
| Seguridad y aislamiento | Suite de permisos/CSRF/concurrencia; acceso ajeno 404, escritura sin CSRF 403 y sesión/logout en Chromium. | No equivale a una auditoría integral de penetración. |
| Integridad de negocio | Revisión/idempotencia, ausencia de dobles escrituras, histórico, evaluación, cierre e instantáneas protegidos por suite y recorrido. | No se cambian las reglas ni se verifican todas las combinaciones posibles de datos. |
| PostgreSQL y persistencia | Base temporal, reinicios y backup/restauración independiente con comparación de datos. | PostgreSQL local 14.24; no se repite sobre PostgreSQL de producción ni se conecta a Neon. |
| Arquitectura y prácticas | Cambios acotados, mecanismo reutilizable, tests reproducibles, build y este informe. | No se crean commits ni CI remoto por instrucción del usuario. |
| Documentación, presentación y reflexión | Causas, evidencias y límites documentados. | No se regeneran memoria PDF/Word, vídeo o presentación; no se inventan métricas de productividad ni nota. |
| Disponibilidad pública y entrega | Sin intervención en servicios remotos. | Despliegue, segunda red, expediente, vídeo, entrega y defensa no se revalidan en esta fase. |

Chromium es headless, con teclado y ratón automatizados y viewport móvil emulado. No se han probado Firefox, Safari, lectores de pantalla ni dispositivos físicos. `beforeunload` depende del navegador y de la interacción previa; su texto es nativo y no hay garantía frente a cierre forzado del proceso o del sistema. No se implementa persistencia de borradores. Los artefactos bajo `artifacts/` están ignorados por Git y permanecen disponibles localmente; el informe de auditoría original está en `/tmp`.

## Veredicto

**LISTO PARA FASE 2**, en el alcance local de estas dos correcciones. La edición tiene una salida explícita, las salidas protegidas requieren una decisión y los recorridos de error/guardado conservan la integridad Full Stack. No quedan fallos de esta fase en las pruebas ejecutadas. Esto no implica que los demás hallazgos UX estén corregidos, que se haya publicado la versión o que el TFG esté formalmente aprobado.
