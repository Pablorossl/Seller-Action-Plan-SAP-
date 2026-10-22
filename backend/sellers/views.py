from rest_framework import viewsets
from django.db.models.deletion import ProtectedError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework.response import Response
from sellers.models import visible_sellers
from sellers.serializers import SellerSerializer


@method_decorator(never_cache, name="dispatch")
class SellerViewSet(viewsets.ModelViewSet):
    serializer_class = SellerSerializer

    def get_queryset(self):
        return visible_sellers(self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({"detail": "El vendedor tiene indicadores históricos y no puede eliminarse."}, status=409)
