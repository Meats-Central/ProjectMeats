from rest_framework import serializers
from tenant_apps.carriers.models import Carrier


class CarrierSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )
    
    # ArrayField serialization
    departments_array = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True,
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
            "my_customer_num_from_carrier",
            "accounting_payable_contact_name",
            "accounting_payable_contact_phone",
            "accounting_payable_contact_email",
            "sales_contact_name",
            "sales_contact_phone",
            "sales_contact_email",
            "accounting_payment_terms",
            "credit_limits",
            "account_line_of_credit",
            "departments",
            "departments_array",
            "how_carrier_make_appointment",
            "contacts",
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
