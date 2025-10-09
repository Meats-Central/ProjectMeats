from rest_framework import serializers
from apps.accounts_receivables.models import AccountsReceivable


class AccountsReceivableSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = AccountsReceivable
        fields = [
            "id",
            "customer",
            "customer_name",
            "invoice_number",
            "amount",
            "due_date",
            "status",
            "description",
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

    def validate_invoice_number(self, value):
        """Validate invoice number is provided and is a valid string."""
        if not value or not isinstance(value, str) or not value.strip():
            raise serializers.ValidationError("Invoice number is required and must be a non-empty string.")
        return value.strip()

    def validate_amount(self, value):
        """Validate amount is a positive number."""
        if value is None or value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
