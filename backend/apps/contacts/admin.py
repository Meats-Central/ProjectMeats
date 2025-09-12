"""
Django admin configuration for Contacts app.
"""
from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin interface for Contact model."""
    
    list_display = ('get_full_name', 'email', 'phone', 'company', 'position', 'created_on')
    list_filter = ('created_on',)
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'company')
    readonly_fields = ('created_on', 'modified_on')
    
    def get_full_name(self, obj):
        """Return full name of the contact."""
        return f"{obj.first_name} {obj.last_name}".strip()
    get_full_name.short_description = 'Name'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Professional Information', {
            'fields': ('company', 'position')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )