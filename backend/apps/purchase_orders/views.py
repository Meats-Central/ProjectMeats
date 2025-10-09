"""
Purchase Orders views for ProjectMeats.

Provides REST API endpoints for purchase order management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.purchase_orders.models import PurchaseOrder
from apps.purchase_orders.serializers import PurchaseOrderSerializer


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing purchase orders."""

    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter purchase orders by current tenant."""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return PurchaseOrder.objects.for_tenant(self.request.tenant)
        return PurchaseOrder.objects.none()

    def perform_create(self, serializer):
        """Set the tenant when creating a new purchase order."""
        serializer.save(tenant=self.request.tenant)
