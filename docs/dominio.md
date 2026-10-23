# Dominio y reglas de calidad

Referencia funcional: fuentes públicas de PcComponentes enlazadas en el README, consultadas de nuevo el 23/10/2026, y requisitos facilitados en el encargo. Las reglas son una instantánea documentada; no se actualizan desde la web automáticamente.

## MQC

| Código SAP | Indicador | Alarma | Umbral informativo de suspensión |
| --- | --- | --- | --- |
| `acceptance` | Aceptación de pedidos | <99 % | <98 % |
| `incidents` | Incidencias abiertas / pedidos | ≥4 % | ≥5 % |
| `tracking` | Pedidos con seguimiento válido | <91 % | <90 % |
| `acceptance_hours` | Tiempo de aceptación | ≥20 h | ≥24 h |
| `response_hours` | Tiempo de respuesta | ≥20 h | ≥24 h |

Las reglas se consideran por canal y con los datos del último mes, con al menos 30 pedidos en ese periodo. Por debajo de ese volumen se devuelve `insufficient_orders`, aunque el valor esté fuera de límites. Exactamente 30 pedidos sí permite evaluar. La clasificación comprueba primero el umbral más grave.

Por ejemplo: aceptación de 98 % implica alarma; 97,99 % alcanza el umbral informativo de suspensión. Incidencias de 5 % alcanzan ese umbral. Las incidencias abiertas se consideran independientemente de su antigüedad; seguimiento mide números válidos, no solo números presentes.

SAP clasifica el registro del periodo indicado, sin agregar pedidos ni certificar los valores manuales. Desde la Fase 1, MQC comprueba que el periodo corresponde a un mes natural o a una ventana móvil de un mes con extremos incluidos: inicio hasta el día anterior a la misma fecha del mes siguiente, ajustada al último día cuando procede. La fuente no define ese algoritmo; es una convención de SAP para la captura manual. Un periodo distinto, un valor ausente o un volumen desconocido se considera `not_evaluable`. El panel conserva las fechas: clasificar un registro histórico no representa el estado actual del vendedor. La procedencia y la correspondencia exacta con Mirakl deberán contrastarse antes de automatizar una captura.

## Indicadores independientes

NPS tiene referencia mínima de 65 % y entrega de 90 %. Un valor inferior se clasifica `below_reference`; no genera una clasificación de suspensión ni queda sujeto al mínimo MQC de pedidos. NPS puede variar entre −100 y 100; SAP registra el valor, sin inventar encuestas ni denominadores. No calcula NPS sobre datos inexistentes.

## Mantenimiento

`quality/rules.py` centraliza las reglas compartidas y los valores de referencia para crear políticas. `seed_demo` crea la política v1 de cada indicador y observaciones ficticias. Para cambiar umbrales, el superusuario crea una política nueva con el mismo código y una versión superior, y la selecciona para las observaciones futuras. Las utilizadas conservan sus valores y no se editan. La asignación a nuevas observaciones es manual: no existe activación por fecha ni selección automática de la versión más reciente.

La evaluación es una ayuda operativa. SAP no envía notificaciones oficiales, no modifica estados de tienda, no bloquea pagos y no tramita reaperturas. No existe cliente API, clave ni integración Mirakl.

## Planes y evaluación implementados

La Fase 1 conserva problema, causa raíz, evidencia, responsables y plazos. Cada objetivo numérico pertenece a un indicador inicial y canal, y puede tener varias revisiones históricas. Las incidencias y los tiempos mejoran al disminuir; aceptación, seguimiento, NPS y entrega mejoran al aumentar. Alcanzar el objetivo admite igualdad; demostrar mejora frente al inicio requiere una variación estricta.

Completar acciones no equivale a cumplir objetivos. Sin una revisión evaluable se muestra resultado no evaluable. Las revisiones MQC también requieren mes y volumen suficiente para concluir mejora o logro; las revisiones de NPS/entrega conservan sus reglas independientes. La valoración del agente se guarda aparte del cálculo. Un plan puede cerrarse sin alcanzar el objetivo, o sin datos suficientes, si se documentan las razones y se conserva la evaluación del momento. Más detalles y recorrido: [Fase 1](fase-1.md).
