# Matriz de cumplimiento del PFM — Fase 4

Fecha: **28/10/2026**. Fuente: [guía oficial consultada](fuentes-pfm.md). La matriz describe evidencia, no una calificación. «Cumplido y verificado» se limita al entorno indicado. Una prueba local no equivale a aceptación pública.

Estados: **Cumplido y verificado**; **Implementado, pendiente de validación**; **Pendiente**; **No verificable con la información disponible**. «Guía» identifica requisitos oficiales; «Fase 4» identifica comprobaciones adicionales del encargo.

| Requisito / origen | Evidencia disponible | Estado | Archivo o ubicación | Acción pendiente |
| --- | --- | --- | --- | --- |
| Modelos Django / Guía | Vendedores, políticas, observaciones y planes | Cumplido y verificado | `backend/*/models.py`; 77 pruebas PostgreSQL | Aceptación pública por separado |
| Vistas y plantillas / Guía | Portal, login, dashboard y Admin | Cumplido y verificado | `backend/config/views.py`, `backend/templates/` | — |
| Autenticación / Guía | Sesiones, login, logout y bloqueo en QA | Cumplido y verificado | `config/settings.py`, `config/tests.py`; Chromium | Repetir con dominio real |
| Persistencia / Guía | PostgreSQL local, reinicios y restauración coincidentes | Cumplido y verificado | `evidencias-fase-4.json`, `scripts/verify_phase3.py` | Validar persistencia remota por separado |
| React con datos Django / Guía | Dashboard, vendedores y planes consumen API | Cumplido y verificado | `frontend/src/pages/`, `services/api.js`, `ejemplo-react-django.json` | Mostrar en vídeo y producción |
| Flujo coherente de datos / Guía | 6% → 4,5% → 3%, acciones, revisión y cierre | Cumplido y verificado | `memoria-pfm.md`, §13; capturas locales | Repetir en URL pública |
| Despliegue público / Guía | Receta y runbook; sin URL confirmada | Pendiente | `render.yaml`, `despliegue.md`, `verificacion-publica.md` | Autorizar coste y desplegar |
| Continuidad durante evaluación / Guía | Condiciones y propuesta de operación | Pendiente | `despliegue.md` | Mantener servicios y supervisar |
| HTTPS y cookies públicos / Guía y Fase 4 | Ajustes y TLS local comprobados | Implementado, pendiente de validación | `config/settings.py`; R01–R02 | Comprobar certificado y proxy reales |
| Persistencia tras redeploy / Fase 4 | Release repetido local; sin deploy remoto | Implementado, pendiente de validación | R14–R15 en `verificacion-publica.md` | Comparar mismo plan antes/después |
| Estáticos y salud públicos / Fase 4 | WhiteNoise y salud 200/503 locales | Implementado, pendiente de validación | R16–R17; `config/views.py` | Verificar servicio real |
| GitHub público o compartido / Guía | API sin autenticar: `private=false` | Cumplido y verificado | [Repositorio](https://github.com/Pablorossl/Seller-Action-Plan-SAP-) | Publicar Fase 4 sólo con autorización |
| README reproducible / Guía | Instalación, configuración, migraciones, arranque y tests | Cumplido y verificado | `../README.md` | Añadir URL real cuando exista |
| Historial progresivo / Guía | Cinco commits, base y fases separadas | Cumplido y verificado | `git log`; `fase-4.md` | Registrar Fase 4 por bloques |
| Estructura y dependencias / Guía | Apps, versiones fijadas, MIT, ignore y migraciones | Cumplido y verificado | `backend/`, `frontend/`, `LICENSE`, `.gitignore` | — |
| CI remota / Fase 4 | `success` para Fase 3 y dos fases anteriores | Cumplido y verificado | [Run 40747706230](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/40747706230) | Comprobar nuevo SHA tras push autorizado |
| Problema y contexto / Guía | Necesidad profesional, independencia y alcance | Cumplido y verificado | `memoria-pfm.md`, §§1–2 | Revisión personal del autor |
| Aportación y eficiencia / Guía | Beneficios esperados separados de resultados medidos | Cumplido y verificado | `memoria-pfm.md`, §§3 y 15 | Ensayar explicación propia |
| Tecnologías justificadas / Guía | Tecnologías efectivas y su función | Cumplido y verificado | `memoria-pfm.md`, §5 | — |
| Tipos de usuarios / Guía | Grupo, permisos y propietario | Cumplido y verificado | `memoria-pfm.md`, §8 | — |
| Casos de uso / Guía | Nueve casos con actor, flujo, resultado y alternativas | Cumplido y verificado | `memoria-pfm.md`, §9 | — |
| Seguridad y protección de datos / Guía | Sesión, hashing, permisos, CSRF/XSS, validación y límites | Cumplido y verificado | `memoria-pfm.md`, §10; tests | Aceptación remota en filas propias |
| Backups y recuperación / Guía y Fase 4 | Recuperación local; retención remota propuesta | Implementado, pendiente de validación | `despliegue.md`, R18 | Activar y ensayar recuperación remota autorizada |
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
| Entrega de cuatro elementos / Guía | GitHub y memoria; aplicación y vídeo faltan | Pendiente | `checklist-entrega.md` | Completar y revisar todos los enlaces |

## Rúbrica oficial

| Criterio | Peso | Evidencia para defenderlo | Límite actual |
| --- | ---: | --- | --- |
| Backend Django | 30% | Modelos, servicios, plantillas, API y pruebas | Sin aceptación pública |
| Integración React | 15% | Datos persistidos y escrituras Fetch | Demo pública y vídeo pendientes |
| Arquitectura y buenas prácticas | 15% | Monolito modular, migraciones, Git y CI | Fase 4 aún sin publicar |
| Seguridad e integridad | 15% | Permisos, CSRF, bloqueos, revisión, idempotencia y restauración | Proxy y recuperación remotos pendientes |
| Documentación y presentación | 15% | Memoria, capturas, diagramas y preparación oral | Vídeo, entrega y ensayo pendientes |
| Reflexión y valor aportado | 10% | Contexto, beneficios esperados, límites y decisiones | Sin estudio de impacto profesional |

Nota mínima: **7/10**. No se deduce una calificación del número de tests. **Fase 4 no finalizada y proyecto todavía no listo para entrega oficial.**
