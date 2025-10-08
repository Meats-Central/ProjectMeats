"""
Serializers for Sales Orders app.
"""
from rest_framework import serializers
from .models import SalesOrder


class SalesOrderSerializer(serializers.ModelSerializer):
    """Serializer for SalesOrder model."""
    
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    carrier_name = serializers.CharField(source="carrier.name", read_only=True, allow_null=True)
    product_code = serializers.CharField(source="product.product_code", read_only=True, allow_null=True)

    class Meta:
        model = SalesOrder
        fields = [
            "id",
            "tenant",
            "our_sales_order_num",
            "date_time_stamp",
            "supplier",
            "supplier_name",
            "customer",
            "customer_name",
            "carrier",
            "carrier_name",
            "product",
            "product_code",
            "plant",
            "contact",
            "pick_up_date",
            "delivery_date",
            "delivery_po_num",
            "carrier_release_num",
            "quantity",
            "total_weight",
            "weight_unit",
            "status",
            "total_amount",
            "notes",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "date_time_stamp", "created_on", "modified_on"]
