# Preparación de SAP para publicación en Vercel Hobby

Revisión del **03/11/2026**, consultas remotas iniciadas a las **21:12 UTC**. Inspección externa de solo lectura. Se recuperó el login de Vercel por petición del titular; no se cambió configuración externa, no se desplegó, no se hizo push y no se ejecutaron migraciones ni cargas de datos. Solo se actualizaron documentos locales y artefactos ignorados de auditoría.

## Git, secretos y candidato

- HEAD local y `main` remoto: **`160fc4c39790a33670ae0be715f6903f224e3668`**.
- Su CI `Verificación SAP` está **completed / success**, [run 41708195577](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/41708195577), evento push del 03/11/2026. Esta aprobación corresponde exactamente a ese SHA.
- Al empezar, `README.md`, `docs/neon-setup.md` y `package.json` estaban modificados, y `scripts/verify_neon_e2e.py` estaba sin seguimiento. **El verificador nuevo y la documentación actualizada no están incluidos en `160fc4c`.**
- Esta revisión añade cambios en `docs/despliegue-vercel.md`, `docs/verificacion-publica.md` y este informe, además de actualizar el README. No se ha creado otro commit. El candidato completo todavía no tiene SHA ni una CI propia aprobada.
- La propuesta es un nuevo commit descendiente de `160fc4c` que incluya los cuatro archivos pendientes iniciales y estos tres documentos de preparación. Desplegar ese nuevo SHA exacto después de publicarlo y aprobar su CI. No atribuirle la CI del padre ni redesplegar `43fcab8` esperando que reciba los cambios locales.
- El índice está vacío. Se examinaron los 168 archivos seguidos, sus versiones del índice y los candidatos locales, comparándolos en memoria con valores privados locales y patrones de claves privadas/cadenas PostgreSQL. **No se encontraron coincidencias de secretos reales**. Se conservan ejemplos ficticios explícitos de CI, pruebas y plantillas.
- `.env`, `.env.before-neon`, `.neon` y `artifacts/` están ignorados. El único archivo de entorno seguido es `.env.example`, sin credenciales reales. No añadir archivos privados al preparar el commit. La revisión de patrones no es una garantía absoluta frente a cualquier secreto desconocido.

Antes de guardar el candidato, volver a revisar únicamente las rutas seleccionadas, comprobar el índice sin imprimir valores y ejecutar `git diff --cached --check`. No usar `git add .` para incluir indiscriminadamente archivos locales. Un push puede disparar despliegue automático después de corregir la integración Git: coordinar primero el orden de publicación.

## Vercel: estado real y diagnóstico del 404

Acceso recuperado con Vercel CLI **65.11.0**. API de equipos, proyecto, dominio, deployments y logs de build consultados con éxito; valores de entorno ocultos.

