# SAP en Vercel Hobby + Neon Free

Revisado el **29/10/2026** con documentación oficial. Objetivo: demo académica personal, no comercial y de poco tráfico, **0 € mientras se mantengan estos planes y sus cuotas**. No se ha contratado, publicado ni hecho push. La validación local no acredita un despliegue público.

**Actualización del 03/11/2026:** se reutiliza Neon `empty-feather-02803695`, rama `production` (`br-divine-sky-b9hvdrte`), ya configurada y probada. La revisión actual de solo lectura confirma identidad, pooling, TLS, 33 migraciones registradas y cero usuarios/datos de negocio. No repetir migraciones ni cargar datos como parte de esta revisión. La rama es predeterminada y no tiene caducidad. Ver [Neon](neon-setup.md) y [preparación de publicación](preparacion-publicacion-vercel-2026-11-03.md).

**Dominio:** el titular confirmó en Settings → Domains que `sap-bice.vercel.app` está asignado a Production. La consulta HTTPS del 29/10/2026 devuelve `404`, `server: Vercel`, `x-vercel-error: NOT_FOUND`: la asignación está confirmada por el titular, pero SAP todavía no está accesible. Si se cambia el dominio, sustituirlo en las variables y los comandos de esta guía.

## 1. Configuración elegida

