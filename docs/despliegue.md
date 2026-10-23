# Producción, Vercel y copias de seguridad

## Estado y verificaciones locales

El repositorio prepara un backend Django WSGI y el panel React bajo un mismo origen. `backend/vercel.json` declara el framework y ejecuta `npm ci` y `npm run build` en `frontend/`. `STATIC_ROOT` está definido; la documentación actual de Vercel indica detección Django y recolección automática de estáticos. WhiteNoise permite comprobar esos recursos en un entorno WSGI local.

Referencia consultada el 22/10/2026: [Django en Vercel](https://vercel.com/docs/frameworks/full-stack/django). Las capacidades del proveedor pueden cambiar; validar la configuración en un preview antes de considerarla operativa.

`python scripts/check_production.py` comprueba los ajustes mediante `check --deploy --fail-level WARNING`, con secreto aleatorio y URL PostgreSQL ficticia. No abre una conexión. Compilar y recoger estáticos localmente comprueba artefactos; no acredita un build de Vercel.

## Condiciones pendientes para el primer preview

1. Seleccionar cuenta/proyecto Vercel y PostgreSQL gestionado con persistencia y TLS. Esta tarea no ha creado recursos externos ni costes.
2. Configurar raíz del proyecto `backend/` y permitir acceso al resto del monorepositorio, necesario para `../frontend`. Seleccionar un runtime Python 3.12 y Node LTS compatible. Si el proveedor no admite esta disposición, ajustar el build antes de publicar.
3. Configurar las seis variables del README en el entorno del proveedor. Usar dominios exactos para hosts y CSRF; clave privada exclusiva; `DEBUG=False`; PostgreSQL persistente. Habilitar la confianza en proxy solo después de confirmar que sanea `X-Forwarded-Proto`.
4. Ejecutar `migrate` una sola vez por release desde una sesión confiable con las variables de ese entorno. No ejecutarlo desde el arranque de cada función ni como operación concurrente del build. Crear el administrador de forma interactiva y no cargar la demo en producción.
5. Construir un preview, revisar logs de instalación, Django y estáticos, y obtener su URL real. Hasta completar esto no existe una receta remota verificada.

No se proporciona una URL inventada ni se ha ejecutado una publicación. Estos pasos son condiciones de preparación pendientes, no un despliegue probado.

## Criterios de aceptación del despliegue

- `check --deploy` con las variables reales sin advertencias; migraciones aplicadas sobre PostgreSQL.
- HTTP redirige a HTTPS; sin bucles detrás del proxy. Cookies Secure, HttpOnly para sesión y SameSite.
- Login y logout con CSRF; escrituras sin token rechazadas y acceso entre agentes impedido.
- Portal Django, `/dashboard/`, JavaScript, CSS y administrador cargan desde el dominio correcto.
- Crear un vendedor, reiniciar o volver a desplegar y comprobar que persiste. No utilizar SQLite de la función.
- No exponer `.env`, trazas DEBUG, credenciales ni copias de base de datos.
- Protección de intentos de login y monitorización configuradas en el servicio elegido.

## Copias y recuperación propuestas

Política inicial: copia diaria y retención mínima de 7 días en PostgreSQL gestionado, con acceso restringido y cifrado del proveedor. Configurar alertas de fallos y registrar la persona responsable. Probar una restauración en una base aislada antes de la exposición pública y después de cambios de esquema importantes. Confirmar que las restricciones, los usuarios y sus asociaciones se conservan.

Las copias y la restauración siguen pendientes de contratación/configuración y prueba. Para SQLite de desarrollo, detener escrituras y copiar `backend/db.sqlite3` fuera del repositorio; no subir la copia a GitHub. Mantener una política de borrado si se incorporan datos personales autorizados en el futuro. Durante el PFM solo se emplean datos ficticios.
