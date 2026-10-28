import React, { useState } from "react";
import {
  Avatar,
  Badge,
  Empty,
  Field,
  FormActions,
  FormError,
  Icon,
  Modal,
  PageHeading,
  Pagination,
  Resource,
  date,
  finalPlan,
  labels,
  metricLabels,
  planUrl,
  sellerUrl,
  useMutation,
  useResource,
  value,
} from "../components/ui.jsx";
import { PlanForm } from "./PlanForm.jsx";

function Comparison({ plan }) {
  return (
    <div
      className="table-wrap"
      tabIndex={0}
      role="region"
      aria-label="Tabla de datos desplazable"
    >
      <table>
        <thead>
          <tr>
            <th>Indicador / canal</th>
            <th>Inicial</th>
            <th>Objetivo</th>
            <th>Último valor</th>
            <th>Resultado medido</th>
          </tr>
        </thead>
        <tbody>
          {plan.evaluation.metrics.map((m) => (
            <tr key={m.metric_id}>
              <td>
                <strong>{metricLabels[m.code]}</strong>
                <small>{m.channel}</small>
              </td>
              <td>{value(m.initial, m.unit)}</td>
              <td>{value(m.target, m.unit)}</td>
              <td className="metric-value">
                {value(m.current, m.unit)}
                <small>
                  {m.period_end
                    ? `Periodo hasta ${date(m.period_end)}`
                    : "Sin revisión registrada"}
                </small>
              </td>
              <td>
                <Badge
                  status={
                    m.achieved === null
                      ? "not_evaluable"
                      : m.achieved
                        ? "achieved"
                        : "not_achieved"
                  }
                />
                {m.improved !== null && (
                  <small>
                    {m.improved
                      ? "Mejora respecto al inicio"
                      : "Sin mejora respecto al inicio"}
                  </small>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function MetricForm({ plan, metric, done, close }) {
  const mutation = useMutation(done);
  const [page, setPage] = useState(1);
  const [baseline, setBaseline] = useState(metric?.baseline.id || "");
  const [target, setTarget] = useState(metric?.target_value || "");
  const resource = useResource(
    !metric ? `/api/metrics/?seller=${plan.seller}&page=${page}` : null,
  );
  return (
    <Modal
      title={metric ? "Editar objetivo" : "Añadir indicador"}
      close={close}
      busy={mutation.busy}
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.submit(
            `/api/plans/${plan.id}/metrics/${metric ? `${metric.id}/` : ""}`,
            metric
              ? { target_value: target, revision: metric.revision }
              : { baseline, target_value: target },
            metric ? "PATCH" : "POST",
          );
        }}
      >
        <FormError error={mutation.error} />
        <p className="info-note">
          El indicador debe coincidir con el periodo {date(plan.period_start)} —{" "}
          {date(plan.period_end)}. El objetivo queda fijado al activar el plan o
          registrar revisiones.
        </p>
        <fieldset disabled={mutation.busy}>
          {metric ? (
            <p>
              {metric.baseline.label} · Inicial:{" "}
              {value(metric.baseline.value, metric.baseline.unit)}
            </p>
          ) : (
            <Resource resource={resource}>
              {(data) => (
                <>
                  <Field
                    label="Observación inicial"
                    name="baseline"
                    required
                    value={baseline}
                    errors={mutation.error?.fields}
                    onChange={(e) => setBaseline(e.target.value)}
                  >
                    <select>
                      <option value="">Selecciona un indicador</option>
                      {data.results
                        .filter(
                          (m) =>
                            m.period_start === plan.period_start &&
                            m.period_end === plan.period_end,
                        )
                        .map((m) => (
                          <option key={m.id} value={m.id}>
                            {m.label} · {m.channel} · {value(m.value, m.unit)}
                          </option>
                        ))}
                    </select>
                  </Field>
                  <Pagination
                    data={data}
                    page={page}
                    setPage={(p) => {
                      setPage(p);
                      setBaseline("");
                    }}
                  />
                </>
              )}
            </Resource>
          )}
          <Field
            label="Valor objetivo (unidad del indicador)"
            name="target_value"
            required
            type="number"
            step="0.01"
            value={target}
            errors={mutation.error?.fields}
            onChange={(e) => setTarget(e.target.value)}
          />
        </fieldset>
        <FormActions busy={mutation.busy} close={close} />
      </form>
    </Modal>
  );
}

function ActionForm({ plan, action, done, close }) {
  const mutation = useMutation(done);
  const [form, setForm] = useState(
    action
      ? Object.fromEntries(
          [
            "description",
            "kind",
            "responsible",
            "due_date",
            "status",
            "completed_on",
            "notes",
            "evidence",
          ].map((key) => [key, action[key] || ""]),
        )
      : {
          description: "",
          kind: "corrective",
          responsible: "",
          due_date: "",
          status: "pending",
          completed_on: "",
          notes: "",
          evidence: "",
        },
  );
  const bind = (name) => ({
    name,
    value: form[name],
    errors: mutation.error?.fields,
    onChange: (e) =>
      setForm((f) => ({
        ...f,
        [name]: e.target.value,
        ...(name === "status" && e.target.value !== "completed"
          ? { completed_on: "" }
          : {}),
      })),
  });
  return (
    <Modal
      title={action ? "Editar acción" : "Añadir acción"}
      close={close}
      busy={mutation.busy}
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.submit(
            `/api/plans/${plan.id}/actions/${action ? `${action.id}/` : ""}`,
            { ...form, completed_on: form.completed_on || null, ...(action ? { revision: action.revision } : {}) },
            action ? "PATCH" : "POST",
          );
        }}
      >
        <FormError error={mutation.error} />
        <fieldset disabled={mutation.busy}>
          <Field
            label="Descripción de la acción"
            required
            {...bind("description")}
          >
            <textarea rows="3" />
          </Field>
          <div className="form-grid">
            <Field label="Tipo" {...bind("kind")} required>
              <select>
                <option value="corrective">Correctiva</option>
                <option value="preventive">Preventiva</option>
              </select>
            </Field>
            <Field
              label="Persona o equipo responsable"
              required
              maxLength={160}
              {...bind("responsible")}
            />
          </div>
          <div className="form-grid">
            <Field
              label="Fecha límite"
              required
              type="date"
              min={plan.period_end}
              max={plan.due_date}
              {...bind("due_date")}
            />
            <Field label="Estado" required {...bind("status")}>
              <select>
                {["pending", "in_progress", "completed", "cancelled"].map(
                  (s) => (
                    <option
                      key={s}
                      value={s}
                      disabled={
                        ["completed", "cancelled"].includes(action?.status) &&
                        s !== action.status
                      }
                    >
                      {labels[s]}
                    </option>
                  ),
                )}
              </select>
            </Field>
          </div>
          {form.status === "completed" && (
            <Field
              label="Fecha de finalización"
              required
              type="date"
              {...bind("completed_on")}
            />
          )}
          <Field
            label="Evidencia de ejecución"
            required={form.status === "completed"}
            {...bind("evidence")}
          >
            <textarea rows="2" />
          </Field>
          <Field label="Observaciones" {...bind("notes")}>
            <textarea rows="2" />
          </Field>
        </fieldset>
        <FormActions
          busy={mutation.busy}
          close={close}
          label={action ? "Guardar acción" : "Añadir acción"}
        />
      </form>
    </Modal>
  );
}

function ReviewForm({ plan, user, done, close }) {
  const mutation = useMutation(done);
  const [form, setForm] = useState({
    plan_metric: plan.metrics[0]?.id || "",
    reviewed_on: user.today,
    value: "",
    period_start: "",
    period_end: "",
    order_count: "",
    comments: "",
    assessment: "on_track",
    next_steps: "",
  });
  const bind = (name) => ({
    name,
    value: form[name],
    errors: mutation.error?.fields,
    onChange: (e) => setForm((f) => ({ ...f, [name]: e.target.value })),
  });
  return (
    <Modal title="Registrar revisión" close={close} busy={mutation.busy}>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.submit(`/api/plans/${plan.id}/reviews/`, {
            ...form,
            value: form.value === "" ? null : form.value,
            order_count:
              form.order_count === "" ? null : Number(form.order_count),
          });
        }}
      >
        <FormError error={mutation.error} />
        <p className="info-note">
          La evaluación utiliza las reglas del indicador. Para MQC se necesita
          un periodo mensual y volumen suficiente de pedidos.
        </p>
        <fieldset disabled={mutation.busy}>
          <Field label="Indicador a revisar" required {...bind("plan_metric")}>
            <select>
              {plan.metrics.map((m) => (
                <option value={m.id} key={m.id}>
                  {m.baseline.label} · {m.baseline.channel} (
                  {m.baseline.unit === "hours" ? "h" : "%"})
                </option>
              ))}
            </select>
          </Field>
          <div className="form-grid">
            <Field
              label="Valor observado"
              type="number"
              step="0.01"
              hint="Déjalo vacío si no hay medición."
              {...bind("value")}
            />
            <Field
              label="Pedidos del periodo"
              type="number"
              min="0"
              step="1"
              {...bind("order_count")}
            />
            <Field
              label="Inicio del periodo medido"
              required
              type="date"
              {...bind("period_start")}
            />
            <Field
              label="Fin del periodo medido"
              required
              type="date"
              {...bind("period_end")}
            />
            <Field
              label="Fecha de revisión"
              required
              type="date"
              max={user.today}
              {...bind("reviewed_on")}
            />
            <Field
              label="Valoración del agente"
              required
              {...bind("assessment")}
            >
              <select>
                {["on_track", "at_risk", "no_progress", "no_data"].map((s) => (
                  <option key={s} value={s}>
                    {labels[s]}
                  </option>
                ))}
              </select>
            </Field>
          </div>
          <Field label="Evolución y evidencias" required {...bind("comments")}>
            <textarea rows="3" />
          </Field>
          <Field label="Próximos pasos" {...bind("next_steps")}>
            <textarea rows="2" />
          </Field>
        </fieldset>
        <FormActions
          busy={mutation.busy}
          close={close}
          label="Guardar revisión"
        />
      </form>
    </Modal>
  );
}

function CloseForm({ plan, done, close }) {
  const mutation = useMutation(done);
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState(
    plan.status === "draft" ? "cancelled" : "closed",
  );
  const [confirm, setConfirm] = useState(false);
  return (
    <Modal title="Finalizar plan de mejora" close={close} busy={mutation.busy}>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          mutation.submit(`/api/plans/${plan.id}/close/`, {
            revision: plan.revision,
            notes,
            status,
            confirm,
          });
        }}
      >
        <FormError error={mutation.error} />
        <div className="closure-summary">
          <Badge status={plan.evaluation.result} />
          <p>
            Acciones completadas: {plan.evaluation.actions.completed}. Acciones
            abiertas:{" "}
            {plan.evaluation.actions.pending +
              plan.evaluation.actions.in_progress}
            .
          </p>
        </div>
        <Comparison plan={plan} />
        <p className="info-note">
          Finalizar el plan conserva su histórico. Las acciones completadas y
          los objetivos alcanzados se evalúan por separado. Si quedan
          pendientes, documenta la decisión.
        </p>
        <fieldset disabled={mutation.busy}>
          <Field
            label="Tipo de finalización"
            name="status"
            errors={mutation.error?.fields}
            value={status}
            onChange={(e) => setStatus(e.target.value)}
          >
            <select>
              <option value="closed" disabled={plan.status === "draft"}>
                Cerrar el plan
              </option>
              <option value="cancelled">Cancelar el plan</option>
            </select>
          </Field>
          <Field
            label="Resultado y razones de la finalización"
            name="notes"
            errors={mutation.error?.fields}
            required
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          >
            <textarea rows="4" />
          </Field>
          <label className="check-label confirmation">
            <input
              type="checkbox"
              required
              checked={confirm}
              onChange={(e) => setConfirm(e.target.checked)}
            />
            He revisado los resultados y confirmo la finalización. El plan no se
            podrá reabrir ni modificar.
          </label>
        </fieldset>
        <FormActions
          busy={mutation.busy}
          close={close}
          label="Confirmar finalización"
        />
      </form>
    </Modal>
  );
}

