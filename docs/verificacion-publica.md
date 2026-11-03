# Acta de verificación pública — 03/11/2026

**Publicación y aceptación técnica ejecutadas** contra [SAP](https://sap-bice.vercel.app), hasta las **21:51 UTC / 22:51 Europe/Madrid**. Las pruebas se realizaron con Chromium headless desde el equipo de ejecución contra HTTPS público, con datos exclusivamente ficticios. No equivalen a una calificación académica ni a una garantía de disponibilidad futura.

| Identidad | Resultado |
| --- | --- |
| Repositorio | `Pablorossl/Seller-Action-Plan-SAP-`, ID `1430152684` |
| Candidato desplegado | **`97b4bff55a07b8fd3c71b05740748db5bf63438b`** |
| CI del SHA exacto | [41722300443 — success](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/41722300443) |
| Proyecto Vercel | `sap`, `prj_1kARDqBB0eW17w9yWX1G3QNoA2gP`, equipo `pablo-s-coding` |
| Primer deployment | `dpl_Gupjfwd6kvY7QBRKngw8zJhx2HHR`, copia git archive del candidato aprobado |
| Deployment final desde Git | **`dpl_DVtuHFEv9eTba7V8ShdLASR9BBTi`**, READY, mismo SHA |
| URL inmutable final | `sap-99vx54roa-pablo-s-coding.vercel.app` |
| Alias público verificado | `sap-bice.vercel.app`, asignado al deployment final |
| Planes comprobados al terminar | **Vercel Hobby activo / Neon Free**, sin contratación ni métodos de pago añadidos |
| Configuración efectiva | Django, raíz `backend`, fuentes externas activadas, build `python build_vercel.py`, Node 22.x, región `fra1` |
| Neon | `empty-feather-02803695` / `production`, ID `br-divine-sky-b9hvdrte`, PostgreSQL 18, rama predeterminada sin TTL |
| Migraciones | 33 registradas, sin pendientes; **ninguna ejecutada durante esta publicación** |

La conexión Git antigua se sustituyó tras conceder el titular acceso a la GitHub App. La API confirmó repo ID `1430152684` y Production `main`. Se conservaron los demás proyectos/repositorios. Production usa conexión pooled con TLS, variables privadas solo en ese entorno, clave estable, DEBUG y modo demo desactivados. La URL directa queda para administración y copias. No se ejecutan migraciones ni semillas en el build o arranque.

## Pruebas realmente ejecutadas

| ID | Comprobación | Resultado observado |
| --- | --- | --- |
| R01 | HTTPS y proxy | Certificado aceptado por clientes con validación TLS; HTTP redirige a HTTPS; login 200 y HSTS. No se probó desde una segunda red independiente |
| R02 | Login/logout | Acceso real, dashboard, logout POST y API 403 tras salir; cookies Secure/HttpOnly/SameSite comprobadas |
| R03 | Dashboard y API | Dashboard React visible, workspace autenticado y consumo de API sin errores del navegador |
| R04 | Vendedores | Búsqueda por referencia, listado y acceso a ficha verificados. Filtros y navegación entre páginas no se recorrieron públicamente |
| R05 | Indicadores | Ficha con observación ficticia inicial del 6%, periodo/política y datos consumidos por React |
| R06 | Plan | Objetivo inválido rechazado sin perder el formulario; creación válida de borrador al 3%, edición y activación |
| R07 | Acciones | Dos acciones, una completada con evidencia y otra pendiente. Plan adicional con plazos ayer/hoy/mañana |
| R08 | Revisiones | Agosto/septiembre, 100 pedidos ficticios, 4,5% y 3%; registro sin medición y cadena posterior de rectificaciones |
| R09 | Evaluación | Plan **5** alcanzado; plan **6** no alcanzado. El historial original se conserva y solo la última rectificación del periodo es efectiva |
| R10 | Cierre | Confirmación, razones e instantánea; cambios y rectificaciones posteriores al cierre rechazados |
| R11 | Aislamiento | Segundo agente: lectura y cierre del plan ajeno 404; anónimo 403. El actor autenticado sin rol se cubre por CI, no con una tercera cuenta pública |
| R12 | CSRF | Escrituras sin token y desde origen ajeno rechazadas con 403; operaciones con token válido realizadas |
| R13 | React-Django | Recorrido de interfaz completo con API real, sin mocks, errores JS ni respuestas críticas 5xx |
| R14 | Recarga y móvil | Mismos IDs tras recarga; ancho 390 px sin desbordamiento global; cierre sin controles de edición |
| R15 | Redespliegue | Mismo SHA: primer deployment → deployment Git final. JSON íntegro del plan 6, acciones, revisiones, cierre, sesión y aislamiento conservados; sin repetir demo ni migraciones |
| R16 | Estáticos | JS/CSS y estilos de login cargados, sin 404/5xx de assets durante el recorrido |
| R17 | Salud | `/healthz/` público 200 con JSON ok antes/después; no se provocó una caída de PostgreSQL de Production |
| R18 | Recuperación | Copia consistente con pg_dump 18.6, restaurada en PostgreSQL 18 local aislado; 21 tablas, todos los conteos/digests, índices y restricciones coincidentes; 33 migraciones y lectura Django de planes de control |

La aceptación adicional rechazó revisiones y periodos futuros, duplicados, rectificaciones sin motivo y ramas de rectificación sobre una revisión ya sustituida. Las revisiones **7 → 8 → 9** del plan 6 conservan autor y fecha. El cierre mantiene un vencimiento histórico y dos acciones no vencidas al cierre. Se leyó de nuevo esa misma instantánea en público tras el redespliegue; el avance simulado de 90 días se comprobó **solo contra la copia restaurada**, sin alterar el reloj ni registros de Production.

Las evidencias posteriores al despliegue se versionan en la rama `docs/sap-publicacion-2026-11-03`. `main` y Production conservan el candidato aprobado `97b4bff`; la rama documental no cambia código de aplicación ni constituye otro candidato publicado.

## Cuentas ficticias y copia privada

Se crearon dos agentes no administrativos mediante `create_demo_agent`. Se ejecutó una vez `seed_evaluation_demo` con modo demo activado únicamente en el proceso administrativo y desactivado al terminar. La carga inicial dejó cinco vendedores, diecisiete indicadores y tres planes; la aceptación añadió los planes de control. No se cargó de nuevo tras desplegar.

Las contraseñas, la clave Django y las cookies de control están en archivos locales privados ignorados por Git, con permisos 0600 y directorios 0700. No figuran en esta acta, capturas, JSON versionado ni logs públicos. Las credenciales deben entregarse al tribunal por canal privado.

La copia está en `backups/private/sap-production-97b4bff-20261103.dump`, modo 0600, SHA-256 `bc09b7278aa942d8e3318de510e0145dc7543948d0ee0c57a1efb5cd3f39b33c`. Se exportó un snapshot repeatable-read de solo lectura y se restauró **únicamente** en `sap_recovery_20261103`, servidor local PostgreSQL 18 aislado, puerto 55448. El servidor temporal quedó detenido después de verificarlo. Production nunca fue destino de restauración. Los binarios y su dependencia se extrajeron en `/tmp` desde paquetes oficiales verificados, sin cambiar paquetes o servicios del sistema.

## Evidencias y límites

- [JSON de resultados sin secretos](evidencias-publicacion-2026-11-03.json).
- Capturas públicas nuevas: [dashboard](screenshots/publicacion-dashboard.png), [rectificación](screenshots/publicacion-rectificacion.png), [cierre histórico](screenshots/publicacion-cierre-historico.png), [persistencia](screenshots/publicacion-persistencia.png) y [móvil](screenshots/publicacion-movil.png). Las capturas antiguas conservan su carácter de QA local.
- Se ejecutaron antes del commit: prueba frontend aprobada, siete pruebas de configuración Django sobre SQLite aislado y validación del paquete Vercel (33 módulos React y 157 estáticos). La CI del candidato ejecutó el workflow completo.
- El permiso GitHub App bloqueó inicialmente la conexión; el titular lo concedió y la sustitución del enlace terminó correctamente. La primera publicación por archivo del commit y la posterior desde Git conservan el mismo SHA aprobado.
- Un selector del checker adicional coincidía con «Vencida» y «No vencida». Se precisó y se completó la comprobación sobre el mismo plan, sin crear otro. El comparador de recuperación se corrigió para tablas cuya clave no es `id`, antes de exportar la copia. No fueron fallos funcionales de SAP.

Quedan pendientes la comprobación desde otra red, los filtros/paginación públicos y la operación continuada durante evaluación, además de actualizar memoria/PDF, revisar capturas seleccionadas por el autor, grabar el vídeo real accesible de hasta cinco minutos y ensayar la defensa personal. Las cuotas Hobby/Free y el estado de los servicios deben seguir revisándose. La publicación técnica no completa por sí sola la entrega académica.
