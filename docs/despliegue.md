# Despliegue y operación de SAP

Actualizado el 28/10/2026. **Preparación local; todavía no hay URL pública verificada.** Los resultados actuales están en [Fase 4](fase-4.md) y el acta remota en [verificación pública](verificacion-publica.md). Los comandos parten de la raíz del repositorio, salvo indicación contraria.

## Destino propuesto y coste

Render: un servicio web Python de 0,5 CPU / 512 MB (`0.5c-512mb`) y PostgreSQL gestionado de 0,1 CPU / 256 MB (`0.1c-256mb`), 1 GB de disco, ambos en Frankfurt. `render.yaml` describe recursos **de pago**, sin despliegue automático por commit y con acceso externo a PostgreSQL cerrado. No se ha aplicado ni contratado. Revisar nombres para no coincidir con recursos existentes y confirmar el importe completo en el panel antes de aprobar.

Se conserva Django + React en un único origen. Gunicorn ejecuta WSGI con dos workers; WhiteNoise sirve el resultado de Vite y los estáticos Django. El proxy del proveedor termina HTTPS y PostgreSQL conserva usuarios, sesiones y registros fuera del disco efímero del servicio. No hacen falta Docker, Nginx, Redis ni un dominio comprado.

La alternativa Railway cobra por uso y exige vigilar consumo y volumen persistente; también sería válida. Se elige Render por su separación explícita de build/pre-deploy/arranque y recuperación gestionada. La preparación anterior `backend/vercel.json` permanece como referencia histórica, sin ser la receta elegida para esta fase.

