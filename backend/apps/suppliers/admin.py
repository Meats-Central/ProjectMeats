"""
Django admin configuration for Suppliers app.
"""
from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin interface for Supplier model."""
    
    list_display = ('name', 'contact_person', 'email', 'phone', 'city', 'created_on')
    list_filter = ('country', 'created_on')
    search_fields = ('name', 'contact_person', 'email', 'phone')
    readonly_fields = ('created_on', 'modified_on')
    
    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'contact_person', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Metadata', {
            'fields': ('created_on', 'modified_on'),
            'classes': ('collapse',)
        }),
    )