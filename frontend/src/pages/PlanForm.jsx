import React, { useEffect, useState } from "react";
import { api } from "../services/api.js";
import {
  Badge,
  Empty,
  ErrorState,
  Field,
  FormActions,
  FormError,
  Icon,
  PageHeading,
  Pagination,
  Resource,
  SearchBox,
  date,
  planUrl,
  sellerUrl,
  useMutation,
  useResource,
  value,
} from "../components/ui.jsx";

function RecordPicker({
  label,
  url,
  chosen,
  onSelect,
  render = (item) => item.name,
}) {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const resource = useResource(
    `${url}?${new URLSearchParams({ search, page })}`,
  );
  return (
    <div className="record-picker">
      <label className="picker-label">{label} *</label>
      {chosen && (
        <div className="selected-record">
          <Icon name="check" size={17} />
          {render(chosen)}
        </div>
      )}
      <SearchBox
        placeholder={`Buscar ${label.toLowerCase()}…`}
        onSearch={(text) => {
          setSearch(text);
          setPage(1);
        }}
      />
      <Resource resource={resource}>
        {(data) => (
          <>
            <div className="picker-options">
              {data.results.map((item) => (
                <button
                  type="button"
                  aria-pressed={chosen?.id === item.id}
                  className={chosen?.id === item.id ? "selected" : ""}
                  key={item.id}
                  onClick={() => onSelect(item)}
                >
                  {render(item)}
                  <Icon
                    name={chosen?.id === item.id ? "check" : "plus"}
                    size={15}
                  />
                </button>
              ))}
            </div>
            {!data.results.length && (
              <p className="muted">Sin coincidencias.</p>
            )}
            <Pagination data={data} page={page} setPage={setPage} />
          </>
        )}
      </Resource>
    </div>
  );
}

