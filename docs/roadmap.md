# Roadmap del MVP

## Fase 0 — Base verificable

Entorno local, dependencias fijadas, roles y asignación, vendedores, indicadores y políticas, plantilla Django, panel React y pruebas. La preparación Vercel no implica publicación. Véase el informe de verificación.

## Fase 1 — Planes y acciones (primera prioridad)

Implementar `ActionPlan` y `ActionItem` con problema, causa raíz, objetivos, responsables, vencimientos y estados. Registrar cambios relevantes y validar transiciones y relaciones en el backend. Un agente debe poder crear, editar y consultar el plan de un vendedor propio; otro agente no debe poder acceder mediante ningún endpoint relacionado. Añadir tests de persistencia, validación y permisos antes de incorporar formularios React.

## Fase 2 — Captura y seguimiento (segunda prioridad)

Implementar `FollowUp`, captura de indicadores para agentes autorizados y vistas React de planes y evolución. Definir formalmente la ventana mensual, normalizar el periodo común y evitar duplicados concurrentes si se amplía la captura. Cada revisión debe relacionar evidencias, compromisos y resultado posterior. Criterio de aceptación: demostrar un plan completo con dos revisiones, métricas persistidas y un agente ajeno sin acceso.

## Fase 3 — Entrega operativa y académica (tercera prioridad)

Probar sobre PostgreSQL y desplegar en Vercel bajo un mismo origen. Verificar variables privadas, cookies, CSRF, HTTPS, estáticos y persistencia tras una nueva instancia. Configurar copias y probar restauración, protección de login y revisión de seguridad. Preparar memoria PDF/Word, vídeo ≤5 min y URL pública; confirmar requisitos administrativos con el docente.

## Fuera del MVP

API Mirakl, datos corporativos, suspensión de tiendas, pagos, reaperturas, cuentas de vendedores, notificaciones asíncronas e inteligencia artificial. Cualquier ampliación necesita requisitos concretos; no se añaden herramientas de infraestructura preventivamente.
