from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from quality.models import QualityMetric
from quality.rules import validate_value
from sellers.models import Seller


class PlanStatus(models.TextChoices):
    DRAFT = "draft", "Borrador"
    IN_PROGRESS = "in_progress", "En progreso"
    IN_REVIEW = "in_review", "En revisión"
    CLOSED = "closed", "Cerrado"
    CANCELLED = "cancelled", "Cancelado"


FINAL_STATUSES = (PlanStatus.CLOSED, PlanStatus.CANCELLED)


class ImprovementPlan(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.PROTECT, related_name="plans", verbose_name="vendedor")
    title = models.CharField("título", max_length=200)
    problem = models.TextField("problema identificado")
    period_start = models.DateField("inicio del periodo de referencia")
    period_end = models.DateField("fin del periodo de referencia")
    root_cause = models.TextField("causa raíz")
    evidence = models.TextField("evidencia del diagnóstico")
    objective = models.TextField("objetivo de mejora")
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="assigned_plans", verbose_name="responsable del seguimiento")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="created_plans", editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField("finalización prevista")
    next_review_on = models.DateField("próxima revisión", null=True, blank=True)
    status = models.CharField("estado", max_length=16, choices=PlanStatus.choices, default=PlanStatus.DRAFT, db_index=True)
    closed_at = models.DateTimeField("fecha real de finalización", null=True, blank=True, editable=False)
    closure_notes = models.TextField("resultado y razones del cierre", blank=True, editable=False)
    closure_evaluation = models.JSONField("evaluación medida al finalizar", default=dict, blank=True, editable=False)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "plan de mejora"
        verbose_name_plural = "planes de mejora"
        permissions = [("close_improvementplan", "Puede cerrar o cancelar planes de mejora")]
        indexes = [models.Index(fields=["seller", "status"])]
        constraints = [
            models.CheckConstraint(condition=models.Q(period_end__gte=models.F("period_start")), name="plan_valid_period"),
            models.CheckConstraint(condition=models.Q(due_date__gte=models.F("period_end")), name="plan_valid_due_date"),
            models.CheckConstraint(condition=models.Q(status__in=PlanStatus.values), name="plan_valid_status"),
            models.CheckConstraint(condition=(
                models.Q(status__in=FINAL_STATUSES, closed_at__isnull=False) & ~models.Q(closure_notes="")
            ) | (~models.Q(status__in=FINAL_STATUSES) & models.Q(closed_at__isnull=True)), name="plan_consistent_closure"),
        ]

    def __str__(self):
        return f"#{self.pk} · {self.title}"

    @property
    def needs_review(self):
        return self.status not in FINAL_STATUSES and (
            self.status == PlanStatus.IN_REVIEW or bool(self.next_review_on and self.next_review_on <= timezone.localdate())
        )

    def clean(self):
        super().clean()
        if self.period_start and self.period_end and self.period_end < self.period_start:
            raise ValidationError({"period_end": "El fin no puede preceder al inicio."})
        if self.due_date and self.period_end and self.due_date < self.period_end:
            raise ValidationError({"due_date": "El plazo no puede preceder al periodo de referencia."})
        if self.next_review_on and self.period_end and self.next_review_on < self.period_end:
            raise ValidationError({"next_review_on": "La revisión no puede preceder al periodo de referencia."})
        if self.status in FINAL_STATUSES:
            if not self.closed_at or not self.closure_notes.strip() or not self.closure_evaluation:
                raise ValidationError("Finaliza el plan mediante la operación de cierre y documenta el resultado.")
            if self.closed_at > timezone.now() or (self.created_at and self.closed_at < self.created_at):
                raise ValidationError("Fecha real de cierre incoherente.")
        elif self.closed_at or self.closure_notes or self.closure_evaluation:
            raise ValidationError("Un plan abierto no puede tener datos de cierre.")
        old = type(self).objects.filter(pk=self.pk).first() if self.pk else None
        if old:
            if old.status in FINAL_STATUSES:
                raise ValidationError("Un plan finalizado conserva su histórico y no puede modificarse.")
            if self.seller_id != old.seller_id or self.created_by_id != old.created_by_id:
                raise ValidationError("El vendedor y el autor de un plan son inmutables.")
            transitions = {
                PlanStatus.DRAFT: {PlanStatus.DRAFT, PlanStatus.IN_PROGRESS, PlanStatus.CANCELLED},
                PlanStatus.IN_PROGRESS: {PlanStatus.IN_PROGRESS, PlanStatus.IN_REVIEW, *FINAL_STATUSES},
                PlanStatus.IN_REVIEW: {PlanStatus.IN_REVIEW, PlanStatus.IN_PROGRESS, *FINAL_STATUSES},
            }
            if self.status not in transitions[old.status]:
                raise ValidationError({"status": "Transición de estado no permitida."})
        elif self.status != PlanStatus.DRAFT:
            raise ValidationError({"status": "Crea primero un borrador con sus indicadores y acciones."})
        if self.status in (PlanStatus.IN_PROGRESS, PlanStatus.IN_REVIEW, PlanStatus.CLOSED):
            if not self.pk or not self.metrics.exists() or not self.actions.exists():
                raise ValidationError("El plan necesita al menos un indicador con objetivo y una acción antes de activarse.")
        if self.pk:
            for metric in self.metrics.select_related("baseline"):
                if metric.baseline.period_start != self.period_start or metric.baseline.period_end != self.period_end:
                    raise ValidationError("El periodo de referencia debe coincidir con los indicadores iniciales.")
            if self.due_date and self.period_end and self.actions.filter(
                models.Q(due_date__lt=self.period_end) | models.Q(due_date__gt=self.due_date)
            ).exists():
                raise ValidationError({"due_date": "El plazo debe incluir las fechas límite de las acciones existentes."})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                type(self).objects.select_for_update().get(pk=self.pk)
            self.full_clean()
            return super().save(*args, **kwargs)


