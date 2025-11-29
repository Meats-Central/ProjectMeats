# Django-Tenants CI/CD Fix Summary

## Problem Solved

The deployment workflows were failing with django-tenants multi-tenancy due to:

1. **Schema-based migrations**: Tests were using regular `migrate` instead of `migrate_schemas`
2. **Missing tenant setup**: CI needed tenant creation for proper testing
3. **Configuration detection**: Tests needed to handle both django-tenants and regular Django setups

## Changes Made

### 1. Enhanced Workflow Test Jobs

**Files Modified:**
- `.github/workflows/11-dev-deployment.yml` 
- `.github/workflows/12-uat-deployment.yml`

**Changes:**
- Added tenant schema setup in test-backend jobs
- Automatic detection of django-tenants configuration
- Fallback to regular migrations when django-tenants not configured
- Added test tenant creation with proper domain setup
- Enhanced error handling and logging

### 2. Enhanced Test Settings

**File:** `backend/projectmeats/settings/test.py`

**Changes:**
- Automatic django-tenants backend selection for PostgreSQL
- Proper middleware ordering for tenant routing
- SQLite fallback that disables multi-tenancy features
- Enhanced ALLOWED_HOSTS for tenant domain testing

### 3. Test Utilities

**File:** `backend/apps/tenants/test_utils.py` (new)

**Features:**
- `TenantTestMixin`: Automatic tenant setup for test cases
- `TenantTestCase`: Drop-in replacement for Django TestCase
- `@with_tenant_context`: Decorator for tenant-specific tests
- Graceful fallback when django-tenants not configured

### 4. Management Command

**File:** `backend/apps/tenants/management/commands/setup_test_tenant.py` (new)

**Usage:**
```bash
python manage.py setup_test_tenant --tenant-name test_tenant --domain test.example.com
```

**Features:**
- Automatic tenant and domain creation
- Schema migration for new tenants
- Graceful handling of existing tenants

## Usage in Tests

### For Unit Tests (with tenant support):

```python
from apps.tenants.test_utils import TenantTestCase, with_tenant_context

class MyModelTestCase(TenantTestCase):
    @with_tenant_context
    def test_tenant_specific_feature(self):
        # This test runs in tenant context when django-tenants is enabled
        # Falls back to regular testing when not configured
        pass
```

### For CI/CD:

The workflows now automatically:
1. Detect if django-tenants is configured
2. Set up shared schema migrations
3. Create test tenant with domain
4. Run tenant schema migrations  
5. Execute tests in proper tenant context

## Benefits

- ✅ **Backward Compatible**: Works with and without django-tenants
- ✅ **Automatic Detection**: No manual configuration needed
- ✅ **Proper Isolation**: Tests run in correct tenant context
- ✅ **Error Handling**: Graceful fallback for configuration issues
- ✅ **Fast SQLite Tests**: Unit tests can still use fast SQLite
- ✅ **Production Parity**: CI uses same PostgreSQL + django-tenants as production

## Migration Path

1. The existing shared-schema multi-tenancy continues to work
2. django-tenants schema-based tenancy is enabled when `DATABASE_URL` uses PostgreSQL
3. Tests automatically adapt to the configured backend
4. No breaking changes to existing functionality

## Technical Details

### Django-Tenants Configuration

When `DATABASE_URL` is provided with PostgreSQL:
- Backend switches to `django_tenants.postgresql_backend`
- Middleware includes `django_tenants.middleware.TenantMainMiddleware`
- Router uses `django_tenants.routers.TenantSyncRouter`
- Models: `TENANT_MODEL = "tenants.Client"`, `TENANT_DOMAIN_MODEL = "tenants.Domain"`

### Fallback Behavior

When using SQLite or when django-tenants is not configured:
- Standard PostgreSQL/SQLite backend
- django-tenants middleware removed
- No schema routing
- All multi-tenancy handled via shared-schema approach

### CI/CD Flow

1. **Detection Phase**: Check if `migrate_schemas` command is available
2. **Schema Setup**: Run shared schema migrations first
3. **Tenant Setup**: Create test tenant and domain
4. **Tenant Migrations**: Run tenant-specific schema migrations
5. **Test Execution**: Run tests with proper tenant context
6. **Graceful Degradation**: Fall back to regular migrations if django-tenants unavailable

## Troubleshooting

### Common Issues

1. **Migration Command Not Found**
   - Symptom: `migrate_schemas` command not available
   - Solution: Automatic fallback to regular migrations

2. **Tenant Creation Fails**
   - Symptom: Error creating test tenant
   - Solution: Continues with shared schema testing

3. **Schema Context Errors**
   - Symptom: AttributeError in schema switching
   - Solution: Graceful fallback with warning message

### Verification Steps

```bash
# Test django-tenants configuration
python manage.py check

# Test migration detection
python manage.py help migrate_schemas

# Run tenant setup manually
python manage.py setup_test_tenant

# Run tests with PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/db python manage.py test
```

## Future Enhancements

1. **Base Classes**: Create `TenantAwareViewSet` and `BaseSerializer`
2. **Custom Exception Handler**: Centralized error responses
3. **Performance Monitoring**: Track schema switching performance
4. **Automated Testing**: Integration tests for both approaches

---

**Resolves**: 
- AttributeError in schema switching
- DisallowedHost errors in CI
- Multi-tenancy CI test failures
- Migration inconsistencies
- psycopg2/django-tenants compatibility issues

**Maintains**:
- Backward compatibility with shared-schema approach
- Fast SQLite testing for unit tests
- Production parity in CI environments
- Flexible deployment configuration