# Defensa de SAP — comprensión y exposición hasta veinte minutos

**Material preparado; ensayo y defensa pendientes.** La guía fija veinte minutos como máximo para la videollamada, con preguntas. Propuesta: 10:30 de exposición, 7:30 de preguntas y 2:00 de margen. Adaptar el reparto a las instrucciones del tribunal y detener la exposición si necesita intervenir; no reservar veinte minutos de monólogo.

Referencias: [SAP público](https://sap-bice.vercel.app), código `97b4bff`, documentación posterior `575c6c9` y acta actualizada local. No ejecutar cambios funcionales ni redespliegues durante la defensa. El material ayuda a explicar el propio código; memorizar respuestas no acredita autoría o comprensión.

## Exposición cronometrada

| Tiempo | Contenido | Apoyo concreto |
| --- | --- | --- |
| 0:00–1:00 | Problema y aportación | De la métrica al seguimiento documentado; beneficios esperados, sin cifras empresariales inventadas |
| 1:00–2:20 | Usuario y alcance | Agente por cartera, administración separada, ausencia de vendedor externo e integración con Mirakl |
| 2:20–4:00 | Arquitectura y petición | Navegador → Vercel Django → DRF/ORM → Neon; React y sesión del mismo origen |
| 4:00–6:40 | Demostración pública | Vendedor/indicador, plan, acciones, revisión, evaluación y cierre; usar datos ficticios y un caso preparado |
| 6:40–8:20 | Integridad y seguridad | F01–F03, permisos, CSRF, transacciones, revisión obsoleta e idempotencia |
| 8:20–9:30 | Publicación y recuperación | SHA aprobado, alias, persistencia tras redeploy y copia restaurada aisladamente |
| 9:30–10:30 | Conclusión y límites | Qué quedó comprobado, qué no se midió y qué se validaría después |
| 10:30–18:00 | Preguntas del tribunal | Ir al archivo y a la condición que sustentan la respuesta |
| 18:00–20:00 | Margen | Aclaraciones, latencia o cierre solicitado por el tribunal |

Tener preparados PDF, código del SHA servido y JSON de evidencias. Los planes públicos 5 y 6 son históricos de aceptación y se pueden consultar. Para acciones que escriban, preparar otro plan ficticio mediante el flujo normal y no alterar los controles ya documentados. Si falla Internet, explicar la incidencia y utilizar la copia documental como apoyo; no presentarla como disponibilidad pública actual.

## Preguntas técnicas, razonamiento y navegación de código

### 1. ¿Qué problema resuelve SAP y qué no resuelve?

Relaciona diagnóstico, compromisos, mediciones y razones de cierre para un agente de marketplace. No gestiona pedidos, catálogo, pagos o sanciones, ni importa datos de Mirakl. Explicar una decisión concreta que resulte difícil reconstruir sin ese histórico. La necesidad está analizada, pero no se ha medido una mejora de productividad con usuarios.

### 2. ¿Por qué Django y por qué un monolito modular?

Django es requisito académico y aporta modelos, ORM, migraciones, plantillas, autenticación y permisos. sellers, quality y action_plans separan responsabilidades sin introducir una red de servicios que el MVP no necesita. Mostrar config/urls.py y las aplicaciones. El argumento es coherencia del alcance, no que los microservicios sean siempre incorrectos.

### 3. ¿Dónde se cumple el requisito de plantillas y qué aporta React?

backend/templates contiene acceso y portal; la vista dashboard sirve el índice compilado de React. Workspace.jsx y PlanDetail.jsx consultan API y representan carga, datos y errores. Mostrar config/views.py y una petición real; React no sustituye las reglas Django ni decide el logro de metas.

### 4. ¿Cómo llega un dato desde PostgreSQL hasta la pantalla?

Seguir un GET de /api/plans/6/: api.js, ruta DRF, autenticación, permiso, queryset visible, prefetch, serializador y evaluate_plan. Mostrar la respuesta y el dato renderizado. Señalar dónde se deja de considerar el dato como entrada confiable. Evitar enseñar cookies en DevTools.

### 5. ¿Qué diferencia hay entre autenticar y autorizar?

La sesión acredita identidad; no otorga automáticamente una cartera ni un permiso de cierre. IsMarketplaceAgent comprueba rol, visible_sellers filtra owner y visible_plans hereda el ámbito. Las vistas exigen permisos por operación y limitan las relaciones de los formularios. Un ID válido de otra cartera sigue devolviendo 404.

### 6. ¿El responsable recibe acceso? ¿is_staff es un permiso global?

El responsable es un dato operativo, no una concesión automática de acceso. is_staff permite entrar en Admin, pero no evita las comprobaciones de permiso o cartera. Una reasignación administrativa de vendedor transfiere el ámbito y conserva autores. Mostrar sellers/models.py, action_plans/serializers.py y configure_plan_agent.

### 7. ¿Por qué CSRF si ya hay contraseña y HTTPS?

La cookie de sesión puede enviarse automáticamente. Una escritura exige además un token válido y un origen permitido. HTTPS protege el transporte, no demuestra la intención de la operación. api.js envía X-CSRFToken; login y logout usan protección Django. Mostrar el 403 de la aceptación y explicar que el token tampoco sustituye el permiso.

### 8. ¿Qué se guarda en el navegador y cómo se protege?

La cookie de sesión es Secure, HttpOnly y SameSite=Lax; CSRF es una protección complementaria. React no guarda contraseñas ni un JWT de larga duración. La sesión vive en PostgreSQL y tiene caducidad de ocho horas. Mostrar ajustes, no sus valores privados. SameSite ayuda, pero no elimina la necesidad de CSRF.

### 9. ¿Qué reduce XSS e inyección SQL y qué no se puede afirmar?

React y las plantillas escapan texto; no se interpreta HTML de usuario. El flujo consulta mediante ORM parametrizado y valida entradas. No afirmar una auditoría de penetración exhaustiva ni que HTTPS elimina XSS. Reconocer los límites de SQL privilegiado y de futuras vías de importación.

### 10. ¿Qué separa una observación global de una revisión de plan?

QualityMetric registra el contexto inicial con una política. PlanMetric lo enlaza con la meta; PlanReview conserva el seguimiento del objetivo. Revisar un plan no sobrescribe automáticamente la observación global. Mostrar las relaciones y explicar por qué cerrar un plan no borra una desviación histórica de la ficha.

### 11. ¿Cómo calcula la evaluación 6 → 4,5 → 3?

Para incidencias, 4,5 mejora respecto a 6, pero no alcanza una meta de 3; la igualdad con la meta sí la alcanza. evaluate_metric usa dirección, datos evaluables y medición efectiva; evaluate_plan requiere que todos los objetivos sean evaluables y alcanzados para éxito global. La valoración narrativa del agente no reemplaza esa comparación.

### 12. ¿Qué hace F01 y por qué no editar la revisión anterior?

La corrección crea una fila, enlaza supersedes, exige motivo y conserva periodo, autor y fecha. La evaluación descarta las sustituidas antes de elegir el periodo vigente. Mostrar PlanReview, la unicidad parcial y el historial de PlanDetail.jsx. Una corrección tardía de agosto no debe desplazar una medición efectiva de septiembre.

### 13. ¿Qué evita una ramificación de rectificaciones?

La relación uno a uno y las restricciones protegen la estructura; la validación rechaza rectificar una revisión ya sustituida y el bloqueo del plan serializa escrituras. No describir la operación como idempotencia universal: un reintento de rectificación ya realizada puede recibir un error de validación.

### 14. ¿Qué hace F02 y por qué hay que filtrar antes de elegir la última?

Valida fechas observadas según Europe/Madrid y excluye datos futuros del resumen. Si primero se eligiera una futura y luego se descartara, podría perderse una anterior válida. Los datos futuros heredados se conservan identificados y no evaluables. Los plazos futuros son distintos y pueden ser válidos. Mostrar quality/views.py, models.py y las pruebas de fecha.

### 15. ¿Qué hace F03 cuando pasa el tiempo?

El cierre usa closure_evaluation y conserva situación de acciones y vencimientos del momento. Un plan finalizado no recalcula el pasado con hoy. Los cierres antiguos sin detalle mantienen desconocido. Se verificó persistencia en público y un avance simulado de 90 días solo sobre la copia restaurada. Mostrar evaluate_plan y PlanAction.is_overdue.

### 16. ¿Por qué cerrar con una acción pendiente o sin éxito?

Finalizar documenta una decisión administrativa; no implica que todas las tareas se completaran ni que el objetivo se alcanzara. Se guardan razones y evaluación real con confirmación y permisos. Los planes 5 y 6 muestran resultados distintos. Una instantánea no debe convertirse en un resultado favorable por cerrar.

### 17. ¿Para qué sirven transacción, bloqueo, revisión e idempotencia?

transaction.atomic agrupa cambios; select_for_update serializa la escritura; revision detecta un formulario leído antes de otro cambio; request_key/request_hash reconocen un reintento de creación del mismo contenido. Son problemas diferentes. Mostrar concurrency.py y explicar el orden vendedor→plan. Un cliente antiguo sin revisión/clave pierde esas garantías adicionales.

### 18. ¿Qué pasa si una revisión compite con el cierre?

Ambas operaciones comparten el bloqueo del plan. Si la revisión gana, puede incorporarse a la evaluación; si el cierre gana, la revisión posterior se rechaza. Una excepción revierte la transacción. Mostrar close_plan y una prueba de concurrencia con conexiones independientes. SQLite no acredita ese bloqueo.

### 19. ¿Qué garantiza la base y qué depende de la aplicación?

FK protegidas, unicidad y restricciones estructurales complementan validaciones de modelo. QuerySet.update, bulk_create y SQL directo pueden omitir clean/save. No son entradas del producto. Mostrar una restricción y una regla dependiente de fecha actual para explicar por qué no se atribuye toda la integridad a PostgreSQL.

### 20. ¿Cómo funcionan filtros y paginación sin filtrar una cartera en React?

El servidor aplica primero el ámbito y después filtros/orden/página. React envía parámetros y muestra count, next y previous. Se recorrieron dos páginas reales de 50 y 1 vendedores ficticios del segundo agente; se retiraron únicamente esos 51 registros. Mostrar Sellers, Pagination y SellerViewSet. Distinguir ese recorrido de los filtros de planes y del detalle histórico no paginado.

### 21. ¿Por qué pooled en runtime y directa para administración?

El runtime usa la URL pooled con TLS y psycopg; Django evita conexiones persistentes por proceso y cursores que sobrevivan una transacción del pooler. La directa se reserva a operaciones administrativas y pg_dump. No se usa el driver JavaScript de Neon en un backend Python. Mostrar settings.py y neon_manage.py, sin abrir .env.

### 22. ¿Cómo ejecuta Vercel Django y quién sirve los estáticos?

El preset usa WSGI en config/wsgi.py; build_vercel.py compila React y lo empaqueta. collectstatic produce los assets del CDN. Root Directory es backend y se permite leer frontend fuera de esa raíz. No se ejecuta Gunicorn ni release.sh como arranque Vercel y no se migra o siembra al construir.

### 23. ¿Qué causó el antiguo 404 y cómo se comprobó la solución?

El alias conservaba un build sin salida de aplicación; otros intentos fallaron por variables incompletas y el enlace Git apuntaba a otro repo ID. Se corrigieron permisos e integración, Production y despliegue. Un READY o un 200 del SSO de Vercel no acreditan SAP: se comprobaron alias, SHA, login Django y health JSON.

### 24. ¿Cómo se demuestra persistencia y recuperación?

Dos deployments de 97b4bff conservaron el mismo JSON de control y la sesión, sin repetir semillas. Se exportó un snapshot consistente con pg_dump 18.6 y se restauró en PostgreSQL 18 aislado; coincidieron 21 tablas, datos, índices y restricciones, con lectura Django. No se restauró sobre Production ni se acredita una copia automática ilimitada.

### 25. ¿Cuál es la diferencia entre los dos commits de entrega?

97b4bff es código servido con CI aprobada y deployment identificado. 575c6c9 es documentación y evidencias posteriores, también comprobadas en su contexto. Esta preparación académica es todavía local. Un push o un redeploy de otro SHA cambiaría el objeto evaluado; no confundir HEAD local con Production.

### 26. ¿Qué significa presupuesto cero y qué queda pendiente?

Se mantienen Hobby y Free dentro de sus condiciones y cuotas, sin nuevos servicios o medios de pago. No son una garantía de disponibilidad continua. Quedan la segunda red independiente, vídeo/enlace, revisión de memoria, justificantes académicos y defensa. No se midió productividad empresarial ni se ha certificado seguridad o accesibilidad.

## Ensayo de comprensión personal

Sin leer el guion, predecir qué responde SAP cuando otro agente pide el ID 6, cuando falta CSRF, cuando dos revisiones intentan sustituir la misma fila y cuando una corrección antigua llega después de un periodo posterior. Abrir luego el archivo y señalar el queryset, la validación o el servicio que sustenta la explicación.

Explicar por separado mejoría, meta alcanzada y cierre; transacción, bloqueo y revisión obsoleta; sesión, CSRF y permiso. Dibujar el recorrido de un GET y un POST. Relacionar una decisión con su prueba y su límite, en lugar de enumerar tecnologías.

Los fallos controlados se ensayan en local o con datos ficticios expresamente preparados. No improvisar migraciones, cambios de permisos o borrados en Production para responder una pregunta. Si se desconoce un detalle, reconocerlo y buscar la condición concreta sin inventar una respuesta.

## Antes de la convocatoria — intervención del autor

Comprobar cámara, audio, duración, enlaces, acceso privado a las cuentas, servicio activo y código del SHA evaluado. Revisar el expediente/confirmación docente mediante sus justificantes. Preparar un PDF local por contingencia y mantener la URL durante revisión y defensa. La convocatoria y evaluación corresponden al equipo académico; este documento no afirma que hayan ocurrido.
