# 🚨 URGENT: Migration State Fix Required

## Problem
The database has `tenant_id` columns that were created by failed migration attempts, but Django's migration history doesn't reflect this. This causes:
- `DuplicateColumn` errors (trying to add columns that exist)
- `FieldDoesNotExist` errors (trying to create indexes before models are loaded)

## Solution
Mark the problematic migrations as "applied" without running them (`--fake`), then proceed with normal migrations.

## Step-by-Step Fix

### Option 1: Using GitHub Actions (Recommended)

Run these commands via the **Ops - Run Management Command** workflow:

1. **Fake each tenant app migration 0002:**
   ```bash
   # Run each of these as separate workflow executions:
   migrate tenant_apps.carriers 0002 --fake
   migrate tenant_apps.accounts_receivables 0002 --fake
   migrate tenant_apps.ai_assistant 0002 --fake  
   migrate tenant_apps.bug_reports 0002 --fake
   migrate tenant_apps.contacts 0002 --fake
   migrate tenant_apps.customers 0002 --fake
   migrate tenant_apps.invoices 0002 --fake
   migrate tenant_apps.plants 0002 --fake
   migrate tenant_apps.products 0002 --fake
   migrate tenant_apps.purchase_orders 0002 --fake
   migrate tenant_apps.sales_orders 0002 --fake
   migrate tenant_apps.suppliers 0002 --fake
   ```

2. **Then run normal migrate:**
   ```bash
   migrate --noinput
   ```

### Option 2: Using the Fix Script (Alternative)

SSH into the server and run:
```bash
# Copy the script
scp scripts/fix_migration_state.sh user@server:/tmp/

# SSH in
ssh user@server

# Run it inside the backend container
docker exec pm-backend bash /tmp/fix_migration_state.sh
```

### Option 3: Manual SQL (Last Resort - NOT RECOMMENDED)

If all else fails, you can manually insert migration records:
```sql
INSERT INTO django_migrations (app, name, applied)
VALUES 
  ('carriers', '0002_carrier_tenant_and_more', NOW()),
  ('accounts_receivables', '0002_accountsreceivable_tenant_and_more', NOW())
  -- ... etc for each app
ON CONFLICT DO NOTHING;
```

## Verification

After fixing, verify with:
```bash
# Check which migrations are applied
python manage.py showmigrations

# All tenant_apps should show:
# [X] 0001_initial
# [X] 0002_<app>_tenant_and_more
```

## Why This Happened

1. Initial migration attempts created `tenant_id` columns in the database
2. Migration failures left Django's migration history incomplete  
3. Subsequent attempts saw existing columns and failed with DuplicateColumn
4. Our "idempotent" SQL fixes bypassed Django's migration tracking

## Prevention

Going forward:
- ✅ Always use `--fake-initial` for production migrations
- ✅ Test migrations on a copy of production data first
- ✅ Never manually ALTER tables outside of migrations
- ✅ If a migration fails halfway, use `--fake` to mark completed parts

## After the Fix

Once migration state is corrected:
1. The normal deployment pipeline will work
2. Future migrations will apply cleanly
3. The RLS (Row-Level Security) implementation will be complete

---

**Status**: Ready to execute
**Priority**: CRITICAL - Blocks deployment
**Estimated Time**: 5-10 minutes
