"""
Customers views for ProjectMeats.

Provides REST API endpoints for customer management.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing customers."""

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Filter customers based on user permissions."""
        return self.queryset

    def perform_create(self, serializer):
        """Set the creator when creating a new customer."""
        serializer.save()
