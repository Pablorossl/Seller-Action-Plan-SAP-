from datetime import date, timedelta
from io import StringIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError, call_command
from django.db import transaction
from django.utils import timezone

from action_plans.models import ImprovementPlan, PlanAction, PlanMetric, PlanReview
from action_plans.services import close_plan
from quality.models import QualityMetric, ThresholdPolicy
from sellers.models import Seller


class Command(BaseCommand):
    help = "Carga representativa, ficticia e idempotente. Nunca se ejecuta al arrancar ni en cada despliegue."

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True)
        parser.add_argument("--confirm-fictitious", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if not options["confirm_fictitious"] or not (settings.DEBUG or settings.SAP_DEMO_MODE):
            raise CommandError("Requiere --confirm-fictitious y DEBUG=True o SAP_DEMO_MODE=True.")
        user = get_user_model().objects.select_for_update().filter(username=options["owner"], is_active=True).first()
        if user is None or user.is_staff or user.is_superuser:
            raise CommandError("Utiliza un agente activo sin acceso administrativo.")
        if not user.has_perms(["action_plans.add_improvementplan", "action_plans.close_improvementplan"]):
            raise CommandError("Configura primero los permisos del agente.")
        if timezone.localdate() < date(2026, 10, 23):
            raise CommandError("Los periodos ficticios de esta demo requieren fecha posterior al 22/10/2026.")
        for command in ["seed_demo", "seed_plan_demo"]:
            call_command(command, owner=user.username, allow_production=True, stdout=StringIO())
        today = timezone.localdate()
        for suffix, title, closed in [
            ("ACTIVO", "DEMO: mejorar incidencias con acciones pendientes", False),
            ("INSUFICIENTE", "DEMO: cierre documentado sin alcanzar el objetivo", True),
        ]:
            seller, _ = Seller.objects.get_or_create(reference=f"SAP-EVAL-{suffix}", defaults={"name": f"Tienda Ficticia {suffix.title()}", "owner": user})
            if seller.owner_id != user.pk:
                raise CommandError("Los datos demo pertenecen a otro usuario; se cancela toda la carga.")
            if seller.plans.exists():
                continue  # No reabre, cambia plazos ni sobrescribe el trabajo del evaluador.
            baseline, _ = QualityMetric.objects.get_or_create(seller=seller, policy=ThresholdPolicy.objects.get(code="incidents", version=1),
                channel="ficticio-es", period_start=date(2026, 7, 1), period_end=date(2026, 7, 31), defaults={"order_count": 100, "value": 6})
            plan = ImprovementPlan.objects.create(seller=seller, title=title, problem="Incidencias del 6% en una muestra ficticia.",
                root_cause="Embalaje insuficiente y revisión tardía de las recogidas.", evidence="Seis casos ficticios entre cien pedidos.",
                objective="Reducir las incidencias al 3%.", period_start=baseline.period_start, period_end=baseline.period_end,
                responsible=user, created_by=user, due_date=today + timedelta(days=30), next_review_on=today)
            metric = PlanMetric.objects.create(plan=plan, baseline=baseline, target_value=3)
            for offset, kind in [(-1, "corrective"), (7, "preventive")]:
                PlanAction.objects.create(plan=plan, description="Revisar embalajes." if offset < 0 else "Auditar recogidas semanales.",
                    kind=kind, responsible="Equipo ficticio de operaciones", due_date=today + timedelta(days=offset))
            plan.status = "in_progress"
            plan.save()
            PlanReview.objects.create(plan_metric=metric, recorded_by=user, reviewed_on=date(2026, 9, 1), value="4.5",
                period_start=date(2026, 8, 1), period_end=date(2026, 8, 31), order_count=100, comments="Mejora parcial ficticia.",
                assessment="on_track", next_steps="Continuar el seguimiento.")
            if closed:
                close_plan(plan_id=plan.pk, actor=user, notes="Cierre ficticio: resultado insuficiente (4,5% frente a 3%); se documenta un nuevo ciclo necesario.")
        self.stdout.write(self.style.SUCCESS("Demo lista: 5 vendedores, planes activos y cierres con objetivos alcanzados y pendientes. Los datos previos se conservan."))
