"""
Serializers for core models.
"""
from rest_framework import serializers
from .models import UserPreferences


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for user preferences."""
    
    class Meta:
        model = UserPreferences
        fields = ['id', 'user', 'theme', 'sidebar_open', 'dashboard_layout', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
