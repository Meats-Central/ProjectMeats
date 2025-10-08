"""
Suppliers views for ProjectMeats.

Provides REST API endpoints for supplier management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.suppliers.models import Supplier
from apps.suppliers.serializers import SupplierSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for managing suppliers."""

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter suppliers by current tenant."""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Supplier.objects.for_tenant(self.request.tenant)
        return Supplier.objects.none()

    def perform_create(self, serializer):
        """Set the tenant when creating a new supplier."""
        serializer.save(tenant=self.request.tenant)
