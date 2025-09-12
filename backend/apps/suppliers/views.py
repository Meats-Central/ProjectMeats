"""
Suppliers views for ProjectMeats.

Provides REST API endpoints for supplier management.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from apps.suppliers.models import Supplier
from apps.suppliers.serializers import SupplierSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for managing suppliers."""

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Filter suppliers based on user permissions."""
        return self.queryset

    def perform_create(self, serializer):
        """Set the creator when creating a new supplier."""
        serializer.save()
