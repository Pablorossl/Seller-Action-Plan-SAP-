# QA integral y cierre UX/UI — Seller Action Plan

Fecha: 07/11/2026. Base inicial: `8459de6`, árbol limpio al comenzar. Revisión local, con datos exclusivamente ficticios. Sin commits, pushes ni despliegues.

## Preparación y alcance

Se revisaron los seis informes solicitados y sus pruebas reproducibles. La auditoría UX/UI original sigue disponible en `/tmp/sap-ux-audit-20261107/AUDITORIA-UX-UI-SAP.md`, junto a sus capturas y JSON de evidencias. Se consulta para comparar hallazgos, no para atribuir verificaciones históricas a esta ejecución ni afirmar que todos están resueltos. No hay AGENTS.md aplicable en el repositorio ni sus directorios superiores.

Se inspeccionaron README, `docs/trazabilidad-requisitos.md`, páginas/componentes React, rutas/foco/guard, estilos Django y React, contratos de listado y verificadores anteriores. Se registró una huella SHA-256 de los 88 archivos versionados de backend/frontend relevantes antes de cualquier corrección, en `artifacts/qa-ux-cierre/source-before.json`.

Plan de ejecución: tests JavaScript/build; composición completa de navegación segura, responsive, teclado, contraste, sistema visual, pulido y Full Stack mediante PostgreSQL temporal; pruebas adicionales del acceso/portal Django, filtros al volver/Atrás, conflicto real 409 y pendientes de la auditoría. Se comprueba persistencia con reinicios y backup/restauración independientes. No se usa la conexión configurada del usuario ni se escribe en servicios remotos.

Herramientas inventariadas: WSL2/Linux, Python QA 3.12.4, Playwright 1.62.0, Node 22.19.0, Django 5.2.18, DRF 3.18.3, psycopg 3.3.6, Gunicorn 26.2.0, PostgreSQL 14.24, OpenSSL, Chromium 151.0.7922.34 y axe-core disponible en el directorio temporal de QA. Firefox y WebKit no están instalados; tampoco Orca, Speech Dispatcher ni eSpeak. El JSON de entorno está en `artifacts/qa-ux-cierre/environment.json`.

Se intentó abrir Chromium con ventana sobre Xvfb privado para comprobar zoom nativo por teclas del sistema. Xvfb está instalado, pero `/tmp/.X11-unix` no es escribible en WSLg y el servidor gráfico no pudo crear un socket. No se modificó la configuración del sistema ni se usó el escritorio del usuario como alternativa. El intento, su fuente y el log comprimido se conservan en `artifacts/qa-ux-cierre/native-probe/native-zoom/`. **Zoom nativo no verificado**; el reflow y las teclas Ctrl+Equal en headless se registran por separado y no lo sustituyen.

El primer inventario de Playwright quedó bloqueado dentro del sandbox; se detuvo ese proceso de solo lectura y se repitió fuera del sandbox con arranque real de Chromium. No se presenta el intento bloqueado como prueba superada.

## Datos y reproducción

La composición crea dos agentes ficticios (`evaluador_qa` y `ajeno_qa`) con claves aleatorias no registradas, cartera separada, demo oficial confirmada como ficticia y 55 vendedores `KEY-QA-*` para paginación. Incluye planes activos, borradores, cierre alcanzado, cierre no alcanzado, cancelación no evaluable y un cierre heredado sin resultado registrado. El recorrido principal usa tasa de incidencias inicial del 6 %, revisión del 4,5 %, segunda revisión del 3 %, dos acciones, evaluación y cierre. Los periodos son julio–septiembre de 2026, con 100 pedidos ficticios por observación.

Los casos de pulido añaden mediante la API 16 borradores `QA PULIDO:*` y 12 acciones para listas largas. El snapshot de la primera composición terminó con 60 vendedores, 24 planes, 28 acciones, 22 indicadores de plan y ocho revisiones. El benchmark posterior añade otros 120 vendedores y observaciones ficticias: no son datos de rendimiento de producción. Las cifras finales y sus huellas están en `result.json`.

Reproducción desde el repositorio, con `.venv`, PostgreSQL/OpenSSL en PATH, Playwright/Chromium y axe-core ya instalados según los verificadores existentes:

```sh
env PATH=/home/pablo/.nvm/versions/node/v22.19.0/bin:$PATH npm test
env PATH=/home/pablo/.nvm/versions/node/v22.19.0/bin:$PATH npm run build
env PATH=/home/pablo/.nvm/versions/node/v22.19.0/bin:$PATH python3 scripts/verify_ux_closure.py --artifacts artifacts/qa-ux-cierre/final
python3 -m py_compile scripts/verify_ux_closure.py
git diff --check
```

