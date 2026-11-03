# Vídeo académico SAP — guion de 4:20

**Preparado; vídeo no grabado ni enlace comprobado.** Objetivo: 260 segundos, con 40 segundos de margen respecto al máximo de cinco minutos. El tiempo real se debe medir con un ensayo; la tabla es un presupuesto, no la duración de un archivo existente.

Usar [SAP público](https://sap-bice.vercel.app), código desplegado `97b4bff55a07b8fd3c71b05740748db5bf63438b`. La evidencia documental `575c6c9` y esta revisión local son versiones posteriores de documentación. No redesplegar para grabar ni mostrar un localhost como sustituto de la URL exigida.

## Preparación antes de grabar

- Entrar por canal privado con el agente de evaluación; ocultar el acceso mientras se introduce la contraseña. Cerrar paneles de proveedores, terminales con entornos, gestor de claves y cabeceras de cookies.
- Preparar, mediante el flujo normal, un plan ficticio nuevo y abierto: observación inicial de incidencias al 6 %, meta 3 %, dos acciones y una revisión de agosto de 2026 al 4,5 %. Conservar los planes 5 y 6 de aceptación; no reabrirlos ni modificar sus evidencias.
- Elegir fechas previstas válidas en el momento de grabar. Los meses de la muestra son históricos y ficticios; no narrarlos como actividad empresarial actual.
- Dejar la acción correctiva pendiente y la preventiva pendiente, para completar una durante la demostración. Tener a mano textos breves para pegar en los formularios, sin contraseñas ni comandos con secretos.
- Preparar una segunda pestaña con DevTools abierto en una respuesta JSON de API. Mostrar únicamente URL/ruta y Response; no Headers con cookies, CSRF o autorización.
- Abrir el diagrama de arquitectura y la referencia al SHA como apoyo. Comprobar el servicio y hacer una prueba de diez segundos de audio. El ensayo puede revelar que hay que reducir narración; no superar el límite para conservar detalles secundarios.

Decir expresamente que el plan se preparó para la demo. Las acciones que se muestren ejecutándose deben guardarse realmente en SAP. No editar una respuesta JSON para simular un resultado ni utilizar las capturas como sustituto de una demostración funcional.

## Secuencia y locución propuesta

| Tiempo | Pantalla/acción | Explicación con palabras propias |
| --- | --- | --- |
| 0:00–0:25 | Título y URL pública | «Soy Pablo Rosales. SAP aborda el seguimiento posterior a detectar un problema de calidad de un vendedor. Una métrica no explica por sí sola qué se acordó, quién debe actuar y por qué se cerró el caso. Todos los datos de esta demo son ficticios.» |
| 0:25–0:45 | Dashboard | «El usuario objetivo es un Account Manager o Marketplace Support Agent. Este espacio reúne su cartera, prioridades y planes. Es un proyecto académico independiente, sin conexión con Mirakl ni datos corporativos.» |
| 0:45–1:20 | Vendedores → buscar referencia → ficha | «React consulta a Django los vendedores permitidos para la sesión. En la ficha vemos un indicador inicial del seis por ciento, su periodo y el contexto del seguimiento. Un agente no recibe la cartera del otro.» |
| 1:20–2:00 | Abrir el plan ficticio preparado | «He preparado este plan para centrar la demostración en el seguimiento. Conserva problema, causa y evidencia, con una meta del tres por ciento. El estado del plan describe el proceso; alcanzar la meta es una evaluación distinta.» |
| 2:00–2:35 | Editar la correctiva y completarla con fecha/evidencia | «Esta acción concreta el compromiso, responsable y plazo. Registro evidencia y la completo; la preventiva queda pendiente. Completar una tarea no demuestra por sí solo que el indicador haya mejorado.» |
| 2:35–3:15 | Mostrar agosto 4,5 %; añadir septiembre 3 %, 100 pedidos ficticios | «Cuatro coma cinco mejora respecto al seis inicial, pero no alcanza la meta. Añado una medición posterior del tres por ciento. Django calcula el resultado con periodo y datos evaluables, mientras React presenta la respuesta persistida.» |
| 3:15–3:40 | Finalizar con razones y confirmación; recargar | «Documento el cierre y confirmo la operación. Se conservan evaluación, revisiones y acciones, incluida la preventiva pendiente. Una rectificación crearía una nueva revisión con motivo, en lugar de borrar la anterior.» |
| 3:40–4:05 | Network, respuesta de /api/plans/ID/ y diagrama | «Django aporta modelos, plantillas, autenticación y reglas. React obtiene y muestra JSON del mismo origen y usa CSRF al escribir. PostgreSQL en Neon conserva los registros; Vercel ejecuta Django y sirve los estáticos.» |
| 4:05–4:20 | Cierre sobre SAP y evidencia | «Se verificaron permisos, historial, persistencia tras redesplegar y restauración aislada. El valor esperado es mejorar la trazabilidad; no he medido ahorro empresarial. El código servido es 97b4bff y puedo explicar sus decisiones y límites.» |

Total previsto: **4 minutos y 20 segundos**. Si la latencia consume el margen, recortar la narración secundaria o editar pausas dejando claros los saltos, sin falsear acciones. No acelerar hasta volver ilegible la interfaz.

## Textos ficticios breves

| Campo | Texto de apoyo |
| --- | --- |
| Plan | DEMO vídeo: reducir incidencias ficticias |
| Problema | Incidencias del 6 % en una muestra ficticia de julio de 2026. |
| Causa | Embalaje insuficiente y falta de revisión previa. |
| Evidencia | 100 pedidos ficticios; sin información de clientes reales. |
| Correctiva | Revisar preparación y expedición. |
| Evidencia de ejecución | Protocolo aplicado a una muestra ficticia. |
| Revisión | Mejora observada en el periodo ficticio. |
| Cierre | Objetivo del 3 % alcanzado; se conserva la preventiva pendiente. |

## Comprobación del archivo y del enlace — pendiente

Reproducir el vídeo completo, comprobar una duración máxima de 300 segundos, audio entendible, texto legible, uso real de React con backend y ausencia de credenciales. Confirmar que la introducción, demostración, tecnologías y límites son correctos. La locución es una ayuda de preparación: el autor debe adaptarla a lo que efectivamente haga y comprenda.

Si se dispone de FFmpeg, `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video-pfm.mp4` permite medir la duración. El comando no afirma que ese archivo exista.

Después, el autor debe alojarlo con permisos adecuados, guardar la URL real y probar el enlace como lo abrirá el tribunal, sin depender de la sesión del propietario. Esa comprobación de permisos no debe presentarse como la prueba de la aplicación desde una segunda red independiente. Registrar duración, fecha y resultado en checklist-entrega.md. **Grabación, subida y enlace siguen pendientes de intervención personal.**
