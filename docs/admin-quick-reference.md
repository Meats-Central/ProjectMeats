# Quick Reference Guide for PostgreSQL Queries

This guide provides common PostgreSQL queries for managing tenants, users, and permissions in the ProjectMeats multi-tenancy system.

## Overview

ProjectMeats uses a **shared-schema multi-tenancy** approach with django-tenants compatibility. Data isolation is achieved through application-level filtering using tenant associations rather than separate PostgreSQL schemas.

---

## Tenants

### List All Tenants (Shared-Schema Approach)

```sql
-- List all tenants from the shared-schema Tenant model
SELECT 
    id,
    name,
    slug,
    schema_name,
    contact_email,
    is_active,
    is_trial,
    trial_ends_at,
    created_at
FROM tenants_tenant
ORDER BY created_at DESC;
```

### List All Clients (Django-Tenants Schema-Based)

```sql
-- For schema-based multi-tenancy (Client model)
SELECT 
    id,
    schema_name,
    name,
    description,
    created_at,
    updated_at
FROM tenants_client
ORDER BY created_at DESC;
```

### Find Tenant by Slug

```sql
SELECT * FROM tenants_tenant WHERE slug = 'your-tenant-slug';
```

### Find Active Tenants on Trial

```sql
SELECT 
    id,
    name,
    slug,
    contact_email,
    trial_ends_at
FROM tenants_tenant 
WHERE is_active = TRUE 
  AND is_trial = TRUE 
  AND (trial_ends_at IS NULL OR trial_ends_at > NOW())
ORDER BY trial_ends_at;
```

### Tenant Domains (Shared-Schema)

```sql
-- List all tenant domains
SELECT 
    td.id,
    td.domain,
    td.is_primary,
    t.name AS tenant_name,
    t.slug AS tenant_slug
FROM tenants_tenantdomain td
JOIN tenants_tenant t ON td.tenant_id = t.id
ORDER BY t.name, td.is_primary DESC;
```

### Domains (Django-Tenants Schema-Based)

```sql
-- List domains for schema-based multi-tenancy
SELECT 
    d.id,
    d.domain,
    d.is_primary,
    c.name AS client_name,
    c.schema_name
FROM tenants_domain d
JOIN tenants_client c ON d.tenant_id = c.id
ORDER BY c.name, d.is_primary DESC;
```

---

## Users

### List All Users

```sql
-- List all Django auth users
SELECT 
    id,
    username,
    email,
    first_name,
    last_name,
    is_active,
    is_staff,
    is_superuser,
    date_joined,
    last_login
FROM auth_user
ORDER BY date_joined DESC;
```

### Find User by Email

```sql
SELECT * FROM auth_user WHERE email = 'user@example.com';
```

### Active Users Count

```sql
SELECT COUNT(*) AS active_users FROM auth_user WHERE is_active = TRUE;
```

### Recently Logged In Users

```sql
SELECT 
    id,
    username,
    email,
    last_login
FROM auth_user 
WHERE last_login IS NOT NULL
ORDER BY last_login DESC
LIMIT 10;
```

---

## Admins and Superusers

### List All Superusers

```sql
-- Superusers have full access to the system
SELECT 
    id,
    username,
    email,
    is_staff,
    is_superuser,
    date_joined
FROM auth_user 
WHERE is_superuser = TRUE
ORDER BY date_joined;
```

### List Staff Users (Django Admin Access)

```sql
-- Staff users can access Django admin
SELECT 
    id,
    username,
    email,
    is_staff,
    is_superuser,
    date_joined
FROM auth_user 
WHERE is_staff = TRUE
ORDER BY date_joined;
```

### Tenant Owners (Owner Role in TenantUser)

```sql
-- List users who are owners of tenants
SELECT 
    au.id,
    au.username,
    au.email,
    t.name AS tenant_name,
    t.slug AS tenant_slug,
    tu.created_at AS ownership_since
FROM auth_user au
JOIN tenants_tenant_user tu ON au.id = tu.user_id
JOIN tenants_tenant t ON tu.tenant_id = t.id
WHERE tu.role = 'owner'
ORDER BY t.name, au.username;
```

