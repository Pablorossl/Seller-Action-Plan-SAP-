# Evidencias visuales — entrega académica de SAP

## Selección final de memoria y ampliación de aceptación

Capturas directas de Chromium contra [SAP público](https://sap-bice.vercel.app), SHA `97b4bff`, tomadas el 03/11/2026. Se seleccionaron para la memoria cinco encuadres; el filtro de vendedores queda como evidencia adicional. No se reconstruyó ni retocó la interfaz. Todos los datos son ficticios.

| Evidencia | Archivo y alcance |
| --- | --- |
| Dashboard actual | [Dashboard](screenshots/entrega-dashboard-publico.png), figura 6 de memoria |
| Filtro de vendedores | [Sin planes abiertos](screenshots/entrega-filtro-vendedores.png), evidencia adicional |
| Historial legible de F01 | [Rectificaciones](screenshots/entrega-historial-rectificaciones.png), captura directa de sección DOM, figura 3 |
| Resultado histórico de F03 | [Cierre](screenshots/entrega-instantanea-cierre.png), sección DOM, figura 4 |
| Paginación real | [Página 2](screenshots/entrega-paginacion-publica.png), figura 7; 51 vendedores temporales del segundo agente, retirados al terminar |
| Móvil legible | [Encuadre 390 × 844](screenshots/entrega-movil-publico.png), figura 9, plan 5, captura de solo lectura; sin desbordamiento horizontal global |

Los [resultados adicionales](evidencias-filtros-paginacion-2026-11-03.json) acreditan filtros, paginación, aislamiento y retirada de los 51 registros creados. La figura de paginación conserva el estado real antes de la limpieza. No se afirma que esos registros permanezcan disponibles. El deployment no cambió; no se repitió una prueba de redespliegue ni se obtuvo acceso a una segunda red.

Las capturas completas se conservan para ampliar detalles. El PDF usa un encuadre móvil, porque reducir toda la página larga a una sola figura hacía ilegible el texto. La vista móvil larga inicial se mantiene más abajo como evidencia complementaria. La [revisión del PDF](revision-memoria-pdf-2026-11-03.json) identifica la exportación final. Ninguna imagen muestra credenciales, tokens, cookies o paneles de proveedores.

## Capturas públicas añadidas el 03/11/2026

Origen: Chromium contra [SAP público](https://sap-bice.vercel.app), candidato `97b4bff`, con datos ficticios y aceptación registrada en [el acta](verificacion-publica.md). Estas imágenes complementan las históricas de QA local:

| Evidencia pública | Archivo |
| --- | --- |
| Dashboard y cartera ficticia | [Dashboard](screenshots/publicacion-dashboard.png) |
| Cadena de revisiones con original, rectificaciones y medición efectiva | [Rectificación](screenshots/publicacion-rectificacion.png) |
| Cierre e indicadores de vencimiento conservados | [Cierre histórico](screenshots/publicacion-cierre-historico.png) |
| Mismo plan después del redespliegue desde Git | [Persistencia](screenshots/publicacion-persistencia.png) |
| Vista móvil pública a 390 px | [Móvil](screenshots/publicacion-movil.png) |

No contienen contraseñas, claves, cookies ni paneles de proveedores. La memoria ya incorpora la selección final y arquitectura Vercel/CDN/Django/Neon con SHA y alcance. El autor debe revisar personalmente el material y grabar su vídeo: la grabación y su enlace siguen pendientes.

## Evidencias históricas de QA local

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
| [Arquitectura](diagramas/arquitectura.svg) | Un origen público, función Django WSGI/CDN en Vercel Hobby y PostgreSQL 18 pooled en Neon Free; no migraciones/semillas en build |
| [Modelo de datos](diagramas/modelo-datos.svg) | Siete modelos de dominio más auth.User; FK reales, vínculo supersedes y campos de rectificación; grupos/permisos nativos resumidos |
| [Casos de uso](diagramas/casos-uso.svg) | Agente y superusuario; no existe vendedor externo |
| [Flujo de mejora](diagramas/flujo-mejora.svg) | Estados, seguimiento y separación entre cierre y resultado |

Se generan como SVG vectoriales mediante `python3 scripts/render_pfm_diagrams.py`, sin imágenes sintéticas ni servicios externos. Son diagramas explicativos del código, no capturas del producto. El ER resume campos; los modelos y migraciones siguen siendo la especificación completa. La memoria final incorpora **cuatro diagramas y cinco capturas públicas**, nueve figuras. Las dieciséis capturas históricas siguen disponibles con su alcance local.

## Reproducción de la evidencia histórica local

Compilar React y ejecutar `python3 scripts/verify_phase3.py --pg-bin /usr/lib/postgresql/14/bin --artifacts artifacts/phase4-evidence`. El comando exige herramientas QA disponibles y puede requerir permiso para sockets locales. Revisar imágenes y JSON antes de copiar evidencias a `docs/`; no copiar automáticamente logs, certificados ni bases. Una nueva ejecución cambia IDs, fechas y títulos aleatorios; actualizar el índice y sus hashes conjuntamente.
