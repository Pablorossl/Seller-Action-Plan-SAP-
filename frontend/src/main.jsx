import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { setCsrfToken } from "./services/api.js";
import {
  Avatar,
  Empty,
  Icon,
  Resource,
  date,
  useResource,
} from "./components/ui.jsx";
import { Dashboard, Plans, SellerDetail, Sellers } from "./pages/Workspace.jsx";
import { PlanForm } from "./pages/PlanForm.jsx";
import { PlanDetail } from "./pages/PlanDetail.jsx";
import "./styles.css";

function App() {
  const [route, setRoute] = useState(location.hash.slice(1) || "/");
  const [mobileNav, setMobileNav] = useState(false);
  const session = useResource("/api/workspace/");
  useEffect(() => {
    const navigate = () => {
      setRoute(location.hash.slice(1) || "/");
      setMobileNav(false);
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", navigate);
    return () => window.removeEventListener("hashchange", navigate);
  }, []);
  useEffect(() => {
    if (session.data) setCsrfToken(session.data.csrf_token);
  }, [session.data]);
  const [path, query = ""] = route.split("?");
  const params = new URLSearchParams(query);
  const section = path.startsWith("/sellers")
    ? "sellers"
    : path.startsWith("/plans")
      ? "plans"
      : "dashboard";
  const sectionName = {
    dashboard: "Dashboard",
    sellers: "Vendedores",
    plans: "Planes de mejora",
  }[section];
  useEffect(() => {
    document.title = `${sectionName} · Seller Action Plan`;
  }, [sectionName]);
  let page;
  const user = session.data;
  if (user) {
    if (path === "/") page = <Dashboard user={user} />;
    else if (path === "/sellers") page = <Sellers />;
    else if (/^\/sellers\/\d+$/.test(path))
      page = <SellerDetail id={path.split("/")[2]} user={user} />;
    else if (path === "/plans") page = <Plans user={user} params={params} />;
    else if (path === "/plans/new")
      page =
        user.permissions.add_improvementplan &&
        user.permissions.add_planmetric ? (
          <PlanForm user={user} params={params} />
        ) : (
          <Empty title="Acceso denegado">
            Tu cuenta no tiene permiso para crear planes.
          </Empty>
        );
    else if (/^\/plans\/\d+$/.test(path))
      page = <PlanDetail id={path.split("/")[2]} user={user} params={params} />;
    else
      page = (
        <Empty title="Página no encontrada">
          <a href="#/">Volver al dashboard</a>
        </Empty>
      );
  }
  return (
    <div className="app-shell">
      <a
        className="skip-link"
        href="#main-content"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById("main-content").focus();
        }}
      >
        Saltar al contenido
      </a>
      <aside className={`sidebar ${mobileNav ? "is-open" : ""}`}>
        <a className="brand" href="#/">
          <span className="brand-mark">
            <Icon name="trend" size={27} />
          </span>
          <span>
            SAP<small>Seller Action Plan</small>
          </span>
        </a>
        <div className="workspace-label">
          <span className="live-dot" />
          Marketplace workspace
        </div>
        <p className="nav-label">GESTIÓN OPERATIVA</p>
        <nav aria-label="Navegación principal">
          {[
            ["dashboard", "/", "Dashboard"],
            ["sellers", "/sellers", "Vendedores"],
            ["plans", "/plans", "Planes de mejora"],
          ].map(([key, href, text]) => (
            <a
              href={`#${href}`}
              key={key}
              className={section === key ? "active" : ""}
              aria-current={section === key ? "page" : undefined}
            >
              <Icon name={key} />
              {text}
              {section === key && <span className="nav-active-dot" />}
            </a>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-note">
            <span>UNA MEJORA A LA VEZ</span>
            <p>
              Del diagnóstico
              <br />a la acción.
            </p>
            <Icon name="trend" size={24} />
          </div>
          {user && (
            <>
              <div className="user-info">
                <Avatar name={user.name} />
                <div>
                  <strong>{user.name}</strong>
                  <small>Marketplace Agent</small>
                </div>
              </div>
              <form action="/accounts/logout/" method="post">
                <input
                  type="hidden"
                  name="csrfmiddlewaretoken"
                  value={user.csrf_token}
                />
                <button className="logout" type="submit">
                  <Icon name="logout" size={17} />
                  Cerrar sesión
                </button>
              </form>
            </>
          )}
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div>
            <button
              className="icon-button mobile-menu"
              aria-label="Mostrar navegación"
              aria-expanded={mobileNav}
              onClick={() => setMobileNav(!mobileNav)}
            >
              <Icon name="menu" />
            </button>
            <span className="topbar-product">Workspace</span>
            <span className="breadcrumb-separator">/</span>
            <strong>{sectionName}</strong>
          </div>
          <div className="topbar-right">
            <span>
              <Icon name="calendar" size={16} />
              {user ? date(user.today) : "Seller Action Plan"}
            </span>
            <span className="environment-pill">Proyecto independiente</span>
          </div>
        </header>
        <main id="main-content" tabIndex="-1">
          <Resource resource={session}>
            {() => <div key={route}>{page}</div>}
          </Resource>
          <footer className="app-footer">
            <span>
              Seller Action Plan <span className="footer-dot">·</span>{" "}
              Seguimiento con propósito
            </span>
            <span>Sin conexión con Mirakl</span>
          </footer>
        </main>
      </div>
    </div>
  );
}
createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
