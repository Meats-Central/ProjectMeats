# Migration 0006 Idempotency Fix

## Problem

Development deployment was failing with:
```
django.db.utils.ProgrammingError: relation "tenants_ten_domain_6df599_idx" does not exist
```

## Root Cause

1. **Main branch (Production)**: Has migration `0005_client_domain.py` which creates indexes with specific names
2. **Development branch**: Added `0006_rename_...` migration that tried to rename indexes
3. **Issue**: The migration assumed the old index names existed, but:
   - Migration 0005 creates indexes with different names in its `CREATE INDEX IF NOT EXISTS` statements
   - When 0006 ran, it tried to rename indexes that didn't exist
   - This caused the deployment to fail

## Timeline

- **Earlier today**: Development deployment was working (run #250 - SUCCESS)
- **3 hours ago**: Multiple merges added migration 0006 to development branch
- **Recent failures**: Runs #251, #252, #253, #254 all failed with same error
- **Production**: Last deployment (run #83) was successful - uses only 0005 migration

## Solution

Modified migration `0006_rename_tenants_ten_domain_6df599_idx_tenants_ten_domain_f3abe6_idx_and_more.py` to be **idempotent**:

### Before (Non-Idempotent)
```python
operations = [
    migrations.RenameIndex(
        model_name="tenantdomain",
        new_name="tenants_ten_domain_f3abe6_idx",
        old_name="tenants_ten_domain_6df599_idx",  # Fails if doesn't exist
    ),
    ...
]
```

### After (Idempotent)
```python
def rename_index_if_exists(apps, schema_editor):
    """Rename indexes only if they exist (idempotent)"""
    with connection.cursor() as cursor:
        cursor.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND indexname = 'tenants_ten_domain_6df599_idx'
                ) THEN
                    ALTER INDEX tenants_ten_domain_6df599_idx 
                    RENAME TO tenants_ten_domain_f3abe6_idx;
                END IF;
            END $$;
        """)
        # ... (same for second index)

operations = [
    migrations.RunPython(
        rename_index_if_exists,
        reverse_code=reverse_rename_index,
    ),
    ...
]
```

## Key Changes

1. **Check before rename**: Uses PostgreSQL `DO $$ ... END $$` block with `IF EXISTS`
2. **No failure on missing index**: If old index name doesn't exist, operation is skipped
3. **Reversible**: Includes proper reverse operation for migration rollback
4. **Safe for all environments**:
   - Fresh databases: Indexes won't exist, operation skipped gracefully
   - Existing databases with old names: Indexes renamed successfully
   - Production databases: Will work when promoted from UAT

## Testing Strategy

1. **Local Testing**: Run `python manage.py migrate` in fresh database
2. **CI/CD**: Next deployment to development will validate the fix
3. **UAT**: Will be promoted after successful development deployment
4. **Production**: Will receive fix through standard promotion workflow

## Prevention

This follows the pattern from migration `0005_client_domain.py` which uses:
- `CREATE TABLE IF NOT EXISTS`
- `CREATE INDEX IF NOT EXISTS`
- Conditional constraint additions

All future migrations should follow this idempotent pattern to prevent similar issues.

## Related Files

- `backend/apps/tenants/migrations/0006_rename_tenants_ten_domain_6df599_idx_tenants_ten_domain_f3abe6_idx_and_more.py` (FIXED)
- `backend/apps/tenants/migrations/0005_client_domain.py` (reference for idempotent pattern)

## Workflow Runs

- **Failed runs**: #19789778260, #19789734194, #19789710466, #19789686100
- **Last successful dev**: #19787862625 (before migration 0006 was added)
- **Last successful prod**: #19789752198 (still on migration 0005 only)
