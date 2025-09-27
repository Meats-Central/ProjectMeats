"""
Django admin configuration for Customers app.
"""
from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Admin interface for Customer model."""
    
    list_display = ('name', 'contact_person', 'email', 'phone', 'city', 'edible_inedible', 'plant', 'created_on')
    list_filter = ('country', 'edible_inedible', 'type_of_plant', 'industry', 'will_pickup_load', 'plant', 'created_on')
    search_fields = ('name', 'contact_person', 'email', 'phone', 'type_of_plant', 'industry')
    readonly_fields = ('created_on', 'modified_on')
    filter_horizontal = ('proteins', 'contacts')
    
    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'contact_person', 'email', 'phone')
        }),
        ('Address', {
            'fields': ('address', 'street_address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Business Details', {
            'fields': ('plant', 'proteins', 'edible_inedible', 'type_of_plant', 'purchasing_preference_origin', 'industry')
        }),
        ('Operations', {
            'fields': ('contacts', 'will_pickup_load')
        }),
        ('Accounting', {
            'fields': ('accounting_terms', 'accounting_line_of_credit')
        }),
        ('Metadata', {
            'fields': ('created_on', 'modified_on'),
            'classes': ('collapse',)
        }),
    )