# Verificación local de la adaptación Vercel

Registro inicial: **29/10/2026**. La adaptación se preparó sobre `57d296f`, entonces sin commit, push ni despliegue. No se crearon recursos de pago ni una base Neon. Se conservaron `.env`, los datos del usuario y la receta histórica Render. La revisión para el commit del **02/11/2026** y sus nuevas comprobaciones figuran al final de este documento.

## Cambios comprobados

- Preset oficial Django, WSGI `config.wsgi.application`, Python 3.12 y una función en Frankfurt. Build de React dentro de `backend/frontend_dist`, con plantillas incluidas y assets bajo `/static/react/assets/`.
- PostgreSQL obligatorio con TLS en producción, conexiones cerradas por petición y cursores del servidor desactivados para PgBouncer. SQLite permanece para desarrollo.
- Vercel ignora `.env`, rechaza DEBUG y mantiene secretos obligatorios, hosts exactos, CSRF, cookies seguras y cabeceras de proxy. El health check también exige HTTPS en Vercel.
- Preview omitido por defecto, credenciales de Production separadas. Migraciones, usuarios y demo siguen siendo operaciones manuales.
- Verificación de paquete añadida a CI y opción `--vercel-settings` para la QA PostgreSQL/navegador existente.

## Resultados ejecutados

| Comprobación | Resultado |
| --- | --- |
| Dependencias Python: `pip check` | Sin incompatibilidades |
| `npm ci` + `vite build`, Node 22.19.0 | Correcto: 33 módulos, JS 279,06 kB y CSS 26,73 kB sin comprimir |
| Tests frontend | 7 aprobados; sesión, CSRF, paginación, conflictos y errores |
| `manage.py check` y `check --deploy --fail-level WARNING` | Correctos; sólo se mantiene la exclusión previa y documentada de `axes.W006` |
| `makemigrations --check --dry-run` | Sin cambios de esquema pendientes |
| Suite SQLite con aplicaciones explícitas | 79 descubiertos: 71 aprobados, 8 omitidos porque requieren PostgreSQL |
| Suite PostgreSQL 14.24 temporal | 79 aprobados, incluidas las 8 pruebas de concurrencia |
| `scripts/verify_vercel.py` | Build, WSGI sin SQL, plantillas y 157 estáticos en copia aislada sin carpeta hermana `frontend/`, `.env` ni SQLite |
| Seguridad del paquete | Login 200; dashboard anónimo 302; API anónima 403; host desconocido 400; HTTP 301; CSRF cookie Secure; HSTS |
| Assets del paquete | JS, CSS, estilo de login y estilo Admin responden 200; `index.html` del dashboard no se publica como estático |
| Configuraciones inseguras | Rechazados secretos ausentes/inseguros, hosts vacíos/comodines, SQLite/TLS desactivado y DEBUG en Vercel, incluido Preview |
| CSRF tras proxy | Login y logout válidos funcionan; token ausente u origen ajeno devuelven 403; usuario sin permisos no accede a API |
| Navegador local con `VERCEL=1`, DEBUG=False y TLS | Login, dashboard, API, creación/edición/acciones/revisiones/cierre, recarga, logout, CSRF y denegación al segundo agente correctos; sin errores de página ni respuestas críticas; ancho móvil 390 px |
| Persistencia local | Mismo plan ficticio ID 5 conservado tras reiniciar PostgreSQL y el proceso WSGI, repetir preparación de estáticos/release y consultar de nuevo |
| Copia/restauración local | Exportación real y restauración en otra base temporal, con huellas y recuentos iguales |
| Semilla voluntaria | Repetirla no modifica registros existentes |
| `git diff --check` | Sin errores de espacios |

Primero se ejecutó la QA habitual y después la variante con ajustes Vercel para comprobar esa rama de configuración. Ambas finalizaron correctamente. El intento inicial de esbuild fue bloqueado por el sandbox con EPERM; la repetición autorizada fuera del aislamiento pasó. Un primer `manage.py test` desde la raíz no descubrió tests: se corrigió usando las etiquetas explícitas que se indican abajo y esos son los resultados de la tabla.

Evidencia local, ignorada por Git: `artifacts/vercel-runtime/result.json`, `postgres-tests.log`, `production-check.log`, `model-drift.log` y `browser/` dentro de esa carpeta. La ejecución anterior está en `artifacts/vercel-postgres/`. Los recursos temporales PostgreSQL se detuvieron y eliminaron al finalizar. No se usaron conexiones del usuario para estas pruebas.

Comandos principales (desde la raíz, Python del venv y Node 22):

```bash
python scripts/verify_vercel.py
npm --prefix frontend test
node frontend/src/services/api.test.js
DJANGO_DEBUG=True DATABASE_URL= python backend/manage.py test config sellers quality action_plans
python scripts/check_production.py
python3 scripts/verify_phase3.py --pg-bin /usr/lib/postgresql/14/bin \
  --vercel-settings --artifacts artifacts/vercel-runtime
```

