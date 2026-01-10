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
    Automatically creates activity log entries for related entities.
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
        """Auto-assign tenant and created_by on create, and log activity."""
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError
        
        if not self.request.tenant:
            raise ValidationError("Tenant is required for creating scheduled calls.")
        
        try:
            scheduled_call = serializer.save(
                tenant=self.request.tenant,
                created_by=self.request.user
            )
            
            # Auto-create activity log entry for the related entity
            self._create_activity_log(
                scheduled_call=scheduled_call,
                action='scheduled',
                user=self.request.user
            )
        except (IntegrityError, ValueError) as e:
            raise ValidationError(f"Failed to create scheduled call: {str(e)}")
    
    def perform_update(self, serializer):
        """Log activity when call is updated or completed."""
        from django.core.exceptions import ValidationError
        from django.db import IntegrityError
        
        if not self.request.tenant:
            raise ValidationError("Tenant is required for updating scheduled calls.")
        
        old_instance = self.get_object()
        was_completed = old_instance.is_completed
        
        try:
            scheduled_call = serializer.save()
            
            # If call was just marked as completed, log it
            if scheduled_call.is_completed and not was_completed:
                self._create_activity_log(
                    scheduled_call=scheduled_call,
                    action='completed',
                    user=self.request.user
                )
        except (IntegrityError, ValueError) as e:
            raise ValidationError(f"Failed to update scheduled call: {str(e)}")
    
    def _create_activity_log(self, scheduled_call, action, user):
        """
        Helper method to create activity log entries for scheduled calls.
        
        This ensures the activity appears in the entity's activity feed automatically.
        """
        # Determine the content based on action
        if action == 'scheduled':
            title = f"Call Scheduled: {scheduled_call.title}"
            content = (
                f"Scheduled call for {scheduled_call.scheduled_for.strftime('%Y-%m-%d %H:%M')}.\n"
                f"Duration: {scheduled_call.duration_minutes} minutes\n"
                f"Purpose: {scheduled_call.call_purpose}"
            )
            if scheduled_call.description:
                content += f"\n\nNotes: {scheduled_call.description}"
        elif action == 'completed':
            title = f"Call Completed: {scheduled_call.title}"
            content = f"Call was completed."
            if scheduled_call.outcome:
                content += f"\n\nOutcome: {scheduled_call.outcome}"
        else:
            title = f"Call Updated: {scheduled_call.title}"
            content = "Call details were updated."
        
        # Create activity log tied to the entity
        ActivityLog.objects.create(
            tenant=scheduled_call.tenant,
            entity_type=scheduled_call.entity_type,
            entity_id=scheduled_call.entity_id,
            title=title,
            content=content,
            created_by=user,
            tags='call,scheduled-call,auto-generated'
        )
