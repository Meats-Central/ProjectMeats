# Django-Tenants Alignment Documentation

## Overview

This document explains how ProjectMeats' multi-tenancy implementation aligns with [django-tenants](https://django-tenants.readthedocs.io/) concepts while maintaining its custom shared-schema approach.

## Background

ProjectMeats initially listed `django-tenants==3.5.0` in `requirements.txt` but implemented a **custom shared-schema multi-tenancy** approach instead of using django-tenants' PostgreSQL schema-based isolation. This decision was documented in `MULTI_TENANCY_ENHANCEMENT_SUMMARY.md`:

> **Key Decision**: We chose to **enhance** the existing shared-schema multi-tenancy approach rather than switch to django-tenants, as the current implementation is working well and is simpler to maintain.

## Architecture Comparison

### django-tenants (Schema-Based)
- **Approach**: Separate PostgreSQL schema per tenant
- **Database Engine**: `django_tenants.postgresql_backend`
- **Data Isolation**: Physical schema separation
- **Models**: Inherit from `TenantMixin` and `DomainMixin`
- **Routing**: Domain-based with middleware
- **Apps Configuration**: `SHARED_APPS` and `TENANT_APPS`

### ProjectMeats (Shared-Schema)
- **Approach**: Single schema with tenant_id filtering
- **Database Engine**: Standard `django.db.backends.postgresql`
- **Data Isolation**: Application-level filtering via middleware
- **Models**: Custom Tenant and Domain models with compatible fields
- **Routing**: X-Tenant-ID header, domain, subdomain, or user default
- **Apps Configuration**: Standard `INSTALLED_APPS`

## Alignment Implementation

To provide compatibility with django-tenants concepts while maintaining the custom approach, the following changes were made:

### 1. Tenant Model Enhancement

**Added `schema_name` field:**
```python
class Tenant(models.Model):
    schema_name = models.CharField(
        max_length=63,
        unique=True,
        null=True,
        blank=True,
        help_text="Database schema name (for future django-tenants compatibility)",
        db_index=True,
    )
```

**Features:**
- Auto-generated from slug (e.g., "test-company" → "test_company")
- Unique constraint for future schema-based migration
- Nullable for backward compatibility
- Follows PostgreSQL identifier length limits (63 chars)

### 2. Domain Model

**Created new Domain model following django-tenants DomainMixin pattern:**
```python
class Domain(models.Model):
    domain = models.CharField(max_length=253, unique=True, db_index=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    is_primary = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Features:**
- Maps domain names to tenants
- Supports multiple domains per tenant
- Primary domain designation
- Compatible with django-tenants Domain model structure

### 3. Middleware Enhancement

**Updated tenant resolution to support domain-based routing:**

**Resolution Order:**
1. **X-Tenant-ID Header** (for API requests)
2. **Full Domain Match** (via Domain model) - **NEW**
3. **Subdomain Match** (via Tenant.slug)
4. **User Default Tenant** (fallback)

**Example:**
```python
# Domain-based routing (NEW)
# Request to: tenant.example.com
# Matches: Domain.objects.get(domain="tenant.example.com")

# Subdomain-based routing (existing)
# Request to: acme.meatscentral.com
# Matches: Tenant.objects.get(slug="acme")
```

## Migration Path

If ProjectMeats decides to migrate to full django-tenants in the future:

### Prerequisites
1. All tenants have `schema_name` populated
2. Domain entries created for all tenants
3. Database backed up

### Steps
1. **Update Settings:**
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django_tenants.postgresql_backend',  # Changed
           # ... other settings
       }
   }
   
   DATABASE_ROUTERS = ('django_tenants.routers.TenantSyncRouter',)
   
   SHARED_APPS = (
       'django_tenants',
       'apps.tenants',
       'django.contrib.admin',
       # ... core apps
   )
   
   TENANT_APPS = (
       'apps.suppliers',
       'apps.customers',
       # ... tenant-specific apps
   )
   
   TENANT_MODEL = "tenants.Tenant"
   TENANT_DOMAIN_MODEL = "tenants.Domain"
   ```

