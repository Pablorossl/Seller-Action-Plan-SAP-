# Guion del vídeo PFM — 4 minutos y 50 segundos

**Estado: guion preparado; grabación y enlace pendientes.** No existe un vídeo explicativo generado por esta fase. La guía oficial admite un máximo de cinco minutos. El objetivo es 4:50, dejando diez segundos de margen; comprobar la duración del archivo exportado, no sólo la del ensayo.

## Preparación

Grabar la versión que se entregue, preferiblemente tras completar el [acta pública](verificacion-publica.md). Abrir SAP con un agente de evaluación sin Admin, datos exclusivamente ficticios y permisos de planes. Preparar el vendedor `SAP-DEMO-PLAN`, observación inicial de julio de 2026 al 6%, 100 pedidos y canal `ficticio-es`. Crear un **nuevo** plan durante la demo: la semilla contiene un ejemplo ya cerrado y no debe presentarse como una creación en directo.

Ensayar una vez el flujo completo. Tener preparados en un archivo local los textos breves del diagnóstico, acciones y cierre para pegarlos; no usar automatización que simule la grabación. Dejar las fechas de revisión en el día real y el plazo del plan treinta días después. Las mediciones de agosto y septiembre son históricas. Si el ensayo no cabe, recortar la narración y mostrar una segunda acción ya preparada en un plan de apoyo, explicando ese salto; no ocultar un cambio de plan como si fuera el mismo recorrido.

Preparar tres pestañas: SAP, diagrama de arquitectura y código `frontend/src/services/api.js` junto a `Workspace.jsx`. Abrir Network con filtro `api/` en otra ventana; ocultar Request Headers, cookies y tokens. Mostrar sólo URL relativa, estado y respuesta JSON ficticia. Desactivar notificaciones del escritorio. No mostrar consola de Render, variables de entorno ni credenciales.

## Guion cronometrado

| Tiempo | Pantalla y acción | Texto orientativo |
| --- | --- | --- |
| 0:00–0:35 · 35 s | Portada con nombre y dashboard | «Soy Pablo Rosales y presento Seller Action Plan. El proyecto nace de mi experiencia en soporte de marketplace. Detectar una desviación en un indicador no basta: necesitamos organizar causas, compromisos y revisiones. SAP centraliza ese seguimiento. Es un proyecto académico independiente que complementa Mirakl; no está conectado a su API y todos los datos de esta demo son ficticios.» |
| 0:35–1:05 · 30 s | Diagrama de arquitectura; volver al dashboard | «Django gestiona modelos, autenticación, permisos y persistencia. React presenta el espacio operativo y consume la API mediante Fetch. PostgreSQL conserva los datos y permite comprobar transacciones y bloqueos. Django sirve la aplicación compilada con Gunicorn y WhiteNoise bajo un mismo origen. El login y el portal también utilizan plantillas Django.» |
| 1:05–1:40 · 35 s | Mostrar contadores; buscar `SAP-DEMO-PLAN`; abrir vendedor e indicador | «El agente ve su cartera y sus prioridades. Desde el directorio busco un vendedor y consulto sus indicadores con canal y periodo. Aquí las incidencias son del seis por ciento en un mes histórico. El dato inicia el análisis, pero SAP no suspende tiendas ni modifica pagos. Voy a documentar un plan con objetivo del tres por ciento.» |
| 1:40–2:10 · 30 s | Crear plan: pegar diagnóstico, meta 3, plazo; guardar borrador | «Registro problema, causa raíz y evidencia, fijo una meta medible y asigno responsable y plazo. El servidor valida que la observación pertenece a este vendedor y que el objetivo mejora el valor inicial. El borrador y sus objetivos se guardan juntos.» |
| 2:10–2:45 · 35 s | Añadir correctiva y preventiva; activar; completar correctiva con evidencia | «Las acciones concretan el trabajo, quién lo realiza y cuándo. Activo el plan y completo la acción correctiva con su fecha y evidencia. Mantengo la preventiva pendiente para distinguir la ejecución de tareas del resultado medido.» |
| 2:45–3:20 · 35 s | Registrar agosto 4,5 y septiembre 3, cada mes con 100 pedidos; mostrar comparación | «Las revisiones conservan autor, periodo y comentarios. Cuatro coma cinco mejora respecto al inicio, pero aún no cumple la meta. La revisión posterior del tres por ciento sí la alcanza. La evaluación la calcula Django; el comentario del agente no reemplaza el resultado.» |
| 3:20–3:40 · 20 s | Cerrar con razones y confirmación; recargar | «Documento las razones y confirmo el cierre. La evaluación queda guardada como instantánea, junto al histórico. Al recargar persisten las dos revisiones y el resultado, incluida la acción preventiva que quedó pendiente.» |
| 3:40–4:20 · 40 s | Network: recargar directorio, seleccionar GET `/api/sellers/`, Response; mostrar api.js y vista | «Esta petición demuestra la integración: React solicita vendedores a Django y recibe JSON con los registros permitidos para la sesión. En el código, Fetch utiliza el mismo origen y devuelve la respuesta que representa la vista. Para escribir también envía CSRF. Los datos que vemos proceden de la base, no de una lista fija dentro del componente.» |
| 4:20–4:50 · 30 s | Resumen de pruebas y cierre sobre SAP | «SAP aplica permisos por vendedor, validación y transacciones. Se han aprobado 77 pruebas Django en PostgreSQL local, incluidas ocho de concurrencia, y el recorrido de navegador. Su valor esperado es mantener seguimiento y trazabilidad; no he medido ahorros empresariales. Como evolución estudiaría importación autorizada de indicadores. La prioridad actual es un flujo coherente que puedo explicar y comprobar.» |

