# Preparación de la defensa de SAP

La guía fija un máximo de **20 minutos**, incluyendo preguntas. Propuesta de exposición: **11 minutos**, con 9 minutos reservados para el tribunal. El guion debe adaptarse al formato que indique el docente. Material preparado; ensayo oral y defensa no realizados.

## Exposición

| Tiempo | Bloque | Qué mostrar y explicar |
| --- | --- | --- |
| 0:00–1:30 | A. Problema y objetivos | Seguimiento entre desviación y cierre; experiencia del autor, independencia de SAP y datos ficticios |
| 1:30–3:00 | B. Arquitectura | Diagrama, apps Django, sesiones, React/Fetch y PostgreSQL; recorrido de una petición |
| 3:00–6:30 | C. Demostración | Dashboard, vendedor, plan de apoyo abierto, acciones, dos revisiones y cierre; separar medición de estado |
| 6:30–8:00 | D. Seguridad | Mostrar `visible_sellers`, permiso de cierre, CSRF y transacción; no mostrar secretos |
| 8:00–9:30 | E. Decisiones y pruebas | `revision`, idempotencia, políticas versionadas; resultados reales y entorno de cada prueba |
| 9:30–11:00 | F. Reflexión | Utilidad esperada, lo no medido, límites del MVP y mejoras futuras |
| 11:00–20:00 | Preguntas | Navegar al código solicitado y razonar desde el caso concreto |

Preparar un plan abierto para interactuar y otro cerrado para consultar histórico si falla una operación. Si no hay producción, reconocerlo y mostrar local sólo como contingencia; no sustituye la URL pública obligatoria. Tener el PDF, el commit evaluado y los resultados de QA a mano.

## Preguntas probables y respuestas que se pueden explicar con palabras propias

### 1. ¿Por qué elegiste Django?

«Necesitaba autenticación, permisos, modelos, migraciones y administración. Django permite construir ese conjunto de forma coherente. Además, es requisito del PFM. En SAP su utilidad se ve en las FK protegidas, las validaciones y el cierre transaccional, no sólo en servir endpoints». Mostrar `backend/action_plans/models.py` y `backend/config/urls.py`.

### 2. ¿Qué aporta React?

«Facilita gestionar el flujo del agente sin entrar en Admin: conserva el contexto del formulario, presenta errores de campo y actualiza el detalle con la respuesta persistida». Mostrar `frontend/src/pages/PlanDetail.jsx`. La regla de negocio sigue en Django.

### 3. ¿Cómo se comunica React con Django?

«Fetch llama a `/api/` en el mismo origen con la cookie de sesión. DRF devuelve JSON. La vista usa esa respuesta para representar datos y, al guardar, sustituye su estado por el detalle devuelto». Mostrar `frontend/src/services/api.js`, `frontend/src/components/ui.jsx` y Network con una respuesta ficticia sin cabeceras privadas.

### 4. ¿Dónde están las plantillas Django que exige la guía?

«En `backend/templates/` están el portal y el login. La vista `dashboard` renderiza el índice compilado de React. Django sigue controlando la entrada a la aplicación». Mostrar `backend/config/views.py` y `backend/templates/registration/login.html`.

### 5. ¿Cómo funciona la autenticación?

«El formulario Django comprueba la contraseña hasheada y establece una sesión. El navegador conserva su cookie y DRF utiliza `SessionAuthentication`. No guardo contraseñas ni un JWT en React». Mostrar `backend/config/settings.py`; las sesiones duran ocho horas.

### 6. ¿Qué protección utiliza frente a CSRF?

«Una cookie de sesión puede enviarse automáticamente. Para una escritura también exijo el token CSRF. React lo recibe del endpoint workspace y lo manda como `X-CSRFToken`; login y logout usan la protección de Django». Mostrar `api.js` y la prueba de 403 sin token en `scripts/verify_browser.py`.

### 7. ¿Cómo se controlan los permisos de cada agente?

