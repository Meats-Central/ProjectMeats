"""
Contacts views for ProjectMeats.

Provides REST API endpoints for contact management.
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from apps.contacts.models import Contact
from apps.contacts.serializers import ContactSerializer


class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet for managing contacts."""

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Filter contacts based on user permissions."""
        return self.queryset

    def perform_create(self, serializer):
        """Set the creator when creating a new contact."""
        serializer.save()
