# Acta de aceptación pública — pendiente

**No ejecutada.** No se dispone de una URL pública confirmada ni de acceso conectado a Render en esta sesión. No se provisionó infraestructura. Las capturas de Fase 4 corresponden exclusivamente a QA local.

Rellenar después de desplegar: URL real, fecha y hora con zona, SHA desplegado, identificador de deploy, versión PostgreSQL, navegador, evaluador de la prueba y ubicación privada de logs sin secretos. Obtener la URL del panel; no deducirla del nombre `sap-web`.

| ID | Comprobación | Procedimiento/evidencia que debe guardarse | Estado remoto |
| --- | --- | --- | --- |
| R01 | HTTPS | Abrir desde otra red, certificado válido, HTTP redirige; verificar proxy y cabeceras | Pendiente |
| R02 | Login y logout | Sesión real y cierre POST; API denegada tras salir; cookies seguras sin publicar sus valores | Pendiente |
| R03 | Dashboard | Contadores corresponden a `/api/overview/` y vendedores asignados | Pendiente |
| R04 | Listado de vendedores | Búsqueda, filtro y paginación | Pendiente |
| R05 | Ficha e indicadores | Vendedor, canal, periodo, política y valor inicial | Pendiente |
| R06 | Crear plan | Borrador con objetivo 3%; validación de objetivo inválido y posterior corrección | Pendiente |
| R07 | Acciones | Dos acciones, completar una con fecha/evidencia; otra pendiente | Pendiente |
| R08 | Revisiones | Meses agosto y septiembre de 2026, 100 pedidos ficticios, valores 4,5% y 3% | Pendiente |
| R09 | Evaluación | Comparar respuesta del backend y tabla React: `achieved` | Pendiente |
| R10 | Cierre | Razones, confirmación, instantánea y plan sin edición | Pendiente |
| R11 | Permisos | Segundo agente: GET y cierre del plan ajeno devuelven 404; sin rol, 403 | Pendiente |
| R12 | CSRF | Escritura con sesión y sin token rechazada con 403; con token válido funciona | Pendiente |
| R13 | React-Django | Network: GET de API, JSON ficticio y datos visibles, sin mostrar cookies | Pendiente |
| R14 | Recarga | Mismo ID, dos acciones, dos revisiones y cierre después de recargar | Pendiente |
| R15 | Redespliegue | Registrar ID y datos antes; redeploy del mismo SHA, volver a consultar sin sembrar datos | Pendiente |
| R16 | Estáticos | CSS/JS con 200; sin 404/5xx, diseño escritorio y móvil | Pendiente |
| R17 | Salud | `/healthz/` devuelve 200 y `status=ok`; fallo SQL sólo en entorno aislado autorizado | Pendiente |
| R18 | Backup y recuperación | Evidencia de PITR/retención; restauración en base nueva, recuentos e histórico coincidentes | Pendiente |

El script `scripts/verify_browser.py` automatiza gran parte del flujo, incluido logout. No valida por sí solo R01 completo, R15 ni R18. Ejecutarlo sólo sobre datos ficticios autorizados:

```bash
python scripts/verify_browser.py --url https://DOMINIO_REAL \
  --username evaluador --other-username otro_agente \
  --seller-reference SAP-DEMO-PLAN --allow-writes
```

Solicita las contraseñas de forma privada y verifica TLS público. No usar `local_tls=True` para aceptar producción. Documentar los fallos tal como sucedan, corregirlos y repetir el caso afectado; no sustituir un resultado pendiente por una prueba de localhost.

Antes del redeploy guardar de forma privada la respuesta de `/api/plans/ID/` sin cabeceras de sesión, comprobar acciones, revisiones y `closure_evaluation`; compararla después del deploy. Anotar ambos identificadores de despliegue. No ejecutar semillas para reconstruir el resultado. Para recuperación seguir [despliegue](despliegue.md), con coste de la segunda base autorizado y sin sobrescribir el origen.
