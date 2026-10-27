"""Evaluación sin efectos externos y cierre autorizado de planes."""
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone

from action_plans.models import FINAL_STATUSES, ActionStatus, ImprovementPlan, PlanMetric, PlanReview, PlanStatus
from quality.services import classify
from sellers.models import visible_sellers


def visible_plans(user):
    return ImprovementPlan.objects.filter(seller__in=visible_sellers(user))


def plans_with_history(queryset):
    return queryset.select_related("seller", "responsible", "created_by").prefetch_related(
        "actions", Prefetch("metrics", queryset=PlanMetric.objects.select_related("baseline__policy", "baseline__seller").prefetch_related(
            Prefetch("reviews", queryset=PlanReview.objects.select_related("recorded_by")))),
    )


def evaluate_metric(metric: PlanMetric) -> dict:
    baseline = metric.baseline
    reviews = list(metric.reviews.all())  # Orden de medición, también con prefetch.
    latest = reviews[0] if reviews else None
    initial_classification = classify(baseline)
    classification = classify(latest) if latest else "not_evaluable"
    evaluable = latest is not None and classification not in ("not_evaluable", "insufficient_orders")
    comparable = evaluable and initial_classification not in ("not_evaluable", "insufficient_orders")
    decreases = baseline.policy.operator == "gte"
    achieved = (latest.value <= metric.target_value if decreases else latest.value >= metric.target_value) if evaluable else None
    improved = (latest.value < baseline.value if decreases else latest.value > baseline.value) if comparable else None
    return {
        "metric_id": metric.pk, "code": baseline.policy.code, "channel": baseline.channel,
        "unit": baseline.policy.unit, "initial": str(baseline.value), "target": str(metric.target_value),
        "current": str(latest.value) if latest and latest.value is not None else None,
        "review_id": latest.pk if latest else None,
        "period_end": latest.period_end.isoformat() if latest else None,
        "classification": classification, "improved": improved, "achieved": achieved,
    }


def evaluate_plan(plan: ImprovementPlan) -> dict:
    metrics = [evaluate_metric(metric) for metric in plan.metrics.all()]
    actions = list(plan.actions.all())
    if not metrics or any(metric["achieved"] is None for metric in metrics):
        result = "not_evaluable"
    else:
        result = "achieved" if all(metric["achieved"] for metric in metrics) else "not_achieved"
    return {
        "result": result, "metrics": metrics,
        "actions": {status: sum(action.status == status for action in actions) for status in ActionStatus.values},
        "overdue_actions": sum(action.is_overdue for action in actions),
    }


@transaction.atomic
def close_plan(*, plan_id: int, actor, notes: str, status: str = PlanStatus.CLOSED) -> ImprovementPlan:
    if not actor.is_active or not actor.has_perms(["action_plans.change_improvementplan", "action_plans.close_improvementplan"]):
        raise PermissionDenied("No tienes permiso para finalizar planes.")
    plan = visible_plans(actor).select_for_update().get(pk=plan_id)
    if status not in FINAL_STATUSES:
        raise ValidationError("La finalización debe ser un cierre o una cancelación.")
    if plan.status in FINAL_STATUSES:
        raise ValidationError("El plan ya está finalizado.")
    if not notes.strip():
        raise ValidationError("Documenta el resultado y las razones de la finalización.")
    plan.closure_evaluation = evaluate_plan(plan)
    plan.closure_notes = notes.strip()
    plan.closed_at = timezone.now()
    plan.next_review_on = None
    plan.status = status
    plan.save()
    return plan
