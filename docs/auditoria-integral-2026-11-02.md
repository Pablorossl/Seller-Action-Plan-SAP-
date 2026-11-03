# Auditoría integral de Seller Action Plan

Fecha: **2 de noviembre de 2026**. Código local: **`54ac2cd`**. Rama: `main`. Remoto comprobado: **`57d296f1a9cee56c925acec485b3d1bae5953cef`**. El árbol estaba limpio al comenzar; el commit local de adaptación Vercel/Neon no está publicado. Este informe describe comprobaciones nuevas, no traslada automáticamente los resultados de fases anteriores.

**Dictamen: SAP tiene un MVP funcional y verificable localmente, pero todavía no constituye una entrega académica completa.** El recorrido principal funciona con datos ficticios precargados. Faltan aplicación pública funcional, vídeo y sincronización de la versión de entrega. Hay tres problemas de fiabilidad funcional reproducidos que conviene resolver antes de consolidar esa versión.

Se consultó directamente la guía oficial mediante Google Drive. La denominación es **Proyecto Final de Máster (PFM) del Máster en Desarrollo Full Stack**. La guía no lo denomina TFG. Durante esta auditoría, Pablo confirmó que ha aprobado las actividades obligatorias de Prework, Frontend y Backend y que tiene autorización docente para iniciar el PFM. Se registra como declaración del autor; no se ha inspeccionado su expediente. También confirmó que todavía no existe vídeo ni una URL alternativa de la aplicación.

## A. Estado general y alcance

| Área | Estado real |
| --- | --- |
| Producto local | Implementado y comprobado: login/logout, cartera por agente, indicadores, dashboard, ficha, planes, objetivos, acciones, revisiones, evaluación y cierre |
| Persistencia e integridad local | Migraciones desde cero, 79 pruebas PostgreSQL, concurrencia, reinicios y restauración separada correctos |
| React/API/Django | Escrituras y lecturas reales comprobadas en Chromium; errores de validación, CSRF y aislamiento comprobados |
| Fiabilidad funcional | Parcial: rectificación de revisiones bloqueada, observaciones futuras admitidas y vencimientos históricos recalculados; detalles en C |
| Publicación | Pendiente: el dominio indicado devuelve 404 de Vercel, no una respuesta de SAP |
| Neon existente | Conectividad directa y pooled con TLS; no aparecen las cinco tablas SAP/Django buscadas. No se verificó pertenencia a proyecto/rama |
| Repositorio y CI | GitHub público. CI aprobada para `57d296f`. El código local `54ac2cd` no tiene ejecución remota comprobable porque no está publicado |
| Documentación | Amplia y aprovechable, pero memoria, arquitectura y guiones conservan el destino Render y resultados anteriores |
| Evidencias | PDF de 30 páginas, 16 capturas indexadas, cuatro diagramas y JSON; son evidencias locales históricas. Se generaron nuevas capturas locales durante esta auditoría |
| Vídeo y defensa | Guiones disponibles. Vídeo inexistente según el autor. Comprensión, ensayo oral y defensa no comprobados |
| Requisitos administrativos | Aprobaciones y autorización confirmadas por el autor en esta conversación; no verificadas documentalmente |

La inspección abarcó las apps Django `sellers`, `quality`, `action_plans` y `config`; modelos, migraciones, servicios, serializadores, vistas, Admin y pruebas; React y su cliente HTTP; configuración y scripts; workflow de CI; documentación, memoria, diagramas y evidencias. No se encontraron instrucciones `AGENTS.md` aplicables en el proyecto o sus directorios superiores. **No existe `sources/` en este checkout** y no se alteró material de referencia. Se conservaron los informes antiguos.

No se modificó funcionalidad, esquema, secretos ni archivos de entorno. No hubo commits, push, despliegues, cambios de datos externos, contratación ni comunicaciones con terceros. Sólo se añadieron este informe y artefactos locales de auditoría; se regeneraron compilados ignorados por Git. Las bases usadas para pruebas fueron temporales y ficticias. Los scripts de QA detuvieron y eliminaron sus instancias PostgreSQL.

### Fuentes y significado de los estados

