import assert from 'node:assert/strict';
import test from 'node:test';
import { ApiError, getAllPages } from './api.js';

test('consume todas las páginas usando rutas del mismo origen', async () => {
  const calls = [];
  const request = async (path, options) => {
    calls.push(path);
    assert.equal(options.credentials, 'same-origin');
    return { ok: true, json: async () => ({
      results: [calls.length], next: calls.length === 1 ? 'https://sap.example/api/sellers/?page=2' : null,
    }) };
  };
  assert.deepEqual(await getAllPages('/api/sellers/', { request }), [1, 2]);
  assert.deepEqual(calls, ['/api/sellers/', '/api/sellers/?page=2']);
});

test('propaga denegación de acceso sin presentarla como lista vacía', async () => {
  await assert.rejects(getAllPages('/api/sellers/', { request: async () => ({ ok: false, status: 403 }) }),
    error => error instanceof ApiError && error.status === 403);
});
