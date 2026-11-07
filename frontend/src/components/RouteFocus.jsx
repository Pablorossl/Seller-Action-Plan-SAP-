import { useEffect, useRef } from "react";

// Wait for the destination's async content, and focus once per accepted route.
// Refreshes, filtering and rejected navigation must not move the user's focus.
export function useRouteFocus(route, content) {
  const initialRoute = useRef(route);
  const navigated = useRef(false);
  useEffect(() => {
    const contextual = /^\/plans\/\d+\?/.test(route) &&
      new URLSearchParams(route.split("?")[1]).has("action");
    if (route !== initialRoute.current) navigated.current = true;
    if (!navigated.current && !contextual) return;
    const root = content.current;
    let finished = false;
    const focusDestination = () => {
      if (finished) return;
      const action = contextual && root.querySelector(".action-item.highlight");
      const target = action || root.querySelector(".page-heading h1, .error-state, .empty h3");
      if (!target) return;
      finished = true;
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
      if (action) target.scrollIntoView({ block: "start" });
      observer.disconnect();
    };
    const observer = new MutationObserver(focusDestination);
    observer.observe(root, { childList: true, subtree: true });
    focusDestination();
    return () => observer.disconnect();
  }, [route, content]);
}
