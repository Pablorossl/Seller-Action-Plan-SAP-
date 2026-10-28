import React, { useEffect, useId, useRef, useState } from "react";
import { api } from "../services/api.js";

export const labels = {
  draft: "Borrador",
  in_progress: "En progreso",
  in_review: "En revisión",
  closed: "Cerrado",
  cancelled: "Cancelado",
  pending: "Pendiente",
  completed: "Completada",
  ok: "Conforme",
  alarm: "Desviación · Alarma",
  suspension_threshold: "Desviación · Umbral de suspensión",
  insufficient_orders: "No evaluable · Pedidos insuficientes",
  not_evaluable: "No evaluable",
  below_reference: "Bajo la referencia",
  achieved: "Objetivo alcanzado",
  not_achieved: "Objetivo no alcanzado",
  on_track: "Evolución favorable",
  at_risk: "En riesgo",
  no_progress: "Sin progreso",
  no_data: "Sin datos suficientes",
};
export const metricLabels = {
  acceptance: "Tasa de aceptación",
  incidents: "Tasa de incidencias",
  tracking: "Seguimiento válido",
  acceptance_hours: "Tiempo de aceptación",
  response_hours: "Tiempo de respuesta",
  nps: "NPS",
  delivery: "Eficiencia de entrega",
};
export const date = (value) =>
  value
    ? new Intl.DateTimeFormat("es-ES", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        timeZone: "Europe/Madrid",
      }).format(new Date(value.length === 10 ? `${value}T12:00:00Z` : value))
    : "Sin programar";
export const value = (number, unit) =>
  number == null
    ? "Sin datos"
    : `${Number(number).toLocaleString("es-ES", { maximumFractionDigits: 2 })} ${unit === "hours" ? "h" : "%"}`;
export const planUrl = (id) => `#/plans/${id}`;
export const sellerUrl = (id) => `#/sellers/${id}`;
export const newPlanUrl = (seller, metric) =>
  `#/plans/new${seller ? `?seller=${seller}${metric ? `&metric=${metric}` : ""}` : ""}`;
export const finalPlan = (plan) =>
  ["closed", "cancelled"].includes(plan.status);

