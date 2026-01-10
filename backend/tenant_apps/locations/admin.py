"""
Django admin configuration for Locations app.
"""
from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import Location


@admin.register(Location)
class LocationAdmin(TenantFilteredAdmin):
    """Admin interface for Location model with tenant filtering."""

    list_display = (
        'name',
        'code',
        'location_type',
        'city',
        'state',
        'contact_name',
        'supplier',
        'customer',
        'is_active',
        'created_on',
    )
    list_filter = (
        'location_type',
        'is_active',
        'created_on',
        'modified_on',
    )
    search_fields = (
        'name',
        'code',
        'city',
        'state',
        'address',
        'contact_name',
        'email',
    )
    readonly_fields = ('created_on', 'modified_on')

    fieldsets = (
        (
            'Basic Information',
            {
                'fields': ('name', 'code', 'location_type', 'is_active')
            },
        ),
        (
            'Address',
            {
                'fields': ('address', 'city', 'state', 'zip_code', 'country')
            },
        ),
        (
            'Contact Information',
            {
                'fields': ('phone', 'email', 'contact_name')
            },
        ),
        (
            'Relationships',
            {
                'fields': ('supplier', 'customer')
            },
        ),
        (
            'Metadata',
            {
                'fields': ('tenant', 'created_on', 'modified_on'),
                'classes': ('collapse',)
            },
        ),
    )
