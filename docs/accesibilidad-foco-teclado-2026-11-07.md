# Accesibilidad — foco y navegación por teclado

Fecha: 07/11/2026. Base: `1cdaa24`, árbol limpio al comenzar. Cambios locales, sin commits, push ni despliegues.

## Referencias y alcance

Antes de modificar el producto se revisaron los informes de [fase 1](ux-fase-1-navegacion-segura-2026-11-07.md) y [fase 2](ux-fase-2-responsive-2026-11-07.md). Está disponible la [auditoría UX/UI del 7 de noviembre](/tmp/sap-ux-audit-20261107/AUDITORIA-UX-UI-SAP.md); se consultaron sus hallazgos UX05, UX20, UX21 y evidencias de teclado, formularios y diálogos. Se verificó el estado actual: los defectos ya corregidos en fases anteriores no se presentan como nuevos.

Se inspeccionaron navegación, dashboard, vendedores/ficha, planes/detalle, edición/creación, indicadores, acciones, revisiones/rectificación, evaluación y cierre; componentes compartidos, guard de cambios y router hash. La reproducción previa usa una base SQLite nueva en `/tmp`, solo con agentes y datos ficticios, incluidos registros adicionales para ejercitar la paginación. La validación final usa PostgreSQL temporal con TLS local, sin conectar a producción.

## Problemas reproducidos y causas

[Registro previo](../artifacts/ux-keyboard/before/keyboard/result.json), con capturas asociadas:

| Problema reproducido | Causa | Resultado implementado |
| --- | --- | --- |
| Al navegar a Vendedores, el foco continuaba en el enlace lateral; otros cambios acababan en `BODY` | El router cambiaba el contenido sin trasladar el foco al destino | Tras una ruta aceptada se espera el contenido asíncrono y se enfoca su H1 una sola vez. No se roba foco al filtrar o refrescar datos. |
| Abrir una prioridad no enfocaba la acción; el foco quedaba en `BODY` | El parámetro `action` solo añadía resaltado visual | La acción se identifica mediante su título, recibe foco programático y se desplaza al encuadre. |
| Acciones vencidas desplazaba la página dejando el control enfocado fuera del encuadre | Enlace sin `href` con comportamiento de botón implementado a mano | Botón HTML nativo, activación con Enter/Espacio y foco en el encabezado de prioridades. |
| Paginación terminaba en `BODY` | La carga desmontaba el botón y toda la paginación | Al volver los datos se enfoca “Página N”; si el usuario se ha movido a otro control durante la espera, se respeta su foco. |
| Limpiar búsqueda terminaba en `BODY` | El botón enfocado desaparecía al vaciar el texto | El foco vuelve al campo de búsqueda. |
| Tab/Shift+Tab alcanzaban `BODY` en límites del diálogo en Chromium | El comportamiento nativo observado permitía abandonar el foco del documento hacia el navegador | Se conserva `<dialog>` y se añade únicamente el retorno en sus extremos, respetando la tabulación nativa dentro de los campos. |
| Durante una petición retenida, al deshabilitar el envío el foco salía a `BODY` | El control enfocado quedaba deshabilitado | Mientras se guarda, se recupera el foco en el título del diálogo; Tab permanece dentro y Escape no abandona una escritura pendiente. |
| Cerrar/finalizar podía eliminar el abridor y dejar el foco sin destino útil | La restauración solo contemplaba un abridor todavía conectado | Se restaura al abridor visible/habilitado o al encabezado/contenido si desaparece, respetando un foco lógico establecido por el padre. Las transiciones de estado enfocan el título cuando desaparece su botón. |
| “Saltar al contenido” no funcionaba con el menú abierto | Intentaba enfocar `main` mientras seguía inerte | Cierra el menú y enfoca el contenido después de retirar la inercia. |
| El botón de navegación mantenía “Mostrar” estando abierto | Nombre accesible fijo | Expone Mostrar/Ocultar según el estado; conserva `aria-expanded`, Escape y restauración del foco. |
| Historial/Activos solo comunicaba selección con estilo | Faltaba un estado accesible | Grupo de botones nativos con `aria-pressed`, activables con Tab, Enter y Espacio. No se introduce un patrón ARIA de tabs que requiera otro teclado. |
| El selector de responsable tenía un `label` sin control asociado | El selector compuesto no es un único input | Grupo nativo `fieldset`/`legend` para vendedor y responsable, conservando botones de selección y su estado. |
| El motivo de rectificación no recibía la asociación del error de campo | Textarea independiente del componente `Field` | Reutiliza `Field`: etiqueta, obligatoriedad, estado inválido y descripción del error. |

