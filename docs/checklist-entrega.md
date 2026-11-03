# Checklist final frente a la guía académica

Revisión: **03/11/2026**. Responsable de la entrega personal: Pablo Rosales. La preparación documental está terminada; **la entrega académica aún requiere vídeo real, revisión personal y envío por el procedimiento docente**. No se ha enviado nada a la academia durante esta tarea.

## Identidad de lo que se entrega

| Elemento | Referencia y alcance |
| --- | --- |
| Aplicación pública | [SAP](https://sap-bice.vercel.app), con datos ficticios |
| Código desplegado | `97b4bff55a07b8fd3c71b05740748db5bf63438b`, [CI aprobada](https://github.com/Pablorossl/Seller-Action-Plan-SAP-/actions/runs/41722300443) |
| Deployment aceptado | `dpl_DVtuHFEv9eTba7V8ShdLASR9BBTi` |
| Documentación pública de partida | `575c6c942318885d6b7427ccedabc1eea7cc5887`; no es otro SHA de aplicación |
| Revisión académica actual | Cambios locales posteriores a `575c6c9`, sin commit nuevo, push ni redespliegue en esta tarea |
| Memoria | [PDF revisado, 24 páginas](memoria-pfm.pdf), [Word editable](memoria-pfm.docx) y [Markdown fuente](memoria-pfm.md) |
| Vídeo | [Guion de 4:20](guion-video-pfm.md), 40 s de margen; archivo, duración real y URL aún inexistentes |
| Defensa | [Guion y 26 preguntas](preparacion-defensa.md); propuesta total máxima de 20 min, incluidos preguntas y margen |

## Completado y comprobado

- [x] Guía original releída; seis contenidos explícitos cubiertos: problema, aportación/eficiencia, tecnologías justificadas, usuarios, casos de uso con resultados/errores y seguridad. Correspondencia detallada en [matriz](trazabilidad-requisitos.md) y anexo A de la memoria.
- [x] Django con modelos, vistas, plantillas, autenticación y persistencia; React consume el backend real en dashboard, vendedores y planes. Repositorio público con README, estructura e historial progresivo.
- [x] HTTPS, redirecciones, sesión/login/logout, estáticos, API, flujo vendedor → indicador → plan → acciones → revisiones → evaluación → cierre, CSRF y aislamiento entre agentes: [acta pública](verificacion-publica.md).
- [x] F01 conserva rectificaciones enlazadas con autor/motivo; F02 rechaza fechas observadas futuras; F03 conserva el cierre histórico. Los límites de pruebas públicas frente a locales/CI están expresados.
- [x] Filtros públicos de vendedores y estados de planes. Paginación de vendedores con 50 + 1 resultados reales, límites y reinicio al buscar/filtrar; 51 registros temporales retirados y datos originales preservados: [resultados](evidencias-filtros-paginacion-2026-11-03.json). No se afirma navegación de dos páginas de planes.
- [x] Persistencia tras redesplegar el mismo candidato, sin recargar demo. Recuperación de copia real en PostgreSQL 18 aislado, con 21 tablas y esquema/datos coincidentes. Nunca se restauró sobre Production.
- [x] Vercel Hobby y Neon Free confirmados en la publicación; rama `production` predeterminada sin TTL. Presupuesto de contratación: 0 €, sin pruebas de pago ni métodos de pago añadidos. Disponibilidad futura sujeta a cuotas y supervisión.
- [x] Memoria actualizada con arquitectura real, capturas públicas, ejemplos ficticios y distinción entre beneficios esperados y resultados técnicos. No se atribuyen métricas de productividad ni experiencias de usuarios no estudiadas.
- [x] Exportaciones PDF y DOCX producidas desde la fuente editable. Las 24 páginas del PDF se revisaron visualmente; [registro de revisión](revision-memoria-pdf-2026-11-03.json) y [reproducción](exportacion-memoria.md). El Word puede repaginarse en otro editor.
- [x] Entregables revisados para excluir secretos conocidos, sesiones, archivos `.env`, copias privadas y archivos generados innecesarios. `sources/` no existe en este checkout y no se ha creado ni modificado.
- [x] Aplicación conservada en el mismo deployment y SHA; esta tarea no incorpora funciones, migraciones, semillas, push ni redespliegues. Los únicos datos temporales fueron los registros ficticios de paginación, ya retirados.

## Preparado, pero pendiente de ejecución

- [ ] Ensayar el vídeo con cronómetro; realizar y guardar las operaciones reales del caso ficticio preparado. El guion reserva 4:20, pero no acredita duración de una grabación.
- [ ] Grabar, reproducir y revisar el archivo completo: ≤300 s, problema/usuario/demostración/Django/React/PostgreSQL, texto y audio legibles, URL pública y ausencia de secretos.
- [ ] Alojar el vídeo y comprobar el enlace con permisos de lectura para el tribunal sin depender de la sesión del autor. No confundir esa comprobación con una red independiente.
- [ ] Ensayar la exposición de defensa de 10:30 y responder las preguntas desde el código; 7:30 para preguntas y 2:00 de margen. El límite de la guía es 20 minutos de videollamada total.
- [ ] Conservar la aplicación y revisar cuotas Free/Hobby durante la revisión y defensa. Una comprobación puntual no acredita continuidad futura.
- [ ] Publicar la revisión documental solo cuando el autor lo autorice en una tarea posterior y comprobar su SHA/CI. El código público debe seguir identificado por `97b4bff` mientras no haya otro candidato validado.

## Pendiente de mi intervención — autor

- [ ] Probar SAP desde **otra red real**, por ejemplo datos móviles con Wi-Fi desactivado; registrar fecha, red, HTTPS, login, estáticos y recorrido. Otra sesión, navegador o agente en el mismo equipo no es equivalente. No se ha dispuesto aquí de una red independiente.
- [ ] Leer y hacer propia la memoria, revisar las capturas y comprender las rutas de código del guion de defensa. Corregir cualquier atribución personal que no pueda sostenerse.
- [ ] Contrastar las aprobaciones de Prework, Frontend y Backend y la confirmación docente previa con sus justificantes. Consta una declaración previa del autor, **no una inspección del expediente**.
- [ ] Compartir las credenciales del evaluador por canal privado, separadas de GitHub, PDF y vídeo. Nunca adjuntar dumps, cookies o archivos privados al paquete académico.
- [ ] Reunir y remitir los cuatro enlaces: [GitHub](https://github.com/Pablorossl/Seller-Action-Plan-SAP-), [app](https://sap-bice.vercel.app), memoria y vídeo. **URL compartida de la memoria: pendiente. URL y duración real del vídeo: pendientes.**
- [ ] Esperar revisión inicial docente; utilizar su Calendly cuando corresponda. Fecha de convocatoria y defensa: pendientes. La guía prevé feedback hasta diez días hábiles después, una defensa por trimestre y mejoras que respondan al feedback en una reentrega.

La rúbrica oficial es backend 30 %, React 15 %, arquitectura 15 %, seguridad 15 %, documentación 15 % y reflexión 10 %, con mínimo 7/10. Esta checklist no calcula ni garantiza una nota. Docker y dominio propio son opcionales; no hay un número de páginas obligatorio. Ningún pendiente se resuelve contratando servicios durante esta preparación.
