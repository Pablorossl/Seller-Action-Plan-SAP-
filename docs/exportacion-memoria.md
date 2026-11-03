# Exportación y revisión de la memoria — 03/11/2026

Fuente: [Markdown editable](memoria-pfm.md). Entregables: [Word editable](memoria-pfm.docx) y [PDF de 24 páginas A4](memoria-pfm.pdf). La extensión es una decisión de maquetación, no un requisito de la guía. El PDF incluye portada, índice con veinte enlaces internos, secciones, numeración continua y nueve figuras: cuatro diagramas y cinco capturas públicas. Las imágenes originales se localizan en [el índice visual](evidencias-visuales.md).

## Reproducción local

Se han utilizado los exportadores documentales del proyecto, Playwright/Chromium para PDF y python-docx/lxml/Pillow para Word. No hay una habilidad específica de PDF disponible en el catálogo de esta sesión; las herramientas se ejecutan localmente, sin subir documentos a servicios externos ni añadir dependencias al backend.

En un entorno documental independiente:

```bash
python3 -m venv /tmp/sap-pfm-docs
/tmp/sap-pfm-docs/bin/python -m pip install playwright python-docx lxml Pillow pymupdf
/tmp/sap-pfm-docs/bin/python -m playwright install chromium
python3 scripts/render_pfm_diagrams.py
/tmp/sap-pfm-docs/bin/python scripts/export_pfm.py --docx
```

Para un Chromium ya instalado se admite `--chromium /ruta/al/ejecutable`, o `SAP_CHROMIUM_EXECUTABLE`. El comando real de esta revisión terminó con ambos mensajes:

```text
DOCX editable generado: .../docs/memoria-pfm.docx
PDF generado: .../docs/memoria-pfm.pdf
```

El entorno de QA ya disponía de Chromium; las demás herramientas se aislaron en `/tmp`. El navegador necesitó ejecución autorizada fuera del sandbox. No se instalaron paquetes del sistema ni se modificaron las dependencias del producto.

Los exportadores cubren el subconjunto Markdown de esta memoria; no son conversores generales. Generan HTML e imágenes auxiliares en `docs/_build/`, ignorado por Git. El PDF bloquea cargas HTTP(S) durante la conversión, incorpora imágenes locales y conserva enlaces HTTPS clicables. El DOCX incorpora sus imágenes, convierte SVG localmente y conserva los enlaces externos. No referencia archivos privados ni depende de imágenes remotas.

## Revisión ejecutada

Se renderizaron las **24 páginas** con PyMuPDF y se inspeccionaron visualmente portada, índice, tablas con cabeceras repetidas, diagramas, capturas, márgenes, saltos y pies. No se encontraron textos o tablas cortados ni páginas vacías. Los espacios reservados para figuras completas son intencionados. Las capturas de escritorio pueden ampliarse en sus PNG originales.

La captura móvil completa quedaba demasiado reducida; se sustituyó en la memoria por un encuadre público real de 390 × 844, sin cambios en datos. Se volvió a exportar PDF/Word. La comparación de los rasterizados finales confirmó que **solo cambió la página 23**, revisada visualmente de nuevo; las otras 23 páginas son idénticas a las inspeccionadas. La captura móvil completa permanece en el índice de evidencia.

Se comprobaron veinte destinos internos del índice, seis destinos externos HTTPS únicos y ausencia de enlaces `file:` o destinos internos inválidos. Los destinos externos conservan sus URL correctas; la guía se leyó mediante Drive, y la aplicación y referencias Git/CI se contrastan con las evidencias de la publicación. El acceso docente a materiales que requieran permisos debe confirmarlo el autor al compartirlos; no se afirma haber navegado manualmente cada enlace desde una cuenta del tribunal.

El [registro de integridad](revision-memoria-pdf-2026-11-03.json) guarda huellas, páginas y límites. La inspección visual completa corresponde al **PDF**, que fija la paginación de entrega. Se revisó la estructura y el contenido del DOCX, pero no se dispone de Word/LibreOffice para inspeccionar su repaginación en esos editores. Si se edita allí, exportar de nuevo y repetir la revisión; no mantener un PDF distinto de la fuente.

Vídeo real, comprobación desde segunda red y entrega formal continúan pendientes según la [checklist](checklist-entrega.md). Ni la exportación ni esta revisión provocan push o redespliegue.
