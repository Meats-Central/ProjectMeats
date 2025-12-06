# Migration Duplicate Column Fix - Complete Summary

## Issue
PR #1141 deployment failed with:
```
psycopg.errors.DuplicateColumn: column "schema_name" of relation "tenants_tenant" already exists
```

**Workflow Run**: https://github.com/Meats-Central/ProjectMeats/actions/runs/19989312532/job/57327746512

## Root Cause

### Timeline of Events
1. **Migration 0004** (Nov 3, 2025): Added `schema_name` column using idempotent SQL
2. **Migration 0011_tenant_schema_name** (Dec 6, 2025): Tried to add same column using Django's `AddField` - **FAILED**
3. **Migration 0011_remove_schema_based_models**: Used `DeleteModel` operations - **FAILED on fresh databases**

## Solution

Converted both migrations to use idempotent SQL operations:

### File 1: `0011_tenant_schema_name.py`
- ✅ Changed from `AddField` to `RunSQL` with `IF NOT EXISTS`
- ✅ Added `UNIQUE` constraint at column level
- ✅ Consistent index naming with migration 0004

### File 2: `0011_remove_schema_based_models.py`
- ✅ Used `SeparateDatabaseAndState` for proper state management
- ✅ Database: Idempotent `DROP TABLE IF EXISTS`
- ✅ State: `DeleteModel` for Django tracking

## Testing Results

✅ Fresh database: All migrations 0001-0012 succeed  
✅ Existing column: Migration succeeds when schema_name already exists  
✅ Idempotency: Multiple runs succeed without errors  
✅ UNIQUE constraint: Properly enforced  
✅ Security scan: 0 alerts  

## Files Changed
- `backend/apps/tenants/migrations/0011_tenant_schema_name.py`
- `backend/apps/tenants/migrations/0011_remove_schema_based_models.py`

**Status:** ✅ READY FOR MERGE
