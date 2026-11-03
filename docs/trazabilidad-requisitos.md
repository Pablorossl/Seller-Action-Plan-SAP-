# Matriz de cumplimiento del PFM — Fase 4

Actualizada: **03/11/2026**. Fuente académica: [guía oficial consultada el 28/10/2026](fuentes-pfm.md). La matriz describe evidencia, no una calificación. «Cumplido y verificado» se limita al entorno indicado. La aplicación ya tiene [aceptación técnica pública](verificacion-publica.md) sobre Vercel Hobby y Neon Free, con [resultados sin secretos](evidencias-publicacion-2026-11-03.json). Las evidencias de fases anteriores mantienen su fecha y alcance local.

Estados: **Cumplido y verificado**; **Implementado, pendiente de validación**; **Pendiente**; **No verificable con la información disponible**. «Guía» identifica requisitos oficiales; «Fase 4» identifica comprobaciones adicionales del encargo.

| Requisito / origen | Evidencia disponible | Estado | Archivo o ubicación | Acción pendiente |
| --- | --- | --- | --- | --- |
| Modelos Django / Guía | Vendedores, políticas, observaciones y planes | Cumplido y verificado | `backend/*/models.py`; 77 pruebas PostgreSQL | Aceptación pública por separado |
| Vistas y plantillas / Guía | Portal, login, dashboard y Admin | Cumplido y verificado | `backend/config/views.py`, `backend/templates/` | — |
| Autenticación / Guía | Login/logout, sesión segura y API pública; bloqueo de login en CI/QA | Cumplido y verificado | `verificacion-publica.md`, R02/R11/R12; Chromium público | Mantener credenciales por canal privado |
| Persistencia / Guía | Mismo JSON, acciones, revisiones, cierre y sesión tras redesplegar; copia Neon restaurada aisladamente | Cumplido y verificado | `evidencias-publicacion-2026-11-03.json` | Mantener copias privadas y continuidad |
| React con datos Django / Guía | Dashboard, vendedores y planes consumen y modifican API pública real | Cumplido y verificado | `verificacion-publica.md`, R03–R16; nuevas capturas públicas | Mostrar en vídeo |
| Flujo coherente de datos / Guía | 6% → 4,5% → 3%, acciones, revisión, evaluación y cierre públicos | Cumplido y verificado | Plan de control 5; acta y capturas públicas | Incorporar a memoria/vídeo |
| Despliegue público / Guía | HTTPS público, Django/React/CDN, SHA aprobado y alias verificado | Cumplido y verificado | `https://sap-bice.vercel.app`; SHA `97b4bff`; deployment `dpl_DVtuHFEv9eTba7V8ShdLASR9BBTi` | Mantener disponible durante evaluación |
| Continuidad durante evaluación / Guía | Plan de operación sujeto a cuotas Hobby/Free | Pendiente | `despliegue-vercel.md`, §8 | Verificar cuotas y mantener servicios durante revisión y defensa |
| HTTPS y cookies públicos / Guía y Fase 4 | TLS validado, HTTP→HTTPS, HSTS y cookies seguras públicos | Cumplido y verificado | R01–R02 | Comprobación adicional desde otra red pendiente |
| Persistencia tras redeploy / Fase 4 | Planes 5/6 conservados entre dos deployments del mismo SHA, sin semillas/migraciones repetidas | Cumplido y verificado | R14–R15; `redeployment_persistence` en JSON público | — |
| Estáticos y salud públicos / Fase 4 | JS/CSS sin errores, móvil 390 px y health público 200 antes/después | Cumplido y verificado | R16–R17 | No se provocó una caída de Production |
| GitHub público o compartido / Guía | API sin autenticar: `private=false`, comprobado el 28/10/2026 | Cumplido y verificado | [Repositorio](https://github.com/Pablorossl/Seller-Action-Plan-SAP-) | Publicar el nuevo commit y verificar acceso al SHA de entrega |
| README reproducible / Guía | Instalación, configuración, migraciones, arranque y tests | Cumplido y verificado | `../README.md` | Añadir URL real cuando exista |
| Historial progresivo / Guía | Base y fases separadas; Fase 4 registrada en `57d296f` | Cumplido y verificado | `git log`; `fase-4.md`; adaptación Vercel/Neon en este cambio | Conservar el SHA definitivo de entrega |
| Estructura y dependencias / Guía | Apps, versiones fijadas, MIT, ignore y migraciones | Cumplido y verificado | `backend/`, `frontend/`, `LICENSE`, `.gitignore` | — |
| CI remota / Fase 4 | `success` del SHA exacto desplegado `97b4bff55a07b8fd3c71b05740748db5bf63438b` | Cumplido y verificado | [Run 41722300443](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/41722300443) | La documentación posterior se versiona por separado |
| Problema y contexto / Guía | Necesidad profesional, independencia y alcance | Cumplido y verificado | `memoria-pfm.md`, §§1–2 | Revisión personal del autor |
| Aportación y eficiencia / Guía | Beneficios esperados separados de resultados medidos | Cumplido y verificado | `memoria-pfm.md`, §§3 y 15 | Ensayar explicación propia |
| Tecnologías justificadas / Guía | Tecnologías efectivas y su función | Cumplido y verificado | `memoria-pfm.md`, §5 | — |
| Tipos de usuarios / Guía | Grupo, permisos y propietario | Cumplido y verificado | `memoria-pfm.md`, §8 | — |
| Casos de uso / Guía | Nueve casos con actor, flujo, resultado y alternativas | Cumplido y verificado | `memoria-pfm.md`, §9 | — |
| Seguridad y protección de datos / Guía | Sesión, hashing, permisos, CSRF/XSS, validación y límites | Cumplido y verificado | `memoria-pfm.md`, §10; tests | Aceptación remota en filas propias |
| Backups y recuperación / Guía y Fase 4 | Snapshot Neon exportado con cliente 18.6 y restaurado en PostgreSQL 18 aislado; 21 tablas/digests y esquema coincidentes | Cumplido y verificado | R18; `recovery` en JSON público | Custodiar copia privada y repetir tras cambios relevantes |
| Memoria PDF o Word / Guía | Markdown completo y PDF para revisión | Cumplido y verificado | `memoria-pfm.md`, `memoria-pfm.pdf`, `exportacion-memoria.md` | Actualizar datos remotos antes de entregar |
| Capturas, diagramas y ejemplos / Guía | 16 capturas locales, cuatro SVG y JSON ficticio | Cumplido y verificado | `evidencias-visuales.md`, `diagramas/`, `screenshots/` | Incorporar evidencia pública cuando exista |
| Vídeo real ≤5 minutos / Guía | Guion de 4:50; no hay grabación | Pendiente | `guion-video-pfm.md` | Grabar y comprobar duración/audio/imagen |
| Enlace accesible de vídeo / Guía | No disponible | Pendiente | `checklist-entrega.md` | Subir con autorización y probar acceso |
| Problema, demo, tecnologías y React en vídeo / Guía | Contenido planificado | Pendiente | `guion-video-pfm.md` | Confirmar contenido del archivo real |
| Defensa ≤20 minutos / Guía | Exposición 11 min + 9 min preguntas, 25 respuestas | Implementado, pendiente de validación | `preparacion-defensa.md` | Ensayar; agendar tras revisión docente |
| Autoría y comprensión / Guía | Código, historial y material de razonamiento | No verificable con la información disponible | Historial y defensa | Demostración personal ante tribunal |
| Prework aprobado / Guía | Sin expediente o confirmación accesible | No verificable con la información disponible | `fuentes-pfm.md` | Confirmación de autor/equipo docente |
| Frontend aprobado / Guía | Sin expediente o confirmación accesible | No verificable con la información disponible | `fuentes-pfm.md` | Confirmación de autor/equipo docente |
| Backend aprobado / Guía | Sin expediente o confirmación accesible | No verificable con la información disponible | `fuentes-pfm.md` | Confirmación de autor/equipo docente |
| Autorización docente previa / Guía | Sin evidencia personal | No verificable con la información disponible | `fuentes-pfm.md` | Acreditar confirmación; no se presume |
| Sin secretos conocidos / Fase 4 | Revisión acotada de 166 blobs históricos y candidatos | Cumplido y verificado | `evidencias-fase-4.json`, `.gitignore` | Revisión final antes del commit/push |
| Entrega de cuatro elementos / Guía | GitHub, memoria para actualizar y aplicación pública; falta vídeo real accesible | Pendiente | `checklist-entrega.md` | Actualizar memoria/PDF, grabar vídeo y revisar enlaces |

## Rúbrica oficial

| Criterio | Peso | Evidencia para defenderlo | Límite actual |
| --- | ---: | --- | --- |
| Backend Django | 30% | Modelos, servicios, plantillas, API, CI y aceptación pública | Alcance de pruebas delimitado en acta |
| Integración React | 15% | Datos persistidos y escrituras Fetch en público | Vídeo pendiente |
| Arquitectura y buenas prácticas | 15% | Monolito modular, Git, CI aprobada y Vercel/Neon públicos | Actualizar memoria/PDF a la arquitectura aceptada |
| Seguridad e integridad | 15% | Permisos, CSRF, proxy, revisión, cierre histórico y recuperación de copia Neon | No se simularon fallos de Production |
| Documentación y presentación | 15% | Memoria, capturas, diagramas y preparación oral | Vídeo, entrega y ensayo pendientes |
| Reflexión y valor aportado | 10% | Contexto, beneficios esperados, límites y decisiones | Sin estudio de impacto profesional |

Nota mínima: **7/10**. No se deduce una calificación del número de tests. **Fase 4 no finalizada y proyecto todavía no listo para entrega oficial.**

## Vigencia del candidato local — 03/11/2026

La guía original se volvió a leer mediante Google Drive (modificación 08/10/2026). Sus requisitos no exigen rectificaciones, una política concreta de fechas ni un formato de instantánea: F01–F03 son decisiones funcionales de SAP que refuerzan el flujo verificable, los casos de uso con errores y la integridad de datos. SAP sigue siendo una herramienta académica independiente para Account Managers/Marketplace Support Agents, sin integración oficial con Mirakl o PcComponentes.

Las cifras de 77 pruebas de las filas anteriores identifican evidencia histórica. Para este incremento, la suite completa ejecutada en PostgreSQL temporal consta de 112 pruebas correctas sin omisiones; después se ampliaron límites de cierre y se verificó su módulo (27 pruebas, incluidas 25 importadas). Véanse [F01](rectificacion-revisiones-2026-11-03.md), [concurrencia y F02](concurrencia-y-observaciones-futuras-2026-11-03.md) y [F03](cierre-historico-f03-2026-11-03.md). Los recuentos incluyen pruebas heredadas/importadas y no equivalen a casos de uso independientes.

El autor confirmó actividades previas y autorización docente según la [auditoría del 02/11](auditoria-integral-2026-11-02.md); no se ha inspeccionado su expediente. Esto actualiza la ausencia de confirmación registrada en las filas históricas, sin convertirlo en verificación documental.

Este candidato es local: siguen pendientes publicación del SHA definitivo y su CI, identidad del destino Neon, despliegue funcional estable, aceptación pública, persistencia/recuperación remotas, actualización final de memoria/PDF y evidencias, vídeo accesible de hasta cinco minutos y preparación/defensa personal. El [diagnóstico de publicación](diagnostico-publicacion-2026-11-03.md) concreta pasos y accesos. No se declara completada la entrega académica.

## Actualización posterior: publicación técnica aceptada

El candidato `97b4bff` se publicó con CI aprobada y quedó accesible en SAP. Se completaron el flujo público, las rectificaciones, el rechazo de fechas futuras, la conservación del cierre, CSRF, aislamiento, persistencia entre deployments del mismo SHA y restauración aislada de una copia real de Neon. La lectura con calendario avanzado 90 días se efectuó solo en la copia restaurada. El párrafo anterior conserva el estado previo de la revisión del candidato, superado en estos aspectos por el [acta pública](verificacion-publica.md).

Continúan pendientes la memoria/PDF actualizados, el vídeo accesible de hasta cinco minutos, la entrega formal y la defensa personal. La continuidad debe mantenerse durante la evaluación; comprobar planes y cuotas sin activar servicios de pago. Las nuevas capturas públicas complementan las antiguas, que no se renombraron como pruebas remotas.
