# Evidencias visuales de Fase 4

Origen: ejecución real del 28/10/2026, `artifacts/phase4-evidence/`, código de producto `49ee198` y script de navegador ampliado en Fase 4. Entorno aislado: PostgreSQL 14.24, Gunicorn, DEBUG=False y certificado TLS local de prueba. Chromium escritorio 1440×1060 y móvil emulado 390×844. Las capturas completas pueden superar la altura del viewport. **No son capturas de producción.**

La cuenta `evaluador_qa` y todos los vendedores, acciones y mediciones son ficticios. La contraseña se generó en memoria; el login se capturó antes de introducirla. No se fotografiaron cabeceras de sesión, tokens ni el panel del proveedor. El entorno se eliminó al finalizar.

| Evidencia | Archivo | Qué acredita |
| --- | --- | --- |
| Acceso | [Login](screenshots/fase-4-login.png) | Plantilla Django |
| Panel operativo | [Dashboard](screenshots/fase-4-dashboard.png) | Datos de resumen del backend |
| Directorio | [Vendedores](screenshots/fase-4-vendedores.png) | Listado persistido autorizado |
| Ficha | [Vendedor](screenshots/fase-4-vendedor.png) | Contexto e histórico |
| Métricas | [Indicadores](screenshots/fase-4-indicadores.png) | 6%, canal, periodo, pedidos y política |
| Listado | [Planes](screenshots/fase-4-planes.png) | Plan creado en el recorrido y ejemplos de la semilla |
| Creación | [Formulario](screenshots/fase-4-formulario-plan.png) | Diagnóstico, meta y fechas |
| Borrador | [Detalle](screenshots/fase-4-detalle-plan.png) | Plan guardado antes de las acciones |
| Acción | [Formulario de acción](screenshots/fase-4-accion.png) | Fecha, estado y evidencia |
| Seguimiento completo | [Revisiones](screenshots/fase-4-revisiones.png) | Plan antes del cierre |
| Histórico legible | [Detalle de revisiones](screenshots/fase-4-historial-revisiones.png) | 4,5% y 3% con periodos |
| Resultado medido | [Evaluación](screenshots/fase-4-evaluacion.png) | Inicial, meta y actual |
| Confirmación | [Diálogo de cierre](screenshots/fase-4-confirmacion-cierre.png) | Razones y consentimiento de cierre |
| Plan final | [Cierre completo](screenshots/fase-4-cierre.png) | Estado persistido después de recargar |
| Resultado final | [Sección de cierre](screenshots/fase-4-resultado-cierre.png) | Instantánea y razones |
| Adaptación | [Móvil](screenshots/fase-4-movil.png) | Emulación de 390 px sin desbordamiento global |

Los fragmentos de indicadores, revisiones, evaluación y resultado son capturas directas de elementos DOM, no imágenes reconstruidas. Los PNG completos se conservan para ampliarlos. Los hashes y tamaños están en [evidencias-fase-4.json](evidencias-fase-4.json). El ejemplo [React-Django](ejemplo-react-django.json) guarda datos ficticios seleccionados de la respuesta real de `/api/plans/5/`; ese ID corresponde a QA temporal y no es una URL pública.

## Diagramas

| Diagrama | Fuente y correspondencia |
| --- | --- |
| [Arquitectura](diagramas/arquitectura.svg) | Ajustes, vistas, build/release, DRF, ORM y destino propuesto |
| [Modelo de datos](diagramas/modelo-datos.svg) | Siete modelos de dominio más auth.User; FK reales; grupos/permisos nativos resumidos |
| [Casos de uso](diagramas/casos-uso.svg) | Agente y superusuario; no existe vendedor externo |
| [Flujo de mejora](diagramas/flujo-mejora.svg) | Estados, seguimiento y separación entre cierre y resultado |

Se generan como SVG vectoriales mediante `python3 scripts/render_pfm_diagrams.py`, sin imágenes sintéticas ni servicios externos. Son diagramas explicativos del código, no capturas del producto. El ER resume campos; los modelos y migraciones siguen siendo la especificación completa. La memoria incorpora los cuatro y trece capturas seleccionadas; las dieciséis están disponibles en este índice.

## Reproducción

Compilar React y ejecutar `python3 scripts/verify_phase3.py --pg-bin /usr/lib/postgresql/14/bin --artifacts artifacts/phase4-evidence`. El comando exige herramientas QA disponibles y puede requerir permiso para sockets locales. Revisar imágenes y JSON antes de copiar evidencias a `docs/`; no copiar automáticamente logs, certificados ni bases. Una nueva ejecución cambia IDs, fechas y títulos aleatorios; actualizar el índice y sus hashes conjuntamente.
