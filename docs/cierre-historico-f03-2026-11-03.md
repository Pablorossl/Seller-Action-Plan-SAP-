# F03: vencimientos al cierre — 3 de noviembre de 2026

## Decisión

Antes, `evaluate_plan` y `PlanAction.is_overdue` consultaban el calendario actual también en planes finalizados. React mezclaba esos resultados con `closure_evaluation`.

Los planes abiertos mantienen la regla existente: una acción pendiente o en curso está vencida cuando su plazo es anterior a `timezone.localdate()` (Europe/Madrid). El propio día del plazo todavía no está vencida.

Los nuevos cierres y cancelaciones guardan, además de los totales existentes, `action_overdue`: un mapa de ID de acción a booleano. `evaluate_plan` devuelve la evaluación guardada para planes finalizados; el detalle de cada acción lee ese mapa. Así, ni el paso del tiempo ni una nueva consulta cambian la evaluación histórica. Las validaciones, permisos y bloqueo transaccional del cierre permanecen intactos.

Para planes antiguos se conservan los totales y resultados realmente guardados. Si falta el mapa, el vencimiento individual devuelve null y la interfaz indica «Vencimiento al cierre no registrado». Si faltan totales de acciones, se devuelven null y se muestran como «No registrado», sin sustituirlos por ceros. Si faltan resultados métricos se devuelve una lista vacía y resultado no evaluable, sin reconstruir mediciones actuales. La normalización opera sobre una copia y no escribe en la base. No se infiere detalle individual a partir del total ni del día de cierre.

No se necesita una migración nueva: el mapa amplía el JSON de nuevos cierres. No se rellenan ni corrigen automáticamente instantáneas existentes.

## Archivos

- `backend/action_plans/models.py`: vencimiento individual histórico en planes finalizados.
- `backend/action_plans/services.py`: lectura de instantánea y captura del mapa en la evaluación abierta usada para cerrar.
- `frontend/src/pages/PlanDetail.jsx`: etiquetas «al cierre», datos ausentes explícitos y eliminación de ceros implícitos en el resumen histórico.
- `backend/action_plans/test_closure_history.py`: regresiones temporales, cierre/cancelación, permisos de cartera e instantáneas antiguas.

## Comprobaciones

- Suite completa PostgreSQL temporal: 112 pruebas, correctas, sin omisiones (40,561 s). Incluye concurrencia.
- Suite completa SQLite: 112 pruebas, correctas, 9 omitidas por requerir PostgreSQL.
- Después se ampliaron las dos pruebas específicas con acciones de ayer/hoy/mañana y se repitió su módulo en PostgreSQL: 27 pruebas correctas (incluye 25 de PlanTests importadas).
- `npm test`, `npm run build`, `makemigrations --check --dry-run` y `git diff --check`: correctos; sin cambios de esquema pendientes.
- Chromium contra servidor local y SQLite temporal: etiqueta de vencimiento al cierre y etiqueta de detalle ausente en una instantánea antigua, correctas. Capturas temporales `/tmp/sap-f03-closed.png` y `/tmp/sap-f03-legacy.png`.

Destino PostgreSQL: instancia temporal ya verificada en la intervención F02, `127.0.0.1:55441`, directorio `/tmp/sap-f02-pg`; Django crea y destruye `test_postgres`. DATABASE_URL se proporciona explícitamente. Ninguna conexión a Neon ni cambios en servicios externos. La simulación de datos antiguos del navegador solo modifica SQLite ficticio en `/tmp`.

Logs locales: `/tmp/sap-f03-postgres.log`, `/tmp/sap-f03-tests.log`, `/tmp/sap-f03-boundaries.log`. No se publica ni despliega.

## Límites

Los cierres antiguos sin detalle seguirán sin él: no existe evidencia suficiente para afirmar el vencimiento individual histórico. Las instantáneas se respetan tal como se guardaron, incluso si pudieran contener errores anteriores; este cambio no las audita ni las repara. No se modifican otras funcionalidades.
