from rest_framework import serializers
from quality.models import QualityMetric
from quality.services import classify


class QualityMetricSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source="policy.code", read_only=True)
    label = serializers.CharField(source="policy.get_code_display", read_only=True)
    unit = serializers.CharField(source="policy.unit", read_only=True)
    policy_version = serializers.IntegerField(source="policy.version", read_only=True)
    seller_name = serializers.CharField(source="seller.name", read_only=True)
    classification = serializers.SerializerMethodField()

    class Meta:
        model = QualityMetric
        fields = ["id", "seller", "seller_name", "code", "label", "unit", "policy_version",
                  "channel", "period_start", "period_end", "order_count", "value", "classification"]

    def get_classification(self, obj):
        return classify(obj)
