"""
Custom permission classes for tenant management.

These permissions ensure tenant owners and admins have appropriate
access to modify tenant settings, while regular users have read-only access.
"""
from rest_framework import permissions
from .models import TenantUser


class IsTenantAdminOrOwner(permissions.BasePermission):
    """
    Permission class for tenant administrative actions.
    
    Allows:
    - Superusers (full access)
    - Tenant owners (full access to their tenant)
    - Tenant admins (full access to their tenant)
    
    Denies:
    - Regular users (read-only access only)
    - Users not associated with the tenant
    
    Usage:
        class TenantViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsTenantAdminOrOwner]
    """
    
    def has_permission(self, request, view):
        """
        Check if user has permission to access the endpoint.
        
        Safe methods (GET, HEAD, OPTIONS) are allowed for authenticated users.
        Unsafe methods (POST, PUT, PATCH, DELETE) require admin/owner role.
        """
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superusers have full access
        if request.user.is_superuser:
            return True
        
        # Safe methods (GET, HEAD, OPTIONS) are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For unsafe methods, check object-level permission
        # (will be checked in has_object_permission)
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to modify this specific tenant.
        
        Args:
            request: The HTTP request
            view: The view handling the request
            obj: The Tenant object being accessed
        
        Returns:
            bool: True if user can modify the tenant, False otherwise
        """
        # Superusers have full access
        if request.user.is_superuser:
            return True
        
        # Safe methods are allowed for any tenant member
        if request.method in permissions.SAFE_METHODS:
            return TenantUser.objects.filter(
                tenant=obj,
                user=request.user,
                is_active=True
            ).exists()
        
        # Unsafe methods require owner or admin role
        return TenantUser.objects.filter(
            tenant=obj,
            user=request.user,
            role__in=['owner', 'admin'],
            is_active=True
        ).exists()


class IsTenantMember(permissions.BasePermission):
    """
    Permission class that allows access only to tenant members.
    
    Any user who belongs to the tenant can access, regardless of role.
    Read-only for all members.
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user is a member of the tenant."""
        if request.user.is_superuser:
            return True
        
        return TenantUser.objects.filter(
            tenant=obj,
            user=request.user,
            is_active=True
        ).exists()
