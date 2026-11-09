import assert from "node:assert/strict";
import test from "node:test";
import { resolveRoute, routeBreadcrumbs } from "./routes.js";

const crumbs = (location, resource) => routeBreadcrumbs(resolveRoute(location), resource);

test("la jerarquía cubre todas las vistas y mantiene sus URLs públicas", () => {
  for (const [location, key, labels, hrefs] of [
    ["/", "dashboard", ["Dashboard"], ["#/"]],
    ["/sellers", "sellers", ["Dashboard", "Vendedores"], ["#/", "#/sellers"]],
    ["/plans?status=open&seller=4", "plans", ["Dashboard", "Planes de mejora"], ["#/", "#/plans"]],
    ["/plans/new?seller=4&metric=8", "plan-new", ["Dashboard", "Planes de mejora", "Crear plan de mejora"], ["#/", "#/plans", "#/plans/new"]],
  ]) {
    assert.equal(resolveRoute(location).key, key);
    assert.deepEqual(crumbs(location).map(item => item.label), labels);
    assert.deepEqual(crumbs(location).map(item => item.href), hrefs);
  }
  assert.equal(resolveRoute("/plans/new?seller=4&metric=8").params.get("metric"), "8");
});

test("los detalles usan los nombres de la misma respuesta que la página", () => {
  const seller = resolveRoute("/sellers/12");
  assert.equal(seller.resourceUrl, "/api/sellers/12/");
  assert.deepEqual(routeBreadcrumbs(seller, { data: { name: "Tienda Álamo" } }), [
    { label: "Dashboard", href: "#/" },
    { label: "Vendedores", href: "#/sellers" },
    { label: "Tienda Álamo", href: "#/sellers/12" },
  ]);
  const plan = resolveRoute("/plans/43?action=9");
  assert.equal(plan.resourceUrl, "/api/plans/43/");
  assert.equal(plan.params.get("action"), "9");
  assert.equal(routeBreadcrumbs(plan, { data: { title: "Mejorar entregas" } }).at(-1).label, "Mejorar entregas");
  assert.equal(routeBreadcrumbs(plan, { data: { title: "Título actualizado" } }).at(-1).label, "Título actualizado");
});

test("carga y errores nunca muestran IDs ni nombres inventados", () => {
  assert.equal(crumbs("/sellers/12", { loading: true }).at(-1).label, "Cargando vendedor…");
  assert.equal(crumbs("/plans/43", { loading: true }).at(-1).label, "Cargando plan…");
  for (const status of [0, 403, 404, 500]) {
    assert.equal(crumbs("/sellers/12", { error: { status } }).at(-1).label, "Vendedor no disponible");
    assert.equal(crumbs("/plans/43", { error: { status } }).at(-1).label, "Plan no disponible");
  }
});

test("las rutas inexistentes no heredan una sección por coincidencia parcial", () => {
  for (const path of ["/sellers/abc", "/sellers/1/edit", "/plans/3/missing", "/plans-archive", "/missing"]) {
    assert.equal(resolveRoute(path).key, "not-found");
    assert.equal(resolveRoute(path).section, null);
    assert.equal(resolveRoute(path).resourceUrl, null);
    assert.deepEqual(crumbs(path).map(item => item.label), ["Dashboard", "Página no encontrada"]);
  }
});