2. **Update Tenant Model:**
   ```python
   from django_tenants.models import TenantMixin
   
   class Tenant(TenantMixin):
       # Existing fields...
       # TenantMixin provides schema_name and other required fields
   ```

3. **Update Domain Model:**
   ```python
   from django_tenants.models import DomainMixin
   
   class Domain(DomainMixin):
       pass  # DomainMixin provides all required fields
   ```

4. **Update Middleware:**
   ```python
   MIDDLEWARE = [
       'django_tenants.middleware.main.TenantMainMiddleware',  # First!
       # ... other middleware
   ]
   ```

5. **Run Migrations:**
   ```bash
   python manage.py migrate_schemas --shared
   python manage.py migrate_schemas
   ```

## Benefits of Current Alignment

### Immediate Benefits
1. **Domain-Based Routing**: Can route requests based on full domain names
2. **Future Compatibility**: Fields and models compatible with django-tenants
3. **Clear Migration Path**: Easy transition to schema-based if needed
4. **Enhanced Flexibility**: Supports both domain and subdomain routing

### Maintaining Custom Approach Benefits
1. **Simplicity**: No schema management overhead
2. **Performance**: Single schema is faster for small-to-medium deployments
3. **Easier Backups**: Single database dump for all tenants
4. **Development**: Easier local development without schema complexity

## Usage Examples

### Creating a Tenant with Domain

```python
from apps.tenants.models import Tenant, Domain

# Create tenant (schema_name auto-generated from slug)
tenant = Tenant.objects.create(
    name="Acme Corp",
    slug="acme-corp",
    contact_email="admin@acme.com"
)
# tenant.schema_name will be "acme_corp"

# Add domains
Domain.objects.create(
    domain="acme.example.com",
    tenant=tenant,
    is_primary=True
)

Domain.objects.create(
    domain="acme-corp.example.com",
    tenant=tenant,
    is_primary=False
)
```

### Accessing via Domain

```bash
# Middleware will resolve tenant from domain
curl https://acme.example.com/api/v1/suppliers/
# → Returns suppliers for Acme Corp tenant

# Or via X-Tenant-ID header
curl -H "X-Tenant-ID: <tenant-uuid>" https://api.example.com/api/v1/suppliers/
# → Returns suppliers for specified tenant
```

### Managing Domains in Admin

1. Navigate to Django Admin
2. Go to **Tenants → Domains**
3. Add new domain mapping
4. Set `is_primary` for the main domain

## Testing

Run tests to verify alignment:

```bash
cd backend
python manage.py test apps.tenants

# Should show:
# - TenantModelTests (3 tests)
# - TenantUserModelTests (3 tests)
# - TenantAPITests (7 tests)
# - DomainModelTests (4 tests)
# - TenantSchemaNameTests (3 tests)
# Total: 20 tests passing
```

## References

- [django-tenants Documentation](https://django-tenants.readthedocs.io/)
- [django-tenants Installation Guide](https://django-tenants.readthedocs.io/en/latest/install.html)
- [ProjectMeats Multi-Tenancy Guide](docs/multi-tenancy.md)
- [Multi-Tenancy Enhancement Summary](MULTI_TENANCY_ENHANCEMENT_SUMMARY.md)

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-09 | Custom shared-schema approach | Simpler to maintain, adequate for current scale |
| 2025-11 | Add django-tenants-compatible fields | Enable future migration path without immediate complexity |

## Future Considerations

### When to Migrate to Full django-tenants

Consider migrating to schema-based approach when:
1. **Scale**: 100+ tenants with high data volume per tenant
2. **Isolation**: Stricter data isolation requirements
3. **Performance**: Query performance degradation due to tenant filtering
4. **Compliance**: Regulatory requirements for physical data separation

### When to Keep Custom Approach

Keep current approach when:
1. **Scale**: < 100 tenants
2. **Simplicity**: Team prefers simpler architecture
3. **Performance**: Adequate performance with current filtering
4. **Development**: Want faster development cycles

## Conclusion

ProjectMeats now has a hybrid approach that:
- Maintains the working custom shared-schema implementation
- Adds django-tenants-compatible models and fields
- Enables domain-based routing
- Provides a clear migration path for future growth

This alignment gives the best of both worlds: current simplicity with future flexibility.
