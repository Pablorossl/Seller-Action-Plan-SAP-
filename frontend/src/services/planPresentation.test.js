import assert from "node:assert/strict";
import test from "node:test";
import { planResult } from "./planPresentation.js";

test("cerrado no implica cumplido: conserva ambos resultados explícitos", () => {
  for (const result of ["achieved", "not_achieved"])
    assert.equal(planResult({ status: "closed", closure_evaluation: { result } }).code, result);
});
test("la instantánea de cierre prevalece sobre una evaluación actual diferente", () => {
  assert.deepEqual(planResult({ status: "closed", closure_evaluation: { result: "not_achieved" }, evaluation: { result: "achieved" } }), {
    code: "not_achieved", label: "Objetivo no alcanzado", qualifier: "Resultado al cierre",
  });
});
test("un cierre histórico incompleto no se reconstruye desde la evaluación actual", () => {
  for (const closure_evaluation of [undefined, null, {}, { metrics: [{ achieved: true }] }]) {
    const result = planResult({ status: "closed", closure_evaluation, evaluation: { result: "achieved" } });
    assert.equal(result.code, "unavailable");
    assert.equal(result.label, "Sin resultado registrado");
  }
});
test("cancelado utiliza su resultado registrado y no inventa un incumplimiento", () => {
  assert.equal(planResult({ status: "cancelled", closure_evaluation: { result: "achieved" } }).code, "achieved");
  assert.equal(planResult({ status: "cancelled" }).code, "unavailable");
});
test("no evaluable permanece distinto de no alcanzado y de resultado ausente", () => {
  assert.equal(planResult({ status: "closed", closure_evaluation: { result: "not_evaluable" } }).label, "No evaluable");
});
test("un plan abierto presenta solo la evaluación actual suministrada por la API", () => {
  assert.deepEqual(planResult({ status: "in_review", evaluation: { result: "not_achieved" }, closure_evaluation: { result: "achieved" } }), {
    code: "not_achieved", label: "Objetivo no alcanzado", qualifier: "Evaluación actual",
  });
  assert.equal(planResult({ status: "draft" }).code, "unavailable");
});
test("los códigos desconocidos no se interpretan como cumplimiento", () => {
  for (const result of ["future_result", "constructor", "__proto__", true, false, 1, null])
    assert.equal(planResult({ status: "closed", closure_evaluation: { result } }).code, "unavailable");
});
test("presentar los resultados no modifica el plan ni su instantánea", () => {
  const plan = Object.freeze({ status: "closed", closure_evaluation: Object.freeze({ result: "achieved" }) });
  const before = JSON.stringify(plan);
  planResult(plan);
  assert.equal(JSON.stringify(plan), before);
});
