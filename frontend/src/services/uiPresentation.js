// Presentation only: the server's validation text and pagination remain authoritative.
const fieldLabels = Object.freeze({
  title: "Título del plan", seller: "Vendedor", problem: "Problema identificado",
  root_cause: "Causa raíz", evidence: "Evidencia del diagnóstico", objective: "Objetivo de mejora",
  responsible: "Responsable", period_start: "Inicio del periodo", period_end: "Fin del periodo",
  due_date: "Fecha objetivo del plan", next_review_on: "Próxima revisión", status: "Estado",
  metrics: "Indicadores y objetivos", baseline: "Observación inicial", target_value: "Valor objetivo",
  plan_metric: "Indicador a revisar", value: "Valor observado", order_count: "Pedidos del periodo",
  reviewed_on: "Fecha de revisión", assessment: "Valoración del agente", comments: "Evolución y evidencias",
  next_steps: "Próximos pasos", correction_reason: "Motivo de rectificación", supersedes: "Revisión original",
  description: "Descripción de la acción", kind: "Tipo de acción", completed_on: "Fecha de finalización",
  notes: "Notas y razones", confirm: "Confirmación", revision: "Versión del registro",
});

export function messages(errors, overrides = {}) {
  if (errors == null) return "";
  if (typeof errors !== "object") return String(errors);
  if (Array.isArray(errors)) return errors.map(error => messages(error, overrides)).filter(Boolean).join(" ");
  return Object.entries(errors).map(([key, value]) => {
    const text = key === "metrics" && Array.isArray(value)
      ? value.map((item, index) => {
          const detail = messages(item, overrides);
          return detail && typeof item === "object" ? `Indicador ${index + 1}: ${detail}` : detail;
        }).filter(Boolean).join(" ")
      : messages(value, overrides);
    if (!text || ["detail", "non_field_errors"].includes(key)) return text;
    const label = /^\d+$/.test(key) ? `Indicador ${Number(key) + 1}`
      : Object.hasOwn(overrides, key) ? overrides[key]
      : Object.hasOwn(fieldLabels, key) ? fieldLabels[key]
      : key.replaceAll("_", " ");
    return `${label}: ${text}`;
  }).filter(Boolean).join(" ");
}

export function paginationRange(data, page, pageSize) {
  const count = data.count;
  const length = data.results.length;
  return {
    first: length ? (page - 1) * pageSize + 1 : 0,
    last: length ? Math.min(count, (page - 1) * pageSize + length) : 0,
    pages: Math.ceil(count / pageSize),
  };
}
