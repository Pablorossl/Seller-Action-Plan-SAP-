from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html_join

from action_plans.forms import ClosePlanForm, ImprovementPlanForm
from action_plans.models import FINAL_STATUSES, ImprovementPlan, PlanAction, PlanMetric, PlanReview
from action_plans.services import close_plan, evaluate_plan, plans_with_history, visible_plans
from quality.models import QualityMetric
from sellers.models import AGENT_GROUP, visible_sellers


class ScopedPlanAdmin(admin.ModelAdmin):
    seller_path = "seller"

    def allowed(self, request):
        user = request.user
        return user.is_active and (user.is_superuser or user.groups.filter(name=AGENT_GROUP).exists())

    def get_queryset(self, request):
        return super().get_queryset(request).filter(**{f"{self.seller_path}__in": visible_sellers(request.user)})

    def has_module_permission(self, request):
        return self.allowed(request) and super().has_module_permission(request)

    def can_access(self, request, obj):
        if not self.allowed(request):
            return False
        return obj is None or self.get_queryset(request).filter(pk=obj.pk).exists()

    def has_view_permission(self, request, obj=None):
        return self.can_access(request, obj) and super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        return self.allowed(request) and super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if not self.can_access(request, obj) or not super().has_change_permission(request, obj):
            return False
        if obj is None:
            return True
        plan = obj if isinstance(obj, ImprovementPlan) else (obj.plan_metric.plan if isinstance(obj, PlanReview) else obj.plan)
        return plan.status not in FINAL_STATUSES

    def has_delete_permission(self, request, obj=None):
        return False  # Se cancelan; nunca se destruye el histórico desde la interfaz.

    def lookup_allowed(self, lookup, value, request):
        if lookup == "plan_metric__plan__id__exact":
            return True  # El queryset sigue limitado al vendedor autorizado.
        return super().lookup_allowed(lookup, value, request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "seller":
            kwargs["queryset"] = visible_sellers(request.user)
        elif db_field.name == "plan":
            kwargs["queryset"] = visible_plans(request.user).exclude(status__in=FINAL_STATUSES)
        elif db_field.name == "baseline":
            kwargs["queryset"] = QualityMetric.objects.filter(seller__in=visible_sellers(request.user)).select_related("seller", "policy")
        elif db_field.name == "plan_metric":
            kwargs["queryset"] = PlanMetric.objects.filter(plan__in=visible_plans(request.user).exclude(status__in=FINAL_STATUSES)).select_related("plan", "baseline__policy")
        elif db_field.name == "responsible":
            users = get_user_model().objects.filter(is_active=True)
            kwargs["queryset"] = users if request.user.is_superuser else users.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ImprovementPlan)
