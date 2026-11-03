# Entrega académica final preparada — 03/11/2026

SAP está publicada en [https://sap-bice.vercel.app](https://sap-bice.vercel.app). La memoria y el material de preparación están actualizados a la publicación validada. **Faltan el vídeo real y su enlace, la segunda red independiente, la revisión personal y el trámite académico.** No se ha realizado la entrega formal ni la defensa.

## Archivos principales

| Material | Archivo |
| --- | --- |
| Memoria paginada, 24 páginas revisadas visualmente | [PDF](memoria-pfm.pdf) |
| Editable en procesador de textos | [Word DOCX](memoria-pfm.docx) |
| Fuente editable que genera ambas exportaciones | [Markdown](memoria-pfm.md) |
| Vídeo, todavía sin grabar | [Guion previsto de 4:20](guion-video-pfm.md), con 40 s de margen |
| Defensa, todavía sin ensayar | [Guion de hasta 20 min y 26 preguntas](preparacion-defensa.md) |
| Cierre frente a la guía | [Checklist de tres estados](checklist-entrega.md) y [trazabilidad](trazabilidad-requisitos.md) |
| Exportación y revisión | [Procedimiento](exportacion-memoria.md) y [registro con huellas](revision-memoria-pdf-2026-11-03.json) |

El paquete local `artifacts/entrega-academica-sap-2026-11-03.zip` reúne estos materiales y la documentación pública de apoyo, con manifiesto de integridad. No incluye el código completo: la referencia es el repositorio GitHub. Los informes de fases anteriores se conservan como antecedentes, con su fecha y entorno. Abrir primero este índice y la checklist para conocer el estado vigente.

## Versiones sin ambigüedad

- Código desplegado: **`97b4bff55a07b8fd3c71b05740748db5bf63438b`**, [CI aprobada](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/41722300443).
- Deployment público: **`dpl_DVtuHFEv9eTba7V8ShdLASR9BBTi`**, alias `sap-bice.vercel.app`.
- Documentación pública posterior de partida: **`575c6c942318885d6b7427ccedabc1eea7cc5887`**, distinta del código servido.
- Esta preparación académica son **cambios locales posteriores**, sin commit nuevo, push ni redespliegue. No se atribuye a esos cambios una CI remota que no se ha ejecutado.

Se releyó la guía original mediante Drive, sin copiarla al repositorio. La referencia `docs/sap-publicacion-2026-11-03` coincide con la rama Git actual; no hay una carpeta con ese nombre en este checkout. Se utilizaron el acta, los JSON y las capturas públicas en `docs/`. `sources/` tampoco existe aquí y no se ha creado ni modificado.

## Pruebas completadas en esta preparación

El [JSON de filtros/paginación](evidencias-filtros-paginacion-2026-11-03.json) registra ocho comprobaciones correctas: filtros de vendedores y planes contrastados con API, páginas reales de 50 + 1 vendedores sin duplicados, navegación/límites, reinicio de página al filtrar/buscar, rechazo de páginas inválidas, aislamiento y limpieza. Se crearon y retiraron exactamente **51 vendedores ficticios** del segundo agente; se preservaron los datos previos. El deployment y SHA no cambiaron. No se generaron planes adicionales para afirmar una navegación de dos páginas de planes.

La exportación terminó con `DOCX editable generado` y `PDF generado`. La revisión de artefactos terminó con:

```json
{
  "pdf_pages": 24,
  "visual_review_all_pages": true,
  "valid_internal_links": 20,
  "external_https_targets": 6,
  "docx_images": 9,
  "all_source_blocks_in_docx": true,
  "known_private_matches": 0,
  "passed": true
}
```

Se revisaron visualmente tablas, imágenes, márgenes, saltos, numeración y enlaces del PDF. La captura móvil completa se sustituyó en la memoria por un encuadre real legible; solo cambió la página 23, inspeccionada de nuevo. Las otras 23 páginas conservaron el rasterizado ya revisado. El Word incorpora todos los bloques de la fuente y nueve imágenes; su paginación en Word/LibreOffice no se ha inspeccionado, porque no se dispone de esos editores. El PDF fija la paginación revisada.

Los tres scripts documentales compilan con `py_compile`, y `git diff --check` no presenta incidencias. No se repite la suite funcional del producto por cambios documentales: la memoria cita la CI exacta y la aceptación pública anteriores con sus límites. Las verificaciones de persistencia y recuperación no se volvieron a ejecutar; se describen a partir de sus evidencias reales: mismo SHA redesplegado y copia restaurada en PostgreSQL 18 aislado, 21 tablas coincidentes.

La revisión del árbol de trabajo y el índice no detectó secretos conocidos ni `.env` privados seguidos. Se contrastaron también el texto extraído del PDF y las partes XML del DOCX con valores privados locales, DSN y patrones de claves privadas, sin coincidencias. Es una comprobación acotada, complementada por la inspección visual de capturas. El paquete excluye credenciales, sesiones, copias de base, directorios privados, `_build/`, `.git/` y la guía original.

## Archivos modificados o añadidos

- Entrada de proyecto: [README](../README.md).
- Memoria y exportaciones: [Markdown](memoria-pfm.md), [PDF](memoria-pfm.pdf), [DOCX](memoria-pfm.docx), [exportación](exportacion-memoria.md), [registro de revisión](revision-memoria-pdf-2026-11-03.json).
- Preparación académica: este índice, [checklist](checklist-entrega.md), [matriz](trazabilidad-requisitos.md), [fuentes](fuentes-pfm.md), [guion de vídeo](guion-video-pfm.md) y [defensa](preparacion-defensa.md).
- Arquitectura y evidencia: [arquitectura](arquitectura.md), [acta](verificacion-publica.md), [índice visual](evidencias-visuales.md), [resultados de filtros](evidencias-filtros-paginacion-2026-11-03.json); SVG de [arquitectura](diagramas/arquitectura.svg), [datos](diagramas/modelo-datos.svg) y [flujo](diagramas/flujo-mejora.svg).
- Seis PNG nuevos: [dashboard](screenshots/entrega-dashboard-publico.png), [filtro](screenshots/entrega-filtro-vendedores.png), [historial](screenshots/entrega-historial-rectificaciones.png), [cierre](screenshots/entrega-instantanea-cierre.png), [paginación](screenshots/entrega-paginacion-publica.png) y [móvil](screenshots/entrega-movil-publico.png).
- Herramientas documentales: [exportador PDF](../scripts/export_pfm.py), [nuevo exportador DOCX](../scripts/export_docx.py) y [generador SVG](../scripts/render_pfm_diagrams.py).

Backend, frontend, migraciones, dependencias y configuración de servicios no se han modificado. No se ha contratado ningún servicio, activado una prueba de pago ni añadido métodos de pago. Se mantienen Vercel Hobby y Neon Free; la ausencia de TTL en la rama predeterminada no garantiza disponibilidad ilimitada ni elimina cuotas.

## Intervención que aún necesita el autor

1. Revisar y comprender memoria/código; ensayar la defensa y contrastar los justificantes académicos y confirmación docente. No se acredita el expediente por una declaración previa.
2. Probar desde una red realmente independiente y registrar el resultado. Otra sesión o navegador del mismo equipo no equivale a otra red.
3. Preparar un plan ficticio distinto de los controles 5/6, grabar el vídeo, medir ≤300 s, revisar contenido/secretos y comprobar su enlace accesible.
4. Compartir memoria y vídeo con los permisos correctos; enviar los cuatro elementos por el procedimiento docente. Entregar credenciales solo mediante canal privado.
5. Mantener aplicación y cuotas durante la evaluación, atender la revisión inicial y reservar defensa cuando lo indique el equipo académico. No se han realizado estos pasos personales.

No hay métricas empresariales de ahorro o productividad ni un estudio de usuarios que puedan defenderse como resultados medidos. La memoria presenta esos beneficios como esperados y delimita la evidencia técnica disponible.
