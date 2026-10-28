"""Diagramas documentales SVG del modelo implementado; sólo biblioteca estándar."""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs/diagramas"
OUT.mkdir(parents=True, exist_ok=True)


class Diagram:
    def __init__(self, title, width, height):
        self.width, self.height = width, height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title>',
            '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#387466"/></marker></defs>',
            f'<rect width="{width}" height="{height}" fill="white"/>']
        self.text(30, 35, title, 23, True)

    def text(self, x, y, value, size=17, bold=False):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" fill="#173b35">{escape(value)}</text>')

    def box(self, x, y, w, title, lines, h=None):
        h = h or 52 + len(lines) * 25
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f1f7f4" stroke="#83ad9c"/>')
        self.text(x+16, y+30, title, 19, True)
        for i, line in enumerate(lines):
            self.text(x+16, y+58+i*25, line, 16)

    def edge(self, points, label="", lx=0, ly=0):
        self.parts.append(f'<polyline points="{points}" fill="none" stroke="#387466" stroke-width="2" marker-end="url(#arrow)"/>')
        if label:
            self.text(lx, ly, label, 15)

    def save(self, name):
        (OUT / name).write_text("\n".join(self.parts) + "</svg>\n")


d = Diagram("Arquitectura de SAP · un origen web", 1050, 800)
d.box(30, 80, 440, "Navegador", ["Login y portal: plantillas Django", "React: dashboard, vendedores y planes", "Fetch /api/ · sesión + CSRF"])
d.box(590, 80, 420, "Build y release", ["Vite → frontend/dist", "collectstatic → WhiteNoise", "release.sh → migrate (una vez)"])
d.box(30, 290, 440, "Entrada WSGI", ["Render HTTPS → Gunicorn (propuesto)", "QA: Gunicorn + TLS local verificado"])
d.box(30, 475, 580, "Django", ["DRF: permisos y serializadores", "sellers → quality → action_plans", "Servicios: evaluación y cierre", "ORM · validación · transacciones"])
d.box(720, 485, 290, "PostgreSQL", ["Usuarios y sesiones", "Dominio e histórico", "TLS · bloqueos de fila"])
d.edge("250,210 250,290", "HTTPS / JSON", 265, 257)
d.edge("250,392 250,475", "petición", 265, 443)
d.edge("610,555 720,555", "ORM", 636, 542)
d.edge("800,210 800,330 470,330", "estáticos compilados", 610, 312)
d.text(30, 725, "PostgreSQL 14.24 probado localmente; 16 propuesto en Render. SQLite sólo desarrollo.", 17)
d.text(30, 755, "No existe conexión con Mirakl. El despliegue público continúa pendiente.", 17)
d.save("arquitectura.svg")

d = Diagram("Modelo entidad-relación · entidades y FK de dominio", 1120, 1030)
d.box(25, 80, 310, "auth.User", ["PK id · username", "Grupos y permisos Django", "is_staff / is_superuser"])
d.box(405, 80, 310, "Seller", ["PK id · reference UNIQUE", "FK owner → User", "name · created_at"])
d.box(785, 80, 310, "ThresholdPolicy", ["PK id · code + version UNIQUE", "unit · operator · alarm", "suspension · minimum_orders", "is_mqc"])
d.box(25, 385, 330, "ImprovementPlan", ["PK id · FK seller", "FK created_by / responsible", "problem · root_cause · evidence", "objective · dates · status", "revision · request_key UNIQUE", "closure_notes / evaluation"])
d.box(785, 385, 310, "QualityMetric", ["PK id · FK seller / policy", "channel · period_start / end", "order_count · value"])
d.box(25, 760, 330, "PlanAction", ["PK id · FK plan", "kind · description · responsible*", "due_date · status · evidence", "revision · request_key UNIQUE"])
d.box(405, 760, 310, "PlanMetric", ["PK id · FK plan / baseline", "target_value · revision", "UNIQUE plan + baseline"])
d.box(785, 760, 310, "PlanReview", ["PK id · FK plan_metric", "FK recorded_by → User", "period · value · order_count", "comments · assessment"])
d.edge("335,142 405,142", "1:N", 350, 130)
d.edge("470,207 470,320 190,320 190,385", "Seller 1:N planes", 210, 310)
d.edge("650,207 650,310 850,310 850,385", "Seller 1:N observaciones", 695, 294)
d.edge("980,232 980,385", "1:N", 992, 320)
d.edge("190,587 190,760", "1:N", 202, 682)
d.edge("355,530 560,530 560,760", "Plan 1:N objetivos", 378, 514)
d.edge("785,465 685,465 685,760", "1:N", 695, 610)
d.edge("715,822 785,822", "1:N", 733, 808)
d.text(25, 960, "FK de dominio: PROTECT. User tiene dos relaciones 1:N con ImprovementPlan y una con PlanReview.", 16)
d.text(25, 987, "* PlanAction.responsible es texto (persona/equipo), no FK. User–Group–Permission: relaciones M:N nativas.", 16)
d.save("modelo-datos.svg")