> **Note:** The `is_owner` field is not a native Django field. Ownership is tracked via the `TenantUser.role` field with value `'owner'`. If a custom `is_owner` boolean field is needed, it should be added to a custom User profile model.
> 
> **TODO:** Consider adding an `is_owner` computed property or custom field if direct owner lookups are frequently needed.

---

## User-Tenant Associations

### List All User-Tenant Relationships

```sql
-- Show all user-tenant associations with roles
SELECT 
    au.id AS user_id,
    au.username,
    au.email,
    t.id AS tenant_id,
    t.name AS tenant_name,
    t.slug AS tenant_slug,
    tu.role,
    tu.is_active AS membership_active,
    tu.created_at AS joined_at
FROM auth_user au
JOIN tenants_tenant_user tu ON au.id = tu.user_id
JOIN tenants_tenant t ON tu.tenant_id = t.id
ORDER BY t.name, tu.role, au.username;
```

### Find Users in a Specific Tenant

```sql
SELECT 
    au.id,
    au.username,
    au.email,
    tu.role,
    tu.is_active,
    tu.created_at
FROM auth_user au
JOIN tenants_tenant_user tu ON au.id = tu.user_id
JOIN tenants_tenant t ON tu.tenant_id = t.id
WHERE t.slug = 'your-tenant-slug'
ORDER BY tu.role, au.username;
```

### Find Tenants for a Specific User

```sql
SELECT 
    t.id,
    t.name,
    t.slug,
    tu.role,
    tu.is_active
FROM tenants_tenant t
JOIN tenants_tenant_user tu ON t.id = tu.tenant_id
JOIN auth_user au ON tu.user_id = au.id
WHERE au.username = 'your-username'
ORDER BY tu.role, t.name;
```

### Users with Multiple Tenant Memberships

```sql
SELECT 
    au.id,
    au.username,
    au.email,
    COUNT(tu.tenant_id) AS tenant_count
FROM auth_user au
JOIN tenants_tenant_user tu ON au.id = tu.user_id
WHERE tu.is_active = TRUE
GROUP BY au.id, au.username, au.email
HAVING COUNT(tu.tenant_id) > 1
ORDER BY tenant_count DESC;
```

---

## Roles and Permissions

### Available Roles in TenantUser

The `TenantUser` model supports these roles:

| Role     | Description                              |
|----------|------------------------------------------|
| owner    | Full tenant ownership and management     |
| admin    | Administrator with elevated permissions  |
| manager  | Manager level access                     |
| user     | Standard user access                     |
| readonly | View-only access                         |

### List All Groups (Django Auth Groups)

```sql
SELECT * FROM auth_group ORDER BY name;
```

### List All Permissions

```sql
SELECT 
    p.id,
    p.name,
    p.codename,
    ct.app_label,
    ct.model
FROM auth_permission p
JOIN django_content_type ct ON p.content_type_id = ct.id
ORDER BY ct.app_label, ct.model, p.codename;
```

### User Permissions (Direct)

```sql
-- Permissions directly assigned to users
SELECT 
    au.username,
    p.codename AS permission,
    ct.app_label,
    ct.model
FROM auth_user au
JOIN auth_user_user_permissions uup ON au.id = uup.user_id
JOIN auth_permission p ON uup.permission_id = p.id
JOIN django_content_type ct ON p.content_type_id = ct.id
ORDER BY au.username, ct.app_label, p.codename;
```

### User Permissions (via Groups)

```sql
-- Permissions inherited through group membership
SELECT 
    au.username,
    ag.name AS group_name,
    p.codename AS permission,
    ct.app_label,
    ct.model
FROM auth_user au
JOIN auth_user_groups ug ON au.id = ug.user_id
JOIN auth_group ag ON ug.group_id = ag.id
JOIN auth_group_permissions gp ON ag.id = gp.group_id
JOIN auth_permission p ON gp.permission_id = p.id
JOIN django_content_type ct ON p.content_type_id = ct.id
ORDER BY au.username, ag.name, ct.app_label, p.codename;
```

