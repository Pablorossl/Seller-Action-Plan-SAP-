# Diagnóstico de publicación SAP — 3 de noviembre de 2026

**Estado: publicación no aceptada.** Diagnóstico de solo lectura, salvo este informe local. No se hace commit, push, despliegue, migración externa, contratación ni modificación de variables. No se han consultado tablas externas en esta intervención.

## 1. Código candidato y remoto

Consulta actual `git ls-remote origin refs/heads/main`: **57d296f1a9cee56c925acec485b3d1bae5953cef**. HEAD local: **54ac2cd7614fb2b3bbf8328ff97a93a5e1f87d5f**, adaptación Vercel/Neon, posterior a `57d296f`. Antes: `49ee198` producción/seguridad, `0ec5a25` interfaz Fase 2 y `39a6d07` dominio de planes.

**No hay todavía un commit candidato completo de entrega.** `54ac2cd` es la base local, pero no incluye las correcciones F01–F03 del árbol de trabajo. Publicar solo ese SHA perdería esas soluciones. El candidato propuesto es un futuro commit revisado que incluya dichas correcciones, la migración 0003, pruebas y documentación, seguido de los ajustes documentales de entrega. No se crea en este diagnóstico.

Cambios pendientes inspeccionados: modelos/serializadores/servicios/pruebas de action_plans; nuevas pruebas de concurrencia y cierre; modelos, serializadores, clasificación, selección y pruebas de quality; consulta de vendedores; PlanDetail, PlanForm y Workspace. Sin seguimiento: migración 0003, test_closure_history y los informes/evidencias de auditoría y rectificación/F02/F03. Deben añadirse explícitamente al candidato; los archivos no seguidos no viajarán por sí solos. No incluir `.env*`, `.neon`, bases, dumps ni artefactos privados.

La referencia remota confirma el código de main, **no el SHA que Vercel está sirviendo**. La CI documentada de commits anteriores no acredita el futuro candidato. Falta una ejecución de CI de su SHA exacto. Las pruebas locales recientes están documentadas en los informes F02/F03: suite PostgreSQL de 112 pruebas sin omisiones, frontend/build y navegador; no se han repetido aquí porque esta tarea es un diagnóstico de publicación.

## 2. Vercel frente a Render

| Aspecto | Vercel preparado | Render conservado |
| --- | --- | --- |
| Configuración | `backend/vercel.json`, preset Django, raíz backend | `render.yaml`, servicio Python desde raíz del repositorio |
| Entrada | WSGI nativo `config/wsgi.py`, función de hasta 60 s | Gunicorn con configuración propia |
| React | build_vercel.py lee ../frontend y copia frontend_dist | scripts/build.sh compila frontend/dist |
| Estáticos | collectstatic automático del preset/CDN | collectstatic en build y WhiteNoise |
| Base | Neon externo; pooled en runtime | Blueprint propone PostgreSQL propio en Frankfurt |
| Migraciones | Manuales y separadas, URL directa | preDeployCommand ejecuta scripts/release.sh y migra |
| Publicación automática | Depende de integración Git/panel; Preview se omite por ignoreCommand | autoDeployTrigger off en YAML |
| Coste | Hobby/Free sujetos a límites y elegibilidad | YAML propone dos recursos de pago |

