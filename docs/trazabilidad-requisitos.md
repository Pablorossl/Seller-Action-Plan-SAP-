# Matriz de cumplimiento del PFM

Estados actualizados para Fase 1; no constituyen certificación académica. Se siguen los requisitos transcritos por el usuario y la referencia a la guía identificada en la revisión del 22/10. No hay una copia oficial versionada en el repositorio.

| Requisito | Estado | Evidencia y pendiente |
| --- | --- | --- |
| Backend Django | Cumplido | `backend/manage.py`, `config/settings.py`, apps `sellers`, `quality` y `action_plans` |
| Modelos, vistas, plantillas, autenticación y persistencia | Cumplido | Modelos y migraciones, portal `home.html`, login/logout, SQLite y tests de persistencia |
| React en una o dos vistas con datos reales | Cumplido | Secciones de vendedores e indicadores en `frontend/src/main.jsx`, Fetch a API Django; no son rutas SPA independientes |
| Aplicación funcional y flujo real | Cumplido en Fase 1 | Plan completo por Admin: dos acciones, dos revisiones y cierre; API y formularios React de planes quedan para Fase 2 |
| GitHub, README e historial significativo | Parcialmente cumplido | Remoto e historial existentes; commit local del hito de Fase 1 con implementación, pruebas e informe técnico; publicación remota pendiente |
| Despliegue mediante URL pública | Pendiente | Configuración Vercel preparada, sin despliegue ni PostgreSQL externo verificados |
| Seguridad y protección de datos | Parcialmente cumplido | Pruebas CSRF, roles, recursos y escape; TLS real, backups, auditoría y resistencia de login pendientes |
| Arquitectura y estructura coherentes | Cumplido | Separación Django/React y apps de dominio; decisiones en `arquitectura.md` |
| Documentación de problema, aportación, tecnologías, usuarios, casos de uso y seguridad | Cumplido | README, dominio, arquitectura, roles y endpoints; evidencia final deberá pasar a la memoria |
| Memoria PDF/Word y vídeo de máximo 5 min | Pendiente | `esquema-informe-pfm.md` y `guion-demostracion.md` son preparación, no entregables finales |
| Prework, Frontend y Backend obligatorios aprobados | No verificable | Requiere expediente o confirmación docente externa |
| Autorización docente para iniciar PFM | No verificable | No se infiere del código ni del acceso al repositorio |

## Rúbrica y evidencias a reunir

| Apartado | Peso | Evidencia actual | Para completar el objetivo |
| --- | --- | --- | --- |
| Backend Django | 30 % | ORM, migraciones, auth, plantillas, API y flujo de planes por Admin probado | Validación final sobre PostgreSQL y aplicación desplegada |
| Integración React | 15 % | Dos secciones con datos persistidos | Formularios y seguimiento de planes, usabilidad y pruebas |
| Arquitectura y buenas prácticas | 15 % | Dependencias fijadas, separación de responsabilidades, tests y CI preparada | Historial significativo, revisión y refactorización según necesidades |
| Seguridad e integridad | 15 % | Acceso por vendedor, CSRF, rangos, restricciones y políticas versionadas | PostgreSQL, auditoría de cambios, revisión operativa y restauración |
| Documentación y presentación | 15 % | README y documentos de apoyo | Memoria final, vídeo y URL pública comprobable |
| Reflexión y valor aportado | 10 % | Problema y alcance delimitados | Evaluar utilidad con escenarios, límites y decisiones justificadas |

Nota mínima indicada: 7/10. Los porcentajes no permiten calcular una nota real a partir de esta base. Confirmar que las dos secciones React satisfacen el criterio de «vistas» de la versión de la guía que aplique al alumno.
