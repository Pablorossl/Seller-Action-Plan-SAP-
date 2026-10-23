# Verificación de la base — 22/10/2026

Resultados observados localmente; no son resultados de GitHub Actions ni de Vercel. La auditoría original se conserva en [auditoria.md](auditoria.md).

## Entorno y dependencias

Python 3.12.4 en `.venv`, Django 5.2.18, DRF 3.18.3, django-environ 0.14.0, psycopg/psycopg-binary 3.3.6, WhiteNoise 6.12.0 y tzdata 2026.5. Dependencias transitivas fijadas en `backend/requirements.txt`; `pip check` sin incompatibilidades. Se volvió a ejecutar la instalación desde ese archivo y todas las versiones estaban satisfechas.

React/React DOM 19.3.1, Vite 7.3.7 y plugin React 5.2.0. Instalación inicial con npm 10.8.2 y Node 20.20.2; `npm ci`, dos casos `node:test` y compilación verificados también con Node 22.19.0 existente, seleccionado solo para esos procesos. `npm ci` informó cero vulnerabilidades conocidas en su auditoría de esa fecha; esto no equivale a una revisión de seguridad exhaustiva.

## Comprobaciones reproducibles

Con el entorno virtual activo, desde `backend/`:

```bash
python -m pip check
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate --check
python manage.py test --verbosity 2
python manage.py collectstatic --noinput
```

Desde `frontend/`: `npm ci`, `npm test` y `npm run build`. Desde la raíz: `python scripts/check_production.py`.

| Comprobación | Resultado observado |
| --- | --- |
| Instalación Python y `pip check` | Correctos; sin dependencias incompatibles |
| Migraciones iniciales | Generadas, aplicadas en SQLite; sin cambios de modelos pendientes |
| `manage.py check` | Sin incidencias |
| Suite Django | 18 pruebas aprobadas, incluida la restricción administrativa de usuarios staff |
| Fetch JavaScript | 2 casos aprobados con Node 22: paginación y denegación |
| Compilación Vite | Correcta: HTML, CSS y JavaScript generados |
| `collectstatic` | Correcto; incluye administrador y recursos React |
| `check --deploy --fail-level WARNING` | Sin incidencias con ajustes ficticios de producción; no conecta a PostgreSQL |
| Secretos e ignorados | `.env`, SQLite, venv, node_modules, dist, staticfiles y directorios de contexto ignorados; sin secretos previamente versionados |
| Git | Cambios locales sin commit ni push; revisión de espacios y enlaces locales |

## Flujo real de navegador

Prueba puntual con Playwright/Chromium ya disponible en el entorno, ejecutada con permiso para abrir puertos locales. Se utilizó una SQLite temporal migrada, un usuario con contraseña aleatoria no mostrada y `seed_demo`; los servidores se cerraron al finalizar. El script de esta prueba se generó en `/tmp`, no es una dependencia ni una prueba automática incluida en el proyecto. Las credenciales y la base temporal no se incorporaron al repositorio.

Se comprobó:

1. Anónimo recibe `403` en la API.
2. Acceso mediante el formulario Django con token CSRF y cookies reales.
3. React muestra las dos tiendas ficticias y catorce observaciones con su clasificación.
4. El flujo funciona en Django con React compilado (`127.0.0.1:8000`) y por el proxy de Vite (`127.0.0.1:5173`).
5. No hubo errores JavaScript y la página no desbordó horizontalmente a 390 px; la tabla conserva su desplazamiento interno.
6. Crear un vendedor por HTTP con sesión y CSRF devuelve `201`; recargar la plantilla Django muestra la escritura persistida.

Para repetir manualmente: seguir instalación, migraciones y demo del README, abrir el panel, iniciar sesión desde su enlace y alternar ambas secciones. La prueba de navegador puntual complementa la suite Django; no se declara una suite E2E instalada.

## Incidencias resueltas y límites

- La primera expectativa del test de volumen usaba el límite exclusivo como si ya implicara suspensión. Se corrigió para probar un valor inferior en los indicadores `lt`; las pruebas de frontera mantienen el valor exacto como alarma.
- El primer run de tests invocado desde la raíz no descubrió los tests de las apps. Se ejecutó después desde `backend/`, comprobando explícitamente el número de pruebas; el README y CI usan ese directorio.
- WhiteNoise avisó inicialmente de la ausencia de `staticfiles/` antes de ejecutar `collectstatic`; los archivos ya se han recogido. No se silenció el control.
- Los accesos de red y la apertura de sockets están restringidos por el sandbox. Las instalaciones y la prueba HTTP se completaron tras solicitar las autorizaciones correspondientes.
- No se probaron Windows/macOS, PostgreSQL externo, Vercel, dominio, HTTPS real, backup ni recuperación. Sus instrucciones y controles están preparados o documentados como pendientes.
- La CI está escrita pero no se ejecutó en GitHub. La memoria y el vídeo son borradores de estructura, no entregables finales. No se atribuye una nota ni aprobación administrativa.


## Verificación de Fase 1 — 23/10/2026

Se repitieron primero las 18 pruebas de la base existente. La suite ampliada incluye 46 pruebas Django y casos de datos inválidos, FK inexistentes, transiciones, fechas, varios indicadores, comparaciones con igualdad, dirección de mejora, datos insuficientes, histórico, cierre y permisos. El recorrido de aceptación se realiza mediante formularios reales de Admin con el cliente de pruebas Django. Se exige CSRF en una prueba específica de cierre. No equivale a una nueva ejecución de navegador real.

La migración `action_plans/0001_initial` se aplicó a la SQLite local sin modificar registros anteriores. La comprobación de modelos no detecta migraciones pendientes. Los resultados completos de cierre de fase se registran en [fase-1.md](fase-1.md).

Durante la ampliación de pruebas, una aserción buscó comentarios en el listado de revisiones, que muestra valor y periodo y deja los comentarios en el detalle. Se corrigió para comprobar que el filtro devuelve las dos revisiones. Después pasaron las 45 pruebas; no quedó ese fallo pendiente. La primera invocación de la suite base usó una ruta relativa de Python incorrecta y se corrigió antes de ejecutarla correctamente desde `backend/`.

Se conservan como históricos los resultados del 22/10 y sus límites: no acreditan PostgreSQL, CI remota ni despliegue público.