Referencias revisadas: [Django en Render](https://render.com/docs/deploy-django), [Blueprint y tamaños vigentes](https://render.com/docs/blueprint-spec), [pre-deploy](https://render.com/docs/deploys), [precios Render](https://render.com/pricing), [precios Railway](https://railway.com/pricing). La tarifa y los límites se confirman al contratar; no se presupone gratuidad. Render Free suspende la web tras 15 minutos sin tráfico y la base gratuita caduca; no se propone para la defensa. [Límites Free](https://render.com/docs/free).

## Presupuesto comprobable antes de autorizar

Consulta de tarifas públicas del 28/10/2026: web `0.5c-512mb`, **7 USD/mes**; PostgreSQL `0.1c-256mb`, **6 USD/mes**; workspace Hobby, **0 USD/mes más cómputo**. Base estimada: **13 USD/mes**, con 1 GB PostgreSQL indicado como incluido en la página de precios. Ampliación de almacenamiento: 0,30 USD/GB/mes; Hobby incluye 5 GB de transferencia, después 0,15 USD/GB. Confirmar factura, impuestos, minutos de build, retención externa y posible coste de una base de recuperación en el panel. No es un límite de gasto ni una oferta contratada. [Tarifas oficiales](https://render.com/pricing).

El tamaño mínimo debe medirse en Render antes de recomendarlo como definitivo. No se promete alta disponibilidad. Free duerme a los 15 minutos y PostgreSQL Free caduca a los 30 días, carece de backups y no permite el mismo procedimiento de consola; no cumple la continuidad prevista de evaluación. [Condiciones Free](https://render.com/docs/free).

La revisión conserva `render.yaml` sin cambios: identificadores, región, disco, versión PostgreSQL, comandos y variables son compatibles con la referencia consultada. Falta validación del Blueprint en la cuenta. En el panel: **New → Blueprint**, conectar este repositorio, elegir `main` y `render.yaml`, revisar exclusivamente `sap-web` y `sap-db`, introducir el secreto privado y comprobar el presupuesto. **No pulsar Apply/Deploy hasta autorizar recursos y coste.** Después seguir «Primera publicación». Los cambios de Fase 4 necesitarán un push expresamente autorizado si se quieren publicar; Fase 3 ya está disponible en GitHub.

## Variables y secretos

| Variable | Configuración |
| --- | --- |
| `DJANGO_SECRET_KEY` | Secreto privado de al menos 50 caracteres aleatorios, diferente al local; introducir en Render. No imprimirlo en logs ni en el repositorio |
| `DJANGO_DEBUG` | `False` |
| `DATABASE_URL` | Conexión interna proporcionada por `sap-db`; Django exige PostgreSQL y `sslmode=require` o verificación superior |
| `RENDER_EXTERNAL_HOSTNAME` | Render la proporciona; se incorpora el hostname exacto a hosts y su origen HTTPS a CSRF |
| `DJANGO_ALLOWED_HOSTS` | Para otro proveedor o dominios propios: hosts exactos separados por comas, sin esquema ni comodines |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Orígenes HTTPS exactos de dominios adicionales. En mismo origen no hace falta habilitar CORS |
| `DJANGO_TRUST_PROXY` | `True` sólo detrás del proxy que sanea `X-Forwarded-Proto`. Verificar comportamiento antes de dar por aceptada la URL |
| `SAP_DEMO_MODE` | `True` únicamente durante la carga explícita de demo; después volver a `False` |
| `NODE_VERSION` | Rama `22`; `.python-version` selecciona Python `3.12`, último parche disponible en Render |
| `WEB_CONCURRENCY` | `2` inicialmente |
| `PORT` | Asignado por el proveedor; Gunicorn lo utiliza |

Django conserva SQLite para desarrollo con `DJANGO_DEBUG=True` y `DATABASE_URL` vacía. Las variables del proceso prevalecen sobre `.env`. Nunca utilizar prefijos `VITE_` para secretos. Render admite TLS con certificados internos autofirmados: `require` cifra la conexión; la URL interna no admite `verify-full`. [Conexiones PostgreSQL](https://render.com/docs/postgresql-creating-connecting).

## Primera publicación

1. Revisar y guardar los cambios locales en Git. Obtener autorización antes de hacer push. No se ha publicado el trabajo de esta fase.
2. Autorizar proveedor y coste. Conectar el repositorio a Render con la cuenta del titular y revisar el Blueprint antes de aplicarlo; no reutilizar nombres de recursos ya existentes sin evaluar el impacto.
3. Crear los recursos definidos y proporcionar la clave privada en el formulario de variables. Mantener la raíz del repositorio, no `backend/`, para que el build alcance `frontend/`. Comprobar las versiones de Python/Node mostradas por el proveedor.
4. Build: `bash scripts/build.sh`. Instala dependencias fijadas, compila React, ejecuta `collectstatic` y `check --deploy`. No modifica datos.
5. Pre-deploy: `bash scripts/release.sh`. Ejecuta `migrate --noinput`, comprueba migraciones y seguridad **una vez por release**, antes de iniciar workers.
6. Arranque: `cd backend && gunicorn config.wsgi:application --config gunicorn.conf.py`.
7. Revisar logs, obtener el dominio real `.onrender.com`, verificar certificado, redirecciones y `/healthz/`. Render puede aceptar 301 como health check: se exceptúa exclusivamente `/healthz/` de la redirección Django para ejecutar SQL incluso en el probe interno. No revela información de la base. [Health checks](https://render.com/docs/health-checks).
8. Crear el administrador por terminal privada si se necesita: `python backend/manage.py createsuperuser`. No utilizarlo como cuenta de evaluación.
9. Preparar el agente y la demo según el apartado siguiente. Ejecutar el recorrido público, reiniciar y redesplegar, y repetir la consulta del mismo plan antes de marcar aceptación.

No se ejecutan migraciones ni semillas desde Gunicorn, importaciones WSGI o cada worker. No usar `runserver` en producción.

## Acceso docente y datos ficticios

En la consola privada del servicio, desde la raíz:

```bash
python backend/manage.py create_demo_agent --username evaluador
# Con SAP_DEMO_MODE=True configurado temporalmente en el proveedor:
python backend/manage.py seed_evaluation_demo --owner evaluador --confirm-fictitious
# Después, devolver SAP_DEMO_MODE a False.
```

`create_demo_agent` solicita y valida la contraseña sin eco y rechaza modificar usuarios existentes. Crea un agente sin `is_staff` ni `is_superuser`. Para un agente existente, `configure_plan_agent --username NOMBRE --interface-only` concede permisos de planes sin activar Admin ni cambiar el staff previo; revisar ese atributo si se reutiliza una cuenta.

La semilla utiliza los comandos anteriores, conserva los datos existentes y rechaza apropiarse de otra demo. Genera cinco vendedores, siete políticas, vendedores conformes y con desviaciones, tres planes (uno abierto y dos cerrados), acciones pendientes/vencidas/completadas y revisiones con resultados alcanzados y pendientes. Los plazos del plan abierto se calculan una vez al crear la demo; repetir el comando no los desplaza ni restaura registros editados por el evaluador. Los periodos de medición de julio–septiembre de 2026 son históricos y se muestran como tales.

El vendedor `SAP-DEMO-PLAN` permite crear desde React un **nuevo** plan de incidencias 6% → 3%, añadir las dos acciones y registrar agosto 4,5% y septiembre 3%. No necesita Admin para ese recorrido. Crear otro agente sin vendedores para comprobar el aislamiento. Compartir URL, usuario y contraseña sólo mediante el canal privado del equipo docente. No enviar claves mediante commits, capturas o comentarios públicos. Al terminar la evaluación, desactivar la cuenta y conservar su histórico; no borrarla.

## Verificación pública pendiente

Desde un equipo de QA con Playwright/Chromium:

```bash
python scripts/verify_browser.py --url https://DOMINIO_REAL \
  --username evaluador --other-username otro_agente \
  --seller-reference SAP-DEMO-PLAN --allow-writes
```

La URL debe ser un origen HTTPS real. El script solicita ambas contraseñas, crea un plan ficticio adicional y valida el certificado público (no ignora errores TLS). Genera capturas y JSON en `artifacts/public-browser/`, ignorado por Git. Requiere permiso de escritura sobre esa demo. La prueba local usa explícitamente un certificado de QA; su informe no cuenta como verificación pública.

Comprobar además desde fuera del proveedor:

- HTTP redirige a HTTPS; la cabecera `X-Forwarded-Proto` suministrada por un cliente no permite eludir las garantías del proxy.
- Login, logout POST, cookies Secure/HttpOnly/SameSite, CSRF, dashboard, estáticos y acceso entre agentes.
- Crear y cerrar el plan; registrar su ID. Reiniciar el servicio y consultar el mismo plan, acciones y revisiones. Ejecutar otro deploy y repetir. No volver a cargar la semilla como sustituto de persistencia.
- Confirmar que `.env`, backups y trazas privadas no se sirven. Un fallo SQL debe dar 503 en `/healthz/`; una URL desconocida no debe mostrar DEBUG.
- Adjuntar a `docs/fase-3.md` fecha, URL real, commit desplegado, navegador y resultados, sin credenciales.

## Migraciones, actualización y rollback

Antes de una actualización: ejecutar tests locales y PostgreSQL, comprobar `makemigrations --check --dry-run`, revisar las migraciones y disponer de un punto de recuperación. La migración `action_plans/0002_concurrency_guards.py` es aditiva; incorpora revisiones y claves de reintento, sin reescribir `0001`. Django-axes añade sus tablas mediante las migraciones del paquete fijado.

Aplicar migraciones mediante pre-deploy. Si falla, no iniciar la nueva versión; revisar el error y corregirlo. No ejecutar `makemigrations` en producción ni dos releases manuales simultáneos. Mantener cambios de esquema compatibles con la versión anterior mientras se sustituyen instancias.

Para revertir una regresión de aplicación, volver a la última versión compatible usando el proveedor. No revertir a ciegas las migraciones ni restaurar una copia sobre la base válida: una restauración puede perder cambios recientes. Revisar compatibilidad y usar una base separada antes de cambiar la conexión. `render.yaml` desactiva auto-deploys para mantener esta decisión explícita.

## Backups y restauración

Responsable propuesto: titular del proyecto (Pablo Rosales), que debe confirmar configuración y alertas. Datos a respaldar: base PostgreSQL completa, incluidos usuarios, hashes de contraseña, grupos/permisos, sesiones, vendedores, políticas, métricas, planes, acciones, revisiones, cierres y migraciones. No hay archivos subidos. El código vive en Git; los secretos se conservan por separado en el gestor del proveedor y un almacén privado, nunca en Git.

La documentación actual de Render ofrece PITR en PostgreSQL **de pago**: ventana de **3 días en workspace Hobby**, 7 días en Pro o superior. La recuperación crea otra instancia, que puede generar coste. No afirmar una retención de siete días con Hobby ni que el repositorio haya activado backups remotos. [Recuperación del proveedor](https://render.com/docs/postgresql-backups).

Política propuesta: comprobar PITR al provisionar, exportación lógica diaria con retención privada de siete días y copia antes de cambios importantes. El titular debe configurar y supervisar ese trabajo; esta fase **no ha programado exportaciones remotas**. Objetivo orientativo para exportaciones: perder como máximo un día de datos y recuperar en una jornada; no hay SLA ni RTO remoto medido.

Exportación manual reproducible, en una terminal privada con herramientas PostgreSQL de la misma versión mayor que el servidor o posterior compatible. Preparar `PGHOST`, `PGPORT`, `PGUSER`, `PGDATABASE`, `PGSSLMODE=require` y `PGPASSFILE` (archivo privado con modo 0600), siguiendo los datos del proveedor. No poner la URL con contraseña en argumentos, historial o documentación. Si la conexión es externa, autorizar sólo la IP necesaria, con aprobación, y retirar esa excepción después.

```bash
umask 077
pg_dump --format=custom --no-owner --no-acl --file sap-private.dump
pg_restore --list sap-private.dump
```

Copiar el archivo cifrado a almacenamiento privado fuera del servicio y comprobar la fecha/resultados. El disco de la web es efímero y no sirve como destino durable de backups. `.dump` está ignorado, pero sigue siendo información sensible. No es suficiente comprobar que el archivo existe.

Restauración controlada: crear una base **nueva y vacía**, configurar las variables de conexión para ese destino y comprobarlas privadamente antes de ejecutar:

```bash
pg_restore --exit-on-error --single-transaction --no-owner --no-acl \
  --dbname sap_recovery sap-private.dump
# Con DATABASE_URL apuntando únicamente a la restauración:
python backend/manage.py migrate --check
python backend/manage.py check --database default
```

No usar `--clean`, ni sobrescribir una base existente. Verificar usuarios/permisos, recuentos, el plan cerrado de referencia, sus revisiones y FK. Probar la restauración antes de sustituir la conexión de la web; cualquier cambio de destino productivo requiere autorización. `scripts/verify_phase3.py` ejecuta una exportación/restauración real aislada y compara huellas de los registros y asignaciones; acredita el procedimiento local, no los backups del proveedor.

## Operación y disponibilidad

Gunicorn emite método, ruta sin query string, estado y duración a stdout; errores a stderr. No registra cuerpos, cookies ni contraseñas. Los errores DEBUG no se muestran al público. Revisar logs de 5xx, `/healthz/`, consumo de conexiones y espacio de PostgreSQL. Configurar alertas de disponibilidad en el proveedor y un monitor HTTPS externo; ambos pendientes de activar.

Login: cinco fallos bloquean el nombre de usuario durante quince minutos, persistidos en base de datos. No se renueva indefinidamente el plazo por nuevos fallos. Tras verificar la identidad, un administrador puede ejecutar `python backend/manage.py axes_reset_username NOMBRE`. El reseteo de contraseñas se realiza con `changepassword`; no se ha añadido correo. Revisar intentos antiguos y limpiar sesiones caducadas con `clearsessions` periódicamente. El bloqueo por usuario puede provocar indisponibilidad temporal de una cuenta bajo ataque; no sustituye a las defensas del proveedor.

Durante la evaluación, mantener servicio y base de pago activos, supervisar cuota/disco y evitar cambios de esquema antes de la defensa. La instancia mínima propuesta no ofrece alta disponibilidad de la base ni un SLA contractual del proyecto. Los tiempos medidos localmente no predicen el rendimiento del proveedor. Confirmar estos límites y fechas de continuidad antes de contratar.
