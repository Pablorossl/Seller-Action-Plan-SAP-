# Checklist de entrega y pendientes externos

**SAP aún no está listo para la entrega oficial.** Responsable de las acciones externas: Pablo Rosales. No se ha contratado, desplegado, enviado correo ni entregado material en nombre del autor.

## Cuatro entregables

| Entregable | Ubicación actual | Pendiente antes de compartir |
| --- | --- | --- |
| Repositorio | [GitHub público](https://github.com/Pablorossl/Seller-Action-Plan-SAP-) | Revisar diff, guardar Fase 4, autorizar push y comprobar CI del nuevo SHA |
| Aplicación | **Sin URL pública confirmada** | Autorizar Render, desplegar y completar las 18 comprobaciones del acta |
| Memoria | [PDF](memoria-pfm.pdf) y [fuente editable](memoria-pfm.md) | Revisión de Pablo; completar evidencia pública y exportar otra vez |
| Vídeo | [Guion 4:50](guion-video-pfm.md) | Grabar, verificar ≤5 min, publicar con autorización y probar enlace |

Compartir credenciales del evaluador por canal privado, separadas del repositorio público. No incluir claves, cookies, tokens ni dumps en capturas, memoria o vídeo. GitHub es público; memoria y vídeo deberán tener permisos de lectura para el tribunal. Comprobar los enlaces como lo haría un docente sin la sesión del autor.

## Orden de cierre

1. Confirmar aprobación de actividades Prework, Frontend y Backend y autorización previa del equipo docente. El repositorio no acredita esos datos.
2. Revisar el presupuesto Render: base orientativa 13 USD/mes más conceptos aplicables; confirmar total en el panel y autorizar recursos. Seguir [despliegue](despliegue.md). No aplicar el Blueprint ni generar costes sin esa autorización.
3. Crear agente de evaluación y segundo agente de comprobación mediante consola privada; cargar únicamente demo ficticia y desactivar después `SAP_DEMO_MODE`.
4. Completar [acta pública](verificacion-publica.md): URL/commit/deploy/fecha, HTTPS, recorrido, permisos, CSRF, recarga, redeploy, estáticos, salud y recuperación. La prueba de recuperación en una segunda instancia puede tener coste adicional y debe estar autorizada.
5. Incorporar resultados remotos reales a memoria, matriz y README. Regenerar PDF, revisar todas las páginas y comprobar que no quedan afirmaciones de producción sin evidencia.
6. Ensayar y grabar el vídeo; revisar contenido y duración y completar su enlace real. Ensayar la [defensa](preparacion-defensa.md) con preguntas sobre código.
7. Guardar cambios en commits descriptivos; solicitar autorización de push cuando el conjunto esté revisado. Verificar Actions y acceso al SHA que se entregue.
8. Reunir los cuatro enlaces y remitirlos por el procedimiento académico indicado, sólo por acción del autor o autorización expresa. No se ha realizado este envío.
9. Mantener la aplicación disponible y supervisada durante revisión y defensa. Después de superar la revisión inicial, utilizar el enlace de Calendly facilitado por la academia. Atender correcciones; la guía contempla feedback hasta diez días hábiles tras la defensa.

## Registro final a completar

| Dato | Valor |
| --- | --- |
| Autor | Pablo Rosales, confirmado por el usuario |
| SHA definitivo de entrega | Pendiente; base auditada `49ee198` |
| URL pública y fecha de aceptación | Pendientes |
| Enlace de memoria entregada | Pendiente de publicación; PDF local existente |
| Enlace, duración y fecha del vídeo | Pendientes |
| Confirmaciones Prework / Frontend / Backend | Pendientes de evidencia |
| Confirmación docente previa | Pendiente de evidencia |
| Fecha de revisión y defensa | Pendiente de convocatoria |
| Continuidad de alojamiento hasta | Pendiente de fijar según evaluación |

## Propuesta de commits

- `test(qa): capturar evidencias PFM y verificar cierre de sesión`: ampliación de `scripts/verify_browser.py`.
- `docs(deploy): actualizar costes y acta de aceptación pública`: `docs/despliegue.md` y `docs/verificacion-publica.md`.
- `docs(pfm): preparar memoria, evidencias, vídeo y defensa`: documentos académicos, PDF, diagramas, capturas, exportador y enlaces del README.

Son propuestas, no commits ejecutados. El historial anterior se conserva. No hay cambios de infraestructura en `render.yaml` que justifiquen un commit ficticio de despliegue. Un push de estos cambios requerirá autorización expresa.
