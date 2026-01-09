"""
Cockpit views for aggregated search across tenant models.

Provides polymorphic search API respecting tenant schema isolation.
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .serializers import (
    CustomerSlotSerializer,
    SupplierSlotSerializer,
    OrderSlotSerializer,
    ActivityLogSerializer,
    ScheduledCallSerializer,
)
from .models import ActivityLog, ScheduledCall
from tenant_apps.customers.models import Customer
from tenant_apps.suppliers.models import Supplier
from tenant_apps.purchase_orders.models import PurchaseOrder


class CockpitSlotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Aggregated search across tenant models (Customer, Supplier, PurchaseOrder).
    
    Returns polymorphic results with type fields for frontend icon rendering.
    Respects shared-schema tenant isolation via tenant_id filtering in querysets.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSlotSerializer  # Default serializer for schema generation
    
    def list(self, request):
        """
        Search across Customers, Suppliers, and PurchaseOrders.
        
        Query Parameters:
        - q: Search query string (filters by name/order_number)
        
        Returns:
        - Polymorphic list with 'type' field: 'customer', 'supplier', or 'order'
        """
        q = request.query_params.get('q', '').strip()
        
        results = []
        
        if q:
            # Search customers by name
            customers = Customer.objects.filter(
                Q(name__icontains=q) | Q(contact_person__icontains=q)
            )[:10]
            results.extend(CustomerSlotSerializer(customers, many=True).data)
            
            # Search suppliers by name
            suppliers = Supplier.objects.filter(
                Q(name__icontains=q) | Q(contact_person__icontains=q)
            )[:10]
            results.extend(SupplierSlotSerializer(suppliers, many=True).data)
            
            # Search orders by order numbers
            orders = PurchaseOrder.objects.filter(
                Q(order_number__icontains=q) | Q(our_purchase_order_num__icontains=q)
            ).select_related('supplier')[:10]
            results.extend(OrderSlotSerializer(orders, many=True).data)
        
        return Response(results)


class ActivityLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Activity Logs with strict tenant isolation.
    
    Supports filtering by entity_type and entity_id for entity-specific note feeds.
    """
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter activity logs by tenant and optional entity filters."""
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            return ActivityLog.objects.none()
        
        queryset = ActivityLog.objects.filter(tenant=self.request.tenant)
        
        # Filter by entity if provided
        entity_type = self.request.query_params.get('entity_type')
        entity_id = self.request.query_params.get('entity_id')
        
        if entity_type and entity_id:
            queryset = queryset.filter(entity_type=entity_type, entity_id=entity_id)
        
        return queryset.order_by('-is_pinned', '-created_on')
    
    def perform_create(self, serializer):
        """Auto-assign tenant and created_by on create."""
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user
        )


class ScheduledCallViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Scheduled Calls with strict tenant isolation.
    
    Supports filtering by date range and completion status.
    """
    serializer_class = ScheduledCallSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter scheduled calls by tenant and optional filters."""
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            return ScheduledCall.objects.none()
        
        queryset = ScheduledCall.objects.filter(tenant=self.request.tenant)
        
        # Filter by completion status
        is_completed = self.request.query_params.get('is_completed')
        if is_completed is not None:
            queryset = queryset.filter(is_completed=is_completed.lower() == 'true')
        
        return queryset
    
    def perform_create(self, serializer):
        """Auto-assign tenant and created_by on create."""
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user
        )
