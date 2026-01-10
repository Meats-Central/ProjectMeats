"""
Suppliers serializers for ProjectMeats.

Provides serialization for supplier API endpoints.
"""
from rest_framework import serializers
from tenant_apps.suppliers.models import Supplier
from tenant_apps.locations.serializers import LocationListSerializer


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model."""
    
    # ArrayField serialization
    departments_array = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True,
    )
    
    # Nested locations (via reverse FK)
    locations = LocationListSerializer(many=True, read_only=True)

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
            "products",
            "shipping_offered",
            "how_to_book_pickup",
            "offer_contracts",
            "offers_export_documents",
            "accounting_payment_terms",
            "credit_limits",
            "account_line_of_credit",
            "fresh_or_frozen",
            "package_type",
            "net_or_catch",
            "departments",
            "departments_array",
            "locations",
            "accounting_terms",
            "accounting_line_of_credit",
            "credit_app_sent",
            "credit_app_set_up",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on", "locations"]

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
