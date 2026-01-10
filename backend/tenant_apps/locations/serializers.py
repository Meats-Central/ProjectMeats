"""
Serializers for Locations app.
"""
from rest_framework import serializers
from .models import Location


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model."""
    
    # Read-only fields for related entity names
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = Location
        fields = [
            'id',
            'name',
            'code',
            'location_type',
            'address',
            'city',
            'state',
            'zip_code',
            'country',
            'phone',
            'email',
            'contact_name',
            'is_active',
            'supplier',
            'supplier_name',
            'customer',
            'customer_name',
            'created_on',
            'modified_on',
        ]
        read_only_fields = ['id', 'supplier_name', 'customer_name', 'created_on', 'modified_on']


class LocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for location lists."""
    
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    
    class Meta:
        model = Location
        fields = [
            'id',
            'name',
            'code',
            'location_type',
            'city',
            'state',
            'supplier',
            'supplier_name',
            'customer',
            'customer_name',
        ]
        read_only_fields = ['id', 'supplier_name', 'customer_name']