Además se mantiene un anillo visible para destinos programáticos y se dibuja el anillo de la tabla dentro de su región, evitando el recorte por el panel. Se deja margen al desplazamiento del foco para la cabecera compacta. La fase actual del plan se expone con `aria-current="step"`; el índice estático del formulario no se presenta como un asistente interactivo.

## Solución de foco, diálogos, menús y formularios

`useRouteFocus` espera al destino mediante observación del contenido y se desconecta después de enfocar. Solo actúa en navegación aceptada o una entrada contextual con acción. La carga inicial normal conserva el recorrido nativo desde el enlace de salto. Ni filtros, recargas parciales ni decisiones de continuar editando activan una nueva navegación de foco.

La paginación comparte una intención de foco dentro de `Resource`, sin alterar la estructura responsive. La búsqueda mantiene una referencia a su input. No se emplean índices positivos de tabulación ni ordenaciones visuales del foco.

Los diálogos siguen siendo HTML nativo. El foco inicial identifica su título; el aviso de cambios sin guardar conserva la opción segura **Continuar editando** y añade su mensaje como descripción accesible. Tab y Shift+Tab recorren los controles habilitados y vuelven al extremo correspondiente. Los campos de fecha conservan sus segmentos y flechas nativos. El estado de guardado mantiene los controles deshabilitados y el foco dentro del diálogo. Escape conserva el guard de datos y el bloqueo durante peticiones.

El menú mantiene enlaces de navegación y comportamiento de apertura/cierre, sin convertirlo en un menú ARIA de aplicación. El enlace de salto puede utilizarse también estando abierto. La etiqueta del botón refleja su estado.

`Field` mantiene simultáneamente las instrucciones y el error, cada uno con su ID en `aria-describedby`; el error no sustituye la ayuda. El resumen sigue siendo un `alert` enfocado, y los datos permanecen en los controles al fallar la validación. La rectificación y los selectores compuestos se integran en esa semántica sin cambiar payloads ni reglas.

## Archivos modificados

| Archivo | Cambio |
| --- | --- |
| `frontend/src/components/RouteFocus.jsx` (nuevo) | Gestión de foco una vez por navegación y destino contextual asíncrono. |
| `frontend/src/main.jsx` | Integra el foco, corrige el salto con menú abierto y el nombre del botón compacto. |
| `frontend/src/components/ui.jsx` | Foco de paginación/búsqueda, ayuda y error asociados, límites de Tab, foco inicial/ocupado/restauración de diálogos. |
| `frontend/src/components/UnsavedChanges.jsx` | Descripción accesible del aviso; decisiones y detección de cambios intactas. |
| `frontend/src/pages/Workspace.jsx` | Botón nativo de vencidas, destino de prioridades y estados del historial. |
| `frontend/src/pages/PlanDetail.jsx` | Destinos de acciones, transición de estado, fase actual y campo de rectificación. |
| `frontend/src/pages/PlanForm.jsx` | Grupos nativos de selección; evita competir con el foco de ruta al crear. Conserva la entrada de foco de edición local. |
| `frontend/src/styles.css` | Anillo de foco y margen de desplazamiento; alineación del nuevo botón de estadísticas equivalente a los enlaces. |
| `scripts/verify_accessibility.py` (nuevo) | Recorrido de teclado, aserciones de foco/semántica/errores, axe opcional y ejecución de las regresiones existentes. |
| Este informe | Diagnóstico, decisiones, resultados y límites. |

No se modifican Django/DRF, modelos, migraciones, API, autenticación, CSRF, permisos, revisión, idempotencia, evaluación, cierre ni persistencia. El router hash y la lógica de cambios pendientes se conservan. No se añaden dependencias al producto ni se realiza rediseño general.

## Pruebas automatizadas y resultados

Comandos desde la raíz, con Node 22 y las dependencias de QA disponibles:

```sh
# Herramienta opcional de auditoría, instalada fuera del producto:
npm install --prefix /tmp/sap-accessibility-tools --no-audit --no-fund axe-core@4.14.0
npm test
npm run build
python3 scripts/verify_accessibility.py --artifacts artifacts/ux-keyboard/final
```

`SAP_AXE_PATH` permite indicar otro archivo `axe.min.js`. Si no existe, el verificador registra que axe no se ha ejecutado. En esta validación sí estaba disponible. El verificador crea PostgreSQL y TLS temporales, agentes ficticios y registros para paginación; ejecuta las suites y elimina el clúster al terminar. La repetición del script local de release comprueba migraciones/estáticos dentro de QA; no publica ni despliega.

