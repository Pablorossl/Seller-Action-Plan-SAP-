# Seller Action Plan (SAP)

Aplicación web para documentar y seguir planes de mejora de vendedores de marketplace a partir de indicadores de calidad. Proyecto Final del Máster en Desarrollo Full Stack de ConquerBlocks.

**Estado: base funcional del MVP.** Incluye Django, API con control de acceso, persistencia, clasificación de indicadores y dos secciones React que consumen datos reales. La gestión de planes, acciones y seguimientos está pendiente. No existe todavía un despliegue público verificado.

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
| Mostrar datos persistidos en Django y React | Plantilla HTML y dos secciones React implementadas |
| Vincular cada plan con responsables, acciones y revisión | Pendiente de las siguientes fases |
| Reproducir la instalación y demostrar el flujo completo | Dependencias fijadas; memoria, vídeo y URL pública pendientes |

## Funcionalidades y estado

| Estado | Funcionalidades |
| --- | --- |
| Implementado | Login y logout Django; usuarios, grupos y administración; CRUD API de vendedores; aislamiento por propietario; registro administrativo de indicadores; API de indicadores de solo lectura; clasificación informativa; políticas de umbrales versionadas; plantilla Django; secciones React de vendedores e indicadores; demo idempotente; migraciones y pruebas |
| Preparado parcialmente | Ajustes de producción, PostgreSQL y configuración Vercel; CI configurada, sin ejecución remota comprobada |
| En desarrollo | No se declara ninguna funcionalidad adicional como iniciada |
| Previsto | Planes, acciones, responsables, plazos, estados, causas raíz, seguimientos, evolución gráfica, formularios React y trazabilidad de cambios |

Las métricas son observaciones registradas, **no cálculos sobre pedidos importados**. La interfaz indica su canal y periodo; una observación histórica no representa automáticamente la situación actual. Las reglas y el tratamiento del periodo se explican en [dominio](docs/domain.md).

## Tecnologías

Versiones instaladas en la preparación inicial del 22/10/2026:

| Tecnología | Versión | Función y justificación |
| --- | --- | --- |
| Python | 3.12.4 verificada | Runtime disponible; para nuevas instalaciones, usar el último parche de Python 3.12 |
| Django | 5.2.18 LTS | Backend académico, ORM, plantillas, autenticación, validación y tests |
| Django REST Framework | 3.18.3 | Serialización, permisos y API paginada |
| django-environ | 0.14.0 | Lectura de `.env` y configuración de la URL de base de datos |
| React / React DOM | 19.3.1 | Dos secciones interactivas que consultan Django mediante Fetch |
| Vite | 7.3.7 | Desarrollo y compilación; rama mantenida, compatible con npm disponible |
| @vitejs/plugin-react | 5.2.0 | Soporte JSX y actualización durante el desarrollo |
| SQLite | Incluida en Python | Base local sin servicios adicionales |
| PostgreSQL / psycopg | Driver 3.3.6 | Base prevista para producción; conexión externa aún no verificada |
| WhiteNoise | 6.12.0 | Servicio de estáticos compilados en una comprobación WSGI local; Vercel prevé servirlos por CDN |
| tzdata | 2026.5 | Zona horaria disponible también en Windows |
| unittest Django / node:test | Incluidos | Pruebas sin instalar otro framework |

`backend/requirements.txt` fija también las dependencias transitivas. `requirements.in` documenta los rangos de actualización; no sustituye al archivo fijado. npm es el único gestor JavaScript y `package-lock.json` debe conservarse.

