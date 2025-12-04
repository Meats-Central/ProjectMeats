"""
Cockpit serializers for aggregated search across tenant models.

Provides lightweight, type-annotated serializers for polymorphic search results.
"""
from rest_framework import serializers
from tenant_apps.customers.models import Customer
from tenant_apps.suppliers.models import Supplier
from tenant_apps.purchase_orders.models import PurchaseOrder


class CustomerSlotSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Customer search results."""
    
    type = serializers.CharField(default='customer', read_only=True)
    contact_name = serializers.CharField(source='contact_person', read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'type', 'contact_name', 'email', 'phone']


class SupplierSlotSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Supplier search results."""
    
    type = serializers.CharField(default='supplier', read_only=True)
    contact_name = serializers.CharField(source='contact_person', read_only=True)

    class Meta:
        model = Supplier
        fields = ['id', 'name', 'type', 'contact_name', 'email', 'phone']


class OrderSlotSerializer(serializers.ModelSerializer):
    """Lightweight serializer for PurchaseOrder search results."""
    
    type = serializers.CharField(default='order', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = ['id', 'order_number', 'our_purchase_order_num', 'type', 'status', 'supplier_name', 'total_amount']