| Verificación final | Resultado | Evidencia |
| --- | --- | --- |
| JavaScript | **18/18**, sin fallos | [Log](../artifacts/ux-keyboard/js-tests.log) |
| Build Vite | **Correcto**, 36 módulos | [Log](../artifacts/ux-keyboard/build.log) |
| Teclado y foco | **12 grupos superados**, incluidas fechas nativas, guardado pendiente y cierre cuyo abridor desaparece; cero errores de página | [Resultado y foco observado](../artifacts/ux-keyboard/final/browser/keyboard/result.json) |
| Fase 1 | **20/20 grupos**, sin regresiones detectadas | [Resultado](../artifacts/ux-keyboard/final/browser/navigation/result.json) |
| Responsive | **128 estados**, sin ensanchamiento accidental ni recorte horizontal en los paneles comprobados; diálogos utilizables | [Resultado](../artifacts/ux-keyboard/final/browser/responsive/result.json), [mediciones](../artifacts/ux-keyboard/final/browser/responsive/measurements.json) |
| Django/PostgreSQL | **116/116**, sin omisiones, PostgreSQL temporal 14.24 | [Log](../artifacts/ux-keyboard/final/postgres-tests.log) |
| Full Stack | Creación, edición, acciones, revisión, evaluación, cierre, recarga, CSRF, aislamiento y logout: **correctos** | [Resultado](../artifacts/ux-keyboard/final/browser/browser-result.json) |
| Persistencia/recuperación | Reinicios PostgreSQL/Gunicorn y backup/restauración en otra base temporal: **correctos** | [Resultado integrado](../artifacts/ux-keyboard/final/result.json) |
| Diferencias | `git diff --check`: **correcto** | Revisión local |

Los grupos de navegador contienen múltiples aserciones; no se suman a los 116 tests Django como si fueran tests unitarios independientes.

La prueba de guardado pendiente retiene una petición real, comprueba controles deshabilitados, Tab y Escape, y después transmite la petición a Django. No sustituye la respuesta de negocio por datos simulados. Las pruebas de validación llegan al backend y comprueban valores, foco del resumen, `aria-invalid` y relaciones con ayuda/error. El caso de valor observado inválido conserva simultáneamente la instrucción y el error.

### Recorridos dirigidos con teclado

Se enviaron exclusivamente **Tab, Shift+Tab, Enter, Espacio, Escape, flechas y entrada de texto** mediante Playwright en estos recorridos. No se usan clics, `fill()` ni `focus()` del test para alcanzar controles; las lecturas DOM y comprobaciones de roles verifican el resultado. No fue una sesión de un operador humano con teclado físico.

1. Login → vendedores → página 2 → buscar/limpiar → ficha → historial/activos.
2. Dashboard → acciones vencidas → encabezado de prioridades → acción seleccionada.
3. Revisión → ciclos de Tab/Shift+Tab → Escape → abridor original.
4. Rectificación → texto pendiente → aviso anidado → continuar/descartar.
5. Edición → cancelar limpio → regresar a Editar plan.
6. Crear desde un indicador → completar campos/fecha → objetivo inválido → error asociado → corregir y guardar.
7. Editar → volver con cambios → continuar → guardar → mismo ID y foco restaurado.
8. Acción → guardar con petición pendiente → Tab/Escape contenidos → activar plan y recuperar foco tras retirar el control.
9. Revisión con valor inválido → ayuda/error/valores conservados → corregir → evaluación → rectificación con motivo inválido.
10. Finalizar → motivo → checkbox con Espacio → confirmar → encabezado cuando desaparece Finalizar plan.
11. Móvil → abrir menú → enlace de salto → abrir/cerrar con Escape → navegar → tabla desplazable con flechas → enlace de última columna.
12. Tablet → abrir con Espacio → cerrar con Escape → botón de apertura enfocado.

Las capturas se revisaron visualmente para comprobar encuadre, foco y controles, además de las aserciones.

### axe-core y herramientas reales

- **Chromium 151.0.7922.34 headless**, Playwright y revisión visual de capturas.
- **axe-core 4.14.0**, diez estados: dashboard, ficha, rectificación, aviso, edición, creación, error de creación, finalización, cierre y ficha móvil. Se ejecutaron las etiquetas WCAG 2.0/2.1 A/AA. [Resultados completos](../artifacts/ux-keyboard/final/browser/keyboard/axe.json).
- En esas muestras, la única regla con infracciones fue **`color-contrast`**: 109 apariciones de nodos entre capturas, con repeticiones del mismo componente. No son 109 problemas distintos. No se detectaron infracciones automáticas de nombres, etiquetas o ARIA en las muestras; el aviso de cambios pendientes no presentó infracciones en ese análisis.
- No se encontró un **lector de pantalla utilizable** en el entorno Linux/headless. No se ha realizado ni se atribuye una prueba con NVDA, VoiceOver, Orca u otro lector.

