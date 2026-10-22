from django.contrib import admin
from quality.models import QualityMetric, ThresholdPolicy
from sellers.admin import SuperuserOnlyAdmin


@admin.register(ThresholdPolicy)
class ThresholdPolicyAdmin(SuperuserOnlyAdmin):
    list_display = ["code", "version", "alarm", "suspension", "minimum_orders"]
    search_fields = ["code"]


@admin.register(QualityMetric)
class QualityMetricAdmin(SuperuserOnlyAdmin):
    list_display = ["seller", "policy", "channel", "period_end", "value"]
    search_fields = ["seller__name", "channel"]
