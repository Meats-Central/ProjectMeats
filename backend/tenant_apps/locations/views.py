"""
ViewSets for Locations app.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Location
from .serializers import LocationSerializer, LocationListSerializer


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Location instances with tenant isolation.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = LocationSerializer
    
    def get_queryset(self):
        """Filter locations by tenant for isolation."""
        return Location.objects.filter(tenant=self.request.tenant)
    
    def get_serializer_class(self):
        """Use lightweight serializer for list actions."""
        if self.action == 'list':
            return LocationListSerializer
        return LocationSerializer
    
    def perform_create(self, serializer):
        """Assign tenant automatically on creation."""
        serializer.save(tenant=self.request.tenant)
