# Roadmap del MVP

## Fase 0 — Base verificable

Entorno local, dependencias fijadas, roles y asignación, vendedores, indicadores y políticas, plantilla Django, panel React y pruebas. La preparación Vercel no implica publicación. Véase el informe de verificación.

## Fase 1 — Planes, acciones y revisiones (implementada)

Modelos `ImprovementPlan`, `PlanMetric`, `PlanAction` y `PlanReview`, migración aditiva, permisos por vendedor y operación de cierre con resultado y razones. Django Admin permite demostrar el caso 6% → 4,5% → 3%, dos acciones y dos revisiones. Se mantienen los indicadores, sus políticas y las dos secciones React. Evidencias y límites en [fase-1.md](fase-1.md).

## Fase 2 — Interfaz operativa (siguiente prioridad)

Crear API y formularios React para el módulo implementado, con ficha de vendedor, edición de acciones, captura de revisiones y cierre. Reutilizar acceso por vendedor, permisos y servicios, y mantener los errores de servidor visibles. Empezar por comparar valor inicial, objetivo y revisiones en una tabla; las gráficas son opcionales. No reconstruir el frontend existente.

## Fase 3 — Entrega operativa y académica (tercera prioridad)

Probar sobre PostgreSQL y desplegar en Vercel bajo un mismo origen. Verificar variables privadas, cookies, CSRF, HTTPS, estáticos y persistencia tras una nueva instancia. Configurar copias y probar restauración, protección de login y revisión de seguridad. Preparar memoria PDF/Word, vídeo ≤5 min y URL pública; confirmar requisitos administrativos con el docente.

## Fuera del MVP

API Mirakl, datos corporativos, suspensión de tiendas, pagos, reaperturas, cuentas de vendedores, notificaciones asíncronas e inteligencia artificial. Cualquier ampliación necesita requisitos concretos; no se añaden herramientas de infraestructura preventivamente.
