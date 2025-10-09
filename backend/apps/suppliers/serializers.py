"""
Suppliers serializers for ProjectMeats.

Provides serialization for supplier API endpoints.
"""
from rest_framework import serializers
from apps.suppliers.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model."""

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "contact_person",
            "email",
            "phone",
            "address",
            "street_address",
            "city",
            "state",
            "zip_code",
            "country",
            "plant",
            "proteins",
            "edible_inedible",
            "type_of_plant",
            "type_of_certificate",
            "tested_product",
            "origin",
            "country_origin",
            "contacts",
            "shipping_offered",
            "how_to_book_pickup",
            "offer_contracts",
            "offers_export_documents",
            "accounting_terms",
            "accounting_line_of_credit",
            "credit_app_sent",
            "credit_app_set_up",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on"]

    def validate_name(self, value):
        """Validate supplier name is provided and is a valid string."""
        if not value or not isinstance(value, str) or not value.strip():
            raise serializers.ValidationError("Supplier name is required and must be a non-empty string.")
        return value.strip()

    def validate_email(self, value):
        """Validate email format if provided."""
        if value and '@' not in value:
            raise serializers.ValidationError("Invalid email format.")
        return value