### Role Distribution per Tenant

```sql
SELECT 
    t.name AS tenant_name,
    t.slug AS tenant_slug,
    tu.role,
    COUNT(*) AS user_count
FROM tenants_tenant_user tu
JOIN tenants_tenant t ON tu.tenant_id = t.id
WHERE tu.is_active = TRUE
GROUP BY t.name, t.slug, tu.role
ORDER BY t.name, tu.role;
```

---

## Tenant Invitations

### List Pending Invitations

```sql
SELECT 
    ti.id,
    ti.email,
    ti.role,
    ti.status,
    t.name AS tenant_name,
    au.username AS invited_by,
    ti.created_at,
    ti.expires_at
FROM tenants_invitation ti
JOIN tenants_tenant t ON ti.tenant_id = t.id
LEFT JOIN auth_user au ON ti.invited_by_id = au.id
WHERE ti.status = 'pending'
ORDER BY ti.expires_at;
```

### Invitations by Status

```sql
SELECT 
    ti.status,
    COUNT(*) AS invitation_count
FROM tenants_invitation ti
GROUP BY ti.status
ORDER BY ti.status;
```

### Expired but Not Updated Invitations

```sql
-- Find invitations that have expired but status not updated
SELECT 
    ti.id,
    ti.email,
    t.name AS tenant_name,
    ti.status,
    ti.expires_at
FROM tenants_invitation ti
JOIN tenants_tenant t ON ti.tenant_id = t.id
WHERE ti.status = 'pending' 
  AND ti.expires_at < NOW()
ORDER BY ti.expires_at;
```

---

# Initialization Scripts

This section provides Python scripts for initializing tenants and users in the ProjectMeats system.

## Superuser Level: Create Super Tenant and Superuser

Use this script to create the initial "super" tenant and superuser for system administration.

