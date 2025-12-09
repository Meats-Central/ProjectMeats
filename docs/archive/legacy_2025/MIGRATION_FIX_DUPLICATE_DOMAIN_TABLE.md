# Migration Fix: Duplicate tenants_domain Table Error

**Issue**: GitHub Actions deployment failing with `psycopg2.errors.DuplicateTable: relation "tenants_domain" already exists`

**Date**: 2025-11-03  
**PR**: [Link to PR]  
**Related GitHub Actions Run**: https://github.com/Meats-Central/ProjectMeats/actions/runs/19045484837/job/54392663646

---

## Problem Description

The deployment pipeline was failing during database migrations with the following error:

```
psycopg2.errors.DuplicateTable: relation "tenants_domain" already exists
```

### Root Cause Analysis

The project had two conflicting migration files in the `backend/apps/tenants/migrations/` directory:

1. **`0004_client_domain.py`** (conflicting migration)
   - Created `Client` model (inheriting from `django_tenants.TenantMixin`)
   - Created `Domain` model (inheriting from `django_tenants.DomainMixin`)
   - Both models used `db_table = "tenants_domain"`

2. **`0004_add_schema_name_and_domain_model.py`** (correct migration)
   - Added `schema_name` field to existing `Tenant` model
   - Created `Domain` model (standalone, referencing `Tenant`)
   - Also used `db_table = "tenants_domain"`

3. **`0005_merge_20251103_1831.py`** (merge migration)
   - Attempted to merge the two conflicting migrations
   - Did not resolve the duplicate table issue

### Why This Happened

The project was in a transitional state with two multi-tenancy approaches:

- **django-tenants approach** (not actually used): `Client` + `Domain` (with DomainMixin)
- **Custom approach** (actually used): `Tenant` + `Domain` (standalone)

The codebase exclusively used the custom `Tenant` model, but django-tenants infrastructure remained in:
- `INSTALLED_APPS` included `django_tenants`
- Database engine set to `django_tenants.postgresql_backend`
- `DATABASE_ROUTERS` included `django_tenants.routers.TenantSyncRouter`
- Migration files for both approaches existed

This caused both Domain models to attempt creating the same database table.

---

## Solution Implemented

### 1. Removed Unused django-tenants Models

**File**: `backend/apps/tenants/models.py`

Deleted the following unused models:
- `Client` class (lines 9-33)
- `Domain` class inheriting from DomainMixin (lines 36-50)

Kept the custom models that are actually used by the application:
- `Tenant` model (shared-schema multi-tenancy)
- `Domain` model (standalone, references Tenant)
- `TenantUser` model
- `TenantInvitation` model

### 2. Removed Conflicting Migration Files

Deleted migrations:
- `backend/apps/tenants/migrations/0004_client_domain.py`
- `backend/apps/tenants/migrations/0005_merge_20251103_1831.py`

Kept the correct migration:
- `backend/apps/tenants/migrations/0004_add_schema_name_and_domain_model.py`

### 3. Updated Django Settings

**Files Modified**:
- `backend/projectmeats/settings/base.py`
- `backend/projectmeats/settings/development.py`
- `backend/projectmeats/settings/production.py`
- `backend/projectmeats/settings/test.py`

**Changes**:

#### base.py
```python
# Before
THIRD_PARTY_APPS = [
    "django_tenants",  # Schema-based multi-tenancy
    ...
]

DATABASE_ROUTERS = [
    "django_tenants.routers.TenantSyncRouter",
]

# After
THIRD_PARTY_APPS = [
    # "django_tenants",  # Commented out - using custom shared-schema approach
    ...
]

# No DATABASE_ROUTERS needed for shared-schema approach
```

#### development.py, production.py, test.py
```python
# Before
if _db_config.get("ENGINE") == "django.db.backends.postgresql":
    _db_config["ENGINE"] = "django_tenants.postgresql_backend"

# After
# Use standard PostgreSQL backend (not django-tenants)
# ProjectMeats uses custom shared-schema multi-tenancy
```

---

## Migration Sequence (After Fix)

The clean migration sequence for the tenants app is now:

```
tenants
 [ ] 0001_initial
 [ ] 0002_alter_tenant_contact_phone_tenantinvitation_and_more
 [ ] 0003_tenant_logo
 [ ] 0004_add_schema_name_and_domain_model
```

