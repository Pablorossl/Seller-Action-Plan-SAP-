# Concurrencia de rectificaciones y F02 — 3 de noviembre de 2026

Continuación de `rectificacion-revisiones-2026-11-03.md`. Se conserva el informe anterior como evidencia de su estado entonces.

## PostgreSQL verificado

PostgreSQL 14 temporal creado con initdb en `/tmp/sap-f02-pg`, usuario `sap_test`. Antes de las pruebas, SQL devolvió base `postgres`, dirección `127.0.0.1`, puerto `55441` y `data_directory=/tmp/sap-f02-pg`. Django creó y destruyó `test_postgres`. Se proporcionó DATABASE_URL explícitamente; no se usó Neon.

Se ejecutaron las pruebas existentes de bloqueo, cierre, reintentos y escrituras concurrentes. Se añadió `ConcurrencyTests.test_api_competing_rectifications_and_originals`: dos conexiones y clientes HTTP independientes compiten por rectificar la misma revisión o crear originales incompatibles del mismo periodo. Ambos escenarios terminan con una respuesta 201 y una 400, un único registro efectivo y el historial intacto. La evaluación referencia ese registro efectivo.

La prueba detectó un mensaje técnico del validador automático de unicidad de DRF (`supersedes`). Se eliminó ese validador de campo para que actúe la validación del modelo dentro del bloqueo del plan: «Esta revisión ya está rectificada. Recarga el historial». Se mantienen la restricción uno a uno de base de datos y la unicidad parcial de originales. No se detectó pérdida de historial ni ramificación.

Comando específico: `env DATABASE_URL=postgres://sap_test@127.0.0.1:55441/postgres DJANGO_DEBUG=True .venv/bin/python backend/manage.py test action_plans.test_concurrency --noinput`. Resultado: 21 pruebas correctas (incluye las pruebas API importadas por ese módulo).

## F02: decisiones

- Se validan `QualityMetric.period_start` y `period_end`: ninguna puede superar `timezone.localdate()`, con zona configurada `Europe/Madrid`. Hoy es válido; se conserva además la validación inicio ≤ fin. No se exige que hoy termine un mes natural: la evaluabilidad mensual sigue siendo una regla distinta.
- `recorded_at` es un instante automático de registro, no la fecha observada, y no se modifica. Las fechas previstas de planes y acciones pueden seguir estando en el futuro.
- El modelo valida en `clean()` y `save()`. Admin usa esa validación y muestra errores en ambos campos. La API de observaciones continúa siendo de solo lectura (POST/PATCH devuelven 405); no se añade una vía de escritura.
- La selección de última observación filtra los periodos futuros **antes** de escoger el último registro por vendedor, código y canal. Así puede recuperar la observación válida anterior. Si solo hay futuras, no hay observación actual.
- El historial conserva los registros futuros heredados. La API expone `is_future`; React los identifica como «Observación futura · excluida del resumen actual». Su clasificación es `not_evaluable`. Los indicadores ausentes se calculan con observaciones no futuras.
- No se admite una observación futura heredada como base de un objetivo nuevo, incluso si se solicita por ID mediante la API de planes.
- No hay migración adicional para F02: son validaciones y consultas, sin cambios de esquema ni saneamiento automático. La migración 0003 de rectificaciones se ejercitó desde cero en la base de pruebas PostgreSQL.

## Verificación final

- Suite completa: `env DATABASE_URL=postgres://sap_test@127.0.0.1:55441/postgres DJANGO_DEBUG=True .venv/bin/python backend/manage.py test action_plans quality sellers config --noinput`: **110 pruebas correctas, ninguna omitida**, 42,336 s.
- Límites cubiertos: hoy, mañana en ambos campos y medianoche de Madrid (23:30 UTC del 2 de noviembre ya es día 3 local).
- Datos heredados: registro futuro conservado, clasificación no evaluable, resumen con observación válida anterior y desviación visible, rechazo de nuevo plan basado en dato futuro; API de observaciones no escribible.
- ModelForm de Admin: mensajes por campo comprobados.
- `npm test`, `npm run build`, `makemigrations --check --dry-run` y `git diff --check`: correctos.
- Chromium real contra servidor y SQLite temporales locales: alta en Admin con inicio y fin de 2099 rechazada y dos mensajes de campo visibles. Captura en `/tmp/sap-f02-admin.png`. La base temporal de navegador es distinta de la de concurrencia.

## Límites

Las pruebas concurrentes acreditan los escenarios ejecutados, no todas las intercalaciones posibles. SQL directo, `QuerySet.update()` y `bulk_create()` omiten la validación del modelo; no son vías de entrada del producto. No se incorpora un CHECK dependiente de la fecha actual ni se modifican datos heredados. No se inspeccionan ni corrigen datos externos. F03 queda expresamente fuera del cambio; no se despliega ni publica.
