import assert from "node:assert/strict";
import test from "node:test";
import { ApiError, api, getAllPages, setCsrfToken } from "./api.js";

test("rechaza JSON malformado, HTML y cuerpos vacíos con HTTP 200", async () => {
  for (const body of ['{"today":', '<html>Proxy interno</html>', '']) {
    await assert.rejects(api("/api/overview/", {
      request: async () => new Response(body, { status: 200 }),
    }), (error) => error instanceof ApiError && error.status === 200 &&
      error.message.includes("respuesta inválida") && !error.message.includes(body || "Proxy"));
  }
});

test("acepta JSON válido y DELETE 204 sin intentar leer JSON", async () => {
  const data = { today: "2026-11-07", counts: { sellers: 2 } };
  assert.deepEqual(await api("/api/overview/", {
    request: async () => Response.json(data),
  }), data);
  assert.equal(await api("/api/sellers/1/", {
    method: "DELETE", request: async () => new Response(null, { status: 204 }),
  }), null);
});

test("conserva estado HTTP y detalles de errores JSON y HTML", async () => {
  for (const status of [400, 403, 500]) {
    for (const body of [JSON.stringify({ detail: "Error controlado" }), "<html>Privado</html>"]) {
      await assert.rejects(api("/api/plans/", {
        request: async () => new Response(body, { status }),
      }), (error) => error instanceof ApiError && error.status === status &&
        !error.message.includes("Privado") &&
        (body.startsWith("<") || error.fields.detail === "Error controlado"));
    }
  }
});

test("no reintenta escrituras con una respuesta inválida", async () => {
  let calls = 0;
  await assert.rejects(api("/api/plans/", { method: "POST", data: {}, request: async () => {
    calls++;
    return new Response("{", { status: 200 });
  } }), ApiError);
  assert.equal(calls, 1);
});

test("respeta cancelaciones durante la lectura del cuerpo", async () => {
  const abort = new DOMException("Aborted", "AbortError");
  await assert.rejects(api("/api/overview/", { request: async () => ({
    ok: true, status: 200, json: async () => { throw abort; },
  }) }), (error) => error === abort);
});

test("envía la clave de reintento y comunica conflictos de edición", async () => {
  await assert.rejects(api("/api/plans/1/actions/", {
    method: "POST", data: { description: "Revisar" }, idempotencyKey: "test-request-key",
    request: async (path, options) => {
      assert.equal(options.headers["Idempotency-Key"], "test-request-key");
      return { ok: false, status: 409, json: async () => ({ detail: "El registro ha cambiado." }) };
    },
  }), (error) => error.status === 409 && error.message.includes("Recarga"));
});

test("consume todas las páginas usando rutas del mismo origen", async () => {
  const calls = [];
  const request = async (path, options) => {
    calls.push(path);
    assert.equal(options.credentials, "same-origin");
    return {
      ok: true,
      json: async () => ({
        results: [calls.length],
        next:
          calls.length === 1 ? "https://sap.example/api/sellers/?page=2" : null,
      }),
    };
  };
  assert.deepEqual(await getAllPages("/api/sellers/", { request }), [1, 2]);
  assert.deepEqual(calls, ["/api/sellers/", "/api/sellers/?page=2"]);
});

test("propaga denegación de acceso sin presentarla como lista vacía", async () => {
  await assert.rejects(
    getAllPages("/api/sellers/", {
      request: async () => ({ ok: false, status: 403 }),
    }),
    (error) => error instanceof ApiError && error.status === 403,
  );
});

test("escribe con sesión, CSRF y JSON y conserva el resultado persistido", async () => {
  setCsrfToken("test-csrf-token");
  const result = await api("/api/plans/1/actions/", {
    method: "POST",
    data: { description: "Revisar embalajes" },
    request: async (path, options) => {
      assert.equal(path, "/api/plans/1/actions/");
      assert.equal(options.credentials, "same-origin");
      assert.equal(options.headers["X-CSRFToken"], "test-csrf-token");
      assert.equal(JSON.parse(options.body).description, "Revisar embalajes");
      return { ok: true, json: async () => ({ id: 1, actions: [{ id: 7 }] }) };
    },
  });
  assert.equal(result.actions[0].id, 7);
});

test("mantiene los errores de campo del servidor", async () => {
  await assert.rejects(
    api("/api/plans/", {
      method: "POST",
      data: {},
      request: async () => ({
        ok: false,
        status: 400,
        json: async () => ({ due_date: ["Plazo incoherente."] }),
      }),
    }),
    (error) =>
      error instanceof ApiError &&
      error.fields.due_date[0] === "Plazo incoherente.",
  );
});

test("distingue acceso denegado y registro no disponible", async () => {
  for (const status of [403, 404]) {
    await assert.rejects(
      api("/api/plans/1/", {
        request: async () => ({ ok: false, status, json: async () => ({}) }),
      }),
      (error) => error.status === status,
    );
  }
});

test("convierte fallos de red en un mensaje recuperable y respeta cancelaciones", async () => {
  await assert.rejects(
    api("/api/overview/", {
      request: async () => {
        throw new TypeError("Failed to fetch");
      },
    }),
    (error) => error.status === 0 && !error.message.includes("TypeError"),
  );
  const abort = new DOMException("Aborted", "AbortError");
  await assert.rejects(
    api("/api/overview/", {
      request: async () => {
        throw abort;
      },
    }),
    (error) => error === abort,
  );
});
