# Development vs Production Deployment Comparison

## Current Status (2025-11-29 21:59 UTC)

### Development Branch - FAILING ❌
- **Last 4 runs**: All failed with same error
- **Failed runs**: #254, #253, #252, #251
- **Error**: `django.db.utils.ProgrammingError: relation "tenants_ten_domain_6df599_idx" does not exist`
- **Failure point**: Migration step (pre-deployment)
- **Last successful**: Run #250 (18:45 UTC) - 3 hours ago

### Production Branch (main) - WORKING ✅
- **Last run**: #83 (21:48 UTC) - 11 minutes ago
- **Status**: SUCCESS
- **Deployment**: Completed successfully
- **Migration**: Only has migration 0005 (no 0006)

## Root Cause Analysis

### What Changed Between Working and Broken State

**Working State (Run #250 - 18:45 UTC)**
- Had migrations 0001-0005
- All migrations idempotent and safe
- Deployment completed successfully

**Broken State (Runs #251-254)**
- New migration 0006 added between 18:45 and 21:41 UTC
- Migration 0006 contains `RenameIndex` operations
- Assumes specific index names exist (they don't)
- Fails immediately on migration step

### Why Production Works But Development Doesn't

**Production (main branch)**
```
backend/apps/tenants/migrations/
├── 0001_initial.py
├── 0002_alter_tenant_contact_phone_tenantinvitation_and_more.py
├── 0003_tenant_logo.py
├── 0004_add_schema_name_and_domain_model.py
└── 0005_client_domain.py  ← Stops here, works fine
```

**Development**
```
backend/apps/tenants/migrations/
├── 0001_initial.py
├── 0002_alter_tenant_contact_phone_tenantinvitation_and_more.py
├── 0003_tenant_logo.py
├── 0004_add_schema_name_and_domain_model.py
├── 0005_client_domain.py
└── 0006_rename_tenants_ten_domain_6df599_idx...py  ← NEW, causes failure
```

## The Fix - What Was Applied

### Before (Non-Idempotent - Causes Failure)
```python
operations = [
    migrations.RenameIndex(
        model_name="tenantdomain",
        new_name="tenants_ten_domain_f3abe6_idx",
        old_name="tenants_ten_domain_6df599_idx",  # ❌ Assumes this exists
    ),
]
```

**Problem**: If `tenants_ten_domain_6df599_idx` doesn't exist → **FAILURE**

### After (Idempotent - Works Everywhere)
```python
def rename_index_if_exists(apps, schema_editor):
    with connection.cursor() as cursor:
        cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = 'tenants_ten_domain_6df599_idx'
                ) THEN
                    ALTER INDEX tenants_ten_domain_6df599_idx 
                    RENAME TO tenants_ten_domain_f3abe6_idx;
                END IF;
            END $$;
        """)

operations = [
    migrations.RunPython(rename_index_if_exists, ...),
]
```

**Solution**: Checks if index exists first → **SUCCESS** regardless of state

## Why This Pattern From Production Is Correct

Looking at the successful production deployment, migration 0005 uses this pattern:

```python
# From 0005_client_domain.py (works in production)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS tenants_client (...)
""")

cursor.execute("""
    CREATE INDEX IF NOT EXISTS tenants_client_schema_name_idx (...)
""")
```

**Key insight**: Production uses `IF NOT EXISTS` everywhere, making migrations idempotent.

## Expected Results After Fix

### Next Development Deployment (After Fix)
1. Migration 0006 will run
2. Will check if old index names exist
3. If they exist → rename them
4. If they don't exist → skip silently (no error)
5. Deployment continues successfully ✅

### UAT/Production Promotion (Future)
- When this fix is promoted through UAT → main
- Will work correctly in all environments
- No manual intervention needed

## Timeline of Events

| Time (UTC) | Event | Status |
|------------|-------|--------|
| 18:45 | Dev run #250 | ✅ SUCCESS (last good) |
| 18:45-21:41 | Merges add migration 0006 | - |
| 21:41 | Dev run #251 | ❌ FAIL (first bad) |
| 21:43 | Dev run #252 | ❌ FAIL |
| 21:46 | Dev run #253 | ❌ FAIL |
| 21:51 | Dev run #254 | ❌ FAIL (most recent) |
| 21:40-21:48 | Prod runs #82, #83 | ✅ SUCCESS (both) |
| 21:59 | Fix applied | 🔧 Waiting for next run |

## Verification Checklist

- [x] Identified root cause (migration 0006 not idempotent)
- [x] Compared working production with failing development
- [x] Found exact point of divergence (migration 0006)
- [x] Applied idempotent pattern from successful migrations
- [x] Created comprehensive documentation
- [x] Committed fix to development branch
- [ ] Next dev deployment validates fix
- [ ] Promote to UAT after successful dev run
- [ ] Promote to production after successful UAT run

## Key Takeaways

1. **Always make migrations idempotent** - Use IF EXISTS patterns
2. **Production had the right pattern** - Migration 0005 was our template
3. **Development diverged recently** - Within last 3 hours
4. **Fix follows existing successful patterns** - Not inventing new approaches
5. **Safe for all environments** - Works whether indexes exist or not

## Files Modified in Fix

- `backend/apps/tenants/migrations/0006_rename_tenants_ten_domain_6df599_idx_tenants_ten_domain_f3abe6_idx_and_more.py`
- `MIGRATION_FIX_0006_IDEMPOTENCY.md` (this documentation)
- `DEPLOYMENT_COMPARISON_SUMMARY.md` (comparison report)

## Next Steps

1. Push fix to development branch
2. Monitor next development deployment
3. If successful, promote to UAT
4. After UAT validation, promote to production
5. Update deployment workflow documentation with this lesson learned
