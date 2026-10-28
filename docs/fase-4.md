# Fase 4 — Auditoría y preparación de entrega

Fecha: **28/10/2026**. Autor confirmado: **Pablo Rosales**. Código base: `49ee19800e35ae72602e6cc7f76e1e6c374ae0d6`. **La fase no está completamente finalizada: faltan aplicación pública verificada, vídeo real y acreditación de requisitos administrativos.**

## Auditoría previa a cambios

Se revisaron README, informes de Fases 1–3, auditoría/verificación inicial, revisión de entrega, arquitectura, dominio, requisitos, esquema de memoria, roadmap, scripts, modelos, servicios, permisos, API, frontend, migraciones y configuración. No se encontró `AGENTS.md` aplicable. No se delegó a subagentes.

El árbol inicial estaba limpio, `main` coincidía con la referencia local `origin/main` y existían cinco commits significativos. No se reescribe ese historial. La guía oficial se localizó por el enlace documentado y se leyó íntegramente en Drive antes de redactar; véase [fuentes](fuentes-pfm.md).

| Área al iniciar Fase 4 | Estado inicial | Acción realizada |
| --- | --- | --- |
| Producto y tests | Implementado, pendiente de revalidación | QA completa PostgreSQL/Chromium repetida |
| URL pública | Pendiente | Receta auditada y acta preparada; sin provisión |
| GitHub/CI | No verificable sólo con las referencias locales | API pública confirma repositorio público y CI exitosa |
| Memoria PDF/Word | Pendiente; sólo esquema | Memoria completa y PDF generados |
| Evidencias visuales | Capturas históricas parciales | 16 capturas actuales y cuatro diagramas |
| Vídeo | Pendiente | Guion 4:50 e instrucciones; sigue sin grabar |
| Defensa | Pendiente | Exposición y 25 preguntas basadas en código |
| Administración académica | No verificable con la información disponible | Consulta de fuentes sin acreditación personal; pendiente |

## A. Estado de SAP

Backend Django, plantillas y sesiones, API y React operativo, persistencia local, ciclo de planes, permisos, validación, transacciones, edición obsoleta e idempotencia comprobados. Se conserva el alcance, sin añadir funcionalidades, métricas, umbrales ni migraciones. Los cambios de código se limitan a QA y utilidades documentales.

## B. Despliegue

**URL pública: no disponible ni verificada.** No hay conexión operativa a Render en esta sesión; no se contrató ni activó infraestructura externa. `render.yaml` se conserva: web Python `0.5c-512mb`, PostgreSQL 16 `0.1c-256mb`, 1 GB, Frankfurt, despliegues automáticos desactivados y base sin acceso externo abierto.

