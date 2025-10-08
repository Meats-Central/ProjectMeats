from rest_framework import serializers
from apps.carriers.models import Carrier


class CarrierSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Carrier
        fields = [
            "id",
            "name",
            "code",
            "carrier_type",
            "contact_person",
            "phone",
            "email",
            "address",
            "city",
            "state",
            "zip_code",
            "country",
            "mc_number",
            "dot_number",
            "insurance_provider",
            "insurance_policy_number",
            "insurance_expiry",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "created_by_name",
        ]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
