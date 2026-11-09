import React from "react";

export function Breadcrumbs({ items }) {
  return (
    <nav className="breadcrumbs" aria-label="Ruta de navegación">
      <ol>
        {items.map((item, index) => (
          <li key={item.href}>
            {index > 0 && <span className="breadcrumb-separator" aria-hidden="true">›</span>}
            {index === items.length - 1 ? (
              <span className="breadcrumb-current" aria-current="page" title={item.label}>{item.label}</span>
            ) : (
              <a href={item.href} title={item.label}>{item.label}</a>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}
