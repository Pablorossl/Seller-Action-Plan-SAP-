export class ApiError extends Error {
  constructor(status, fields = {}) {
    super(
      status === 403
        ? "Tu sesión ha caducado o no tienes permiso para esta operación."
        : status === 404
          ? "No se encuentra este registro o no tienes acceso a él."
          : status === 400
            ? "Revisa los campos indicados antes de guardar."
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

export async function api(
  path,
  { method = "GET", data, signal, request = fetch } = {},
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
      },
      ...(data !== undefined ? { body: JSON.stringify(data) } : {}),
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new ApiError(0);
  }
  const body = await response.json().catch(() => ({}));
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
