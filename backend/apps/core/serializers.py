"""
Serializers for Core app.
"""
from rest_framework import serializers
from apps.core.models import UserPreferences


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for UserPreferences model."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserPreferences
        fields = [
            'id',
            'user',
            'username',
            'theme',
            'dashboard_layout',
            'sidebar_collapsed',
            'quick_menu_items',
            'widget_preferences',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'username', 'created_at', 'updated_at']
