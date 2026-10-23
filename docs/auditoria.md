# Auditoría inicial — 22/10/2026

## Estado observado antes de instalar dependencias del proyecto

- Repositorio: `Seller-Action-Plan-SAP-`; remoto `git@github.com:Pablorossl/Seller-Action-Plan-SAP-.git`.
- Git limpio. Único commit: `048450c Initial commit`.
- Archivos versionados: `README.md` (introducción de dos líneas), `.gitignore` (plantilla amplia de Python) y `LICENSE` (MIT, Pablo Rosales, 2026).
- Sin `package.json`, lockfile, `requirements.txt`, `pyproject.toml`, Django, React, modelos, migraciones, pruebas ni despliegue.
- No había dependencias redundantes o incompatibles que retirar, ni arquitectura previa que sustituir.
- No se encontraron archivos sensibles versionados entre esos tres archivos. Los directorios de contexto `.agents`, `.codex` y `.aws` no se consultaron como fuentes de credenciales y se añadieron al ignore.
- Sin `AGENTS.md` aplicable encontrado en el repositorio o sus directorios ascendentes comprobados.

## Herramientas observadas

| Herramienta | Versión/contexto |
| --- | --- |
| Python | 3.12.4, instalación Miniconda existente |
| pip inicial | 24.2 global; 24.0 en el venv creado |
| Node inicial | 20.20.2 |
| npm inicial | 10.8.2 |
| Node adicional encontrado | 22.19.0, utilizado después para verificar sin cambiar el default global |
| uv | No encontrado; no necesario |

El CLI Codex instalado en el turno anterior no es una dependencia de SAP y no se incorpora al proyecto.

## Decisiones y correcciones controladas

Conservar licencia y ampliar el ignore existente. Crear Django 5.2 LTS, DRF y sesiones nativas en un venv local; React y Vite mediante npm, sin otro gestor ni capas adicionales. SQLite local; exigir PostgreSQL persistente en producción. Comenzar por vendedores, indicadores y políticas y aplazar los modelos de planes al desarrollo siguiente.

Los intentos iniciales de acceso a PyPI/npm desde el entorno restringido fallaron; se solicitaron permisos de red y se completaron las instalaciones. npm 10 sufrió un fallo interno `edgesOut` al resolver Vite 8 con dependencias opcionales; se eligió Vite 7.3.7, rama mantenida, con plugin React 5.2.0 y se comprobó el lockfile con `npm ci`.

No se eliminaron archivos previos, no se modificó la licencia y no se hicieron commits, pushes ni publicaciones. La base deja pendientes el flujo de planes, el despliegue real, los entregables finales y la confirmación administrativa del PFM. Véanse la matriz de requisitos y el informe de verificación.
