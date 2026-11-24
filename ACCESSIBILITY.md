# Accesibilidad de Seller Action Plan

Auditoría del 24 de noviembre de 2026. El estándar de referencia es WCAG 2.2 nivel AA. Esta auditoría cubre el contraste pendiente y la exposición semántica de los recorridos de evaluación. [Recomendación WCAG 2.2 del W3C](https://www.w3.org/TR/WCAG22/)

## Contraste

El criterio 1.4.3 exige 4,5:1 para texto normal y 3:1 para texto grande. El criterio 1.4.11 exige 3:1 para la información visual necesaria para reconocer controles, estados o gráficos frente a los colores adyacentes. El icono decorativo de un campo ya identificado por su etiqueta se distingue de un icono que realiza una acción. [Contraste mínimo](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) · [Contraste no textual](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)

Se extrajeron los colores computados de Chromium, se compusieron las transparencias sobre sus fondos y se calculó `(L mayor + 0,05) / (L menor + 0,05)` con luminancia relativa sRGB. Los umbrales se comparan antes del redondeo. Los dos casos indeterminados de Axe en el recorrido anterior correspondían a texto parcialmente oculto por el área desplazable del diálogo de finalización. El muestreo ampliado reprodujo esos casos y añadió una etiqueta sobre fondo solapado y un aviso parcialmente oculto. Los cuatro textos distintos superaron sus umbrales. La evidencia registra el selector exacto, la causa indicada por Axe y las mediciones del estado renderizado.

| Elemento | Primer plano / fondo | Ratio | Mínimo |
| --- | --- | ---: | ---: |
| Recuento de acciones del diálogo de finalización | `#1c302d` / `#ffffff` | 13,91 | 4,5 |
| Nota explicativa del diálogo de finalización | `#526447` / `#f7f9f4` | 6,05 | 4,5 |
| Etiqueta «Fecha límite» en el diálogo de acción a 768 px | `#425847` / `#ffffff` | 7,72 | 4,5 |
| Texto del aviso de cambios sin guardar a 375 px | `#1c302d` / `#ffffff` | 13,91 | 4,5 |
| Botón principal, texto e icono | `#ffffff` / `#146952` | 6,62 | 4,5 / 3 |
| Icono funcional sobre blanco | `#668074` / `#ffffff` | 4,28 | 3 |
| Confirmación de éxito | `#4b6b3f` / `#ebf5e6` | 5,39 | 4,5 |
| Mensaje de error | `#99432c` / `#fff1eb` | 5,96 | 4,5 |
| Estado Cerrado o Cancelado | `#445861` / `#edf1f4` | 6,57 | 4,5 |
| Placeholder de búsqueda | `#53665c` / `#ffffff` | 6,14 | 4,5 |
| Anillo de foco sobre el fondo de página | `#277fbc` / `#f5f7f6` | 4,03 | 3 |

## Semántica y anuncios

- El árbol de accesibilidad de Chromium expone el contenido principal, los nombres de las navegaciones, el salto al contenido y los encabezados de las rutas y los diálogos.
- Las tablas de planes, vendedores e indicadores conservan sus encabezados de columna y tienen nombres accesibles propios. Sus regiones desplazables están etiquetadas y describen el desplazamiento por teclado cuando corresponde. La comparación de indicadores del recorrido se presenta como tabla con valores y resultados textuales.
- Los filtros y formularios exponen etiquetas y nombres, y los errores de validación conservan las asociaciones de campo y el foco del resumen. La paginación enfoca el texto de página al sustituir sus controles, siempre que el usuario no haya movido el foco durante la petición.
- La confirmación del plan actualiza una región `status` que permanece montada y presenta el estado alcanzado. La guía conserva la región viva entre sus pasos y mantiene su animación.
- El clic o toque conserva el foco real con el contorno oculto. La navegación por teclado muestra el indicador y mantiene el foco lógico en diálogos, rutas y transiciones.

## Resultados de la ejecución

| Verificación | Resultado |
| --- | --- |
| Frontend | 39 pruebas aprobadas y compilación de producción correcta. |
| Django con PostgreSQL temporal | 119 pruebas aprobadas. |
| Chromium | 14 casos de teclado y foco, 20 de cambios sin guardar y 127 estados responsive en seis tamaños. |
| Axe en el recorrido de accesibilidad | 10 estados, sin infracciones detectadas. Dos textos indeterminados verificados por cálculo en la tabla de contraste. |
| Muestreo suplementario | 58 estados y 54 escaneos Axe sin infracciones detectadas. Todos los valores muestreados de texto, iconos, placeholders y bordes superaron sus umbrales. |
| Inspección semántica | Revisión del DOM y de las instantáneas de accesibilidad exportadas por Playwright. Escucha de anuncios pendiente. |

Las comprobaciones responsive cubrieron el reflujo equivalente a 200 % y 400 % mediante tamaños CSS. El zoom nativo no cambió el viewport CSS en Chromium headless. Las tablas de comparación de las dos fixtures sin indicadores tienen encabezados y una explicación visual de que faltan datos. Axe solicitó revisar la asociación de celdas en esas tablas vacías. Su lectura se incluye en la revisión manual.

## Cómo repetir las comprobaciones

En un entorno local con Node 22, las dependencias Python del proyecto, Playwright con Chromium, PostgreSQL y un archivo local de axe-core, ejecutar:

```sh
npm test
npm run build
SAP_AXE_PATH=/ruta/a/axe.min.js python3 scripts/verify_accessibility.py --artifacts /tmp/sap-a11y
```

La suite usa datos ficticios en PostgreSQL temporal y ejecuta las pruebas Django, el recorrido de teclado, los cambios sin guardar, el recorrido responsive y el flujo funcional. En `browser/keyboard/` quedan los resultados Axe con sus nodos indeterminados, las instantáneas `.aria.txt` y las mediciones de los estados con contraste indeterminado. Para ampliar el muestreo de colores y estados, usar `scripts/verify_contrast.py` con la misma configuración. En el muestreo ampliado, `browser/contrast/axe.json` incluye los nodos y los ratios medidos. En casos nuevos de texto parcialmente oculto, desplazar el contenedor hasta mostrarlo completo y comprobar colores durante hover, foco o selección cuando correspondan.

## Protocolo manual con lector de pantalla

Esta ejecución utilizó el árbol de accesibilidad de Chromium y pruebas de teclado. La sesión automatizada no tenía acceso a un escritorio interactivo con salida de audio. Narrador existe en el sistema anfitrión Windows, pero no se pudo verificar su salida desde Chromium headless en Linux. La escucha de anuncios y su orden requieren una sesión humana con NVDA y Firefox o Chrome, VoiceOver y Safari, u Orca y Firefox en un escritorio habilitado.

| Recorrido | Resultado que debe confirmar la persona evaluadora |
| --- | --- |
| Acceso, Dashboard y menú móvil | La lista de landmarks distingue contenido principal y navegaciones. La lista de encabezados identifica la vista. «Saltar al contenido» cierra el menú y lleva al contenido. |
| Vendedores y Planes de mejora | Los filtros anuncian nombre, estado y valor. La navegación por tablas lee el nombre, los encabezados y su asociación con las celdas. La página nueva se anuncia al pulsar «Siguiente» sin abandonar el listado. |
| Crear o editar un plan | Se oyen etiquetas, ayuda y campos obligatorios. Al enviar datos inválidos se oye el resumen y, al volver al campo, su error asociado. Comprobar si el resumen se repite. |
| Añadir acción, aviso de cambios y finalización | El lector identifica el diálogo por título y lee su descripción cuando existe. Tab permanece dentro, Escape respeta las reglas del diálogo y se recupera el foco al cerrarlo. |
| Activar, pasar a revisión y continuar | Probar con Espacio y Enter. Comprobar el anuncio del estado alcanzado, su orden respecto al título enfocado y que se oye una sola confirmación por cambio. |
| Guía e indicadores | Al avanzar en la guía comprobar el anuncio del paso, título y descripción. Confirmar que la comparación tabular permite conocer indicador, valor inicial, objetivo, último valor y resultado. En un cierre histórico sin indicadores, comprobar cómo se presenta la tabla vacía y el mensaje explicativo. |

Registrar lector, versión, navegador, sistema, acción, foco, anuncio exacto y resultado. La inspección del árbol y Axe aportan evidencia sobre los casos ejercitados. La confirmación auditiva sigue pendiente.
