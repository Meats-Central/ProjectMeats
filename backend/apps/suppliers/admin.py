"""
Django admin configuration for Suppliers app.
"""
from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin interface for Supplier model."""
    
    list_display = ('name', 'contact_person', 'email', 'phone', 'city', 'edible_inedible', 'plant', 'created_on')
    list_filter = ('country', 'edible_inedible', 'type_of_plant', 'type_of_certificate', 'tested_product', 'origin', 'plant', 'offer_contracts', 'offers_export_documents', 'created_on')
    search_fields = ('name', 'contact_person', 'email', 'phone', 'type_of_plant', 'type_of_certificate', 'origin', 'country_origin')
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
            'fields': ('plant', 'proteins', 'edible_inedible', 'type_of_plant', 'type_of_certificate', 'tested_product', 'origin', 'country_origin')
        }),
        ('Operations', {
            'fields': ('contacts', 'shipping_offered', 'how_to_book_pickup', 'offer_contracts', 'offers_export_documents')
        }),
        ('Accounting', {
            'fields': ('accounting_terms', 'accounting_line_of_credit', 'credit_app_sent', 'credit_app_set_up')
        }),
        ('Metadata', {
            'fields': ('created_on', 'modified_on'),
            'classes': ('collapse',)
        }),
    )