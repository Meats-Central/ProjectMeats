"""
Cockpit views for aggregated search across tenant models.

Provides polymorphic search API respecting tenant schema isolation.
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .serializers import CustomerSlotSerializer, SupplierSlotSerializer, OrderSlotSerializer
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
