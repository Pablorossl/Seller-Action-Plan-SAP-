from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from sellers.models import Seller
from quality.rules import MQC_MINIMUM_ORDERS, validate_value


class MetricCode(models.TextChoices):
    ACCEPTANCE = "acceptance", "Tasa de aceptación"
    INCIDENTS = "incidents", "Tasa de incidencias abiertas"
    TRACKING = "tracking", "Seguimiento válido"
    ACCEPTANCE_HOURS = "acceptance_hours", "Tiempo de aceptación"
    RESPONSE_HOURS = "response_hours", "Tiempo de respuesta"
    NPS = "nps", "NPS"
    DELIVERY = "delivery", "Eficiencia de entrega"


class ThresholdPolicy(models.Model):
    """Versión inmutable al utilizarse: preserva la evaluación histórica."""

    code = models.CharField(max_length=24, choices=MetricCode.choices)
    version = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit = models.CharField(max_length=8, choices=[("percent", "%"), ("hours", "h")])
    operator = models.CharField(max_length=3, choices=[("lt", "<"), ("gte", ">=")])
    alarm = models.DecimalField(max_digits=8, decimal_places=2)
    suspension = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    minimum_orders = models.PositiveIntegerField(default=30)
    is_mqc = models.BooleanField(default=True)

    class Meta:
        ordering = ["code", "version"]
        constraints = [
            models.UniqueConstraint(fields=["code", "version"], name="unique_policy_version"),
            models.CheckConstraint(condition=models.Q(operator__in=["lt", "gte"]), name="policy_operator"),
            models.CheckConstraint(condition=models.Q(unit__in=["percent", "hours"]), name="policy_unit"),
            models.CheckConstraint(condition=models.Q(version__gte=1), name="policy_positive_version"),
        ]

    def clean(self):
        super().clean()
        hours = self.code in [MetricCode.ACCEPTANCE_HOURS, MetricCode.RESPONSE_HOURS]
        if self.unit != ("hours" if hours else "percent"):
            raise ValidationError("Unidad incompatible con el indicador.")
        expected_operator = "gte" if hours or self.code == MetricCode.INCIDENTS else "lt"
        if self.operator != expected_operator:
            raise ValidationError("Comparador incompatible con el indicador.")
        if self.is_mqc != (self.code not in [MetricCode.NPS, MetricCode.DELIVERY]):
            raise ValidationError("NPS y entrega se evalúan fuera de MQC.")
        if self.is_mqc != (self.suspension is not None):
            raise ValidationError("Solo MQC requiere un umbral informativo de suspensión.")
        if self.is_mqc and self.minimum_orders is not None and self.minimum_orders < MQC_MINIMUM_ORDERS:
            raise ValidationError({"minimum_orders": "MQC requiere al menos 30 pedidos en el mes."})
        lower = -100 if self.code == MetricCode.NPS else 0
        for value in [self.alarm, self.suspension]:
            if value is not None and (value < lower or (not hours and value > 100)):
                raise ValidationError("Umbral fuera de rango.")
        if self.suspension is not None and (
            (self.operator == "lt" and self.suspension >= self.alarm)
            or (self.operator == "gte" and self.suspension <= self.alarm)
        ):
            raise ValidationError("La suspensión debe representar una desviación más grave.")
        if self.pk and self.metrics.exists():
            old = type(self).objects.get(pk=self.pk)
            fields = ["code", "version", "unit", "operator", "alarm", "suspension", "minimum_orders", "is_mqc"]
            if any(getattr(old, field) != getattr(self, field) for field in fields):
                raise ValidationError("Política utilizada: crea una nueva versión.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_code_display()} v{self.version}"


class QualityMetric(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT, related_name="metrics")
    policy = models.ForeignKey(ThresholdPolicy, on_delete=models.PROTECT, related_name="metrics")
    channel = models.CharField(max_length=40)
    period_start = models.DateField()
    period_end = models.DateField()
    order_count = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(-100)])
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller} · {self.policy} · {self.channel} · {self.period_start}/{self.period_end}: {self.value}"

    class Meta:
        ordering = ["-period_end", "seller_id", "id"]
        constraints = [
            models.CheckConstraint(condition=models.Q(period_end__gte=models.F("period_start")), name="metric_valid_period"),
            models.CheckConstraint(condition=models.Q(value__gte=-100), name="metric_min_value"),
            models.UniqueConstraint(fields=["seller", "policy", "channel", "period_start", "period_end"], name="unique_metric_observation"),
        ]

    def clean(self):
        super().clean()
        if not self.policy_id or self.value is None:
            return
        try:
            validate_value(self.policy, self.value)
        except ValidationError as exc:
            raise ValidationError({"value": exc.messages}) from exc
        if self.pk and self.plan_metrics.exists():
            old = type(self).objects.get(pk=self.pk)
            fields = ["seller_id", "policy_id", "channel", "period_start", "period_end", "order_count", "value"]
            if any(getattr(old, field) != getattr(self, field) for field in fields):
                raise ValidationError("Observación utilizada en un plan: registra una nueva observación.")
        if self.period_start and self.period_end and self.period_end < self.period_start:
            raise ValidationError({"period_end": "El fin debe ser igual o posterior al inicio."})
        duplicates = type(self).objects.filter(
            seller_id=self.seller_id, policy__code=self.policy.code, channel=self.channel,
            period_start=self.period_start, period_end=self.period_end,
        ).exclude(pk=self.pk)
        if duplicates.exists():
            raise ValidationError("Ya existe ese indicador, canal y periodo; no cambies la versión para duplicarlo.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
