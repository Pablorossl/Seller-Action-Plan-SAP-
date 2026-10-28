# Fuentes y alcance de la auditoría académica

Consulta: **28/10/2026**. Versión del producto revisada: `49ee19800e35ae72602e6cc7f76e1e6c374ae0d6`. Los cambios de Fase 4 son documentación y evidencia de QA; no cambian reglas de negocio.

## Guía obligatoria

[FS Proyecto Final - Máster en Desarrollo Full Stack](https://docs.google.com/document/d/1KhmvNgC4g9WI8suPOBjGFcUCQeA8rVPkoVS53fYLOkQ/edit). Leída íntegramente mediante el conector de Google Drive; modificación indicada por Drive: 08/10/2026, 17:36 UTC. No se redistribuye una copia de la guía de la academia en el repositorio público.

La guía establece seis contenidos: problema; aportación y eficiencia; tecnologías justificadas; usuarios; casos de uso con flujo, resultado y errores; seguridad. Exige Django con modelos, vistas, plantillas, autenticación y persistencia, y una o dos vistas React con datos del backend. Los cuatro entregables son GitHub, aplicación pública estable, memoria PDF/Word con capturas, diagramas y ejemplos, y vídeo accesible de hasta cinco minutos. No exige dominio propio, Docker, extensión ni número concreto de páginas de memoria.

En requisitos mínimos dice repositorio público; en procedimiento admite público o compartido con el equipo docente. SAP se ha comprobado público, satisfaciendo ambas formulaciones. La defensa dura como máximo veinte minutos y sirve para comprobar comprensión y autoría. La rúbrica es 30/15/15/15/15/10 y el aprobado, 7/10; no se estima ni promete una nota.

Primero deben estar aprobadas las actividades de Prework, Frontend y Backend y existir confirmación docente. La guía no acredita el expediente del autor. La carpeta accesible «ConquerBlocks» no devolvió archivos al consultarla; no se localizó evidencia administrativa en el repositorio ni en esa consulta de Drive. **Pendiente de confirmación de Pablo y del equipo docente.** No se ha revisado un expediente ni se han enviado comunicaciones.

Tras la entrega, el equipo revisa código y documentos; si se supera la revisión inicial, facilita Calendly para reservar defensa. La guía prevé comunicación de nota y feedback hasta diez días hábiles después, ajustes menores cuando proceda y una defensa por trimestre académico. En una reentrega exige mejoras que respondan al feedback.

## Fuentes funcionales

- [Criterios automatizados](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/20561228339357-criterios-de-calidad-automatizados): límites MQC, periodo y volumen. Contrastados con `backend/quality/rules.py`; no modificados.
- [Preparación de planes](https://marketplacehelp.pccomponentes.com/hc/es-es/articles/38119386983965-como-mejorar-tus-indicadores-de-calidad-y-preparar-un-plan-de-accion): contexto del diagnóstico, acciones y seguimiento. No es una especificación de SAP ni certifica el proyecto.
- Código, migraciones y pruebas de `backend/`, `frontend/` y `scripts/`; informes históricos `fase-1.md`, `fase-2.md`, `fase-3.md`, `auditoria.md`, `verificacion.md` y `revision-entrega.md`. Las afirmaciones de esos informes describen su fecha y no sustituyen la matriz actual.

## Fuentes operativas

- [Precios Render](https://render.com/pricing), [planes de cómputo](https://render.com/docs/compute-plans), [Blueprint](https://render.com/docs/blueprint-spec), [deploys](https://render.com/docs/deploys), [límites gratuitos](https://render.com/docs/free), [recuperación PostgreSQL](https://render.com/docs/postgresql-backups).
- [Repositorio público](https://github.com/Pablorossl/Seller-Action-Plan-SAP-) y [CI de Fase 3](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/40747706230), comprobados por API pública sin autenticación. La consulta web inicial falló; la API confirmó `private=false` y `conclusion=success` para `49ee198`. No acredita CI de cambios de Fase 4 todavía locales.

Los precios web se consultaron el 28/10/2026. El extractor de la página dinámica no mostró las tablas al abrirla directamente; los resultados indexados del dominio oficial sí las devolvieron. Por ello la cifra presupuestada es orientativa y requiere confirmación en el panel antes de contratar.
