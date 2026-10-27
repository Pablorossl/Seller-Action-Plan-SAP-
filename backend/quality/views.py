from rest_framework import viewsets
from django.db.models import OuterRef, Subquery
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from quality.models import QualityMetric
from quality.serializers import QualityMetricSerializer
from sellers.models import visible_sellers


def latest_metrics(sellers):
    latest = QualityMetric.objects.filter(seller_id=OuterRef("seller_id"),
        policy__code=OuterRef("policy__code"), channel=OuterRef("channel")).order_by("-period_end", "-id")
    return QualityMetric.objects.filter(seller__in=sellers, pk=Subquery(latest.values("pk")[:1]))


@method_decorator(never_cache, name="dispatch")
class QualityMetricViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QualityMetricSerializer

    def get_queryset(self):
        sellers = visible_sellers(self.request.user)
        qs = latest_metrics(sellers) if self.request.query_params.get("latest") == "1" else QualityMetric.objects.filter(seller__in=sellers)
        seller = self.request.query_params.get("seller")
        if seller:
            if not seller.isdecimal():
                return qs.none()
            qs = qs.filter(seller_id=seller)
        return qs.select_related("seller", "policy")
