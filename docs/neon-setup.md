# Configuración Neon: resultado y pasos pendientes

Actualizado el **29/10/2026**. Se ha preparado el repositorio y probado una conexión real de sólo lectura. **No se ha completado el despliegue de servicios ni la verificación funcional sobre Neon.**

Destino solicitado: organización `org-rough-thunder-87253091`, proyecto `winter-grass-28484559`, rama `production`, sólo PostgreSQL. El archivo privado `.neon` apunta a ese destino, pero el CLI lo escribió **offline**, sin verificar que la cuenta tenga acceso. No se han creado recursos, contratado planes ni publicado SAP en Vercel.

## Trabajo realizado

- Instalado globalmente Neon CLI **8.13.2** mediante `npm i -g neon@latest` usando Node 22.
- Ejecutado el `neon init` solicitado. Creó `neon.ts`, `package.json`, lockfile y `.neon`; añadió `.neon` a `.gitignore`.
- Instalado y consultado el plugin Neon para Codex: skills [neon](https://github.com/neondatabase/agent-skills/tree/main/skills/neon) y [neon-postgres](https://github.com/neondatabase/agent-skills/tree/main/skills/neon-postgres). Se conserva Django ORM y psycopg, con TLS, conexiones por petición y compatibilidad con PgBouncer. No se utiliza un driver JavaScript en Django ni se sustituye el login por Neon Auth.
- Añadidos comandos raíz `npm run build`, `npm start`, `npm test` y `npm run db:migrate`. El último es explícito y usa `DATABASE_URL_UNPOOLED`, sin modificar la URL pooled guardada en disco.
- Django lee `.env` si existe y, en su ausencia, `.env.local`, igual que el destino de `neon env pull`. Las variables del proceso prevalecen. En Vercel no lee ninguno de esos archivos.
- Añadido `scripts/check_neon.py`: sólo ejecuta consultas de lectura y peticiones GET, oculta las credenciales y devuelve un estado no satisfactorio si faltan tablas o falla el health check.

La copia privada `.env.before-neon` conserva el entorno previo, donde `DATABASE_URL` estaba vacía. Durante la sesión apareció en `.env` una pareja manual `DATABASE_URL` directa / `DATABASE_URL_POOLED`. No se han sobrescrito esas URLs. El titular no pudo confirmar a qué proyecto/rama pertenecen, por lo que no se aplicaron migraciones ni se escribieron registros de prueba en ellas.

## Resultados y fallos

| Paso | Resultado real |
| --- | --- |
| Instalar CLI | Correcto: `added 161 packages in 45s`; versión 8.13.2 |
| Primer `neon init` | Creó configuración y enlace offline, pero terminó con error al intentar instalar el plugin de GitHub Copilot CLI, que no existe en este equipo. El plugin de Codex sí se instaló |
| Reintento con `--no-agent-setup` | Conservó `neon.ts`; `Written offline (--no-checks): nothing was verified` |
| Autenticación CLI | Sin credenciales en este entorno. El titular inició sesión en otra máquina y después indicó que no podía proporcionar acceso aquí |
| `neon deploy` | No ejecutado: falta autenticación local y no se ha podido comprobar el plan/estado remoto |
| `npm run build` | Correcto: 33 módulos compilados; JS 279,06 kB y CSS 26,73 kB |
| Tests de configuración Django | 7 aprobados sobre SQLite temporal |
| Selección de archivo de entorno | Verificados fallback `.env.local` y prioridad de `.env`, con valores ficticios aislados |
| Arranque local | `npm start -- --noreload`, en `http://127.0.0.1:8000`; el primer intento falló por DNS en el sandbox, el reintento con acceso de red arrancó |
| Conexión directa Neon | `SELECT 1` correcto, TLS activo |
| Conexión pooled Neon | `SELECT 1` correcto, TLS activo |
| Esquema SAP | No se encontraron las cinco tablas SAP/Django comprobadas en `public` |
| HTTP local | Login 200; API anónima 403; health 503 porque falta el esquema |
| Flujo autenticado y persistencia en Neon | Pendientes; no se crearon usuarios ni datos de prueba en un destino incierto |

Salida del build:

```text
> build
> npm --prefix frontend run build
vite v7.3.7 building client environment for production...
✓ 33 modules transformed.
dist/index.html                   0.40 kB │ gzip:  0.28 kB
dist/assets/index-aK7tKlOf.css   26.73 kB │ gzip:  6.72 kB
dist/assets/index-CCWXBMZ1.js   279.06 kB │ gzip: 84.67 kB
✓ built in 2.29s
```

Salida de la comprobación de sólo lectura (exit code **1**, por esquema/health incompletos):

```json
{
  "read_only": true,
  "project_and_branch_verified": false,
  "connections": {
    "direct": {"ok": true, "select_1": true, "tls": true, "sap_tables_found": []},
    "pooled": {"ok": true, "select_1": true, "tls": true, "sap_tables_found": []}
  },
  "http": {"/accounts/login/": 200, "/healthz/": 503, "/api/plans/": 403},
  "read_only_checks_passed": false
}
```

Esto acredita conectividad desde el backend local. **No demuestra que esas URLs pertenezcan al proyecto solicitado, ni constituye una prueba funcional completa o un despliegue público.**

## Cómo completar la configuración

Primero confirmar en [el proyecto de Neon](https://console.neon.tech/app/projects/winter-grass-28484559) la organización, rama `production`, plan **Free** y conexiones de **Connect**. Comparar privadamente el endpoint y la base con `.env`. Si no coinciden, no migrar la base actual. No enviar claves, URLs con contraseña ni capturas de credenciales al chat.

Autenticar el CLI **en la misma máquina Ubuntu que contiene este repositorio**. Un login efectuado en otro equipo no crea credenciales aquí. La vuelta del navegador utiliza `127.0.0.1` del equipo donde corre el CLI; un simple enlace abierto en otra máquina no basta.

```bash
cd ~/projects/Seller-Action-Plan-SAP-
source ~/.nvm/nvm.sh
nvm use 22
neon login
# Terminar el acceso en el navegador y esperar confirmación en la terminal.
neon me
neon init -y --org-id org-rough-thunder-87253091 \
  --project-id winter-grass-28484559 --branch production \
  --services postgres --no-agent-setup
neon config plan
# Revisar que no desactive servicios existentes ni proponga cambios no deseados.
neon deploy
```

`--no-agent-setup` reutiliza el plugin instalado y evita repetir la instalación fallida de Copilot. No activar servicios adicionales ni cambiar a un plan de pago. El `neon.ts` creado conserva el login Django y el resto de servicios sin habilitar. Si el plan muestra cambios sobre servicios ya existentes, revisarlos antes de continuar.

`neon deploy` aplicará la configuración y actualizará sólo variables gestionadas por Neon. La forma canónica para SAP es:

| Variable privada | Uso |
| --- | --- |
| `DATABASE_URL` | URL **pooled** para Django y Vercel, con TLS |
| `DATABASE_URL_UNPOOLED` | URL **directa** de la misma rama/base para migraciones y administración |

La variable manual `DATABASE_URL_POOLED` sólo se reconoce en el diagnóstico para comprobar la pareja existente; Django utiliza `DATABASE_URL`. Si se copian las conexiones manualmente, guardar los dos nombres canónicos anteriores después de confirmar el destino. No construir una URL inventando un hostname.

Aplicar migraciones **cuando el destino esté confirmado**:

```bash
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
npm ci
npm --prefix frontend ci
npm run build
npm run db:migrate -- --plan
npm run db:migrate -- --noinput
npm run db:migrate -- --check
python scripts/neon_manage.py create_demo_agent --username evaluador
# Carga voluntaria, sólo ficticia:
SAP_DEMO_MODE=True python scripts/neon_manage.py seed_evaluation_demo \
  --owner evaluador --confirm-fictitious
npm start
```

`npm start` es el servidor de desarrollo local de Ubuntu, no el runtime productivo. Mantener `DJANGO_DEBUG=True` sólo localmente. En otra terminal, con el venv activo:

```bash
python scripts/check_neon.py
```

Después comprobar el login real, el dashboard y la API con el evaluador; crear un registro ficticio, reiniciar el proceso y consultar el mismo ID. Para aceptación pública seguir [despliegue-vercel.md](despliegue-vercel.md): Vercel sigue siendo el alojamiento de la aplicación y exige `DEBUG=False`, URLs pooled, secretos propios y hosts exactos. No se ha autorizado un push ni desplegado Vercel en esta tarea.
