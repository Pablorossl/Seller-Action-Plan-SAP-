# Revisión de preparación para la entrega — 22/10/2026

## Dictamen

SAP tiene una base técnica funcional, pero todavía no está preparado para entregar como herramienta de planes de mejora: permite consultar vendedores e indicadores, pero no crear planes, acciones ni revisiones. También faltan evidencias de despliegue público y los entregables académicos finales.

Esta revisión contrasta el código versionado en `f844974`, la documentación del repositorio y la guía académica localizada en Drive. No asigna una nota ni un porcentaje de finalización: aprobar pruebas locales no acredita todos los criterios de evaluación.

## Fuente académica comprobada

[FS Proyecto Final - Máster en Desarrollo Full Stack](https://docs.google.com/document/d/1KhmvNgC4g9WI8suPOBjGFcUCQeA8rVPkoVS53fYLOkQ/edit), documento compartido en Drive, modificado el 08/10/2026 y consultado el 22/10/2026. La guía denomina el trabajo PFM, aunque en la conversación se use TFG.

La guía exige cuatro entregables: repositorio GitHub, aplicación desplegada, memoria PDF/Word y vídeo mediante enlace de duración máxima de cinco minutos. La aplicación debe seguir disponible durante revisión y defensa. La defensa por videollamada tiene una duración máxima de veinte minutos y se agenda después de superar la revisión inicial. La nota mínima es 7/10.

También exige haber aprobado las actividades obligatorias de Prework, Frontend y Backend y contar con confirmación docente para iniciar el proyecto. Esos requisitos personales no quedan acreditados por el repositorio.

La sección de requisitos mínimos pide repositorio público; el procedimiento acepta público o compartido con el equipo docente. Un repositorio público satisface ambas formulaciones. Si se mantiene privado, confirmar con el docente y comprobar su acceso.

## Requisitos frente al estado observado

| Requisito | Estado comprobado | Trabajo pendiente |
| --- | --- | --- |
| Django: modelos, vistas, plantillas, autenticación y persistencia | Implementado para vendedores e indicadores | Extender al flujo de planes del alcance de SAP |
| React: una o dos vistas que consuman datos del backend | Panel con dos secciones y Fetch a la API real | Demostrarlo en la versión desplegada; la guía no exige dos rutas SPA |
| Aplicación completa y coherente con el problema | Parcial: consulta y clasificación; no hay gestión de planes | Cerrar un flujo de plan, acciones y revisión, o redefinir expresamente el alcance con el docente |
| URL pública estable y funcional | No acreditada; solo configuración preparada | Desplegar y comprobar acceso, login, estáticos y persistencia |
| GitHub, README e historial progresivo | README amplio; dos commits locales, incluido el de implementación | Comprobar acceso docente y continuar con commits que reflejen trabajo real |
| Memoria PDF/Word | Solo existe un esquema Markdown | Redactar y exportar documento final con capturas, diagramas y ejemplos |
| Vídeo accesible mediante enlace, máximo cinco minutos | Solo existe guion preparatorio | Grabar, comprobar duración y acceso al enlace |
| Seguridad y protección de datos | Controles de aplicación y pruebas locales presentes | Verificar HTTPS y sesiones reales; configurar y probar copias de seguridad |
| Reflexión sobre aportación y eficiencia | Problema y objetivos descritos; falta evaluación final | Explicar mejoras del proceso con escenarios y evidencias, límites y decisiones |
| Requisitos administrativos y defensa | No comprobados | Confirmación docente y preparación de explicación técnica propia |

Los pesos confirmados por la guía son backend 30 %, React 15 %, arquitectura 15 %, seguridad e integridad 15 %, documentación y presentación 15 %, reflexión y valor 10 %. La falta de memoria y reflexión afecta a apartados con peso propio; no conviene posponerlos hasta después de ampliar funcionalidades opcionales.

## Qué funciona

- Django gestiona usuarios, grupos, login/logout, sesiones, portal HTML y persistencia.
- La API permite crear, consultar, editar y eliminar vendedores accesibles. El servidor asigna el propietario y bloquea modificaciones sobre vendedores ajenos.
- Las métricas y políticas tienen modelos, migraciones, validaciones, clasificación y lectura por API. Los umbrales utilizados se preservan mediante versiones y validación de guardado.
- React muestra vendedores e indicadores persistidos, con carga, vacío, errores y lectura paginada. Las dos secciones pertenecen a un mismo componente.
- Hay controles CSRF, escape de plantillas, permisos por vendedor, restricciones de base de datos y configuración de producción.
- Las dependencias están fijadas, existe demo reproducible y hay un workflow de CI escrito.

## Pendientes funcionales prioritarios

### 1. Planes y acciones

No existen modelos, migraciones, endpoints ni formularios para `ActionPlan` y `ActionItem`. Solo aparecen como diseño futuro en `docs/arquitectura.md` y `docs/hoja-de-ruta.md`. Las únicas rutas de dominio registradas en `backend/config/urls.py` son vendedores e indicadores.

Implementar un plan vinculado a un vendedor y a la desviación que lo motiva, con problema, causa raíz, objetivo, responsable, fechas y estado. Incorporar acciones con compromiso concreto, responsable, vencimiento y resultado o evidencia. Validar relaciones, fechas y transiciones en Django.

**Cierre:** un agente crea y edita un plan de un vendedor propio, añade acciones, recarga y conserva los datos; otro agente no puede consultar ni modificar el plan o sus recursos relacionados.

### 2. Seguimiento y resultado

No existe `FollowUp` ni relación entre un plan y resultados posteriores. El clasificador evalúa observaciones individuales; no calcula evolución ni demuestra mejora.

Registrar revisiones con fecha, autor, observaciones, resultado y referencia a nuevas métricas. Definir qué permite cerrar un plan y conservar los cambios relevantes. No es necesario construir un sistema genérico de auditoría para cerrar este flujo, pero sí explicar quién registró cada revisión y cuándo.

**Cierre propuesto para SAP:** demostrar una desviación inicial, un plan con dos acciones y dos revisiones, y comparar el resultado final con el objetivo. Es un criterio de aceptación del MVP propuesto aquí y en el roadmap; la guía académica no exige ese número de acciones o revisiones.

### 3. Interfaz operativa

`frontend/src/main.jsx` solo consulta datos. No permite crear o editar vendedores, capturar métricas ni gestionar planes. Las escrituras de vendedores están disponibles por API y las métricas se registran mediante Django Admin.

Priorizar formularios de planes, acciones y revisiones y una ficha del vendedor que conecte indicadores con planes. Mostrar errores de validación, confirmación de guardado y estados comprensibles. Añadir navegación de sesión para acceder al portal y cerrar sesión desde el panel.

Capturar métricas desde React es útil para que el agente complete toda la operativa. También puede mantenerse la carga administrativa en el MVP si se explica y permite demostrar el flujo completo. Las gráficas de evolución son opcionales: una comparación clara de observaciones puede bastar.

## Despliegue y seguridad operativa

La configuración `backend/vercel.json` y el script `scripts/check_production.py` preparan el despliegue. El script usa datos ficticios y no conecta a PostgreSQL. No hay evidencia de una URL pública operativa.

Antes de entregar:

1. Configurar un servicio de aplicación y PostgreSQL persistente, conforme a los ajustes actuales del proyecto. Vercel es una elección del proyecto; la guía admite otros proveedores.
2. Configurar variables privadas, hosts, orígenes CSRF y confianza en el proxy según el entorno real.
3. Aplicar migraciones, disponer de cuentas de demostración con datos ficticios y comprobar el acceso del evaluador. `seed_demo` está bloqueado con `DEBUG=False`: hay que preparar una carga de demostración controlada para el entorno de evaluación.
4. Verificar HTTPS, login/logout, acceso entre agentes, escrituras CSRF, dashboard y estáticos desde la URL real.
5. Crear datos, volver a desplegar y comprobar que persisten.
6. Configurar copias de seguridad y demostrar una restauración aislada; documentar qué se hizo y qué cubre.
7. Revisar la protección ante intentos repetidos de login del servicio elegido. La recuperación de contraseña y un registro general de auditoría son mejoras de seguridad, no entregables independientes explícitos de la guía.

La unicidad de métricas entre versiones de una política se valida en aplicación, pero la restricción SQL usa el identificador de política. Las escrituras concurrentes o masivas podrían eludir parte de esa validación. Está documentado en la arquitectura: reforzarlo si se añade importación o captura concurrente; no presentar el esquema actual como garantía universal de integridad. Definir también la ventana mensual y procedencia antes de automatizar métricas; hoy son observaciones manuales por periodo.

## Memoria, vídeo y defensa

La memoria debe desarrollar los seis apartados explícitos de la guía: problema; reflexión sobre aportación y eficiencia; tecnologías justificadas; tipos de usuarios; casos de uso con flujo, resultado y errores; seguridad y protección de datos. Añadir capturas de la versión final, diagrama del modelo y arquitectura, ejemplos, pruebas observadas, URL y commit de entrega. El README y los Markdown de apoyo no sustituyen este archivo.

La reflexión debería comparar cómo se realiza el seguimiento sin SAP y con SAP, qué trabajo simplifica y qué evidencia conserva. Si se mide tiempo o se consulta a usuarios, describir el procedimiento y los resultados reales. Si no hay medición, presentarlo como beneficio esperado y reconocer la limitación.

El vídeo debe mostrar problema, demostración funcional, tecnologías y React consumiendo datos de Django. Grabar la versión entregada, comprobar que dura como máximo cinco minutos y abrir el enlace como lo hará el evaluador.

Preparar una defensa de hasta veinte minutos: explicar modelo de datos, sesiones y CSRF, permisos por vendedor, validaciones, React/Fetch, pruebas, despliegue y límites. La guía evalúa autoría y comprensión integral; es necesario poder explicar y modificar el código entregado.

## Documentación desactualizada

- README y matriz afirman que no se dispone de la guía oficial. Esta revisión ya identifica y contrasta el documento compartido por la academia.
- README y matriz citan solo el commit inicial. Actualmente existen `048450c` y `f844974`. La auditoría inicial puede conservar esa afirmación como dato histórico.
- `docs/verificacion.md` describe cambios todavía sin commit ni push. Al comenzar esta revisión el árbol estaba limpio y `main` coincidía con la referencia local `origin/main`. Esto no verifica por sí solo el acceso web del docente ni el estado remoto actual de Actions.
- La ejecución remota de CI sigue sin comprobarse en esta revisión. Hay que consultar el resultado de GitHub Actions para el commit que se vaya a entregar.

## Verificación ejecutada en esta revisión

| Comprobación | Resultado |
| --- | --- |
| `pip check` | Sin dependencias incompatibles |
| `manage.py check` | Sin incidencias |
| `makemigrations --check --dry-run` | Sin cambios pendientes |
| `migrate --check` | Correcto |
| `manage.py test --verbosity 2` | 18 pruebas aprobadas sobre SQLite de test |
| `npm test` y ejecución con Node 22 | Correctos; archivo de pruebas Fetch con casos de paginación y denegación |
| `npm run build` | Compilación Vite correcta |
| `manage.py collectstatic --noinput` | Correcto; recursos del frontend y administrador recogidos |
| `scripts/check_production.py` | Correcto con configuración ficticia; no prueba PostgreSQL ni despliegue |

Se revisaron backend, frontend, migraciones, pruebas, scripts, plantillas, configuración de CI/despliegue y documentación. No se repitió la prueba de navegador descrita en `docs/verificacion.md` ni se verificaron PostgreSQL externo, disponibilidad pública, restauración o ejecución remota de CI. El acceso público al repositorio no pudo confirmarse mediante la herramienta web; ese fallo no demuestra que sea privado.

## Orden de trabajo recomendado

1. Confirmar las condiciones administrativas y fijar el alcance final.
2. Implementar planes y acciones con permisos y persistencia.
3. Incorporar revisiones, comparación de resultados y formularios para demostrar el ciclo completo.
4. Extender las pruebas a las nuevas relaciones, estados y acceso entre agentes; comprobar el flujo en navegador.
5. Desplegar, comprobar persistencia y seguridad operativa y dejar acceso de evaluación.
6. Actualizar documentación y comprobar CI y acceso a GitHub.
7. Terminar la memoria con evidencias finales y grabar el vídeo; preparar la defensa.

La memoria puede redactarse en paralelo al desarrollo, actualizando capturas y resultados al cerrar la versión. No hace falta incorporar Docker, microservicios, IA, integraciones Mirakl ni gráficas para satisfacer los mínimos de la guía.
