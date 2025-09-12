"""
Suppliers serializers for ProjectMeats.

Provides serialization for supplier API endpoints.
"""
from rest_framework import serializers
from apps.suppliers.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model."""

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'contact_person', 'email', 'phone',
            'address', 'city', 'state', 'zip_code', 'country',
            'created_on', 'modified_on'
        ]
        read_only_fields = ['id', 'created_on', 'modified_on']
