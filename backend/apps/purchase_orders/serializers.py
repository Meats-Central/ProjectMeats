"""
Purchase Orders serializers for ProjectMeats.

Provides serialization for purchase order API endpoints.
"""
from rest_framework import serializers
from apps.purchase_orders.models import PurchaseOrder


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for PurchaseOrder model."""

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'total_amount', 'status',
            'order_date', 'delivery_date', 'notes', 'created_on', 'modified_on'
        ]
        read_only_fields = ['id', 'created_on', 'modified_on']
