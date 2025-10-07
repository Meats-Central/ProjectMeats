from rest_framework import serializers
from apps.plants.models import Plant


class PlantSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = Plant
        fields = [
            "id",
            "name",
            "code",
            "plant_type",
            "address",
            "city",
            "state",
            "zip_code",
            "country",
            "phone",
            "email",
            "manager",
            "capacity",
            "is_active",
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