class ImprovementPlanAdmin(ScopedPlanAdmin):
    form = ImprovementPlanForm
    change_form_template = "admin/action_plans/improvementplan/change_form.html"
    list_display = ["id", "title", "seller", "responsible", "status", "due_date", "pending_review"]
    list_filter = ["status"]
    search_fields = ["title", "seller__name", "seller__reference"]
    readonly_fields = ["created_by", "created_at", "closed_at", "closure_notes", "measured_result", "action_summary", "related_records"]

    def get_queryset(self, request):
        return plans_with_history(super().get_queryset(request))

    @admin.display(boolean=True, description="Pendiente de revisión")
    def pending_review(self, obj):
        return obj.needs_review

    @admin.display(description="Inicial → objetivo → actual")
    def measured_result(self, obj):
        if not obj or not obj.pk:
            return "Guarda el borrador y añade indicadores con sus objetivos."
        evaluation = obj.closure_evaluation or evaluate_plan(obj)
        labels = {True: "alcanzado", False: "pendiente", None: "no evaluable"}
        return format_html_join("", "<p>{} / {}: {} → {} → {} {} · Objetivo {} · Mejora: {}</p>", (
            (row["code"], row["channel"], row["initial"], row["target"], row["current"] if row["current"] is not None else "sin datos",
                "h" if row["unit"] == "hours" else "%", labels[row["achieved"]], {True: "sí", False: "no", None: "no evaluable"}[row["improved"]])
            for row in evaluation["metrics"]
        )) or "Sin indicadores asociados."

    @admin.display(description="Acciones y resultado")
    def action_summary(self, obj):
        if not obj or not obj.pk:
            return "Sin acciones."
        evaluation = obj.closure_evaluation or evaluate_plan(obj)
        counts = evaluation["actions"]
        result = {"achieved": "Objetivos alcanzados", "not_achieved": "Objetivos pendientes", "not_evaluable": "Resultado no evaluable"}[evaluation["result"]]
        return f"{result}. Pendientes: {counts['pending']}; en progreso: {counts['in_progress']}; completadas: {counts['completed']}; canceladas: {counts['cancelled']}; vencidas: {evaluation['overdue_actions']}."

    @admin.display(description="Acciones, objetivos y revisiones")
    def related_records(self, obj):
        if not obj or not obj.pk:
            return "Guarda primero el borrador."
        links = []
        for model, field, label in [(PlanMetric, "plan__id__exact", "Objetivos"), (PlanAction, "plan__id__exact", "Acciones"),
            (PlanReview, "plan_metric__plan__id__exact", "Histórico de revisiones")]:
            links.append((reverse(f"admin:action_plans_{model._meta.model_name}_changelist") + f"?{field}={obj.pk}", label))
        return format_html_join(" · ", '<a href="{}">{}</a>', links)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_urls(self):
        return [path("<int:object_id>/close/", self.admin_site.admin_view(self.close_view), name="action_plans_improvementplan_close")] + super().get_urls()

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = {**(extra_context or {}), "can_close": request.user.has_perm("action_plans.close_improvementplan")}
        return super().change_view(request, object_id, form_url, extra_context)

    def close_view(self, request, object_id):
        plan = self.get_object(request, object_id)
        if plan is None:
            raise Http404
        if not self.has_change_permission(request, plan) or not request.user.has_perm("action_plans.close_improvementplan"):
            raise PermissionDenied
        form = ClosePlanForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            try:
                close_plan(plan_id=plan.pk, actor=request.user, **form.cleaned_data)
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                self.message_user(request, "Plan finalizado con su resultado medido y sus razones.", messages.SUCCESS)
                return HttpResponseRedirect(reverse("admin:action_plans_improvementplan_change", args=[plan.pk]))
        return TemplateResponse(request, "admin/action_plans/close_plan.html", {
            **self.admin_site.each_context(request), "title": f"Finalizar {plan}", "opts": self.model._meta,
            "original": plan, "form": form, "summary": self.action_summary(plan),
        })


@admin.register(PlanMetric)
class PlanMetricAdmin(ScopedPlanAdmin):
    seller_path = "plan__seller"
    list_display = ["plan", "baseline", "target_value"]
    list_select_related = ["plan", "baseline__policy", "baseline__seller"]
    search_fields = ["plan__title", "plan__seller__name", "baseline__policy__code"]


class OverdueFilter(admin.SimpleListFilter):
    title = "vencimiento"
    parameter_name = "overdue"

    def lookups(self, request, model_admin):
        return [("yes", "Acciones vencidas")]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(due_date__lt=timezone.localdate(), status__in=["pending", "in_progress"])
        return queryset


@admin.register(PlanAction)
class PlanActionAdmin(ScopedPlanAdmin):
    seller_path = "plan__seller"
    list_display = ["description", "plan", "kind", "responsible", "status", "due_date", "overdue"]
    list_select_related = ["plan"]
    list_filter = ["status", "kind", OverdueFilter]
    search_fields = ["description", "plan__title", "plan__seller__name", "responsible"]

    @admin.display(boolean=True, description="Vencida")
    def overdue(self, obj):
        return obj.is_overdue


@admin.register(PlanReview)
class PlanReviewAdmin(ScopedPlanAdmin):
    seller_path = "plan_metric__plan__seller"
    list_display = ["plan_metric", "reviewed_on", "value", "measurement_unit", "period_start", "period_end", "recorded_by", "assessment"]
    list_select_related = ["plan_metric__plan", "plan_metric__baseline__policy", "recorded_by"]
    list_filter = ["assessment"]
    search_fields = ["plan_metric__plan__title", "plan_metric__plan__seller__name", "comments"]
    readonly_fields = ["recorded_by", "recorded_at", "measurement_unit"]

    @admin.display(description="Unidad")
    def measurement_unit(self, obj):
        return ("h" if obj.unit == "hours" else "%") if obj and obj.plan_metric_id else "La del indicador seleccionado (% o h)."

    def has_change_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.recorded_by = request.user
        super().save_model(request, obj, form, change)
