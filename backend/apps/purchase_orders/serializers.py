"""
Purchase Orders serializers for ProjectMeats.

Provides serialization for purchase order API endpoints.
"""
from rest_framework import serializers
from apps.purchase_orders.models import PurchaseOrder, PurchaseOrderHistory


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model."""

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "order_number",
            "supplier",
            "total_amount",
            "status",
            "order_date",
            "delivery_date",
            "notes",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on"]


class PurchaseOrderHistorySerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrderHistory model."""

    changed_by_username = serializers.CharField(
        source="changed_by.username", read_only=True, allow_null=True
    )
    purchase_order_number = serializers.CharField(
        source="purchase_order.order_number", read_only=True
    )

    class Meta:
        model = PurchaseOrderHistory
        fields = [
            "id",
            "purchase_order",
            "purchase_order_number",
            "changed_data",
            "changed_by",
            "changed_by_username",
            "change_type",
            "created_on",
            "modified_on",
        ]
        read_only_fields = [
            "id",
            "purchase_order",
            "changed_data",
            "changed_by",
            "change_type",
            "created_on",
            "modified_on",
        ]