const paths = {
  dashboard: (
    <>
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
    </>
  ),
  sellers: (
    <>
      <path d="m3 9 2-6h14l2 6M4 10v10h16V10M9 20v-7h6v7" />
      <path d="M3 9c0 4 5 4 5 0 0 4 8 4 8 0 0 4 5 4 5 0" />
    </>
  ),
  plans: (
    <>
      <rect x="5" y="4" width="14" height="17" rx="2" />
      <path d="M9 4V2h6v2M9 10h6M9 14h6M9 18h3" />
    </>
  ),
  arrow: <path d="M5 12h14m-5-5 5 5-5 5" />,
  plus: <path d="M12 5v14M5 12h14" />,
  search: (
    <>
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="m16 16 4.5 4.5" />
    </>
  ),
  clock: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </>
  ),
  check: <path d="m5 12 4 4L19 6" />,
  close: <path d="m6 6 12 12M18 6 6 18" />,
  alert: (
    <>
      <path d="m12 3 10 17H2L12 3Z" />
      <path d="M12 9v4m0 3v1" />
    </>
  ),
  calendar: (
    <>
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M7 2v6M17 2v6M3 11h18" />
    </>
  ),
  logout: (
    <>
      <path d="M9 3H4v18h5M10 12h11m-4-4 4 4-4 4" />
    </>
  ),
  menu: <path d="M4 6h16M4 12h16M4 18h16" />,
  trend: (
    <>
      <path d="m3 17 6-6 4 4 8-10M15 5h6v6" />
    </>
  ),
};
export function Icon({ name, size = 20 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name] || paths.plans}
    </svg>
  );
}
export function Badge({ status, children }) {
  return (
    <span className={`badge badge-${status}`}>
      <span className="status-dot" />
      {children || labels[status] || status}
    </span>
  );
}
export function Avatar({ name = "", small = false }) {
  return (
    <span className={`avatar ${small ? "small" : ""}`} aria-hidden="true">
      {name
        .split(/\s+/)
        .map((s) => s[0])
        .slice(0, 2)
        .join("")
        .toUpperCase()}
    </span>
  );
}
export function PageHeading({ eyebrow, title, description, children }) {
  return (
    <header className="page-heading">
      <div>
        {eyebrow && <div className="eyebrow">{eyebrow}</div>}
        <h1 tabIndex="-1">{title}</h1>
        {description && <p>{description}</p>}
      </div>
      <div className="heading-actions">{children}</div>
    </header>
  );
}
export function Empty({
  title = "Todavía no hay registros",
  children,
  icon = "plans",
}) {
  return (
    <div className="empty">
      <span className="empty-icon">
        <Icon name={icon} size={26} />
      </span>
      <h3>{title}</h3>
      <div>{children}</div>
    </div>
  );
}
export function Loading() {
  return (
    <div className="loading" role="status">
      <span className="spinner" /> Cargando información…
    </div>
  );
}
export function ErrorState({ error, retry }) {
  return (
    <div className="error-state" role="alert">
      <Icon name="alert" />
      <div>
        <strong>{error.message}</strong>
        {error.status === 403 && (
          <p>
            <a
              href={`/accounts/login/?next=${encodeURIComponent(location.pathname + location.hash)}`}
            >
              Iniciar sesión con una cuenta autorizada
            </a>
          </p>
        )}
        {retry && (
          <button className="button secondary" onClick={retry}>
            Volver a intentar
          </button>
        )}
      </div>
    </div>
  );
}
export function useResource(url) {
  const [version, setVersion] = useState(0);
  const [state, setState] = useState({
    data: null,
    loading: true,
    error: null,
  });
  useEffect(() => {
    if (!url) {
      setState({ data: null, loading: false, error: null });
      return;
    }
    const controller = new AbortController();
    setState({ data: null, loading: true, error: null });
    api(url, { signal: controller.signal })
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((error) => {
        if (error.name !== "AbortError")
          setState({ data: null, loading: false, error });
      });
    return () => controller.abort();
  }, [url, version]);
  return {
    ...state,
    reload: () => setVersion((v) => v + 1),
    setData: (data) => setState({ data, loading: false, error: null }),
  };
}
export function Resource({ resource, children }) {
  return resource.loading ? (
    <Loading />
  ) : resource.error ? (
    <ErrorState error={resource.error} retry={resource.reload} />
  ) : resource.data ? (
    children(resource.data)
  ) : null;
}
export function Pagination({ data, page, setPage }) {
  return (
    <div className="pagination">
      <span>
        {data.count} {data.count === 1 ? "registro" : "registros"}
      </span>
      <div>
        <button
          className="button secondary compact"
          type="button"
          disabled={!data.previous}
          onClick={() => setPage(page - 1)}
        >
          Anterior
        </button>
        <span>Página {page}</span>
        <button
          className="button secondary compact"
          type="button"
          disabled={!data.next}
          onClick={() => setPage(page + 1)}
        >
          Siguiente
        </button>
      </div>
    </div>
  );
}
export function SearchBox({
  onSearch,
  placeholder = "Buscar por nombre o identificador…",
  initial = "",
}) {
  const [text, setText] = useState(initial);
  return (
    <div className="search-box" role="search">
      <Icon name="search" />
      <input
        aria-label={placeholder}
        placeholder={placeholder}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            e.preventDefault();
            onSearch(text);
          }
        }}
      />
      <button type="button" onClick={() => onSearch(text)}>
        Buscar
      </button>
      {text && (
        <button
          type="button"
          aria-label="Limpiar búsqueda"
          onClick={() => {
            setText("");
            onSearch("");
          }}
        >
          <Icon name="close" size={16} />
        </button>
      )}
    </div>
  );
}
export function messages(errors) {
  if (!errors) return "";
  if (typeof errors === "string") return errors;
  if (Array.isArray(errors)) return errors.map(messages).join(" ");
  return Object.entries(errors)
    .map(
      ([key, val]) =>
        `${/^\d+$/.test(key) ? `Indicador ${Number(key) + 1}` : key}: ${messages(val)}`,
    )
    .join(" ");
}
export function Field({
  label,
  name,
  errors,
  hint,
  children,
  required = false,
  ...props
}) {
  const id = useId();
  const error = messages(errors?.[name]);
  const component = children ? (
    React.cloneElement(children, {
      id,
      name,
      required,
      "aria-invalid": !!error,
      "aria-describedby": error || hint ? `${id}-help` : undefined,
      ...props,
    })
  ) : (
    <input
      id={id}
      name={name}
      required={required}
      aria-invalid={!!error}
      aria-describedby={error || hint ? `${id}-help` : undefined}
      {...props}
    />
  );
  return (
    <div className={`field ${props.className || ""}`}>
      <label htmlFor={id}>
        {label}
        {required && <span aria-hidden="true"> *</span>}
      </label>
      {component}
      {(error || hint) && (
        <small className={error ? "field-error" : ""} id={`${id}-help`}>
          {error || hint}
        </small>
      )}
    </div>
  );
}
export function FormError({ error }) {
  const ref = useRef();
  useEffect(() => {
    if (error) ref.current?.focus();
  }, [error]);
  return error ? (
    <div ref={ref} tabIndex="-1" className="form-error" role="alert">
      {error.message}
      <p>{messages(error.fields)}</p>
    </div>
  ) : null;
}
export function Modal({ title, children, close, busy = false }) {
  const ref = useRef();
  const titleId = useId();
  useEffect(() => {
    const previous = document.activeElement;
    const dialog = ref.current;
    dialog.showModal();
    return () => {
      dialog.close();
      if (previous?.isConnected) previous.focus({ preventScroll: true });
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className="modal"
      aria-labelledby={titleId}
      onCancel={(e) => {
        e.preventDefault();
        if (!busy) close();
      }}
    >
      <div className="modal-head">
        <h2 id={titleId}>{title}</h2>
        <button
          className="icon-button"
          disabled={busy}
          aria-label="Cerrar formulario"
          onClick={close}
        >
          <Icon name="close" />
        </button>
      </div>
      {children}
    </dialog>
  );
}
export function useMutation(onSuccess) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const lock = useRef(false);
  const attempt = useRef(null);
  async function submit(url, data, method = "POST") {
    if (lock.current) return;
    lock.current = true;
    setBusy(true);
    setError(null);
    try {
      // Un reintento con los mismos datos conserva su clave, incluso si se perdió
      // la respuesta. Modificar el formulario inicia una operación diferente.
      const signature = JSON.stringify([url, method, data]);
      if (attempt.current?.signature !== signature)
        attempt.current = { signature, key: crypto.randomUUID() };
      const result = await api(url, { method, data, idempotencyKey: attempt.current.key });
      attempt.current = null;
      onSuccess(result);
    } catch (err) {
      setError(err);
    } finally {
      lock.current = false;
      setBusy(false);
    }
  }
  return { busy, error, submit };
}
export function FormActions({ busy, close, label = "Guardar cambios" }) {
  return (
    <div className="form-actions">
      {close && (
        <button
          className="button secondary"
          type="button"
          disabled={busy}
          onClick={close}
        >
          Cancelar
        </button>
      )}
      <button className="button primary" type="submit" disabled={busy}>
        {busy ? "Guardando…" : label}
        <Icon name="arrow" size={17} />
      </button>
    </div>
  );
}