El PATH absoluto corresponde a este equipo; en otro entorno basta Node compatible disponible en PATH. `verify_ux_closure.py` compone los verificadores existentes, usa `verify_phase3.py` para infraestructura y sobrescribe explícitamente DATABASE_URL con PostgreSQL temporal en loopback. Ejecuta migraciones en esa base nueva, tests Django, `check --deploy`, `collectstatic`, Gunicorn con TLS local, navegador, reinicios, copia y restauración. `scripts/release.sh` se ejecuta únicamente contra ese entorno temporal para comprobar repetición de checks/migraciones: **no es un despliegue**. Claves y dump se eliminan junto a los recursos temporales. Los artefactos son locales e ignorados por Git; deben conservarse aparte si se necesita trasladar la evidencia.

## Recorridos funcionales y regresión

Las comprobaciones de teclado se ejecutan con teclas reales de Playwright en Chromium, además de asserts de foco y estilos computados. La revisión manual de esta tarea consiste en inspección visual de capturas, colores y resultados; no equivale a una sesión de un usuario ni al uso de un lector de pantalla.

| Recorrido | Resultado observado y evidencia |
| --- | --- |
| 1. Inicio/cierre de sesión | Login válido real, error de credenciales ficticias y acceso anónimo rechazado; login y portal Django en los seis tamaños. Logout real con CSRF; si hay cambios, continuar mantiene la sesión/formulario y descartar permite salir. `closure`, `navigation`, recorrido Full Stack. |
| 2. Dashboard/prioridades | Datos React de la API real, orden operativo, totales/resumen limitado explícitos y enlace contextual a acción con foco y scroll. Carga retenida y error HTTP 503 deliberadamente interceptados, recuperación posterior real. `screens`, `keyboard`. |
| 3. Buscar/paginar vendedores | Filtros con/sin planes, búsqueda, limpieza, página 50 + resto, rango/total y foco de paginación. **El contexto se pierde al abandonar y regresar**; se caracteriza en I04, no se declara corregido. |
| 4. Ficha y planes del vendedor | Observación inicial y revisiones del plan distinguidas, planes abiertos/histórico, condición para crear sin observaciones y acceso al plan correcto. Cartera vacía y acceso ajeno 404. `screens`, `closure`. |
| 5. Crear/editar plan | Precarga, selección de observación, índice de secciones, validación Django, creación de un único borrador frente a doble envío, edición y guardado con foco/feedback. Identidad de vendedor/plan conservada. `navigation`, `keyboard`, Full Stack. |
| 6. Volver/cancelar/Atrás | «Volver al plan» sale de edición con el mismo ID; cancelar limpio no avisa; Atrás/Adelante restaura URL y estado esperado. Diálogos y rutas protegidos cuando hay texto pendiente. `navigation`, 20 grupos. |
| 7. Cambios sin guardar | Continuar y Escape conservan valores; descarte no escribe; modificar y revertir no avisa; beforeunload nativo al recargar realmente rechazado. No es una simulación mediante evento JavaScript. `navigation`. |
| 8. Validación/guardado fallido | Error 400 real conserva entradas y nombres comprensibles; 503 deliberado conserva formulario/guardia/clave de reintento. Tres conflictos **409 reales** provocados por otra escritura API con revisión vigente conservan título local y no pisan servidor. Tras descarte consciente/recarga se lee la versión nueva. `closure`, `navigation`, `screens`. |
| 9. Acciones | Crear, editar, completar y volver a pendientes; validaciones y foco; protección de diálogos; largo de descripción/responsable en seis tamaños. Sin cambios en payloads o reglas. |
| 10. Revisiones | Registro 6 → 4,5 → 3, lectura ordenada, valoración humana separada del resultado calculado. Rectificación con motivo, autor/histórico, precarga limpia y un envío al guardar; no destrucción de revisiones. |
| 11. Evaluación/cierre | Evaluación backend, confirmación y cierre real, datos congelados al cerrar, acciones abiertas documentadas. `browser-result.json`, tests Django y contrastes. |
| 12. Estado/resultado | «Cerrado»/«Cancelado» neutros, separados de «Objetivo alcanzado», «Objetivo no alcanzado», «No evaluable» y «Sin resultado registrado». No se deduce éxito de estar cerrado; el snapshot permanece igual. `contrast/semantics` y tests JS de resultado. |
| 13. Persistencia/recuperación | Recarga del plan, reinicio de PostgreSQL, reinicio de Gunicorn/repetición del release local y pg_dump/pg_restore a otra base temporal; comparación de hashes y recuentos de los 13 modelos/relaciones de negocio y permisos. Readiness 503 mientras PostgreSQL está detenido. No se comprueba aquí continuidad de sesión del navegador a través de los reinicios. |

