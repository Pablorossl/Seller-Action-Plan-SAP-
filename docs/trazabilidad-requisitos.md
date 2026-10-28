# Matriz de cumplimiento del PFM

Actualizada el 27/10/2026. Sigue los requisitos transcritos en el encargo y la guía identificada en la revisión anterior; no hay copia oficial versionada ni certificación académica.

| Requisito | Estado | Evidencia y pendiente |
| --- | --- | --- |
| Django: modelos, vistas, plantillas y autenticación | Implementado y probado | Apps de dominio, portal, login/logout, API y Admin |
| Persistencia e integridad | Probadas localmente | Migraciones vacías, restricciones, PostgreSQL 14.24, reinicios y restauración; proveedor remoto pendiente |
| React consumiendo Django | Implementado y probado | Dashboard, vendedores y ciclo completo de planes con datos reales de la base ficticia |
| Flujo funcional completo | Probado en QA | Chromium, Gunicorn y PostgreSQL con DEBUG=False: 6% → 4,5% → 3%, cierre, recarga y permisos |
| URL pública funcional | **Pendiente** | Blueprint Render y runbook preparados; faltan acceso, autorización de coste/push y pruebas remotas |
| Seguridad | Probada localmente; aceptación remota pendiente | CSRF, sesión, alcance por vendedor, login limitado, configuración TLS, ocho pruebas de concurrencia; proxy/HTTPS público pendientes |
| Repositorio e historial | Parcial | Commits anteriores conservados, README actualizado y cambios Fase 3 locales; no se ha hecho push ni comprobado acceso docente |
| Arquitectura coherente | Conservada | Monolito Django + React, PostgreSQL y WSGI sin infraestructura innecesaria |
| Documentación técnica | Preparada | README, arquitectura, `fase-3.md`, `despliegue.md`, evidencia JSON y capturas ficticias |
| Memoria PDF/Word | Fase 4 | Documentación actual es materia prima, no memoria final |
| Vídeo ≤5 min y defensa ≤20 min | Fase 4 | No se han generado ni ensayado en esta fase |
| Actividades obligatorias y autorización docente | No verificable | Requiere expediente/confirmación externa |

## Rúbrica

| Criterio | Peso | Evidencia actual | Pendiente principal |
| --- | ---: | --- | --- |
| Backend Django | 30% | Dominio, ORM, auth, vistas, plantillas y pruebas | Validación del mismo código desplegado |
| Integración React | 15% | Interfaz operativa, Fetch/CSRF y flujo Chromium | Repetir desde URL pública |
| Arquitectura y buenas prácticas | 15% | Separación de apps, dependencias fijadas, migraciones y CI preparada | CI remota y revisión del hito publicado |
| Seguridad e integridad | 15% | PostgreSQL, bloqueos, revisión, idempotencia, permisos y recuperación | Proxy/TLS y backups del proveedor |
| Documentación y presentación | 15% | Informes y runbook reproducibles | Memoria, vídeo y URL |
| Reflexión y valor aportado | 10% | Complemento de Mirakl, decisiones, límites y utilidad operativa | Síntesis y defensa en Fase 4 |

La nota mínima indicada es 7/10. No se calcula ni garantiza una calificación a partir de estos estados. La Fase 3 no se declara completa mientras falten los criterios remotos.
