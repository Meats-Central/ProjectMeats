from django.contrib import admin
from .models import Tenant, TenantUser


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""
    
    list_display = [
        'name', 'slug', 'domain', 'is_active', 'is_trial', 
        'trial_ends_at', 'created_at'
    ]
    list_filter = ['is_active', 'is_trial', 'created_at']
    search_fields = ['name', 'slug', 'domain', 'contact_email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ('name', 'slug', 'domain')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Status & Trial', {
            'fields': ('is_active', 'is_trial', 'trial_ends_at')
        }),
        ('Configuration', {
            'fields': ('settings',),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    """Admin interface for TenantUser associations."""
    
    list_display = ['user', 'tenant', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'tenant']
    search_fields = ['user__username', 'user__email', 'tenant__name', 'tenant__slug']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Association', {
            'fields': ('tenant', 'user', 'role')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'tenant')
