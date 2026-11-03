# Configuración y verificación de Neon

Actualizado el **03/11/2026**. Configuración completada y flujo funcional verificado desde la aplicación local contra PostgreSQL real en Neon.

| Destino | Valor verificado mediante el CLI autenticado |
| --- | --- |
| Organización | `org-rough-thunder-87253091` |
| Proyecto | `SAP` / `empty-feather-02803695` |
| Rama | `production` / `br-divine-sky-b9hvdrte` |
| Servicios utilizados | PostgreSQL |
| Aplicación local | `http://127.0.0.1:8000` |

## Cambios y conexión

- Neon CLI actualizado globalmente a **8.18.0**, con Node **22.19.0**. El login del navegador terminó con `Auth complete (profile DEFAULT)`.
- `.neon` enlaza ahora el proyecto solicitado. Este archivo local y `.env` están ignorados por Git.
- Se conserva `neon.ts`, incluido `auth: false`: el login y las sesiones siguen en Django y se almacenan en PostgreSQL.
- `neon deploy` confirmó la configuración existente y descargó tres variables a `.env`, que conserva permisos `600`: `DATABASE_URL`, `DATABASE_URL_UNPOOLED` y `NEON_BRANCH`.
- Se reutiliza la integración existente: Django ORM y **psycopg 3**, URL pooled para peticiones y URL directa para migraciones mediante `scripts/neon_manage.py`. Las dos conexiones pertenecen al mismo endpoint/base y usan TLS. Se mantienen conexiones por petición y cursores compatibles con PgBouncer. [Guía oficial de conexión](https://neon.com/docs/connect/choose-connection).
- Las **33 migraciones** se validaron primero en una rama temporal derivada de `production` y después se aplicaron a `production`. La rama temporal se eliminó; no se cambiaron las credenciales locales a ella.
- Añadidos `scripts/verify_neon_e2e.py` y `npm run verify:neon -- --allow-writes`. El script arranca `npm start`, comprueba login, React, operaciones de API, SQL independiente y persistencia tras reiniciar la aplicación. Usa una cuenta y un vendedor temporales y elimina sus registros al terminar.

Neon proporciona aquí PostgreSQL. La aplicación se ejecutó localmente; esta operación no publica el frontend ni cambia la configuración de Vercel.

## Evidencias

Todos los comandos finales siguientes terminaron con **exit code 0**.

`neon deploy`:

```text
→ Applying to branch production (br-divine-sky-b9hvdrte)
Utilized services: Postgres
No changes — branch production already matches the policy.
Pulled 3 Neon variables into .env
  Postgres        DATABASE_URL, DATABASE_URL_UNPOOLED
  Branch          NEON_BRANCH
```

`npm run build`:

```text
vite v7.3.7 building client environment for production...
✓ 33 modules transformed.
dist/index.html                   0.40 kB │ gzip:  0.28 kB
dist/assets/index-aK7tKlOf.css   26.73 kB │ gzip:  6.72 kB
dist/assets/index-DEZfk4kj.js   280.36 kB │ gzip: 85.05 kB
✓ built in 1.32s
```

`npm run db:migrate -- --noinput` aplicó las 33 migraciones con `OK`. `npm run db:migrate -- --check` terminó sin migraciones pendientes. La validación previa de la rama temporal terminó con:

```text
PASS: all Django migrations applied and verified on the isolated Neon branch.
```

`npm run verify:neon -- --allow-writes` guardó también el informe local en `artifacts/neon-setup-e2e.json`:

```json
{
  "service": "postgres",
  "branch": "production",
  "checks": {
    "health_http_200": true,
    "login_dashboard_and_react_assets": true,
    "api_create_201_and_update_200": true,
    "independent_direct_connection_confirms_write_and_tls": true,
    "pooled_connection_tls": true,
    "session_and_data_survive_app_restart": true,
    "api_delete_204_then_404": true,
    "logout_and_anonymous_403": true,
    "temporary_records_cleaned": true
  },
  "passed": true
}
```

`npm test`: **1 test, 1 aprobado, 0 fallos**.

Tras dejar `npm start -- --noreload` activo, `.venv/bin/python scripts/check_neon.py` confirmó `SELECT 1`, TLS y las cinco tablas SAP/Django en las conexiones directa y pooled. Resultado HTTP:

```json
{
  "/accounts/login/": 200,
  "/healthz/": 200,
  "/api/plans/": 403
}
```

El informe terminó con `"read_only_checks_passed": true`. Su campo `project_and_branch_verified` permanece en `false` por diseño: ese script comprueba SQL/HTTP, mientras que la pertenencia al proyecto y rama se verificó por separado mediante el CLI autenticado.

## Incidencias resueltas

- El `neon init` exacto intentó instalar plugins de agentes: Copilot CLI no estaba disponible y el instalador quedó esperando en Claude/Codex. Se interrumpió y se repitió con `--no-agent-setup`, reutilizando las skills Neon ya instaladas.
- Antes del login, `init` escribió un enlace offline. Después del login se repitió y el API confirmó el proyecto y descargó las variables. El enlace offline por sí solo no acredita acceso.
- El sandbox bloqueó el acceso al API y la resolución DNS de PostgreSQL. Los reintentos autorizados con acceso de red funcionaron.
- La primera ejecución del nuevo checker llegó a verificar la persistencia tras reiniciar, pero su petición DELETE omitía CSRF y recibió el 403 esperado. Se corrigió el cliente de prueba para incluir CSRF en todas las operaciones de escritura y la ejecución final pasó íntegramente.

## Repetir la verificación

Desde la raíz, con Node 22 y el venv instalado:

```bash
npm run build
npm run db:migrate -- --check
# El puerto 8000 debe estar libre: el checker arranca y reinicia su propio servidor.
npm run verify:neon -- --allow-writes
npm start -- --noreload
# En otra terminal, comprobación de sólo lectura:
.venv/bin/python scripts/check_neon.py
```

El checker elimina sus credenciales temporales. Para crear una cuenta propia sin poner la contraseña en argumentos o logs:

```bash
.venv/bin/python scripts/neon_manage.py create_demo_agent --username evaluador
```

Para alojar la aplicación públicamente, seguir [despliegue-vercel.md](despliegue-vercel.md).
