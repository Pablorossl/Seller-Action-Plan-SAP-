export class ApiError extends Error {
  constructor(status, fields = {}, invalidResponse = false) {
    super(
      invalidResponse
        ? "SAP ha devuelto una respuesta inválida. Vuelve a cargar los datos o inténtalo de nuevo."
        : status === 403
        ? "Tu cuenta no tiene permiso para esta operación."
        : status === 404
          ? "No se encuentra este registro o no tienes acceso a él."
          : status === 400
            ? "Revisa los campos indicados antes de guardar."
            : status === 409
              ? "El registro ha cambiado. Recarga sus datos y revisa tus cambios antes de guardarlos."
            : "No se pudo conectar con SAP. Inténtalo de nuevo.",
    );
    this.status = status;
    this.fields = fields;
  }
}

let csrfToken = "";
export function setCsrfToken(token) {
  csrfToken = token;
}
export function localPath(path) {
  const url = new URL(path, "http://localhost");
  return url.pathname + url.search;
}

function checkSession(response) {
  if (response.headers?.get("X-SAP-Session") === "expired") {
    window.location.replace("/accounts/login/?next=" + encodeURIComponent(window.location.pathname + window.location.hash));
  }
}

export async function api(
  path,
  { method = "GET", data, signal, idempotencyKey, request = fetch } = {},
) {
  let response;
  try {
    response = await request(localPath(path), {
      method,
      credentials: "same-origin",
      signal,
      headers: {
        Accept: "application/json",
        ...(data !== undefined ? { "Content-Type": "application/json" } : {}),
        ...(method !== "GET" ? { "X-CSRFToken": csrfToken } : {}),
        ...(idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {}),
      },
      ...(data !== undefined ? { body: JSON.stringify(data) } : {}),
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new ApiError(0);
  }
  checkSession(response);
  if (response.status === 204) return null;
  let body;
  try {
    body = await response.json();
  } catch (error) {
    if (error.name === "AbortError") throw error;
    // Los errores HTTP conservan su estado incluso si el proxy devuelve HTML.
    // Un éxito con cuerpo ilegible nunca debe llegar al consumidor como datos.
    throw new ApiError(response.status, {}, response.ok);
  }
  if (!response.ok) throw new ApiError(response.status, body);
  return body;
}

export async function getAllPages(path, { signal, request = fetch } = {}) {
  const results = [];
  let next = path;
  while (next) {
    const response = await request(next, {
      credentials: "same-origin",
      signal,
    });
    checkSession(response);
    if (!response.ok) throw new ApiError(response.status);
    const page = await response.json();
    results.push(...page.results);
    // Mantener el mismo origen también para los enlaces de paginación de Django.
    next = page.next
      ? new URL(page.next, "http://localhost").pathname +
        new URL(page.next, "http://localhost").search
      : null;
  }
  return results;
}
