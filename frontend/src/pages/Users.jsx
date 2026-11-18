import React, { useState } from "react";
import { Field, FormError, Modal, Resource, useResource } from "../components/ui.jsx";
import { api } from "../services/api.js";

function AccountForm({ user, close, saved }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  async function submit(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    data.is_active = data.is_active === "on";
    setBusy(true);
    setError(null);
    try {
      const account = await api(user ? `/api/users/${user.id}/` : "/api/users/", {method: user ? "PATCH" : "POST", data});
      saved(account);
    } catch (err) {
      setError(err);
      setBusy(false);
    }
  }
  return <Modal title={user ? "Editar agente" : "Crear agente"} close={close} busy={busy}>
    <form onSubmit={submit}>
      <fieldset className="account-fields" disabled={busy}>
        <Field label="Nombre de usuario" name="username" autoComplete="off" defaultValue={user?.username} required maxLength={150} errors={error?.fields}/>
        {!user && <Field label="Contraseña inicial" name="password" type="password" autoComplete="new-password" required minLength={8} maxLength={128} errors={error?.fields}/>}
        <div className="form-grid">
          <Field label="Nombre" name="first_name" defaultValue={user?.first_name} maxLength={150}/>
          <Field label="Apellidos" name="last_name" defaultValue={user?.last_name} maxLength={150}/>
        </div>
        <Field label="Correo electrónico" name="email" type="email" defaultValue={user?.email} maxLength={254}/>
        <label><input type="checkbox" name="is_active" defaultChecked={user?.is_active ?? true}/> Cuenta activa</label>
      </fieldset>
      <FormError error={error}/>
      <div className="form-actions"><button type="button" className="button secondary" disabled={busy} onClick={close}>Cancelar</button>
        <button className="button primary" disabled={busy}>{busy ? "Guardando…" : "Guardar agente"}</button></div>
    </form>
  </Modal>;
}

function Assignments({ user, data, onChange }) {
  const [selected, setSelected] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const assigned = data.sellers.filter(store => store.owner_id === user.id);
  async function save(store, owner) {
    setBusy(true);
    setError(null);
    try {
      await api(`/api/assignments/${store.id}/`, {method: "PATCH", data: {owner, previous_owner: store.owner_id}});
      setSelected("");
      onChange("Asignación guardada.");
    } catch (err) { setError(err); }
    finally { setBusy(false); }
  }
  return <section className="panel account-panel">
    <h2>Tiendas de {user.username}</h2>
    {assigned.length ? <ul className="account-list">{assigned.map(store => <li key={store.id}>
      <span>{store.name} · {store.reference}</span>
      <button className="button secondary compact" disabled={busy} onClick={() => save(store, null)}>Retirar</button>
    </li>)}</ul> : <p className="muted">Sin tiendas asignadas.</p>}
    {user.is_active && <form className="assignment-form" onSubmit={event => {
      event.preventDefault();
      save(data.sellers.find(store => store.id === Number(selected)), user.id);
    }}>
      <Field label="Asignar una tienda" name="seller" required value={selected} onChange={e => setSelected(e.target.value)}>
        <select disabled={busy}><option value="">Selecciona una tienda</option>
          {data.sellers.filter(store => store.owner_id !== user.id).map(store =>
            <option key={store.id} value={store.id}>{store.name} · {store.reference} ({data.users.find(u => u.id === store.owner_id)?.username || "Sin asignar"})</option>)}
        </select>
      </Field>
      <button className="button primary" disabled={busy || !selected}>Asignar a {user.username}</button>
    </form>}
    <FormError error={error}/>
  </section>;
}

export function Users() {
  const resource = useResource("/api/users/");
  const [selected, setSelected] = useState(null);
  const [editor, setEditor] = useState(undefined);
  const [notice, setNotice] = useState("");
  const refresh = message => { setNotice(message); resource.reload(); };
  return <>
    <div className="page-heading"><h1>Gestión de usuarios</h1><button className="button primary" onClick={() => setEditor(null)}>Crear agente</button></div>
    <p role="status">{notice}</p>
    <Resource resource={resource}>{data => {
      const current = data.users.find(u => u.id === selected) || data.users[0];
      return <><section className="panel account-panel"><h2>Cuentas registradas</h2>
        <ul className="account-list">{data.users.map(u => <li key={u.id}>
          <div><strong>{u.username}</strong><div>{u.role === "ADMIN" ? "Administrador" : "Agente"} · {u.is_active ? "Activa" : "Inactiva"}</div></div>
          <div className="form-actions"><button className="button secondary compact" aria-pressed={u.id === current?.id} onClick={() => setSelected(u.id)}>Ver tiendas</button>
          {u.role === "AGENT" && <button className="button secondary compact" onClick={() => setEditor(u)}>Editar</button>}</div>
        </li>)}</ul>
      </section>{current && <Assignments key={current.id} user={current} data={data} onChange={refresh}/>}</>;
    }}</Resource>
    {editor !== undefined && <AccountForm user={editor} close={() => setEditor(undefined)} saved={account => {
      setEditor(undefined); setSelected(account.id); refresh("Cuenta guardada.");
    }}/>}
  </>;
}
