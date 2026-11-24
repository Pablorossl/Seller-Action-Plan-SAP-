import React, { useState } from "react";
import { FormError, Modal } from "./ui.jsx";
import { api } from "../services/api.js";

export function Guide({ user, close }) {
  const [step, setStep] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const steps = [
    ["Bienvenido a Seller Action Plan", "En el dashboard puedes evaluar el rendimiento de tus vendedores y consultar qué requiere tu atención."],
    ["Tus tiendas asignadas", user.role === "ADMIN" ? "Consulta tus tiendas en Vendedores. En Gestión de usuarios puedes distribuir tiendas entre las cuentas." : "Abre Vendedores para consultar las tiendas que te ha asignado el administrador y sus indicadores."],
    ["Planes de mejora", user.permissions.add_improvementplan && user.permissions.add_planmetric ? "Desde la ficha de una tienda puedes crear un plan, definir objetivos y registrar acciones." : "Consulta los planes disponibles desde Planes de mejora."],
    ["Seguimiento y resultados", "En el detalle de cada plan puedes consultar su estado, las revisiones y la evolución de los indicadores."],
  ];
  async function finish() {
    if (busy) return;
    setBusy(true);
    try {
      if (user.onboarding_pending) await api("/api/onboarding/complete/", {method: "POST"});
      close();
    } catch (err) { setError(err); setBusy(false); }
  }
  return <Modal title="Guía de SAP" close={finish} busy={busy}>
    <div aria-live="polite" aria-atomic="true">
      <div className="guide-step" key={step}>
        <small>Paso {step + 1} de {steps.length}</small><h3>{steps[step][0]}</h3><p>{steps[step][1]}</p>
      </div>
    </div>
    <FormError error={error}/>
    <div className="form-actions">
      <button className="button secondary" disabled={busy} onClick={finish}>Omitir guía</button>
      {step > 0 && <button className="button secondary" disabled={busy} onClick={() => setStep(step - 1)}>Atrás</button>}
      <button className="button primary" disabled={busy} onClick={step === steps.length - 1 ? finish : () => setStep(step + 1)}>
        {busy ? "Guardando…" : step === steps.length - 1 ? "Finalizar" : "Siguiente"}
      </button>
    </div>
  </Modal>;
}
