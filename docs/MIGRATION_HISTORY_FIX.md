# Migration History Fix Guide

## Problem Statement

The GitHub Actions deploy runs failed due to a Django `InconsistentMigrationHistory` exception:

```
Migration purchase_orders.0004_alter_purchaseorder_carrier_release_format_and_more 
is applied before its dependency suppliers.0006_alter_supplier_package_type on database 'default'.
```

This affects:
- **Dev environment**: dev.meatscentral.com
- **UAT environment**: uat.meatscentral.com

## Root Cause

Migration `purchase_orders.0004_alter_purchaseorder_carrier_release_format_and_more` has a dependency on `suppliers.0006_alter_supplier_package_type` (line 13 of the migration file), but in the Dev and UAT databases, migration 0004 was applied before 0006.

This likely occurred due to:
1. Migrations being run in incorrect order manually
2. Race condition during deployment
3. Database state being manually manipulated

## Solution Overview

The solution involves manually resetting the migration history on affected environments to match the correct dependency order. This is done using Django's `--fake` option to manipulate the migration history without actually running SQL operations.

## Prerequisites

Before proceeding:
1. ✅ Backup the databases (see Backup Procedure below)
2. ✅ Ensure no deployments are running
3. ✅ Verify you have SSH access to the servers
4. ✅ Confirm you have Django management permissions

## Backup Procedure

### For Dev Environment (dev.meatscentral.com)

```bash
# SSH to the dev server
ssh django@dev.meatscentral.com

# Navigate to project directory
cd /home/django/ProjectMeats/backend

# Activate virtual environment
source venv/bin/activate

# Backup the database
# For SQLite
cp db.sqlite3 db.sqlite3.backup_$(date +%Y%m%d_%H%M%S)

# For PostgreSQL
pg_dump -U $DB_USER -h $DB_HOST -d $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql
```

### For UAT Environment (uat.meatscentral.com)

```bash
# SSH to the UAT server
ssh django@uat.meatscentral.com

# Navigate to project directory
cd /home/django/ProjectMeats/backend

# Activate virtual environment
source venv/bin/activate

# Backup the database (typically PostgreSQL for UAT)
pg_dump -U $DB_USER -h $DB_HOST -d $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Fix Procedure

### Step 1: Fix Dev Environment

```bash
# SSH to dev server
ssh django@dev.meatscentral.com

# Navigate to project directory
cd /home/django/ProjectMeats/backend

# Activate virtual environment
source venv/bin/activate

# Step 1.1: Roll back purchase_orders migration (fake)
# This marks migration 0004 as unapplied without running SQL
python manage.py migrate purchase_orders 0003 --fake

# Step 1.2: Apply suppliers migration 0006
# This marks migration 0006 as applied (likely already is, but ensures it)
python manage.py migrate suppliers 0006

# Step 1.3: Re-apply purchase_orders migration 0004
# This marks migration 0004 as applied (should already be applied in DB)
python manage.py migrate purchase_orders 0004

# Step 1.4: Ensure all migrations are consistent
python manage.py migrate

# Step 1.5: Verify migration history
python manage.py showmigrations purchase_orders suppliers
```

**Expected Output:**
```
purchase_orders
 [X] 0001_initial
 [X] 0002_purchaseorder_tenant
 [X] 0003_purchaseorder_carrier_and_more
 [X] 0004_alter_purchaseorder_carrier_release_format_and_more
suppliers
 [X] 0001_initial
 [X] 0002_supplier_accounting_line_of_credit_and_more
 [X] 0003_supplier_tenant
 [X] 0004_supplier_account_line_of_credit_and_more
 [X] 0005_add_defaults_for_postgres_compatibility
 [X] 0006_alter_supplier_package_type
```

### Step 2: Fix UAT Environment

Repeat the exact same steps for UAT:

```bash
# SSH to UAT server
ssh django@uat.meatscentral.com

# Navigate to project directory
cd /home/django/ProjectMeats/backend

# Activate virtual environment
source venv/bin/activate

# Apply the same fix sequence
python manage.py migrate purchase_orders 0003 --fake
python manage.py migrate suppliers 0006
python manage.py migrate purchase_orders 0004
python manage.py migrate

# Verify
python manage.py showmigrations purchase_orders suppliers
```

## Verification Steps

After applying the fix on each environment:

### 1. Check Migration History
```bash
python manage.py showmigrations
```
Should show all migrations as `[X]` applied with no warnings.

### 2. Run Django Check
```bash
python manage.py check
```
Should return: `System check identified no issues (0 silenced).`

### 3. Test Deployment
Re-trigger the GitHub Actions deployment workflow and verify:
- No `InconsistentMigrationHistory` errors
- Migrations run successfully
- Application starts without errors

### 4. Verify Database Integrity
```bash
# Check that tables exist and have correct structure
python manage.py dbshell
```

```sql
-- Verify purchase_orders tables exist
SELECT COUNT(*) FROM purchase_orders_purchaseorder;
SELECT COUNT(*) FROM purchase_orders_carrierpurchaseorder;
SELECT COUNT(*) FROM purchase_orders_coldstorageentry;

-- Verify suppliers table exists
SELECT COUNT(*) FROM suppliers_supplier;
```

## Rollback Procedure

If something goes wrong, restore from backup:

### For SQLite
```bash
cp db.sqlite3.backup_YYYYMMDD_HHMMSS db.sqlite3
```

### For PostgreSQL
```bash
# Drop and recreate database (BE CAREFUL!)
dropdb $DB_NAME
createdb $DB_NAME
psql $DB_NAME < backup_YYYYMMDD_HHMMSS.sql
```

## Prevention Measures

To prevent this from happening again, we've added:

1. **CI/CD Check**: `python manage.py makemigrations --check` in `.github/workflows/unified-deployment.yml`
2. **Migration Order Validation**: Pre-deployment step to verify migration dependencies
3. **Documentation**: This guide for future reference

## Troubleshooting

### Error: "Migration X is applied before its dependency Y"
This is the original error. Follow the fix procedure above.

### Error: "No such migration: purchase_orders.0003"
The migration file is missing. Ensure code is up to date:
```bash
git fetch origin development
git checkout development
git reset --hard origin/development
```

### Error: "Table already exists"
The `--fake` flag should prevent this. If it occurs:
1. Verify you're using `--fake` flag
2. Check that migration is actually in the database: `SELECT * FROM django_migrations WHERE app='purchase_orders';`

### Error: "Migration is unapplied but table exists"
This means database state is inconsistent. Use `--fake` to mark migration as applied:
```bash
python manage.py migrate purchase_orders 0004 --fake
```

## Additional Resources

- [Django Migrations Documentation](https://docs.djangoproject.com/en/4.2/topics/migrations/)
- [Django Migration Operations](https://docs.djangoproject.com/en/4.2/ref/migration-operations/)
- [Troubleshooting Django Migrations](https://docs.djangoproject.com/en/4.2/howto/migrations/)

## Contact

If you encounter issues not covered in this guide:
1. Check GitHub Actions logs: https://github.com/Meats-Central/ProjectMeats/actions
2. Review error logs on the server: `/home/django/ProjectMeats/backend/logs/`
3. Contact the development team

---

**Last Updated**: 2025-10-13
**Author**: GitHub Copilot
**Status**: Active - Manual intervention required on Dev and UAT servers