«Primero compruebo grupo o superusuario, después filtro vendedores por `owner`. Los planes derivan de ese ámbito y exigen permisos por operación. Ocultar un botón ayuda a la interfaz, pero la seguridad está en el backend». Mostrar `backend/sellers/models.py`, `permissions.py`, `backend/action_plans/views.py`.

### 8. ¿El responsable del plan recibe acceso automáticamente?

«No. Es un dato operativo. El acceso depende del propietario del vendedor. Si se reasigna el vendedor, el nuevo agente puede consultar su histórico y los autores permanecen». Mostrar `visible_plans()` en `services.py` y `PlanWriteSerializer`.

### 9. ¿Por qué PostgreSQL en producción?

«La base debe sobrevivir al redeploy de la web y necesito bloqueos de fila reales para las escrituras concurrentes. SQLite simplifica el arranque local, pero sus pruebas no demuestran esa concurrencia». Mostrar `backend/config/settings.py` y `backend/action_plans/test_concurrency.py`.

### 10. ¿Qué ocurre si dos usuarios modifican el mismo plan?

«La transacción bloquea vendedor y plan para serializar la operación. Además, React envía la revisión que leyó: si ya cambió, recibe 409 y debe recargar. Son dos problemas distintos: concurrencia durante la escritura y formulario desactualizado». Mostrar `concurrency.py`. Aclarar que la revisión es opcional para clientes antiguos, que pierden esa detección adicional.

### 11. ¿Y si se pierde la respuesta y el usuario reintenta crear?

«Para planes y acciones React conserva una clave UUID con el mismo contenido. Si el servidor ya guardó esa solicitud, devuelve el registro existente. Reutilizar la clave con otro contenido produce conflicto». Mostrar `request_identity`, `previous_request` y `request_key`. Claves distintas o clientes sin cabecera pueden crear operaciones distintas.

### 12. ¿Cómo conservas las revisiones históricas?

«Cada revisión es una fila nueva vinculada al objetivo y con autor impuesto por el servidor. La API sólo permite añadirlas y los modelos impiden modificarlas por las rutas soportadas. Las FK protegidas conservan sus referencias». Mostrar `PlanReview` y `PlanChild`. Reconocer que SQL directo puede eludir controles de aplicación.

### 13. ¿Cómo determinas si un indicador ha mejorado?

«Comparo la última revisión evaluable con el valor inicial según dirección: incidencias y tiempos deben bajar; otros indicadores deben subir. Mejorar exige cambio estricto, alcanzar la meta admite igualdad. Para MQC verifico periodo y pedidos antes de concluir». Mostrar `evaluate_metric()` y `quality/services.py`.

### 14. ¿Qué pasa si la última revisión no tiene datos suficientes?

«Muestro no evaluable. No recupero una revisión favorable anterior para fingir un resultado actual. En un plan con varios indicadores todos deben ser evaluables y alcanzar la meta para éxito global». Mostrar `evaluate_plan()` y el orden de `PlanReview.Meta`.

### 15. ¿Por qué se puede cerrar con acciones pendientes?

«Cerrar documenta una decisión de seguimiento. La ejecución y la medición se conservan por separado. Puedo cerrar sin éxito o con trabajo pendiente, pero debo indicar razones y guardar la evaluación real». Mostrar `close_plan()` y la captura del caso ficticio.

### 16. ¿Qué ocurre si falla una operación de cierre?

«El cierre se ejecuta en una transacción. Si falla validación o guardado, se revierte; no queda un estado final con una instantánea a medias. Los bloqueos también impiden que una revisión se añada después de finalizar». Mostrar `@transaction.atomic` y las pruebas de doble cierre/revisión contra cierre.

### 17. ¿Por qué versionar políticas?

«Una observación histórica debe conservar la regla con la que fue registrada. La política utilizada no se edita mediante las rutas normales; para futuras observaciones se crea otra versión». Mostrar `ThresholdPolicy.clean()`. No existe selección automática por fecha de vigencia.

