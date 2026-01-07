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
        'city',
        'state_zip',
        'contact_name',
        'supplier',
        'customer',
        'created_on',
    )
    list_filter = (
        'how_make_appointment',
        'created_on',
        'modified_on',
    )
    search_fields = (
        'name',
        'city',
        'address',
        'contact_name',
        'contact_email',
        'plant_est_number',
    )
    readonly_fields = ('created_on', 'modified_on')

    fieldsets = (
        (
            'Basic Information',
            {
                'fields': ('name', 'address', 'city', 'state_zip')
            },
        ),
        (
            'Contact Information',
            {
                'fields': ('contact_name', 'contact_phone', 'contact_email')
            },
        ),
        (
            'Appointment & Plant Details',
            {
                'fields': ('how_make_appointment', 'plant_est_number')
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
