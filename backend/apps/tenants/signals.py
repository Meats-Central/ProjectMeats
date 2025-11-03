"""
Signal handlers for tenant-related events.

Handles automatic permission and group assignment based on tenant roles.
"""
import logging
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import TenantUser

logger = logging.getLogger(__name__)


# Define role-based group permissions
ROLE_PERMISSIONS = {
    "owner": {
        "is_staff": True,
        "is_superuser": False,  # Don't make owners full superusers
        "permissions": ["add", "change", "delete", "view"],  # Full CRUD
    },
    "admin": {
        "is_staff": True,
        "is_superuser": False,
        "permissions": ["add", "change", "delete", "view"],  # Full CRUD
    },
    "manager": {
        "is_staff": True,  # Allow managers to access admin
        "is_superuser": False,
        "permissions": ["add", "change", "view"],  # No delete permission
    },
    "user": {
        "is_staff": False,  # Regular users don't get admin access
        "is_superuser": False,
        "permissions": ["add", "change", "view"],  # Basic CRUD except delete
    },
    "readonly": {
        "is_staff": False,
        "is_superuser": False,
        "permissions": ["view"],  # Read-only access
    },
}


def get_or_create_role_group(role, tenant):
    """
    Get or create a Django Group for a specific role and tenant.
    
    Args:
        role: Role name (owner, admin, manager, user, readonly)
        tenant: Tenant instance
        
    Returns:
        Group instance for this role-tenant combination
    """
    group_name = f"{tenant.slug}_{role}"
    group, created = Group.objects.get_or_create(name=group_name)
    
    if created:
        logger.info(f"Created new group: {group_name}")
        # Assign permissions based on role
        role_config = ROLE_PERMISSIONS.get(role, {})
        permission_types = role_config.get("permissions", [])
        
        # Add permissions for key models
        # We'll add permissions for models that users commonly interact with
        model_names = [
            "customer",
            "supplier",
            "purchaseorder",
            "salesorder",
            "plant",
            "contact",
            "carrier",
            "product",
        ]
        
        for model_name in model_names:
            for perm_type in permission_types:
                perm_codename = f"{perm_type}_{model_name}"
                try:
                    # Try to find the permission
                    permission = Permission.objects.filter(
                        codename=perm_codename
                    ).first()
                    if permission:
                        group.permissions.add(permission)
                        logger.debug(
                            f"Added permission {perm_codename} to group {group_name}"
                        )
                except Permission.DoesNotExist:
                    logger.warning(
                        f"Permission {perm_codename} not found for group {group_name}"
                    )
                    continue
    
    return group


@receiver(post_save, sender=TenantUser)
def assign_role_permissions(sender, instance, created, **kwargs):
    """
    Assign Django admin access and group permissions when a TenantUser is created or updated.
    
    This signal:
    1. Sets is_staff flag for owner/admin/manager roles to enable Django admin access
    2. Adds user to a tenant-specific group with appropriate permissions
    3. Removes is_staff if user no longer has admin-level roles in any tenant
    """
    user = instance.user
    role = instance.role
    tenant = instance.tenant
    is_active = instance.is_active
    
    # Only process active tenant associations
    if not is_active:
        logger.debug(
            f"Skipping inactive TenantUser: {user.username} @ {tenant.slug} ({role})"
        )
        # Check if user should lose staff status
        _check_and_remove_staff_status(user)
        return
    
    # Get role configuration
    role_config = ROLE_PERMISSIONS.get(role, {})
    should_be_staff = role_config.get("is_staff", False)
    
    # Update user's staff status if they should have admin access
    if should_be_staff and not user.is_staff:
        user.is_staff = True
        user.save(update_fields=["is_staff"])
        logger.info(
            f"Granted Django admin access to {user.username} "
            f"(role: {role} at {tenant.slug})"
        )
    
    # If this role doesn't grant staff access, check if user should lose it
    if not should_be_staff:
        _check_and_remove_staff_status(user)
    
    # Add user to role-specific group for this tenant
    group = get_or_create_role_group(role, tenant)
    user.groups.add(group)
    logger.info(
        f"Added {user.username} to group {group.name} "
        f"(tenant: {tenant.slug}, role: {role})"
    )
    
    # Log permission assignment
    if created:
        logger.info(
            f"Created TenantUser: {user.username} @ {tenant.slug} "
            f"with role {role} (is_staff={user.is_staff})"
        )


@receiver(pre_delete, sender=TenantUser)
def remove_role_permissions(sender, instance, **kwargs):
    """
    Remove group membership when a TenantUser association is deleted.
    Also remove is_staff if user no longer has any admin-level roles.
    """
    user = instance.user
    role = instance.role
    tenant = instance.tenant
    
    # Remove from role-specific group
    group_name = f"{tenant.slug}_{role}"
    try:
        group = Group.objects.get(name=group_name)
        user.groups.remove(group)
        logger.info(
            f"Removed {user.username} from group {group_name} "
            f"(TenantUser deletion for {tenant.slug})"
        )
    except Group.DoesNotExist:
        logger.warning(f"Group {group_name} not found during TenantUser deletion")
    
    # Check if user should lose staff status
    # Exclude the instance being deleted when checking
    _check_and_remove_staff_status(user, exclude_id=instance.id)


def _check_and_remove_staff_status(user, exclude_id=None):
    """
    Check if user still has any admin-level roles across all tenants.
    Remove is_staff if they don't.
    
    Args:
        user: User instance to check
        exclude_id: TenantUser ID to exclude from check (when deleting)
    """
    # Don't touch superusers
    if user.is_superuser:
        return
    
    # Check if user has any active admin-level roles
    admin_roles = ["owner", "admin", "manager"]
    query = TenantUser.objects.filter(
        user=user, role__in=admin_roles, is_active=True
    )
    
    # Exclude the instance being deleted if specified
    if exclude_id:
        query = query.exclude(id=exclude_id)
    
    has_admin_role = query.exists()
    
    if not has_admin_role and user.is_staff:
        user.is_staff = False
        user.save(update_fields=["is_staff"])
        logger.info(
            f"Removed Django admin access from {user.username} "
            f"(no longer has admin-level roles in any tenant)"
        )
