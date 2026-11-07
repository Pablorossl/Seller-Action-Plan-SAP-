const results = Object.freeze({
  achieved: "Objetivo alcanzado",
  not_achieved: "Objetivo no alcanzado",
  not_evaluable: "No evaluable",
});

// Present the result supplied by the API. Final plans use only the recorded
// closure snapshot, including when a legacy snapshot has no result.
export function planResult(plan) {
  const final = ["closed", "cancelled"].includes(plan?.status);
  const result = (final ? plan.closure_evaluation : plan?.evaluation)?.result;
  const recorded = Object.hasOwn(results, result);
  return {
    code: recorded ? result : "unavailable",
    label: recorded ? results[result] : "Sin resultado registrado",
    qualifier: final ? "Resultado al cierre" : "Evaluación actual",
  };
}
