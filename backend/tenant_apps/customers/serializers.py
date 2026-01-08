"""
Customers serializers for ProjectMeats.

Provides serialization for customer API endpoints.
"""
from rest_framework import serializers
from tenant_apps.customers.models import Customer
from tenant_apps.locations.serializers import LocationListSerializer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    # ArrayField serialization
    industry_array = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True,
    )
    preferred_protein_types = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True,
    )
    
    # Nested locations (via reverse FK)
    locations = LocationListSerializer(many=True, read_only=True)

    class Meta:
        model = Customer
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
            "purchasing_preference_origin",
            "industry",
            "industry_array",
            "preferred_protein_types",
            "contacts",
            "will_pickup_load",
            "locations",
            "accounting_payment_terms",
            "credit_limits",
            "account_line_of_credit",
            "buyer_contact_name",
            "buyer_contact_phone",
            "buyer_contact_email",
            "contact_title",
            "product_exportable",
            "accounting_terms",
            "accounting_line_of_credit",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on", "locations"]

    def validate_name(self, value):
        """Validate customer name is provided and is a valid string."""
        if not value or not isinstance(value, str) or not value.strip():
            raise serializers.ValidationError("Customer name is required and must be a non-empty string.")
        return value.strip()

    def validate_email(self, value):
        """Validate email format if provided."""
        if value and '@' not in value:
            raise serializers.ValidationError("Invalid email format.")
        return value
