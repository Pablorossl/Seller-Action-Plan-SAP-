from rest_framework import viewsets
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from quality.models import QualityMetric
from quality.serializers import QualityMetricSerializer
from sellers.models import visible_sellers


@method_decorator(never_cache, name="dispatch")
class QualityMetricViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = QualityMetricSerializer

    def get_queryset(self):
        return QualityMetric.objects.filter(seller__in=visible_sellers(self.request.user)).select_related("seller", "policy")
