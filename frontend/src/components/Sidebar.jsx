import React, { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { Avatar, Icon } from "./ui.jsx";

const sections = [
  ["dashboard", "/", "Dashboard"],
  ["sellers", "/sellers", "Vendedores"],
  ["plans", "/plans", "Planes de mejora"],
];

export function Sidebar({
  sidebarRef, section, user, collapsed, mobile, open, onToggle, onClose,
}) {
  const [tooltip, setTooltip] = useState(null);
  const tooltipId = useId();
  const dismissTimer = useRef(null);
  const keepTooltip = () => clearTimeout(dismissTimer.current);
  const dismissTooltip = () => {
    keepTooltip();
    dismissTimer.current = setTimeout(() => setTooltip(null), 120);
  };
  useEffect(() => {
    setTooltip(null);
    const dismiss = () => setTooltip(null);
    const escape = (event) => { if (event.key === "Escape") dismiss(); };
    window.addEventListener("resize", dismiss);
    document.addEventListener("scroll", dismiss, true);
    document.addEventListener("keydown", escape);
    return () => {
      clearTimeout(dismissTimer.current);
      window.removeEventListener("resize", dismiss);
      document.removeEventListener("scroll", dismiss, true);
      document.removeEventListener("keydown", escape);
    };
  }, [collapsed, open]);
  const showTooltip = (event, label) => {
    if (!collapsed) return;
    keepTooltip();
    const rect = event.currentTarget.getBoundingClientRect();
    setTooltip({
      label,
      left: Math.max(sidebarRef.current.getBoundingClientRect().right, rect.right) + 12,
      top: Math.max(24, Math.min(window.innerHeight - 24, rect.top + rect.height / 2)),
    });
  };
  const describe = (label) => ({
    "aria-describedby": collapsed && tooltip?.label === label ? tooltipId : undefined,
    onMouseEnter: (event) => showTooltip(event, label),
    onMouseLeave: dismissTooltip,
    onFocus: (event) => showTooltip(event, label),
    onBlur: dismissTooltip,
  });
  const closeCurrentRoute = (event) => {
    if (mobile && event.button === 0 && !event.metaKey && !event.ctrlKey &&
        !event.shiftKey && !event.altKey && event.currentTarget.href === window.location.href) {
      onClose();
    }
  };
  return (
    <aside ref={sidebarRef} id="workspace-navigation" aria-label="Menú lateral"
      className={`sidebar${open ? " is-open" : ""}`}
      inert={mobile && !open ? true : undefined} aria-hidden={mobile && !open ? true : undefined}>
      <div className="sidebar-scroll">
        <a className="brand" href="#/" aria-label="SAP · Seller Action Plan" onClick={closeCurrentRoute}
          {...describe("SAP · Seller Action Plan")}>
          <span className="brand-mark"><Icon name="trend" size={27} /></span>
          <span className="sidebar-label">SAP<small>Seller Action Plan</small></span>
        </a>
        <div className="workspace-label"><span className="live-dot" /><span className="sidebar-label">Marketplace workspace</span></div>
        <p className="nav-label">GESTIÓN OPERATIVA</p>
        <nav aria-label="Navegación principal">
          {sections.map(([key, href, text]) => (
            <a href={`#${href}`} key={key} className={section === key ? "active" : ""}
              aria-label={text} aria-current={section === key ? "page" : undefined}
              onClick={closeCurrentRoute} {...describe(text)}>
              <Icon name={key} />
              <span className="sidebar-label">{text}</span>
              {section === key && <span className="nav-active-dot" />}
            </a>
          ))}
        </nav>
        {user && <div className="sidebar-bottom">
          <div className="user-info" title={user.name}>
            <Avatar name={user.name} />
            <div className="sidebar-label"><strong>{user.name}</strong><small>Marketplace Agent</small></div>
          </div>
          <form action="/accounts/logout/" method="post">
            <input type="hidden" name="csrfmiddlewaretoken" value={user.csrf_token} />
            <button className="logout" type="submit" aria-label="Cerrar sesión" {...describe("Cerrar sesión")}>
              <Icon name="logout" /><span className="sidebar-label">Cerrar sesión</span>
            </button>
          </form>
        </div>}
      </div>
      <button type="button" className="sidebar-toggle" aria-label={collapsed ? "Expandir menú lateral" : "Contraer menú lateral"}
        aria-expanded={!collapsed} aria-controls="workspace-navigation" onClick={onToggle} />
      {collapsed && tooltip && createPortal(
        <div id={tooltipId} role="tooltip" className="sidebar-tooltip" style={{ left: tooltip.left, top: tooltip.top }}
          onMouseEnter={keepTooltip} onMouseLeave={dismissTooltip}>{tooltip.label}</div>, document.body)}
    </aside>
  );
}