Estados adicionales: búsqueda sin coincidencias, lista/acciones/revisiones vacías, vendedor sin observaciones, cartera realmente vacía del segundo agente, plan inexistente y sin acceso, error de login, borrador con activación no permitida, cancelado/heredado y respuestas inválidas JSON/HTML. Los fallos HTTP interceptados son pruebas deliberadas de recuperación; no se atribuyen a caídas espontáneas ni sustituyen los conflictos reales y validaciones backend.

## Incidencias, cambios y pendientes

Prioridad local: P1 bloquea una tarea crítica o pone datos en riesgo; P2 dificulta una tarea con alternativa segura; P3 pulido o prevención. Las prioridades originales de la auditoría se conservan en su documento; esta tabla clasifica el impacto residual observado para cerrar este alcance. No quedan P0/P1 conocidos en la ejecución aprobada; los pendientes no se ocultan.

| ID / pantalla | Pasos reproducibles y entorno | Esperado / observado antes de corregir | Impacto, prioridad y estado |
| --- | --- | --- | --- |
| I01 · Login/portal Django | Abrir `/accounts/login/` o `/` autenticado, Chromium, seis tamaños. Inspeccionar `.auth-eyebrow` y axe. | Texto normal ≥4,5:1; `#70865d` sobre blanco daba **3,99:1**. | Legibilidad; P2 **corregida** con `#56685e`, **5,94:1**. Hueco previo de cobertura: anteriores suites se centraban en React, sin atribuirlo a una regresión nueva. |
| I02 · Campos de login | Ver campos sin foco en login, especialmente móvil; medir borde sobre fondo blanco. | Contorno identificable ≥3:1; `#d6e0cf` daba **1,36:1**. | Identificación del control; P2 **corregida** con `#748278`, **4,03:1**. No cambia tamaño, etiqueta, sesión ni CSRF. |
| I03 · Error de edición | Abrir edición de plan activo, cambiar título local, PATCH concurrente de objetivo con revisión actual, guardar UI con revisión antigua. Escritorio/tablet/móvil. | Una instrucción de conflicto; el resumen y `detail` repetían literalmente la misma frase. | Ruido/anuncio duplicado; P3 **corregida**. `FormError` omite solo el detalle idéntico al encabezado y los párrafos vacíos; conserva detalles distintos, campos y foco. Assert de texto único sobre 409 backend real en tres tamaños. |
| I04 · Vendedores/planes | Buscar/filtrar → ficha/detalle → enlace Volver; página 2 → ficha/detalle → Atrás del navegador. 1440, 768 y 375 px. | Mantener búsqueda/filtro/página; vuelve a consulta vacía y página 1. **12/12 casos no conservan el contexto**. | Repetir selección; sin pérdida de registros ni cambios del plan. P2 **pendiente**, UX07. Estado local de listas desmontado al cambiar ruta. Propuesta separada: decidir contexto en URL/restauración y probar Atrás/Adelante junto al guard; no se implementa una función nueva en esta fase. |
| I05 · Conflicto de versión | Mismo 409 real de I03; intentar continuar tras mensaje de recarga. | Guiar comparación/conservación y carga de versión vigente; solo hay instrucción de recargar. | Fricción al recuperar, con bloqueo correcto de sobrescritura y valores locales conservados. P2 **pendiente**, UX22. Copiar cambios y descartar conscientemente permite recargar; no afirmar una recuperación guiada inexistente. |
| I06 · Crear/editar: responsable | Abrir selector con agente de cartera; tiene una opción pero buscador y paginación de una página. Tres tamaños. | Presentación contextual más simple con una sola opción; permanece picker completo. | Controles redundantes, sin bloqueo; P3 **pendiente**, UX17. No ampliar permisos ni opciones para aparentar mejora. |
| I07 · Diálogo largo | Abrir revisión/finalización en móvil, recorrer hasta Guardar/Cancelar. | Acciones fácilmente localizables; requieren scroll interno hasta el final. | P3 **pendiente parcial**, UX19: scroll, foco, Escape y teclado funcionan; no se añade pie fijo que pueda tapar campos. |
| I08 · Registrar revisión | Abrir revisión nueva, leer «Valoración del agente». | Decisión consciente; valor inicial `on_track` («Evolución favorable»). | Valor por defecto **observado**; sesgo/errores humanos **no medidos**. P3 **pendiente de decisión de producto**, UX24. La distinción respecto al cálculo está validada; no se cambia el default automáticamente. |
| I09 · Portal Django | Abrir `/` con 60 vendedores ficticios tras login. | Acceso secundario cómodo con volumen; tarjeta estrecha/lista larga sin paginación propia. | P3 **pendiente**, UX27. Se conserva acceso destacado a React y portal funcional/académico; no se sustituye ni añade funcionalidad. |

