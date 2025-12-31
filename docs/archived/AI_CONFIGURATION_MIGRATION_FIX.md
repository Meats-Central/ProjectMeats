# AIConfiguration Migration Fix - Summary

## Problem
Deployment failed with error:
```
psycopg.errors.UndefinedTable: relation "ai_assistant_aiconfiguration" does not exist
```

The issue was that:
1. **Migration 0001_initial.py** created the `AIConfiguration` table WITHOUT the `tenant` field
2. **Migration 0002_aiconfiguration_tenant.py** attempted to ADD the `tenant_id` column to an existing table
3. However, the table was missing in production (likely dropped or never created)

## Root Cause
The migration sequence assumed the table existed from 0001, but in reality:
- 0001 created a partial table (no tenant field)
- 0002 tried to add tenant to a non-existent table

## Solution
Modified `0002_aiconfiguration_tenant.py` to be **idempotent** and handle multiple scenarios:

### Scenario 1: Table Does NOT Exist (Fresh Deployment)
```sql
CREATE TABLE ai_assistant_configurations (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants_tenant(id),
    name VARCHAR(100) NOT NULL UNIQUE,
    provider VARCHAR(50) NOT NULL DEFAULT 'openai',
    model_name VARCHAR(100) NOT NULL DEFAULT 'gpt-4o-mini',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

### Scenario 2: Table Exists WITHOUT tenant_id
- If tenants exist: Add `tenant_id` as NOT NULL with first tenant as default
- If no tenants: Add `tenant_id` as nullable (test environment)

### Scenario 3: Table Exists WITH tenant_id
- Skip column creation (no-op)

## Migration File
**File**: `backend/tenant_apps/ai_assistant/migrations/0002_aiconfiguration_tenant.py`

**Key Features**:
1. ✅ Checks if table exists before creating
2. ✅ Checks if `tenant_id` column exists before adding
3. ✅ Handles both production (tenants exist) and test (no tenants) scenarios
4. ✅ Creates index for tenant lookups
5. ✅ Uses raw SQL for full control
6. ✅ Idempotent - safe to run multiple times

## Testing

### Test Results
```bash
cd /workspaces/ProjectMeats
python test_ai_migration.py
```

**Output**:
- ✅ Migration applied successfully
- ✅ Table `ai_assistant_configurations` exists with 8 columns
- ✅ `tenant_id` column added (nullable in test, NOT NULL in production)
- ✅ Index `ai_assistant_configurations_tenant_id_idx` created
- ✅ Django system check passes with no issues

### Verification Commands
```bash
# Check migration status
cd backend
python manage.py showmigrations ai_assistant

# Apply migrations
python manage.py migrate ai_assistant

# Verify no pending migrations
python manage.py makemigrations --check

# Check for Django issues
python manage.py check
```

## Production Deployment

### Migration Command
```bash
# Standard Django migration (NOT django-tenants)
python manage.py migrate --fake-initial --noinput
```

**Important**: Use `--fake-initial` for idempotency in production deployments.

### Expected Behavior
- If table exists: Adds `tenant_id` column only if missing
- If table missing: Creates complete table with all fields
- No data loss in either scenario

## Related Files
- `backend/tenant_apps/ai_assistant/models.py` - Model definition
- `backend/tenant_apps/ai_assistant/migrations/0001_initial.py` - Initial migration (without tenant)
- `backend/tenant_apps/ai_assistant/migrations/0002_aiconfiguration_tenant.py` - Fixed tenant migration
- `test_ai_migration.py` - Validation test script

## Architectural Notes

### Multi-Tenancy Pattern (CRITICAL)
**ProjectMeats uses SHARED SCHEMA multi-tenancy:**
- ❌ NEVER use `django-tenants` or schema-based isolation
- ✅ ALWAYS use `tenant` ForeignKey on business models
- ✅ ALWAYS filter by `tenant=request.tenant` in ViewSets
- ✅ ALWAYS use standard `python manage.py migrate` (NOT `migrate_schemas`)

### Why This Matters
The `AIConfiguration` model inherits the shared-schema pattern:
```python
class AIConfiguration(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    # ... other fields
```

All data lives in the `public` PostgreSQL schema, isolated by `tenant_id` foreign keys.

## Cleanup
After successful deployment, remove the test script:
```bash
rm /workspaces/ProjectMeats/test_ai_migration.py
```

## Next Steps
1. ✅ Migration fixed and tested
2. ⏳ Deploy to production with `migrate --fake-initial`
3. ⏳ Verify table exists in production database
4. ⏳ Monitor deployment logs for any migration errors
5. ⏳ Create AIConfiguration instances for each tenant

## Lessons Learned
1. **Always create tables with tenant field from the start** - Don't split into multiple migrations
2. **Use idempotent migrations** - Check existence before creating/altering
3. **Test both scenarios** - Table exists vs. doesn't exist
4. **Use raw SQL for complex migrations** - More control than Django's migration framework
5. **Follow shared-schema patterns** - Never deviate to schema-based isolation