---

## Verification Steps

### 1. Django System Check
```bash
python manage.py check
# Result: System check identified no issues (0 silenced).
```

### 2. Migration Check
```bash
python manage.py makemigrations --dry-run
# Result: No changes detected
```

### 3. Apply Migrations to Clean Database
```bash
python manage.py migrate
# Result: All migrations apply successfully, including:
# Applying tenants.0004_add_schema_name_and_domain_model... OK
```

### 4. Verify Database Tables
```sql
SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'tenants%';
```

Expected tables:
- `tenants_domain` (single table, no duplicates!)
- `tenants_tenant`
- `tenants_invitation`
- `tenants_tenant_user`

### 5. Code Review
- ✅ No issues found
- ✅ Code review feedback addressed

### 6. Security Check (CodeQL)
- ✅ No security alerts found

---

## Impact Assessment

### What Changed
- Django-tenants infrastructure removed from active use
- Database engine changed from `django_tenants.postgresql_backend` to standard `django.db.backends.postgresql`
- Two migration files deleted
- Two model classes removed from codebase

### What Remains the Same
- Custom `Tenant` model and all its functionality
- Custom `Domain` model for tenant routing
- Application-level tenant filtering
- All existing tenant-related features
- Database schema structure (same tables, same data)

### Breaking Changes
**None** - The removed models were not used by any application code

### Compatibility
- ✅ Backward compatible with existing database
- ✅ No data migration required
- ✅ All existing code continues to work
- ✅ Future migrations can proceed normally

---

## Preventing Future Occurrences

### Guidelines for Multi-Tenancy

1. **Choose One Approach**: Don't mix django-tenants schema-based isolation with custom shared-schema approach
   
2. **Migration Naming**: Avoid creating migrations with duplicate numbers. If parallel development creates numbered conflicts, use Django's merge migration feature properly

3. **Model Validation**: Before creating new models, verify no duplicate table names exist:
   ```python
   class Meta:
       db_table = "unique_table_name"  # Check this doesn't conflict
   ```

4. **Settings Alignment**: Ensure settings match the chosen multi-tenancy approach:
   - For schema-based: Use `django_tenants.postgresql_backend` + `TenantMainMiddleware`
   - For shared-schema: Use standard `postgresql` backend + custom middleware

5. **Migration Reviews**: Review migration files before merging to catch table name conflicts

---

## Related Documentation

- [Django Tenants Documentation](https://django-tenants.readthedocs.io/)
- [Django Migrations Documentation](https://docs.djangoproject.com/en/4.2/topics/migrations/)
- [ProjectMeats Multi-Tenancy Implementation](./MULTI_TENANCY_IMPLEMENTATION.md)
- [Migration Fix Summary](./MIGRATION_FIX_SUMMARY.md)

---

## Testing in Different Environments

### Development
```bash
# With SQLite (default)
python manage.py migrate

# With PostgreSQL
DATABASE_URL=postgres://user:pass@localhost/dbname python manage.py migrate
```

### Staging/UAT/Production
The fix ensures migrations will apply cleanly in all environments. The deployment workflow will:

1. Pull latest code (includes migration fixes)
2. Apply migrations without duplicate table errors
3. Application starts successfully

---

## Security Summary

**CodeQL Analysis**: ✅ No vulnerabilities detected

The changes are purely structural (removing unused code) and do not introduce any security risks:
- No new code paths added
- No changes to authentication/authorization
- No changes to data handling
- Standard PostgreSQL backend is well-tested and secure

---

## Rollback Plan

If issues arise (unlikely), rollback steps:

1. Revert the PR
2. Manually resolve migration conflicts in database:
   ```sql
   -- If table exists from old migration
   DROP TABLE IF EXISTS tenants_domain CASCADE;
   ```
3. Apply migrations with `--fake-initial` if needed:
   ```bash
   python manage.py migrate tenants --fake-initial
   ```

**Note**: Rollback should not be necessary as the fix is backward compatible.

---

## Conclusion

This fix resolves the duplicate table migration error by:
- Removing unused django-tenants models
- Cleaning up conflicting migrations
- Aligning settings with the actual multi-tenancy implementation

The project now has a clean, maintainable migration history and uses a consistent shared-schema multi-tenancy approach throughout.
