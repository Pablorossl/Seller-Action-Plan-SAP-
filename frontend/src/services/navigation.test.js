import assert from "node:assert/strict";
import test from "node:test";
import { formSnapshot, installHashNavigation } from "./navigation.js";

function browser() {
  const win = new EventTarget();
  win.document = new EventTarget();
  const entries = [{ url: "https://sap.invalid/dashboard/#/plans", state: null }];
  let position = 0;
  win.location = { get href() { return entries[position].url; }, get hash() { return new URL(this.href).hash; } };
  win.history = {
    get state() { return entries[position].state; },
    replaceState(state, _, url) { entries[position] = { state, url: url || win.location.href }; },
    pushState(state, _, url) { entries.splice(position + 1); entries.push({ state, url }); position++; },
    go(delta) {
      assert.ok(position + delta >= 0 && position + delta < entries.length);
      position += delta;
      queueMicrotask(() => win.dispatchEvent(new Event("hashchange")));
    },
  };
  win.click = (hash) => {
    const link = { href: `https://sap.invalid/dashboard/${hash}`, target: "", hasAttribute: () => false };
    const event = new Event("click", { cancelable: true });
    Object.defineProperties(event, { button: { value: 0 }, target: { value: { closest: () => link } } });
    win.document.dispatchEvent(event);
  };
  win.hash = (hash) => {
    win.history.pushState(null, "", `https://sap.invalid/dashboard/${hash}`);
    win.dispatchEvent(new Event("hashchange"));
  };
  return win;
}
const settle = () => new Promise(resolve => setImmediate(resolve));

test("compara valores reales, IDs normalizados, booleanos y cambios revertidos", () => {
  const initial = { title: "Plan", responsible: 4, metrics: [{ baseline: 7, target: "3" }], confirm: false };
  const edited = { ...initial, title: "Plan editado" };
  assert.notEqual(formSnapshot(edited), formSnapshot(initial));
  edited.title = "Plan";
  assert.equal(formSnapshot(edited), formSnapshot(initial));
  assert.equal(formSnapshot({ ...initial, responsible: "4" }), formSnapshot(initial));
  assert.notEqual(formSnapshot({ ...initial, confirm: true }), formSnapshot(initial));
  assert.notEqual(formSnapshot({ ...initial, metrics: [] }), formSnapshot(initial));
});

test("enlaces: conservar no navega y descartar llega al destino una sola vez", async () => {
  const win = browser(), routes = [];
  let allow = false, prompts = 0;
  const dispose = installHashNavigation(win, async () => { prompts++; return allow; }, route => routes.push(route));
  win.click("#/sellers"); await settle();
  assert.equal(win.location.hash, "#/plans"); assert.deepEqual(routes, []);
  allow = true;
  win.click("#/sellers"); await settle();
  assert.equal(prompts, 2); assert.deepEqual(routes, ["/sellers"]);
  dispose();
});

test("Atrás rechazado conserva entrada, formulario y destino para un segundo intento", async () => {
  const win = browser(), routes = [];
  let allow = true;
  const dispose = installHashNavigation(win, async () => allow, route => routes.push(route));
  win.click("#/plans/4"); await settle();
  allow = false;
  win.history.go(-1); await settle();
  assert.equal(win.location.hash, "#/plans/4"); assert.deepEqual(routes, ["/plans/4"]);
  allow = true;
  win.history.go(-1); await settle();
  assert.equal(win.location.hash, "#/plans");
  win.history.go(1); await settle();
  assert.deepEqual(routes, ["/plans/4", "/plans", "/plans/4"]);
  dispose();
});

test("hash programático rechazado se restaura; después de guardar navega", async () => {
  const win = browser(), routes = [];
  let allow = false;
  const dispose = installHashNavigation(win, async () => allow, route => routes.push(route));
  win.hash("#/sellers"); await settle();
  assert.equal(win.location.hash, "#/plans"); assert.deepEqual(routes, []);
  allow = true;
  win.hash("#/plans/8"); await settle();
  assert.deepEqual(routes, ["/plans/8"]);
  dispose();
});

test("una decisión pendiente no duplica advertencias ni cambios de ruta", async () => {
  const win = browser(), routes = [];
  let finish, prompts = 0;
  const dispose = installHashNavigation(win, () => { prompts++; return new Promise(r => { finish = r; }); }, r => routes.push(r));
  win.click("#/sellers"); win.click("#/plans/9");
  assert.equal(prompts, 1);
  finish(true); await settle();
  assert.deepEqual(routes, ["/sellers"]);
  dispose();
});

test("reinicializar tras recarga conserva los índices y la navegación atrás", async () => {
  const win = browser();
  let dispose = installHashNavigation(win, async () => true, () => {});
  win.click("#/plans/7"); await settle(); dispose();
  const routes = [];
  dispose = installHashNavigation(win, async () => true, r => routes.push(r));
  win.history.go(-1); await settle();
  assert.deepEqual(routes, ["/plans"]);
  dispose();
});
