# Checklist de entrega y pendientes externos

Actualizada el **02/11/2026**. **SAP aún no está listo para la entrega oficial.** Responsable de las acciones externas: Pablo Rosales. Destino actual: Vercel Hobby + Neon Free. Esta revisión guarda cambios en Git y valida el entorno local; la aceptación pública sigue pendiente.

## Cuatro entregables

| Entregable | Ubicación actual | Pendiente antes de compartir |
| --- | --- | --- |
| Repositorio | [GitHub público](https://github.com/Pablorossl/Seller-Action-Plan-SAP-); Fase 4 registrada en `57d296f` | Publicar el commit de adaptación Vercel/Neon y comprobar CI del nuevo SHA |
| Aplicación | `sap-bice.vercel.app`, **pendiente de aceptación pública** | Confirmar proyecto/rama Neon, migrar, desplegar en Vercel y completar las 18 comprobaciones del acta |
| Memoria | [PDF](memoria-pfm.pdf) y [fuente editable](memoria-pfm.md) | Revisión de Pablo; completar evidencia pública y exportar otra vez |
| Vídeo | [Guion 4:50](guion-video-pfm.md) | Grabar, verificar ≤5 min, publicar con autorización y probar enlace |

Compartir credenciales del evaluador por canal privado, separadas del repositorio público. No incluir claves, cookies, tokens ni dumps en capturas, memoria o vídeo. GitHub es público; memoria y vídeo deberán tener permisos de lectura para el tribunal. Comprobar los enlaces como lo haría un docente sin la sesión del autor.

## Orden de cierre

1. Confirmar aprobación de actividades Prework, Frontend y Backend y autorización previa del equipo docente. El repositorio no acredita esos datos.
2. Confirmar proyecto/rama y conexiones en [Neon setup](neon-setup.md), así como los planes Free/Hobby y sus cuotas. Seguir [despliegue Vercel](despliegue-vercel.md) para configurar variables, migraciones y publicación. Render queda como antecedente; no forma parte del destino actual.
3. Crear agente de evaluación y segundo agente de comprobación mediante consola privada; cargar únicamente demo ficticia y desactivar después `SAP_DEMO_MODE`.
4. Completar [acta pública](verificacion-publica.md): URL/commit/deploy/fecha, HTTPS, recorrido, permisos, CSRF, recarga, redeploy, estáticos, salud y recuperación. Ensayar restauración en una base separada dentro de las cuotas gratuitas, sin sobrescribir el origen.
5. Incorporar resultados remotos reales a memoria, matriz y README. Regenerar PDF, revisar todas las páginas y comprobar que no quedan afirmaciones de producción sin evidencia.
6. Ensayar y grabar el vídeo; revisar contenido y duración y completar su enlace real. Ensayar la [defensa](preparacion-defensa.md) con preguntas sobre código.
7. Guardar cambios en commits descriptivos; solicitar autorización de push cuando el conjunto esté revisado. Verificar Actions y acceso al SHA que se entregue.
8. Reunir los cuatro enlaces y remitirlos por el procedimiento académico indicado, sólo por acción del autor o autorización expresa. No se ha realizado este envío.
9. Mantener la aplicación disponible y supervisada durante revisión y defensa. Después de superar la revisión inicial, utilizar el enlace de Calendly facilitado por la academia. Atender correcciones; la guía contempla feedback hasta diez días hábiles tras la defensa.

## Registro final a completar

| Dato | Valor |
| --- | --- |
| Autor | Pablo Rosales, confirmado por el usuario |
| SHA definitivo de entrega | Pendiente; Fase 4 en `57d296f`, seguida de la adaptación Vercel/Neon |
| URL pública y fecha de aceptación | Pendientes |
| Enlace de memoria entregada | Pendiente de publicación; PDF local existente |
| Enlace, duración y fecha del vídeo | Pendientes |
| Confirmaciones Prework / Frontend / Backend | Pendientes de evidencia |
| Confirmación docente previa | Pendiente de evidencia |
| Fecha de revisión y defensa | Pendiente de convocatoria |
| Continuidad de alojamiento hasta | Pendiente de fijar según evaluación |

## Registro del avance

La memoria, evidencias y preparación de defensa se registraron en `57d296f` (`docs(fase-4)`). El siguiente bloque prepara el despliegue Vercel/Neon, sus comprobaciones y la actualización de esta checklist. Las [evidencias de revisión](verificacion-vercel.md) identifican qué se ha probado localmente. El SHA de entrega se fijará tras publicar y comprobar la CI y la aplicación pública.
