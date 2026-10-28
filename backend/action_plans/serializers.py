"""API de planes: permisos de relaciones y validación del dominio en los modelos."""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as ModelValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import APIException

from action_plans.models import ImprovementPlan, PlanAction, PlanMetric, PlanReview
from action_plans.services import evaluate_plan
from quality.models import QualityMetric
from quality.serializers import QualityMetricSerializer
from sellers.models import visible_sellers


def model_error(exc):
    from action_plans.concurrency import RevisionConflict
    if isinstance(exc, RevisionConflict):
        error = APIException(exc.messages[0])
        error.status_code = 409
        return error
    return serializers.ValidationError(getattr(exc, "message_dict", {"non_field_errors": exc.messages}))


class ValidatedModelSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except ModelValidationError as exc:
            raise model_error(exc) from exc

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except ModelValidationError as exc:
            raise model_error(exc) from exc


class PlanActionSerializer(ValidatedModelSerializer):
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = PlanAction
        fields = ["id", "revision", "description", "kind", "responsible", "due_date", "status", "completed_on", "notes", "evidence", "is_overdue"]
        read_only_fields = ["id", "revision"]


class PlanReviewSerializer(ValidatedModelSerializer):
    recorded_by_name = serializers.CharField(source="recorded_by.username", read_only=True)

    class Meta:
        model = PlanReview
        fields = ["id", "plan_metric", "reviewed_on", "recorded_by_name", "recorded_at", "value", "period_start", "period_end", "order_count", "comments", "assessment", "next_steps"]
        read_only_fields = ["id", "recorded_at"]
        # full_clean() aplica unicidad una vez resueltas las relaciones autorizadas.
        validators = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plan_metric"].queryset = PlanMetric.objects.filter(plan=self.context["plan"])


class MetricInputSerializer(serializers.Serializer):
    baseline = serializers.PrimaryKeyRelatedField(queryset=QualityMetric.objects.none())
    target_value = serializers.DecimalField(max_digits=8, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "request" in self.context:
            self.fields["baseline"].queryset = QualityMetric.objects.filter(seller__in=visible_sellers(self.context["request"].user))


class PlanMetricSerializer(serializers.ModelSerializer):
    baseline = QualityMetricSerializer(read_only=True)

    class Meta:
        model = PlanMetric
        fields = ["id", "revision", "baseline", "target_value"]


class PlanSummarySerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source="seller.name", read_only=True)
    seller_reference = serializers.CharField(source="seller.reference", read_only=True)
    responsible_name = serializers.CharField(source="responsible.username", read_only=True)
    metrics = PlanMetricSerializer(many=True, read_only=True)
    needs_review = serializers.BooleanField(read_only=True)
    next_action = serializers.SerializerMethodField()
    pending_actions = serializers.IntegerField(read_only=True)

    class Meta:
        model = ImprovementPlan
        fields = ["id", "revision", "seller", "seller_name", "seller_reference", "title", "objective", "status", "responsible", "responsible_name", "created_at", "due_date", "next_review_on", "needs_review", "metrics", "next_action", "pending_actions", "closure_evaluation"]

    def get_next_action(self, obj):
        actions = getattr(obj, "pending_action_list", [])
        return PlanActionSerializer(actions[0]).data if actions else None


class PlanDetailSerializer(PlanSummarySerializer):
    actions = PlanActionSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    evaluation = serializers.SerializerMethodField()

    class Meta(PlanSummarySerializer.Meta):
        fields = PlanSummarySerializer.Meta.fields + ["problem", "root_cause", "evidence", "period_start", "period_end", "closed_at", "closure_notes", "actions", "reviews", "evaluation"]

    def get_evaluation(self, obj):
        return evaluate_plan(obj)

    def get_reviews(self, obj):
        reviews = [review for metric in obj.metrics.all() for review in metric.reviews.all()]
        reviews.sort(key=lambda r: (r.period_end, r.reviewed_on, r.pk), reverse=True)
        return PlanReviewSerializer(reviews, many=True, context={"plan": obj}).data


class PlanWriteSerializer(ValidatedModelSerializer):
    metrics = serializers.ListField(child=serializers.DictField(), write_only=True, required=True, allow_empty=False)

    class Meta:
        model = ImprovementPlan
        fields = ["seller", "title", "problem", "period_start", "period_end", "root_cause", "evidence", "objective", "responsible", "due_date", "next_review_on", "status", "metrics"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context["request"].user
        self.fields["seller"].queryset = visible_sellers(user)
        users = get_user_model().objects.filter(is_active=True)
        self.fields["responsible"].queryset = users if user.is_superuser else users.filter(pk=user.pk)

    def validate_metrics(self, values):
        serializer = MetricInputSerializer(data=values, many=True, context=self.context)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def validate(self, attrs):
        if self.instance and "metrics" in attrs:
            raise serializers.ValidationError({"metrics": "Los indicadores iniciales se conservan. Crea otro plan para un nuevo diagnóstico."})
        if attrs.get("status") in ("closed", "cancelled"):
            raise serializers.ValidationError({"status": "Utiliza el cierre documentado del plan."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        metrics = validated_data.pop("metrics")
        plan = super().create(validated_data)
        for index, metric in enumerate(metrics):
            try:
                PlanMetric.objects.create(plan=plan, **metric)
            except ModelValidationError as exc:
                raise serializers.ValidationError({"metrics": {str(index): getattr(exc, "message_dict", {"non_field_errors": exc.messages})}}) from exc
        return plan
