"""
Customers views for ProjectMeats.

Provides REST API endpoints for customer management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing customers."""

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter customers by current tenant."""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Customer.objects.for_tenant(self.request.tenant)
        return Customer.objects.none()

    def perform_create(self, serializer):
        """Set the tenant when creating a new customer."""
        serializer.save(tenant=self.request.tenant)
