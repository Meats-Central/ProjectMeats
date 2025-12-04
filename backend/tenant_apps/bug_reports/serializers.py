"""
Bug Reports serializers for ProjectMeats.
"""
from rest_framework import serializers
from .models import BugReport


class BugReportSerializer(serializers.ModelSerializer):
    """Serializer for BugReport model."""

    reporter_name = serializers.CharField(
        source="reporter.get_full_name", read_only=True
    )

    class Meta:
        model = BugReport
        fields = [
            "id",
            "title",
            "description",
            "category",
            "severity",
            "status",
            "reporter",
            "reporter_name",
            "reporter_email",
            "browser",
            "os",
            "screen_resolution",
            "url",
            "steps_to_reproduce",
            "expected_behavior",
            "actual_behavior",
            "created_at",
            "updated_at",
            "resolved_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        """Set reporter from request user if not provided."""
        if "reporter" not in validated_data and self.context.get("request"):
            validated_data["reporter"] = self.context["request"].user
        return super().create(validated_data)