| Campo | Estado observado |
| --- | --- |
| Equipo | `pablo-s-coding`, ID `team_QEO60SkY07InWgc6CX0nIb5J` |
| Plan | **Hobby**, estado **active** |
| Proyecto | [`sap`](https://vercel.com/pablo-s-coding/sap), ID `prj_1kARDqBB0eW17w9yWX1G3QNoA2gP` |
| Git conectado | `Pablorossl/sap`, repo ID **1437556401**, rama Production `main` |
| Repositorio de este checkout | `Pablorossl/Seller-Action-Plan-SAP-`, repo ID **1430152684** |
| Dominio | `sap-bice.vercel.app`, verificado y asociado al proyecto |
| Framework actual del proyecto | Django |
| Root Directory actual | `backend` |
| Fuentes fuera de Root Directory | Activadas |
| Overrides actuales de build/install/output | Sin override explícito en los campos consultados |
| Node actual | `24.x`, compatible con los engines del repo; la validación local usa 22.19.0 |
| Región por defecto actual | `iad1`; el `backend/vercel.json` candidato solicita `fra1` |
| Fluid Compute / máquina de build | Activado / basic |
| Protección de deployments | `all_except_custom_domains`; verificar acceso externo del dominio final |

Los IDs Git son diferentes: **Vercel no está conectado al repositorio de este checkout**. La API pública de GitHub devuelve 404 para `Pablorossl/sap`; eso no permite distinguir un repositorio privado de uno ya no disponible. La diferencia de IDs sí acredita que no es el repositorio revisado. Hace falta corregir la integración Git tras autorizar los cambios externos; un push al repositorio actual no garantiza un build en este proyecto Vercel.

| Deployment Production | SHA y resultado |
| --- | --- |
| Alias vigente: `dpl_8c9Fhi8FCwffd5agwbS1FosT7iYJ` | `43fcab8301d0feafa9b346573ff6e1cc15405d3a`, **READY**, alias asignado |
| Último intento: `dpl_F921JG7M7sjGchUmsaLkNcw8ndVk` | Mismo SHA, **ERROR**, `DJANGO_SETTINGS_FAILED`: exige PostgreSQL mediante `DATABASE_URL`; alias no asignado |
| Anterior: `dpl_Dh41YgfVf9hzKBcXsKbzNeRFhwWJ` | Mismo SHA, **ERROR** al validar `DJANGO_ALLOWED_HOSTS` |
| Primero de los intentos Django: `dpl_DTFhw1uhcr1oQAK1oCa78gLDuD3J` | Mismo SHA, **ERROR** por `DJANGO_SECRET_KEY` ausente |

El deployment que conserva el alias se construyó con framework y buildCommand sin configurar en su snapshot. Sus metadatos muestran `routes: null` y un grupo de build con `entrypoint: "."` y `output: []`; **no contiene una salida WSGI Django que sirva SAP**. Su log solo acredita que terminó un build, no una aplicación funcional. Los tres intentos siguientes detectaron Django y compilaron React, pero fallaron antes de obtener el paquete funcional y no sustituyeron el alias.

Los GET de metadatos y las peticiones HEAD anónimas actuales confirman:

- `sap-bice.vercel.app`: `/`, `/accounts/login/`, `/healthz/` y `/api/plans/` devuelven **404**, `server: Vercel`, `x-vercel-error: NOT_FOUND`.
- URL inmutable del deployment con alias: `sap-nqq3mxqcy-pablo-s-coding.vercel.app`; sin seguir redirecciones devuelve **302 a Vercel SSO** en login/health.
- URL del último intento fallido: `sap-3zf321qww-pablo-s-coding.vercel.app`; también devuelve 302 a SSO. Un cliente que sigue redirecciones obtiene el HTML de acceso de Vercel, que no es el login Django ni un health 200 de SAP.
- Los registros CDN consultados asocian los 404 y las redirecciones al deployment vigente. Los logs de build se pudieron inspeccionar y se guardaron solo señales de diagnóstico, sin sus mensajes completos ni valores privados.

La consulta inicial de logs de ejecución con ventana de una hora fue rechazada por exceder la retención disponible de Hobby. Se repitió con quince minutos: **exit code 0, sin registros de ejecución**. La consulta CDN de quince minutos terminó también con exit code 0 y sí devolvió peticiones. La ausencia de logs de ejecución no sustituye la inspección de salidas del deployment ni acredita un health correcto.

**Diagnóstico:** el alias permanece en un build anterior sin salida de aplicación; los intentos Django fallaron por configuración de entorno incompleta. Además, la fuente Git conectada no es la del código preparado. El estado READY de ese build no demuestra aceptación de SAP. La propuesta debe corregir fuente, entorno y publicación del SHA elegido, en ese orden. Véase [NOT_FOUND](https://vercel.com/docs/errors/not_found).

La consulta REST de árbol de archivos de ese deployment devolvió 404. Ese endpoint documenta recuperación del código fuente para deployments subidos mediante CLI/API con archivos, por lo que ese 404 no demuestra que el deployment no exista. Se usaron los metadatos de salida, los logs de build y los registros CDN para el diagnóstico. [API de archivos](https://vercel.com/docs/rest-api/deployments/list-deployment-files).

## Neon: identidad y estado de la base

La conexión local se comparó en memoria con `neon connection-string production --project-id empty-feather-02803695 --pooled`. Coinciden endpoint, base y rol; los valores no se imprimieron.

| Comprobación de solo lectura | Resultado |
| --- | --- |
| Proyecto / rama | `empty-feather-02803695` / `production` |
| Branch ID | `br-divine-sky-b9hvdrte` |
| Estado | `ready`, predeterminada y primaria |
| Expiración / TTL | **Ausentes**, sin eliminación automática programada |
| `neon.ts` | No asigna TTL a la rama predeterminada; siete días solo para nuevas ramas no predeterminadas |
| PostgreSQL | **18** |
| URL de la app | Pooled, mismo destino que el CLI autenticado, TLS requerido |
| URL directa | Mismo endpoint/base/rol, sin pooling |
| Transacción de inspección | `transaction_read_only=on`, TLS activo |
| Esquema | Tablas Django/SAP presentes; **33 migraciones** registradas, incluidas las tres de action_plans |
| Datos actuales | **0** usuarios, sesiones, vendedores, métricas y planes |

No hay caducidad automática que acortar para la evaluación. Las ramas predeterminadas no admiten fecha de expiración según la [documentación Neon](https://neon.com/docs/guides/branch-expiration). No se habilitó protección de pago ni se cambió ninguna propiedad. El login real para el tribunal necesita cuentas todavía por crear: el verificador anterior limpió sus registros temporales. No se crearon cuentas en esta revisión.

## Propuesta concreta para Production — sin aplicar

1. Conservar el proyecto Vercel `sap` y su dominio. Tras autorización, conectar su integración Git al repo ID **1430152684**, `Pablorossl/Seller-Action-Plan-SAP-`, rama `main`, comprobando qué acción disparará el primer build.
2. Mantener preset Django, raíz `backend`, acceso a `../frontend`, salida/install predeterminados y variables de sistema automáticas. Aplicar el `backend/vercel.json` del SHA elegido: `python build_vercel.py`, función `config/wsgi.py`, región `fra1`, duración 60 s, inclusión de plantillas y React compilado. No usar `scripts/release.sh`, Gunicorn ni una salida Vite independiente en Vercel. [Django nativo y collectstatic](https://vercel.com/docs/frameworks/full-stack/django).
3. Mantener Hobby activo y proponer Node **22.x** (al menos 22.12) para alinear el deployment con la CI y el build local validado con 22.19.0. Node 24 actual también cumple los engines, por lo que no se atribuye a esa versión el fallo observado. Confirmar Python 3.12 y la región efectiva del nuevo deployment.
4. Configurar todas las variables antes del primer build del SHA final, **solo Production**:

| Variable | Estado de presencia observado | Propuesta, sin valores |
| --- | --- | --- |
| `DATABASE_URL` | **Ausente** | Añadir privadamente la URL pooled de la rama/base verificada, con TLS |
| `DJANGO_SECRET_KEY` | Presente, sensitive, Production | Validar privadamente su calidad y mantenerla estable entre redespliegues; no reutilizar la clave local |
| `DJANGO_ALLOWED_HOSTS` | Presente, sensitive, Production | Validar que permite exclusivamente el dominio canónico y cualquier alias expresamente aprobado |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Presente, sensitive, Production | Validar los orígenes HTTPS exactos correspondientes |
| `DJANGO_DEBUG` | Ausente | Configurar explícitamente la desactivación; Django ya la desactiva por defecto |
| `SAP_DEMO_MODE` | Ausente | Configurar explícitamente la desactivación |
| `VERCEL`, `VERCEL_ENV` | Exposición automática activada | Mantenerlas gestionadas por Vercel |

No se descifraron ni validaron los contenidos de las tres variables existentes: solo se inspeccionaron nombres, tipo y ámbito. No copiar `.env` completo. La URL directa `DATABASE_URL_UNPOOLED` no se añade al runtime; permanece en administración local. No asignar secretos productivos a Preview ni usar prefijos que los expongan en React. `NEON_BRANCH` es metadato local y no es necesario para servir Django.

## Validación local realizada

`scripts/verify_vercel.py`, Node 22.19.0 y Python del venv, **exit code 0**:

```text
✓ 33 modules transformed.
✓ built in 1.27s
System check identified no issues (1 silenced).
React preparado en backend/frontend_dist. Build sin migraciones ni semillas.
157 static files copied
OK: paquete backend aislado, WSGI sin SQL, plantillas, JS/CSS, rutas, HTTPS y hosts.
```

El script usa una URL ficticia inaccesible y configuración aislada; no consulta ni modifica Neon. Los 403/404 y DisallowedHost del log local son casos negativos esperados. No invoca el builder remoto de Vercel. No se repitió `verify_neon_e2e.py`, porque crea registros temporales y esta revisión prohíbe escrituras externas.

Artefactos locales ignorados en `artifacts/publication-review-2026-11-03/`: `secret-review.json`, `remote-metadata.json`, `vercel-detail.json`, `neon-state.json` y `runtime-log-summary.json`. Los documentos anteriores conservan sus fechas y no se presentan como pruebas nuevas.

## Publicación y aceptación pendientes de autorización

1. **Fijar fuente:** revisar y guardar el candidato completo; registrar su SHA. Comprobar CI aprobada de ese SHA exacto y que el deployment utiliza el mismo repo ID/SHA. Si la conexión Git dispara builds automáticamente, coordinar su activación con la configuración del entorno y la CI; no enviar un push accidentalmente durante la revisión.
2. **Entorno y cuentas:** validar privadamente las variables anteriores, seguir en Hobby, confirmar nuevamente identidad y estado de la base. Como está migrada, no migrar de nuevo por rutina. Solo tras autorizar escrituras, crear dos agentes ficticios con permisos funcionales y, si procede, cargar la demo una sola vez. Contraseñas por terminal/canal privado; no superusuarios para el tribunal.
3. **Deployment:** generar una publicación Production del SHA aprobado, revisar sus logs, Python/Node, copia React y collectstatic, función WSGI y archivos incluidos. Debe quedar READY con salidas de aplicación, sin errores de configuración, y recibir el alias canónico. Un Redeploy de un deployment antiguo conserva su fuente antigua.
4. **HTTPS y acceso externo:** comprobar certificado y HTTP→HTTPS; login accesible sin cuenta Vercel, `/healthz/` con JSON ok, redirección anónima de `/dashboard/` al login y API anónima denegada. Confirmar que la protección Vercel no impide el acceso al tribunal. Cookies Secure/HttpOnly/SameSite, HSTS y CSRF; un 200 de SSO no cuenta como respuesta de SAP.
5. **Estáticos y API:** CSS/JS y estilos del login con 200 desde CDN, sin errores de navegador ni contenido mixto; dashboard y respuestas de API coherentes, búsqueda, filtros y vista móvil.
6. **Recorrido completo:** vendedor e indicadores; crear plan con objetivos válidos, acciones y activación; registrar revisiones, rectificar/corregir con motivo y conservar el historial; rechazar duplicados y mediciones futuras; comprobar evaluación por periodo y cierre con confirmación/instantánea y bloqueo de edición posterior. Incluir errores recuperables y logout POST.
7. **Aislamiento:** otro agente no ve cartera ni plan ajenos; detalle y operaciones sobre ID ajeno denegados con 404; sin rol, 403. Rechazar escrituras sin CSRF y revalidar tras reentrar. El checker local de Neon no sustituye este recorrido público de dos agentes.
8. **Persistencia tras redespliegue:** guardar privadamente ID y JSON ficticio de un plan, acciones, revisiones y cierre. Hacer otro deployment del mismo SHA manteniendo base y clave Django, sin migraciones/semillas de rutina. Recuperar el mismo ID y comparar datos, permisos y continuidad de sesión según política. Registrar ambos deployment IDs. Reiniciar un servidor local, como en la prueba Neon previa, no acredita este paso remoto.
9. **Restauración aislada:** preparar `pg_dump` y `pg_restore` **18**, obtener una copia consistente por conexión directa y guardarla en ubicación privada. Restaurarla exclusivamente en otra base vacía aislada PostgreSQL 18 autorizada, con un proyecto/env de QA que no pueda escribir en Production. Comparar migraciones, conteos, registro de control y acceso de agentes; hacer una lectura funcional desde la app contra el destino aislado. No restaurar encima de production ni usar semillas para reconstruir la evidencia. El equipo solo tiene clientes **14.24**; no sirven para exportar PostgreSQL 18. [Compatibilidad de pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html).
10. **Acta:** completar `docs/verificacion-publica.md` con fecha/zona, SHA, CI, repo ID, deployment/alias, versiones, resultados y evidencia sin secretos. Mantener el plan gratuito y revisar cuotas antes de la evaluación. Hasta completar la aceptación, la URL continúa pendiente.

Las pruebas de navegador existentes y `verify_phase3.py` aportan QA local; no acreditan un redespliegue Vercel ni una restauración del Neon actual. La prueba de exportación/restauración queda pendiente, no se ejecuta como parte de esta revisión.