Django 5.2 es compatible con Python 3.12. Vite 7.3 sigue recibiendo correcciones importantes y de seguridad según su [política de soporte](https://vite.dev/releases). npm 10.8.2 falló internamente resolviendo dependencias opcionales de Vite 8; se eligió una combinación mantenida que permite la instalación normal, sin omitir la validación de pares.

## Arquitectura

```mermaid
flowchart LR
    U[Usuario autenticado] --> H[Vista HTML Django]
    U --> R[React: vendedores e indicadores]
    R -->|Fetch y cookie de sesión| API[API REST Django]
    H --> ORM[ORM Django]
    API --> P[Rol y vendedores asignados]
    P --> ORM
    ORM --> DB[(SQLite local / PostgreSQL previsto)]
    API --> C[Clasificación según política versionada]
```

Django es el backend principal y gestiona sesiones, permisos y persistencia. En desarrollo Vite reenvía `/api/` y `/accounts/` a Django conservando el origen del navegador. En la compilación integrada, Django entrega `/dashboard/` y los archivos React se sirven bajo `/static/react/`. No se necesita habilitar CORS.

Se conserva `auth.User` de Django. `Seller.owner` representa la asignación inicial a un agente; `QualityMetric` almacena un indicador por vendedor, política, canal y periodo. `ThresholdPolicy` permite nuevas versiones de umbrales sin reescribir el clasificador. La [arquitectura detallada](docs/architecture.md) distingue entidades existentes y diseño futuro.

## Estructura

```text
.
├── backend/
│   ├── config/              # Ajustes, rutas, vistas HTML y WSGI
│   ├── sellers/             # Vendedores, acceso, API y comando seed_demo
│   ├── quality/             # Indicadores, políticas, clasificador y API
│   ├── templates/           # Portal y formulario de acceso Django
│   ├── manage.py
│   ├── requirements.in
│   ├── requirements.txt
│   └── vercel.json          # Preparación del proveedor, sin publicación
├── frontend/
│   ├── src/services/        # Fetch paginado y pruebas
│   ├── src/main.jsx         # Secciones React
│   ├── src/styles.css
│   ├── vite.config.js
│   ├── package.json
│   └── package-lock.json
├── docs/                    # Dominio, arquitectura, PFM y verificación
├── scripts/                 # Configuración local y check de producción ficticia
├── .github/workflows/ci.yml
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

Revisa y versiona las migraciones junto al cambio. `PROTECT` impide borrar propietarios, vendedores o políticas todavía referenciados. La API devuelve `409` al intentar borrar un vendedor con histórico.

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

Autenticación por **cookie de sesión Django**, sin JWT ni Basic Auth. Se requiere superusuario o grupo `Marketplace Agent`. Las respuestas paginadas incluyen `count`, `next`, `previous` y `results` (50 registros por página).

| Endpoint | Métodos | Comportamiento |
| --- | --- | --- |
| `/api/` | GET | Índice de endpoints, con rol autorizado |
| `/api/sellers/` | GET, POST | Lista accesible; crea vendedor asignado al usuario actual |
| `/api/sellers/{id}/` | GET, PUT, PATCH, DELETE | Solo vendedor accesible; no permite reasignar `owner` |
| `/api/metrics/` | GET | Observaciones de vendedores accesibles, con clasificación |
| `/api/metrics/{id}/` | GET | Detalle de observación accesible |
| `/accounts/login/` | GET, POST | Formulario HTML y creación de sesión; POST con CSRF |
| `/accounts/logout/` | POST | Cierre de sesión con CSRF |

POST de vendedor, con sesión y token CSRF válidos:

```json
{"name": "Tienda Ficticia", "reference": "FICTICIA-003"}
```

Las escrituras autenticadas necesitan `X-CSRFToken` o el campo de formulario `csrfmiddlewaretoken`. No hay endpoints de escritura de métricas, planes ni seguimientos. El registro de indicadores y políticas se realiza por el administrador.

Clasificaciones: `ok`, `alarm`, `suspension_threshold`, `insufficient_orders` y `below_reference`. `suspension_threshold` significa exclusivamente que la observación alcanza el umbral informativo: SAP no ejecuta suspensiones. Sin sesión o rol se devuelve `403`; un recurso ajeno se oculta con `404`; errores de validación producen `400`; métodos no implementados, `405`.

## Usuarios y permisos

| Rol | Capacidades actuales |
| --- | --- |
| Administrador (`is_superuser`) | Todos los vendedores e indicadores; usuarios, grupos, asignaciones y políticas mediante Django Admin |
| Marketplace Agent / Account Manager | CRUD de vendedores propios y lectura de sus indicadores; sin acceso administrativo por defecto |
| Autenticado sin rol | Sin acceso a la API de dominio; portal sin vendedores |
| Anónimo | Formulario de acceso; sin acceso a datos |

El filtrado del queryset se aplica tanto al listado como al detalle y a las escrituras. No se confía en ocultar botones para autorizar. Conceder `is_staff` por sí solo no otorga acceso administrativo a los modelos de dominio, reservados al superusuario en esta base.

Casos de uso disponibles:

| Actor | Caso de uso | Resultado |
| --- | --- | --- |
| Usuario | Iniciar sesión y abrir el portal Django | Consulta únicamente los vendedores permitidos por su rol |
| Agente | Crear o editar un vendedor mediante API | Registro persistido y asignado al agente autenticado |
| Administrador | Registrar indicadores y políticas desde Admin | Observaciones vinculadas al vendedor, canal, periodo y versión |
| Agente | Abrir las secciones React | Consulta de vendedores e indicadores reales con clasificación informativa |

Crear planes, asignar acciones y registrar revisiones son casos previstos, todavía sin implementación.

## Seguridad

**Implementado:** hashing de contraseñas y validadores nativos de Django, sesiones en base de datos, cookie de sesión HttpOnly y SameSite, CSRF en login/logout/escrituras, escape de plantillas Django y React, ORM parametrizado, roles y acceso por vendedor, validación de indicadores, claves foráneas, restricciones de base de datos, secretos ignorados y respuestas de dominio sin caché. React es de solo lectura, por lo que no contiene todavía formularios de validación de negocio.

Con `DEBUG=False` se activan HTTPS, cookies Secure, HSTS y protección contra inclusión en iframes; se exige PostgreSQL y se solicita TLS al driver. Estos son ajustes preparados: el HTTPS y la cadena de proxy reales siguen pendientes de verificación. CORS permanece cerrado al trabajar bajo el mismo origen.

**Pendiente antes de exposición pública:** verificar TLS y proxy, protección frente a intentos repetidos de login en la plataforma, recuperación de contraseña, registro de auditoría de cambios, política de conservación y pruebas PostgreSQL. Los futuros formularios React validarán para ayudar al usuario, manteniendo Django como autoridad.

**Copias de seguridad previstas:** PostgreSQL gestionado con copia diaria y retención inicial de 7 días; comprobar restauración en una base aislada antes de publicar y tras cambios relevantes. Esta política debe contratarse/configurarse y no existe todavía un backup operativo verificado. En local, detén el servidor antes de copiar SQLite; trata la copia como privada. Detalles en [seguridad y despliegue](docs/deployment.md).

## Testing

Ejecuta los tests Django **desde `backend/`** para que el descubrimiento incluya ambas aplicaciones:

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

Las pruebas Django utilizan una base de datos de test real de SQLite y ejecutan migraciones. Cubren login/logout, CSRF, roles, acceso entre propietarios, CRUD y persistencia, respuestas API, rangos, histórico de políticas, comparadores exclusivos/inclusivos y volúmenes 0, 29 y 30. Las pruebas de Fetch comprueban paginación y errores; sus dobles HTTP no acreditan persistencia, que se verifica en Django y en el flujo integrado.

El script de producción utiliza variables **ficticias y temporales** para ejecutar `check --deploy --fail-level WARNING`; no modifica `.env` ni conecta con PostgreSQL. El flujo de GitHub Actions está preparado, sin badge ni resultado remoto atribuido. Evidencia y limitaciones en [verificación](docs/verification.md).

## Despliegue

**Preparación local para Vercel; publicación pendiente.** `backend/vercel.json` declara Django y la compilación de React. El proveedor se plantea con raíz `backend/`, acceso a los archivos del monorepositorio y PostgreSQL externo persistente. No se instalaron Gunicorn ni una CLI global: el destino previsto proporciona el runtime WSGI.

Se han preparado los ajustes y la compilación; esto no acredita un despliegue. Falta configurar cuenta/proyecto, variables privadas, servicio PostgreSQL, migraciones controladas, estáticos, dominio y pruebas HTTPS en el entorno remoto. No hay una URL pública de SAP que pueda documentarse todavía. Consulta [la preparación y las validaciones pendientes](docs/deployment.md) y la [documentación oficial de Vercel](https://vercel.com/docs/frameworks/full-stack/django).

## Roadmap

1. **Base técnica:** repositorio, entorno, vendedores, indicadores, roles, React y tests. Completada en el alcance descrito.
2. **Planes y acciones:** modelos `ActionPlan` y `ActionItem`, estados, responsables, vencimientos, CRUD y pruebas por recurso.
3. **Seguimiento:** `FollowUp`, causas raíz, resultados, histórico y vistas React de planes/evolución.
4. **Entrega:** PostgreSQL y Vercel verificados, revisión de seguridad, memoria y vídeo de máximo cinco minutos.

El [roadmap detallado](docs/roadmap.md) define criterios de aceptación. No se prevén integraciones Mirakl en esta fase.

## Cumplimiento académico

| Requisito | Estado actual |
| --- | --- |
| Backend Django | Cumplido para la base técnica |
| Modelos, vistas, plantillas, autenticación y persistencia Django | Cumplido para vendedores e indicadores |
| React en una o dos vistas con datos reales | Cumplido en dos secciones del panel; MVP de planes pendiente |
| Flujo funcional de datos | Parcialmente cumplido: flujo vendedores/indicadores, sin planes |
| GitHub, README e historial significativo | Parcialmente cumplido: remoto y README; solo commit inicial en la auditoría |
| URL pública funcional | Pendiente |
| Seguridad y protección de datos | Parcialmente cumplido: controles locales; validación operativa pendiente |
| Arquitectura coherente | Cumplido para la base técnica |
| Documentación del problema, aportación, usuarios y seguridad | Cumplido en documentación del repositorio; memoria final pendiente |
| Memoria PDF/Word y vídeo ≤5 min | Pendiente; estructura y guion preparados |
| Actividades obligatorias aprobadas y autorización docente | No verificable a partir del repositorio |

La [matriz de requisitos](docs/requirements-mapping.md) vincula cada punto con evidencias y la rúbrica. No se puede garantizar una nota por instalar paquetes o aprobar estas pruebas. El README no sustituye a memoria, vídeo ni despliegue.

## Referencias

- Guía académica del PFM: requisitos y ponderaciones facilitados en el encargo. No se dispone en el repositorio del documento oficial ni de su versión; confirmar con el docente antes de la entrega.
- [PcComponentes: criterios de calidad automatizados](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/20561228339357-criterios-de-calidad-automatizados).
- [PcComponentes: preparación de planes de acción](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/38119386983965-como-mejorar-tus-indicadores-de-calidad-y-preparar-un-plan-de-accion).
- [PcComponentes: NPS y eficiencia de entrega](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/37487009483805-NPS-y-eficiencia-de-entrega).
- [Compatibilidad Django 5.2](https://docs.djangoproject.com/en/5.2/faq/install/) y [checklist de despliegue](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).
- [Django REST Framework](https://www.django-rest-framework.org/), [React con herramientas de compilación](https://react.dev/learn/build-a-react-app-from-scratch), [Vite](https://vite.dev/guide/), [django-environ](https://django-environ.readthedocs.io/en/latest/quickstart.html), [psycopg](https://www.psycopg.org/psycopg3/docs/basic/install.html) y [WhiteNoise](https://whitenoise.readthedocs.io/en/stable/django.html).

Fuentes públicas consultadas el 22/10/2026. Revisar su vigencia antes de modificar las políticas; no se consultaron datos corporativos ni credenciales.

## Autoría y licencia

Autoría indicada en la licencia preexistente: **Pablo Rosales**. Repositorio con licencia [MIT](LICENSE), conservada sin cambios. Proyecto académico independiente; las marcas citadas pertenecen a sus titulares y no implican afiliación ni respaldo.
