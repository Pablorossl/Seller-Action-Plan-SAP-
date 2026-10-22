from rest_framework import serializers
from sellers.models import Seller


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["id", "name", "reference", "created_at"]
        read_only_fields = ["id", "created_at"]