I01/I02 son ajustes acotados a contraste existente y I03 a presentación de errores compartidos. Ninguna incidencia exigió tocar modelos, migraciones, permisos, contratos o lógica de evaluación. Los pendientes I04/I05 son deuda UX reproducida y aceptable para **QA local del alcance probado**, no requisitos marcados como cumplidos.

Se conserva el primer recorrido PostgreSQL completo, anterior a I03, en `integrated-before-message-fix/`. El ensayo previo del nuevo verificador falló por asumir erróneamente un único resultado en búsqueda DRF: el término numérico `1` también coincide con `10`. Se corrigió el verificador para elegir el enlace del título exacto y se repitió; no era un defecto del producto. Ese intento incompleto no se cuenta como ejecución aprobada.

## Responsive, teclado y accesibilidad

Se repite la suite de 128 estados con datos y textos largos en **320 × 568, 375 × 812, 430 × 932, 768 × 1024, 1024 × 768 y 1440 × 900**. Se comprueba anchura del documento, contención/desplazamiento horizontal local de tablas, encuadre de controles, formularios y diálogos, menú compacto y conservación/descarte. Se añaden login y portal en los mismos seis tamaños. Los casos de pulido y conflictos amplían escritorio, tablet y móvil; no se afirma que cada combinación posible de estado, rol y tamaño haya sido ejecutada.

La suite de 12 grupos de teclado verifica Tab/Shift+Tab/Enter/Espacio, enlace de salto, foco tras ruta/carga/paginación y acceso contextual desde prioridades; regiones de tabla enfocables con flechas; diálogos con foco contenido, Escape y restauración, incluyendo el caso de abridor que desaparece tras transición. Menú compacto abre/cierra por teclado, cambia nombre y devuelve el foco. Se inspeccionan anillos visibles y relaciones label/ayuda/error; no basta con que `activeElement` exista.

Comprobación manual de los colores modificados, con luminancia relativa sRGB y estilos computados en superficie blanca opaca:

| Combinación | Antes | Después | Umbral aplicado |
| --- | ---: | ---: | ---: |
| Texto de apoyo `#70865d` → `#56685e` / blanco | 3,9946:1 | 5,9365:1 | 4,5:1, texto normal de 10 px |
| Borde de campo `#d6e0cf` → `#748278` / blanco | 1,3616:1 | 4,0331:1 | 3:1, identificación del control |

Se revisaron visualmente las capturas de login antes/después con idéntico encuadre, errores 409, cierre no alcanzado, listados móviles y pantallas/diálogos representativos de las suites. No hay cambio geométrico en login ni dependencia exclusiva del color en estado/resultado: se mantienen textos e iconos/etiquetas explícitos. La revisión no añade una conformidad WCAG global a partir de estas medidas puntuales.

axe-core **4.14.0** ejecuta etiquetas WCAG 2/2.1/2.2 A/AA disponibles sin desactivar reglas. La composición definitiva produjo **182 análisis y cero infracciones**, con `incomplete` que requieren interpretación manual: seis `th-has-data-cells` en tablas vacías heredadas/no evaluables y siete `color-contrast` en capas de diálogo/elementos parcialmente superpuestos. Se conservan los JSON, estilos y capturas; se revisan bordes, textos y regiones afectadas. **No se convierten los `incomplete` en pruebas automáticas superadas**, ni se atribuye anuncio/orden hablado sin lector. Estos resultados no constituyen conformidad WCAG completa.

Reflow adicional a 720 × 450 y 360 × 225 desde base 1440 × 900: ejecutado como cambio de viewport. El ensayo Ctrl+Equal de la suite headless no cambió viewport CSS. El intento posterior con ventana/Xvfb falló. **Ninguno de estos pasos acredita zoom nativo al 200 % o 400 %.** No hay Firefox/WebKit, dispositivos físicos ni lector de pantalla disponibles para validación equivalente.

## Estado de la auditoría original

Auditoría disponible y consultada: copia del documento y selección de evidencias originales en `artifacts/qa-ux-cierre/audit-original/`. «Corregido en alcance» significa que la conducta concreta se verifica localmente; «parcial» conserva parte de la propuesta original pendiente. No es una declaración de que todos los hallazgos estén resueltos ni una nueva investigación de usabilidad.

