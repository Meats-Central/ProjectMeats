"""
Serializers for Invoices app.
"""
from rest_framework import serializers
from .models import Invoice, Claim, PaymentTransaction


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
            "payment_status",
            "outstanding_amount",
            "notes",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "date_time_stamp", "created_on", "modified_on"]


class ClaimSerializer(serializers.ModelSerializer):
    """Serializer for Claim model."""
    
    created_by_name = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Claim
        fields = [
            "id",
            "claim_number",
            "claim_type",
            "status",
            "supplier",
            "customer",
            "purchase_order",
            "sales_order",
            "invoice",
            "reason",
            "description",
            "claimed_amount",
            "approved_amount",
            "settled_amount",
            "claim_date",
            "resolution_date",
            "resolution_notes",
            "assigned_to",
            "assigned_to_name",
            "created_by",
            "created_by_name",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on", "assigned_to_name", "created_by_name"]
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created this claim."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return "System"
    
    def get_assigned_to_name(self, obj):
        """Get the name of the user this claim is assigned to."""
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
        return None


class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for PaymentTransaction model."""
    
    created_by_name = serializers.SerializerMethodField()
    entity_type = serializers.SerializerMethodField()
    entity_reference = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'tenant', 'purchase_order', 'sales_order', 'invoice',
            'amount', 'payment_date', 'payment_method', 'reference_number',
            'notes', 'created_by', 'created_by_name', 'created_on', 'updated_on',
            'entity_type', 'entity_reference'
        ]
        read_only_fields = ['id', 'tenant', 'created_on', 'updated_on', 'created_by_name', 'entity_type', 'entity_reference']
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created the payment."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return "System"
    
    def get_entity_type(self, obj):
        """Determine what type of entity this payment is for."""
        if obj.purchase_order:
            return "purchase_order"
        elif obj.sales_order:
            return "sales_order"
        elif obj.invoice:
            return "invoice"
        return None
    
    def get_entity_reference(self, obj):
        """Get a human-readable reference for the related entity."""
        if obj.purchase_order:
            return obj.purchase_order.order_number
        elif obj.sales_order:
            return obj.sales_order.our_sales_order_num
        elif obj.invoice:
            return obj.invoice.invoice_number
        return None
