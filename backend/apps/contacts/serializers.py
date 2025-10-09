"""
Contacts serializers for ProjectMeats.

Provides serialization for contact API endpoints.
"""
from rest_framework import serializers
from apps.contacts.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for Contact model."""

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "company",
            "position",
            "status",
            "created_on",
            "modified_on",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_on", "modified_on", "created_at", "updated_at"]

    def validate_first_name(self, value):
        """Validate first name is provided and is a valid string."""
        if not value or not isinstance(value, str) or not value.strip():
            raise serializers.ValidationError("First name is required and must be a non-empty string.")
        return value.strip()

    def validate_last_name(self, value):
        """Validate last name is provided and is a valid string."""
        if not value or not isinstance(value, str) or not value.strip():
            raise serializers.ValidationError("Last name is required and must be a non-empty string.")
        return value.strip()

    def validate_email(self, value):
        """Validate email format if provided."""
        if value and '@' not in value:
            raise serializers.ValidationError("Invalid email format.")
        return value
