export class ApiError extends Error {
  constructor(status) {
    super(status === 403 ? 'Accede con una cuenta autorizada para consultar los datos.' : 'No se pudieron cargar los datos.');
    this.status = status;
  }
}

export async function getAllPages(path, { signal, request = fetch } = {}) {
  const results = [];
  let next = path;
  while (next) {
    const response = await request(next, { credentials: 'same-origin', signal });
    if (!response.ok) throw new ApiError(response.status);
    const page = await response.json();
    results.push(...page.results);
    // Mantener el mismo origen también para los enlaces de paginación de Django.
    next = page.next ? new URL(page.next, 'http://localhost').pathname + new URL(page.next, 'http://localhost').search : null;
  }
  return results;
}
