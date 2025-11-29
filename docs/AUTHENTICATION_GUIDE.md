# Authentication & Permissions Guide

**Last Updated**: November 29, 2024  
**Tech Stack**: Django 4.2.7, Django REST Framework, django-tenants 3.5.0

---

## Table of Contents

1. [Overview](#overview)
2. [Superuser Management](#superuser-management)
3. [Environment-Specific Credentials](#environment-specific-credentials)
4. [Permissions System](#permissions-system)
5. [Guest Mode](#guest-mode)
6. [Multi-Tenant Authentication](#multi-tenant-authentication)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

ProjectMeats implements a comprehensive authentication system with:
- Environment-specific superuser management
- Multi-tenant user isolation
- Role-based permissions
- Guest mode for limited access
- Automated credential synchronization

### Authentication Flow

```
User Login → Tenant Resolution → Permission Check → Access Granted
```

---

## Superuser Management

### Two Management Commands

#### 1. `setup_superuser` - Credential Synchronization

Syncs superuser credentials from environment variables. **Always updates** password when user exists.

```bash
# Development
cd backend && DJANGO_ENV=development python manage.py setup_superuser

# Via Makefile
make sync-superuser

# In deployment workflows (automatic)
python manage.py setup_superuser
```

**Use Cases**:
- ✅ Deployment automation (runs on every deploy)
- ✅ Password rotation
- ✅ Dynamic credential configuration per environment
- ✅ Emergency password reset

**Behavior**:
- Creates superuser if doesn't exist
- **Updates password** if user exists
- Updates email if changed
- Idempotent and safe to run multiple times

#### 2. `create_super_tenant` - Full Infrastructure Setup

Creates superuser, root tenant, and links them. Idempotent.

```bash
# Create or update
make superuser

# Direct command
cd backend && python manage.py create_super_tenant
```

**What It Does**:
1. Creates superuser (if not exists)
2. Creates "Super Tenant" (root tenant)
3. Creates default domain for tenant
4. Links superuser to tenant via TenantUser

**Use Cases**:
- ✅ Initial setup
- ✅ Ensuring tenant infrastructure exists
- ✅ Deployment verification

---

## Environment-Specific Credentials

### Variable Naming Convention

Format: `{ENVIRONMENT}_SUPERUSER_{ATTRIBUTE}`

| Environment | Username Variable | Email Variable | Password Variable |
|-------------|-------------------|----------------|-------------------|
| Development | `DEVELOPMENT_SUPERUSER_USERNAME` | `DEVELOPMENT_SUPERUSER_EMAIL` | `DEVELOPMENT_SUPERUSER_PASSWORD` |
| Staging/UAT | `STAGING_SUPERUSER_USERNAME` | `STAGING_SUPERUSER_EMAIL` | `STAGING_SUPERUSER_PASSWORD` |
| Production | `PRODUCTION_SUPERUSER_USERNAME` | `PRODUCTION_SUPERUSER_EMAIL` | `PRODUCTION_SUPERUSER_PASSWORD` |

### Configuration

#### Development Environment

```bash
# config/environments/development.env
DJANGO_ENV=development
DEVELOPMENT_SUPERUSER_USERNAME=admin
DEVELOPMENT_SUPERUSER_EMAIL=admin@meatscentral.com
DEVELOPMENT_SUPERUSER_PASSWORD=DevAdmin123!SecurePass
```

#### Staging Environment

Set as GitHub Secrets in UAT environment:

```yaml
# GitHub Repository → Settings → Environments → uat2-backend → Secrets
STAGING_SUPERUSER_USERNAME: "uat_admin"
STAGING_SUPERUSER_EMAIL: "uat-admin@meatscentral.com"
STAGING_SUPERUSER_PASSWORD: "<strong-random-password>"
```

#### Production Environment

Set as GitHub Secrets in production environment:

```yaml
# GitHub Repository → Settings → Environments → prod2-backend → Secrets
PRODUCTION_SUPERUSER_USERNAME: "prod_admin"
PRODUCTION_SUPERUSER_EMAIL: "admin@meatscentral.com"
PRODUCTION_SUPERUSER_PASSWORD: "<very-strong-random-password>"
```

### Automatic Environment Detection

The system automatically detects environment from `DJANGO_ENV`:

```python
# backend/projectmeats/settings/base.py
ENV = os.getenv("DJANGO_ENV", "development")

# Determines which variables to use
if ENV == "production":
    prefix = "PRODUCTION"
elif ENV == "staging" or ENV == "uat":
    prefix = "STAGING"
else:
    prefix = "DEVELOPMENT"

SUPERUSER_USERNAME = os.getenv(f"{prefix}_SUPERUSER_USERNAME")
SUPERUSER_EMAIL = os.getenv(f"{prefix}_SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = os.getenv(f"{prefix}_SUPERUSER_PASSWORD")
```

---

## Permissions System

### Django Permission Model

ProjectMeats uses Django's built-in permission system with custom extensions.

#### Permission Types

1. **Model Permissions** (Auto-generated)
   - `add_<model>`: Can add instances
   - `change_<model>`: Can modify instances
   - `delete_<model>`: Can delete instances
   - `view_<model>`: Can view instances

2. **Custom Permissions** (Defined in Meta)
   ```python
   class MyModel(models.Model):
       class Meta:
           permissions = [
               ("approve_mymodel", "Can approve my model"),
               ("export_mymodel", "Can export my model data"),
           ]
   ```

### Staff vs Superuser

| Attribute | Staff (`is_staff=True`) | Superuser (`is_superuser=True`) |
|-----------|------------------------|----------------------------------|
| Admin Access | ✅ Yes | ✅ Yes |
| All Permissions | ❌ No (must be granted) | ✅ Yes (automatic) |
| Bypass Permission Checks | ❌ No | ✅ Yes |
| Use Case | Regular administrators | System administrators |

### Checking Permissions

```python
# In views
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

# In code
if user.has_perm('myapp.add_mymodel'):
    # Allow action
    pass

if user.is_superuser:
    # Superusers bypass all checks
    pass

# Check multiple permissions
if user.has_perms(['myapp.add_mymodel', 'myapp.change_mymodel']):
    pass
```

### Granting Permissions

```python
# Via Django admin or code
from django.contrib.auth.models import Permission, User

user = User.objects.get(username='john')
permission = Permission.objects.get(codename='add_customer')
user.user_permissions.add(permission)

# Via groups (recommended)
from django.contrib.auth.models import Group

# Create group
managers_group = Group.objects.create(name='Managers')
managers_group.permissions.add(permission)

# Add user to group
user.groups.add(managers_group)
```

---

## Guest Mode

### Overview

Guest mode allows limited, read-only access without authentication.

### Implementation

```python
# apps/core/permissions.py
from rest_framework.permissions import BasePermission

class AllowGuestReadOnly(BasePermission):
    """
    Allow guest users read-only access to specific endpoints.
    """
    def has_permission(self, request, view):
        # Allow all GET/HEAD/OPTIONS
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Require authentication for modifications
        return request.user and request.user.is_authenticated

# Usage in views
class PublicViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowGuestReadOnly]
    queryset = PublicData.objects.all()
```

### Guest User Detection

```python
def is_guest_user(user):
    """Check if user is in guest mode"""
    return not user.is_authenticated or user.groups.filter(name='Guests').exists()

# In view
if is_guest_user(request.user):
    # Restrict to read-only
    queryset = queryset.filter(is_public=True)
```

### Configuration

```python
# settings/base.py
GUEST_MODE_ENABLED = os.getenv('GUEST_MODE_ENABLED', 'false').lower() == 'true'

# Middleware to handle guest sessions
MIDDLEWARE = [
    # ...
    'apps.core.middleware.GuestSessionMiddleware',
]
```

---

## Multi-Tenant Authentication

### Tenant Resolution

```python
# apps/tenants/middleware.py
class TenantMiddleware:
    """Resolve tenant from request and set in thread-local"""
    
    def __call__(self, request):
        # Get tenant from domain
        tenant = self.get_tenant(request)
        
        # Set in thread-local for access anywhere
        set_current_tenant(tenant)
        
        response = self.get_response(request)
        return response
```

### User-Tenant Association

```python
# apps/tenants/models.py
class TenantUser(models.Model):
    """Links users to tenants with role"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['tenant', 'user']

# Check user's tenant
def get_user_tenants(user):
    return Tenant.objects.filter(
        tenantuser__user=user,
        tenantuser__is_active=True
    )
```

### Filtering by Tenant

```python
# In views
class CustomerViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        tenant = get_current_tenant()
        return Customer.objects.filter(tenant=tenant)

# In managers
class TenantAwareManager(models.Manager):
    def get_queryset(self):
        tenant = get_current_tenant()
        return super().get_queryset().filter(tenant=tenant)

class Customer(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    objects = TenantAwareManager()
```

---

## Best Practices

### 1. Never Hardcode Credentials

❌ **Don't**:
```python
SUPERUSER_USERNAME = "admin"
SUPERUSER_PASSWORD = "password123"
```

✅ **Do**:
```python
SUPERUSER_USERNAME = os.getenv('DEVELOPMENT_SUPERUSER_USERNAME')
SUPERUSER_PASSWORD = os.getenv('DEVELOPMENT_SUPERUSER_PASSWORD')
```

### 2. Use Groups for Permission Management

❌ **Don't** assign permissions individually to users

✅ **Do** create groups and assign permissions to groups:

```python
# Create role groups
admin_group = Group.objects.create(name='Administrators')
manager_group = Group.objects.create(name='Managers')
staff_group = Group.objects.create(name='Staff')

# Assign permissions to groups
admin_permissions = Permission.objects.filter(
    codename__in=['add_customer', 'change_customer', 'delete_customer', 'view_customer']
)
admin_group.permissions.set(admin_permissions)

# Assign users to groups
user.groups.add(manager_group)
```

### 3. Rotate Credentials Regularly

```bash
# Update environment variables
# For production: Update GitHub Secrets
# For development: Update config/environments/development.env

# Run sync command to apply
make sync-superuser
```

### 4. Validate Permissions in Views

```python
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'], 
            permission_classes=[IsAuthenticated, HasApprovalPermission])
    def approve(self, request, pk=None):
        # Only users with approval permission can execute
        pass
```

### 5. Log Authentication Events

```python
import logging

logger = logging.getLogger(__name__)

def login_user(request, user):
    login(request, user)
    logger.info(f"User {user.username} logged in from {request.META.get('REMOTE_ADDR')}")

def failed_login(username, ip):
    logger.warning(f"Failed login attempt for {username} from {ip}")
```

---

## Troubleshooting

### Issue: Superuser Creation Fails

**Symptom**:
```
CommandError: Environment variable not set
```

**Solution**:
```bash
# Check environment variables
echo $DJANGO_ENV
echo $DEVELOPMENT_SUPERUSER_USERNAME
echo $DEVELOPMENT_SUPERUSER_PASSWORD

# Set if missing
export DJANGO_ENV=development
export DEVELOPMENT_SUPERUSER_USERNAME=admin
export DEVELOPMENT_SUPERUSER_PASSWORD=SecurePass123!

# Or use environment file
python config/manage_env.py setup development
```

### Issue: Permission Denied in Admin

**Symptom**: User with `is_staff=True` cannot access admin panel

**Cause**: Missing permissions

**Solution**:
```python
# Make user superuser (has all permissions)
user.is_superuser = True
user.save()

# Or grant specific admin permissions
from django.contrib.auth.models import Permission

perms = Permission.objects.filter(
    content_type__app_label='myapp',
    codename__in=['add_mymodel', 'change_mymodel', 'view_mymodel']
)
user.user_permissions.set(perms)
```

### Issue: Multi-Tenant Permission Leakage

**Symptom**: Users seeing data from other tenants

**Cause**: Missing tenant filtering

**Solution**:
```python
# Always filter by tenant
class CustomerViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        tenant = get_current_tenant()
        if not tenant:
            return Customer.objects.none()  # No access if tenant unknown
        return Customer.objects.filter(tenant=tenant)
    
    def perform_create(self, serializer):
        # Automatically set tenant on creation
        serializer.save(tenant=get_current_tenant())
```

### Issue: Guest Mode Not Working

**Symptom**: Guest users getting authentication errors

**Cause**: Missing guest permission configuration

**Solution**:
```python
# Update permission classes
class PublicViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowGuestReadOnly]  # Allow unauthenticated
    
    def get_queryset(self):
        # Only show public data to guests
        if not self.request.user.is_authenticated:
            return self.queryset.filter(is_public=True)
        return self.queryset
```

---

## Deployment Integration

### Workflow Steps

```yaml
# .github/workflows/11-dev-deployment.yml
- name: Setup Superuser
  run: |
    cd backend
    python manage.py setup_superuser
  env:
    DJANGO_ENV: development
    DEVELOPMENT_SUPERUSER_USERNAME: ${{ secrets.DEV_SUPERUSER_USERNAME }}
    DEVELOPMENT_SUPERUSER_EMAIL: ${{ secrets.DEV_SUPERUSER_EMAIL }}
    DEVELOPMENT_SUPERUSER_PASSWORD: ${{ secrets.DEV_SUPERUSER_PASSWORD }}

- name: Create Super Tenant
  run: |
    cd backend
    python manage.py create_super_tenant
```

---

## Quick Reference

### Commands

```bash
# Sync superuser credentials
make sync-superuser

# Create superuser and tenant
make superuser

# Check user permissions
cd backend && python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> user.get_all_permissions()
>>> user.has_perm('customers.add_customer')

# Grant permission
>>> from django.contrib.auth.models import Permission
>>> perm = Permission.objects.get(codename='add_customer')
>>> user.user_permissions.add(perm)
```

### Environment Variables Checklist

- [ ] `DJANGO_ENV` set correctly
- [ ] `{ENV}_SUPERUSER_USERNAME` configured
- [ ] `{ENV}_SUPERUSER_EMAIL` configured
- [ ] `{ENV}_SUPERUSER_PASSWORD` configured (strong password)
- [ ] Secrets configured in GitHub (staging/production)
- [ ] Environment files not committed to git

---

## Additional Resources

- [Django Authentication Docs](https://docs.djangoproject.com/en/4.2/topics/auth/)
- [DRF Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- Internal: `docs/lessons-learned/3-MONTH-RETROSPECTIVE.md`
- Internal: `docs/MULTI_TENANCY_GUIDE.md`

---

**Maintainer**: Development Team  
**Review Cycle**: Monthly  
**Related Docs**: `docs/DEPLOYMENT_GUIDE.md`, `docs/TROUBLESHOOTING.md`
