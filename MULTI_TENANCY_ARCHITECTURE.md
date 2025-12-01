# ProjectMeats Multi-Tenancy Architecture Guide

**Version:** 1.0  
**Date:** 2025-12-01  
**Status:** Active Implementation  
**Type:** Custom Shared-Schema Multi-Tenancy

---

## 📋 Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Tenant Resolution Flow](#tenant-resolution-flow)
5. [Database Schema](#database-schema)
6. [Middleware & Request Flow](#middleware--request-flow)
7. [Management Commands](#management-commands)
8. [CI/CD Integration](#cicd-integration)
9. [Development Patterns](#development-patterns)
10. [Common Pitfalls](#common-pitfalls)
11. [Troubleshooting](#troubleshooting)

---

## Executive Summary

ProjectMeats implements **custom shared-schema multi-tenancy** using row-level isolation via foreign keys. 

### ⚠️ Critical Understanding

**ProjectMeats DOES NOT use django-tenants schema-based multi-tenancy.**

Despite the presence of legacy `Client` and `Domain` models from django-tenants in the codebase, these are **NOT actively used**. They exist for backward compatibility only.

### Key Facts

- **Database Strategy:** Single PostgreSQL database, single `public` schema
- **Isolation Method:** Row-level via `tenant` foreign key on all tenant-scoped models
- **Routing:** Custom `TenantMiddleware` resolves tenant from request context
- **Active Models:** `Tenant`, `TenantUser`, `TenantDomain` (custom shared-schema)
- **Legacy Models:** `Client`, `Domain` (NOT USED for multi-tenancy)

### Why This Matters

**Common Mistake:** Assuming django-tenants is active because models exist
**Consequence:** Using non-existent commands like `migrate_schemas`, `ensure_public_tenant`
**Result:** Deployment failures, HTTP 500 errors, migration issues

---

## Architecture Overview

### Shared-Schema Multi-Tenancy

```
┌─────────────────────────────────────────────────┐
│         Single PostgreSQL Database              │
├─────────────────────────────────────────────────┤
│  Schema: public                                 │
│  ├── tenants_tenant (tenant registry)          │
│  ├── tenants_tenantuser (user associations)    │
│  ├── tenants_tenantdomain (domain routing)     │
│  ├── customers_customer (tenant FK)            │
│  ├── suppliers_supplier (tenant FK)            │
│  ├── products_product (tenant FK)              │
│  └── ... (all tenant-scoped tables)            │
└─────────────────────────────────────────────────┘

Isolation Mechanism:
  SELECT * FROM customers_customer WHERE tenant_id = <current_tenant>
```

### Request Flow

```
┌──────────────┐
│ HTTP Request │
└──────┬───────┘
       │
       ▼
┌────────────────────────────┐
│   TenantMiddleware         │
│   Resolves tenant from:    │
│   1. X-Tenant-ID header    │
│   2. Domain match          │
│   3. Subdomain extraction  │
│   4. User's default tenant │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│  request.tenant = Tenant   │
│  request.tenant_user = ... │
└──────┬─────────────────────┘
       │
       ▼
┌────────────────────────────┐
│   ViewSet/View             │
│   Filters by tenant:       │
│   queryset.filter(         │
│     tenant=request.tenant  │
│   )                        │
└────────────────────────────┘
```

---

## Core Components

### 1. Tenant Model (`apps.tenants.models.Tenant`)

**Primary tenant registry** for shared-schema multi-tenancy.

```python
class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    slug = models.SlugField(unique=True, max_length=100)
    name = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=False)
    settings = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Usage:**
- Every tenant-scoped model has: `tenant = models.ForeignKey(Tenant, ...)`
- Queries filter by: `Model.objects.filter(tenant=request.tenant)`
- Creation auto-assigns: `obj.tenant = request.tenant`

**Example Tenants:**
- Root tenant (slug: 'root') - Main organization
- Guest tenant (slug: 'guest-demo') - Trial/demo access
- Customer tenants (slug: company-name) - Individual customers

### 2. TenantUser Model (`apps.tenants.models.TenantUser`)

**User-to-Tenant association** with role-based access control.

```python
class TenantUser(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),      # Full control
        ('admin', 'Admin'),      # Manage users & data
        ('member', 'Member'),    # Read/write data
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
```

**Role Permissions:**

| Role | Can Delete Tenant | Can Manage Users | Can Modify Data | Can View Data |
|------|------------------|------------------|-----------------|---------------|
| owner | ✅ | ✅ | ✅ | ✅ |
| admin | ❌ | ✅ | ✅ | ✅ |
| member | ❌ | ❌ | ✅ | ✅ |

**Multi-Tenant Users:**
- A user can belong to multiple tenants
- Each association has its own role
- Middleware prioritizes owner/admin roles for default tenant

### 3. TenantDomain Model (`apps.tenants.models.TenantDomain`)

**Domain-to-Tenant routing** for shared-schema approach.

```python
class TenantDomain(models.Model):
    domain = models.CharField(max_length=253, unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Current Production Mappings:**
- `dev.meatscentral.com` → Development tenant
- `uat.meatscentral.com` → UAT/Staging tenant
- `meatscentral.com` → Production root tenant

**Workflow:**
1. Request arrives at `uat.meatscentral.com`
2. Middleware queries: `TenantDomain.objects.get(domain='uat.meatscentral.com')`
3. Gets associated `Tenant` object
4. Sets `request.tenant` for filtering

### 4. Legacy Models (NOT USED)

#### Client Model (`apps.tenants.models.Client`)

```python
class Client(models.Model):
    schema_name = models.CharField(max_length=63, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
```

**⚠️ WARNING:** This is a django-tenants model for schema-based tenancy.
**NOT USED** for active multi-tenancy in ProjectMeats.

#### Domain Model (`apps.tenants.models.Domain`)

```python
class Domain(models.Model):
    domain = models.CharField(max_length=253, unique=True)
    tenant = models.ForeignKey(Client, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=True)
```

**⚠️ WARNING:** This is a django-tenants model for schema routing.
**NOT USED** for active domain routing (use `TenantDomain` instead).

**Why They Exist:**
- Historical: ProjectMeats initially explored django-tenants
- Migrated: Moved to custom shared-schema for simplicity
- Compatibility: Kept models to avoid breaking old migrations
- Future: May be removed in major version upgrade

---

## Tenant Resolution Flow

### TenantMiddleware (`apps.tenants.middleware.TenantMiddleware`)

**Purpose:** Automatically resolve and set `request.tenant` on every request.

### Resolution Priority (High → Low)

#### 1. X-Tenant-ID Header (Explicit Selection)

**Use Case:** API clients specifying tenant

```bash
curl -H "X-Tenant-ID: 550e8400-e29b-41d4-a716-446655440000" \
  https://api.meatscentral.com/api/v1/customers/
```

**Behavior:**
- Validates user has `TenantUser` association
- Returns 403 Forbidden if user lacks access
- Superusers can access any tenant

#### 2. Domain Match (via TenantDomain)

**Use Case:** Web browsers accessing tenant-specific domains

```
Request: https://uat.meatscentral.com/api/v1/health/
Resolves: TenantDomain.objects.get(domain='uat.meatscentral.com').tenant
```

**Behavior:**
- Matches full domain (no wildcards)
- Case-sensitive
- Requires `TenantDomain` entry to exist

#### 3. Subdomain Extraction

**Use Case:** Multi-tenant SaaS with subdomains

```
Request: https://acme.meatscentral.com/dashboard/
Resolves: Tenant.objects.get(slug='acme', is_active=True)
```

**Behavior:**
- Extracts first subdomain segment
- Ignores 'www'
- Matches against `tenant.slug`

#### 4. User's Default Tenant (Fallback)

**Use Case:** Authenticated users without explicit tenant context

```python
TenantUser.objects.filter(
    user=request.user,
    is_active=True
).order_by('-role').first().tenant
```

**Behavior:**
- Only for authenticated users
- Prioritizes owner → admin → member roles
- Returns first active association

### Special Case: Health Check Bypass

```python
# In middleware __call__ method
if request.path.startswith('/api/v1/health/') or \
   request.path.startswith('/api/v1/ready/'):
    request.tenant = None
    request.tenant_user = None
    return self.get_response(request)
```

**Why:**
- Health checks run during deployment before tenants exist
- Middleware database queries would fail on empty database
- Prevents chicken-and-egg problems

**Endpoints Bypassed:**
- `/api/v1/health/` - Basic health check
- `/api/v1/ready/` - Readiness probe

---

## Database Schema

### Migrations

**✅ CORRECT: Standard Django Migrations**

```bash
# Apply all migrations
python manage.py migrate --noinput

# Check migration status
python manage.py showmigrations

# Create new migration
python manage.py makemigrations <app_name>
```

**❌ INCORRECT: django-tenants Commands**

```bash
# These commands DO NOT EXIST and will FAIL
python manage.py migrate_schemas --shared      # ❌
python manage.py migrate_schemas --tenant      # ❌
python manage.py ensure_public_tenant          # ❌
python manage.py create_tenant                 # ❌
```

**Why They Don't Exist:**
- django-tenants is NOT in `INSTALLED_APPS`
- `TenantMainMiddleware` is NOT in `MIDDLEWARE`
- No `TENANT_APPS` / `SHARED_APPS` configuration
- Using custom shared-schema approach instead

### Deployment Migration Order

```bash
# 1. Run standard Django migrations
python manage.py migrate --noinput

# 2. Create tenants (idempotent)
python manage.py create_super_tenant --verbosity=1
python manage.py create_guest_tenant --verbosity=1

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Start application
gunicorn projectmeats.wsgi:application
```

---

## Management Commands

### create_super_tenant

**Purpose:** Idempotent creation of superuser and root tenant.

**Location:** `backend/apps/core/management/commands/create_super_tenant.py`

**Usage:**
```bash
# Use environment variables
python manage.py create_super_tenant --verbosity=1

# Override with CLI args
python manage.py create_super_tenant \
  --username admin \
  --email admin@example.com \
  --password securepass123
```

**Environment Variables (by environment):**

**Development:**
- `DEVELOPMENT_SUPERUSER_EMAIL`
- `DEVELOPMENT_SUPERUSER_PASSWORD`
- `DEVELOPMENT_SUPERUSER_USERNAME`

**UAT/Staging:**
- `STAGING_SUPERUSER_EMAIL`
- `STAGING_SUPERUSER_PASSWORD`
- `STAGING_SUPERUSER_USERNAME`

**Production:**
- `PRODUCTION_SUPERUSER_EMAIL`
- `PRODUCTION_SUPERUSER_PASSWORD`
- `PRODUCTION_SUPERUSER_USERNAME`

**Fallback:** `SUPERUSER_EMAIL`, `SUPERUSER_PASSWORD`, `SUPERUSER_USERNAME`

**What It Does:**
1. Creates or updates Django superuser (`is_superuser=True`, `is_staff=True`)
2. Creates `Tenant(slug='root', name='Root')`
3. Creates `TenantUser(user=superuser, tenant=root, role='owner')`
4. Handles duplicate users gracefully (deletes extras, keeps first)

**Idempotency:**
- Safe to run multiple times
- Uses `get_or_create` for tenant
- Updates password if user exists
- No duplicate creation errors

### create_guest_tenant

**Purpose:** Create demo tenant and guest user for trials.

**Location:** `backend/apps/core/management/commands/create_guest_tenant.py`

**Usage:**
```bash
# Use defaults
python manage.py create_guest_tenant --verbosity=1

# Customize
python manage.py create_guest_tenant \
  --username demo \
  --password demo123 \
  --tenant-name "Demo Organization" \
  --tenant-slug demo-org
```

**Defaults:**
- Username: `guest`
- Password: `guest123`
- Tenant Name: `Guest Demo Organization`
- Tenant Slug: `guest-demo`

**What It Does:**
1. Creates `User(username='guest', is_staff=True, is_superuser=False)`
2. Creates `Tenant(slug='guest-demo', is_trial=True)`
3. Creates `TenantUser(user=guest, tenant=guest_demo, role='admin')`
4. Grants Django admin permissions for tenant-scoped models

**Guest User Permissions:**

✅ **CAN:**
- View/add/change/delete: Customers, Suppliers, Contacts, Products, POs, SOs, Invoices
- Access Django admin at `/admin/` (for testing)
- Full CRUD within guest tenant via API

❌ **CANNOT:**
- Manage users or permissions (not superuser)
- Access system-wide settings
- View/modify other tenants' data
- Delete guest tenant (admin role, not owner)

---

## CI/CD Integration

### GitHub Actions Pattern

**✅ CORRECT Deployment Workflow:**

```yaml
# Step 1: Apply Migrations
- name: Run migrations
  run: |
    cd backend
    python manage.py migrate --noinput

# Step 2: Setup Tenants (Idempotent)
- name: Create super tenant
  run: |
    cd backend
    python manage.py create_super_tenant --verbosity=1 || true

- name: Create guest tenant
  run: |
    cd backend
    python manage.py create_guest_tenant --verbosity=1 || true

# Step 3: Collect Static Files
- name: Collect static
  run: |
    cd backend
    python manage.py collectstatic --noinput

# Step 4: Health Check
- name: Health check
  run: |
    curl -f http://localhost:8000/api/v1/health/
```

**❌ INCORRECT (Old Pattern):**

```yaml
# DO NOT USE - These commands don't exist
- name: Run migrations
  run: |
    python manage.py migrate_schemas --shared --noinput
    python manage.py ensure_public_tenant --domain=example.com
    python manage.py migrate_schemas --noinput
```

### Common CI/CD Errors

#### Error: "Command 'migrate_schemas' not found"

**Cause:** Workflow trying to use django-tenants commands  
**Fix:** Replace with `python manage.py migrate --noinput`

#### Error: HTTP 500 on Health Check

**Possible Causes:**
1. Migrations didn't run
2. TenantDomain missing for domain
3. Middleware querying before tables exist

**Fix:**
1. Ensure `migrate` runs before server starts
2. Create TenantDomain entries for deployment domains
3. Verify health endpoint bypass in middleware

---

## Development Patterns

### Adding Tenant-Scoped Models

**Checklist:**

1. **Add tenant foreign key:**
```python
class NewModel(models.Model):
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='new_models'
    )
    # ... other fields
```

2. **Add created_by tracking:**
```python
created_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='created_new_models'
)
```

3. **Update ViewSet:**
```python
class NewModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        if not self.request.tenant:
            return NewModel.objects.none()
        return NewModel.objects.filter(tenant=self.request.tenant)
    
    def perform_create(self, serializer):
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user
        )
```

4. **Create migration:**
```bash
python manage.py makemigrations your_app
python manage.py migrate
```

### ViewSet Pattern (Tenant Filtering)

```python
# ✅ CORRECT: Always filter by tenant
class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    
    def get_queryset(self):
        # Return empty if no tenant context
        if not self.request.tenant:
            return Customer.objects.none()
        
        # Filter by current tenant
        return Customer.objects.filter(
            tenant=self.request.tenant
        ).select_related('created_by')
    
    def perform_create(self, serializer):
        # Validate tenant context exists
        if not self.request.tenant:
            raise ValidationError("Tenant context required")
        
        # Auto-inject tenant and user
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user
        )
    
    def perform_update(self, serializer):
        # Verify object belongs to current tenant
        if serializer.instance.tenant != self.request.tenant:
            raise PermissionDenied("Cannot modify other tenant's data")
        
        serializer.save()
```

**Key Points:**
- Always check `request.tenant` exists
- Return `.none()` if no tenant (prevents data leakage)
- Auto-inject tenant on create
- Validate tenant ownership on modify

### Public/Shared Models (No Tenant FK)

Some models are shared across all tenants:
- `User` (django.contrib.auth.models.User)
- `Tenant` (apps.tenants.models.Tenant)
- `TenantUser` (apps.tenants.models.TenantUser)
- `TenantDomain` (apps.tenants.models.TenantDomain)

**Pattern:**
```python
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    
    def get_queryset(self):
        # Show only users in current tenant
        if not self.request.tenant:
            return User.objects.none()
        
        tenant_user_ids = TenantUser.objects.filter(
            tenant=self.request.tenant,
            is_active=True
        ).values_list('user_id', flat=True)
        
        return User.objects.filter(id__in=tenant_user_ids)
```

---

## Common Pitfalls

### 1. Forgetting Tenant Filter

```python
# ❌ BAD: No tenant filtering (data leakage!)
def get_queryset(self):
    return Customer.objects.all()  # Returns ALL tenants' data!

# ✅ GOOD: Always filter by tenant
def get_queryset(self):
    if not self.request.tenant:
        return Customer.objects.none()
    return Customer.objects.filter(tenant=self.request.tenant)
```

### 2. Assuming django-tenants is Active

```python
# ❌ BAD: Trying to use schema context
from django_tenants.utils import schema_context

with schema_context('tenant_schema'):
    # This will fail - no schema-based tenancy!
    Customer.objects.all()

# ✅ GOOD: Use tenant foreign key filtering
customers = Customer.objects.filter(tenant=my_tenant)
```

### 3. Not Handling Missing Tenant

```python
# ❌ BAD: Assuming tenant always exists
def my_view(request):
    tenant_name = request.tenant.name  # May error if None!
    
# ✅ GOOD: Check tenant exists
def my_view(request):
    if not request.tenant:
        return Response(
            {"error": "Tenant context required"},
            status=400
        )
    tenant_name = request.tenant.name
```

### 4. Using Wrong Migration Commands

```bash
# ❌ BAD: Non-existent commands
python manage.py migrate_schemas --shared
python manage.py ensure_public_tenant

# ✅ GOOD: Standard Django migrations
python manage.py migrate --noinput
```

---

## Troubleshooting

### Issue: "No tenant could be resolved for request"

**Symptoms:**
- Empty querysets in views
- `request.tenant is None`

**Causes:**
1. No `TenantDomain` for request domain
2. User not linked to any tenant
3. No `X-Tenant-ID` header in API request
4. Subdomain doesn't match tenant slug

**Solutions:**

1. **Create TenantDomain:**
```python
from apps.tenants.models import Tenant, TenantDomain

tenant = Tenant.objects.get(slug='my-tenant')
TenantDomain.objects.create(
    domain='uat.meatscentral.com',
    tenant=tenant,
    is_primary=True
)
```

2. **Link user to tenant:**
```python
from apps.tenants.models import TenantUser

TenantUser.objects.create(
    user=my_user,
    tenant=my_tenant,
    role='member',
    is_active=True
)
```

3. **Add header to API requests:**
```bash
curl -H "X-Tenant-ID: <tenant-uuid>" \
  https://api.example.com/api/v1/customers/
```

### Issue: HTTP 500 on Health Check

**Symptoms:**
- `/api/v1/health/` returns 500 during deployment
- "relation does not exist" errors

**Causes:**
1. Migrations not applied
2. Middleware querying database before tables exist
3. Health check not bypassing tenant resolution

**Solutions:**

1. **Run migrations first:**
```bash
python manage.py migrate --noinput
# Then start server
python manage.py runserver
```

2. **Verify bypass in middleware:**
```python
# In TenantMiddleware.__call__
if request.path.startswith('/api/v1/health/'):
    request.tenant = None
    return self.get_response(request)
```

3. **Check middleware order in settings:**
```python
MIDDLEWARE = [
    # ...
    'apps.tenants.middleware.TenantMiddleware',  # Should be after auth
    # ...
]
```

### Issue: "Command 'migrate_schemas' not found"

**Cause:** Trying to use django-tenants commands

**Solution:** Use standard Django migrations:
```bash
# ❌ WRONG
python manage.py migrate_schemas --shared

# ✅ CORRECT
python manage.py migrate --noinput
```

---

## References

### Code Locations

- **Middleware:** `backend/apps/tenants/middleware.py`
- **Models:** `backend/apps/tenants/models.py`
- **Management Commands:**
  - `backend/apps/core/management/commands/create_super_tenant.py`
  - `backend/apps/core/management/commands/create_guest_tenant.py`
- **Health Check:** `backend/projectmeats/health.py`
- **Settings:** `backend/projectmeats/settings/base.py`

### Documentation

- **Django Multi-Tenancy:** https://docs.djangoproject.com/en/stable/topics/db/multi-db/
- **Row-Level Security:** https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- **Deployment Fix:** `/workspaces/ProjectMeats/DEPLOYMENT_MULTI_TENANCY_FIX.md`

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-12-01 | Created comprehensive architecture guide | Copilot Agent |
| 2025-12-01 | Documented shared-schema vs django-tenants differences | Copilot Agent |

---

**Document Owner:** Development Team  
**Last Updated:** 2025-12-01  
**Next Review:** 2026-01-01
