# Matriz de trazabilidad y cumplimiento académico — entrega final preparada

Actualizada: **03/11/2026**. [Guía original releída mediante Drive](fuentes-pfm.md). Esta matriz registra evidencias y límites; no otorga una nota. Código desplegado: **`97b4bff55a07b8fd3c71b05740748db5bf63438b`**. Documentación pública posterior de partida: **`575c6c9`**. Esta memoria, sus exportaciones y las pruebas adicionales son cambios locales posteriores, sin push ni redespliegue.

Estados usados: **Completado y comprobado** (entorno explícito); **Preparado, pendiente de ejecución**; **Pendiente de intervención del autor**. Las evidencias históricas conservan sus fechas y no se convierten en pruebas nuevas.

## Contenidos y mínimos de la guía

| Requisito explícito | Evidencia de SAP | Estado / límite |
| --- | --- | --- |
| Problema: contexto, carencia, impacto y solución | Memoria §§1–2 y resumen; seguimiento posterior a desviaciones de vendedores | Completado y comprobado documentalmente; contexto profesional sin investigación empresarial atribuida |
| Aportación y reflexión sobre eficiencia | Memoria §3 y conclusiones: trazabilidad y capacidades verificadas frente a beneficios esperados | Completado y comprobado; sin métricas de ahorro, encuestas ni resultados empresariales inventados |
| Tecnologías justificadas | Memoria §4 y §§7–8: Django, React, PostgreSQL, librerías, sesión y arquitectura | Completado y comprobado contra código/configuración; Render se identifica como antecedente |
| Tipos de usuarios y acciones | Memoria §5; rol, permiso específico y cartera por propietario | Completado y comprobado; vendedor externo no es usuario |
| Casos de uso por actores, flujo, resultado y errores | Memoria §6, ocho casos; recorrido §11 | Completado y comprobado documentalmente; administración con evidencia de código/QA, no cuenta privilegiada pública |
| Seguridad: autenticación, validación, CSRF/XSS, hashing, secretos, HTTPS, copias | Memoria §§9–10 y 14; acta R01/R02/R11/R12/R18 | Completado y comprobado en los entornos descritos; no auditoría exhaustiva de penetración |
| Django: modelos, vistas y plantillas | `backend/sellers`, `quality`, `action_plans`, `config/views.py`, `templates/` | Completado y comprobado por código, CI y recorrido público |
| Autenticación y persistencia | Login/logout reales; datos y sesión tras redespliegue; recuperación aislada | Completado y comprobado; acta R02/R15/R18 |
| Una o dos vistas React integradas con backend real | Dashboard, vendedores y planes con Fetch/API Django; memoria §7 y figuras 6–7 | Completado y comprobado públicamente; no mocks |
| Aplicación funcional en URL pública | [SAP](https://sap-bice.vercel.app), alias y deployment aceptados | Completado y comprobado; continuidad futura requiere supervisión |
| Repositorio público/compartido con README e historial progresivo | [GitHub](https://github.com/Pablorossl/Seller-Action-Plan-SAP-); memoria §11 y README | Completado y comprobado para la versión pública; documentación actual local pendiente de publicación autorizada |
| Organización y configuración reproducibles | Apps separadas, dependencias fijadas, migraciones, build y documentación de despliegue | Completado y comprobado; Docker y dominio propio opcionales |
| Memoria PDF o Word clara y completa | [PDF](memoria-pfm.pdf), [Word](memoria-pfm.docx), [fuente](memoria-pfm.md), 24 páginas PDF revisadas | Completado y comprobado; Word puede repaginarse según editor |
| Capturas, diagramas y ejemplos | Nueve figuras en memoria, ejemplo JSON del plan público 5, [índice visual](evidencias-visuales.md) | Completado y comprobado; imágenes públicas separadas de QA local |
| Vídeo ≤5 min: problema, demo, tecnologías e integración React | [Guion de 4:20](guion-video-pfm.md) con 40 s de margen | Preparado, pendiente de ejecución: no hay archivo real ni duración medida |
| Enlace accesible del vídeo | Comprobación de permisos y reproducción prevista | Pendiente de intervención del autor: grabar, alojar y verificar URL |
| Cuatro elementos de entrega | GitHub y app públicos; memoria local preparada; vídeo pendiente | Pendiente de intervención del autor: cuatro enlaces y envío formal |
| Aplicación disponible durante revisión y defensa | Hobby/Free, rama Neon predeterminada sin TTL | Preparado, pendiente de ejecución continuada; no garantía futura |
| Prework, Frontend y Backend aprobados; confirmación docente previa | Declaración previa recogida en auditoría del 02/11; sin expediente inspeccionado | Pendiente de intervención del autor: contrastar justificantes y confirmación |
| Defensa de máximo veinte minutos; comprensión/autoría | [Guion](preparacion-defensa.md): 10:30 exposición, 7:30 preguntas, 2:00 margen; 26 preguntas con rutas de código | Preparado, pendiente de ensayo y defensa personal; comprensión no se acredita por documentos |
| Revisión inicial, convocatoria y feedback | Checklist con revisión docente → Calendly → defensa; hasta diez días hábiles para feedback | Pendiente de intervención del autor/equipo docente; una defensa por trimestre y mejoras ante reentrega |

## Verificaciones adicionales de la entrega

| Comprobación | Evidencia real y alcance | Estado |
| --- | --- | --- |
| SHA y CI exactos | [CI 41722300443](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/41722300443), success de `97b4bff`; `575c6c9` es documental | Completado y comprobado en la publicación |
| Flujo central | Plan 5: 6 % → 4,5 % → 3 %, dos acciones, evaluación y cierre alcanzado | Completado y comprobado públicamente |
| F01: rectificación sin destrucción | Plan 6, revisiones 7 → 8 → 9, motivo/autor/fecha, efectiva 4 %, rechazo de bifurcación | Completado y comprobado públicamente; casos adicionales en CI/QA |
| F02: fechas observadas | Rechazo público de revisiones/periodos futuros; observaciones globales heredadas, Admin y límites de hoy en código/QA | Completado y comprobado con cobertura delimitada; sin introducir datos futuros inválidos en Production |
| F03: cierre histórico | Instantánea pública antes/después del redeploy; reloj +90 días solo sobre restauración aislada | Completado y comprobado; no avance del reloj público |
| Aislamiento y CSRF | Lectura/cierre ajenos 404; anónimo 403; escritura sin token/origen ajeno 403 | Completado y comprobado; cuenta autenticada sin rol cubierta por CI |
| Filtros públicos | Vendedores con/sin planes abiertos; planes abiertos/cerrados; UI contrastada con API | Completado y comprobado en [JSON adicional](evidencias-filtros-paginacion-2026-11-03.json) |
| Paginación pública | 51 vendedores ficticios, páginas 50 + 1, límites, ausencia de duplicados, reset al filtrar/buscar; limpieza de esos 51 | Completado y comprobado; no se afirma dos páginas de planes |
| Estáticos, salud y móvil | R14/R16/R17; Chromium emulado 390 px y encuadre móvil público final | Completado y comprobado; no dispositivo físico |
| Segunda red independiente | No disponible en este equipo; navegador/sesión adicional no equivale | Pendiente de intervención del autor |
| Persistencia tras redeploy | Mismo SHA, JSON íntegro y sesión conservados entre dos deployments, sin nueva demo | Completado y comprobado en publicación; no se ha repetido un despliegue en esta tarea |
| Recuperación | pg_dump/restore 18.6; PostgreSQL 18 aislado, 21 tablas/digests/esquema y 33 migraciones coincidentes | Completado y comprobado; copia privada fuera de entregables, sin restaurar Production |
| Coste y duración de rama | Hobby y Free activos al terminar publicación; rama `production` predeterminada sin TTL | Completado y comprobado puntualmente; cuotas/continuidad por supervisar |
| PDF y enlaces | 24 páginas revisadas visualmente; índice 20 enlaces válidos, seis destinos externos HTTPS | Completado y comprobado en [registro](revision-memoria-pdf-2026-11-03.json); acceso final docente a materiales privados pendiente |
| Ausencia de secretos en entregables | Revisión acotada de valores privados conocidos, DSN, claves privadas y contenido extraído de PDF/DOCX; paquete explícito | Completado y comprobado en el alcance indicado; no garantía universal de detección |
| Conservación del producto y fuentes | Ningún cambio en backend/frontend/configuración de servicio; `sources/` ausente y no tocado | Completado y comprobado; sin push, redespliegue, migraciones ni semillas |

## Rúbrica oficial y límites de interpretación

| Criterio | Peso | Material para defenderlo |
| --- | ---: | --- |
| Backend Django | 30 % | Modelos, servicios, plantillas, API, CI del candidato y acta pública |
| Integración React | 15 % | Lecturas/escrituras públicas con Fetch; vídeo preparado todavía sin grabar |
| Arquitectura y buenas prácticas | 15 % | Monolito modular, Git/CI, despliegue real y diagramas actualizados |
| Seguridad e integridad | 15 % | Permisos, CSRF, historial, cierre, persistencia y recuperación aislada |
| Documentación y presentación | 15 % | Memoria PDF/Word, capturas, guiones; falta ejecución personal del vídeo/defensa |
| Reflexión y valor aportado | 10 % | Problema, beneficios esperados, evidencia técnica y límites explícitos |

La nota mínima indicada es **7/10**; no se calcula una nota con el número de pruebas. Las cifras históricas de 77/110/112 tests corresponden a ejecuciones y herencias distintas, no se suman ni equivalen a casos independientes. Véanse los informes fechados de F01, concurrencia/F02 y F03. Las pruebas de esta preparación amplían filtros/paginación; no vuelven a ejecutar ni atribuir como nuevas las verificaciones históricas.

La [checklist final](checklist-entrega.md) concentra los pasos restantes. La memoria y su exportación están preparadas; el vídeo real, la segunda red, la entrega formal y la defensa siguen pendientes.
