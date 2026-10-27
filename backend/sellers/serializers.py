from rest_framework import serializers
from sellers.models import Seller


class SellerSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    open_plans = serializers.IntegerField(read_only=True)
    class Meta:
        model = Seller
        fields = ["id", "name", "reference", "created_at", "owner_name", "open_plans"]
        read_only_fields = ["id", "created_at"]