| Hallazgo | Estado actual / evidencia o límite |
| --- | --- |
| UX01 · Volver desde edición | **Corregido en alcance**: salida real con ID conservado; `navigation`/teclado. |
| UX02 · Pérdida de texto | **Corregido en alcance**: rutas, Atrás/Adelante, Escape, descarte/continuar y beforeunload real; errores conservan valores. |
| UX03 · Overflow global | **Corregido en alcance**: 128 estados/seis tamaños, tablas con scroll local y contenido largo. |
| UX04 · Contraste | **Corregido en combinaciones medidas**, ampliado a acceso/portal con I01/I02; no conformidad global. |
| UX05 · Foco de navegación | **Corregido en alcance**: destino/ruta y acción de prioridad visibles con foco; 12 grupos de teclado. |
| UX06 · Cerrado parece éxito | **Corregido en alcance**: estado neutro y resultado al cierre independiente; cuatro resultados, snapshot igual. |
| UX07 · Filtros al volver | **Pendiente confirmado**: I04, 12 observaciones; no se implementó persistencia. |
| UX08 · Urgencia dashboard | **Mejorado**: KPIs operativos y revisiones antes del panel secundario en móvil; orden/textos comprobados, eficacia humana no medida. |
| UX09 · Resumen truncado | **Corregido en alcance**: «Mostrando N de total» y enlace honesto a planes; no cola nueva. |
| UX10 · Próxima acción/revisión | **Corregido en alcance** con campos existentes de la API y texto de ausencia. |
| UX11 · Directorio | **Parcial**: planes abiertos ganan jerarquía; agente/registro siguen visibles, sin compactación adicional. |
| UX12 · Crear sin observaciones | **Corregido en alcance**: condición y ayuda junto a CTA; carga/error no se confunden con cero. |
| UX13 · Fuente de observaciones | **Corregido en alcance**: observación inicial del vendedor y revisiones del plan etiquetadas por separado. |
| UX14 · Texto pequeño | **Parcial**: escala operativa consolidada; microtexto de marca/apoyo sigue pequeño, incluido eyebrow de 10 px ahora contrastado. |
| UX15 · Errores técnicos | **Parcial**: campos/índices traducidos, errores asociados y valores conservados; sin enlaces del resumen a cada campo. I03 elimina duplicación literal. |
| UX16 · Banda de pasos | **Corregido en alcance**: índice nativo de secciones, foco sin cambiar ruta/hash, formulario único. |
| UX17 · Responsable único | **Pendiente confirmado**: I06; no modificación de permisos. |
| UX18 · Rectificación visual | **Corregido en alcance**: Field/botón compartidos, motivo asociado e histórico conservado. |
| UX19 · Diálogo largo | **Parcial**: contenido y acciones alcanzables por scroll/teclado; sin cabecera/pie fijos. I07. |
| UX20 · Menú compacto | **Corregido en alcance**: Escape, foco, nombre y relación semántica con panel probados en móvil/tablet. |
| UX21 · Estado y regiones | **Corregido en alcance**: estado actual/pressed y nombres específicos de regiones; sin convertir controles en tabs con interacción incompatible. |
| UX22 · Recuperación 409 | **Pendiente**: I05. Nuevas pruebas de concurrencia real confirman conservación/rechazo seguro; no recuperación guiada. |
| UX23 · Finalizar domina | **Corregido en alcance**: tarea operativa primaria según estado, finalizar secundario visible y confirmado. |
| UX24 · Valoración preseleccionada | **Parcial**: valoración humana y cálculo separados; `on_track` sigue por defecto. Sesgo es hipótesis sin medición. I08. |
| UX25 · Ayudas | **Parcial**: copy operativo sin jerga Django/MQC; no se reescriben todas las reglas detalladas por indicador. |
| UX26 · Paginación | **Corregido en alcance**: rango, páginas/total, páginas parciales 20/50 y vacíos probados. |
| UX27 · Portal Django | **Pendiente**: I09; login/portal ahora también comprobados en seis tamaños, sin paginación nueva. |
| UX28 · Arquitectura | **Parcial**: componentes/tokens/helpers compartidos existentes conservados; PlanDetail sigue grande, sin refactor amplio en QA. |
| UX29 · Feedback | **Parcial**: guardados con mensajes específicos; creación sigue redirigiendo al borrador sin aviso adicional de creación. |
| UX30 · Tokens/densidad | **Mejorado gradualmente** por sistema visual existente; variantes funcionales conservadas, sin uniformar todo. |
| UX31 · Fuente externa | **Pendiente preventivo**: importación DM Sans externa/fallback; sin autoalojado nuevo ni prueba de disponibilidad futura. |
| UX32 · Carga/altura | **Pendiente**: carga/error/recuperación comprobados; spinner sin skeleton/reserva nueva. No se ha medido CLS. |
| UX33 · Microinteracciones | **No reproducible como fallo funcional**: propuesta estética/hipótesis original, sin estudio de usuarios ni rediseño. No se acredita reducción de movimiento con una nueva prueba manual. |