### 18. ¿Por qué no se actualiza el indicador global al revisar un plan?

«La revisión pertenece al seguimiento del objetivo. `QualityMetric` es una observación global administrada aparte. Mezclarlas automáticamente ocultaría su procedencia; por eso puede persistir una desviación global histórica tras cerrar un plan». Mostrar relaciones de `PlanReview` y `PlanMetric`.

### 19. ¿Qué pruebas has implementado?

«Reglas de frontera, fechas y transiciones; API, permisos y CSRF; rollback e histórico; reintentos y conflictos; ocho carreras reales en PostgreSQL; cliente Fetch y recorrido Chromium. En Fase 4 pasan 77 pruebas Django en total, no 77 más ocho». Mostrar `docs/evidencias-fase-4.json` y una prueba relevante, evitando enumerarlas sin explicar qué comprueban.

### 20. ¿Cómo sabes que los datos persisten?

«En QA guardé un plan, reinicié base y servidor, repetí release y comparé huellas de registros. También restauré un dump en otra base y comprobé igualdad. Es evidencia local; la misma validación tras redeploy público está pendiente». Mostrar `scripts/verify_phase3.py`. Actualizar esa última frase sólo tras completar el acta remota.

### 21. ¿Qué protege frente a XSS e inyección SQL?

«React y las plantillas muestran texto escapado; no interpreto HTML del usuario. Las consultas del flujo usan ORM parametrizado. Además valido entradas en Django. No presento esto como garantía absoluta frente a cualquier vulnerabilidad». Mostrar campos textuales y `api.js`.

### 22. ¿Qué limitaciones tiene SAP?

«Las observaciones son manuales; no hay integración, correo ni adjuntos. El detalle de un histórico muy grande no está paginado y no he medido beneficio empresarial. Falta la aceptación pública y el vídeo para entregar». Mostrar `docs/trazabilidad-requisitos.md`; retirar pendientes sólo con evidencia.

### 23. ¿Por qué SAP no sustituye a Mirakl?

«No gestiona pedidos, catálogo, pagos ni suspensiones. Organiza el trabajo posterior a detectar una desviación. El objetivo es conservar acciones y resultados, no replicar la plataforma de marketplace».

### 24. ¿Qué mejorarías si dispusieras de más tiempo?

«Primero validaría el flujo con agentes y mediría utilidad. Después estudiaría una importación autorizada que preserve procedencia y periodos. Las notificaciones o informes deberían responder a una necesidad comprobada». Son posibilidades, no funcionalidades actuales.

### 25. ¿Qué parte puedes modificar o explicar en directo?

«Puedo seguir una petición desde la página React, pasar por API y permisos, y localizar el modelo y servicio que la resuelven. Antes de cambiar una regla identificaría qué test protege su frontera». Ensayar explicar `evaluate_metric()` con 6, 4,5 y 3, y localizar el 409 por revisión sin ejecutar cambios improvisados en producción.

## Ensayo de comprensión

Explicar sin leer por qué 4,5 mejora pero no alcanza la meta; por qué cerrar no completa acciones; por qué un ID no concede acceso; por qué CSRF y autenticación son diferentes; por qué pasar pruebas SQLite no demuestra bloqueo PostgreSQL. Después abrir el archivo correspondiente y señalar la condición concreta.

Practicar un fallo controlado en local: meta 7% para incidencias iniciales 6%, o escritura sin CSRF. Explicar el mensaje y cómo se corrige, sin alterar el entorno público. Ensayar el recorrido de API con JSON real, no un ejemplo inventado en un editor.

Antes de la videollamada: confirmar cámara/audio, enlaces, credenciales privadas, servicio activo y commit evaluado. Mantener una copia local de PDF y capturas como apoyo, sin presentarlas como disponibilidad remota. Si una pregunta excede lo implementado, describir el límite y dónde se introduciría el cambio, sin atribuir funciones inexistentes.
