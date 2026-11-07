import assert from "node:assert/strict";
import test from "node:test";
import { messages, paginationRange } from "./uiPresentation.js";

test("traduce errores anidados y mantiene el indicador de una lista con entradas vacías", () => {
  const fields = { metrics: [{}, { target_value: ["El objetivo debe mejorar el valor inicial."] }] };
  assert.equal(messages(fields), "Indicadores y objetivos: Indicador 2: Valor objetivo: El objetivo debe mejorar el valor inicial.");
});
test("conserva el índice de errores de indicador serializados como objeto", () => {
  assert.equal(messages({ metrics: { 2: { baseline: ["Periodo diferente."] } } }),
    "Indicadores y objetivos: Indicador 3: Observación inicial: Periodo diferente.");
});
test("errores generales y de campo conservan el texto del servidor sin nombres técnicos", () => {
  assert.equal(messages({ due_date: ["El plazo no puede preceder al periodo de referencia."], detail: "Conflicto de versión.", non_field_errors: ["Revisa el plan."] }),
    "Fecha objetivo del plan: El plazo no puede preceder al periodo de referencia. Conflicto de versión. Revisa el plan.");
});
test("el contexto de acción puede nombrar su fecha límite sin alterar los datos", () => {
  const fields = Object.freeze({ due_date: Object.freeze(["Plazo inválido."]) });
  assert.equal(messages(fields, { due_date: "Fecha límite" }), "Fecha límite: Plazo inválido.");
  assert.equal(messages(fields), "Fecha objetivo del plan: Plazo inválido.");
});
test("no descarta mensajes desconocidos ni utiliza propiedades heredadas como etiquetas", () => {
  assert.equal(messages({ future_field: ["Dato rechazado."], constructor: "Valor inválido." }),
    "future field: Dato rechazado. constructor: Valor inválido.");
  assert.equal(messages(null), "");
  assert.equal(messages(["Primero.", "Segundo."]), "Primero. Segundo.");
});
test("paginación de vendedores: segunda página parcial conserva offset y total", () => {
  assert.deepEqual(paginationRange({ count: 60, results: Array(10) }, 2, 50), { first: 51, last: 60, pages: 2 });
});
test("paginación de planes usa su tamaño 20, también en la última página de un registro", () => {
  assert.deepEqual(paginationRange({ count: 21, results: [1] }, 2, 20), { first: 21, last: 21, pages: 2 });
});
test("un filtro sin resultados no inventa una primera página ni un registro", () => {
  assert.deepEqual(paginationRange({ count: 0, results: [] }, 1, 50), { first: 0, last: 0, pages: 0 });
});
test("rango de primera página y total exacto no añaden una página vacía", () => {
  assert.deepEqual(paginationRange({ count: 20, results: Array(20) }, 1, 20), { first: 1, last: 20, pages: 1 });
});
