from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as ModelValidationError
from django.db import transaction
from django.db.models import Count, Prefetch, Q
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from action_plans.models import FINAL_STATUSES, ImprovementPlan, PlanAction, PlanMetric
from action_plans.serializers import MetricInputSerializer, PlanActionSerializer, PlanDetailSerializer, PlanReviewSerializer, PlanSummarySerializer, PlanWriteSerializer, model_error
from action_plans.services import close_plan, plans_with_history, visible_plans
from quality.serializers import QualityMetricSerializer
from quality.services import classify
from quality.views import latest_metrics
from sellers.models import visible_sellers


class WorkspacePagination(PageNumberPagination):
    page_size = 20


def require(user, *permissions):
    if not user.has_perms([f"action_plans.{permission}" for permission in permissions]):
        raise PermissionDenied("No tienes permiso para realizar esta operación.")


def summary_plans(user):
    return visible_plans(user).select_related("seller", "responsible").annotate(
        pending_actions=Count("actions", filter=Q(actions__status__in=["pending", "in_progress"])),
    ).order_by("-created_at", "-id").prefetch_related(
        Prefetch("metrics", queryset=PlanMetric.objects.select_related("baseline__policy", "baseline__seller")),
        Prefetch("actions", queryset=PlanAction.objects.filter(status__in=["pending", "in_progress"]).order_by("due_date", "id")[:1], to_attr="pending_action_list"),
    )


