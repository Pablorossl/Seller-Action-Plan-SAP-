import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { setCsrfToken } from "./services/api.js";
import {
  Empty,
  Icon,
  Resource,
  date,
  useResource,
} from "./components/ui.jsx";
import { Dashboard, Plans, SellerDetail, Sellers } from "./pages/Workspace.jsx";
import { PlanForm } from "./pages/PlanForm.jsx";
import { PlanDetail } from "./pages/PlanDetail.jsx";
import { UnsavedChangesProvider, useLeaveConfirmation } from "./components/UnsavedChanges.jsx";
import { installHashNavigation } from "./services/navigation.js";
import { useRouteFocus } from "./components/RouteFocus.jsx";
import { Sidebar } from "./components/Sidebar.jsx";
import "./styles.css";

function App() {
  const requestLeave = useLeaveConfirmation();
  const [route, setRoute] = useState(location.hash.slice(1) || "/");
  const [mobileNav, setMobileNav] = useState(false);
  const [isMobile, setIsMobile] = useState(() => window.matchMedia("(max-width: 760px)").matches);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => window.matchMedia("(max-width: 1199px)").matches);
  const menuButton = useRef(null);
  const sidebar = useRef(null);
  const content = useRef(null);
  useRouteFocus(route, content);
  const closeMenu = () => {
    setMobileNav(false);
    menuButton.current?.focus();
  };
  useEffect(() => {
    const mobile = window.matchMedia("(max-width: 760px)");
    const tablet = window.matchMedia("(max-width: 1199px)");
    const resize = () => {
      const focused = document.activeElement;
      const inSidebar = sidebar.current?.contains(focused);
      setIsMobile(mobile.matches);
      setSidebarCollapsed(tablet.matches);
      setMobileNav(false);
      if (mobile.matches && inSidebar) requestAnimationFrame(() => menuButton.current?.focus());
      else if (!mobile.matches && focused === menuButton.current)
        requestAnimationFrame(() => sidebar.current?.querySelector("nav a[aria-current]")?.focus());
    };
    mobile.addEventListener("change", resize);
    tablet.addEventListener("change", resize);
    return () => {
      mobile.removeEventListener("change", resize);
      tablet.removeEventListener("change", resize);
    };
  }, []);
  useEffect(() => {
    if (!mobileNav || !isMobile) return;
    (sidebar.current?.querySelector("nav a[aria-current]") || sidebar.current?.querySelector("nav a"))?.focus();
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const keyboard = (event) => {
      if (document.querySelector("dialog[open]")) return;
      if (event.key === "Escape") {
        event.preventDefault();
        setMobileNav(false);
        menuButton.current?.focus();
      }
      if (event.key === "Tab") {
        const controls = [...sidebar.current.querySelectorAll("a[href], button:not([disabled])")]
          .filter(control => control.getClientRects().length);
        controls.push(menuButton.current);
        const index = controls.indexOf(document.activeElement);
        if (index === -1 || (!event.shiftKey && index === controls.length - 1) || (event.shiftKey && index === 0)) {
          event.preventDefault();
          controls[event.shiftKey ? controls.length - 1 : 0]?.focus();
        }
      }
    };
    window.addEventListener("keydown", keyboard);
    return () => {
      window.removeEventListener("keydown", keyboard);
      document.body.style.overflow = previousOverflow;
    };
  }, [mobileNav, isMobile]);
  const session = useResource("/api/workspace/");
  useEffect(() => {
    return installHashNavigation(window, requestLeave, (nextRoute) => {
      setRoute(nextRoute);
      setMobileNav(false);
      window.scrollTo(0, 0);
    });
  }, [requestLeave]);
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
    <div className={`app-shell${sidebarCollapsed && !isMobile ? " sidebar-collapsed" : ""}`}>
      <a
        className="skip-link"
        href="#main-content"
        onClick={(e) => {
          e.preventDefault();
          setMobileNav(false);
          requestAnimationFrame(() => content.current?.focus());
        }}
      >
        Saltar al contenido
      </a>
      <Sidebar sidebarRef={sidebar} section={section} user={user}
        collapsed={sidebarCollapsed && !isMobile} mobile={isMobile} open={mobileNav}
        onToggle={() => setSidebarCollapsed(value => !value)} onClose={closeMenu} />
      <button className={`nav-backdrop${mobileNav ? " is-visible" : ""}`} tabIndex={-1}
        aria-hidden={!mobileNav} aria-label="Cerrar navegación" onClick={closeMenu} />
      <div className="main-shell">
        <header className="topbar">
          <div>
            <button
              ref={menuButton}
              className="icon-button mobile-menu"
              aria-label={mobileNav ? "Ocultar navegación" : "Mostrar navegación"}
              aria-expanded={mobileNav}
              aria-controls="workspace-navigation"
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
        <main ref={content} id="main-content" tabIndex="-1" inert={mobileNav || undefined}>
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
    <UnsavedChangesProvider><App /></UnsavedChangesProvider>
  </React.StrictMode>,
);