export function PlanForm({ user, params, existing, onSaved }) {
  const sellerId = existing?.seller || params.get("seller");
  const [selectedSeller, setSelectedSeller] = useState(null);
  const [responsible, setResponsible] = useState({
    id: existing?.responsible || user.id,
    name: existing?.responsible_name || user.name,
  });
  const [form, setForm] = useState(
    existing
      ? Object.fromEntries(
          [
            "title",
            "problem",
            "period_start",
            "period_end",
            "root_cause",
            "evidence",
            "objective",
            "due_date",
            "next_review_on",
          ].map((key) => [key, existing[key] || ""]),
        )
      : {
          title: "",
          problem: "",
          root_cause: "",
          evidence: "",
          objective: "",
          period_start: "",
          period_end: "",
          due_date: "",
          next_review_on: "",
        },
  );
  const [selected, setSelected] = useState([]);
  const [metricPage, setMetricPage] = useState(1);
  const [initError, setInitError] = useState(null);
  const metricResource = useResource(
    !existing && selectedSeller
      ? `/api/metrics/?seller=${selectedSeller.id}&page=${metricPage}`
      : null,
  );
  const mutation = useMutation((result) => {
    if (onSaved) onSaved(result);
    else location.hash = planUrl(result.id);
  });
  useEffect(() => {
    if (!sellerId) return;
    const controller = new AbortController();
    api(`/api/sellers/${sellerId}/`, { signal: controller.signal })
      .then(setSelectedSeller)
      .catch((error) => {
        if (error.name !== "AbortError") setInitError(error);
      });
    return () => controller.abort();
  }, [sellerId]);
  useEffect(() => {
    const id = params.get("metric");
    if (!id || existing) return;
    const controller = new AbortController();
    api(`/api/metrics/${id}/`, { signal: controller.signal })
      .then((metric) => {
        if (String(metric.seller) !== String(sellerId)) return;
        setSelected([{ baseline: metric.id, target_value: "", metric }]);
        setForm((f) => ({
          ...f,
          period_start: metric.period_start,
          period_end: metric.period_end,
        }));
      })
      .catch((error) => {
        if (error.name !== "AbortError") setInitError(error);
      });
    return () => controller.abort();
  }, [sellerId, existing, params.get("metric")]);
  const change = (name) => ({
    value: form[name],
    onChange: (e) => setForm((f) => ({ ...f, [name]: e.target.value })),
    errors: mutation.error?.fields,
    name,
  });
  const chooseMetric = (metric) => {
    if (selected.some((m) => m.baseline === metric.id)) return;
    if (!selected.length)
      setForm((f) => ({
        ...f,
        period_start: metric.period_start,
        period_end: metric.period_end,
      }));
    setSelected([
      ...selected,
      { baseline: metric.id, target_value: "", metric },
    ]);
  };
  const submit = (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      responsible: responsible.id,
      next_review_on: form.next_review_on || null,
    };
    if (!existing)
      Object.assign(payload, {
        seller: selectedSeller?.id || null,
        metrics: selected.map(({ baseline, target_value }) => ({
          baseline,
          target_value,
        })),
      });
    mutation.submit(
      existing ? `/api/plans/${existing.id}/` : "/api/plans/",
      payload,
      existing ? "PATCH" : "POST",
    );
  };
  if (initError) return <ErrorState error={initError} />;
  return (
    <>
      <a
        className="back-link"
        href={
          existing
            ? planUrl(existing.id)
            : sellerId
              ? sellerUrl(sellerId)
              : "#/plans"
        }
      >
        ←{" "}
        {existing
          ? "Volver al plan"
          : sellerId
            ? "Volver al vendedor"
            : "Volver a planes"}
      </a>
      <PageHeading
        eyebrow={existing ? `PLAN #${existing.id}` : "NUEVO PLAN"}
        title={
          existing
            ? "Editar diagnóstico y seguimiento"
            : "Cada mejora empieza con un plan"
        }
        description="Define el problema, concreta el objetivo y organiza el seguimiento. Los campos con * son obligatorios."
      />
      <ol className="stepper form-stepper">
        <li>
          <span>1</span>Diagnóstico
        </li>
        <li>
          <span>2</span>Indicadores y objetivos
        </li>
        <li>
          <span>3</span>Responsable y plazos
        </li>
      </ol>
      <form className="plan-form" onSubmit={submit}>
        <FormError error={mutation.error} />
        <fieldset disabled={mutation.busy}>
          <section className="panel form-panel">
            <div className="section-number">01</div>
            <div className="form-section-body">
              <h2>Entender el problema</h2>
              <p className="muted">
                Un diagnóstico concreto ayuda a definir acciones que funcionan.
              </p>
              {sellerId ? (
                <div className="selected-record">
                  <Icon name="sellers" />
                  {selectedSeller
                    ? `${selectedSeller.name} · ${selectedSeller.reference}`
                    : "Cargando vendedor…"}
                </div>
              ) : (
                <RecordPicker
                  label="Vendedor"
                  url="/api/sellers/"
                  chosen={selectedSeller}
                  render={(s) => `${s.name} · ${s.reference}`}
                  onSelect={(s) => {
                    setSelectedSeller(s);
                    setSelected([]);
                    setMetricPage(1);
                    setForm((f) => ({
                      ...f,
                      period_start: "",
                      period_end: "",
                    }));
                  }}
                />
              )}
              <Field
                label="Título del plan"
                required
                maxLength={200}
                placeholder="Ej. Reducir las incidencias en los envíos"
                {...change("title")}
              />
              <div className="form-grid">
                <Field
                  label="Problema identificado"
                  required
                  {...change("problem")}
                >
                  <textarea
                    rows="3"
                    placeholder="Qué ocurre y cómo afecta al vendedor"
                  />
                </Field>
                <Field label="Causa raíz" required {...change("root_cause")}>
                  <textarea
                    rows="3"
                    placeholder="Qué proceso o control está fallando"
                  />
                </Field>
              </div>
              <Field
                label="Evidencia del diagnóstico"
                required
                {...change("evidence")}
              >
                <textarea
                  rows="2"
                  placeholder="Datos, muestras o referencias que sustentan el diagnóstico"
                />
              </Field>
              <Field
                label="Objetivo de mejora"
                required
                {...change("objective")}
              >
                <textarea
                  rows="2"
                  placeholder="Describe el resultado que quieres conseguir"
                />
              </Field>
            </div>
          </section>
          <section className="panel form-panel">
            <div className="section-number">02</div>
            <div className="form-section-body">
              <h2>Medir la mejora</h2>
              <p className="muted">
                Selecciona uno o varios indicadores del mismo periodo. Django
                valida la dirección de mejora y el objetivo.
              </p>
              {!existing && (
                <>
                  {selectedSeller ? (
                    <Resource resource={metricResource}>
                      {(data) => (
                        <>
                          {data.results.length ? (
                            <div className="baseline-options">
                              {data.results.map((m) => (
                                <div className="baseline-option" key={m.id}>
                                  <div>
                                    <strong>{m.label}</strong>
                                    <small>
                                      {m.channel} · {date(m.period_start)} —{" "}
                                      {date(m.period_end)}
                                    </small>
                                    <Badge status={m.classification} />
                                  </div>
                                  <strong>{value(m.value, m.unit)}</strong>
                                  <button
                                    className="button secondary compact"
                                    type="button"
                                    disabled={selected.some(
                                      (s) => s.baseline === m.id,
                                    )}
                                    onClick={() => chooseMetric(m)}
                                  >
                                    {selected.some((s) => s.baseline === m.id)
                                      ? "Añadido"
                                      : "Añadir"}
                                    <Icon name="plus" size={15} />
                                  </button>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <Empty title="Sin observaciones iniciales">
                              Este vendedor necesita indicadores registrados
                              antes de crear un plan.
                            </Empty>
                          )}
                          <Pagination
                            data={data}
                            page={metricPage}
                            setPage={setMetricPage}
                          />
                        </>
                      )}
                    </Resource>
                  ) : (
                    <p className="info-note">
                      Selecciona primero un vendedor para consultar sus
                      indicadores.
                    </p>
                  )}
                  {selected.map((m, index) => (
                    <div className="target-row" key={m.baseline}>
                      <div>
                        <strong>{m.metric.label}</strong>
                        <small>
                          {m.metric.channel} · Inicial:{" "}
                          {value(m.metric.value, m.metric.unit)}
                        </small>
                      </div>
                      <Field
                        label={`Objetivo · ${m.metric.unit === "hours" ? "horas" : "%"}`}
                        name="target_value"
                        errors={mutation.error?.fields?.metrics?.[index]}
                        required
                        type="number"
                        step="0.01"
                        value={m.target_value}
                        onChange={(e) =>
                          setSelected(
                            selected.map((item, i) =>
                              i === index
                                ? { ...item, target_value: e.target.value }
                                : item,
                            ),
                          )
                        }
                      />
                      <button
                        type="button"
                        className="icon-button"
                        aria-label={`Quitar ${m.metric.label}`}
                        onClick={() =>
                          setSelected(
                            selected.filter((s) => s.baseline !== m.baseline),
                          )
                        }
                      >
                        <Icon name="close" size={18} />
                      </button>
                    </div>
                  ))}
                </>
              )}
              {existing && (
                <p className="info-note">
                  Los indicadores iniciales y su periodo se conservan para
                  mantener la trazabilidad del plan.
                </p>
              )}
              <div className="form-grid">
                <Field
                  label="Inicio del periodo de referencia"
                  required
                  type="date"
                  readOnly={!!existing}
                  {...change("period_start")}
                />
                <Field
                  label="Fin del periodo de referencia"
                  required
                  type="date"
                  readOnly={!!existing}
                  {...change("period_end")}
                />
              </div>
            </div>
          </section>
          <section className="panel form-panel">
            <div className="section-number">03</div>
            <div className="form-section-body">
              <h2>Organizar el seguimiento</h2>
              <RecordPicker
                label="Responsable del seguimiento"
                url="/api/responsibles/"
                chosen={responsible}
                onSelect={setResponsible}
              />
              <div className="form-grid">
                <Field
                  label="Fecha objetivo del plan"
                  required
                  type="date"
                  {...change("due_date")}
                />
                <Field
                  label="Próxima revisión"
                  type="date"
                  hint="Opcional. No se programará una fecha automáticamente."
                  {...change("next_review_on")}
                />
              </div>
            </div>
          </section>
        </fieldset>
        <div className="form-bottom">
          <p>
            <Icon name="plans" size={17} />
            {existing
              ? "El histórico se conserva al guardar."
              : "Se guardará como borrador. Después podrás añadir las acciones y activarlo."}
          </p>
          <FormActions
            busy={mutation.busy}
            label={existing ? "Guardar cambios" : "Crear borrador"}
          />
        </div>
      </form>
    </>
  );
}