```python
#!/usr/bin/env python
"""
Script to create a super tenant and superuser for ProjectMeats.

Usage:
    python manage.py shell < create_super_tenant.py
    
Or in Django shell:
    exec(open('scripts/create_super_tenant.py').read())
"""
import os
from django.contrib.auth.models import User
from django.db import transaction
from apps.tenants.models import Tenant, TenantUser, TenantDomain

# Configuration - customize these values
SUPER_TENANT_NAME = os.getenv('SUPER_TENANT_NAME', 'Super Admin Tenant')
SUPER_TENANT_SLUG = os.getenv('SUPER_TENANT_SLUG', 'super-admin')
SUPER_TENANT_EMAIL = os.getenv('SUPER_TENANT_EMAIL', 'admin@projectmeats.com')
SUPER_TENANT_DOMAIN = os.getenv('SUPER_TENANT_DOMAIN', 'admin.localhost')

SUPERUSER_USERNAME = os.getenv('SUPERUSER_USERNAME', 'admin')
SUPERUSER_EMAIL = os.getenv('SUPERUSER_EMAIL', 'admin@projectmeats.com')
SUPERUSER_PASSWORD = os.getenv('SUPERUSER_PASSWORD', 'changeme123!')


def create_super_tenant():
    """Create or get the super admin tenant."""
    try:
        with transaction.atomic():
            # Check if super tenant exists
            tenant, created = Tenant.objects.get_or_create(
                slug=SUPER_TENANT_SLUG,
                defaults={
                    'name': SUPER_TENANT_NAME,
                    'contact_email': SUPER_TENANT_EMAIL,
                    'is_active': True,
                    'is_trial': False,  # Super tenant is not on trial
                }
            )
            
            if created:
                print(f'✅ Created super tenant: {tenant.name} ({tenant.slug})')
                
                # Create domain for super tenant
                domain, _ = TenantDomain.objects.get_or_create(
                    domain=SUPER_TENANT_DOMAIN,
                    defaults={
                        'tenant': tenant,
                        'is_primary': True,
                    }
                )
                print(f'   ↳ Domain: {domain.domain}')
            else:
                print(f'ℹ️  Super tenant already exists: {tenant.name} ({tenant.slug})')
            
            return tenant
    except Exception as e:
        print(f'❌ Error creating super tenant: {e}')
        raise


def create_superuser(tenant):
    """Create or get the superuser and associate with super tenant."""
    try:
        with transaction.atomic():
            # Check if superuser exists
            user, created = User.objects.get_or_create(
                username=SUPERUSER_USERNAME,
                defaults={
                    'email': SUPERUSER_EMAIL,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            
            if created:
                user.set_password(SUPERUSER_PASSWORD)
                user.save()
                print(f'✅ Created superuser: {user.username} ({user.email})')
                print(f'   ⚠️  Please change the password immediately!')
            else:
                # Ensure existing user has superuser privileges
                if not user.is_superuser:
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                    print(f'ℹ️  Updated user to superuser: {user.username}')
                else:
                    print(f'ℹ️  Superuser already exists: {user.username}')
            
            # Associate superuser with super tenant as owner
            tenant_user, tu_created = TenantUser.objects.get_or_create(
                tenant=tenant,
                user=user,
                defaults={
                    'role': 'owner',
                    'is_active': True,
                }
            )
            
            if tu_created:
                print(f'✅ Associated superuser with super tenant as owner')
            else:
                print(f'ℹ️  Superuser already associated with super tenant')
            
            return user
    except Exception as e:
        print(f'❌ Error creating superuser: {e}')
        raise


def main():
    """Main entry point."""
    print('\n' + '=' * 60)
    print('SUPER TENANT & SUPERUSER INITIALIZATION')
    print('=' * 60 + '\n')
    
    tenant = create_super_tenant()
    user = create_superuser(tenant)
    
    print('\n' + '=' * 60)
    print('INITIALIZATION COMPLETE')
    print('=' * 60)
    print(f'\nTenant: {tenant.name} ({tenant.slug})')
    print(f'Domain: {SUPER_TENANT_DOMAIN}')
    print(f'Superuser: {user.username} ({user.email})')
    print('\nNext steps:')
    print('  1. Change the superuser password')
    print('  2. Configure tenant settings as needed')
    print('  3. Create additional tenants and users')
    print('')


if __name__ == '__main__':
    main()
```

---

## New Tenant Onboarding Script

Use this script to create a new tenant, associate a domain, create an initial admin user, and generate a reusable invitation link.

```python
#!/usr/bin/env python
"""
Script to onboard a new tenant with admin user and invitation link.

Usage:
    python manage.py shell
    >>> from scripts.onboard_tenant import onboard_new_tenant
    >>> result = onboard_new_tenant(
    ...     schema_name='acme_corp',
    ...     name='ACME Corporation',
    ...     domain='acme.example.com',
    ...     admin_email='admin@acme.com',
    ...     admin_password='secure_password_123'
    ... )
"""
import uuid
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from apps.tenants.models import Tenant, TenantUser, TenantDomain, TenantInvitation


def onboard_new_tenant(
    schema_name: str,
    name: str,
    domain: str,
    admin_email: str,
    admin_password: str,
    admin_username: str = None,
    is_trial: bool = True,
    trial_days: int = 30,
    invitation_days_valid: int = 7,
) -> dict:
    """
    Onboard a new tenant with initial admin user and invitation link.
    
    Args:
        schema_name: Unique schema identifier (e.g., 'acme_corp')
        name: Tenant organization name
        domain: Primary domain for the tenant
        admin_email: Email for the initial admin user
        admin_password: Password for the initial admin user
        admin_username: Username (defaults to email prefix)
        is_trial: Whether tenant starts on trial
        trial_days: Number of trial days if on trial
        invitation_days_valid: Days until invitation expires
    
    Returns:
        dict with tenant, admin_user, and invitation_link
    
    Raises:
        ValueError: If tenant or user already exists
    """
    # Generate defaults
    if not admin_username:
        admin_username = admin_email.split('@')[0]
    
    slug = schema_name.replace('_', '-')
    
    try:
        with transaction.atomic():
            # 1. Create the Tenant
            print(f'\n🏢 Creating tenant: {name}...')
            
            if Tenant.objects.filter(slug=slug).exists():
                raise ValueError(f'Tenant with slug "{slug}" already exists')
            
            if Tenant.objects.filter(schema_name=schema_name).exists():
                raise ValueError(f'Tenant with schema_name "{schema_name}" already exists')
            
            trial_ends_at = None
            if is_trial:
                trial_ends_at = timezone.now() + timedelta(days=trial_days)
            
            tenant = Tenant.objects.create(
                name=name,
                slug=slug,
                schema_name=schema_name,
                contact_email=admin_email,
                is_active=True,
                is_trial=is_trial,
                trial_ends_at=trial_ends_at,
            )
            print(f'   ✅ Tenant created: {tenant.name} ({tenant.id})')
            
            # 2. Create the Domain
            print(f'\n🌐 Creating domain: {domain}...')
            
            tenant_domain = TenantDomain.objects.create(
                domain=domain.lower(),
                tenant=tenant,
                is_primary=True,
            )
            print(f'   ✅ Domain created: {tenant_domain.domain} (primary)')
            
            # 3. Create the Admin User
            print(f'\n👤 Creating admin user: {admin_username}...')
            
            if User.objects.filter(username=admin_username).exists():
                raise ValueError(f'User with username "{admin_username}" already exists')
            
            if User.objects.filter(email=admin_email).exists():
                raise ValueError(f'User with email "{admin_email}" already exists')
            
            admin_user = User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                is_staff=True,  # Allow Django admin access
                is_active=True,
            )
            print(f'   ✅ Admin user created: {admin_user.username}')
            
            # 4. Associate Admin with Tenant as Owner
            print(f'\n🔗 Associating admin as tenant owner...')
            
            tenant_user = TenantUser.objects.create(
                tenant=tenant,
                user=admin_user,
                role='owner',
                is_active=True,
            )
            print(f'   ✅ Admin associated with tenant as {tenant_user.role}')
            
            # 5. Generate Reusable Invitation Link
            print(f'\n📧 Creating reusable invitation link...')
            
            invitation = TenantInvitation.objects.create(
                tenant=tenant,
                email='invite@' + domain,  # Generic invitation email
                role='user',  # Default role for new invitees
                invited_by=admin_user,
                expires_at=timezone.now() + timedelta(days=invitation_days_valid),
                message=f'Welcome to {name}! Use this link to join our organization.',
            )
            
            # Generate invitation URL
            invitation_url = f'https://{domain}/signup/?token={invitation.token}'
            print(f'   ✅ Invitation created')
            print(f'   📎 Invitation URL: {invitation_url}')
            
            # Summary
            print('\n' + '=' * 60)
            print('TENANT ONBOARDING COMPLETE')
            print('=' * 60)
            print(f'\nTenant Details:')
            print(f'  - Name: {tenant.name}')
            print(f'  - Slug: {tenant.slug}')
            print(f'  - Schema: {tenant.schema_name}')
            print(f'  - Domain: {tenant_domain.domain}')
            print(f'  - Trial: {"Yes" if tenant.is_trial else "No"}')
            if tenant.trial_ends_at:
                print(f'  - Trial Ends: {tenant.trial_ends_at.strftime("%Y-%m-%d")}')
            
            print(f'\nAdmin User:')
            print(f'  - Username: {admin_user.username}')
            print(f'  - Email: {admin_user.email}')
            print(f'  - Role: {tenant_user.role}')
            
            print(f'\nInvitation Link:')
            print(f'  - URL: {invitation_url}')
            print(f'  - Token: {invitation.token}')
            print(f'  - Expires: {invitation.expires_at.strftime("%Y-%m-%d %H:%M")}')
            print('')
            
            return {
                'tenant': tenant,
                'domain': tenant_domain,
                'admin_user': admin_user,
                'tenant_user': tenant_user,
                'invitation': invitation,
                'invitation_url': invitation_url,
            }
            
    except Exception as e:
        print(f'\n❌ Error during tenant onboarding: {e}')
        raise


def generate_invitation_link(tenant, request=None, role='user', days_valid=7):
    """
    Generate a reusable invitation link for a tenant.
    
    Args:
        tenant: Tenant instance
        request: Optional HTTP request for domain detection
        role: Role to assign to new users
        days_valid: Number of days until invitation expires
    
    Returns:
        tuple of (invitation, invitation_url)
    """
    # Get the primary domain for the tenant
    primary_domain = tenant.tenant_domains.filter(is_primary=True).first()
    
    if not primary_domain:
        # Fallback to tenant's domain field or generate from slug
        domain = tenant.domain or f'{tenant.slug}.example.com'
    else:
        domain = primary_domain.domain
    
    # Override with request host if provided
    if request:
        domain = request.get_host()
    
    # Create invitation
    invitation = TenantInvitation.objects.create(
        tenant=tenant,
        email=f'invite@{domain}',
        role=role,
        expires_at=timezone.now() + timedelta(days=days_valid),
        message=f'You have been invited to join {tenant.name}.',
    )
    
    # Generate URL
    protocol = 'https' if not domain.startswith('localhost') else 'http'
    invitation_url = f'{protocol}://{domain}/signup/?token={invitation.token}'
    
    return invitation, invitation_url


# Example usage when run directly
if __name__ == '__main__':
    # Example: Onboard a new tenant
    result = onboard_new_tenant(
        schema_name='demo_company',
        name='Demo Company',
        domain='demo.localhost',
        admin_email='admin@demo.localhost',
        admin_password='demo_password_123',
    )
```

