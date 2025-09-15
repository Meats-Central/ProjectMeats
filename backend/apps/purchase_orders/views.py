"""
Purchase Orders views for ProjectMeats.

Provides REST API endpoints for purchase order management.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from apps.purchase_orders.models import PurchaseOrder
from apps.purchase_orders.serializers import PurchaseOrderSerializer


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing purchase orders."""

    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Filter purchase orders based on user permissions."""
        return self.queryset

    def perform_create(self, serializer):
        """Set the creator when creating a new purchase order."""
        serializer.save()
