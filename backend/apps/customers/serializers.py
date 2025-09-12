"""
Customers serializers for ProjectMeats.

Provides serialization for customer API endpoints.
"""
from rest_framework import serializers
from apps.customers.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone',
            'address', 'city', 'state', 'zip_code', 'country',
            'created_on', 'modified_on'
        ]
        read_only_fields = ['id', 'created_on', 'modified_on']
