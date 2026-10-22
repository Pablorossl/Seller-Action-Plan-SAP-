# Dominio y reglas de calidad

Referencia funcional: fuentes públicas de PcComponentes enlazadas en el README, consultadas el 22/10/2026, y requisitos facilitados en el encargo. Las reglas son una instantánea documentada; no se actualizan desde la web automáticamente.

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

Esta base registra el periodo y el número de pedidos junto a cada observación, y clasifica únicamente ese registro. No calcula automáticamente la ventana móvil del último mes, no agrega pedidos por canal y no comprueba la veracidad de los valores cargados por el administrador. El panel muestra fechas para evitar presentar un histórico como evaluación actual. La fase de captura deberá definir formalmente la ventana mensual, zona horaria, cierres y procedencia antes de automatizarla; no se debe mezclar meses ni canales.

## Indicadores independientes

NPS tiene referencia mínima de 65 % y entrega de 90 %. Un valor inferior se clasifica `below_reference`; no genera una clasificación de suspensión ni queda sujeto al mínimo MQC de pedidos. NPS puede variar entre −100 y 100; SAP registra el valor, sin inventar encuestas ni denominadores. No calcula NPS sobre datos inexistentes.

## Mantenimiento

`seed_demo` crea la política v1 de cada indicador y observaciones ficticias. Para cambiar umbrales, el superusuario crea una política nueva con el mismo código y una versión superior, y la selecciona para las observaciones futuras. Las utilizadas conservan sus valores y no se editan. La asignación a nuevas observaciones es manual: no existe activación por fecha ni selección automática de la versión más reciente.

La evaluación es una ayuda operativa. SAP no envía notificaciones oficiales, no modifica estados de tienda, no bloquea pagos y no tramita reaperturas. No existe cliente API, clave ni integración Mirakl.

## Planes previstos

Un plan deberá explicar problema, causa raíz, acciones correctivas/preventivas, responsable, plazo, evidencia y medida de éxito. La revisión deberá comparar resultados con una observación posterior y registrar conclusiones, no limitarse a marcar tareas como terminadas. Esta gestión sigue pendiente y no se considera implementada por disponer del clasificador.
