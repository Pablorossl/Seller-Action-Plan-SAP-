# Exportación y revisión de la memoria

Fuente editable: [memoria-pfm.md](memoria-pfm.md). Archivo generado: [memoria-pfm.pdf](memoria-pfm.pdf), **30 páginas A4** en la exportación de Fase 4. La extensión es una decisión de maquetación, no un requisito académico. El PDF tiene portada, índice con enlaces, secciones numeradas, pies con número de página, trece capturas y cuatro diagramas vectoriales.

## Reproducir

Desde la raíz, con un Python que tenga Playwright y Chromium disponibles:

```bash
python3 scripts/render_pfm_diagrams.py
python3 scripts/export_pfm.py
```

El entorno de QA de esta sesión ya dispone de esas herramientas. Para un equipo nuevo puede prepararse un entorno independiente, sin añadir dependencias al backend:

```bash
python3 -m venv /tmp/sap-pfm-docs
/tmp/sap-pfm-docs/bin/python -m pip install playwright
/tmp/sap-pfm-docs/bin/python -m playwright install chromium
/tmp/sap-pfm-docs/bin/python scripts/export_pfm.py
```

Si faltan bibliotecas del sistema para Chromium, seguir las indicaciones de Playwright para el sistema operativo y obtener permiso antes de instalar paquetes del sistema. En Windows utilizar una carpeta temporal y su ejecutable `Scripts/python.exe`; esa variante no se ha probado aquí.

El exportador utiliza un subconjunto explícito de Markdown que cubre este documento; no es un conversor general. Genera `docs/_build/memoria-pfm.html`, ignorado por Git, y el PDF versionable. Carga sólo imágenes locales y bloquea peticiones HTTP(S) de la página durante la conversión. Los enlaces externos permanecen clicables en el PDF. No sube la memoria a Drive ni a otra plataforma.

La primera exportación del entorno restringido falló al arrancar Chromium. Se repitió con autorización para ejecutar el navegador fuera del sandbox y terminó correctamente. La versión inicial tenía saltos excesivos; se ajustó el flujo para evitar una página con una sola línea y se volvió a exportar.

## Revisión del resultado

Comprobar portada, nombre del autor, índice, pie y todos los apartados; abrir enlaces; revisar tablas partidas con cabecera repetida y legibilidad de SVG/capturas. Las capturas originales están enlazadas en [evidencias visuales](evidencias-visuales.md) para ampliarlas. El PDF incorpora explícitamente los pendientes; no debe llamarse versión definitiva de entrega hasta completar la aceptación pública.

Cuando se añadan URL, evidencias remotas o cambios de texto: editar Markdown, regenerar PDF y revisar otra vez. Actualizar el hash del PDF y el número de páginas en el informe si varían. No editar el PDF a mano manteniendo una fuente Markdown distinta.
