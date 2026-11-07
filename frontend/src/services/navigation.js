// Hash routes keep their public URLs. Index entries so a rejected Back/Forward
// restores the original entry instead of overwriting the destination's history.
export function installHashNavigation(win, canLeave, onNavigate) {
  const key = "sapNavigationIndex";
  let index = Number.isInteger(win.history.state?.[key]) ? win.history.state[key] : 0;
  let url = win.location.href;
  let pending = false;
  let restoring = null;
  let replay = false;
  let disposed = false;
  win.history.replaceState({ ...win.history.state, [key]: index }, "", url);
  const commit = (nextIndex) => {
    index = nextIndex;
    url = win.location.href;
    onNavigate(win.location.hash.slice(1) || "/");
  };
  const navigate = async (target) => {
    if (pending || target === url) return;
    pending = true;
    try {
      if (await canLeave() && !disposed) {
        win.history.pushState({ [key]: index + 1 }, "", target);
        commit(index + 1);
      }
    } finally {
      pending = false;
    }
  };
  const click = (event) => {
    const link = event.target.closest?.("a[href]");
    if (!link || event.defaultPrevented || event.button !== 0 ||
        event.metaKey || event.ctrlKey || event.shiftKey || event.altKey ||
        link.hasAttribute("download") || (link.target && link.target !== "_self")) return;
    const target = new URL(link.href, url);
    const current = new URL(url);
    if (target.origin !== current.origin || target.pathname !== current.pathname ||
        target.search !== current.search || !target.hash.startsWith("#/")) return;
    event.preventDefault();
    void navigate(target.href);
  };
  const hashchange = async () => {
    if (restoring && win.location.href === url) {
      const resolve = restoring;
      restoring = null;
      resolve();
      return;
    }
    if (win.location.href === url) return;
    let nextIndex = win.history.state?.[key];
    if (!Number.isInteger(nextIndex)) {
      nextIndex = index + 1;
      win.history.replaceState({ ...win.history.state, [key]: nextIndex }, "");
    }
    if (replay) {
      replay = false;
      commit(nextIndex);
      return;
    }
    const delta = nextIndex - index;
    // Rendered form remains mounted throughout the history round trip.
    const wasPending = pending;
    pending = true;
    await new Promise((resolve) => {
      restoring = resolve;
      win.history.go(-delta);
    });
    if (wasPending || disposed) return;
    try {
      if (await canLeave() && !disposed) {
        replay = true;
        win.history.go(delta);
      }
    } finally {
      pending = false;
    }
  };
  win.document.addEventListener("click", click);
  win.addEventListener("hashchange", hashchange);
  return () => {
    disposed = true;
    win.document.removeEventListener("click", click);
    win.removeEventListener("hashchange", hashchange);
  };
}

// Compare submitted values, not touched flags or API display objects. IDs from
// selects can be strings even when their initial API representation is numeric.
export function formSnapshot(value) {
  const normalize = (item) => {
    if (Array.isArray(item)) return item.map(normalize);
    if (item && typeof item === "object")
      return Object.fromEntries(Object.keys(item).sort().map(k => [k, normalize(item[k])]));
    return typeof item === "number" ? String(item) : item ?? "";
  };
  return JSON.stringify(normalize(value));
}
