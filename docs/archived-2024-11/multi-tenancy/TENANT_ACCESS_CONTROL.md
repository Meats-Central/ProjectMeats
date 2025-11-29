# Tenant-Based Access Control and Role Permissions

## Overview

This document describes the multi-tenant access control system implemented in ProjectMeats. The system ensures that users only see data for their assigned tenant(s) and have appropriate permissions based on their role.

## Security Model

### API Access Control

**All environments (Development, Staging, Production):**
- ✅ **Authentication Required**: All API endpoints require authentication
- ✅ **Tenant Context Mandatory**: Users must have a tenant association to access data
- ✅ **Strict Isolation**: Users only see data for their tenant(s)
- ❌ **No DEBUG Bypasses**: Removed all DEBUG-based authentication/permission overrides

### Django Admin Access Control

**Admin Interface Access:**
- ✅ **Role-Based Admin Access**: Owner, Admin, and Manager roles automatically get `is_staff=True`
- ✅ **Tenant Filtering**: Staff users only see data for their tenant(s)
- ✅ **Superuser Override**: Superusers see all data across all tenants
- ✅ **Permission-Based Actions**: Different roles have different permissions

## Role Permissions

### Role Hierarchy

| Role | API Access | Django Admin | Add | Change | Delete | View |
|------|-----------|--------------|-----|--------|--------|------|
| **Owner** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Manager** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **User** | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
| **Read-Only** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |

### Automatic Permission Assignment

When a user is assigned to a tenant with a role:

1. **is_staff Flag**: Owner/Admin/Manager roles automatically get `is_staff=True` for Django admin access
2. **Django Groups**: User is added to a tenant-specific group (e.g., `acme_owner`, `acme_admin`)
3. **Model Permissions**: Group permissions are automatically assigned based on role
4. **Automatic Removal**: When user loses admin-level roles or TenantUser is deleted, `is_staff` is automatically removed

## Tenant Resolution

### API Endpoints

Tenant is resolved in the following order:

1. **X-Tenant-ID Header** (highest priority)
   - Format: UUID string
   - Example: `X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000`
   - Use case: Explicit tenant selection in API requests

2. **User's Default Tenant** (fallback)
   - Middleware automatically sets `request.tenant` from user's TenantUser association
   - Prioritizes owner/admin roles when user has multiple tenants
   - Use case: Single-tenant users, implicit tenant context

3. **No Tenant = No Data**
   - If no tenant can be resolved, returns empty queryset
   - Ensures security - never exposes cross-tenant data

### Django Admin

Admin interface filtering:

1. **Superusers**: See all data across all tenants
2. **Staff Users**: See only data for their tenant(s)
3. **Automatic Filtering**: TenantFilteredAdmin base class handles this automatically

## Implementation Details

### Signal Handlers (`apps/tenants/signals.py`)

**Post-Save Signal on TenantUser:**
- Assigns `is_staff=True` for owner/admin/manager roles
- Creates tenant-specific Django group
- Adds user to group with appropriate permissions
- Removes `is_staff` when role changes to user/readonly

**Pre-Delete Signal on TenantUser:**
- Removes user from tenant-specific group
- Removes `is_staff` if user has no remaining admin-level roles

### Base Admin Class (`apps/core/admin.TenantFilteredAdmin`)

Provides automatic tenant filtering for Django admin:

```python
from apps.core.admin import TenantFilteredAdmin

@admin.register(MyModel)
class MyModelAdmin(TenantFilteredAdmin):
    # Your admin configuration
    pass
```

Features:
- `get_queryset()`: Filters by user's tenant(s)
- `has_add_permission()`: Requires active tenant association
- `has_change_permission()`: Verifies object belongs to user's tenant
- `has_delete_permission()`: Only owners/admins can delete
- `save_model()`: Auto-assigns tenant on object creation

### ViewSet Security

All ViewSets enforce tenant isolation:

```python
class MyModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Strict tenant filtering
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return MyModel.objects.for_tenant(self.request.tenant)
        return MyModel.objects.none()  # No tenant = no data
```

## User Invitation Flow

1. **Admin/Owner Creates Invitation**
   - Specifies email and role
   - System generates unique invitation token
   - Email sent to invitee with signup link

2. **User Signs Up**
   - Uses invitation token to complete signup
   - System creates User account
   - Creates TenantUser association with specified role
   - **Automatic Role Permissions**:
     - If role is owner/admin/manager, `is_staff=True` is set
     - User added to tenant-specific group
     - Permissions assigned based on role

3. **User Gets Access**
   - Can immediately access API with their role permissions
   - If owner/admin/manager, can access Django admin

## Testing

### Role Permission Tests

Located in `apps/tenants/tests_role_permissions.py`:

- ✅ Owner/admin/manager get staff status
- ✅ User/readonly don't get staff status
- ✅ Users added to tenant-specific groups
- ✅ Staff status removed when role downgraded
- ✅ Staff status removed when TenantUser deleted
- ✅ Staff status removed when TenantUser deactivated
- ✅ Superuser status preserved
- ✅ Multi-tenant users keep staff status correctly

### Running Tests

```bash
# All tests
python manage.py test --settings=projectmeats.settings.test

# Just role permission tests
python manage.py test apps.tenants.tests_role_permissions --settings=projectmeats.settings.test

# Just tenant isolation tests
python manage.py test apps.tenants.test_isolation --settings=projectmeats.settings.test
```

## Migration Guide

### For Existing Deployments

1. **Deploy the Code**: Signal handlers will run automatically
2. **Existing Users**: Signal will fire on next TenantUser save
3. **Force Update** (if needed):
   ```python
   from apps.tenants.models import TenantUser
   
   # Re-save all TenantUsers to trigger signal
   for tu in TenantUser.objects.filter(is_active=True):
       tu.save()
   ```

### For New Deployments

No special steps needed - signals run automatically on TenantUser creation.

## Troubleshooting

### User Can't Access Django Admin

**Check:**
1. User has owner/admin/manager role in at least one tenant
2. TenantUser association is active (`is_active=True`)
3. User's `is_staff` flag is set to `True`

**Fix:**
```python
from django.contrib.auth.models import User
from apps.tenants.models import TenantUser

user = User.objects.get(username='username')
tenant_user = TenantUser.objects.get(user=user)
tenant_user.save()  # Re-save to trigger signal
```

### User Sees No Data in Admin

**Check:**
1. User has active TenantUser association
2. Data has `tenant` field populated
3. User is not trying to access data from another tenant

### User Has Wrong Permissions

**Check:**
1. User's role in TenantUser
2. User's group memberships: `user.groups.all()`
3. User's permissions: `user.get_all_permissions()`

**Fix:**
```python
# Re-assign permissions by re-saving TenantUser
tenant_user.save()
```

## Security Best Practices

1. **Never Bypass Tenant Filtering**: Always filter by tenant, even in DEBUG mode
2. **Use TenantFilteredAdmin**: For all admin classes dealing with tenant data
3. **Validate Tenant Context**: Before any data access, ensure `request.tenant` is set
4. **Audit Logs**: Log all cross-tenant access attempts
5. **Regular Security Audits**: Review signal handlers and admin permissions periodically

## References

- Django Signals: https://docs.djangoproject.com/en/4.2/topics/signals/
- Django Permissions: https://docs.djangoproject.com/en/4.2/topics/auth/default/#permissions-and-authorization
- Django Admin: https://docs.djangoproject.com/en/4.2/ref/contrib/admin/