Un proyecto Vercel, preset **Django**, entrada `backend/config/wsgi.py` (`config.wsgi.application`). El [soporte nativo de Django](https://vercel.com/docs/frameworks/full-stack/django) detecta `manage.py`, instala Python y ejecuta `collectstatic`. No se necesitan adaptadores antiguos, carpeta `api/` ni reglas que envíen todas las rutas a un HTML.

`backend/build_vercel.py` instala y compila React con el lockfile y copia `frontend/dist/` a `backend/frontend_dist/`. Django carga su `index.html` como plantilla del dashboard autenticado; sólo `assets/` entra en estáticos. Las plantillas se incluyen explícitamente en la función. El CDN sirve `/static/`; las rutas `/accounts/`, `/dashboard/`, `/admin/` y `/api/` conservan el mismo origen y las sesiones Django. No configurar CORS ni una URL de API externa.

Usuarios, sesiones, bloqueo de login y registros viven en PostgreSQL. Vercel no guarda datos persistentes en disco. No hay subida de archivos en SAP. El build y la importación WSGI **no migran, crean usuarios ni cargan semillas**.

La receta anterior de Render se conserva como antecedente en [despliegue.md](despliegue.md) y `render.yaml`; es de pago y no se utiliza en este procedimiento.

## 2. Ajustes exactos en Vercel

En el proyecto existente → **Settings → Build and Deployment** (algunas opciones pueden aparecer en General):

| Campo | Valor |
| --- | --- |
| Plan de la cuenta/equipo | **Hobby**, sin prueba Pro ni complementos de pago |
| Framework Preset | **Django** |
| Root Directory | **`backend`** |
| Include source files outside of the Root Directory in the Build Step | **Activado**: permite leer `../frontend/` durante el build |
| Build Command | **`python build_vercel.py`**, definido en `backend/vercel.json`; quitar overrides distintos en el panel |
| Output Directory | **Override desactivado / valor predeterminado de Django**. No introducir `dist`, `frontend/dist`, `public` ni `staticfiles` |
| Install Command | **Override desactivado**. El preset instala `backend/requirements.txt`; el script instala Node con `npm ci --include=dev` |
| Node.js Version | **22.x**, al menos 22.12; compatible con Vite y `frontend/package.json` |
| Python | **3.12**, indicado en `backend/.python-version`; comprobar versión en el log |
| Production Branch | **`main`** (confirmar que es la rama que se desea publicar) |
| Function Region | **Frankfurt `fra1`**, fijado en `vercel.json`; una región |
| Fluid Compute | Activado; mantener los valores incluidos en Hobby |
| Duración de la función | **60 segundos**, en `functions["config/wsgi.py"].maxDuration` |
| Ignored Build Step | **`test "$VERCEL_ENV" != production`**, definido en `vercel.json`; sin override contradictorio |
| Automatically expose System Environment Variables | **Activado**: Vercel proporciona `VERCEL=1` y `VERCEL_ENV` |

La inclusión de archivos externos está documentada en [Monorepos FAQ](https://vercel.com/docs/monorepos/monorepo-faq). [Una región se puede elegir en Hobby](https://vercel.com/docs/functions/configuring-functions/region); no se utiliza despliegue multirregión. Las opciones de funciones y de omisión del build están en [vercel.json](https://vercel.com/docs/project-configuration/vercel-json).

No conectar/aplicar `render.yaml`. No ejecutar `scripts/release.sh` como Build Command. No usar Gunicorn como comando de arranque de Vercel: lo gestiona el runtime WSGI nativo.

## 3. Reutilizar el proyecto Neon configurado

1. Seleccionar el proyecto existente `empty-feather-02803695`, organización `org-rough-thunder-87253091`, rama `production`. No crear otro proyecto ni ejecutar `neon deploy` durante una revisión.
2. La base inspeccionada usa **PostgreSQL 18**; la CI actual usa PostgreSQL 16. Registrar ambas versiones y no presentar la CI como una prueba del servidor 18. Para exportar/restaurar, preparar clientes PostgreSQL 18 compatibles; el cliente 14 instalado en este equipo no sirve para exportar un servidor 18.
3. La pareja local canónica ya está en `.env`: `DATABASE_URL` pooled y `DATABASE_URL_UNPOOLED` directa. Se comparó la conexión pooled, sin imprimirla, con la que devuelve el CLI autenticado para el proyecto/rama explícitos.
4. Tras autorizar la configuración externa, transferir privadamente la URL pooled a `DATABASE_URL` **solo de Production** en Vercel. Verificar el destino por metadatos; no pegar valores en Git, el chat ni logs. La directa queda fuera del runtime Vercel.
5. Mantener `neon.ts` y el login Django. La rama predeterminada no recibe el TTL de siete días que la configuración reserva a ramas nuevas no predeterminadas. No se contratan otros servicios.

Copiar los valores de Neon evita errores al codificar caracteres especiales de la contraseña. No quitar `sslmode` ni `channel_binding` si Neon los proporciona. Django exige TLS en producción, usa `CONN_MAX_AGE=0`, timeout de conexión de 5 s y desactiva cursores del servidor para PgBouncer en modo transacción. Una conexión se cierra al finalizar la petición; no se añade un segundo pool local. [Django con Neon](https://neon.com/docs/guides/django), [conexiones serverless](https://neon.com/docs/guides/serverless-connection-pooling).

## 4. Variables de entorno

En Vercel → Settings → Environment Variables, elegir **Production solamente**. Introducir valores sin comillas externas. Son necesarias tanto al construir como al ejecutar: el preset importa Django para descubrir el proyecto. Configurar todas antes de reintentar, para evitar la sucesión de errores de secreto, hosts y base.

| Variable | Requisito | Valor o ejemplo |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Obligatoria y privada | Nueva clave aleatoria de al menos 50 caracteres; distinta de desarrollo/Preview. No usar el texto de ejemplo ni `django-insecure-…` |
| `DJANGO_ALLOWED_HOSTS` | Obligatoria | `sap-bice.vercel.app` |
| `DATABASE_URL` | Obligatoria y privada | URL **pooled real** obtenida de Neon, con TLS |
| `DJANGO_DEBUG` | Fijar explícitamente | `False`; su valor predeterminado también es False y Vercel rechaza True |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Recomendada explícita | `https://sap-bice.vercel.app`; opcional en peticiones estrictamente del mismo origen |
| `SAP_DEMO_MODE` | Opcional | `False`; sólo se activa en la terminal para una carga voluntaria |
| `DJANGO_TRUST_PROXY` | Opcional fuera de Vercel | No definir en Vercel: `VERCEL=1` activa el proxy HTTPS. Localmente False salvo proxy propio fiable |
| `VERCEL` / `VERCEL_ENV` | Automáticas, no secretos | Vercel proporciona `1` y `production`/`preview`; no copiarlas al `.env` local |

`ALLOWED_HOSTS` admite dominios exactos separados por comas; CSRF, orígenes HTTPS exactos. No añadir `*`, `.vercel.app` ni `https://*.vercel.app`. Los aliases de despliegue no quedan permitidos automáticamente: navegar por el dominio canónico. Si se necesita otro alias, añadir sólo ese host y su origen.

`SECURE_PROXY_SSL_HEADER` reconoce `X-Forwarded-Proto` de Vercel. Se mantiene la validación del `Host`, sin confiar en `X-Forwarded-Host`, junto con HTTPS, HSTS, cookies Secure/HttpOnly/SameSite y CSRF. Los intentos de login se limitan por usuario en PostgreSQL. [Cabeceras de Vercel](https://vercel.com/docs/headers/request-headers).

No subir `.env`, bases SQLite, dumps ni claves. No utilizar prefijos `VITE_` para secretos: los expone el bundle. No cambiar la clave de Django en cada build: debe mantenerse entre despliegues para conservar sesiones.

## 5. Production y Preview separados

La configuración actual omite los builds Git de Preview: el `ignoreCommand` devuelve 0 para omitirlos y 1 para construir Production. No asignar credenciales productivas a “All Environments”. Tampoco copiar un despliegue Preview a Production como sustituto de configurar correctamente los entornos.

Si más adelante se necesita Preview:

1. Crear **otro proyecto Neon Free vacío**, por ejemplo `sap-tfg-preview`, con credenciales diferentes y sólo datos ficticios. Así se evita clonar por defecto los usuarios, sesiones y datos de Production.
2. Configurar variables **sólo Preview**, con otra clave Django, su propia `DATABASE_URL`, `DJANGO_DEBUG=False` y hosts/orígenes HTTPS exactos. Utilizar un alias estable de esa rama, confirmado en Vercel; los hosts aleatorios no están permitidos por defecto.
3. Migrar esa base explícitamente desde Ubuntu y, si se desea, crear su demo por separado.
4. Quitar `ignoreCommand` del JSON para habilitar Preview y revisar que no exista un override de omisión en el panel. Conservar las variables de Production intactas.
5. Usar la protección de previews incluida con Vercel Authentication si se desea; no depender de Password Protection de pago.

El comando de omisión no es una barrera de seguridad para despliegues manuales: la separación de variables y bases es obligatoria. Incluso en Preview, Django falla si faltan secreto, hosts o PostgreSQL. No usar SQLite ni habilitar DEBUG para hacer pasar un build.

## 6. Ubuntu: dependencias, migraciones y usuario

Abrir una terminal **Bash** para seguir los ejemplos (`bash` si normalmente se usa zsh). Desde la raíz del repositorio:

```bash
cd ~/projects/Seller-Action-Plan-SAP-
python3 --version
# Se necesita Python 3.10 o superior para Django 5.2; producción usa 3.12.
# En Ubuntu 24.04, si faltan Python/venv:
sudo apt update
sudo apt install python3 python3-venv
# Crear sólo si todavía no existe el entorno:
test -d .venv || python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m pip check
```

Para compilar, si ya tienes nvm instalado (como en este equipo):

```bash
source ~/.nvm/nvm.sh
nvm install 22
nvm use 22
node --version
npm --prefix frontend ci
npm --prefix frontend test
npm --prefix frontend run build
```

Si no tienes nvm, seguir su [instalación oficial](https://github.com/nvm-sh/nvm#installing-and-updating) y abrir otra terminal antes de estos comandos. No instalar Node 20 antiguo desde `apt` para este Vite.

El `.env` actual apunta a Neon `production` para las verificaciones autorizadas. Para desarrollar sin tocar esa base, usar otro entorno local explícito (por ejemplo SQLite mediante una variable de proceso vacía); no sobrescribir el archivo actual ni ejecutar semillas/pruebas de escritura contra Production por defecto. `python scripts/configure_env.py` crea `.env` solo si no existe.

Para **administrar Neon**, usar una subshell: al terminar con `exit`, desaparecen las variables productivas y se recupera el entorno local. No usar `set -x` ni pegar secretos en comandos que queden en el historial.

```bash
bash
source .venv/bin/activate
unset VERCEL VERCEL_ENV RENDER_EXTERNAL_HOSTNAME
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS=sap-bice.vercel.app
export DJANGO_CSRF_TRUSTED_ORIGINS=https://sap-bice.vercel.app
export DJANGO_TRUST_PROXY=False
export SAP_DEMO_MODE=False

# Copiar privadamente la clave de Production ya configurada en Vercel:
read -rsp 'DJANGO_SECRET_KEY de Production: ' DJANGO_SECRET_KEY; echo
export DJANGO_SECRET_KEY
# Pegar aquí la URL DIRECTA de Neon, nunca la de otra base:
read -rsp 'URL directa de Neon (migraciones): ' DATABASE_URL; echo
export DATABASE_URL

python backend/manage.py check --deploy --fail-level WARNING
# Consulta del estado; no aplica migraciones:
python backend/manage.py showmigrations --plan
# Este destino ya registra las 33 migraciones. No repetir migrate.
# Solo después de autorizar el alta ficticia y confirmar de nuevo la base:
python backend/manage.py create_demo_agent --username evaluador
```

`create_demo_agent` pide la contraseña sin mostrarla, la valida y crea un agente con permisos funcionales, sin acceso administrativo. Rechaza sobrescribir usuarios existentes. Para cambiar una contraseña usar `python backend/manage.py changepassword evaluador`; no recrear cuentas. Un superusuario sólo si hace falta: `python backend/manage.py createsuperuser` (no entregarlo al tribunal).

Si aún no tienes clave productiva, generarla **en tu terminal privada**, antes de configurar Vercel, con `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`. Copiarla al gestor de secretos y a Production; no enviar su salida, capturarla ni versionarla.

Carga **opcional**, exclusivamente ficticia, desde la misma subshell y después de crear el agente:

```bash
SAP_DEMO_MODE=True python backend/manage.py seed_evaluation_demo \
  --owner evaluador --confirm-fictitious
# Segundo agente vacío para comprobar aislamiento:
python backend/manage.py create_demo_agent --username otro_agente
exit
```

Sin esa carga, la aplicación empieza vacía. La semilla conserva los registros existentes y no restaura modificaciones del evaluador. Compartir las credenciales sólo por el canal privado académico. No ejecutar `manage.py test` contra Production: las pruebas usan bases desechables y se ejecutan localmente/CI.

Las actualizaciones siguen el mismo procedimiento de migraciones **una vez por release**, nunca por petición, importación o build. Revisar compatibilidad de esquema con la versión en servicio y guardar una copia privada antes de cambios. Los comandos de mantenimiento `clearsessions` o `axes_reset_username` también se ejecutan desde esta terminal con la URL directa cuando sean necesarios.

## 7. Redesplegar y aceptar la demo

Estos pasos los realizará el titular **cuando autorice la publicación**. Este trabajo no hace push ni despliega.

1. Revisar el diff y guardar/publicar el código autorizado. Corregir la integración Git al repo ID `1430152684`, como detalla la revisión actual. Un push a una rama conectada puede disparar Vercel automáticamente: coordinarlo con la aprobación de CI y la configuración de variables. El esquema actual ya está aplicado; no repetir migraciones por rutina.
2. Guardar los ajustes autorizados. Crear un deployment Production desde el SHA final exacto: si todavía no existe un deployment de ese SHA, publicarlo mediante la integración Git configurada; si existe, revisar su SHA antes de usar Redeploy. Un Redeploy conserva la fuente del deployment elegido y no incorpora cambios locales ni el nuevo HEAD por sí solo. Para la primera comprobación desactivar “Use existing Build Cache”.
3. Revisar el log: Python 3.12, instalación de requirements, `npm ci`, `vite build`, comprobación Django y `collectstatic`. Debe terminar sin migraciones, semillas ni errores de variables. Comprobar `sap-bice.vercel.app` como dominio de Production.
4. Abrir `https://sap-bice.vercel.app/accounts/login/` y entrar con el agente. El destino debe ser `/dashboard/`; revisar CSS/JS, vendedores, planes y `/api/workspace/` con la sesión. Sin sesión, dashboard redirige al login y la API devuelve 403. Un agente sin asignaciones no debe ver registros ajenos (404 al pedir su detalle).
5. Comprobar `/healthz/` → `200 {"status":"ok"}`, HTTP → HTTPS, ausencia de bucles y cookies seguras. Logout es POST y requiere CSRF. Un POST sin token o desde un origen ajeno debe devolver 403. Un host ajeno debe ser rechazado por Vercel o Django, sin servir SAP.
6. Crear un **plan ficticio nuevo**, anotar su ID y un texto único, añadir acción/revisión y guardar. Volver a entrar para confirmar que se lee desde API y dashboard.
7. Hacer otro **Redeploy de Production**, con la misma base y clave y sin volver a cargar demo. Abrir el **mismo ID** y comprobar título, acciones y revisiones. Ese paso acredita persistencia entre despliegues. Revisar también que el otro agente sigue sin poder acceder.
8. Registrar fecha, URL, commit, ID ficticio y resultados en [verificacion-publica.md](verificacion-publica.md), sin contraseñas. Sólo entonces marcar el despliegue público como verificado.

Comprobaciones sin credenciales:

```bash
curl -I http://sap-bice.vercel.app/accounts/login/
curl -I https://sap-bice.vercel.app/accounts/login/
curl --fail-with-body https://sap-bice.vercel.app/healthz/
curl -i https://sap-bice.vercel.app/api/plans/
```

El recorrido automatizado existente usa Playwright/Chromium en un entorno de QA, solicita las contraseñas y **escribe datos ficticios**. Ejecutarlo sólo cuando se autoricen esas escrituras y esté cargada la demo:

```bash
python scripts/verify_browser.py --url https://sap-bice.vercel.app \
  --username evaluador --other-username otro_agente \
  --seller-reference SAP-DEMO-PLAN --allow-writes
```

Ese script valida login, React, API, permisos, CSRF, acciones y cierre, pero **no redespliega Vercel**: completar manualmente los pasos 6–8. Instalar Playwright sólo en QA según el README; no añadirlo al runtime productivo.

## 8. Límites gratuitos y preparación de la defensa

Valores consultados el 29/10/2026, sujetos a cambios del proveedor. Confirmar **Free/Hobby** y las cuotas en los paneles antes de la defensa; no aceptar upgrades al agotarlas.

| Proveedor / límite | Consecuencia para SAP |
| --- | --- |
| Vercel Hobby: uso personal no comercial | Adecuado para esta demostración académica independiente. Revisar plan si pasa a uso comercial |
| Vercel: 4 horas de CPU activa, 360 GB-h de memoria provisionada y 1 millón de invocaciones | Evitar pruebas de carga y procesos continuos; son cuotas compartidas de la cuenta/equipo |
| Vercel: 100 GB de transferencia rápida, 10 GB desde origen y 1 millón de peticiones CDN | Los assets de React se sirven por CDN; controlar Usage |
| Vercel: 100 despliegues/día; máximo Hobby de 300 s por función | SAP fija 60 s; migraciones y trabajo prolongado se ejecutan desde Ubuntu |
| Neon Free: 100 CU-h/mes por proyecto; hasta 2 CU | Preferir cómputo pequeño; 0,25 CU durante 4 h consume 1 CU-h |
| Neon: 1 GB PostgreSQL/proyecto, 20 GB total entre proyectos Free; 5 GB de salida/mes/proyecto | Demo pequeña y ficticia; vigilar almacenamiento y transferencia |
| Neon: suspensión tras 5 min de inactividad, obligatoria en Free | Primer acceso puede tardar más. Abrir la demo poco antes de exponer; no mantenerla despierta con pings continuos |
| Neon: 100 proyectos, 10 ramas/proyecto | Sobra para Production y un proyecto Preview separado; no crear ramas por cada commit |
| Neon Free: restauración instantánea limitada a 6 h y tamaño de cambios; sin backups programados | No prometer recuperación de varios días; guardar una exportación privada antes de cambios relevantes |

Vercel puede pausar funciones al exceder cuotas, normalmente hasta que pasen 30 días. Neon suspende cómputo al agotar CU-h o transferencia hasta el siguiente periodo; al superar espacio fallan operaciones que aumentan almacenamiento. La cuota no equivale a disponibilidad garantizada. Mantener ambos planes gratuitos evita contratar consumo adicional; una pausa puede impedir la defensa. [Vercel Hobby](https://vercel.com/docs/plans/hobby), [Neon Pricing](https://neon.com/pricing), [límites y consecuencias de Neon Free](https://neon.com/docs/introduction/plans).

No hacen falta dominio comprado, Redis, almacenamiento de archivos, IP dedicada, failover, monitor de pago, cron ni funciones beta. No activar un monitor que consulte SQL cada minuto: impediría que Neon duerma y consumiría la cuota. Preparar también una demo local y capturas para contingencias de red o disponibilidad. Las copias deben ir a almacenamiento privado fuera del disco efímero de Vercel. Para esta base PostgreSQL 18, preparar `pg_dump`/`pg_restore` 18, exportar por conexión directa y restaurar únicamente en una base aislada autorizada. Comparar migraciones, conteos e IDs de control antes de eliminar el entorno de restauración. No ejecutar estos pasos durante una revisión de solo lectura.

## 9. Validación local y estado pendiente

Comprobaciones reproducibles, sin desplegar:

```bash
source .venv/bin/activate
nvm use 22
python scripts/verify_vercel.py
DJANGO_DEBUG=True DATABASE_URL= python backend/manage.py test config sellers quality action_plans
python scripts/check_production.py
```

`verify_vercel.py` compila y copia el backend a un directorio temporal sin `frontend/`, `.env` ni SQLite. Con una URL PostgreSQL ficticia inaccesible verifica WSGI, seguridad, plantillas, rutas y archivos estáticos; demuestra que no requiere SQL al importar ni durante el build. **No invoca el builder remoto de Vercel ni acredita su CDN.** La CI incorpora esta comprobación junto con las pruebas existentes SQLite/PostgreSQL.

Para QA real de PostgreSQL aislado y navegador, con las herramientas del README disponibles:

```bash
python3 scripts/verify_phase3.py --pg-bin /usr/lib/postgresql/14/bin \
  --vercel-settings --artifacts artifacts/vercel-postgres
```

Este script crea una base temporal, usa TLS local, migra, verifica permisos y flujo de navegador, reinicios y restauración; no toca Neon ni los datos del usuario. Con `--vercel-settings`, el recorrido de producción usa `VERCEL=1` y los assets empaquetados. La suite de tests conserva su configuración de pruebas habitual. El PostgreSQL 14 local no sustituye a comprobar Neon y su pool. Resultados de esta adaptación: [verificacion-vercel.md](verificacion-vercel.md).

Neon y las 33 migraciones están preparados. La revisión del 03/11/2026 ya inspeccionó Vercel y confirmó Hobby activo; encontró una integración Git con otro repo ID y un alias sobre un build sin salida Django. Quedan pendientes: corregir esa integración y guardar las variables Production tras autorización, crear las cuentas/datos ficticios autorizados, versionar los cambios posteriores a `160fc4c`, aprobar la CI de ese nuevo SHA, publicar ese SHA y completar el recorrido público, persistencia tras redespliegue y restauración aislada. No guardar credenciales en el informe. La aprobación de CI de `160fc4c` no cubre archivos locales posteriores.
