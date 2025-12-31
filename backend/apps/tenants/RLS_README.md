# PostgreSQL Row-Level Security (RLS) for Multi-Tenancy

## Overview

ProjectMeats implements **defense-in-depth** tenant isolation using both application-level filtering and database-level Row-Level Security (RLS).

## Architecture

### Dual-Layer Security

1. **Application Layer** (Primary):
   - `TenantMiddleware` sets `request.tenant` based on domain/header/user
   - ViewSets filter querysets with `.filter(tenant=request.tenant)`
   - Enforced in Django ORM queries

2. **Database Layer** (Defense-in-Depth):
   - PostgreSQL RLS policies enforce `tenant_id` filtering at the database level
   - Provides protection even if application-level filtering fails
   - Uses PostgreSQL session variable `app.current_tenant_id`

## How It Works

### 1. Middleware Sets Session Variable

When a request is processed, `TenantMiddleware` sets the PostgreSQL session variable:

```python
# In apps/tenants/middleware.py
with connection.cursor() as cursor:
    cursor.execute(
        "SET LOCAL app.current_tenant_id = %s",
        [str(tenant.id)]
    )
```

The `LOCAL` keyword ensures the variable is scoped to the current transaction.

### 2. RLS Policies Enforce Isolation

RLS policies are defined in migration `0002_enable_rls_policies.py`:

```sql
ALTER TABLE tenant_apps_supplier ENABLE ROW LEVEL SECURITY;

CREATE POLICY supplier_tenant_isolation ON tenant_apps_supplier
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

This policy ensures that:
- SELECT queries only return rows where `tenant_id` matches the session variable
- INSERT/UPDATE/DELETE operations are restricted to the current tenant's data

### 3. Protected Tables

RLS is enabled on all tenant-aware business models:
- `tenant_apps_supplier`
- `tenant_apps_customer`
- `tenant_apps_purchaseorder`
- `tenant_apps_salesorder`
- `tenant_apps_product`
- `tenant_apps_contact`
- `tenant_apps_invoice`
- `tenant_apps_carrier`
- `tenant_apps_plant`

## Benefits

### Security
- **Defense-in-Depth**: Database enforces isolation even if application code has bugs
- **Audit Trail**: PostgreSQL logs show RLS policy evaluations
- **Tamper-Proof**: Direct database access (e.g., via psql) respects RLS

### Compliance
- Meets data isolation requirements for multi-tenant SaaS
- Provides additional layer for SOC 2, GDPR compliance
- Database-level enforcement for sensitive data protection

## Implementation Details

### Session Variable Scope

The session variable is `LOCAL` to the transaction:
- Set at the beginning of each request
- Automatically cleared when transaction completes
- No risk of leaking between requests

### Superuser Bypass

PostgreSQL superusers bypass RLS policies by default. For testing RLS:

```sql
-- Disable superuser bypass
ALTER TABLE tenant_apps_supplier FORCE ROW LEVEL SECURITY;

-- Or test with non-superuser role
SET ROLE app_user;
```

### Performance Impact

RLS policies add minimal overhead:
- Policy evaluation is index-friendly (uses `tenant_id` foreign key index)
- PostgreSQL query planner optimizes RLS predicates
- Comparable performance to application-level filtering

## Testing RLS

### Verify RLS is Active

```sql
-- Check if RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename LIKE 'tenant_apps_%';

-- Check policies
SELECT schemaname, tablename, policyname, cmd, qual
FROM pg_policies
WHERE tablename LIKE 'tenant_apps_%';
```

### Test Isolation

```python
# In Django shell
from django.db import connection
from tenant_apps.suppliers.models import Supplier

# Set tenant context
with connection.cursor() as cursor:
    cursor.execute("SET LOCAL app.current_tenant_id = 'tenant-uuid-here'")

# Query will only return suppliers for that tenant
suppliers = Supplier.objects.all()
```

### Test Without Tenant Context

```python
# Without setting session variable, RLS will block access
from tenant_apps.suppliers.models import Supplier

# This will return empty (or raise error if FORCE RLS is enabled)
suppliers = Supplier.objects.all()
```

## Migration

### Applying RLS

The RLS migration is in `apps/tenants/migrations/0002_enable_rls_policies.py`.

Apply it with:

```bash
python manage.py migrate tenants
```

### Rollback

If needed, rollback RLS:

```bash
python manage.py migrate tenants 0001
```

This will:
- Drop all RLS policies
- Disable RLS on all tables
- Revert to application-level filtering only

## Troubleshooting

### Issue: Empty Querysets

**Symptom**: Queries return no results even though data exists.

**Cause**: Session variable not set or incorrect.

**Solution**: Ensure `TenantMiddleware` is properly configured and tenant is resolved.

```python
# Check middleware order in settings.py
MIDDLEWARE = [
    'apps.tenants.middleware.TenantMiddleware',  # Must be early
    # ... other middleware
]
```

### Issue: RLS Policy Violation

**Symptom**: `permission denied` errors when inserting/updating.

**Cause**: Trying to set `tenant_id` different from session variable.

**Solution**: Always use `request.tenant` when creating objects:

```python
# In ViewSet
def perform_create(self, serializer):
    serializer.save(tenant=self.request.tenant)
```

### Issue: Superuser Sees All Data

**Symptom**: Superuser queries bypass RLS.

**Cause**: PostgreSQL superusers bypass RLS by default.

**Solution**: For development/testing, use non-superuser roles or enable `FORCE ROW LEVEL SECURITY`.

## Best Practices

### 1. Always Set Tenant in ViewSets

```python
class SupplierViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Application-level filtering (primary)
        return Supplier.objects.filter(tenant=self.request.tenant)
    
    def perform_create(self, serializer):
        # Set tenant on creation
        serializer.save(tenant=self.request.tenant)
```

### 2. Test with RLS Enabled

Include RLS in your test suite:

```python
from django.test import TestCase
from django.db import connection

class SupplierRLSTestCase(TestCase):
    def test_tenant_isolation(self):
        # Set tenant context
        with connection.cursor() as cursor:
            cursor.execute(
                "SET LOCAL app.current_tenant_id = %s",
                [str(self.tenant1.id)]
            )
        
        # Should only see tenant1's suppliers
        suppliers = Supplier.objects.all()
        self.assertTrue(
            all(s.tenant_id == self.tenant1.id for s in suppliers)
        )
```

### 3. Monitor RLS in Production

Add logging to track RLS activity:

```python
# In middleware
logger.info(
    f"RLS: Set current_tenant_id={tenant.id} for request {request.path}"
)
```

## References

- [PostgreSQL RLS Documentation](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Django Database API](https://docs.djangoproject.com/en/4.2/topics/db/sql/)
- ProjectMeats Architecture Guide: `docs/ARCHITECTURE.md`
- Migration: `backend/apps/tenants/migrations/0002_enable_rls_policies.py`
