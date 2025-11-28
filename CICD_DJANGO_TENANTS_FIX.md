# CI/CD Django-Tenants Configuration Fix

**Date:** 2025-01-28  
**Branch:** `fix/cicd-django-tenants-test-config`  
**Related PRs:** #526 (Middleware fix)

## Problem Statement

After PR #526 removed django-tenants middleware from base.py to fix local development, CI/CD tests continued failing with "relation does not exist" errors. This revealed a deeper architectural inconsistency in how test and production environments handled multi-tenancy.

## Root Cause Analysis

### The Architectural Mismatch

1. **Production/Development (base.py):**
   - Uses **custom shared-schema multi-tenancy**
   - No django-tenants in INSTALLED_APPS
   - No django-tenants middleware
   - Custom `apps.tenants.middleware.TenantMiddleware`
   - All tenants share same schema with `tenant_id` filtering

2. **CI/CD Testing (test.py - OLD):**
   - **Added django-tenants dynamically** for PostgreSQL tests
   - Used `django_tenants.postgresql_backend`
   - Added `TenantMainMiddleware`
   - Used schema-based tenant isolation
   - Required `migrate_schemas` commands

3. **Workflow Commands:**
   - Called `migrate_schemas --shared`
   - Called `setup_test_tenant`
   - Called `migrate_schemas --tenant`
   - Expected schema-based isolation

### Why PR #526 Fixed Local But Broke CI/CD

- **Local dev:** Uses base.py directly → middleware removal worked
- **CI/CD:** test.py tried to re-add django-tenants → failed because:
  - Middleware list from base.py was already modified
  - Django-tenants models (Client, Domain) don't match custom approach
  - Schema-based commands incompatible with shared-schema architecture

## Solution

Align the test environment with the production architecture by removing all django-tenants dependencies from CI/CD.

### Changes Made

#### 1. backend/projectmeats/settings/test.py

**BEFORE:**
```python
# Use django-tenants PostgreSQL backend
if _db_config.get("ENGINE") == "django.db.backends.postgresql":
    _db_config["ENGINE"] = "django_tenants.postgresql_backend"

# Add django-tenants to INSTALLED_APPS
INSTALLED_APPS = ["django_tenants"] + [...]

# Add django-tenants middleware
MIDDLEWARE = ["django_tenants.middleware.TenantMainMiddleware"] + [...]

# Configure django-tenants routing
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)
TENANT_MODEL = "tenants.Client"
TENANT_DOMAIN_MODEL = "tenants.Domain"
```

**AFTER:**
```python
# Use STANDARD PostgreSQL backend (not django-tenants)
if _db_config.get("ENGINE") == "django.db.backends.postgresql":
    pass  # Keep django.db.backends.postgresql

# Remove django-tenants from INSTALLED_APPS
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django_tenants"]

# Remove django-tenants middleware
MIDDLEWARE = [m for m in MIDDLEWARE if "django_tenants" not in m]

# No schema-based routing
DATABASE_ROUTERS = []
```

#### 2. .github/workflows/11-dev-deployment.yml

**Test Backend Job - BEFORE:**
```yaml
- name: Run django-tenants shared migrations (idempotent)
  run: |
    python manage.py migrate_schemas --shared --noinput || true

- name: Create test tenant (idempotent)
  run: |
    python manage.py setup_test_tenant --tenant-name test_tenant --domain test.example.com || true

- name: Run tenant-specific migrations (idempotent)
  run: |
    python manage.py migrate_schemas --tenant test_tenant --noinput || true
```

**AFTER:**
```yaml
- name: Apply database migrations
  run: |
    python manage.py migrate --noinput
```

**Deploy Backend Job - BEFORE:**
```bash
if python manage.py help migrate_schemas >/dev/null 2>&1; then
  python manage.py migrate_schemas --shared --noinput
  python manage.py ensure_public_tenant --domain=localhost
  python manage.py migrate_schemas --noinput
else
  python manage.py migrate --noinput
fi
```

**AFTER:**
```bash
python manage.py migrate --noinput
```

## Benefits

1. **Consistency:** Test environment now matches production architecture
2. **Simplicity:** No more dual-tenancy approach confusion
3. **Reliability:** Standard Django migrations are well-tested
4. **Maintainability:** Single approach across all environments
5. **Performance:** No schema-switching overhead in tests

## Testing Strategy

The custom shared-schema multi-tenancy is tested through:

1. **Unit Tests:** Test tenant filtering logic in models
2. **Middleware Tests:** Test `TenantMiddleware` functionality
3. **Integration Tests:** Test multi-tenant data isolation
4. **API Tests:** Test tenant context in API calls

No django-tenants-specific testing needed.

## Migration Path

### For Existing Deployments

If any environment is currently using django-tenants schema-based isolation:

1. **DO NOT** apply this fix directly
2. **FIRST** migrate data from schema-based to shared-schema approach
3. **THEN** apply these configuration changes

### For New Deployments

These changes are safe and should be applied immediately.

## Verification

After merging, verify:

1. ✅ CI/CD tests pass (test-backend job)
2. ✅ Migrations run successfully
3. ✅ No "relation does not exist" errors
4. ✅ No django-tenants import errors
5. ✅ Deployment succeeds without schema commands

## Related Documentation

- `DJANGO_TENANTS_ALIGNMENT.md` - Original multi-tenancy architecture
- `MULTI_TENANCY_IMPLEMENTATION.md` - Custom shared-schema approach
- `TENANT_ACCESS_CONTROL.md` - Tenant isolation strategy
- `BACKEND_TESTING_GUIDE.md` - Testing strategy

## Conclusion

This fix resolves the architectural inconsistency between development/production and CI/CD testing environments. By removing django-tenants from the test configuration, we ensure all environments use the same custom shared-schema multi-tenancy approach, improving reliability and maintainability.
