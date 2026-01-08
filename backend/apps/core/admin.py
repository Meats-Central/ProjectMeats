"""
Core admin for ProjectMeats.

Admin interface for core models and base admin classes for multi-tenancy.
"""
from django.contrib import admin
from apps.core.models import Protein, UserPreferences
from apps.tenants.models import TenantUser


class TenantFilteredAdmin(admin.ModelAdmin):
    """
    Base admin class that filters all querysets by the current user's tenant.
    
    This ensures that staff users only see data for their own tenant,
    even when accessing the Django admin interface.
    
    Superusers see all data across all tenants.
    """
    
    def get_queryset(self, request):
        """
        Filter queryset by user's tenant.
        
        - Superusers see everything
        - Staff users (owners/admins/managers) only see their tenant's data
        """
        qs = super().get_queryset(request)
        
        # Anonymous users get no data
        if not request.user.is_authenticated:
            return qs.none()
        
        # Superusers see all data
        if request.user.is_superuser:
            return qs
        
        # Get user's tenant(s)
        tenant_users = TenantUser.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('tenant')
        
        if not tenant_users.exists():
            # User has no tenant - return empty queryset
            return qs.none()
        
        # Filter by user's tenant(s)
        # If model has a 'tenant' field, filter by it
        if hasattr(qs.model, 'tenant'):
            tenant_ids = [tu.tenant_id for tu in tenant_users]
            return qs.filter(tenant_id__in=tenant_ids)
        
        # If no tenant field, return all (for non-tenanted models like User, Group, etc.)
        return qs
    
    def has_module_permission(self, request):
        """
        Allow staff users with an active tenant to see the app modules.
        
        - Superusers see everything
        - Staff users with active tenant association can see modules
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return TenantUser.objects.filter(user=request.user, is_active=True).exists()
    
    def has_view_permission(self, request, obj=None):
        """
        Allow staff users with an active tenant to view model instances.
        
        - Superusers can view everything
        - Staff users with active tenant can view their tenant's data
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        
        # If checking a specific object, ensure it belongs to their tenant
        if obj is not None and hasattr(obj, 'tenant'):
            user_tenants = TenantUser.objects.filter(
                user=request.user, 
                is_active=True
            ).values_list('tenant_id', flat=True)
            return obj.tenant_id in user_tenants
            
        return TenantUser.objects.filter(user=request.user, is_active=True).exists()
    
    def has_add_permission(self, request):
        """
        Check if user can add objects.
        
        Requires user to have at least one active tenant association.
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        
        # Check if user has any active tenant association
        return TenantUser.objects.filter(
            user=request.user,
            is_active=True
        ).exists()
    
    def has_change_permission(self, request, obj=None):
        """
        Check if user can change objects.
        
        If obj is provided, ensure it belongs to user's tenant.
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        
        # Check user has active tenant
        if not TenantUser.objects.filter(user=request.user, is_active=True).exists():
            return False
        
        # If checking specific object, ensure it belongs to user's tenant
        if obj is not None and hasattr(obj, 'tenant'):
            user_tenants = TenantUser.objects.filter(
                user=request.user,
                is_active=True
            ).values_list('tenant_id', flat=True)
            return obj.tenant_id in user_tenants
        
        return True
    
    def has_delete_permission(self, request, obj=None):
        """
        Check if user can delete objects.
        
        Only owners and admins can delete. Managers and below cannot.
        """
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        
        # Check if user has owner/admin role
        admin_roles = ['owner', 'admin']
        has_admin_role = TenantUser.objects.filter(
            user=request.user,
            role__in=admin_roles,
            is_active=True
        ).exists()
        
        if not has_admin_role:
            return False
        
        # If checking specific object, ensure it belongs to user's tenant
        if obj is not None and hasattr(obj, 'tenant'):
            user_tenants = TenantUser.objects.filter(
                user=request.user,
                role__in=admin_roles,
                is_active=True
            ).values_list('tenant_id', flat=True)
            return obj.tenant_id in user_tenants
        
        return True
    
    def save_model(self, request, obj, form, change):
        """
        Set tenant on object save if it's a new object.
        
        Uses the user's first active tenant (prioritizing owner/admin/manager roles).
        """
        if not change and hasattr(obj, 'tenant') and not obj.tenant_id:
            # Define role priority order explicitly
            role_priority = {'owner': 0, 'admin': 1, 'manager': 2, 'user': 3, 'readonly': 4}
            
            # Get user's primary tenant (prioritize by role order)
            tenant_users = TenantUser.objects.filter(
                user=request.user,
                is_active=True
            ).select_related('tenant')
            
            # Sort by role priority
            sorted_tenant_users = sorted(
                tenant_users,
                key=lambda tu: role_priority.get(tu.role, 999)
            )
            
            if sorted_tenant_users:
                obj.tenant = sorted_tenant_users[0].tenant
        
        super().save_model(request, obj, form, change)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Filter tenant dropdown to only show user's authorized tenants.
        
        Security: Prevents tenant admins from seeing or selecting other tenants.
        For any ForeignKey to Tenant model, restrict choices to user's active tenants.
        """
        if db_field.name == "tenant" and request.user.is_authenticated and not request.user.is_superuser:
            # Import here to avoid circular dependency
            from apps.tenants.models import Tenant
            
            # Get user's active tenant IDs
            tenant_ids = TenantUser.objects.filter(
                user=request.user, 
                is_active=True
            ).values_list('tenant_id', flat=True)
            
            # Restrict queryset to only user's tenants
            kwargs["queryset"] = Tenant.objects.filter(id__in=tenant_ids)
            
            # If user has only one tenant, set it as default
            if len(tenant_ids) == 1:
                kwargs["initial"] = tenant_ids[0]
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Protein)
class ProteinAdmin(admin.ModelAdmin):
    """Admin interface for Protein model."""

    list_display = ["name"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for UserPreferences model."""

    list_display = ["user", "theme", "sidebar_collapsed", "updated_at"]
    search_fields = ["user__username", "user__email"]
    list_filter = ["theme", "sidebar_collapsed", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("User", {
            "fields": ("user",)
        }),
        ("Theme Settings", {
            "fields": ("theme", "sidebar_collapsed")
        }),
        ("Layout Configuration", {
            "fields": ("dashboard_layout", "widget_preferences", "quick_menu_items"),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