@method_decorator(never_cache, name="dispatch")
class PlanViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    pagination_class = WorkspacePagination
    filter_backends = [SearchFilter]
    search_fields = ["title", "seller__name", "seller__reference", "responsible__username"]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        require(request.user, "view_improvementplan")

    def get_queryset(self):
        qs = summary_plans(self.request.user) if self.action == "list" else plans_with_history(visible_plans(self.request.user))
        for key in ["seller", "responsible"]:
            value = self.request.query_params.get(key)
            if value:
                if not value.isdecimal():
                    raise serializers.ValidationError({key: "Identificador inválido."})
                qs = qs.filter(**{f"{key}_id": value})
        status = self.request.query_params.get("status")
        if status == "open":
            qs = qs.exclude(status__in=FINAL_STATUSES)
        elif status == "final":
            qs = qs.filter(status__in=FINAL_STATUSES)
        elif status:
            qs = qs.filter(status=status)
        if self.request.query_params.get("review") == "due":
            qs = qs.exclude(status__in=FINAL_STATUSES).filter(Q(status="in_review") | Q(next_review_on__lte=timezone.localdate()))
        return qs

    def get_serializer_class(self):
        return PlanSummarySerializer if self.action == "list" else PlanDetailSerializer

    def render_plan(self, plan_id, status=200):
        plan = plans_with_history(visible_plans(self.request.user)).get(pk=plan_id)
        return Response(PlanDetailSerializer(plan).data, status=status)

    def create(self, request, *args, **kwargs):
        require(request.user, "add_improvementplan", "add_planmetric")
        serializer = PlanWriteSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        plan = serializer.save(created_by=request.user)
        return self.render_plan(plan.pk, 201)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        require(request.user, "change_improvementplan")
        plan = get_object_or_404(visible_plans(request.user).select_for_update(), pk=kwargs["pk"])
        serializer = PlanWriteSerializer(plan, data=request.data, partial=True, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.render_plan(plan.pk)

    @action(detail=True, methods=["post"], url_path="actions")
    def add_action(self, request, pk=None):
        require(request.user, "add_planaction")
        plan = self.get_object()
        serializer = PlanActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(plan=plan)
        return self.render_plan(plan.pk, 201)

    @action(detail=True, methods=["patch"], url_path=r"actions/(?P<action_id>[0-9]+)")
    @transaction.atomic
    def edit_action(self, request, pk=None, action_id=None):
        require(request.user, "change_planaction")
        plan = get_object_or_404(visible_plans(request.user).select_for_update(), pk=pk)
        instance = get_object_or_404(PlanAction, plan=plan, pk=action_id)
        serializer = PlanActionSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.render_plan(plan.pk)

    @action(detail=True, methods=["post"], url_path="reviews")
    def add_review(self, request, pk=None):
        require(request.user, "add_planreview")
        plan = self.get_object()
        serializer = PlanReviewSerializer(data=request.data, context={"plan": plan})
        serializer.is_valid(raise_exception=True)
        serializer.save(recorded_by=request.user)
        return self.render_plan(plan.pk, 201)

    @action(detail=True, methods=["post"], url_path="metrics")
    def add_metric(self, request, pk=None):
        require(request.user, "add_planmetric")
        plan = self.get_object()
        serializer = MetricInputSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            PlanMetric.objects.create(plan=plan, **serializer.validated_data)
        except ModelValidationError as exc:
            raise model_error(exc) from exc
        return self.render_plan(plan.pk, 201)

    @action(detail=True, methods=["patch"], url_path=r"metrics/(?P<metric_id>[0-9]+)")
    @transaction.atomic
    def edit_metric(self, request, pk=None, metric_id=None):
        require(request.user, "change_planmetric")
        plan = get_object_or_404(visible_plans(request.user).select_for_update(), pk=pk)
        metric = get_object_or_404(PlanMetric, plan=plan, pk=metric_id)
        metric.target_value = serializers.DecimalField(max_digits=8, decimal_places=2).run_validation(request.data.get("target_value"))
        try:
            metric.save()
        except ModelValidationError as exc:
            raise model_error(exc) from exc
        return self.render_plan(plan.pk)

    @action(detail=True, methods=["post"], url_path="close")
    def close(self, request, pk=None):
        require(request.user, "change_improvementplan", "close_improvementplan")
        plan = self.get_object()
        if request.data.get("confirm") is not True:
            raise serializers.ValidationError({"confirm": "Confirma el cierre después de revisar los resultados."})
        notes = serializers.CharField().run_validation(request.data.get("notes", ""))
        try:
            close_plan(plan_id=plan.pk, actor=request.user, notes=notes, status=request.data.get("status", "closed"))
        except ModelValidationError as exc:
            raise model_error(exc) from exc
        return self.render_plan(plan.pk)


@never_cache
@api_view(["GET"])
def workspace(request):
    user = request.user
    names = ["view_improvementplan", "add_improvementplan", "change_improvementplan", "close_improvementplan", "add_planmetric", "change_planmetric", "add_planaction", "change_planaction", "add_planreview"]
    return Response({"id": user.pk, "name": user.get_full_name() or user.username,
        "username": user.username, "csrf_token": get_token(request), "today": timezone.localdate(),
        "permissions": {name: user.has_perm(f"action_plans.{name}") for name in names}})


@never_cache
@api_view(["GET"])
def responsibles(request):
    require(request.user, "view_improvementplan")
    users = get_user_model().objects.filter(is_active=True)
    if not request.user.is_superuser:
        users = users.filter(pk=request.user.pk)
    if request.query_params.get("search"):
        users = users.filter(username__icontains=request.query_params["search"])
    paginator = WorkspacePagination()
    page = paginator.paginate_queryset(users.order_by("username"), request)
    return paginator.get_paginated_response([{"id": user.pk, "name": user.get_full_name() or user.username} for user in page])


@never_cache
@api_view(["GET"])
def overview(request):
    today = timezone.localdate()
    sellers = visible_sellers(request.user)
    plans = visible_plans(request.user) if request.user.has_perm("action_plans.view_improvementplan") else ImprovementPlan.objects.none()
    opened = plans.exclude(status__in=FINAL_STATUSES)
    actions = PlanAction.objects.filter(plan__in=opened, status__in=["pending", "in_progress"])
    reviews = opened.filter(Q(status="in_review") | Q(next_review_on__lte=today))
    urgent = actions.filter(due_date__lte=today + timedelta(days=7)).select_related("plan__seller").order_by("due_date", "id")
    metrics = latest_metrics(sellers).select_related("seller", "policy")
    deviations = []
    affected = set()
    for metric in metrics.iterator():
        if classify(metric) in ["alarm", "suspension_threshold", "below_reference"]:
            affected.add(metric.seller_id)
            if len(deviations) < 10:
                deviations.append(metric)
    return Response({
        "today": today, "counts": {"sellers": sellers.count(), "open_plans": opened.count(), "pending_actions": actions.count(),
            "overdue_actions": actions.filter(due_date__lt=today).count(), "needs_review": reviews.count(),
            "closed_plans": plans.filter(status="closed").count(), "sellers_with_deviations": len(affected)},
        "priorities_count": urgent.count(), "priorities": [{**PlanActionSerializer(item).data,
            "plan": item.plan_id, "plan_title": item.plan.title, "seller": item.plan.seller_id, "seller_name": item.plan.seller.name} for item in urgent[:10]],
        "reviews_count": reviews.count(), "reviews": PlanSummarySerializer(summary_plans(request.user).filter(pk__in=reviews).order_by("next_review_on", "id")[:5], many=True).data,
        "deviations": QualityMetricSerializer(deviations, many=True).data,
        "recent_plans": PlanSummarySerializer(summary_plans(request.user).filter(pk__in=plans)[:5], many=True).data,
    })
