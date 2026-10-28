# Seller Action Plan (SAP)

Aplicación web para documentar y seguir planes de mejora de vendedores de marketplace a partir de indicadores de calidad. Proyecto Final del Máster en Desarrollo Full Stack de ConquerBlocks.

**Estado: Fase 4 preparada localmente; entrega oficial pendiente de URL pública, vídeo y confirmación académica.** Consulta el [informe actual](docs/fase-4.md), la [memoria PDF](docs/memoria-pfm.pdf) y la [matriz de cumplimiento](docs/trazabilidad-requisitos.md).

Dashboard operativo, vendedores con búsqueda y ficha individual, planes con varios indicadores, acciones, revisiones y cierre desde React integrado con Django. Los informes de [Fase 1](docs/fase-1.md), [Fase 2](docs/fase-2.md) y [Fase 3](docs/fase-3.md) conservan las decisiones y evidencias históricas. El [procedimiento operativo](docs/despliegue.md) prepara la publicación; todavía no existe un despliegue público verificado.

Proyecto académico independiente: no es una aplicación oficial de PcComponentes ni de Mirakl. SAP no suspende tiendas, no bloquea pagos ni tramita reaperturas. Se utilizan exclusivamente datos ficticios y reproducibles.

## Índice

- [Problema que resuelve](#problema-que-resuelve)
- [Solución propuesta](#solución-propuesta)
- [Objetivos](#objetivos)
- [Funcionalidades y estado](#funcionalidades-y-estado)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Estructura](#estructura)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Variables de entorno](#variables-de-entorno)
- [Base de datos](#base-de-datos)
- [Ejecución local](#ejecución-local)
- [API](#api)
- [Usuarios y permisos](#usuarios-y-permisos)
- [Seguridad](#seguridad)
- [Testing](#testing)
- [Despliegue](#despliegue)
- [Roadmap](#roadmap)
- [Demo y documentación académica](#demo-y-documentación-académica)
- [Cumplimiento académico](#cumplimiento-académico)
- [Referencias](#referencias)
- [Autoría y licencia](#autoría-y-licencia)

## Problema que resuelve

Las plataformas de marketplace permiten consultar indicadores operativos, pero el análisis de causas, las responsabilidades y la revisión de compromisos requieren seguimiento estructurado. La información dispersa dificulta comprobar qué se hizo y si mejoraron los resultados.

## Solución propuesta

SAP propone complementar estos sistemas con un registro de indicadores, planes correctivos y preventivos, acciones con responsables y revisiones históricas. Sus usuarios principales son agentes de Marketplace Support, account managers y administradores. No requiere una cuenta para cada vendedor en el MVP: la operativa inicial es interna y cada agente accede a sus vendedores asignados.

## Objetivos

**Objetivo general:** construir una herramienta que permita relacionar las desviaciones de calidad de un vendedor con acciones de mejora y resultados verificables.

| Objetivo medible | Evidencia prevista o disponible |
| --- | --- |
| Evaluar los cinco criterios MQC con sus límites exactos | Servicio de clasificación y pruebas de fronteras implementados |
| Restringir cada agente a sus vendedores | Consultas filtradas y pruebas de acceso implementadas |
| Mostrar datos persistidos en Django y React | Plantillas HTML y dashboard, vendedores y planes en React implementados |
| Vincular cada plan con responsables, acciones y revisión | Implementado en React y Django Admin; demo 6% → 4,5% → 3% y pruebas del flujo completo |
| Reproducir la instalación y demostrar el flujo completo | Dependencias fijadas y memoria PDF preparada; vídeo y URL pública pendientes |

## Funcionalidades y estado

| Estado | Funcionalidades |
| --- | --- |
| Implementado | Login/logout, grupos, vendedores asignados, API y React de vendedores/indicadores, políticas versionadas, clasificación informativa, planes con varios indicadores, acciones, revisiones históricas, cierre autorizado y dos demos idempotentes, migraciones y pruebas |
| Fase 3 | PostgreSQL probado localmente, concurrencia, seguridad, Gunicorn, receta Render y QA de producción; publicación y backups remotos pendientes; CI de Fase 3 verificada |
| Fase 2 | Dashboard con datos persistidos, fichas de vendedores, búsqueda y paginación, API de planes, formularios React, acciones, revisiones y cierre autorizado |
| Previsto | Trazabilidad general de cambios y validación de producción |

Las métricas son observaciones registradas, **no cálculos sobre pedidos importados**. La interfaz indica su canal y periodo; una observación histórica no representa automáticamente la situación actual. Las reglas y el tratamiento del periodo se explican en [dominio](docs/dominio.md).

## Tecnologías

Versiones del repositorio auditado el 28/10/2026:

| Tecnología | Versión | Función y justificación |
| --- | --- | --- |
| Python | 3.12.4 verificada | Runtime disponible; para nuevas instalaciones, usar el último parche de Python 3.12 |
| Django | 5.2.18 LTS | Backend académico, ORM, plantillas, autenticación, validación y tests |
| Django REST Framework | 3.18.3 | Serialización, permisos y API paginada |
| django-environ | 0.14.0 | Lectura de `.env` y configuración de la URL de base de datos |
| React / React DOM | 19.3.1 | Interfaz operativa que consulta y escribe en Django mediante Fetch |
| Vite | 7.3.7 | Desarrollo y compilación; rama mantenida, compatible con npm disponible |
| @vitejs/plugin-react | 5.2.0 | Soporte JSX y actualización durante el desarrollo |
| SQLite | Incluida en Python | Base local sin servicios adicionales |
| PostgreSQL / psycopg | PostgreSQL 14.24 local; 16 propuesto para Render / driver 3.3.6 | Persistencia y bloqueos reales; instancia remota pendiente |
| WhiteNoise | 6.12.0 | Estáticos Django y React compilados bajo el mismo origen |
| Gunicorn | 26.2.0 | Servidor WSGI de producción, dos workers |
| django-axes | 8.3.1 | Bloqueo persistente de intentos de login |
| tzdata | 2026.5 | Zona horaria disponible también en Windows |
| unittest Django / node:test | Incluidos | Pruebas sin instalar otro framework |

`backend/requirements.txt` fija también las dependencias transitivas. `requirements.in` documenta los rangos de actualización; no sustituye al archivo fijado. npm es el único gestor JavaScript y `package-lock.json` debe conservarse.

Django 5.2 es compatible con Python 3.12. Vite 7.3 sigue recibiendo correcciones importantes y de seguridad según su [política de soporte](https://vite.dev/releases). npm 10.8.2 falló internamente resolviendo dependencias opcionales de Vite 8; se eligió una combinación mantenida que permite la instalación normal, sin omitir la validación de pares.

## Arquitectura

```mermaid
flowchart LR
    U[Usuario autenticado] --> H[Vista HTML Django]
    U --> R[React: dashboard, vendedores y planes]
    R -->|Fetch y cookie de sesión| API[API REST Django]
    H --> ORM[ORM Django]
    API --> P[Rol y vendedores asignados]
    P --> ORM
    ORM --> DB[(SQLite local / PostgreSQL producción)]
    API --> C[Clasificación según política versionada]
```

Django es el backend principal y gestiona sesiones, permisos y persistencia. En desarrollo Vite reenvía `/api/` y `/accounts/` a Django conservando el origen del navegador. En la compilación integrada, Django entrega `/dashboard/` y los archivos React se sirven bajo `/static/react/`. No se necesita habilitar CORS.

Se conserva `auth.User` de Django. `Seller.owner` representa la asignación inicial a un agente; `QualityMetric` almacena un indicador por vendedor, política, canal y periodo. `ThresholdPolicy` permite nuevas versiones de umbrales sin reescribir el clasificador. La app `action_plans` añade planes, acciones, objetivos vinculados a observaciones iniciales y revisiones. Consulta la [arquitectura](docs/arquitectura.md) y las [decisiones de la Fase 1](docs/fase-1.md).

## Estructura

```text
.
├── backend/
│   ├── config/              # Ajustes, rutas, vistas HTML y WSGI
│   ├── sellers/             # Vendedores, acceso, API y comando seed_demo
│   ├── quality/             # Indicadores, políticas, clasificador y API
│   ├── action_plans/        # Planes, acciones, objetivos, revisiones, servicios y Admin
│   ├── templates/           # Portal y formulario de acceso Django
│   ├── manage.py
│   ├── requirements.in
│   ├── requirements.txt
│   └── gunicorn.conf.py     # Arranque WSGI de producción
├── frontend/
│   ├── src/services/        # Fetch paginado y pruebas
│   ├── src/main.jsx         # Navegación integrada
│   ├── src/components/      # Formularios, estados, tablas y peticiones
│   ├── src/pages/           # Dashboard, vendedores y ciclo de planes
│   ├── src/styles.css
│   ├── vite.config.js
│   ├── package.json
│   └── package-lock.json
├── docs/                    # Dominio, arquitectura, PFM y verificación
├── scripts/                 # Configuración local y check de producción ficticia
├── .github/workflows/ci.yml
├── render.yaml              # Propuesta revisable con coste; no aplicada
├── .env.example
├── .gitignore
└── LICENSE
```

`.venv/`, `.env`, `backend/db.sqlite3`, `frontend/node_modules/`, `frontend/dist/` y `backend/staticfiles/` se generan localmente y no se versionan.

## Requisitos previos

- Git y Python 3.12 con `venv` y pip. Versión comprobada: Python 3.12.4, pip 24.2 inicial.
- Node.js **22.12+ LTS o 24 LTS recomendado** y npm. Se verificaron Node 20.20.2 / npm 10.8.2 y Node 22.19.0 ya instalado. `.nvmrc` selecciona la rama 22 para quien use nvm. Usar el último parche mantenido: Node 20 está fuera de soporte y no debe elegirse para producción. [Calendario oficial](https://nodejs.org/en/about/previous-releases).
- Un navegador moderno. PostgreSQL no es necesario para el arranque local.

No se requiere instalar herramientas globales, Docker, Redis ni una API de Mirakl. Los comandos siguientes parten de una terminal normal y crean un entorno Python local al repositorio.

## Instalación

### Linux / macOS

```bash
git clone https://github.com/Pablorossl/Seller-Action-Plan-SAP-.git
cd Seller-Action-Plan-SAP-
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python scripts/configure_env.py
cd frontend
npm ci
cd ..
```

En Debian/Ubuntu, si falta `venv`, instala el paquete correspondiente a tu Python con el gestor del sistema antes de continuar. En macOS, `python3` debe corresponder a Python 3.12.

### Windows PowerShell

```powershell
git clone https://github.com/Pablorossl/Seller-Action-Plan-SAP-.git
Set-Location Seller-Action-Plan-SAP-
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python scripts/configure_env.py
Set-Location frontend
npm ci
Set-Location ..
```

Si PowerShell no permite activar scripts, utiliza directamente `.\.venv\Scripts\python.exe` en lugar de `python` en los comandos posteriores; no es necesario cambiar la política global del equipo.

El script crea `.env` desde `.env.example`, genera una clave aleatoria sin mostrarla y conserva un `.env` ya existente. Como alternativa, copia el ejemplo (`cp .env.example .env` o `Copy-Item .env.example .env`) y asigna una clave generada con `python -c "import secrets; print(secrets.token_urlsafe(64))"`. No dejes la clave vacía.

## Variables de entorno

Django lee exclusivamente `.env` en la raíz, además de las variables del proceso, que tienen prioridad. Ninguna variable de secreto debe exponerse mediante `VITE_*`.

| Variable | Desarrollo | Producción |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Clave aleatoria generada localmente; mínimo 50 caracteres | Nueva clave privada, distinta por entorno |
| `DJANGO_DEBUG` | `True` | `False`; valor predeterminado si se omite |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Dominios reales sin esquema, separados por comas; evitar `*` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | Orígenes HTTPS exactos; nunca comodines generales |
| `DATABASE_URL` | Vacía: `backend/db.sqlite3` | URL PostgreSQL privada; p. ej. `postgresql://usuario:CLAVE@host:5432/sap?sslmode=require` |
| `DJANGO_TRUST_PROXY` | `False` | `True` solamente si el proxy confiable reescribe `X-Forwarded-Proto` |
| `RENDER_EXTERNAL_HOSTNAME` | No necesario | Render lo proporciona; host y origen HTTPS exactos |
| `SAP_DEMO_MODE` | `False` | `True` sólo para la carga ficticia explícita; después `False` |
| `WEB_CONCURRENCY` / `PORT` | No necesarios para runserver | Dos workers por defecto / puerto asignado por proveedor |

Producción rechaza SQLite, requiere clave y activa cookies seguras, redirección HTTPS y HSTS. La verificación estática con valores ficticios no prueba la disponibilidad del servicio de base de datos.

## Base de datos

Con el entorno virtual activo, desde la raíz:

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo --owner TU_USUARIO
```

Sustituye `TU_USUARIO` por el nombre que acabas de crear. La contraseña se introduce interactivamente y nunca se incluye en el repositorio. `seed_demo` añade el grupo `Marketplace Agent` al usuario indicado y crea **dos vendedores, siete políticas y catorce observaciones** ficticias de septiembre de 2026. Puede repetirse sin duplicar datos; no reasigna una demo de otro usuario. Solo funciona con `DEBUG=True` y no crea contraseñas ni usuarios.

Para probar un agente sin privilegios globales, crea un usuario desde `/admin/`, sin `is_staff` ni `is_superuser`, asígnale el grupo `Marketplace Agent` y selecciona ese usuario como `owner` de sus vendedores. El grupo puede crearse desde el administrador si no se cargó la demo.

En cambios futuros de modelos:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py makemigrations --check --dry-run
```

Revisa y versiona las migraciones junto al cambio. `PROTECT` impide borrar propietarios, vendedores, políticas o registros de planes todavía referenciados. La API devuelve `409` al intentar borrar un vendedor con histórico.

Para habilitar la gestión de planes a un usuario existente, desde `backend/`:

```bash
python manage.py configure_plan_agent --username TU_USUARIO
python manage.py seed_plan_demo --owner TU_USUARIO
```

El primer comando habilita `is_staff`, añade el grupo de agente y permisos individuales del módulo. No concede acceso administrativo a vendedores, políticas ni usuarios. Con `--interface-only` conserva `is_staff` y habilita sólo los permisos funcionales; para una cuenta nueva sin Admin usa `python manage.py create_demo_agent --username evaluador`. El segundo carga, solo en desarrollo, un vendedor ficticio adicional con el caso completo **6% → 4,5% → 3%**, dos acciones y cierre. Puede repetirse sin modificar el histórico. Para gestionar desde React, entra en `/dashboard/` después de compilar. El permiso `is_staff` solo es necesario para Admin; la [guía de Fase 1](docs/fase-1.md) explica también cómo crear el recorrido manualmente.

## Ejecución local

**Terminal 1**, entorno virtual activo, directorio `backend/`:

```bash
python manage.py runserver 127.0.0.1:8000
```

**Terminal 2**, directorio `frontend/`:

```bash
npm run dev
```

| URL | Uso |
| --- | --- |
| `http://127.0.0.1:8000/` | Portal HTML Django, acceso y vendedores persistidos |
| `http://127.0.0.1:8000/dashboard/` | Aplicación operativa de la Fase 2; requiere `npm run build` |
| `http://127.0.0.1:8000/admin/` | Administración; requiere usuario autorizado |
| `http://127.0.0.1:5173/static/react/` | React en desarrollo; usa su enlace «Iniciar sesión» |
| `http://127.0.0.1:8000/api/sellers/` | JSON de los vendedores accesibles para la sesión |

Utiliza `127.0.0.1` de forma consistente: `localhost` y `127.0.0.1` mantienen cookies distintas. Accede desde el enlace del propio frontend para establecer su sesión mediante el proxy.

Para verificar el frontend compilado bajo Django:

```bash
# Desde la raíz, con el entorno virtual activo
npm --prefix frontend run build
cd backend
python manage.py collectstatic --noinput
python manage.py runserver 127.0.0.1:8000
```

Abre `http://127.0.0.1:8000/dashboard/` e inicia sesión. Si compilaste después de arrancar Django, reinicia el servidor para que detecte `frontend/dist/`. `npm run preview` es solo una previsualización de archivos estáticos y no incorpora el proxy de desarrollo ni sustituye al flujo integrado.

## API

Autenticación por **cookie de sesión Django**, sin JWT ni Basic Auth. Se requiere superusuario o grupo `Marketplace Agent`. Las respuestas paginadas incluyen `count`, `next`, `previous` y `results`: 50 registros para vendedores/observaciones y 20 para planes/responsables. React solicita solo la página necesaria.

| Endpoint | Métodos | Comportamiento |
| --- | --- | --- |
| `/api/` | GET | Índice de endpoints, con rol autorizado |
| `/api/sellers/` | GET, POST | Lista accesible; búsqueda `search`, filtro `active_plans=1/0`, paginación y número de planes abiertos; crea vendedor asignado al usuario |
| `/api/sellers/{id}/` | GET, PUT, PATCH, DELETE | Solo vendedor accesible; no permite reasignar `owner` |
| `/api/metrics/` | GET | Observaciones accesibles; filtros `seller` y `latest=1`, con clasificación del backend |
| `/api/metrics/{id}/` | GET | Detalle de observación accesible |
| `/api/workspace/` | GET | Sesión, capacidades y token CSRF |
| `/api/overview/` | GET | Resumen operativo, prioridades y revisiones |
| `/api/responsibles/` | GET | Responsables autorizados, búsqueda y paginación |
| `/api/plans/` | GET, POST | Lista paginada y creación atómica con varios indicadores |
| `/api/plans/{id}/` | GET, PATCH | Detalle, evaluación y edición autorizada |
| `/api/plans/{id}/actions/` | POST | Crear una acción |
| `/api/plans/{id}/actions/{action_id}/` | PATCH | Editar acción, estado, finalización y evidencias |
| `/api/plans/{id}/metrics/` | POST | Añadir un indicador a un plan abierto |
| `/api/plans/{id}/metrics/{metric_id}/` | PATCH | Editar el objetivo mientras el dominio lo permita |
| `/api/plans/{id}/reviews/` | POST | Registrar una revisión histórica |
| `/api/plans/{id}/close/` | POST | Finalización con razones, permiso específico y `confirm: true` |
| `/accounts/login/` | GET, POST | Formulario HTML y creación de sesión; POST con CSRF |
| `/accounts/logout/` | POST | Cierre de sesión con CSRF |
| `/healthz/` | GET, HEAD | Disponibilidad SQL; 200 o 503 sin datos privados |

POST de vendedor, con sesión y token CSRF válidos:

```json
{"name": "Tienda Ficticia", "reference": "FICTICIA-003"}
```

Las escrituras autenticadas necesitan `X-CSRFToken` o el campo de formulario `csrfmiddlewaretoken`. Las políticas y las observaciones iniciales siguen registrándose por un superusuario. La Fase 2 añade la API de planes, acciones, objetivos y revisiones con los permisos existentes y aislamiento por vendedor. La autoría la impone el servidor; las revisiones y los planes finalizados conservan su histórico.

Para editar planes, objetivos y acciones o cerrar un plan, React envía la `revision` recibida: una revisión obsoleta devuelve `409` y requiere recargar. Los clientes anteriores sin revisión conservan escrituras serializadas, pero no detectan formularios obsoletos. En POST de planes/acciones, `Idempotency-Key` (UUID) permite repetir los mismos datos: devuelve el plan existente y no crea otro registro; reutilizar la clave con datos distintos da `409`. Sin clave, cada POST es una nueva creación. Las revisiones se deduplican por objetivo y periodo.

Clasificaciones: `ok`, `alarm`, `suspension_threshold`, `insufficient_orders`, `not_evaluable` y `below_reference`. MQC exige una ventana mensual y volumen conocido suficiente; el detalle de la convención de periodos está en [dominio](docs/dominio.md). `suspension_threshold` significa exclusivamente que la observación alcanza el umbral informativo: SAP no ejecuta suspensiones. Sin sesión o rol se devuelve `403`; un recurso ajeno se oculta con `404`; errores de validación producen `400`; métodos no implementados, `405`.

## Usuarios y permisos

| Rol | Capacidades actuales |
| --- | --- |
| Administrador (`is_superuser`) | Todos los vendedores e indicadores; usuarios, grupos, asignaciones y políticas mediante Django Admin |
| Marketplace Agent (incluye uso por Account Manager) | CRUD de vendedores propios y lectura de indicadores; gestión React de planes con permisos explícitos; Admin solo si además tiene `is_staff` |
| Autenticado sin rol | Sin acceso a la API de dominio; portal sin vendedores |
| Anónimo | Formulario de acceso; sin acceso a datos |

El filtrado del queryset se aplica tanto al listado como al detalle y a las escrituras. No se confía en ocultar botones para autorizar. Conceder `is_staff` por sí solo no otorga acceso a planes: se exige también grupo y permisos Django. La administración de vendedores, indicadores y políticas sigue reservada al superusuario.

Casos de uso disponibles:

| Actor | Caso de uso | Resultado |
| --- | --- | --- |
| Usuario | Iniciar sesión y abrir el portal Django | Consulta únicamente los vendedores permitidos por su rol |
| Agente | Crear o editar un vendedor mediante API | Registro persistido y asignado al agente autenticado |
| Administrador | Registrar indicadores y políticas desde Admin | Observaciones vinculadas al vendedor, canal, periodo y versión |
| Agente | Abrir las secciones React | Consulta de vendedores e indicadores reales con clasificación informativa |

El agente habilitado puede crear planes propios, añadir objetivos y acciones, registrar revisiones y finalizar el plan documentando el resultado. El cierre exige un permiso específico; el histórico no se edita ni se elimina desde Admin. [Recorrido completo y decisiones](docs/fase-1.md).

## Seguridad

Sesiones persistidas, CSRF en login/logout y escrituras, permisos por vendedor y operación, ORM y escape de HTML, FK protegidas, histórico inmutable y transacciones. React valida los formularios y Django vuelve a validar cada escritura. La Fase 3 añade bloqueo persistente de login (cinco fallos, quince minutos), revisiones para detectar ediciones obsoletas y claves idempotentes para crear planes/acciones sin duplicarlos al reintentar.

Con `DEBUG=False` se exige clave privada, hosts exactos y PostgreSQL con TLS; se activan cookies Secure, HSTS, redirección HTTPS y protección de iframes. No se permite `sslmode=disable`. `/healthz/` sólo informa de disponibilidad SQL y admite el probe HTTP interno. `check --deploy` no silencia avisos Django; se justifica exclusivamente `axes.W006` porque el bloqueo global por usuario no depende de IP, cookies o User-Agent. Véanse pruebas y explicación en [Fase 3](docs/fase-3.md).

La cadena HTTPS/proxy y los backups **remotos** siguen pendientes de verificar. Se ha preparado Render PostgreSQL de pago y una estrategia de recuperación; la ventana PITR depende del workspace (Hobby: tres días según documentación actual). Procedimiento, credenciales docentes y riesgos residuales en [despliegue](docs/despliegue.md).

## Testing

Ejecuta los tests Django **desde `backend/`** para que el descubrimiento incluya las tres aplicaciones:

```bash
# Entorno virtual activo; desde la raíz
python -m pip check
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python manage.py test --verbosity 2
cd ../frontend
npm test
npm run build
cd ..
python scripts/check_production.py
```

La Fase 3 conserva las pruebas anteriores y añade regresiones de reintentos, ediciones obsoletas, seguridad y volumen, además de pruebas `TransactionTestCase` con conexiones PostgreSQL independientes. SQLite omite expresamente las pruebas de bloqueo: no acredita concurrencia de filas. Los resultados exactos están en [fase-3.md](docs/fase-3.md).

```bash
# QA opcional; Python con Playwright/Chromium y binarios PostgreSQL disponibles:
python3 scripts/verify_phase3.py --pg-bin /usr/lib/postgresql/14/bin
```

El script crea un PostgreSQL aislado y temporal, aplica migraciones, ejecuta tests, arranca Gunicorn con `DEBUG=False` y TLS de prueba, verifica Chromium, reinicios y una restauración separada. Nunca usa la base ni las cuentas locales del usuario. Escribe evidencias en `artifacts/phase3/`, ignorado por Git. No es un despliegue público. Playwright y las herramientas de auditoría no son dependencias de la aplicación.

`check_production.py` sigue siendo sólo una comprobación estática con valores ficticios. GitHub Actions incluye PostgreSQL 16 y pruebas SQLite. Se comprobó el [run aprobado de Fase 3](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/40747706230) para `49ee198`; no acredita todavía los cambios locales de Fase 4. La [Fase 2](docs/fase-2.md) conserva sus evidencias históricas.

## Despliegue

**Render preparado; publicación pendiente de cuenta, coste y autorización.** `render.yaml` propone web Python y PostgreSQL gestionado en Frankfurt. Es una configuración con coste y no se ha aplicado. `scripts/build.sh` compila React y recoge estáticos; `scripts/release.sh` aplica migraciones; Gunicorn sirve Django y WhiteNoise los estáticos. La base permanece fuera del disco efímero de la web.

No hay URL pública verificada. Antes de publicar deben autorizarse el push y los recursos del proveedor; después verificar HTTPS, flujo funcional y persistencia tras un despliegue real. Instrucciones completas de variables, usuario de evaluación, backups, recuperación y aceptación en [docs/despliegue.md](docs/despliegue.md).

## Roadmap

1. **Base técnica:** vendedores, indicadores, roles, React y tests, implementada.
2. **Fase 1:** planes, acciones, objetivos, revisiones y cierre documentado desde Admin, implementada y probada.
3. **Fase 2:** dashboard, vendedores y gestión React de planes, implementados; pruebas y capturas en [fase-2.md](docs/fase-2.md).
4. **Fase 3:** preparación y verificación local de producción; faltan publicación y aceptación remota.
5. **Fase 4:** memoria Markdown/PDF, capturas, diagramas, guion de 4:50 y preparación de defensa disponibles; grabación, publicación y confirmaciones pendientes.

El [roadmap detallado](docs/hoja-de-ruta.md) define criterios de aceptación. No se prevén integraciones Mirakl en esta fase.

## Demo y documentación académica

**URL pública: pendiente.** La demo local se abre en `http://127.0.0.1:8000/dashboard/` después de instalar, migrar, crear una cuenta, cargar los datos ficticios y compilar siguiendo este README. La demo controlada de evaluación y el acceso privado del tribunal se preparan según [despliegue](docs/despliegue.md). Nunca publicar contraseñas de evaluación en GitHub.

| Material | Ubicación |
| --- | --- |
| Informe de Fase 4 y pendientes | [fase-4.md](docs/fase-4.md) |
| Memoria técnica | [PDF](docs/memoria-pfm.pdf) · [Markdown](docs/memoria-pfm.md) · [Conversión](docs/exportacion-memoria.md) |
| Capturas, diagramas y pruebas | [Índice visual](docs/evidencias-visuales.md) · [Resultados JSON](docs/evidencias-fase-4.json) |
| Vídeo, todavía sin grabar | [Guion de 4:50](docs/guion-video-pfm.md) |
| Defensa | [Exposición y 25 preguntas](docs/preparacion-defensa.md) |
| Requisitos oficiales | [Matriz](docs/trazabilidad-requisitos.md) · [Fuentes](docs/fuentes-pfm.md) |
| Cierre externo | [Acta pública pendiente](docs/verificacion-publica.md) · [Checklist de entrega](docs/checklist-entrega.md) |

El caso 6% → 4,5% → 3% utiliza datos ficticios y demuestra software, no resultados empresariales. La memoria reconoce los pendientes; el proyecto no se declara listo para entregar mientras falten URL, vídeo y confirmaciones obligatorias.

## Cumplimiento académico

| Requisito | Estado actual |
| --- | --- |
| Backend Django | Base y módulo de planes funcionales |
| Modelos, vistas, plantillas, autenticación y persistencia Django | Cumplido para vendedores, indicadores y planes |
| React en una o dos vistas con datos reales | Dashboard, vendedores y planes integrados con datos y escrituras reales de Django |
| Flujo funcional de datos | Caso completo 6% → 4,5% → 3% comprobado en API y navegador, con acciones, revisiones y cierre sin entrar en Admin |
| GitHub, README e historial significativo | Repositorio público y CI de Fase 3 verificados; Fase 4 local, sin commit ni push |
| URL pública funcional | Pendiente |
| Seguridad y protección de datos | Controles, PostgreSQL y concurrencia probados localmente; aceptación remota pendiente |
| Arquitectura coherente | Cumplido para la base técnica |
| Documentación del problema, aportación, usuarios y seguridad | Memoria completa y PDF para revisión; falta incorporar aceptación pública |
| Memoria PDF/Word | [PDF generado](docs/memoria-pfm.pdf) y [fuente editable](docs/memoria-pfm.md) |
| Vídeo ≤5 min | Grabación y enlace pendientes; [guion 4:50](docs/guion-video-pfm.md) preparado |
| Actividades obligatorias aprobadas y autorización docente | No verificable a partir del repositorio |

La [matriz de requisitos](docs/trazabilidad-requisitos.md) vincula cada punto con evidencias y la rúbrica. No se puede garantizar una nota por instalar paquetes o aprobar estas pruebas. El README no sustituye a memoria, vídeo ni despliegue.

## Referencias

- [Guía oficial del PFM](https://docs.google.com/document/d/1KhmvNgC4g9WI8suPOBjGFcUCQeA8rVPkoVS53fYLOkQ/edit), consultada íntegramente el 28/10/2026. [Registro de fuentes y requisitos](docs/fuentes-pfm.md); no se redistribuye la guía académica en GitHub.
- [PcComponentes: criterios de calidad automatizados](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/20561228339357-criterios-de-calidad-automatizados).
- [PcComponentes: preparación de planes de acción](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/38119386983965-como-mejorar-tus-indicadores-de-calidad-y-preparar-un-plan-de-accion).
- [PcComponentes: NPS y eficiencia de entrega](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/37487009483805-NPS-y-eficiencia-de-entrega).
- [Compatibilidad Django 5.2](https://docs.djangoproject.com/en/5.2/faq/install/) y [checklist de despliegue](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).
- [Django REST Framework](https://www.django-rest-framework.org/), [React con herramientas de compilación](https://react.dev/learn/build-a-react-app-from-scratch), [Vite](https://vite.dev/guide/), [django-environ](https://django-environ.readthedocs.io/en/latest/quickstart.html), [psycopg](https://www.psycopg.org/psycopg3/docs/basic/install.html) y [WhiteNoise](https://whitenoise.readthedocs.io/en/stable/django.html).

Fuentes funcionales y condiciones Render contrastadas el 28/10/2026, sin modificar umbrales ni acceder a datos corporativos. Las referencias técnicas históricas se conservan como documentación de las decisiones.

## Autoría y licencia

Autoría indicada en la licencia preexistente: **Pablo Rosales**. Repositorio con licencia [MIT](LICENSE), conservada sin cambios. Proyecto académico independiente; las marcas citadas pertenecen a sus titulares y no implican afiliación ni respaldo.