Comparación visible: el original de cierre no alcanzado tenía chip «Cerrado» verde y resultado lejos de la cabecera; ahora el estado es neutro y «Objetivo no alcanzado» aparece con texto explícito arriba. El original móvil de vendedores mostraba overflow documentado por la auditoría; las mediciones actuales verifican contención en seis tamaños. Las imágenes históricas conservan su tamaño original (390 px móvil), distinto de algunas capturas actuales de 375 px: no se presentan como comparación píxel a píxel.

## Full Stack, TFG y límites de evidencia

Se contrasta con [la matriz de trazabilidad](trazabilidad-requisitos.md), cuya versión del 03/11 describe evidencias públicas/históricas. Esta revisión añade evidencia **local actual**, no vuelve a declarar vigentes esas publicaciones.

| Área/requisito | Comprobado en esta tarea | Fuera de la evidencia actual |
| --- | --- | --- |
| Django, DRF, modelos, vistas y plantillas | Suite completa PostgreSQL, login/portal Django reales, checks, migraciones nuevas y ausencia de drift; lectura/escritura React ↔ API real. | Revisión académica de autoría/calidad y ejecución PostgreSQL 18/infraestructura pública. |
| React integrado | Dashboard, directorio/ficha, planes/edición/seguimiento y ciclo completo con datos reales de la base ficticia. Build y tests JS actuales. | Versión publicada, otro motor/dispositivo y todos los perfiles de UI. |
| Sesión, CSRF y permisos | Login/logout reales; anónimo 403, token ausente/origen no permitido rechazados, cartera ajena 404; permisos de rol cubiertos por tests backend. | Pentest completo, identidad/roles externos y sesión de navegador conservada tras reiniciar servicios en este run. |
| Validación, revisiones, idempotencia | Tests PostgreSQL, incluyendo concurrencia; rechazo de fechas/valores inválidos; doble envío/reintento; 409 real y valores locales protegidos. | Recuperación guiada UX22, conflictos en todos los formularios/motores. |
| Evaluación/cierre/histórico | Evaluación backend y snapshot al cierre, rectificación trazable, cuatro resultados de presentación, sin inferir éxito por estado. | Efecto organizativo real o dictamen académico de la lógica. |
| Persistencia/recuperación | Hashes/filas de negocio y permisos iguales tras PG/Gunicorn/release local y restauración independiente; readiness detecta DB detenida. | Recuperación de producción, copia de sesiones y todas las tablas operativas, segundo proveedor/red, continuidad futura. |
| Contratos/fuentes | Huellas antes/después y diff acotado: sin cambios en modelos, migraciones, API, servicios, rutas o reglas. | Huella no equivale por sí sola a validación semántica de todo el proyecto. |
| Organización/documentación | Instrucciones, README, matriz, informes previos y requisitos contrastados; verificador nuevo reproducible. | No se reexportan/revisan PDF o Word ni todas las capturas de la memoria. No se concede nota por cantidad de tests. |
| URL pública/repositorio/CI | Ninguna operación remota de escritura; el HEAD local `8459de6` difiere de la versión pública `97b4bff` descrita en la matriz. | Disponibilidad/TLS/CI remoto actuales y publicación de estas mejoras: no comprobados aquí; no hubo despliegue. |
| Vídeo/entrega/defensa | Pendientes documentados en matriz leídos. | Vídeo real ≤5 min, enlace reproducible, cuatro enlaces de entrega, confirmación docente, segunda red, prerrequisitos académicos y defensa requieren al autor/docente. |

El certificado autofirmado valida integración HTTPS local; Chromium ignora exclusivamente sus errores en contexto QA. No acredita certificado público, red independiente ni seguridad de producción. PostgreSQL usado es 14.24, no se atribuye como prueba de producción/Neon 18. No se instalaron dependencias nuevas.

## Evidencias disponibles

Raíz: [artefactos de esta revisión](../artifacts/qa-ux-cierre/). No están versionados. La base temporal y las contraseñas no se entregan.

