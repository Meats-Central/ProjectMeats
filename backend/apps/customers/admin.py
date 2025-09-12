"""
Django admin configuration for Customers app.
"""
from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin interface for Customer model."""
    
    list_display = ('name', 'contact_person', 'email', 'phone', 'city', 'status', 'created_at')
    list_filter = ('status', 'country', 'created_at')
    search_fields = ('name', 'contact_person', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'contact_person', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )