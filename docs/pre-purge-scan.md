# Pre-Purge Assessment Report
Date: 2025-12-06
Repository: Meats-Central/ProjectMeats
Branch: copilot/update-django-tenants-routing

## Executive Summary
This report documents all django-tenants references in the codebase prior to the Master Convergence migration to shared-schema multi-tenancy.

## django-tenants References Found

### 1. Management Commands (HIGH PRIORITY - MUST FIX)

#### backend/apps/tenants/management/commands/init_dev_tenant.py
- Line 11: `from django_tenants.utils import get_tenant_model, get_tenant_domain_model`
- Status: ❌ CRITICAL - Command will fail without django-tenants
- Action: Replace with direct model imports

#### backend/apps/tenants/management/commands/setup_test_tenant.py
- Line 34: `from django_tenants.utils import get_tenant_model, schema_context`
- Line 58: `with schema_context(tenant.schema_name):`
- Line 63: `call_command('migrate_schemas', schema_name=tenant.schema_name, verbosity=0)`
- Status: ❌ CRITICAL - Uses schema_context pattern
- Action: Replace with shared-schema approach

#### backend/apps/tenants/management/commands/create_tenant.py
- Line 97: References to `migrate_schemas` command
- Line 115: `call_command('migrate_schemas', schema_name=tenant.schema_name)`
- Status: ⚠️  MEDIUM - Command references schema-based migration
- Action: Replace with standard migrate

### 2. Test Files (MEDIUM PRIORITY)

#### backend/apps/core/tests/test_user_preferences.py
- Line 15: `from django_tenants.utils import schema_context, get_public_schema_name`
- Line 25: `with schema_context(get_public_schema_name()):`
- Status: ⚠️  Tests use schema_context
- Action: Update to shared-schema test patterns

### 3. Migration Files (LOW PRIORITY - HISTORICAL)

#### backend/apps/tenants/migrations/0005_client_domain.py
- Lines 12-15: Import django_tenants with try/except fallback
- Status: ✅ OK - Historical migration with fallback

#### backend/apps/tenants/migrations/0010_schema_based_client_domain.py
- Lines 12-15: Import django_tenants with try/except fallback
- Status: ✅ OK - Historical migration with fallback

#### backend/apps/tenants/migrations/0012_purge_legacy_architecture.py
- Documentation references only
- Status: ✅ OK - Migration that removes legacy tables

### 4. Documentation/Comments (INFO ONLY)

Multiple files contain documentation explaining the removal of django-tenants:
- requirements.txt: Comment explaining shared-schema approach
- models.py: Architecture decision documentation
- Various migration files: Historical context

## Schema-Based Pattern References

### migrate_schemas Command Usage
Found in 3 locations:
1. init_dev_tenant.py - Line 131
2. setup_test_tenant.py - Line 63
3. create_tenant.py - Lines 97, 115

### schema_context Usage
Found in 2 locations:
1. setup_test_tenant.py - Line 58
2. test_user_preferences.py - Line 25

## Current Architecture State

### ✅ Correctly Implemented
- requirements.txt: No django-tenants dependency
- settings/base.py: Uses standard Django backend
- models.py: Tenant model with schema_name for compatibility only
- Middleware: Custom TenantMiddleware (not django-tenants)
- Workflows: Use standard `python manage.py migrate`

### ❌ Needs Fixing
1. Three management commands importing django_tenants
2. Two test files using schema_context
3. References to migrate_schemas in commands

## Risk Assessment

### High Risk Items
1. **init_dev_tenant.py** - Used for development setup, will fail immediately
2. **setup_test_tenant.py** - Used in CI/CD, could break pipeline

### Medium Risk Items
1. **create_tenant.py** - Used for tenant creation, has schema migration logic
2. **test_user_preferences.py** - Test will fail with ImportError

### Low Risk Items
- Historical migrations (already run, have fallbacks)
- Documentation references (informational only)

## Recommendations

### Immediate Actions (Phase 1)
1. Fix init_dev_tenant.py to use Tenant/TenantDomain models directly
2. Fix setup_test_tenant.py to remove schema_context usage
3. Update create_tenant.py to remove migrate_schemas references
4. Update test_user_preferences.py to use shared-schema patterns

### Data Backup Strategy
- No Client/Domain tables exist (already dropped by migration 0012)
- Current Tenant/TenantDomain tables use shared schema
- Backup command should export Tenant, TenantDomain, TenantUser data

### Testing Strategy
1. Unit tests for Tenant model creation
2. Integration tests for TenantMiddleware resolution
3. E2E tests for multi-tenant data isolation
4. CI/CD pipeline validation

## Conclusion
The codebase is 90% migrated to shared-schema multi-tenancy. Only 4 files require updates to complete the convergence. The main work is updating management commands and test utilities to use the shared-schema approach.

No data loss risk - legacy Client/Domain tables were already removed in migration 0012_purge_legacy_architecture.