| Evidencia | Ubicación |
| --- | --- |
| Resultado integrado definitivo y persistencia | [final/result.json](../artifacts/qa-ux-cierre/final/result.json) |
| Resumen comprobado e integridad de fuentes | [validation-summary.json](../artifacts/qa-ux-cierre/validation-summary.json), [source-integrity.json](../artifacts/qa-ux-cierre/source-integrity.json) |
| Tests frontend/build | [js-tests.log](../artifacts/qa-ux-cierre/js-tests.log), [build.log](../artifacts/qa-ux-cierre/build.log) |
| Suite backend | [postgres-tests.log](../artifacts/qa-ux-cierre/final/postgres-tests.log) |
| Entorno y colores | [environment.json](../artifacts/qa-ux-cierre/environment.json), [contrast-manual.json](../artifacts/qa-ux-cierre/contrast-manual.json) |
| Contraste login antes/después, mismo tamaño | [antes 375](../artifacts/qa-ux-cierre/auth-before/closure/django-login-375.png), [después 375](../artifacts/qa-ux-cierre/final/browser/closure/django-login-375.png), [axe antes](../artifacts/qa-ux-cierre/auth-before/closure/axe.json) |
| Registro de revisión visual | [visual-review.json](../artifacts/qa-ux-cierre/visual-review.json): imágenes inspeccionadas y límites |
| Error 409 antes/después | [antes duplicado](../artifacts/qa-ux-cierre/integrated-before-message-fix/browser/closure/real-conflict-409-375.png), [después](../artifacts/qa-ux-cierre/final/browser/closure/real-conflict-409-375.png) |
| Filtros y conflictos reales | [filters.json](../artifacts/qa-ux-cierre/final/browser/closure/filters.json), [closure/result.json](../artifacts/qa-ux-cierre/final/browser/closure/result.json), capturas `*-selection-*`, `*-return-*` en la misma carpeta |
| Accesibilidad y regresión | Subdirectorios [browser](../artifacts/qa-ux-cierre/final/browser/) `components`, `contrast`, `keyboard`, `navigation`, `responsive`, `screens`, `closure`: JSON, estilos, observaciones y PNG |
| Auditoría original preservada | [documento](../artifacts/qa-ux-cierre/audit-original/AUDITORIA-UX-UI-SAP.md), [cierre original](../artifacts/qa-ux-cierre/audit-original/evidence/cierre-no-alcanzado-1440x900-full.png), [vendedores original](../artifacts/qa-ux-cierre/audit-original/evidence/vendedores-390x844.png) |
| Cierre no alcanzado actual | [1440 px](../artifacts/qa-ux-cierre/final/browser/contrast/not-achieved-1440.png): estado neutro y resultado textual |
| Zoom nativo no ejecutable | [motivo y estado](../artifacts/qa-ux-cierre/native-probe/native-zoom/result.json), fuente del intento y log Xvfb comprimido en esa carpeta |

## Archivos modificados

1. `backend/sellers/static/sap/auth.css`: solo dos colores, I01/I02.
2. `frontend/src/components/ui.jsx`: evita duplicación literal de `FormError`, I03, conserva detalles distintos y foco.
3. `scripts/verify_ux_closure.py`: composición de regresión y pruebas de login/portal en seis tamaños, contexto al regresar, 409 real con texto único, cartera vacía y acceso inexistente/ajeno; solo datos ficticios locales.
4. `docs/qa-integral-cierre-ux-ui-2026-11-07.md`: este informe.

Las huellas de fuentes anteriores y posteriores quedan en `source-before.json` y `source-integrity.json`. Los ficheros de las fases previas se conservan. No hay commits, pushes ni despliegues.

## Riesgos y recomendaciones antes de la entrega

1. Conservar esta carpeta de evidencias junto al informe: `artifacts/` no se incluye automáticamente en Git. Repetir el comando integrado sobre el candidato exacto si cambia código o configuración después de esta acta.
2. Comprobar en un equipo disponible el zoom **nativo** 200 %/400 %, al menos Firefox y Safari/WebKit, dispositivos táctiles físicos y un lector de pantalla (nombres, orden, anuncios de guardado/error y retorno de foco). Los resultados automáticos actuales no cubren esas combinaciones; los `incomplete` de axe se entregan con sus límites.
3. Priorizar aparte UX07 (búsqueda/filtros/página en navegación) y UX22 (recuperación explícita de conflictos sin sobrescribir). Mantener sus pruebas de descarte/continuar y revisión al diseñarlos. El comportamiento actual es reproducible y no implica pérdida de datos guardados; requiere repetir selección o conservar manualmente el texto antes de recargar.
4. Tratar selector único, defaults de valoración, acciones al final de diálogos y portal secundario como decisiones de producto/pulido posteriores. No modificar permisos, algoritmos o valoración por una preferencia visual. Fuente externa y carga sin reserva de altura siguen como deuda preventiva, sin fallos de disponibilidad o CLS medidos en esta revisión.
5. Antes de una publicación autorizada, verificar SHA/CI/entorno de producción exactos y disponibilidad desde otra red; repetir humo con la configuración pública correspondiente. Esta tarea no modifica producción ni sustituye esa validación. El autor debe revisar coherencia de memoria/capturas con la UI final, grabar y medir el vídeo ≤5 min, comprobar enlaces/permisos, requisitos docentes y entrega/defensa; aquí no se presentan como completados.

