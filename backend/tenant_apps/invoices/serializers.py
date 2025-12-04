"""
Serializers for Invoices app.
"""
from rest_framework import serializers
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model."""
    
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    sales_order_num = serializers.CharField(source="sales_order.our_sales_order_num", read_only=True, allow_null=True)
    product_code = serializers.CharField(source="product.product_code", read_only=True, allow_null=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "tenant",
            "invoice_number",
            "date_time_stamp",
            "customer",
            "customer_name",
            "sales_order",
            "sales_order_num",
            "product",
            "product_code",
            "pick_up_date",
            "delivery_date",
            "due_date",
            "our_sales_order_num",
            "delivery_po_num",
            "accounting_payable_contact_name",
            "accounting_payable_contact_phone",
            "accounting_payable_contact_email",
            "type_of_protein",
            "description_of_product_item",
            "quantity",
            "total_weight",
            "weight_unit",
            "edible_or_inedible",
            "tested_product",
            "unit_price",
            "total_amount",
            "tax_amount",
            "status",
            "notes",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "date_time_stamp", "created_on", "modified_on"]
