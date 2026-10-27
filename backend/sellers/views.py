from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.response import Response
from sellers.models import visible_sellers
from sellers.serializers import SellerSerializer
from quality.models import MetricCode


@method_decorator(never_cache, name="dispatch")
class SellerViewSet(viewsets.ModelViewSet):
    serializer_class = SellerSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name", "reference"]

    def get_queryset(self):
        qs = visible_sellers(self.request.user).select_related("owner").annotate(
            open_plans=Count("plans", filter=~Q(plans__status__in=["closed", "cancelled"])))
        if self.request.query_params.get("active_plans") == "1":
            qs = qs.filter(open_plans__gt=0)
        elif self.request.query_params.get("active_plans") == "0":
            qs = qs.filter(open_plans=0)
        return qs.order_by("name", "id")

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        seller = self.get_object()
        data = self.get_serializer(seller).data
        recorded = set(seller.metrics.values_list("policy__code", flat=True).distinct())
        data["missing_indicators"] = [{"code": code, "label": label} for code, label in MetricCode.choices if code not in recorded]
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({"detail": "El vendedor tiene indicadores o planes históricos y no puede eliminarse."}, status=409)
