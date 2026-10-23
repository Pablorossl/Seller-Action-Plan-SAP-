import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { getAllPages } from './services/api';
import './styles.css';

const statuses = {
  ok: 'Dentro de referencia', alarm: 'Alarma', suspension_threshold: 'Umbral de suspensión (informativo)',
  insufficient_orders: 'Volumen insuficiente para MQC', below_reference: 'Por debajo de referencia',
  not_evaluable: 'No evaluable: faltan datos o el periodo no es mensual',
};

function App() {
  const [page, setPage] = useState('sellers');
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    setData(null);
    setError('');
    getAllPages(`/api/${page}/`, { signal: controller.signal })
      .then(setData).catch(err => { if (err.name !== 'AbortError') setError(err.message); });
    return () => controller.abort();
  }, [page]);
  const loginNext = import.meta.env.DEV ? '/static/react/' : '/dashboard/';
  return <main>
    <header><span className="eyebrow">SELLER ACTION PLAN · BASE DEL MVP</span><h1>Calidad con seguimiento.</h1>
      <p>Consulta tus vendedores y sus indicadores. SAP facilita la evaluación y nunca suspende tiendas.</p></header>
    <nav aria-label="Secciones">
      <button aria-pressed={page === 'sellers'} onClick={() => setPage('sellers')}>Vendedores</button>
      <button aria-pressed={page === 'metrics'} onClick={() => setPage('metrics')}>Indicadores</button>
      <a href={`/accounts/login/?next=${encodeURIComponent(loginNext)}`}>Iniciar sesión</a>
    </nav>
    <section aria-live="polite">
      <h2>{page === 'sellers' ? 'Vendedores asignados' : 'Indicadores por canal y periodo'}</h2>
      {error && <p role="alert">{error}</p>}
      {!data && !error && <p>Cargando datos…</p>}
      {data?.length === 0 && <p>No hay registros accesibles. Solicita al administrador que revise tu asignación.</p>}
      {data?.length > 0 && (page === 'sellers' ? <ul className="cards">{data.map(seller => <li key={seller.id}>
        <span>{seller.reference}</span><h3>{seller.name}</h3></li>)}</ul> : <div className="table-wrap"><table>
        <caption>Observaciones registradas; la clasificación corresponde al periodo indicado.</caption>
        <thead><tr>{['Vendedor', 'Indicador', 'Canal', 'Periodo', 'Pedidos', 'Valor', 'Evaluación'].map(label => <th key={label}>{label}</th>)}</tr></thead>
        <tbody>{data.map(metric => <tr key={metric.id}><td>{metric.seller_name}</td><td>{metric.label}</td><td>{metric.channel}</td>
          <td>{metric.period_start} / {metric.period_end}</td><td>{metric.order_count}</td>
          <td>{metric.value} {metric.unit === 'hours' ? 'h' : '%'}</td><td>{statuses[metric.classification] ?? metric.classification}</td></tr>)}</tbody>
      </table></div>)}
    </section>
    <footer>Proyecto académico independiente · Datos ficticios · Sin conexión con Mirakl</footer>
  </main>;
}

createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>);
