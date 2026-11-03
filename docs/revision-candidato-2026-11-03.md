# Revisión del candidato local — 3 de noviembre de 2026

Base: 54ac2cd. El commit que incorpora este informe es el candidato local de las correcciones F01–F03, no una entrega pública aceptada.

Se revisaron instrucciones disponibles (sin AGENTS.md aplicables), diff completo, migración, pruebas, interfaz, auditoría del 02/11, informes de implementación y diagnóstico de publicación. `sources/` no existe en este checkout; no se modifica material de referencia. Todos los cambios pendientes se atribuyen al trabajo documentado en esta conversación.

La guía original se volvió a leer mediante Google Drive, modificada el 08/10/2026. Se conserva su referencia en fuentes-pfm.md, sin redistribuir su contenido. Los requisitos explícitos incluyen Django, integración React, persistencia/autenticación, repositorio/README/historial, aplicación pública estable, memoria PDF/Word y vídeo accesible de hasta cinco minutos. F01–F03 son decisiones del dominio SAP, no funcionalidades exigidas nominalmente por la guía. Refuerzan casos de uso, errores, integridad y resultados verificables para un Account Manager o Marketplace Support Agent. SAP sigue siendo académico e independiente, sin integración oficial con Mirakl o PcComponentes.

Se incluyen código de F01–F03, migración 0003 sin modificación de datos, pruebas y presentación React; auditoría y evidencias textuales, informes y diagnóstico de publicación. README y matriz reciben una nota de vigencia. Los informes anteriores describen su fecha: la falta de concurrencia verificada en el informe inicial de F01 se resuelve con las pruebas posteriores de F02. La confirmación administrativa del autor no se presenta como inspección de expediente.

## Evidencias y comprobaciones

- Se contrastaron los logs existentes de F03: suite PostgreSQL completa de 112 pruebas correctas sin omisiones y módulo posterior de 27 pruebas correctas con límites ayer/hoy/mañana. No se repitieron esas suites en esta revisión porque no se cambió código desde su verificación. Los recuentos incluyen pruebas heredadas/importadas, no 112 casos funcionales independientes.
- Se repitió `makemigrations --check --dry-run` con DATABASE_URL vacía y DEBUG=True: sin cambios pendientes.
- Se repitió `scripts/verify_vercel.py` con Node 22.19.0: npm ci/build, check de producción, estáticos, paquete backend aislado, WSGI sin SQL, plantillas, rutas, HTTPS y hosts correctos. Log local `/tmp/sap-candidate-vercel-node22.log`. No ejecuta builder remoto ni despliega. Las trazas DisallowedHost son la comprobación esperada del host no permitido.
- El primer intento del build falló por esbuild EPERM dentro del sandbox, con Node 20 del PATH. La repetición final se hizo fuera del aislamiento y con Node 22 requerido. Se conserva el resultado final anterior como el válido para el candidato.
- `git diff --check`: correcto.
- JSON candidatos analizados correctamente. Revisión acotada contra valores privados locales de entorno y patrones de URLs con contraseña/claves privadas: sin coincidencias reales. La URL de README con usuario/CLAVE/host es un ejemplo. No se imprime ni incorpora ningún secreto.
- No se repiten navegador ni pruebas frontend independientes en esta revisión. Sus ejecuciones previas y límites están en los informes F01–F03; el build React sí se repitió en la comprobación del paquete.

Se excluyen archivos ignorados: entornos, .neon, SQLite, dumps, node_modules, frontend/dist, backend/frontend_dist, staticfiles y artefactos de QA. Las evidencias JSON conservan hashes y ubicaciones temporales; esos archivos temporales no se empaquetan en el commit ni se presentan como evidencias accesibles públicamente.

## Pendientes de entrega

Publicar el SHA con autorización y comprobar su CI; confirmar proyecto/rama/endpoint Neon y configuración Vercel; migrar y preparar datos ficticios solo con autorización; resolver los 404 y aceptar HTTPS/rutas/login/flujo completo/aislamiento/persistencia/recuperación remotos. Actualizar memoria/PDF, guiones, diagramas y capturas a la versión finalmente desplegada; grabar y comprobar vídeo/enlace; preparar defensa y mantener aplicación operativa durante evaluación. El diagnóstico previo de publicación conserva el estado anterior al commit; este informe registra la preparación del candidato posterior.

No se hace push, despliegue, contratación ni cambio de datos o servicios externos. La lectura de la guía se hace con el plugin Google Drive y la habilidad google-drive.
