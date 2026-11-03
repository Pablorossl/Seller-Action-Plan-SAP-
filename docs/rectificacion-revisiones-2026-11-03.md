# Rectificación de revisiones — 3 de noviembre de 2026

Resuelve F01 de la auditoría del 2 de noviembre. No altera el informe ni sus evidencias históricas.

Cada rectificación es una nueva PlanReview inmutable. `supersedes` enlaza con la versión efectiva anterior y `correction_reason` exige el motivo. El autor se obtiene de la sesión y `recorded_at` registra el instante de alta. El objetivo y las fechas del periodo se conservan; un periodo distinto requiere una revisión original distinta.

La unicidad parcial mantiene un único registro original por objetivo y periodo. La relación uno a uno impide ramificaciones; el modelo rechaza rectificar versiones ya sustituidas. Los bloqueos del plan serializan la escritura con otras revisiones y con el cierre. Los reintentos no crean otra medición: reciben un error de validación si ya existe la rectificación. No se modifican registros anteriores.

La evaluación descarta registros sustituidos antes de elegir el periodo más reciente. Una rectificación de un periodo antiguo no desplaza una medición posterior. El historial API conserva todas las versiones; React distingue las sustituidas de las efectivas y muestra motivo, vínculo, autor y fecha. Se utiliza el permiso existente `add_planreview` y el aislamiento de cartera. Los planes cerrados o cancelados rechazan nuevas rectificaciones.

La migración 0003 añade dos campos y sustituye la unicidad original por una restricción parcial. No contiene operaciones de modificación de datos. Debe aplicarse antes de ejecutar esta versión; no se ha aplicado a servicios externos.

## Verificación local

- `DATABASE_URL='' DJANGO_DEBUG=True .venv/bin/python backend/manage.py test action_plans quality sellers config --noinput`: 106 pruebas, correctas; 8 omitidas al requerir PostgreSQL. La clase de rectificaciones reutiliza también las pruebas heredadas de planes.
- `makemigrations --check --dry-run`: sin cambios pendientes.
- `npm test`: correcto.
- `npm run build`: correcto.
- `git diff --check`: correcto.
- Migración desde cero sobre SQLite temporal: correcta.
- Chromium contra servidor local y SQLite temporal: revisión sin datos, formulario de rectificación con medición, historial y recarga correctos. Captura temporal: `/tmp/sap-rect-browser.png`.

Se cubren recuperación sin datos, errata, cadena histórica, motivo obligatorio, periodo inmutable, duplicados, evaluación, permisos de cartera/rol y prohibición tras cierre. No se ha ejecutado la suite de concurrencia PostgreSQL en esta intervención; los bloqueos y restricciones siguen el patrón existente. F02 (observaciones futuras) y F03 (vencimientos históricos) quedan fuera de este cambio. No se publica ni despliega.