Se contrastaron los campos con documentación vigente. Presupuesto base orientativo: web 7 + PostgreSQL 6 = **13 USD/mes**, workspace Hobby sin cuota adicional; extras, impuestos y recuperación deben confirmarse en el panel antes de autorizar. [Precios oficiales](https://render.com/pricing). Condiciones, límites Free, retención y comandos precisos están en [despliegue](despliegue.md). No se declara validado un Blueprint por el proveedor ni medido su rendimiento real.

El [acta pública](verificacion-publica.md) contiene las 18 comprobaciones, todas pendientes en remoto. Incluye explícitamente redeploy y recuperación, que no cubre el recorrido de navegador por sí solo.

## C. Memoria

[Fuente Markdown](memoria-pfm.md) y [PDF de revisión](memoria-pfm.pdf), 30 páginas. Incluye portada confirmada, resumen, quince capítulos solicitados, nueve casos de uso, matriz de permisos, seguridad y límites, desarrollo, pruebas, demo, conclusiones y anexos. Trece capturas y cuatro SVG incluidos. [Procedimiento reproducible de exportación](exportacion-memoria.md).

El contenido diferencia beneficio esperado y resultado medido. No afirma integración Mirakl, condición de aplicación oficial, impacto empresarial ni producción existente. La memoria está materializada, pero deberá actualizarse con la evidencia remota antes de la entrega final.

## D. Evidencias y resultados

| Verificación Fase 4 | Entorno | Resultado |
| --- | --- | --- |
| `pip check` | venv del producto | Sin incompatibilidades |
| `npm test` | Node 22.19.0 | Correcto; runner agrupa el archivo |
| `node --test --experimental-test-isolation=none --test-reporter=spec src/services/api.test.js` | Node 22.19.0 | Siete casos aprobados |
| `npm run build` | Frontend | Correcto, Vite 7.3.7 |
| `scripts/check_production.py` | Variables ficticias | Correcto; no prueba conectividad |
| `scripts/verify_phase3.py --pg-bin /usr/lib/postgresql/14/bin --artifacts artifacts/phase4-evidence` | PostgreSQL 14.24, TLS local, Gunicorn | Exit 0; 77/77 pruebas Django, incluidas ocho de concurrencia |
| Migraciones y release | QA temporal | Base vacía, sin deriva, migraciones aplicadas y release repetido |
| Chromium | Escritorio y móvil emulado | Flujo 6 → 4,5 → 3, cierre, recarga, CSRF, agente ajeno y logout correctos |
| Salud SQL | QA | 200 con DB, 503 al detenerla |
| Persistencia | QA | Huellas coincidentes tras reiniciar PostgreSQL/Gunicorn y repetir release |
| Backup/restauración | QA | `pg_dump`, restauración separada y comparación correctos |
| CI GitHub | SHA `49ee198` | [Success](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/40747706230) |
| Aceptación de producción | Internet/proveedor | No ejecutada |

[Resumen JSON con hashes](evidencias-fase-4.json), [índice visual](evidencias-visuales.md) y [ejemplo real de JSON ficticio](ejemplo-react-django.json). Logs completos locales en `artifacts/phase4-evidence/`, ignorados por Git. No se incluyen dumps, secretos ni certificados.

Validación documental final: 135 enlaces locales sin destinos rotos, hashes de las 16 capturas coincidentes, 18 destinos del índice PDF resueltos, 13 imágenes incrustadas y cuatro SVG vectoriales. Se revisó una vista conjunta de las 30 páginas y ampliaciones de portada, índice, arquitectura, ER, permisos, casos de uso y pantallas principales. No se detectó texto fuera de los límites de página. `git diff --check` y compilación sintáctica de los tres scripts modificados/añadidos correctos. Hash del PDF y de su Markdown en el JSON de evidencia.

La QA se ejecutó primero sin cambios; después al añadir capturas/logout y, finalmente, al corregir la espera de carga de dos capturas. La revisión visual evitó incorporar un listado todavía cargando. Las tres ejecuciones terminaron correctamente; sólo la última se usa como evidencia visual final. No hubo un fallo funcional del producto. La exportación PDF necesitó permiso para arrancar Chromium fuera del sandbox; el fallo inicial y la corrección de maquetación se documentan.

Las auditorías de paquetes sin vulnerabilidades conocidas son evidencia histórica de Fase 3 del mismo día, no una nueva consulta de Fase 4. Tampoco se ejecutó una prueba de carga pública ni se certificó accesibilidad. La suite local de Fase 4 se ejecutó en PostgreSQL; SQLite está cubierto por la CI comprobada, no por una nueva ejecución local declarada aquí.

## E. Vídeo

[Guion de 4:50](guion-video-pfm.md), con narración, pantalla, acción, tiempos, textos ficticios e instrucciones de grabación y acceso. **Grabación y enlace pendientes.** La captura automática de QA no es un vídeo explicativo y no sustituye la narración del autor.

## F. Defensa

[Material preparado](preparacion-defensa.md): 11 minutos de exposición y 9 de preguntas; 25 preguntas probables, respuestas concretas y archivos para enseñarlas. Incluye ensayo de comprensión, contingencia local y límites del producto. No se afirma que Pablo haya ensayado ni que la defensa esté agendada.

## G. GitHub

La consulta de API pública confirma `private=false`. El run de Fase 3 y los de Fases 1–2 finalizaron con éxito. El fallo inicial de la herramienta web no se interpretó como repositorio privado; se verificó por API con acceso de red autorizado. La consulta no cambió GitHub.

README actualizado con instalación, configuración, migraciones, uso, pruebas, acceso local, estado de demo pública y enlaces académicos. `.env.example`, dependencias fijadas, migraciones históricas y licencia MIT se conservan. Se revisaron 166 blobs del historial con patrones de claves privadas, tokens comunes, asignaciones de secreto y URLs de base; los candidatos eran placeholders, pruebas y contraseña efímera de CI. No se detectaron secretos reales conocidos. Es una revisión acotada, no una certificación exhaustiva. Ningún `.env`, dump, SQLite, clave privada ni caché está versionado.

Los commits anteriores permanecen intactos. Los cambios de Fase 4 están locales, sin commit ni push. Se proponen tres commits en el [checklist](checklist-entrega.md). No se envían correos ni materiales. Los informes de fases anteriores conservan sus estados históricos; la matriz de Fase 4 es la referencia actual.

## H. Matriz de cumplimiento

[Tabla completa contra ConquerBlocks](trazabilidad-requisitos.md): requisito, evidencia, estado, ubicación y acción pendiente, con separación de exigencias oficiales y controles adicionales de Fase 4. Incluye los seis criterios ponderados de la rúbrica y las limitaciones de cada evidencia. No asigna ni garantiza nota.

## I. Pendientes que impiden finalizar

1. Autorizar recursos/coste y desplegar SAP; aportar URL real y mantenerla durante revisión/defensa.
2. Ejecutar y registrar aceptación pública, persistencia tras redeploy y recuperación remota autorizada.
3. Revisar personalmente la memoria, incorporar resultados remotos y generar su versión definitiva.
4. Grabar vídeo real ≤5 minutos, publicarlo con autorización y comprobar acceso al enlace.
5. Confirmar Prework, Frontend y Backend aprobados y autorización docente; no se obtuvo evidencia personal.
6. Guardar/publicar Fase 4 mediante commits y push autorizados; comprobar CI del SHA final y permisos de los materiales.
7. Ensayar comprensión y defensa; entregar los cuatro elementos y agendar sólo según revisión docente.

Detalle y registro de enlaces: [checklist de entrega](checklist-entrega.md). El PDF y los materiales preparados permiten avanzar, pero **no justifican declarar el proyecto listo para entregar**.