class PlanChild(models.Model):
    """Las escrituras hijas se serializan con el cierre usando el mismo bloqueo."""
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.parent_plan_id:
                ImprovementPlan.objects.select_for_update().filter(pk=self.parent_plan_id).first()
            self.full_clean()
            return super().save(*args, **kwargs)

    def validate_open_plan(self):
        plan = ImprovementPlan.objects.filter(pk=self.parent_plan_id).first()
        if plan and plan.status in FINAL_STATUSES:
            raise ValidationError("No se puede modificar un plan finalizado.")
        return plan


class PlanMetric(PlanChild):
    plan = models.ForeignKey(ImprovementPlan, on_delete=models.PROTECT, related_name="metrics", verbose_name="plan")
    baseline = models.ForeignKey(QualityMetric, on_delete=models.PROTECT, related_name="plan_metrics", verbose_name="indicador inicial")
    target_value = models.DecimalField("objetivo medible", max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "objetivo por indicador"
        verbose_name_plural = "objetivos por indicador"
        constraints = [models.UniqueConstraint(fields=["plan", "baseline"], name="unique_plan_baseline")]

    @property
    def parent_plan_id(self):
        return self.plan_id

    def __str__(self):
        return f"{self.plan} · {self.baseline.policy.get_code_display()} · {self.baseline.channel}"

    def clean(self):
        super().clean()
        plan = self.validate_open_plan()
        baseline = QualityMetric.objects.select_related("policy").filter(pk=self.baseline_id).first()
        if not plan or not baseline:
            return  # full_clean informa las FK inexistentes.
        if baseline.seller_id != plan.seller_id:
            raise ValidationError({"baseline": "El indicador debe pertenecer al vendedor del plan."})
        if (baseline.period_start, baseline.period_end) != (plan.period_start, plan.period_end):
            raise ValidationError({"baseline": "El indicador debe coincidir con el periodo de referencia."})
        if self.target_value is not None:
            try:
                validate_value(baseline.policy, self.target_value)
            except ValidationError as exc:
                raise ValidationError({"target_value": exc.messages}) from exc
            improves = self.target_value < baseline.value if baseline.policy.operator == "gte" else self.target_value > baseline.value
            if not improves:
                raise ValidationError({"target_value": "El objetivo debe mejorar el valor inicial en la dirección del indicador."})
        if type(self).objects.filter(plan=plan, baseline__policy__code=baseline.policy.code,
            baseline__channel=baseline.channel).exclude(pk=self.pk).exists():
            raise ValidationError("Ese indicador y canal ya tienen un objetivo en el plan.")
        if self.pk:
            old = type(self).objects.get(pk=self.pk)
            if old.plan_id != self.plan_id or old.baseline_id != self.baseline_id:
                raise ValidationError("No se puede mover un objetivo a otro plan o indicador.")
            if old.target_value != self.target_value and (plan.status != PlanStatus.DRAFT or self.reviews.exists()):
                raise ValidationError("El objetivo queda fijado al activar el plan o registrar revisiones.")


class ActionStatus(models.TextChoices):
    PENDING = "pending", "Pendiente"
    IN_PROGRESS = "in_progress", "En progreso"
    COMPLETED = "completed", "Completada"
    CANCELLED = "cancelled", "Cancelada"


class PlanAction(PlanChild):
    plan = models.ForeignKey(ImprovementPlan, on_delete=models.PROTECT, related_name="actions", verbose_name="plan")
    description = models.TextField("descripción")
    kind = models.CharField("tipo", max_length=12, choices=[("corrective", "Correctiva"), ("preventive", "Preventiva")])
    responsible = models.CharField("persona o equipo responsable", max_length=160)
    due_date = models.DateField("fecha límite", db_index=True)
    status = models.CharField("estado", max_length=16, choices=ActionStatus.choices, default=ActionStatus.PENDING, db_index=True)
    completed_on = models.DateField("fecha de finalización", null=True, blank=True)
    notes = models.TextField("observaciones", blank=True)
    evidence = models.TextField("evidencia de ejecución", blank=True)

    class Meta:
        ordering = ["due_date", "id"]
        verbose_name = "acción del plan"
        verbose_name_plural = "acciones del plan"
        constraints = [
            models.CheckConstraint(condition=models.Q(status__in=ActionStatus.values), name="action_valid_status"),
            models.CheckConstraint(condition=models.Q(kind__in=["corrective", "preventive"]), name="action_valid_kind"),
            models.CheckConstraint(condition=models.Q(status="completed", completed_on__isnull=False)
                | (~models.Q(status="completed") & models.Q(completed_on__isnull=True)), name="action_consistent_completion"),
        ]

    @property
    def parent_plan_id(self):
        return self.plan_id

    @property
    def is_overdue(self):
        return self.status in (ActionStatus.PENDING, ActionStatus.IN_PROGRESS) and self.due_date < timezone.localdate()

    def __str__(self):
        return self.description[:100]

    def clean(self):
        super().clean()
        plan = self.validate_open_plan()
        if plan and self.due_date and not plan.period_end <= self.due_date <= plan.due_date:
            raise ValidationError({"due_date": "El plazo debe estar entre el periodo de referencia y el fin previsto del plan."})
        if (self.status == ActionStatus.COMPLETED) != (self.completed_on is not None):
            raise ValidationError({"completed_on": "Solo las acciones completadas requieren fecha de finalización."})
        if self.completed_on and (self.completed_on > timezone.localdate() or (plan and self.completed_on < plan.period_end)):
            raise ValidationError({"completed_on": "Fecha de finalización incoherente."})
        if self.status == ActionStatus.COMPLETED and not self.evidence.strip():
            raise ValidationError({"evidence": "Documenta la evidencia de ejecución."})
        if self.pk:
            old = type(self).objects.get(pk=self.pk)
            if old.plan_id != self.plan_id:
                raise ValidationError("No se puede mover una acción a otro plan.")
            if old.status in (ActionStatus.COMPLETED, ActionStatus.CANCELLED) and old.status != self.status:
                raise ValidationError({"status": "Una acción finalizada no puede reabrirse."})


class PlanReview(PlanChild):
    plan_metric = models.ForeignKey(PlanMetric, on_delete=models.PROTECT, related_name="reviews", verbose_name="objetivo evaluado")
    reviewed_on = models.DateField("fecha de revisión", default=timezone.localdate)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="plan_reviews", editable=False)
    recorded_at = models.DateTimeField(auto_now_add=True)
    value = models.DecimalField("valor observado", max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Vacío si no hay datos; el resultado será no evaluable.")
    period_start = models.DateField("inicio de medición")
    period_end = models.DateField("fin de medición")
    order_count = models.PositiveIntegerField("pedidos del canal en el periodo", null=True, blank=True)
    comments = models.TextField("evolución y evidencias")
    assessment = models.CharField("valoración del agente", max_length=16,
        choices=[("on_track", "Evolución favorable"), ("at_risk", "En riesgo"), ("no_progress", "Sin progreso"), ("no_data", "Sin datos suficientes")])
    next_steps = models.TextField("próximos pasos", blank=True)

    class Meta:
        ordering = ["-period_end", "-reviewed_on", "-id"]
        verbose_name = "revisión del plan"
        verbose_name_plural = "revisiones del plan"
        constraints = [
            models.CheckConstraint(condition=models.Q(period_end__gte=models.F("period_start")), name="review_valid_period"),
            models.CheckConstraint(condition=models.Q(reviewed_on__gte=models.F("period_end")), name="review_after_measurement"),
            models.CheckConstraint(condition=models.Q(assessment__in=["on_track", "at_risk", "no_progress", "no_data"]), name="review_valid_assessment"),
            models.UniqueConstraint(fields=["plan_metric", "period_start", "period_end"], name="unique_review_measurement"),
        ]

    @property
    def parent_plan_id(self):
        return PlanMetric.objects.filter(pk=self.plan_metric_id).values_list("plan_id", flat=True).first()

    @property
    def policy(self):
        return self.plan_metric.baseline.policy

    @property
    def unit(self):
        return self.policy.unit

    def __str__(self):
        return f"{self.plan_metric} · {self.reviewed_on}"

    def clean(self):
        super().clean()
        self.validate_open_plan()
        if self.pk:
            raise ValidationError("Las revisiones son históricas: registra una nueva revisión.")
        metric = PlanMetric.objects.select_related("baseline__policy").filter(pk=self.plan_metric_id).first()
        if metric:
            try:
                validate_value(metric.baseline.policy, self.value)
            except ValidationError as exc:
                raise ValidationError({"value": exc.messages}) from exc
            if self.period_end and self.period_end <= metric.baseline.period_end:
                raise ValidationError({"period_end": "La medición debe ser posterior al indicador inicial."})
        if self.period_start and self.period_end and self.period_end < self.period_start:
            raise ValidationError({"period_end": "El fin no puede preceder al inicio."})
        if self.reviewed_on and (self.reviewed_on > timezone.localdate() or (self.period_end and self.reviewed_on < self.period_end)):
            raise ValidationError({"reviewed_on": "La revisión debe seguir a la medición y no estar en el futuro."})
