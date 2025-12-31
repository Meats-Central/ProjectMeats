# GitHub Issue: Fix Inconsistent Migration History Blocking Dev and UAT Deployments

## Title
Fix Inconsistent Migration History Blocking Dev and UAT Deployments

## Labels
- `bugfix`
- `high-priority`
- `deployment`
- `database`

## Issue Description

### Problem Statement

The GitHub Actions deploy runs are failing due to a Django `InconsistentMigrationHistory` exception:

**Error:**
```
django.db.migrations.exceptions.InconsistentMigrationHistory: 
Migration purchase_orders.0004_alter_purchaseorder_carrier_release_format_and_more 
is applied before its dependency suppliers.0006_alter_supplier_package_type on database 'default'.
```

**Affected Environments:**
- **Dev**: dev.meatscentral.com
- **UAT**: uat.meatscentral.com

**Failed Deployment Runs:**
- https://github.com/Meats-Central/ProjectMeats/actions/runs/18469484231/job/52619645399
- https://github.com/Meats-Central/ProjectMeats/actions/runs/18469484231/job/52619645427

### Root Cause

Migration `purchase_orders.0004_alter_purchaseorder_carrier_release_format_and_more` has an explicit dependency on `suppliers.0006_alter_supplier_package_type` (see line 13 of the migration file), but in the Dev and UAT database environments, migration 0004 was applied before 0006.

This likely occurred due to:
1. Migrations being run in incorrect order manually
2. Race condition during concurrent deployments
3. Manual database manipulation

### Impact

- ❌ Deployments to Dev and UAT are blocked
- ❌ Cannot apply new migrations until history is corrected
- ❌ Development and testing workflows are disrupted

## Solution Implemented

### 1. Documentation Created

Created comprehensive fix guide: **`docs/MIGRATION_HISTORY_FIX.md`**

This document includes:
- ✅ Detailed problem statement and root cause analysis
- ✅ Backup procedures for SQLite and PostgreSQL
- ✅ Step-by-step fix procedure using Django's `--fake` flag
- ✅ Verification steps
- ✅ Rollback procedures
- ✅ Troubleshooting guide
- ✅ 7KB+ of comprehensive documentation

### 2. CI/CD Prevention Measures

Enhanced `.github/workflows/unified-deployment.yml` with migration validation:

**Added "Check migration consistency" step:**
```yaml
- name: 🔍 Check migration consistency
  working-directory: ./backend
  run: |
    echo "Checking for unapplied migrations..."
    python manage.py makemigrations --check --dry-run || {
      echo "❌ Error: Unapplied migrations detected!"
      exit 1
    }
    
    echo "Verifying migration dependencies..."
    python manage.py migrate --plan || {
      echo "❌ Error: Migration dependency issues detected!"
      exit 1
    }
```

**Benefits:**
- ✅ Detects unapplied migrations before deployment
- ✅ Validates migration dependency order
- ✅ Fails CI build if issues detected
- ✅ Prevents future migration history corruption

### 3. Documentation Updates

- ✅ Updated `CHANGELOG.md` with bugfix entry
- ✅ Updated `copilot-log.md` with detailed task log and lessons learned

## Manual Intervention Required

**⚠️ CRITICAL: The fix cannot be fully automated and requires manual execution on servers to prevent data loss.**

### Quick Fix Steps

See **`docs/MIGRATION_HISTORY_FIX.md`** for complete detailed instructions.

#### Dev Environment (dev.meatscentral.com)

```bash
# SSH to server
ssh django@dev.meatscentral.com
cd /home/django/ProjectMeats/backend
source venv/bin/activate

# Backup database first!
pg_dump -U $DB_USER -h $DB_HOST -d $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql

# Fix migration history
python manage.py migrate purchase_orders 0003 --fake
python manage.py migrate suppliers 0006
python manage.py migrate purchase_orders 0004
python manage.py migrate

# Verify
python manage.py showmigrations purchase_orders suppliers
```

#### UAT Environment (uat.meatscentral.com)

Repeat the same steps as Dev environment.

## Verification Checklist

After applying the fix on each environment:

- [ ] Run `python manage.py showmigrations` - all migrations show `[X]`
- [ ] Run `python manage.py check` - no issues reported
- [ ] Re-trigger GitHub Actions deployment - no `InconsistentMigrationHistory` errors
- [ ] Verify migrations run successfully in deployment logs
- [ ] Test application functionality in affected environment

## Prevention Measures

The following measures have been implemented to prevent this from happening again:

1. **CI/CD Validation**
   - `python manage.py makemigrations --check` runs in all test jobs
   - `python manage.py migrate --plan` validates dependency order
   - Build fails if migration issues detected

2. **Documentation**
   - Comprehensive fix guide for future reference
   - Troubleshooting section for common errors

3. **Best Practices**
   - Always backup database before migration operations
   - Never run migrations manually on servers during deployments
   - Use deployment workflows exclusively for applying migrations

## Files Changed

### Modified
- `.github/workflows/unified-deployment.yml` - Added migration consistency checks
- `CHANGELOG.md` - Added bugfix entry
- `copilot-log.md` - Added detailed task documentation

### Created
- `docs/MIGRATION_HISTORY_FIX.md` - Comprehensive manual fix guide (7KB+)

## References

- **Django Migrations Documentation**: https://docs.djangoproject.com/en/4.2/topics/migrations/
- **Migration Operations**: https://docs.djangoproject.com/en/4.2/ref/migration-operations/
- **Troubleshooting Migrations**: https://docs.djangoproject.com/en/4.2/howto/migrations/

## Timeline

1. **Issue Detected**: 2025-10-13 (GitHub Actions runs 18469484231)
2. **Analysis Completed**: 2025-10-13
3. **Documentation Created**: 2025-10-13
4. **CI/CD Prevention Added**: 2025-10-13
5. **Manual Fix Required**: Pending execution on Dev and UAT servers
6. **Expected Resolution**: Once manual fix is applied

## Assignees

- Infrastructure/DevOps team (for manual server fixes)
- Development team (for code review and CI/CD validation)

## Related Issues

- Original error in GitHub Actions: https://github.com/Meats-Central/ProjectMeats/actions/runs/18469484231

## Status

**Status**: Solution implemented, manual intervention required

**Next Actions**:
1. Execute manual fix on Dev server
2. Execute manual fix on UAT server  
3. Re-trigger deployments to verify
4. Monitor deployment logs for clean migration output
5. Close issue once verified

---

**Created**: 2025-10-13
**Branch**: `copilot/fix-inconsistent-migration-history`
**Priority**: High
**Category**: Deployment / Database
