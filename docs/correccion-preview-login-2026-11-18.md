# Corrección de previsualización Vercel y detalles del login

## Diagnóstico con evidencias

Revisión de solo lectura del proyecto Vercel `sap`, preset Django, raíz `backend`, build `python build_vercel.py`, Node 22.x. Entrada WSGI `backend/config/wsgi.py`; React se compila como dashboard autenticado y Django sirve el login. No hay proxy propio ni adaptador adicional.

Los Runtime Logs del deployment `dpl_8F4q3XVCLfKYJ1P7nuTbm2zxqLGd` contienen, el 18/11/2026 a las 20:27:03 y 20:27:05 UTC (21:27 hora de Madrid), `DisallowedHost` para `sap-quqvtctzd-pablo-s-coding.vercel.app`, en las solicitudes GET `/`. Request IDs: `tthtv-1795033622278-e4e1518fde17` y `q5ds6-1795033625050-9a7e0ee60c68`. El deployment anterior presenta el mismo error con su hostname único. La causa es la diferencia entre ese hostname, usado por la captura de Vercel, y el alias público permitido.

La consulta pública de `/` devuelve 302 al login. Los logs de producción muestran GET login 200, POST login 302, dashboard y APIs 200 y logout 302 sobre `sap-bice.vercel.app`. Son evidencias del despliegue existente, no validación del cambio local.

## Corrección mínima

`backend/config/settings.py` añade únicamente `VERCEL_URL` a `ALLOWED_HOSTS` cuando `VERCEL=1`. Valida que sea un hostname exacto terminado en `.vercel.app`, sin esquema, puerto, ruta, comodines ni sufijos adicionales. La lista explícita de producción sigue siendo obligatoria. No usa datos de la petición ni acepta otros deployments. No cambia CSRF, HTTPS, cookies, sesiones, middleware, rutas ni `USE_X_FORWARDED_HOST`.

La variable del sistema está documentada por Vercel: https://vercel.com/docs/environment-variables/system-environment-variables

## Comprobaciones de configuración y publicación pendientes

- Mantener `DJANGO_ALLOWED_HOSTS=sap-bice.vercel.app` y los demás dominios exactos que estén autorizados.
- Mantener `DJANGO_DEBUG=False` y `DJANGO_CSRF_TRUSTED_ORIGINS=https://sap-bice.vercel.app` (más otros orígenes expresamente autorizados si existen).
- Verificar **Automatically expose System Environment Variables** activado; `VERCEL_URL` debe ser el hostname automático del deployment. No fijarlo al hostname de un despliegue anterior ni copiar el dominio de una petición HTTP.
- La API permitió consultar metadatos pero devolvió vacíos los valores de estas variables; no se presentan como valores efectivos verificados.
- Tras publicar manualmente estos cambios, regenerar la captura y confirmar que no se repite `DisallowedHost` para el nuevo hostname. La protección SSO de la URL única puede redirigir al login de Vercel; no se ha desactivado.
- No se ha ejecutado commit, push, despliegue ni modificación de configuración remota. El 400 actual de producción seguirá pendiente de corregir allí hasta publicar el cambio.

## Login

El icono de información era un fondo CSS a una coordenada vertical fija; una regla posterior anulaba el ajuste para ventanas bajas. Se sustituye por SVG real de 18 × 18 px, decorativo, en un contenedor flex con alineación centrada, separación de 10 px y `flex-shrink: 0`. El texto conserva su contenido y admite dos líneas.

Las etiquetas tenían margen inferior de 6 px y altura de línea heredada; los inputs inline también aportaban espacio de línea. Ahora cada grupo usa flex en columna con gap de 6 px, etiqueta sin margen y line-height 1.4; los inputs se muestran como bloques. Ambos grupos se separan 20 px, incluida la variante de poca altura. Los inputs mantienen 44 px de alto, radio, foco y funcionamiento.

## Validación local

- Suite Django `config sellers quality action_plans`: 116 casos, sin fallos; 9 omitidos por requerir PostgreSQL (ejecución SQLite aislada).
- Tras el cambio de settings, suite `config`: 9 casos correctos, incluidas nuevas variantes de `VERCEL_URL` malformada.
- `scripts/verify_vercel.py`: build React y paquete backend aislado correctos. Comprueba el alias configurado y el dominio único, `/` 302, login 200, API anónima 403, dominios ajenos 400, spoofing de `X-Forwarded-Host` rechazado, HTTPS y cookies seguras. PostgreSQL ficticio sin conexión; no es una publicación remota.
- `npm test`: suites de servicios y presentación React correctas.
- Verificación Chromium del login con base SQLite temporal: 15 tamaños (incluye 360 × 640), 14 comprobaciones funcionales, foco, contraste, errores y acceso con/sin JavaScript correctos. Sin scroll en el login inicial para alturas desde 568 px, sin errores JS ni assets. Capturas en `artifacts/login-redesign/`; inspección visual de escritorio y móvil con texto de ayuda en dos líneas.
- `git diff --check`: correcto. No se han añadido dependencias.
