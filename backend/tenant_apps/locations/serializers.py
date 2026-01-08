"""
Serializers for Locations app.
"""
from rest_framework import serializers
from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model."""
    
    class Meta:
        model = Location
        fields = [
            'id',
            'name',
            'address',
            'city',
            'state_zip',
            'contact_name',
            'contact_phone',
            'contact_email',
            'how_make_appointment',
            'plant_est_number',
            'supplier',
            'customer',
            'created_on',
            'modified_on',
        ]
        read_only_fields = ['id', 'created_on', 'modified_on']


class LocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for location lists."""
    
    class Meta:
        model = Location
        fields = ['id', 'name', 'city', 'state_zip']
        read_only_fields = ['id']