Los resultados automáticos no sustituyen el recorrido por teclado ni certifican conformidad WCAG. Las advertencias de contraste siguen pendientes para una fase específica de contraste/sistema visual; no se han ocultado ni desactivado en el análisis.

## Regresiones de navegación segura y responsive

Se repiten Volver al plan/ID, cancelación limpia, comparación real de cambios, continuar/descartar, guardado, errores 400/503 con valores conservados, revisiones e idempotencia, doble envío, X/Cancelar/Escape, Atrás/Adelante y el aviso nativo real al rechazar una recarga. El menú conserva la prioridad de los diálogos abiertos al manejar Escape. Se comprueban por separado el aviso anidado, el cierre del menú y la conservación de valores al navegar desde él.

Los tamaños responsive repetidos son **320 × 568, 375 × 812, 430 × 932, 768 × 1024, 1024 × 768 y 1440 × 900**. El recorrido dedicado solo con teclado usa 1440 × 900, 375 × 812 y 768 × 1024. La suite responsive adicional combina teclado y ratón para comprobar todas las columnas y acciones.

Se repite reflow en 720 × 450 y 360 × 225, equivalente al espacio CSS del 200/400 % desde escritorio. El zoom nativo no cambió el viewport en Chromium headless y **no se declara validado**.

## Evidencias

- [Diagnóstico previo de foco](../artifacts/ux-keyboard/before/keyboard/result.json).
- Navegación: [antes](../artifacts/ux-keyboard/before/keyboard/route-sellers.png) / [después](../artifacts/ux-keyboard/final/browser/keyboard/route-sellers.png).
- Paginación: [antes](../artifacts/ux-keyboard/before/keyboard/pagination.png) / [después](../artifacts/ux-keyboard/final/browser/keyboard/pagination.png).
- Prioridad: [antes](../artifacts/ux-keyboard/before/keyboard/priority-target.png) / [después](../artifacts/ux-keyboard/final/browser/keyboard/priority-target.png).
- [Diálogo abierto](../artifacts/ux-keyboard/final/browser/keyboard/review-open.png), [guardado pendiente](../artifacts/ux-keyboard/final/browser/keyboard/action-busy.png), [foco alternativo tras cierre](../artifacts/ux-keyboard/final/browser/keyboard/closed-fallback.png), [tabla móvil con anillo interior](../artifacts/ux-keyboard/final/browser/keyboard/mobile-table-focus.png), [error de validación](../artifacts/ux-keyboard/final/browser/keyboard/creation-validation.png).

Los artefactos están ignorados por Git y disponibles localmente. La auditoría original permanece en `/tmp`; no se confunden estas capturas ficticias con evidencia de producción.

## Límites y riesgos pendientes

No se detectan regresiones funcionales pendientes en los recorridos ejecutados. La prueba con petición retenida descubrió y permitió corregir la salida de foco durante el guardado. Se ajustó además el momento de capturar la paginación para registrar el foco estabilizado después de la carga; los intentos fallidos intermedios no se presentan como verificaciones superadas.

No se han comprobado lectores de pantalla, Firefox/Safari, dispositivos físicos, teclado virtual, tecnologías de voz o zoom nativo con interfaz. La captura del estado y el nombre accesible no equivale a verificar cómo lo anuncia cada lector. Las infracciones de contraste siguen abiertas, y tampoco se declara cumplimiento integral de WCAG 2.2 AA.

La validación es local con datos ficticios y PostgreSQL 14.24: no certifica producción, otra versión de PostgreSQL, disponibilidad pública ni todos los perfiles de permisos. Los permisos, CSRF, aislamiento y reglas siguen cubiertos por la suite y el recorrido indicados. No se han regenerado memoria/vídeo ni se certifica la evaluación académica.

## Veredicto

**LISTO PARA LA SIGUIENTE FASE**, en el alcance de foco y teclado. Las acciones principales pueden recorrerse con teclas, el foco tiene destinos predecibles y visibles, los diálogos permiten continuar y salir de forma segura, y las fases 1 y 2 pasan sus regresiones. Permanecen explícitamente pendientes el contraste y la validación con lectores de pantalla y otros entornos; este veredicto no es una certificación global de accesibilidad.
