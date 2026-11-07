import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { Modal } from "./ui.jsx";
import { formSnapshot } from "../services/navigation.js";

const Context = createContext(null);

export function UnsavedChangesProvider({ children }) {
  const active = useRef(null);
  const pending = useRef(null);
  const [warning, setWarning] = useState(false);
  const register = useCallback((guard) => {
    active.current = guard;
    return () => { if (active.current === guard) active.current = null; };
  }, []);
  const requestLeave = useCallback(() => {
    if (pending.current) return pending.current.promise;
    const guard = active.current;
    if (guard?.busy()) return Promise.resolve(false);
    if (!guard?.dirty()) return Promise.resolve(true);
    let resolve;
    const promise = new Promise(r => { resolve = r; });
    pending.current = { promise, resolve, guard };
    setWarning(true);
    return promise;
  }, []);
  const choose = (discard) => {
    const choice = pending.current;
    if (!choice) return;
    pending.current = null;
    if (discard) choice.guard.discard();
    setWarning(false);
    choice.resolve(discard);
  };
  useEffect(() => {
    const beforeUnload = (event) => {
      if (active.current?.dirty() || active.current?.busy()) {
        event.preventDefault();
        event.returnValue = "";
      }
    };
    const logout = async (event) => {
      const form = event.target;
      if (new URL(form.action).pathname !== "/accounts/logout/") return;
      event.preventDefault();
      if (await requestLeave()) HTMLFormElement.prototype.submit.call(form);
    };
    window.addEventListener("beforeunload", beforeUnload);
    document.addEventListener("submit", logout);
    return () => {
      window.removeEventListener("beforeunload", beforeUnload);
      document.removeEventListener("submit", logout);
    };
  }, [requestLeave]);
  return (
    <Context.Provider value={{ register, requestLeave }}>
      {children}
      {warning && (
        <Modal title="Cambios sin guardar" close={() => choose(false)} initialFocus="[data-continue-editing]">
          <p>Hay cambios sin guardar. Si los descartas, perderás los datos introducidos.</p>
          <div className="form-actions unsaved-actions">
            <button data-continue-editing className="button secondary" onClick={() => choose(false)}>Continuar editando</button>
            <button className="button primary" onClick={() => choose(true)}>Descartar los cambios y abandonar</button>
          </div>
        </Modal>
      )}
    </Context.Provider>
  );
}

export function useLeaveConfirmation() {
  return useContext(Context).requestLeave;
}

export function useUnsavedChanges(values, { busy = false } = {}) {
  const { register, requestLeave } = useContext(Context);
  const baseline = useRef(formSnapshot(values));
  const current = useRef(null);
  const discarded = useRef(false);
  current.current = { snapshot: formSnapshot(values), busy };
  useEffect(() => register({
    dirty: () => !discarded.current && current.current.snapshot !== baseline.current,
    busy: () => current.current.busy,
    discard: () => { discarded.current = true; },
  }), [register]);
  return {
    requestLeave,
    markSaved: () => { discarded.current = true; },
    resetBaseline: (initial) => { baseline.current = formSnapshot(initial); },
    close: (callback) => async () => { if (await requestLeave()) callback(); },
  };
}
