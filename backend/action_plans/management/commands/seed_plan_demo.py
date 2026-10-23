from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from action_plans.models import ActionStatus, ImprovementPlan, PlanAction, PlanMetric, PlanReview, PlanStatus
from action_plans.services import close_plan
from quality.models import QualityMetric, ThresholdPolicy
from quality.rules import DEFAULT_POLICIES
from sellers.models import Seller, visible_sellers


class Command(BaseCommand):
    help = "Demuestra el recorrido ficticio 6% → 4,5% → 3%, con acciones y cierre; solo DEBUG=True."

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("La demo solo se carga en desarrollo.")
        owner = get_user_model().objects.filter(username=options["owner"], is_active=True).first()
        if owner is None or not owner.has_perms(["action_plans.add_improvementplan", "action_plans.change_improvementplan", "action_plans.close_improvementplan"]):
            raise CommandError("Configura primero el agente con configure_plan_agent o utiliza un superusuario.")
        seller, _ = Seller.objects.get_or_create(reference="SAP-DEMO-PLAN", defaults={"name": "Tienda Ficticia Envíos", "owner": owner})
        if seller.owner_id != owner.pk or not visible_sellers(owner).filter(pk=seller.pk).exists():
            raise CommandError("La demo pertenece a otro usuario; no se reasignarán datos.")
        title = "DEMO: reducir incidencias de envío del 6% al 3%"
        if seller.plans.filter(title=title).exists():
            self.stdout.write("La demo de planes ya existe; se conserva sin cambios.")
            return
        _, unit, operator, alarm, suspension, is_mqc = next(row for row in DEFAULT_POLICIES if row[0] == "incidents")
        policy, _ = ThresholdPolicy.objects.get_or_create(code="incidents", version=1, defaults={
            "unit": unit, "operator": operator, "alarm": Decimal(alarm), "suspension": Decimal(suspension), "is_mqc": is_mqc,
        })
        baseline, _ = QualityMetric.objects.get_or_create(seller=seller, policy=policy, channel="ficticio-es",
            period_start=date(2026, 7, 1), period_end=date(2026, 7, 31), defaults={"order_count": 100, "value": Decimal("6")})
        plan = ImprovementPlan.objects.create(seller=seller, title=title,
            problem="Incidencias en el 6% de los pedidos del canal ficticio España.",
            period_start=baseline.period_start, period_end=baseline.period_end,
            root_cause="El control de embalaje no detecta daños y la recogida del transportista se realiza tarde.",
            evidence="Muestra ficticia: seis incidencias de envío entre cien pedidos de julio.",
            objective="Reducir las incidencias del 6% al 3%.", responsible=owner, created_by=owner,
            due_date=date(2026, 10, 31), next_review_on=date(2026, 10, 1))
        metric = PlanMetric.objects.create(plan=plan, baseline=baseline, target_value=Decimal("3"))
        action = PlanAction.objects.create(plan=plan, description="Revisar el embalaje del 100% de los paquetes frágiles.",
            kind="corrective", responsible="Equipo ficticio de logística", due_date=date(2026, 8, 20))
        PlanAction.objects.create(plan=plan, description="Auditar semanalmente las recogidas y registrar el cumplimiento.",
            kind="preventive", responsible="Equipo ficticio de operaciones", due_date=date(2026, 10, 30))
        plan.status = PlanStatus.IN_PROGRESS
        plan.save()
        action.status = ActionStatus.COMPLETED
        action.completed_on = date(2026, 8, 20)
        action.evidence = "Lista ficticia de comprobación de embalaje aplicada a todos los paquetes frágiles."
        action.save()
        for start, end, reviewed_on, value in [
            (date(2026, 8, 1), date(2026, 8, 31), date(2026, 9, 1), "4.5"),
            (date(2026, 9, 1), date(2026, 9, 30), date(2026, 10, 1), "3"),
        ]:
            PlanReview.objects.create(plan_metric=metric, recorded_by=owner, reviewed_on=reviewed_on,
                value=Decimal(value), period_start=start, period_end=end, order_count=100,
                comments="Medición mensual ficticia; se observa una reducción de incidencias.", assessment="on_track",
                next_steps="Mantener el control de embalaje y completar la auditoría preventiva.")
        close_plan(plan_id=plan.pk, actor=owner, notes="Objetivo del 3% alcanzado en septiembre. Se mantiene la auditoría preventiva pendiente en el histórico.")
        self.stdout.write(self.style.SUCCESS(f"Plan demo #{plan.pk}: 6% → 4,5% → 3%, dos acciones, dos revisiones y cierre documentado."))