- **G — requisito explícito:** [guía oficial del PFM](https://docs.google.com/document/d/1KhmvNgC4g9WI8suPOBjGFcUCQeA8rVPkoVS53fYLOkQ/edit), leída completa en esta sesión; modificación comunicada por Drive: 08/10/2026.
- **S — criterio propio de SAP:** necesidad del encargo, [dominio](dominio.md), modelo y flujo implementados. Las fuentes públicas funcionales orientan el diseño; no son requisitos de la academia ni certifican una integración corporativa.
- **R — recomendación:** mejora derivada de esta revisión; no se convierte en requisito académico por aparecer aquí.
- **C — confirmación:** afirmación del autor o cuestión que necesita verificación externa.

«Verificado localmente» no implica aceptación pública. «Histórico» identifica evidencia de otra revisión. «No comprobado» no significa necesariamente que el elemento falle.

## B. Matriz de trazabilidad

Las ubicaciones citan archivos y símbolos o apartados concretos. Las reproducciones nuevas están en `artifacts/audit-2026-11-02/`, ignorado por Git; su resumen se conserva en [evidencias de esta auditoría](evidencias-auditoria-2026-11-02.json).

| Requisito o necesidad | Fuente | Estado | Evidencia concreta | Pendiente |
| --- | --- | --- | --- | --- |
| Denominación y programa | G, portada de la guía | Verificado directamente | Guía: PFM, Máster en Desarrollo Full Stack | Usar PFM de forma uniforme; algún commit histórico dice TFM |
| Actividades previas y autorización docente | G, procedimiento §1; C | Confirmado por el autor | Respuesta de Pablo durante esta sesión | Conservar confirmación para trámites; expediente no inspeccionado |
| Backend Django: modelos, vistas, plantillas | G, mínimos 1 | Verificado localmente | [Modelos de planes](../backend/action_plans/models.py), [rutas](../backend/config/urls.py), [vistas HTML](../backend/config/views.py), `backend/templates/` | Demostrar la misma versión publicada |
| Autenticación y persistencia | G, mínimos 1 | Verificado localmente | [settings](../backend/config/settings.py), `SessionAuthentication`; pruebas `sellers.tests` y `config.tests`; QA de reinicios | Login, sesiones y continuidad remotos |
| Una o dos vistas React con datos del backend | G, mínimos 2 | Verificado; supera el mínimo de vistas | [Workspace](../frontend/src/pages/Workspace.jsx), [PlanDetail](../frontend/src/pages/PlanDetail.jsx), [api.js](../frontend/src/services/api.js); navegador y JSON | Mostrarlo en el vídeo real |
| Flujo funcional de datos | G, objetivos; S | Verificado en el caso nominal | QA: creación y cierre de un plan nuevo, dos acciones, dos revisiones, recarga del mismo ID | Resolver recuperación de una revisión incompleta y repetir el flujo en público |
| URL pública estable | G, mínimos 3 y entrega 2 | No cumplido actualmente | GET HTTPS a `/`, `/accounts/login/`, `/healthz/`, `/api/plans/`: 404 `NOT_FOUND` | Publicar y completar aceptación pública |
| Mantener la app durante revisión y defensa | G, entrega 2 | Pendiente | [Acta pública](verificacion-publica.md) sin aceptación; app no disponible | Fijar periodo de operación y comprobar disponibilidad durante él |
| GitHub accesible, README e historial significativo | G, mínimos 4 y entrega 1 | Cumplido para la versión remota anterior | [Repositorio público](https://github.com/Pablorossl/Seller-Action-Plan-SAP-), historial por fases, README; API pública `private=false` | Publicar posteriormente la versión final y verificar su acceso |
| CI del código entregado | S/R; la guía no exige GitHub Actions literalmente | Parcial | [Run 40754122404](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/40754122404): `success`, SHA `57d296f` | CI del SHA definitivo; no atribuir este éxito a `54ac2cd` |
| Instalación reproducible | G, README; S | Verificada en Linux | Exportación de HEAD sin `.env` ni dependencias; venv nuevo, pip install/check, npm ci, build y migraciones correctos | Windows/macOS y builder remoto no ensayados |
| Arquitectura y dependencias coherentes | G, estructura/rúbrica | Código coherente; documentación parcial | Monolito modular, ORM, API con sesiones, locks y configuración separada; [build Vercel](../backend/build_vercel.py) | Actualizar memoria y diagrama al destino elegido |
| Problema, contexto, impacto y solución | G, estructura §1 | Documentado | [Memoria](memoria-pfm.md), §§1–2 | Revisión personal del autor y versión final |
| Reflexión, aportación y eficiencia | G, estructura §2 | Documentado con límites apropiados | Memoria §§3 y 15; beneficios esperados separados de impacto medido | Defender argumentos propios; no inventar ahorro empresarial |
| Tecnologías justificadas | G, estructura §3 | Parcialmente actualizado | Memoria §5; requirements y lockfiles efectivos | Sustituir explicación del hosting anterior y actualizar resultados |
| Usuarios y permisos descritos | G, estructura §4; S | Implementado y probado | [visible_sellers](../backend/sellers/models.py), [IsMarketplaceAgent](../backend/sellers/permissions.py), [PlanViewSet](../backend/action_plans/views.py); memoria §8 | Explicar que responsable del plan no otorga acceso |
| Aislamiento entre agentes | S; soporte de seguridad G | Verificado en rutas probadas | Tests de API/Admin y Chromium: plan ajeno devuelve 404, anónimo/sin rol 403 | Repetir con dos agentes ficticios públicos |
| Acceso del vendedor externo | S, alcance del MVP | Fuera de alcance deliberadamente | No existe rol ni portal seller; `Seller` es un registro de dominio | No presentarlo como funcionalidad pendiente exigida por la guía |
| Casos de uso con errores y resultados | G, estructura §5 | Documentado y contrastado | Memoria §9, CU01–CU09; pruebas API y navegador | Añadir límites detectados de rectificación y preparar demo final |
| Seguridad: hashing, validación, CSRF/XSS, secretos, HTTPS, copias | G, estructura §6 | Controles locales verificados; remoto pendiente | `config/tests.py`, `config/test_vercel.py`, permisos, escape, `check --deploy`, copia/restauración | Certificado/proxy/CDN reales y recuperación remota |
| Límites de indicadores | S, fuentes funcionales y dominio | Código y fronteras comprobados | [rules.py](../backend/quality/rules.py), [classify](../backend/quality/services.py), `quality/tests.py` | Mantener fecha de referencia; no interpretar observación histórica como estado actual |
| Indicadores observados frente a calculados | S | Separación correcta; riesgo temporal detectado | Valores manuales; SAP calcula clasificación/comparación, no indicadores sobre pedidos; prueba de observación futura aceptada | Impedir fechas futuras de observaciones o distinguirlas expresamente |
| Diagnóstico y varios objetivos | S | Implementado y probado | `ImprovementPlan`, `PlanMetric`, `PlanWriteSerializer`; pruebas multiindicador y transacción atómica | Asegurar datos iniciales y políticas en el entorno de evaluación |
| Acciones, responsables y evidencia | S | Implementado | `PlanAction.clean`, `ActionForm`; completar exige fecha y evidencia | No hay vínculo de cada acción a un objetivo concreto; basta el vínculo al plan para el MVP actual |
| Revisiones trazables y recuperación ante errores | S/R | Parcial | Autor y registro históricos; `PlanReview` impide cambios y duplicados; reproducción: 201 sin datos, 400 al completarlos en el mismo periodo | Definir rectificación conservando original, motivo y autor |
| Evaluación y cierre | S | Caso nominal verificado; presentación histórica parcial | `evaluate_metric`, `evaluate_plan`, `close_plan`; `closure_evaluation` conserva instantánea | Mostrar vencimientos al cierre sin confundirlos con cálculo de hoy |
| Memoria PDF o Word | G, entrega 3 | Existe, requiere actualización | [PDF](memoria-pfm.pdf): 30 páginas, 13 imágenes incrustadas, 26 enlaces; [Markdown](memoria-pfm.md) | Regenerar tras fijar versión y aceptación pública |
| Capturas, diagramas y ejemplos | G, entrega 3 | Existen y son trazables localmente | [Índice visual](evidencias-visuales.md), cuatro SVG, JSON React-Django; 38 hashes históricos cotejados sin discrepancias | Actualizar arquitectura, fechas y versión; evidencias públicas separadas |
| Vídeo ≤5 minutos y enlace accesible | G, entrega 4; C | Falta | [Guion 4:50](guion-video-pfm.md); autor confirma ausencia de vídeo | Grabar, revisar duración y contenido, publicar después y probar acceso docente |
| Defensa ≤20 minutos y comprensión | G, defensa | Material preparado, ejecución no comprobada | [Preparación](preparacion-defensa.md), exposición y 25 preguntas | Ensayo real y defensa; corregir explicación de última revisión |
| Cuatro entregables coherentes | G, procedimiento | Incompleto | Repositorio y PDF existentes; app pública y vídeo ausentes | Unificar SHA, URLs, memoria, demo y acceso |

La guía exige **repositorio, aplicación, memoria PDF/Word y vídeo accesible**. El vídeo debe incluir contexto, demostración, tecnologías y consumo de datos Django desde React. No exige dominio propio; Docker es opcional. No fija una extensión ni un número de páginas para la memoria. En mínimos habla de GitHub público y en el procedimiento admite público o compartido con docentes: el repositorio público comprobado satisface ambas formulaciones. No se encontró una fecha concreta de entrega ni un canal personal de envío en esta guía; confirmar esos datos con la convocatoria.

La rúbrica pondera backend 30%, React 15%, arquitectura 15%, seguridad/integridad 15%, documentación/presentación 15% y reflexión 10%; fija aprobado en 7/10. **No se estima una nota ni un porcentaje de avance.** La revisión inicial precede a la reserva de defensa; la guía prevé una defensa por trimestre y feedback hasta diez días hábiles después. [Fuente académica original](https://docs.google.com/document/d/1KhmvNgC4g9WI8suPOBjGFcUCQeA8rVPkoVS53fYLOkQ/edit).

## C. Recorrido del Account Manager / Marketplace Support Agent

El flujo es comprensible: prioridades → vendedor → indicador con contexto → diagnóstico y objetivo → acciones → revisiones → resultado y cierre. La interfaz muestra fechas, canal, volumen y política; presenta estados de carga, vacíos, errores y denegaciones; conserva formularios cuando Django rechaza una meta incorrecta. El caso Chromium ejecutado pasa tanto en configuración habitual como con `VERCEL=1`, siempre localmente.

| Paso | Evaluación operativa |
| --- | --- |
| Entrada | Login Django, sesión y logout funcionan. No hay autorregistro: la cuenta se prepara administrativamente |
| Cartera y prioridades | Se limita al agente. Acciones vencidas y revisiones pendientes ayudan a priorizar. Los pendientes de planes finalizados salen del trabajo activo por decisión explícita |
| Ficha e indicadores | Se ven observaciones reales de la base y se accede a planes e histórico. La última observación disponible puede ser antigua |
| Creación | Diagnóstico, evidencia, causa, objetivo general y meta numérica coherentes. Los indicadores deben corresponder al vendedor y periodo; alta atómica |
| Activación y acciones | Se exige un objetivo y una acción. Acciones correctivas/preventivas, responsables textuales, fechas y evidencia permiten seguimiento operativo |
| Revisiones | Conservan autor y fecha de registro, medición, periodo y valoración humana. La actualización de `next_review_on` es manual desde edición del plan |
| Evaluación | 4,5% mejora sobre 6%, pero no alcanza 3%; 3% alcanza por igualdad. La última revisión se ordena por periodo medido, fecha e ID; si no es evaluable, no se usa una anterior favorable |
| Cierre | Separa resultado medido de decisión administrativa; exige razones, permiso y confirmación. Puede conservar acciones pendientes o cerrar sin éxito. No reabre el plan |

**Dependencia operativa aceptable, pero obligatoria para la demo:** los vendedores y observaciones iniciales deben existir. React permite consultar vendedores y gestionar planes; el CRUD de vendedores está en API y la carga de políticas/observaciones está reservada al superusuario en Admin. Un agente ante una cartera vacía o sin observaciones no puede completar el recorrido por sí solo. Esto está reconocido en el alcance de la memoria y no obliga a desarrollar un importador ni un nuevo módulo; sí obliga a preparar una cuenta docente y datos coherentes.

**Acuerdo con el vendedor:** SAP registra los compromisos mediante el agente, no una aceptación digital del vendedor. El contacto y acuerdo suceden fuera de la aplicación. Debe explicarse así en la defensa, sin presentar el sistema como un portal compartido o una prueba formal de consentimiento.

### Hallazgos reproducidos

**F01 — Una revisión sin datos bloquea la medición posterior del mismo periodo.**

En un plan activo se guardó agosto con `value=null`, `order_count=null`, valoración `no_data`: HTTP 201. Al recibir el dato, un segundo POST de agosto con valor 3 y 100 pedidos devolvió 400 por duplicado. Sólo quedó la primera revisión. El modelo prohíbe editar revisiones y Admin tampoco permite cambiarlas ni borrarlas. La misma dificultad afecta a una errata de una revisión ya guardada.

Ubicación: [PlanReview](../backend/action_plans/models.py), líneas 262, 285 y 303; [API de revisiones](../backend/action_plans/views.py), `add_review`; [formulario](../frontend/src/pages/PlanDetail.jsx), `ReviewForm`, línea 317. Reproducción: `probe_domain.py` y `domain-probes.json` de esta auditoría.

Impacto: bloquea un caso real de seguimiento, aunque la demostración nominal con datos completos pase. No conviene resolverlo sobrescribiendo o borrando el histórico. Propuesta para decidir antes de desarrollar: rectificación explícita vinculada a la original, con motivo, autor y elección clara de la medición efectiva; reintentos idénticos deben continuar sin duplicar mediciones.

**F02 — Una observación futura puede desplazar los indicadores disponibles.**

El 02/11/2026 se guardó por el modelo una observación ficticia de enero de 2027. `save()`/`full_clean()` la aceptaron; `/api/metrics/?latest=1` la seleccionó y la clasificó `ok`. El modelo valida orden de fechas, pero no que la observación haya ocurrido. El clasificador comprueba mensualidad y volumen, no actualidad. Un error administrativo podría ocultar una desviación pasada en el resumen.

Ubicación: [QualityMetric.clean](../backend/quality/models.py), línea 98; [latest_metrics](../backend/quality/views.py), línea 10. Sólo el administrador registra observaciones por las interfaces previstas: no se trata de una escritura anónima. Recomendación: rechazar periodos futuros para datos observados, con prueba de frontera «hoy», y revisar una posible base existente antes de añadir restricciones.

**F03 — El contador de vencidas de un plan cerrado cambia después del cierre.**

Se cerró un plan con una acción pendiente cuyo plazo era mañana: instantánea con cero vencidas. Al simular tres días después, GET del mismo plan conservó `closure_evaluation.overdue_actions=0`, pero devolvió `evaluation.overdue_actions=1`. React muestra este último número como vencidas «en el histórico». La instantánea almacenada está intacta; el problema es la mezcla de cálculo actual y presentación histórica.

Ubicación: [PlanAction.is_overdue](../backend/action_plans/models.py), línea 237; [evaluate_plan](../backend/action_plans/services.py), línea 44; [PlanDetailSerializer.get_evaluation](../backend/action_plans/serializers.py), línea 106; [PlanDetail](../frontend/src/pages/PlanDetail.jsx), línea 677. Solución recomendada: usar la evaluación del cierre para el resumen histórico, o distinguir expresamente «al cierre» y «a fecha de hoy».

**F04 — La observación global y la revisión del plan son fuentes distintas.**

Reproducción: el plan alcanzó 3% en septiembre, mientras la ficha conservó 6% de julio con clasificación `suspension_threshold`. Es una decisión documentada en memoria §7, no un error de persistencia: `PlanReview` no actualiza `QualityMetric`. La interfaz ya muestra fechas y advierte del carácter registrado de los datos. Aun así, «Actualizado al [hoy]» en el dashboard puede confundirse con actualidad de las mediciones. Conviene indicar que se ha calculado hoy el resumen de observaciones disponibles y explicar cómo se incorpora una nueva observación global. No actualizar automáticamente una fuente desde la otra sin definir procedencia.

### Reglas contrastadas

Los límites del código coinciden con la fuente pública consultada: aceptación alarma `<99%`/umbral `<98%`; incidencias `≥4%`/`≥5%`; seguimiento `<91%`/`<90%`; tiempos de aceptación y respuesta `≥20 h`/`≥24 h`. MQC requiere canal, mes y al menos 30 pedidos. Las pruebas comprueban fronteras y 0/29/30 pedidos. [Criterios oficiales de referencia](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/20561228339357-criterios-de-calidad-automatizados).

NPS y entrega se tratan aparte, con referencias de 65 y 90 respectivamente, sin suspensión automática. SAP admite NPS entre −100 y 100 y almacena el valor observado; no calcula encuestas ni entregas desde pedidos. [NPS y eficiencia de entrega](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/37487009483805-NPS-y-eficiencia-de-entrega).

El algoritmo de mes natural/ventana móvil con extremos incluidos es una **convención de SAP**, no una regla interna de Mirakl verificada. Las políticas tienen versiones; la selección de nuevas versiones es manual. Problema, causa, acciones, responsables, plazos y revisión se ajustan al proceso descrito en la [referencia pública sobre planes](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/38119386983965-como-mejorar-tus-indicadores-de-calidad-y-preparar-un-plan-de-accion). Las consecuencias administrativas del marketplace quedan fuera de SAP.

## D. Pendientes priorizados

### 1. Bloqueos para cumplir requisitos o demostrar el flujo central

| ID y origen | Qué falta y por qué importa | Cómo verificar resolución | Dependencia |
| --- | --- | --- | --- |
| B1 · G | App pública funcional. Cuatro rutas del dominio devuelven 404; Neon no tiene las tablas buscadas. Sin ello falta un entregable obligatorio | Confirmar proyecto/rama/base; preparar configuración y esquema posteriormente; login real, dashboard, API, flujo completo y `/healthz/` 200 en HTTPS público | Pablo y servicios Vercel/Neon; publicación fuera de esta auditoría |
| B2 · G | Vídeo real accesible ≤300 s. El guion no es el entregable | Reproducir archivo completo: contexto, demo, tecnologías y React/API; duración real; abrir enlace como docente | Pablo y servicio de alojamiento del vídeo |
| B3 · G/S | Código final disponible y entorno docente con datos. El remoto no contiene la adaptación de hosting y una cuenta vacía no demuestra el MVP | SHA público igual al desplegado; CI del mismo SHA; agente sin Admin con vendedor, observaciones y permisos; segundo agente de comprobación | Pablo, GitHub y hosting |

El recorrido nominal local no necesita nuevos módulos para satisfacer su objetivo. B1–B3 son bloqueos reales de entrega. F01 es un bloqueo de un caso de seguimiento específico, tratado como fiabilidad prioritaria a continuación.

### 2. Fiabilidad, seguridad y despliegue

| ID y origen | Qué falta y por qué importa | Cómo verificar resolución | Dependencia |
| --- | --- | --- | --- |
| R1 · S/R, alta | Resolver F01: completar/corregir medición del mismo periodo sin destruir el original | Caso sin datos → dato recibido; corrección de errata; autor/motivo; cálculo efectivo; doble reintento; rechazo tras cierre y a agente ajeno | Decisión funcional de Pablo e implementación local; no requiere docente ni servicios nuevos |
| R2 · S/R | Resolver F02: una observación no puede afirmar resultados futuros | API/modelo/Admin rechazan fecha futura; admiten fecha de hoy; última observación sigue siendo válida | Implementación local |
| R3 · S/R | Resolver F03: resumen histórico coherente con cierre | Congelar reloj antes/después del plazo; representación del cierre no cambia y sigue coincidiendo con `closure_evaluation` | Implementación local |
| R4 · S | Normalizar configuración Neon. `DATABASE_URL` es directa, existe `DATABASE_URL_POOLED`, falta `DATABASE_URL_UNPOOLED`; el comando de migración no puede planificar | Confirmar destino sin mostrar claves; app usa pooled y administración directa de la misma base; `neon_manage.py migrate --plan` lista operaciones previstas | Pablo para confirmar proyecto/rama; servicio Neon. No aplicar `neon deploy` por rutina sólo para migrar Django |
| R5 · G/S | Acreditar seguridad y recuperación reales: ajustes locales no prueban proxy/CDN, continuidad, redeploy ni backup del proveedor | Acta pública: HTTPS, cookies, CSRF, aislamiento, estáticos, mismo ID tras redeploy sin resembrar, restauración separada y retención documentada | Hosting, Neon y Pablo; ventana concreta de aceptación |
| R6 · S/R | Explicar F04 y la preparación administrativa del dato. Riesgo de confundir fecha del resumen con periodo observado | Un evaluador identifica fuente, canal y periodo; sabe por qué plan y ficha difieren y cómo cargar la siguiente observación | Ajuste de textos/procedimiento; no requiere integración Mirakl |

La guía exige analizar copias y medidas de seguridad; el protocolo detallado de 18 comprobaciones, la comparación de IDs tras redeploy y las pruebas de concurrencia son criterios de aceptación de SAP, no una lista literal de la academia. No se descubrió acceso cruzado en las pruebas ejecutadas. Esto no equivale a una auditoría de penetración exhaustiva.

### 3. Documentación, evidencias y entrega

| ID y origen | Qué falta y por qué importa | Cómo verificar resolución | Dependencia |
| --- | --- | --- | --- |
| D1 · G/S | Actualizar memoria, PDF, arquitectura y guiones al alojamiento real; ahora describen Render/Gunicorn y 77 pruebas | Mismo SHA, arquitectura, versiones, resultados, URL y pendientes en todos los materiales; regenerar PDF desde Markdown y revisar paginación/legibilidad | Trabajo local y aceptación pública previa para las afirmaciones remotas |
| D2 · S | Distinguir informes históricos de referencia actual. `fase-4.md` aún dice sin commit/push; README y matriz sólo acreditan CI de Fase 3 | Índice identifica fecha/versión; se enlaza CI `57d296f` y luego la final; no reescribir informes históricos como si fueran pruebas nuevas | Trabajo local |
| D3 · G/R | Corregir defensa pregunta 13: dice «última revisión evaluable», aunque el código toma la última y puede devolver no evaluable; la pregunta 14 sí lo explica bien | Explicación uniforme demostrada con última revisión sin datos; 79 pruebas actuales, incluidas ocho de concurrencia | Pablo y edición documental |
| D4 · G | Ensayo oral, acceso docente, cuatro enlaces y datos de convocatoria | Ensayo ≤20 min; explicar una petición, permiso, validación y cierre desde código; abrir materiales desde sesión independiente; confirmar fecha/canal académico | Pablo; docente para procedimiento y convocatoria, no para reaprobar requisitos ya confirmados |

La memoria actual es una versión histórica coherente con buena parte del producto, pero no una memoria final del despliegue elegido. Su PDF contiene siete menciones a Render y ninguna a Vercel/Neon. El diagrama `arquitectura.svg` conserva «Render HTTPS → Gunicorn (propuesto)». El guion de vídeo también narra Gunicorn/WhiteNoise como arquitectura productiva y menciona 77 tests. `docs/arquitectura.md` necesita actualizarse o etiquetarse inequívocamente como antecedente.

La falta de una auditoría general de ediciones de diagnóstico/acciones está reconocida. Las revisiones y planes finalizados conservan historial por las rutas admitidas; no debe afirmarse que toda modificación previa al cierre queda auditada. Los campos de evidencia son texto, no documentos adjuntos.

### 4. Mejoras opcionales

- Evaluación de usabilidad con un agente y un escenario ficticio; medir comprensión antes de ampliar funcionalidades. No se ha demostrado ahorro de tiempo empresarial.
- Revisión de accesibilidad con teclado, lector de pantalla y contraste. Hay etiquetas, estados de error, tablas desplazables y diálogo nativo; la QA de 390 px no acredita WCAG.
- Paginación del detalle cuando existan planes con mucho histórico. Los listados ya paginan; el detalle precarga acciones y revisiones completas.
- Relación explícita acción–objetivo o registro de aceptación del vendedor sólo si la validación funcional demuestra necesidad. No son exigencias académicas explícitas.

No se propone incorporar IA, integraciones externas, notificaciones complejas ni nuevos módulos para completar esta entrega.

## E. Plan de continuidad en pasos verificables

1. **Decidir y cerrar el contrato de rectificación de revisiones.** Usar F01 como caso inicial y acordar cómo se conserva el original y qué dato se evalúa. Finaliza con regla escrita y casos de aceptación, antes de modificar modelos.
2. **Aplicar los ajustes de fiabilidad acordados.** Rectificación, fechas futuras y representación del cierre en cambios acotados. Finaliza con pruebas específicas de regresión y suite existente sin fallos; repetir navegador si cambia la interfaz.
3. **Confirmar destino Neon y separar entornos.** Identificar proyecto, rama y base; normalizar pooled/directa; conservar desarrollo aislado. Finaliza con configuración validada sin exponer secretos y plan de migraciones revisado. Todavía sin escribir datos externos durante la auditoría.
4. **Fijar un candidato de entrega.** Actualizar instrucciones y arquitectura, registrar el cambio y, en una tarea autorizada de publicación, subirlo. Finaliza con SHA público y CI aprobada del mismo código.
5. **Preparar y publicar la demo.** En una tarea posterior autorizada: migraciones, cuentas ficticias, carga inicial y despliegue. Finaliza cuando login, indicadores, plan, acciones, revisiones y cierre funcionan desde Internet.
6. **Completar aceptación operativa.** Probar aislamiento, CSRF, TLS, estáticos, persistencia tras redeploy y recuperación separada; fijar continuidad hasta la defensa. Finaliza con acta de resultados reales, fechas y IDs, no casillas marcadas por inferencia.
7. **Cerrar memoria y vídeo sobre esa versión.** Actualizar Markdown/diagramas, regenerar PDF, seleccionar capturas con procedencia y grabar vídeo ≤5 min. Finaliza con enlaces accesibles y contenidos que coincidan con la app.
8. **Ensayar y entregar.** Confirmar fecha/canal de convocatoria, practicar explicación y fallos controlados, reunir cuatro enlaces y credenciales por canal privado. Mantener el servicio durante revisión y defensa.

**Siguiente paso recomendado:** resolver la decisión funcional de F01 antes de una modificación de alcance mayor. Criterio de finalización del siguiente incremento: registrar una revisión sin medición, aportar después el dato del mismo periodo, conservar ambas entradas con su relación y autoría, evaluar la entrada efectiva y mantener la protección frente a duplicados, cierre y acceso ajeno. No exige ampliar el producto fuera de su seguimiento central.

La confirmación del destino Neon puede avanzar en paralelo por parte de Pablo. No hace falta esperar a nuevas funcionalidades para preparar vídeo, narración o convocatoria, pero la grabación definitiva debe reflejar la versión entregada.

## F. Comprobaciones ejecutadas, limitaciones y confirmaciones

Todos los comandos Django de escritura/pruebas se ejecutaron con variables de proceso que sustituyen la conexión local por SQLite/PostgreSQL temporal. No ejecutar esas pruebas directamente contra el `.env` actual: apunta a Neon. Node utilizado: 22.19.0; Python: 3.12; PostgreSQL local: 14.24.

| Comando o comprobación | Resultado actual | Límite |
| --- | --- | --- |
| `git status --short --branch`, `git log`, `git remote -v` | Árbol inicialmente limpio; `main` un commit por delante; HEAD `54ac2cd` | No se publicó nada |
| `git diff --check` | Correcto | No sustituye revisión funcional |
| `.venv/bin/python -m pip check` | Sin incompatibilidades | Entorno existente; también se comprobó venv limpio |
| `python manage.py check` desde `backend/` | Correcto | Un aviso silenciado deliberadamente: `axes.W006`, documentado y con prueba de bloqueo por usuario |
| `python manage.py makemigrations --check --dry-run` | Sin deriva de modelos | Bases temporales |
| `python manage.py migrate --noinput` y `migrate --check` | Correctos desde base vacía | SQLite y PostgreSQL aislados |
| `python manage.py test --verbosity 2` con SQLite | 79 descubiertos, 71 ejecutados correctamente, ocho omitidos | Omisiones de concurrencia que requieren PostgreSQL |
| `npm test` y `node frontend/src/services/api.test.js` | Correctos; ejecución directa muestra siete casos aprobados | Prueban cliente HTTP, no todos los componentes React |
| `npm run build` | Correcto, 33 módulos | Es compilación, no publicación |
| `python scripts/check_production.py` | Correcto con valores ficticios | No comprueba infraestructura |
| `python scripts/verify_vercel.py` | npm ci/build; paquete aislado, 157 estáticos, plantillas, WSGI sin conexión SQL y comprobaciones HTTP correctas | No ejecuta el builder de Vercel |
| `python3 scripts/verify_phase3.py --pg-bin /usr/lib/postgresql/14/bin --artifacts artifacts/audit-2026-11-02/postgres` | 79/79 en PostgreSQL, incluidas ocho de concurrencia; Chromium y persistencia/restore correctos | TLS local de prueba; no público |
| Mismo comando con `--vercel-settings --artifacts artifacts/audit-2026-11-02/vercel-runtime` | Segunda configuración validada: 79/79 y recorrido completo correctos | Gunicorn sirve de arnés local; no reproduce toda la plataforma Vercel |
| `.venv/bin/python artifacts/audit-2026-11-02/probe_domain.py` | F01–F04 reproducidos sobre SQLite temporal | Código de diagnóstico en artefactos; no se añadieron correcciones funcionales |
| `npm audit --json` en raíz y `frontend/` | Cero avisos conocidos devueltos por ambos análisis | Resultado de hoy, no garantía de ausencia de vulnerabilidades |
| `pip_audit -r backend/requirements.txt --no-deps --disable-pip ...` | 12 dependencias fijadas consultadas, cero vulnerabilidades conocidas, ninguna omitida | Herramienta instalada en `/tmp`; no se cambiaron dependencias del producto |
| Revisión acotada de secretos | 229 blobs históricos: sin coincidencias con secretos locales ni patrones de claves privadas/tokens GitHub/AWS usados | No es un escáner exhaustivo; no se imprimieron valores privados |
| Exportación de `git archive HEAD` a `/tmp`, venv nuevo, instalación de requirements, pip check, npm ci raíz/frontend, build, check y migrate | Correctos tras repetir operaciones bloqueadas por el sandbox | Linux; no se ha instalado en Windows/macOS |
| `.venv/bin/python scripts/check_neon.py` | `SELECT 1` y TLS correctos en directa/pooled; ninguna de las cinco tablas buscadas; código 1 | Consultas `READ ONLY`. URLs no atribuidas a un proyecto/rama. HTTP local inaccesible porque no había servidor residente en 8000 |
| `.venv/bin/python scripts/neon_manage.py migrate --plan` | El script rechaza configuración sin `DATABASE_URL_UNPOOLED` | Se detiene antes de conectar/migrar. No se aplicó ninguna migración remota |
| API pública GitHub, GET de repo/commit/runs | Público; remoto `57d296f`; CI de ese SHA `success` | No se consultó panel privado de Vercel |
| GET a cuatro rutas de `https://sap-bice.vercel.app` | Las cuatro devuelven 404 de Vercel | Confirma indisponibilidad observada, no su causa dentro de la cuenta |
| PDF, hashes y enlaces locales | PDF 30 páginas, 13 imágenes, 26 enlaces, sin páginas vacías; 38 hashes históricos coinciden; sin destinos locales rotos en enlaces Markdown revisados | Extracción completa de texto y muestreo visual, no inspección visual exhaustiva de las 30 páginas |

El primer acceso externo a GitHub y la instalación Python limpia fallaron por DNS del sandbox. Se repitieron con la autorización de ejecución necesaria y terminaron correctamente. La instalación React en la copia temporal falló por `spawnSync esbuild EPERM`; el reintento autorizado pasó. La primera consulta `pip-audit` también falló por DNS y el reintento terminó sin avisos. Estos fallos del entorno no se contabilizan como defectos de SAP.

La QA local comprobó Chrome/Chromium de escritorio y móvil emulado de 390 px, sin errores de página ni respuestas críticas. Las muestras visuales son claras y el flujo mantiene contexto. No se comprobaron Safari/Firefox, dispositivos físicos, accesibilidad completa, carga sostenida pública ni pruebas de penetración. El ensayo con 125 vendedores y 857 observaciones acota consultas en los endpoints medidos; no acredita capacidad productiva bajo carga.

Quedan sin comprobar el builder real, bundle/CDN/proxy público, login público, persistencia y recuperación remotas, cuotas efectivas de las cuentas, titularidad de los endpoints Neon, accesos finales del tribunal y comprensión oral del autor. No se consultaron datos corporativos ni se validó una integración Mirakl, que no existe en el código revisado.

**Confirmaciones recibidas:** actividades y autorización docente aprobadas; no existe vídeo ni otra URL. **Información todavía necesaria para continuar:** destino exacto de las conexiones Neon, configuración efectiva del proyecto Vercel y fechas/canal de entrega y defensa. No se necesitan credenciales pegadas en el chat. La elección de cómo rectificar revisiones es una decisión de producto de SAP; no se atribuye a la guía académica.
