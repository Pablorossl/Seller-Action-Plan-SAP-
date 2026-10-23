from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from quality.models import QualityMetric, ThresholdPolicy
from sellers.models import AGENT_GROUP, Seller
from quality.rules import DEFAULT_POLICIES as POLICIES
from quality.rules import MQC_MINIMUM_ORDERS


class Command(BaseCommand):
    help = "Carga datos ficticios idempotentes para un usuario existente; solo DEBUG=True."

    def add_arguments(self, parser):
        parser.add_argument("--owner", required=True, help="Username existente; no crea credenciales.")

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Los datos demo solo se cargan en desarrollo.")
        try:
            owner = get_user_model().objects.get(username=options["owner"])
        except get_user_model().DoesNotExist as exc:
            raise CommandError("Crea primero el usuario indicado.") from exc
        group, _ = Group.objects.get_or_create(name=AGENT_GROUP)
        owner.groups.add(group)
        policies = []
        for code, unit, operator, alarm, suspension, is_mqc in POLICIES:
            policy, _ = ThresholdPolicy.objects.get_or_create(code=code, version=1, defaults={
                "unit": unit, "operator": operator, "alarm": Decimal(alarm),
                "suspension": Decimal(suspension) if suspension else None,
                "is_mqc": is_mqc, "minimum_orders": MQC_MINIMUM_ORDERS if is_mqc else 0,
            })
            policies.append(policy)
        for reference, name, values in [
            ("DEMO-001", "Tienda Demo Norte", ["98.50", "4", "91", "19.99", "24", "64", "90"]),
            ("DEMO-002", "Tienda Demo Sur", ["99", "2", "95", "12", "10", "70", "96"]),
        ]:
            seller, created = Seller.objects.get_or_create(reference=reference, defaults={"name": name, "owner": owner})
            if not created and seller.owner_id != owner.pk:
                raise CommandError("La demo pertenece a otro usuario; no se reasignarán datos.")
            for policy, value in zip(policies, values):
                QualityMetric.objects.get_or_create(
                    seller=seller, policy=policy, channel="demo-es",
                    period_start=date(2026, 9, 1), period_end=date(2026, 9, 30),
                    defaults={"order_count": 50, "value": Decimal(value)},
                )
        self.stdout.write(self.style.SUCCESS("Demo lista: 2 vendedores, 14 observaciones ficticias; sin contraseñas creadas."))