La documentación oficial confirma detección mediante manage.py y WSGI, y collectstatic automático: [Django en Vercel](https://vercel.com/docs/frameworks/full-stack/django). El proyecto requiere raíz **backend**, acceso al frontend fuera de esa raíz, preset Django, build `python build_vercel.py` y Output Directory sin override. No sirve importar el repositorio como una SPA Vite ni dirigir todas las rutas a index.html: login y API son Django.

`backend/vercel.json` no está en la raíz del repositorio. Esto hace especialmente relevante comprobar Root Directory y la configuración efectiva del panel. Su ignoreCommand omite Preview y permite Production; un entorno o override equivocado puede dejar el cambio sin build productivo. Las versiones de runtime y los archivos empaquetados requieren comprobar logs reales; las validaciones locales del paquete no sustituyen el builder remoto.

**No mezclar recetas:** no aplicar render.yaml ni usar scripts/release.sh como build Vercel. Render propone otra base y ejecuta migraciones predeploy; usarlo supondría una decisión distinta de infraestructura, coste y destino de datos.

## 3. Los 404: evidencias e hipótesis

HEAD HTTPS nuevo el 03/11/2026, 19:50 UTC, sin desactivar la validación del certificado:

| Ruta en sap-bice.vercel.app | Resultado |
| --- | --- |
| / | HTTP/2 404, server Vercel, x-vercel-error NOT_FOUND |
| /accounts/login/ | Igual |
| /healthz/ | Igual |
| /api/plans/ | Igual |

Se obtuvo HSTS y un identificador x-vercel-id; esto acredita respuesta HTTPS del proveedor, no el login, el esquema de base ni el funcionamiento de SAP. El titular confirmó previamente asignación Production; no se ha inspeccionado ahora su panel. Esta intervención usa HEAD, no una aceptación funcional GET/navegador pública.

**Comprobado:** main remoto carece del commit de adaptación; el dominio sigue devolviendo el error del proveedor en rutas que existen en Django. No es evidencia de un 404 emitido por las vistas de SAP.

**Hipótesis a comprobar, en este orden:**

1. No existe deployment Production Ready válido, el alias apunta a otro deployment/proyecto o el deployment se eliminó. Obtener URL inmutable, ID, estado, SHA, equipo/proyecto y asignación del dominio. Comparar URL inmutable y dominio canónico.
2. La integración usa una rama o versión anterior; el último cambio no llegó a GitHub, o un build se omitió. Revisar repositorio conectado, Production Branch e historial de builds con razones de omisión.
3. Root Directory/preset/output o overrides del panel generan otro tipo de artefacto. Comparar ajuste por ajuste con la tabla de `despliegue-vercel.md`; revisar descubrimiento WSGI y lista de funciones/rutas.
4. Build fallido por frontend externo no incluido, runtime, dependencias o variables productivas ausentes: puede dejar al alias sin una publicación válida. Pedir logs de build redactados, no suponer que ocurrió.
5. Restricciones de acceso o protección del deployment: inspeccionar configuración y respuesta de la URL inmutable.

Un fallo de conexión/esquema PostgreSQL suele manifestarse al iniciar o ejecutar SAP, y no explica por sí solo un NOT_FOUND de plataforma en todas esas rutas. Tampoco hay evidencia para atribuirlo a CORS: el diseño es del mismo origen. La guía oficial propone revisar URL, existencia del deployment, logs y permisos: [NOT_FOUND](https://vercel.com/docs/errors/not_found). **No se identifica una causa única sin acceso de lectura al proyecto y sus logs.**

## 4. Neon: configuración sin secretos

Inspección local por presencia/tipo, sin imprimir valores de conexión:

- `.env`: DATABASE_URL presente, PostgreSQL Neon **directa**, TLS requerido. DATABASE_URL_POOLED presente, pooled, TLS requerido. **DATABASE_URL_UNPOOLED ausente**.
- Django solo usa DATABASE_URL; no toma DATABASE_URL_POOLED como alternativa. Para runtime se propone DATABASE_URL pooled y para herramientas manuales DATABASE_URL_UNPOOLED directa. Deben obtenerse del destino confirmado, sin inventar hostnames.
- `scripts/neon_manage.py` exige la variable UNPOOLED y TLS antes de invocar Django. Con la configuración local inspeccionada no está preparado para migrar por esa vía. No se ejecuta ni se corrige aquí.
- Producción exige PostgreSQL y TLS; CONN_MAX_AGE=0 y DISABLE_SERVER_SIDE_CURSORS=True son compatibles con el patrón pooled. El login y las sesiones siguen siendo Django; no se necesita Neon Auth.
- `.neon` declara organización `org-rough-thunder-87253091`, proyecto `winter-grass-28484559` y rama de nombre `production`. Es contexto escrito offline; **no demuestra acceso, identidad de endpoint ni existencia de la rama**. `neon.ts` tampoco acredita infraestructura desplegada.
- Evidencia histórica del 02/11: SELECT 1 y TLS funcionaron en conexiones directa y pooled, pero no aparecieron cinco tablas SAP buscadas; proyecto/rama no verificados. No se extrapola esa ausencia al estado actual.

Falta confirmar por consola/API de solo lectura: titular y organización, project ID, branch ID estable además del nombre, endpoint/compute ID y región, database y rol, y correspondencia del endpoint de ambas URLs con esa rama/base. Comparar además lo configurado en Production de Vercel, con valores ocultos. Verificar plan, cuotas y retención de recuperación de la cuenta.

Después de identificar el destino, una verificación SQL en transacción de solo lectura debe confirmar base/usuario/versión/TLS, esquema public, django_migrations y tablas/conteos esperados, sin extraer datos personales. Inventariar si hay datos previos y su propietario. No asumir que una base vacía pertenece a SAP. No aplicar migraciones ni semillas hasta tener identidad, autorización y copia si procede. No hace falta compartir contraseñas en el chat.

## 5. Coherencia documental

| Material | Diferencia frente al candidato | Actualización necesaria |
| --- | --- | --- |
| README | Estado Fase 4; no explica F01–F03 ni SHA completo candidato; confirmación académica figura pendiente | Resumen funcional vigente, pruebas del SHA final, confirmación declarada por autor según auditoría; URL solo después de aceptación |
| memoria-pfm.md / PDF | Referencia 49ee198, 77 pruebas, propuesta Render y pendientes antiguos | Arquitectura elegida, migración/historial, fechas futuras, cierre histórico, versión y validación actuales; separar confirmación administrativa de evidencia documental |
| guion-video-pfm.md | 77 pruebas y referencia a Render | Guion cronometrado con infraestructura real, evidencia pública y breve rectificación; grabar después de aceptación |
| guion-demostracion.md / preparacion-defensa.md | Flujo anterior y explicación de última revisión | Medición efectiva por cadena y periodo; exclusión de futuras y vencimientos al cierre; demostrar errores y permisos |
| arquitectura.md y diagramas, dominio.md | Necesitan contraste con hosting y reglas corregidas | Origen único, función/CDN/Neon si se elige Vercel, nuevos invariantes; regenerar figuras |
| trazabilidad-requisitos.md, checklist-entrega.md | Resultados/pendientes de fases previas | SHA, CI y cuatro entregables coherentes |
| verificacion-publica.md | Acta sin ejecutar | Deployment ID, SHA, fecha/zona, rutas, pruebas, persistencia y restauración remotas |
| despliegue-vercel.md / neon-setup.md / verificacion-vercel.md | Guías preparadas y evidencias históricas | Destino verificado y configuración efectiva; mantener fechas de evidencias locales |
| Capturas, índices y PDF exportado | Representan versiones anteriores | Capturas ficticias de versión aceptada; hashes y regeneración PDF con enlaces revisados |

No convertir los informes de auditoría ni capturas antiguas en evidencias nuevas cambiándoles la fecha. Conservarlos y añadir aceptación nueva. El vídeo y la URL pública siguen pendientes; el éxito local no sustituye esos entregables.

## 6. Plan ejecutable por etapas — aún no autorizado para ejecución externa

1. **Fijar candidato local.** Revisar diff completo, incluir migración 0003 y pruebas/archivos no seguidos; revisar secretos; repetir checks del paquete Vercel y QA de producción sobre árbol final. Actualizar documentación técnica local, confirmar commit y registrar SHA. Dependencia: cierre de revisión del candidato.
2. **Inspeccionar hosting y base en lectura.** Resolver las hipótesis con panel/logs Vercel y metadatos Neon. Registrar IDs sin secretos, confirmar Production/main y alias canónico. Dependencia: acceso de lectura y decisión de destino.
3. **Confirmar coste y operación.** Preferencia actual del repositorio: Vercel Hobby + Neon Free para demo personal académica. Confirmar límites reales de la cuenta, alertas y periodo de disponibilidad. Si se elige Render, revisar Blueprint y presupuesto antes de crear sus dos recursos.
4. **Preparar publicación aprobada.** Antes de cualquier push, revisar si la integración Vercel publicaría automáticamente; evitar un despliegue accidental. Después de autorización, subir candidato y exigir CI verde del mismo SHA. Configurar entornos separados, secretos estables productivos, hosts y CSRF exactos, DEBUG=False, URL pooled y proxy gestionado. No compartir credenciales productivas con Preview.
5. **Preparar datos con autorización separada.** Confirmar nuevamente endpoint/base; backup previo si existen datos. Examinar plan de migraciones vía conexión directa; probar 0003 en entorno aislado equivalente y aplicar una sola vez al destino aprobado. Crear evaluador sin superusuario, con rol/cartera; segundo agente ficticio para aislamiento; cargar solo datos ficticios autorizados. Guardar credenciales en canal privado. No migrar desde build ni sembrar en cada redeploy.
6. **Desplegar SHA aprobado.** Preset/raíz/build según receta seleccionada. Verificar logs sin secretos, paquete React, función WSGI y estáticos. Registrar URL inmutable, ID y SHA. Si falla, conservar logs, no encadenar cambios de variables sin diagnóstico.
7. **Aceptar HTTPS y rutas.** Validar certificado, nombre, cadena y caducidad sin `-k`; redirección HTTP→HTTPS, HSTS, cookies Secure/HttpOnly/SameSite y ausencia de contenido mixto. GET / y /dashboard/ anónimos deben redirigir a login; /accounts/login/ debe devolver 200; /healthz/ 200 con JSON ok; /api/plans/ anónimo 403; con agente 200. Comprobar /admin/ y una ruta inexistente, y JS/CSS de /static/react/assets/ con 200. No confundir 404 del proveedor, 404 de dominio, 403 esperado y 503 de health.
8. **Aceptar el recorrido del evaluador.** Login/logout, cartera, indicador y clasificación; crear plan con varios objetivos, acciones y activación; revisión sin datos→rectificación→corrección con motivo/autor/fecha; historial y evaluación única por periodo; rechazar duplicados, futuras y acceso ajeno; cerrar con confirmación y comprobar instantánea/acciones, bloqueo posterior. Verificar errores recuperables y recarga en Chromium y vista móvil. La cuenta debe entrar sin necesitar cuenta de Vercel; probar protección del deployment desde sesión externa.
9. **Persistencia y recuperación.** Crear registro ficticio y guardar ID/datos de control; reiniciar/republicar el mismo código sin semillas, recuperar ese mismo ID y sesiones según política. Copia pg_dump por conexión directa, cifrada y con retención/responsable; restaurar en otra base autorizada aislada y comparar migraciones, conteos y registro. Nunca probar restore encima de Production. Verificar ventanas reales de recuperación Neon, no asumirlas por el nombre del plan.
10. **Cerrar entrega.** Rellenar acta pública, regenerar memoria/PDF/diagramas/capturas, grabar vídeo ≤5 min, comprobar enlaces desde usuario externo y coherencia de SHA/URL/evidencias. Mantener servicio durante evaluación/defensa y definir responsable de cuotas, caídas y backups. Un rollback de código no revierte una migración ni datos: revisar compatibilidad con 0003 antes de elegir un SHA anterior.

## 7. Costes y decisiones pendientes del titular

Vercel Hobby es gratuito para uso personal no comercial, con límites cuya superación puede suspender funciones: [plan Hobby](https://vercel.com/docs/plans/hobby). Neon Free anuncia $0, 100 CU-h mensuales y 1 GB por proyecto en la página consultada; estos límites actuales difieren de cifras históricas y deben confirmarse en la cuenta antes de publicar: [precios Neon](https://neon.com/pricing). Ninguno garantiza disponibilidad ilimitada.

Render implicaría coste del servicio web y de PostgreSQL, más almacenamiento/consumo aplicable. La página consultada no permitió extraer una tarifa numérica verificable para los tamaños del YAML; solicitar cotización del panel, moneda/impuestos y límite mensual antes de aprobar: [precios Render](https://render.com/pricing). No se ofrece un importe antiguo como presupuesto vigente. Dominio propio, planes superiores y almacenamiento de copias podrían añadir costes; no son necesarios para mantener el subdominio actual si resulta válido.

Se necesita del titular:

- Confirmar Vercel/Neon como destino, dominio y periodo que debe seguir operativo; o elegir explícitamente Render y presupuesto máximo.
- Acceso de lectura al proyecto/equipo Vercel, deployment Production, ajustes y logs; no basta conocer el dominio. Puede aportar esos metadatos redactados si no desea conectar la cuenta.
- Confirmación del proyecto/rama/base/rol/endpoint Neon mediante consola y acceso de lectura para contrastarlos; no enviar URLs con contraseña al chat.
- Definir cuenta del evaluador, segundo agente de prueba y canal privado para credenciales, así como si la demo será solo ficticia.
- Cuando el candidato y destino estén revisados, autorización explícita para commit/push/publicación y, por separado, migraciones/carga ficticia. Este informe no ejecuta esas operaciones.
- Responsable y ubicación privada de copias, retención, procedimiento de recuperación y presupuesto máximo para cualquier ampliación.

**Conclusión de diagnóstico:** las correcciones funcionales están verificadas localmente, pero faltan un SHA candidato completo, inspección de deployment y prueba de identidad Neon. La publicación solo se puede aceptar después del recorrido público y de persistencia/recuperación del SHA definitivo.