---

## Using Management Commands

ProjectMeats provides management commands for common tenant operations:

### Create a New Tenant

```bash
# Basic tenant creation
python manage.py create_tenant \
    --schema-name=acme_corp \
    --name="ACME Corporation" \
    --domain=acme.example.com \
    --contact-email=admin@acme.com

# Tenant with trial period
python manage.py create_tenant \
    --schema-name=demo_co \
    --name="Demo Company" \
    --domain=demo.example.com \
    --on-trial \
    --paid-until=2024-12-31
```

### Initialize Tenant with Admin User

```bash
# Initialize tenant with admin user and invitation
python manage.py init_tenant \
    --schema-name=new_tenant \
    --name="New Tenant Inc" \
    --domain=newtenant.example.com \
    --admin-email=admin@newtenant.com \
    --admin-password=secure_password
```

### Add Domain to Existing Tenant

```bash
python manage.py add_tenant_domain \
    --tenant-slug=acme-corp \
    --domain=www.acme.com \
    --is-primary
```

---

## Utility Functions

The `apps.tenants.utils` module provides helper functions:

```python
from apps.tenants.utils import (
    create_demo_tenants,      # Create demo tenants for testing
    create_custom_tenants,    # Create custom tenant configurations
    create_single_tenant,     # Create a single tenant
    cleanup_demo_tenants,     # Remove demo tenants
    generate_invitation_link, # Generate invitation URL for tenant
)

# Create demo tenants for development
from apps.tenants.utils import create_demo_tenants
tenants = create_demo_tenants(environment='development', count=3)

# Generate invitation link for a tenant
from apps.tenants.utils import generate_invitation_link
from apps.tenants.models import Tenant

tenant = Tenant.objects.get(slug='acme-corp')
invitation, url = generate_invitation_link(tenant, role='admin', days_valid=14)
print(f'Invitation URL: {url}')
```

---

## Security Considerations

1. **Password Management**: Always use environment variables for sensitive credentials in production
2. **Invitation Tokens**: Tokens are cryptographically secure and expire automatically
3. **Role Assignment**: Validate role assignments to prevent privilege escalation
4. **Audit Trail**: TenantInvitation model tracks who created each invitation

---

## Related Documentation

- [Multi-Tenancy Guide](./MULTI_TENANCY_GUIDE.md)
- [Authentication Guide](./AUTHENTICATION_GUIDE.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Tenant Onboarding](../backend/apps/tenants/TENANT_ONBOARDING.md)
