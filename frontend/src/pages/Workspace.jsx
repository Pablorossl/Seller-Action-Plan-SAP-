import React, { useState } from "react";
import {
  Avatar,
  Badge,
  Empty,
  Icon,
  PageHeading,
  Pagination,
  Resource,
  SearchBox,
  date,
  labels,
  metricLabels,
  newPlanUrl,
  planUrl,
  sellerUrl,
  useResource,
  value,
} from "../components/ui.jsx";

export function PlanTable({
  plans,
  empty = "No hay planes que coincidan con los filtros",
}) {
  if (!plans.length)
    return (
      <Empty title={empty}>
        Los planes que registres aparecerán aquí con su estado y próxima acción.
      </Empty>
    );
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
            <th scope="col">Plan / vendedor</th>
            <th scope="col">Indicadores</th>
            <th scope="col">Estado</th>
            <th scope="col">Responsable</th>
            <th scope="col">Fecha objetivo</th>
            <th scope="col">
              <span className="sr-only">Acceso</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {plans.map((plan) => (
            <tr key={plan.id}>
              <td>
                <a className="table-title" href={planUrl(plan.id)}>
                  {plan.title}
                </a>
                <a className="muted table-sub" href={sellerUrl(plan.seller)}>
                  {plan.seller_name}
                </a>
                <small>Creado el {date(plan.created_at)}</small>
              </td>
              <td>
                <div className="metric-tags">
                  {plan.metrics.map((m) => (
                    <span key={m.id}>{metricLabels[m.baseline.code]}</span>
                  ))}
                </div>
              </td>
              <td>
                <Badge status={plan.status} />
                {plan.needs_review && (
                  <small className="text-warning">Requiere revisión</small>
                )}
              </td>
              <td>
                <div className="person">
                  <Avatar name={plan.responsible_name} small />
                  {plan.responsible_name}
                </div>
              </td>
              <td>{date(plan.due_date)}</td>
              <td>
                <a
                  className="icon-button"
                  aria-label={`Abrir ${plan.title}`}
                  href={planUrl(plan.id)}
                >
                  <Icon name="arrow" size={18} />
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Dashboard({ user }) {
  const resource = useResource("/api/overview/");
  const canCreate =
    user.permissions.add_improvementplan && user.permissions.add_planmetric;
  return (
    <>
      <PageHeading
        eyebrow="TU ESPACIO DE TRABAJO"
        title={`Hola, ${user.name.split(" ")[0]}`}
        description="Una visión clara de tus vendedores y de lo que necesita atención."
      >
        {canCreate && (
          <a className="button primary" href={newPlanUrl()}>
            <Icon name="plus" size={18} />
            Crear plan de mejora
          </a>
        )}
      </PageHeading>
      <Resource resource={resource}>
        {(data) => (
          <>
            <div className="overview-caption">
              <span className="live-dot" /> Resumen operativo{" "}
              <span>Actualizado al {date(data.today)}</span>
            </div>
            <section className="stats-grid" aria-label="Resumen operativo">
              {[
                [
                  "Vendedores asignados",
                  "sellers",
                  "sellers",
                  "#/sellers",
                  "En tu ámbito de acceso",
                ],
                [
                  "Planes abiertos",
                  "open_plans",
                  "plans",
                  "#/plans?status=open",
                  "Borradores y planes en seguimiento",
                ],
                [
                  "Acciones pendientes",
                  "pending_actions",
                  "check",
                  "#/plans?status=open",
                  "De planes abiertos",
                ],
                [
                  "Acciones vencidas",
                  "overdue_actions",
                  "alert",
                  "#prioridades",
                  "Requieren tu atención",
                ],
                [
                  "Planes por revisar",
                  "needs_review",
                  "clock",
                  "#/plans?review=due",
                  "Según estado o fecha registrada",
                ],
                [
                  "Planes cerrados",
                  "closed_plans",
                  "trend",
                  "#/plans?status=closed",
                  "Con resultado documentado",
                ],
              ].map(([label, key, icon, href, hint]) => (
                <a
                  href={href === "#prioridades" ? undefined : href}
                  onClick={
                    href === "#prioridades"
                      ? (e) => {
                          e.preventDefault();
                          document
                            .getElementById("prioridades")
                            ?.scrollIntoView({ behavior: "smooth" });
                        }
                      : undefined
                  }
                  role={href === "#prioridades" ? "button" : undefined}
                  tabIndex={href === "#prioridades" ? 0 : undefined}
                  onKeyDown={
                    href === "#prioridades"
                      ? (e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            document
                              .getElementById("prioridades")
                              ?.scrollIntoView();
                          }
                        }
                      : undefined
                  }
                  className={`stat ${key === "overdue_actions" && data.counts[key] ? "stat-warning" : ""}`}
                  key={key}
                >
                  <div className="stat-top">
                    <span>{label}</span>
                    <Icon name={icon} />
                  </div>
                  <strong>{data.counts[key]}</strong>
                  <small>{hint}</small>
                </a>
              ))}
            </section>
            <div className="dashboard-columns">
              <section className="panel" id="prioridades">
                <div className="panel-heading">
                  <div>
                    <div className="eyebrow">TU PRÓXIMO PASO</div>
                    <h2>
                      Prioridades de la semana{" "}
                      <span className="count-pill">
                        {data.priorities_count}
                      </span>
                    </h2>
                  </div>
                  <Icon name="calendar" />
                </div>
                <p className="panel-intro">
                  Acciones vencidas y con plazo en los próximos 7 días.
                </p>
                {data.priorities.length ? (
                  <div className="priority-list">
                    {data.priorities.map((item) => (
                      <a
                        className="priority-item"
                        key={item.id}
                        href={`${planUrl(item.plan)}?action=${item.id}`}
                      >
                        <span
                          className={`priority-icon ${item.is_overdue ? "overdue" : ""}`}
                        >
                          <Icon
                            name={item.is_overdue ? "alert" : "clock"}
                            size={19}
                          />
                        </span>
                        <div>
                          <strong>{item.description}</strong>
                          <span>
                            {item.seller_name} · {item.plan_title}
                          </span>
                          <small>
                            {item.responsible} · {labels[item.status]}
                          </small>
                        </div>
                        <div className="priority-date">
                          <Badge status={item.is_overdue ? "alarm" : "pending"}>
                            {item.is_overdue ? "Vencida" : "Próxima"}
                          </Badge>
                          <small>{date(item.due_date)}</small>
                        </div>
                        <Icon name="arrow" size={17} />
                      </a>
                    ))}
                  </div>
                ) : (
                  <Empty title="Todo al día" icon="check">
                    No hay acciones vencidas ni con plazo en los próximos siete
                    días.
                  </Empty>
                )}
                {data.priorities_count > 10 && (
                  <a className="panel-link" href="#/plans?status=open">
                    Ver planes abiertos para consultar el resto{" "}
                    <Icon name="arrow" size={16} />
                  </a>
                )}
              </section>
              <aside className="dashboard-aside">
                <section className="focus-panel">
                  <div className="eyebrow">SEGUIMIENTO DE CALIDAD</div>
                  <div className="focus-number">
                    {data.counts.sellers_with_deviations}
                    <Icon name="trend" size={36} />
                  </div>
                  <h2>Vendedores con desviaciones registradas</h2>
                  <p>
                    Según la última observación de cada indicador y canal.
                    Consulta siempre su periodo de referencia.
                  </p>
                  <a className="button dark" href="#/sellers">
                    Revisar vendedores
                    <Icon name="arrow" size={17} />
                  </a>
                </section>
                <section className="panel review-panel">
                  <div className="panel-heading">
                    <h2>Por revisar</h2>
                    <Icon name="clock" />
                  </div>
                  {data.reviews.length ? (
                    data.reviews.map((plan) => (
                      <a
                        className="review-item"
                        key={plan.id}
                        href={planUrl(plan.id)}
                      >
                        <span>
                          <strong>{plan.title}</strong>
                          <small>{plan.seller_name}</small>
                          <small>
                            {plan.next_review_on
                              ? date(plan.next_review_on)
                              : "Estado: en revisión · Sin fecha programada"}
                          </small>
                        </span>
                        <Icon name="arrow" size={16} />
                      </a>
                    ))
                  ) : (
                    <p className="muted">No hay revisiones pendientes.</p>
                  )}
                  {data.reviews_count > 5 && (
                    <a href="#/plans?review=due">Ver todas las revisiones</a>
                  )}
                </section>
              </aside>
            </div>
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <div className="eyebrow">CONTINÚA DONDE LO DEJASTE</div>
                  <h2>Planes recientes</h2>
                </div>
                {user.permissions.view_improvementplan && (
                  <a className="text-link" href="#/plans">
                    Ver todos
                    <Icon name="arrow" size={16} />
                  </a>
                )}
              </div>
              <PlanTable
                plans={data.recent_plans}
                empty="Tu próximo plan empieza aquí"
              />
            </section>
            {!!data.deviations.length && (
              <section className="panel">
                <div className="panel-heading">
                  <h2>Desviaciones registradas</h2>
                  <span className="muted">
                    Hasta 10 observaciones recientes
                  </span>
                </div>
                <div
                  className="table-wrap"
                  tabIndex={0}
                  role="region"
                  aria-label="Tabla de datos desplazable"
                >
                  <table>
                    <thead>
                      <tr>
                        <th>Vendedor</th>
                        <th>Indicador / canal</th>
                        <th>Valor</th>
                        <th>Periodo</th>
                        <th>Evaluación</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.deviations.map((m) => (
                        <tr key={m.id}>
                          <td>
                            <a href={sellerUrl(m.seller)}>{m.seller_name}</a>
                          </td>
                          <td>
                            {m.label}
                            <small>{m.channel}</small>
                          </td>
                          <td>{value(m.value, m.unit)}</td>
                          <td>
                            {date(m.period_start)} – {date(m.period_end)}
                          </td>
                          <td>
                            <Badge status={m.classification} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}
          </>
        )}
      </Resource>
    </>
  );
}

export function Sellers() {
  const [search, setSearch] = useState("");
  const [active, setActive] = useState("");
  const [page, setPage] = useState(1);
  const resource = useResource(
    `/api/sellers/?${new URLSearchParams({ search, active_plans: active, page })}`,
  );
  return (
    <>
      <PageHeading
        eyebrow="DIRECTORIO"
        title="Vendedores"
        description="Conoce su situación, consulta sus indicadores y coordina la mejora."
      />
      <section className="panel">
        <div className="toolbar">
          <SearchBox
            onSearch={(text) => {
              setSearch(text);
              setPage(1);
            }}
          />
          <label className="filter-label">
            Planes
            <select
              value={active}
              onChange={(e) => {
                setActive(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Todos los vendedores</option>
              <option value="1">Con planes abiertos</option>
              <option value="0">Sin planes abiertos</option>
            </select>
          </label>
        </div>
        <Resource resource={resource}>
          {(data) => (
            <>
              {data.results.length ? (
                <div
                  className="table-wrap"
                  tabIndex={0}
                  role="region"
                  aria-label="Tabla de datos desplazable"
                >
                  <table>
                    <thead>
                      <tr>
                        <th>Vendedor</th>
                        <th>Identificador</th>
                        <th>Agente asignado</th>
                        <th>Planes abiertos</th>
                        <th>Registrado</th>
                        <th>
                          <span className="sr-only">Acceso</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.results.map((s) => (
                        <tr key={s.id}>
                          <td>
                            <div className="person">
                              <Avatar name={s.name} />
                              <a className="table-title" href={sellerUrl(s.id)}>
                                {s.name}
                              </a>
                            </div>
                          </td>
                          <td>
                            <code>{s.reference}</code>
                          </td>
                          <td>{s.owner_name}</td>
                          <td>
                            <span className="count-pill">{s.open_plans}</span>
                          </td>
                          <td>{date(s.created_at)}</td>
                          <td>
                            <a className="text-link" href={sellerUrl(s.id)}>
                              Ver ficha
                              <Icon name="arrow" size={16} />
                            </a>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <Empty
                  title={
                    search || active
                      ? "No se encontraron vendedores"
                      : "Aún no tienes vendedores asignados"
                  }
                  icon="sellers"
                >
                  {search || active
                    ? "Prueba otro nombre, identificador o filtro."
                    : "Los vendedores asignados a tu cuenta aparecerán aquí."}
                </Empty>
              )}
              <Pagination data={data} page={page} setPage={setPage} />
            </>
          )}
        </Resource>
      </section>
    </>
  );
}

export function Plans({ params, user }) {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState(params.get("status") || "");
  const [page, setPage] = useState(1);
  const resource = useResource(
    `/api/plans/?${new URLSearchParams({ search, status, page, ...(params.get("seller") ? { seller: params.get("seller") } : {}), ...(params.get("review") ? { review: params.get("review") } : {}) })}`,
  );
  return (
    <>
      <PageHeading
        eyebrow="DE LA DESVIACIÓN A LA MEJORA"
        title="Planes de mejora"
        description={
          params.get("review")
            ? "Planes en revisión o con una revisión programada para hoy o antes."
            : "Diagnósticos, compromisos y resultados, en un mismo lugar."
        }
      >
        {user.permissions.add_improvementplan &&
          user.permissions.add_planmetric && (
            <a
              className="button primary"
              href={newPlanUrl(params.get("seller"))}
            >
              <Icon name="plus" size={18} />
              Crear plan de mejora
            </a>
          )}
      </PageHeading>
      <section className="panel">
        <div className="toolbar">
          <SearchBox
            placeholder="Buscar plan, vendedor o responsable…"
            onSearch={(text) => {
              setSearch(text);
              setPage(1);
            }}
          />
          <label className="filter-label">
            Estado
            <select
              value={status}
              onChange={(e) => {
                setStatus(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Todos los estados</option>
              <option value="open">Todos los abiertos</option>
              {["draft", "in_progress", "in_review", "closed", "cancelled"].map(
                (s) => (
                  <option key={s} value={s}>
                    {labels[s]}
                  </option>
                ),
              )}
            </select>
          </label>
          {(params.get("review") || params.get("seller")) && (
            <a className="text-link" href="#/plans">
              Quitar filtro contextual
            </a>
          )}
        </div>
        <Resource resource={resource}>
          {(data) => (
            <>
              <PlanTable plans={data.results} />
              <Pagination data={data} page={page} setPage={setPage} />
            </>
          )}
        </Resource>
      </section>
    </>
  );
}

export function SellerDetail({ id, user }) {
  const seller = useResource(`/api/sellers/${id}/`);
  const [metricPage, setMetricPage] = useState(1);
  const [planPage, setPlanPage] = useState(1);
  const [history, setHistory] = useState(false);
  const [allMetrics, setAllMetrics] = useState(false);
  const metrics = useResource(
    `/api/metrics/?seller=${id}&latest=${allMetrics ? "0" : "1"}&page=${metricPage}`,
  );
  const plans = useResource(
    user.permissions.view_improvementplan
      ? `/api/plans/?seller=${id}&status=${history ? "final" : "open"}&page=${planPage}`
      : null,
  );
  const canCreate =
    user.permissions.add_improvementplan && user.permissions.add_planmetric;
  return (
    <Resource resource={seller}>
      {(s) => (
        <>
          <a className="back-link" href="#/sellers">
            ← Volver a vendedores
          </a>
          <PageHeading
            eyebrow={`VENDEDOR · ${s.reference}`}
            title={s.name}
            description={`Agente asignado: ${s.owner_name} · Registrado el ${date(s.created_at)}`}
          >
            {canCreate && (
              <a className="button primary" href={newPlanUrl(id)}>
                <Icon name="plus" size={18} />
                Crear plan de mejora
              </a>
            )}
          </PageHeading>
          <section className="panel">
            <div className="panel-heading">
              <div>
                <h2>Indicadores de calidad</h2>
                <p className="muted">
                  Observaciones registradas por canal. Consulta el periodo antes
                  de interpretar el resultado.
                </p>
              </div>
              <label className="check-label">
                <input
                  type="checkbox"
                  checked={allMetrics}
                  onChange={(e) => {
                    setAllMetrics(e.target.checked);
                    setMetricPage(1);
                  }}
                />
                Ver histórico de observaciones
              </label>
            </div>
            <Resource resource={metrics}>
              {(data) => (
                <>
                  {data.results.length ? (
                    <div
                      className="table-wrap"
                      tabIndex={0}
                      role="region"
                      aria-label="Tabla de datos desplazable"
                    >
                      <table>
                        <thead>
                          <tr>
                            <th>Indicador</th>
                            <th>Valor</th>
                            <th>Periodo de referencia</th>
                            <th>Pedidos</th>
                            <th>Evaluación</th>
                            {canCreate && (
                              <th>
                                <span className="sr-only">Acciones</span>
                              </th>
                            )}
                          </tr>
                        </thead>
                        <tbody>
                          {data.results.map((m) => (
                            <tr key={m.id}>
                              <td>
                                <strong>{m.label}</strong>
                                <small>
                                  {m.channel} · Política v{m.policy_version}
                                </small>
                              </td>
                              <td className="metric-value">
                                {value(m.value, m.unit)}
                              </td>
                              <td>
                                {date(m.period_start)}
                                <small>hasta {date(m.period_end)}</small>
                              </td>
                              <td>{m.order_count ?? "Sin datos"}</td>
                              <td>
                                <Badge status={m.classification} />
                              </td>
                              {canCreate && (
                                <td>
                                  <a
                                    className="text-link"
                                    href={newPlanUrl(id, m.id)}
                                  >
                                    Crear plan
                                    <Icon name="plus" size={16} />
                                  </a>
                                </td>
                              )}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <Empty title="Sin indicadores disponibles" icon="trend">
                      Aún no se han registrado observaciones para este vendedor.
                      Se necesita una observación inicial para crear un plan.
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
            {!!s.missing_indicators?.length && (
              <div className="missing-indicators">
                <strong>Sin datos disponibles</strong>
                <div className="metric-tags">
                  {s.missing_indicators.map((m) => (
                    <span key={m.code}>{m.label}</span>
                  ))}
                </div>
              </div>
            )}
            <div className="info-note">
              SAP muestra datos registrados; no existe sincronización en tiempo
              real con Mirakl. Un umbral de suspensión es informativo: SAP no
              suspende tiendas.
            </div>
          </section>
          <section className="panel">
            <div className="panel-heading">
              <div className="tabs" aria-label="Planes del vendedor">
                <button
                  className={!history ? "active" : ""}
                  onClick={() => {
                    setHistory(false);
                    setPlanPage(1);
                  }}
                >
                  Planes activos{" "}
                  <span className="count-pill">{s.open_plans}</span>
                </button>
                <button
                  className={history ? "active" : ""}
                  onClick={() => {
                    setHistory(true);
                    setPlanPage(1);
                  }}
                >
                  Historial y resultados
                </button>
              </div>
            </div>
            {user.permissions.view_improvementplan ? (
              <Resource resource={plans}>
                {(data) => (
                  <>
                    {data.results.length ? (
                      <div className="seller-plans">
                        {data.results.map((p) => (
                          <article key={p.id}>
                            <div>
                              <Badge status={p.status} />
                              <a href={planUrl(p.id)}>
                                <h3>{p.title}</h3>
                              </a>
                              <p>{p.objective}</p>
                              <small>
                                {history
                                  ? labels[p.closure_evaluation.result]
                                  : p.next_action
                                    ? `Próxima acción: ${p.next_action.description} · ${date(p.next_action.due_date)}`
                                    : "Sin acciones pendientes"}
                              </small>
                            </div>
                            <a
                              className="button secondary"
                              href={planUrl(p.id)}
                            >
                              Ver plan
                              <Icon name="arrow" size={16} />
                            </a>
                          </article>
                        ))}
                      </div>
                    ) : (
                      <Empty
                        title={
                          history
                            ? "Sin planes finalizados"
                            : "Sin planes activos"
                        }
                      >
                        Aquí podrás consultar las medidas adoptadas y sus
                        resultados.
                      </Empty>
                    )}
                    <Pagination
                      data={data}
                      page={planPage}
                      setPage={setPlanPage}
                    />
                  </>
                )}
              </Resource>
            ) : (
              <p className="info-note">
                Tu cuenta no tiene permiso de consulta de planes.
              </p>
            )}
          </section>
        </>
      )}
    </Resource>
  );
}