d = Diagram("Casos de uso · acceso según rol y vendedor", 1040, 720)
d.box(30, 100, 260, "Agente autorizado", ["Marketplace Agent", "Permisos de planes", "Vendedores propios"])
d.box(370, 80, 625, "Operación React", ["Consultar dashboard y buscar vendedor", "Leer indicadores y detectar desviación", "Crear plan, objetivos y acciones", "Registrar revisión y consultar evaluación", "Cerrar con razones y permiso específico"])
d.box(30, 400, 260, "Superusuario", ["Administración global", "Acceso a todos los datos"])
d.box(370, 400, 625, "Configuración Django Admin", ["Gestionar usuarios, grupos y permisos", "Crear/asignar vendedores", "Registrar políticas y observaciones iniciales"])
d.edge("290,180 370,180", "usa", 310, 166)
d.edge("290,475 370,475", "usa", 310, 461)
d.edge("155,400 155,335 680,335 680,257", "también puede operar", 362, 324)
d.text(30, 635, "Todos los casos de negocio requieren sesión. Anónimo: login y salud pública, sin datos de dominio.", 17)
d.text(30, 665, "No hay rol de vendedor externo. is_staff permite entrar en Admin, pero no sustituye permisos.", 17)
d.save("casos-uso.svg")

d = Diagram("Flujo de mejora · resultado separado del estado", 1060, 730)
d.box(30, 90, 300, "1. Desviación", ["Observación, canal y periodo", "Demo: incidencias 6%"])
d.box(390, 90, 300, "2. Diagnóstico", ["Problema, causa y evidencia", "Objetivo: 3% · borrador"])
d.box(750, 90, 280, "3. Acciones", ["Responsables y plazos", "Activar el plan"])
d.box(750, 345, 280, "4. Seguimiento", ["Revisiones: 4,5% y 3%", "Periodos mensuales"])
d.box(390, 345, 300, "5. Evaluación", ["Valor inicial / meta / actual", "Logro, mejora o sin datos"])
d.box(30, 345, 300, "6. Finalización", ["Razones y confirmación", "Instantánea e histórico"])
d.edge("330,140 390,140")
d.edge("690,140 750,140")
d.edge("890,192 890,345")
d.edge("750,395 690,395")
d.edge("390,395 330,395")
d.text(30, 555, "Borrador → en progreso ⇄ en revisión → cerrado. Cancelación posible desde estados abiertos.", 18)
d.text(30, 595, "Cerrar no exige éxito: puede conservar acciones pendientes o resultados no evaluables.", 18)
d.text(30, 635, "La evaluación es interna e informativa. SAP no cambia el estado de tiendas ni pagos en Mirakl.", 18)
d.save("flujo-mejora.svg")
print(f"Cuatro diagramas SVG generados en {OUT}")
