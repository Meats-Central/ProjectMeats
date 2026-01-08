"""
Cockpit serializers for aggregated search across tenant models.

Provides lightweight, type-annotated serializers for polymorphic search results.
"""
from rest_framework import serializers
from tenant_apps.customers.models import Customer
from tenant_apps.suppliers.models import Supplier
from tenant_apps.purchase_orders.models import PurchaseOrder
from tenant_apps.cockpit.models import ActivityLog, ScheduledCall


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


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model."""
    
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "entity_type",
            "entity_id",
            "title",
            "content",
            "created_by",
            "created_by_name",
            "is_pinned",
            "tags",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on", "created_by_name"]
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created this log."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return "System"


class ScheduledCallSerializer(serializers.ModelSerializer):
    """Serializer for ScheduledCall model."""
    
    assigned_to_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ScheduledCall
        fields = [
            "id",
            "entity_type",
            "entity_id",
            "title",
            "description",
            "scheduled_for",
            "duration_minutes",
            "is_completed",
            "completed_at",
            "assigned_to",
            "assigned_to_name",
            "created_by",
            "created_by_name",
            "activity_log",
            "created_on",
            "modified_on",
        ]
        read_only_fields = ["id", "created_on", "modified_on", "assigned_to_name", "created_by_name"]
    
    def get_assigned_to_name(self, obj):
        """Get the name of the user this call is assigned to."""
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}".strip() or obj.assigned_to.username
        return None
    
    def get_created_by_name(self, obj):
        """Get the name of the user who created this call."""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return "System"