## Ejecución final y veredicto

La segunda composición completa, **tras las tres correcciones**, terminó con código 0 y limpieza de recursos temporales. No se suman sus cifras con los ensayos anteriores. Evidencia final disponible el 07/11/2026 a las 22:49 UTC (23:49 CET).

| Comando/comprobación ejecutada | Resultado definitivo |
| --- | --- |
| `npm test` con Node 22.19.0 | **35/35**: API 12, navegación 6, resultado 8, presentación 9; cero fallos. Repetido después de I03. |
| `npm run build` | **Correcto**, Vite, 38 módulos, 1,22 s; repetido después de I03 y usado por Gunicorn/WhiteNoise en la composición final. |
| `python3 scripts/verify_ux_closure.py --artifacts artifacts/qa-ux-cierre/final` | **Código 0**, toda la composición y sus verificaciones internas descritas abajo. |
| `manage.py test --verbosity 2`, PostgreSQL temporal | **116/116**, 38,659 s, cero fallos. Incluye permisos, revisión/idempotencia/concurrencia, validación, evaluación y cierre. No se ejecuta sobre SQLite como sustituto de esta suite. |
| Migración desde cero / `makemigrations --check --dry-run` / `migrate --check` | **Correctos**, sin drift. Migraciones existentes sin modificación. |
| `check --deploy --fail-level WARNING`, collectstatic y repetición de release local | **Correctos** en configuración temporal; sin publicación remota. |
| Sistema visual / contraste | **33 estados/12 axe** y **58 estados/54 axe**, sin errores JavaScript ni infracciones; snapshot de cierre igual. |
| Teclado / navegación segura | **12 grupos/10 axe** y **20 grupos**; beforeunload nativo, ID, formularios y foco conservados. |
| Responsive | **128 estados**, seis resoluciones requeridas y contenido largo; contención y controles utilizables. Reflow adicional medido por separado. |
| Pulido de pantallas | **73 estados/73 axe**, escritorio/tablet/móvil, búsqueda/paginación, validación, carga/error/recuperación y resultados. |
| Nuevos casos de cierre | **51 estados/33 axe**: acceso/portal en seis tamaños, 12 retornos de filtros caracterizados, tres 409 reales seguros con instrucción única, cartera vacía e inexistente/ajeno. |
| Total axe de composición final | **182 análisis, cero infracciones**; 13 apariciones de reglas `incomplete` (6 + 7) conservadas con límites, no aprobadas automáticamente. |
| Full Stack | **Correcto**: 6 → 4,5 → 3, plan cerrado/objetivo alcanzado, recarga, logout, CSRF, cartera ajena denegada y recuperación ante JSON/HTML inválidos. |
| Reinicios/backup | **Correctos**: PG y Gunicorn/release local conservan snapshot; readiness 503 sin DB; pg_dump/restore independiente coincide y migraciones restauradas al día. |
| `python3 -m py_compile scripts/verify_ux_closure.py` / `git diff --check` | **Correctos**. Huellas de 88 fuentes revisadas: solo cambian los dos archivos de presentación declarados. HEAD permanece `8459de6`. |

El snapshot definitivo mantiene 60 vendedores, 24 planes, 28 acciones, 22 indicadores de plan y ocho revisiones. Benchmark exploratorio local posterior (180 vendedores/857 observaciones, cinco lecturas por endpoint): medianas de 103,01 ms para overview, 9,63 ms vendedores y 23,68 ms planes, con 25/6/10 consultas respectivamente. No es una prueba de carga, capacidad o rendimiento de producción; no se modifica ningún cálculo ni consulta a partir de esas cifras.

**Veredicto: QA LOCAL APROBADO**, exclusivamente para los recorridos críticos probados en **Chromium 151.0.7922.34 + Django/DRF/Gunicorn + PostgreSQL 14.24 aislados, con datos ficticios y los seis tamaños indicados**. Las mejoras conviven sin fallos bloqueantes conocidos en ese alcance: navegación segura, foco, responsive, datos/revisiones, permisos, evaluación/cierre y recuperación están verificados. Se corrigieron I01/I02/I03 y se repitió la composición completa.

Permanecen la deuda UX documentada (en especial contexto de filtros y recuperación guiada de conflictos), los resultados automáticos indeterminados y las limitaciones de motores, lector, dispositivos y zoom nativo. Esta aprobación **no sustituye validación en producción, conformidad WCAG completa ni revisión/aceptación académica**. No hubo commits, pushes ni despliegues.