Total: **290 segundos**. De los dos minutos de demostración, reservar tiempo para cargar y comprobar cada respuesta; no narrar más rápido para compensar un flujo sin ensayar. Si el vídeo se graba antes de publicar, decir expresamente «entorno local»; ese vídeo no acredita el requisito de despliegue. Tras completar producción, ajustar únicamente las frases que cuenten con evidencia remota.

## Textos breves para la demostración

| Campo | Contenido ficticio |
| --- | --- |
| Título | Reducir incidencias de la tienda ficticia |
| Problema | Incidencias del 6% en el periodo de julio de 2026. |
| Causa | Embalaje insuficiente y falta de control previo. |
| Evidencia | Revisión de una muestra de 100 pedidos ficticios. |
| Objetivo | Alcanzar un máximo del 3% de incidencias. |
| Correctiva | Revisar preparación y expedición de pedidos. |
| Preventiva | Control previo de incidencias recurrentes. |
| Responsable de acciones | Equipo ficticio de logística |
| Evidencia de ejecución | Protocolo aplicado a una muestra ficticia. |
| Revisión | Mejora observada en la muestra ficticia del periodo. |
| Cierre | Objetivo del 3% alcanzado; se conserva la acción preventiva pendiente. |

## Grabación y entrega

Utilizar OBS, Loom o una herramienta disponible de captura de pantalla y micrófono. Elegir 1920×1080 o resolución legible, comprobar audio con una toma de diez segundos y grabar una sesión real. Se puede editar pausas, manteniendo la secuencia y explicando los saltos. No utilizar capturas animadas como sustituto de la demostración real.

Reproducir el archivo completo: duración ≤300 s, texto legible, audio comprensible, ejemplo React-Django visible y sin credenciales. Si se dispone de FFmpeg, `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 video-pfm.mp4` permite obtener la duración; el comando no afirma que exista ese archivo.

Subir sólo después de revisión y autorización del autor. Guardar enlace real, duración y fecha en el checklist de entrega. Probar el acceso con la misma configuración que tendrá el tribunal, desde sesión privada u otra cuenta autorizada. No se ha publicado ningún vídeo ni se han enviado materiales.