El último comando requiere Playwright/Chromium en el Python que ejecuta el script y las herramientas PostgreSQL/OpenSSL. Las pruebas usan datos y contraseñas ficticias; no son credenciales del tribunal.

## Alcance y pendientes públicos

Se consultó la documentación oficial actual de [Django en Vercel](https://vercel.com/docs/frameworks/full-stack/django), [Neon/Django](https://neon.com/docs/guides/django) y los planes [Hobby](https://vercel.com/docs/plans/hobby) y [Neon Free](https://neon.com/docs/introduction/plans). Ajustes y límites en [la guía de despliegue](despliegue-vercel.md).

El titular confirmó `sap-bice.vercel.app` asignado a Production en su panel. La consulta externa HTTPS respondió **404 de Vercel, NOT_FOUND**. Esto confirma una respuesta del proveedor; no demuestra SAP funcionando ni permite auditar la cuenta.

**No verificados:** builder remoto, contenido final del bundle de Vercel, CDN, proxy público, conexión real Neon/pooler, login público y persistencia después de un redeploy Vercel. La copia local valida las rutas y los archivos previstos, no simula toda la plataforma. La suite existente usa PostgreSQL 16 en CI, pero la ejecución realizada aquí utilizó 14.24.

El seguimiento posterior en [neon-setup.md](neon-setup.md) acredita conectividad de sólo lectura. Falta confirmar el proyecto/rama de esas conexiones, guardar las variables de Production, migrar y crear el usuario desde Ubuntu, publicar el código y ejecutar [el acta pública](verificacion-publica.md). En especial, registrar un ID antes de redesplegar y recuperar **ese mismo registro** después, sin ejecutar semillas. Hasta entonces el estado es **preparado y validado localmente; despliegue público pendiente**.

## Revisión para commit — 02/11/2026

Se revisaron todos los cambios pendientes sobre `57d296f`: build y configuración Vercel, ajustes Django, configuración Neon y lockfile raíz, scripts, pruebas, CI y documentación. La revisión actualiza README, matriz de requisitos, checklist y acta pública para que identifiquen el destino Vercel/Neon y el commit existente de Fase 4. La memoria PDF y las evidencias de fases anteriores conservan su fecha; deben actualizarse con los resultados públicos antes de la entrega.

| Comprobación repetida | Resultado |
| --- | --- |
| `python -m pip check` | Sin incompatibilidades |
| `npm ci --ignore-scripts --no-audit --no-fund` en la raíz | Lockfile instalado correctamente; carga local de `neon.ts` correcta, sin aplicar infraestructura |
| `manage.py test` desde `backend/`, con SQLite de prueba | 79 descubiertos: 71 aprobados y 8 omitidos por requerir PostgreSQL |
| `makemigrations --check --dry-run` | Sin cambios de esquema pendientes |
| `npm test` desde la raíz y ejecución directa de `api.test.js` | Correctos; 7 casos del frontend aprobados |
| `scripts/check_production.py` | Correcto con configuración ficticia |
| `scripts/verify_vercel.py` | Build correcto, 157 estáticos y comprobaciones del paquete aislado aprobadas |
| QA con `--vercel-settings`, PostgreSQL 14.24 temporal | 79 pruebas aprobadas, incluidas las 8 de concurrencia |
| Chromium con TLS local y `DEBUG=False` | Flujo 6% → 4,5% → 3%, cierre, recarga, logout, CSRF, aislamiento y móvil correctos; sin errores de página ni respuestas críticas |
| Persistencia y recuperación aisladas | Mismo plan ID 5 tras reinicios y preparación repetida; copia restaurada en otra base con recuentos y huellas coincidentes |
| Revisión de secretos y exclusiones | Sin coincidencias de credenciales locales ni patrones de claves privadas/tokens en los 23 archivos candidatos; `.env*`, `.neon`, SQLite y artefactos permanecen ignorados |

Comando de QA ejecutado desde la raíz:

```bash
python3 scripts/verify_phase3.py --pg-bin /usr/lib/postgresql/14/bin \
  --vercel-settings --artifacts artifacts/revision-commit-2026-11-02
```

Los logs, capturas y `result.json` se conservan localmente en esa carpeta ignorada por Git. El script eliminó sus recursos temporales al terminar. No se utilizaron las bases del usuario ni se aplicaron migraciones a Neon.

La configuración se contrastó con el [preset Django de Vercel](https://vercel.com/docs/frameworks/full-stack/django) y la [compatibilidad de Django con pooling por transacción](https://docs.djangoproject.com/en/5.2/ref/databases/#transaction-pooling-and-server-side-cursors). Esta revisión no ejecuta el builder remoto ni comprueba la CI de GitHub. Publicación, aceptación pública, actualización final de memoria, vídeo y confirmaciones académicas siguen pendientes según la [checklist](checklist-entrega.md).