export function PlanDetail({ id, user, params }) {
  const resource = useResource(`/api/plans/${id}/`);
  const [modal, setModal] = useState(null);
  const [editing, setEditing] = useState(false);
  const [notice, setNotice] = useState("");
  const done = (plan) => {
    resource.setData(plan);
    setModal(null);
    setEditing(false);
    setNotice("Cambios guardados correctamente.");
  };
  const transition = useMutation(done);
  if (editing && resource.data)
    return (
      <PlanForm
        existing={resource.data}
        user={user}
        params={params}
        onSaved={done}
      />
    );
  return (
    <Resource resource={resource}>
      {(plan) => {
        const closed = finalPlan(plan);
        const canEdit = !closed && user.permissions.change_improvementplan;
        const progress = closed
          ? 4
          : plan.status === "in_review"
            ? 3
            : plan.status === "in_progress"
              ? 2
              : 1;
        return (
          <>
            <a className="back-link" href="#/plans">
              ← Volver a planes
            </a>
            <PageHeading
              eyebrow={`PLAN DE MEJORA · #${plan.id}`}
              title={plan.title}
              description={
                <a href={sellerUrl(plan.seller)}>
                  {plan.seller_name} · {plan.seller_reference} ↗
                </a>
              }
            >
              <Badge status={plan.status} />
              {canEdit && (
                <button
                  className="button secondary"
                  onClick={() => setEditing(true)}
                >
                  Editar plan
                </button>
              )}
              {canEdit && user.permissions.close_improvementplan && (
                <button
                  className="button primary"
                  onClick={() => setModal({ type: "close" })}
                >
                  Finalizar plan
                  <Icon name="check" size={17} />
                </button>
              )}
            </PageHeading>
            {notice && (
              <div className="success-notice" role="status">
                <Icon name="check" size={18} />
                {notice}
                <button
                  className="icon-button"
                  aria-label="Ocultar confirmación"
                  onClick={() => setNotice("")}
                >
                  <Icon name="close" size={16} />
                </button>
              </div>
            )}
            <FormError error={transition.error} />
            <ol className="stepper">
              {[
                "Diagnóstico",
                "Plan de acción",
                "Seguimiento",
                "Resultado",
              ].map((step, i) => (
                <li className={i < progress ? "reached" : ""} key={step}>
                  <span>
                    {i + 1 < progress ? <Icon name="check" size={15} /> : i + 1}
                  </span>
                  {step}
                </li>
              ))}
            </ol>
            <div className="plan-layout">
              <div className="plan-content">
                <section className="panel">
                  <div className="panel-heading">
                    <h2>Diagnóstico y objetivos</h2>
                    <Icon name="trend" />
                  </div>
                  <div className="diagnosis-grid">
                    <div>
                      <h3>Problema identificado</h3>
                      <p className="preserve">{plan.problem}</p>
                    </div>
                    <div>
                      <h3>Causa raíz</h3>
                      <p className="preserve">{plan.root_cause}</p>
                    </div>
                    <div>
                      <h3>Evidencias</h3>
                      <p className="preserve">{plan.evidence}</p>
                    </div>
                    <div>
                      <h3>Objetivo de mejora</h3>
                      <p className="preserve">{plan.objective}</p>
                    </div>
                  </div>
                  <Comparison plan={plan} />
                  {!closed && (
                    <div className="metric-controls">
                      {user.permissions.add_planmetric && (
                        <button
                          className="button secondary compact"
                          onClick={() => setModal({ type: "metric" })}
                        >
                          Añadir indicador
                        </button>
                      )}
                      {plan.status === "draft" &&
                        user.permissions.change_planmetric &&
                        plan.metrics.map((m) => (
                          <button
                            key={m.id}
                            className="button secondary compact"
                            onClick={() =>
                              setModal({ type: "metric", metric: m })
                            }
                          >
                            Editar objetivo · {metricLabels[m.baseline.code]}
                          </button>
                        ))}
                    </div>
                  )}
                  {!plan.metrics.length && (
                    <Empty title="Sin indicadores vinculados">
                      Este plan necesita al menos un objetivo antes de
                      activarse.
                    </Empty>
                  )}
                </section>
                <section className="panel" id="acciones">
                  <div className="panel-heading">
                    <div>
                      <h2>
                        Acciones{" "}
                        <span className="count-pill">
                          {plan.actions.length}
                        </span>
                      </h2>
                      <p className="muted">
                        {plan.evaluation.actions.completed} completadas ·{" "}
                        {plan.evaluation.overdue_actions} vencidas
                        {closed ? " en el histórico" : ""}
                      </p>
                    </div>
                    {!closed && user.permissions.add_planaction && (
                      <button
                        className="button secondary compact"
                        onClick={() => setModal({ type: "action" })}
                      >
                        <Icon name="plus" size={16} />
                        Añadir acción
                      </button>
                    )}
                  </div>
                  {plan.actions.length ? (
                    <div className="action-list">
                      {plan.actions.map((a) => (
                        <article
                          id={`action-${a.id}`}
                          className={`action-item ${String(a.id) === params.get("action") ? "highlight" : ""}`}
                          key={a.id}
                        >
                          <span
                            className={`action-check ${a.status === "completed" ? "done" : ""}`}
                          >
                            <Icon
                              name={
                                a.status === "completed" ? "check" : "plans"
                              }
                              size={18}
                            />
                          </span>
                          <div className="action-main">
                            <h3>{a.description}</h3>
                            <div className="action-meta">
                              <Badge status={a.status} />
                              <span>
                                {a.kind === "corrective"
                                  ? "Correctiva"
                                  : "Preventiva"}
                              </span>
                              <span>{a.responsible}</span>
                              <span
                                className={a.is_overdue ? "text-danger" : ""}
                              >
                                {a.is_overdue ? "Vencida · " : "Plazo · "}
                                {date(a.due_date)}
                              </span>
                            </div>
                            {a.completed_on && (
                              <small>
                                Finalizada el {date(a.completed_on)}
                              </small>
                            )}
                            {a.evidence && (
                              <p className="preserve">
                                <strong>Evidencia:</strong> {a.evidence}
                              </p>
                            )}
                            {a.notes && (
                              <p className="preserve muted">{a.notes}</p>
                            )}
                          </div>
                          {!closed && user.permissions.change_planaction && (
                            <button
                              className="button secondary compact"
                              aria-label={`Editar acción: ${a.description}`}
                              onClick={() =>
                                setModal({ type: "action", action: a })
                              }
                            >
                              Editar
                            </button>
                          )}
                        </article>
                      ))}
                    </div>
                  ) : (
                    <Empty title="Concreta el siguiente paso">
                      Añade acciones correctivas y preventivas con un
                      responsable y una fecha límite.
                    </Empty>
                  )}
                </section>
                <section className="panel">
                  <div className="panel-heading">
                    <div>
                      <h2>
                        Revisiones y evolución{" "}
                        <span className="count-pill">
                          {plan.reviews.length}
                        </span>
                      </h2>
                      <p className="muted">
                        Ordenadas por el periodo de medición, del más reciente
                        al más antiguo.
                      </p>
                    </div>
                    {!closed && user.permissions.add_planreview && (
                      <button
                        className="button secondary compact"
                        onClick={() => setModal({ type: "review" })}
                      >
                        <Icon name="plus" size={16} />
                        Registrar revisión
                      </button>
                    )}
                  </div>
                  {plan.reviews.length ? (
                    <div className="timeline">
                      {plan.reviews.map((r) => {
                        const m = plan.metrics.find(
                          (m) => m.id === r.plan_metric,
                        );
                        return (
                          <article key={r.id}>
                            <span className="timeline-dot" />
                            <div className="review-heading">
                              <div>
                                <strong>
                                  {m?.baseline.label} ·{" "}
                                  {value(r.value, m?.baseline.unit)}
                                </strong>
                                <small>
                                  {date(r.period_start)} — {date(r.period_end)}{" "}
                                  · {r.order_count ?? "Sin datos de"} pedidos
                                </small>
                              </div>
                              <Badge status={r.assessment} />
                            </div>
                            <p className="preserve">{r.comments}</p>
                            {r.next_steps && (
                              <p className="preserve">
                                <strong>Próximos pasos:</strong> {r.next_steps}
                              </p>
                            )}
                            <small>
                              Revisión del {date(r.reviewed_on)} · Registrada
                              por {r.recorded_by_name}
                            </small>
                          </article>
                        );
                      })}
                    </div>
                  ) : (
                    <Empty
                      title="La evolución empieza con una revisión"
                      icon="trend"
                    >
                      Registra valores observados y evidencias para evaluar los
                      objetivos.
                    </Empty>
                  )}
                </section>
                {closed && (
                  <section className="panel closure-panel">
                    <div className="panel-heading">
                      <h2>Resultado y cierre</h2>
                      <Badge status={plan.closure_evaluation.result} />
                    </div>
                    <p className="preserve">{plan.closure_notes}</p>
                    <small>
                      Finalizado el {date(plan.closed_at)}. Evaluación
                      conservada en el momento del cierre.
                    </small>
                    <p>
                      Acciones al finalizar:{" "}
                      {plan.closure_evaluation.actions?.completed ?? 0}{" "}
                      completadas ·{" "}
                      {(plan.closure_evaluation.actions?.pending ?? 0) +
                        (plan.closure_evaluation.actions?.in_progress ??
                          0)}{" "}
                      abiertas.
                    </p>
                  </section>
                )}
              </div>
              <aside className="plan-sidebar">
                <section className="panel">
                  <div className="panel-heading">
                    <h2>Seguimiento</h2>
                  </div>
                  <dl>
                    <dt>Responsable</dt>
                    <dd className="person">
                      <Avatar name={plan.responsible_name} small />
                      {plan.responsible_name}
                    </dd>
                    <dt>Fecha objetivo</dt>
                    <dd>
                      <Icon name="calendar" size={17} />
                      {date(plan.due_date)}
                    </dd>
                    <dt>Próxima revisión</dt>
                    <dd>{date(plan.next_review_on)}</dd>
                    <dt>Periodo del diagnóstico</dt>
                    <dd>
                      {date(plan.period_start)}
                      <br />— {date(plan.period_end)}
                    </dd>
                    <dt>Creado</dt>
                    <dd>{date(plan.created_at)}</dd>
                  </dl>
                  {canEdit && (
                    <div className="state-actions">
                      {plan.status === "draft" && (
                        <>
                          <p>
                            Añade indicadores y al menos una acción para activar
                            el plan.
                          </p>
                          <button
                            className="button primary"
                            disabled={transition.busy}
                            onClick={() =>
                              transition.submit(
                                `/api/plans/${id}/`,
                                { status: "in_progress", revision: plan.revision },
                                "PATCH",
                              )
                            }
                          >
                            Activar plan
                            <Icon name="arrow" size={16} />
                          </button>
                        </>
                      )}
                      {plan.status === "in_progress" && (
                        <button
                          className="button secondary"
                          disabled={transition.busy}
                          onClick={() =>
                            transition.submit(
                              `/api/plans/${id}/`,
                              { status: "in_review", revision: plan.revision },
                              "PATCH",
                            )
                          }
                        >
                          Pasar a revisión
                        </button>
                      )}
                      {plan.status === "in_review" && (
                        <button
                          className="button secondary"
                          disabled={transition.busy}
                          onClick={() =>
                            transition.submit(
                              `/api/plans/${id}/`,
                              { status: "in_progress", revision: plan.revision },
                              "PATCH",
                            )
                          }
                        >
                          Continuar en progreso
                        </button>
                      )}
                    </div>
                  )}
                </section>
                <div className="result-note">
                  <Icon name="trend" />
                  <h3>Resultados con contexto</h3>
                  <p>
                    El cumplimiento se calcula a partir de las revisiones y las
                    reglas de cada indicador.
                  </p>
                  <Badge status={plan.evaluation.result} />
                </div>
              </aside>
            </div>
            {modal?.type === "metric" && (
              <MetricForm
                plan={plan}
                metric={modal.metric}
                done={done}
                close={() => setModal(null)}
              />
            )}
            {modal?.type === "action" && (
              <ActionForm
                plan={plan}
                action={modal.action}
                done={done}
                close={() => setModal(null)}
              />
            )}
            {modal?.type === "review" && (
              <ReviewForm
                plan={plan}
                user={user}
                done={done}
                close={() => setModal(null)}
              />
            )}
            {modal?.type === "close" && (
              <CloseForm plan={plan} done={done} close={() => setModal(null)} />
            )}
          </>
        );
      }}
    </Resource>
  );
}
