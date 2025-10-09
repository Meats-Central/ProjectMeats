"""
Contacts views for ProjectMeats.

Provides REST API endpoints for contact management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.contacts.models import Contact
from apps.contacts.serializers import ContactSerializer


class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet for managing contacts."""

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter contacts by current tenant."""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Contact.objects.for_tenant(self.request.tenant)
        return Contact.objects.none()

    def perform_create(self, serializer):
        """Set the tenant when creating a new contact."""
        serializer.save(tenant=self.request.tenant)
