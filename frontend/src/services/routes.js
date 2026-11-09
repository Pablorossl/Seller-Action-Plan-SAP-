// The hash router, sidebar and breadcrumbs share the same route definitions.
export const navigationSections = [
  { key: "dashboard", path: "/", label: "Dashboard" },
  { key: "sellers", path: "/sellers", label: "Vendedores" },
  { key: "plans", path: "/plans", label: "Planes de mejora" },
];

const routes = [
  ...navigationSections.map(section => ({ ...section, section: section.key })),
  { key: "plan-new", path: "/plans/new", section: "plans", label: "Crear plan de mejora" },
  { key: "seller", pattern: /^\/sellers\/(\d+)$/, section: "sellers", nameField: "name", resourceName: "Vendedor" },
  { key: "plan", pattern: /^\/plans\/(\d+)$/, section: "plans", nameField: "title", resourceName: "Plan" },
];

export function resolveRoute(location) {
  const [path, query = ""] = location.split("?");
  for (const definition of routes) {
    const match = definition.pattern?.exec(path);
    if (definition.path === path || match) {
      const id = match?.[1];
      return {
        ...definition,
        path,
        id,
        params: new URLSearchParams(query),
        resourceUrl: id ? `/api/${definition.section}/${id}/` : null,
      };
    }
  }
  return {
    key: "not-found",
    path,
    section: null,
    label: "Página no encontrada",
    params: new URLSearchParams(query),
    resourceUrl: null,
  };
}

export function routeBreadcrumbs(route, resource) {
  const root = navigationSections[0];
  const crumbs = [{ label: root.label, href: `#${root.path}` }];
  if (route.key === root.key) return crumbs;
  const parent = navigationSections.find(section => section.key === route.section);
  if (parent && route.key !== parent.key) {
    crumbs.push({ label: parent.label, href: `#${parent.path}` });
  }
  const label = route.nameField
    ? resource?.data?.[route.nameField] || (
      resource?.error
        ? `${route.resourceName} no disponible`
        : `Cargando ${route.resourceName.toLowerCase()}…`
    )
    : route.label;
  crumbs.push({ label, href: `#${route.path}` });
  return crumbs;
}
