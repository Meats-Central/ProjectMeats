# Production-to-UAT Database Sync Strategy

## Overview

This document describes the **Golden Standard** approach for refreshing UAT with production data while maintaining security, data integrity, and UAT seed data.

## Architecture

### Why GitHub Actions over DigitalOcean Tools?

**DigitalOcean's "Database Forking"** creates a 100% clone, which violates our security requirements:
- ❌ Includes all production passwords
- ❌ Includes superuser accounts
- ❌ Overwrites UAT seed data
- ❌ No granular filtering capability

**Our GitHub Actions Approach** provides:
- ✅ Row-level and table-level filtering
- ✅ Excludes sensitive auth data
- ✅ Preserves UAT seed data (test tenants)
- ✅ Automated scheduling (daily at midnight UTC)
- ✅ Follows existing security patterns (SSH tunnels, environment secrets)

## Sync Process

### 1. Tunnel Setup (Bastion Pattern)

```bash
# Production DB tunnel → localhost:5433
ssh -N -L 5433:$PROD_DB_HOST:5432 $SSH_USER@$SSH_HOST

# UAT DB tunnel → localhost:5434
ssh -N -L 5434:$UAT_DB_HOST:5432 $UAT_SSH_USER@$UAT_SSH_HOST
```

This uses the **proven SSH tunnel pattern** from `reusable-deploy.yml`.

### 2. Data Extraction (Production)

**Included Tables:**
- All business models: `apps_tenants_*`, `apps_suppliers_*`, `apps_plants_*`, `apps_customers_*`, etc.
- Tenant configuration: `apps_tenants_tenant`, `apps_tenants_tenantdomain`

**Excluded Tables:**
- `auth_user` - Production credentials stay in production
- `auth_permission` - System-managed
- `auth_group*` - System-managed
- `django_session` - Temporary data
- `authtoken_token` - Production API tokens
- `django_admin_log` - Audit trail (production-specific)
- `django_content_type` - System-managed
- `django_migrations` - System-managed

**Command:**
```bash
pg_dump \
  --no-owner \
  --no-privileges \
  --data-only \
  --exclude-table='auth_user' \
  --exclude-table='django_session' \
  --exclude-table='authtoken_token' \
  ...
```

### 3. Tenant Filtering

**Preserves UAT Seed Data:**
```bash
# Filter out test tenant rows (schema_name starting with 'test_')
grep -v "^INSERT INTO.*apps_tenants_tenant.*'test_" prod_data.sql > filtered_data.sql
```

This ensures:
- Production tenants are imported
- UAT test tenants (created by `seed_tenants` command) are preserved
- UAT can maintain its own test data independently

### 4. UAT Data Clearing (Selective)

**Strategy:**
- Delete business data for NON-test tenants
- Preserve test tenant data (schema_name starts with 'test_')
- Keep system tables untouched

**SQL Logic:**
```sql
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN (
    SELECT table_schema, table_name
    FROM information_schema.columns
    WHERE column_name = 'tenant_id'
      AND table_schema NOT IN ('pg_catalog', 'information_schema')
      AND table_name NOT LIKE 'auth_%'
  ) LOOP
    -- Delete only non-test tenant data
    EXECUTE format('DELETE FROM %I.%I WHERE tenant_id NOT IN 
      (SELECT id FROM apps_tenants_tenant WHERE schema_name LIKE ''test_%%'');', 
      r.table_schema, r.table_name);
  END LOOP;
END $$;
```

### 5. Data Import

Import filtered production data:
```bash
psql -h localhost -p 5434 -U $UAT_DB_USER -d $UAT_DB_NAME -f filtered_data.sql
```

### 6. Post-Restore Fixup (Critical)

**Problem:** Production data references production user IDs via foreign keys:
- `owner_id` → `auth_user.id`
- `created_by_id` → `auth_user.id`
- `updated_by_id` → `auth_user.id`

**Solution:** Remap all user references to the UAT superuser:
```sql
-- Get UAT superuser ID
SELECT id FROM auth_user WHERE is_superuser = true LIMIT 1;

-- Update all owner references
UPDATE apps_suppliers_supplier SET owner_id = $UAT_SUPERUSER_ID WHERE owner_id IS NOT NULL;
UPDATE apps_plants_plant SET owner_id = $UAT_SUPERUSER_ID WHERE owner_id IS NOT NULL;
UPDATE apps_customers_customer SET owner_id = $UAT_SUPERUSER_ID WHERE owner_id IS NOT NULL;

-- Update all created_by references
UPDATE apps_suppliers_supplier SET created_by_id = $UAT_SUPERUSER_ID WHERE created_by_id IS NOT NULL;
-- ... (repeat for all models with user foreign keys)
```

This ensures:
- No orphaned foreign key references
- UAT testers can access all imported data
- Database integrity is maintained

### 7. Validation

**Data Integrity Checks:**
```sql
-- Count total tenants
SELECT COUNT(*) FROM apps_tenants_tenant;

-- Verify test tenants preserved
SELECT COUNT(*) FROM apps_tenants_tenant WHERE schema_name LIKE 'test_%';

-- Check for orphaned references
SELECT COUNT(*) FROM apps_suppliers_supplier 
WHERE owner_id NOT IN (SELECT id FROM auth_user);
```

If validation fails, the workflow aborts and notifications are sent.

## Security Guarantees

### 1. No Production Credentials in UAT
- `auth_user` table is **never** copied
- UAT maintains its own separate user database
- Production passwords never leave production

### 2. No Production API Tokens
- `authtoken_token` table is excluded
- UAT has its own API token space

### 3. No Session Leakage
- `django_session` table is excluded
- No production session cookies in UAT

### 4. Secrets Never Logged
- All database passwords passed via `PGPASSWORD` environment variable
- SSH passwords passed via `SSHPASS` environment variable
- `set -euo pipefail` ensures errors stop execution immediately
- Temp files cleaned up in `always()` step

## UAT Seed Data Preservation

### How Test Tenants Are Protected

**UAT Seed Data Pattern:**
```python
# Created by management command: python manage.py seed_tenants
Tenant(schema_name='test_acme', name='Test Acme Corp')
Tenant(schema_name='test_global', name='Test Global Meats')
Tenant(schema_name='test_premium', name='Test Premium Foods')
```

**Protection Mechanism:**
1. Production dump is filtered to exclude rows with `schema_name LIKE 'test_%'`
2. UAT clearing step preserves all rows where `tenant_id IN (test tenants)`
3. Production import adds new tenants alongside test tenants

**Result:**
- UAT has production tenant data for realistic testing
- UAT also has test tenants with 3 sample rows per model for feature testing
- Testers can switch between real and test data

## Scheduling

### Automatic Daily Sync
```yaml
on:
  schedule:
    - cron: "0 0 * * *"  # Daily at midnight UTC
```

### Manual Trigger
```bash
gh workflow run db-sync-prod-to-uat.yml
```

### Post-Deployment Trigger (Optional)
Can be extended to run after production deployments:
```yaml
on:
  workflow_run:
    workflows: ["Deploy Production (Frontend + Backend via DOCR)"]
    types: [completed]
```

## Rollback Strategy

### Automatic Backup
Before every sync, UAT database is backed up:
```bash
pg_dump --format=custom > uat_backup_$(date +%Y%m%d_%H%M%S).dump
```

### Manual Restore
If sync fails or data is corrupted:
```bash
# Download backup from workflow artifacts
gh run download <run_id>

# Restore to UAT
pg_restore -h $UAT_DB_HOST -U $UAT_DB_USER -d $UAT_DB_NAME uat_backup_*.dump
```

## Required GitHub Secrets

### Production Environment (`production-backend`)
- `PROD_DB_HOST` - Private database host
- `PROD_DB_PORT` - Database port (default: 5432)
- `PROD_DB_USER` - Database username
- `PROD_DB_PASSWORD` - Database password
- `PROD_DB_NAME` - Database name
- `SSH_HOST` - Bastion host
- `SSH_USER` - Bastion username
- `SSH_PASSWORD` - Bastion password

### UAT Environment (`uat-backend`)
- `UAT_DB_HOST` - Private database host
- `UAT_DB_PORT` - Database port (default: 5432)
- `UAT_DB_USER` - Database username
- `UAT_DB_PASSWORD` - Database password
- `UAT_DB_NAME` - Database name
- `UAT_SSH_HOST` - Bastion host
- `UAT_SSH_USER` - Bastion username
- `UAT_SSH_PASSWORD` - Bastion password

**Note:** These follow the **Environment Manifest v5.1** pattern (no prefixes, environment-scoped).

## Monitoring & Alerts

### Success Indicators
- ✅ Workflow completes without errors
- ✅ Test tenant count > 0
- ✅ No orphaned foreign key references
- ✅ Total tenant count = test tenants + production tenants

### Failure Scenarios
1. **SSH tunnel fails** - Check bastion host connectivity
2. **pg_dump fails** - Check production database connectivity/credentials
3. **Import fails** - Check UAT database connectivity/credentials
4. **Validation fails** - Check data integrity (orphaned references)

### Notification Strategy
```yaml
- name: Send notification on failure
  if: failure()
  run: |
    # TODO: Integrate with Slack/email
    echo "Sync failed: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
```

## Performance Considerations

### Sync Duration
- **Expected:** 10-15 minutes for typical dataset
- **Timeout:** 30 minutes (workflow-level)

### Database Impact
- **Production:** Read-only operations (minimal impact)
- **UAT:** Exclusive lock during clearing/import (scheduled during low-usage hours)

### Network Transfer
- All data flows through GitHub Actions runner (encrypted tunnels)
- No direct database-to-database connection required
- Bandwidth: ~100MB-500MB depending on dataset size

## Maintenance

### Adding New Tables
When new business models are added:
1. No workflow changes needed (auto-included if they have `tenant_id`)
2. Add user foreign key fixup if model has `owner_id`, `created_by_id`, etc.

### Excluding Sensitive Tables
To exclude a new table:
```yaml
--exclude-table='new_sensitive_table'
```

### Adjusting Schedule
To change sync frequency, update cron expression:
```yaml
- cron: "0 */6 * * *"  # Every 6 hours
- cron: "0 0 * * 0"    # Weekly on Sunday
```

## Comparison with Alternatives

### ✅ Our Approach (GitHub Actions + Selective Sync)
- Granular table/row filtering
- Preserves UAT seed data
- No production credentials leaked
- Automated and auditable
- Uses proven SSH tunnel pattern

### ❌ DigitalOcean Database Forking
- 100% clone (no filtering)
- Overwrites all UAT data
- Includes production credentials
- Manual process
- Creates new database cluster (cost)

### ❌ Manual SQL Scripts
- Error-prone
- Not automated
- No version control
- Hard to audit
- Inconsistent execution

### ❌ Django Fixtures
- Doesn't scale with large datasets
- Requires manual export/import
- Version control conflicts
- Hard to maintain

## Testing the Workflow

### Before Production Use

1. **Test on Development:**
```bash
# Modify workflow to sync dev→uat first
sed -i 's/production-backend/dev-backend/g' .github/workflows/db-sync-prod-to-uat.yml
gh workflow run db-sync-prod-to-uat.yml
```

2. **Validate Seed Data Preservation:**
```sql
-- Before sync
SELECT COUNT(*) FROM apps_tenants_tenant WHERE schema_name LIKE 'test_%';

-- After sync
SELECT COUNT(*) FROM apps_tenants_tenant WHERE schema_name LIKE 'test_%';
-- Should be SAME
```

3. **Check Foreign Key Integrity:**
```sql
SELECT COUNT(*) FROM apps_suppliers_supplier WHERE owner_id NOT IN (SELECT id FROM auth_user);
-- Should be 0
```

4. **Verify Authentication Isolation:**
```sql
-- Try logging in with production credentials in UAT
-- Should FAIL (credentials not copied)
```

## Related Documentation

- `/config/env.manifest.json` - Secret naming and environment configuration
- `/docs/CONFIGURATION_AND_SECRETS.md` - Secret management guide
- `/.github/workflows/reusable-deploy.yml` - SSH tunnel pattern reference
- `/docs/GOLDEN_STANDARD_ACHIEVEMENT.md` - CI/CD architecture overview

## Change Log

| Date       | Version | Changes                                      |
|------------|---------|----------------------------------------------|
| 2026-01-04 | 1.0     | Initial implementation of daily sync         |

## Support

For issues or questions:
1. Check workflow logs: `gh run view --log`
2. Review secret configuration: `python config/manage_env.py audit`
3. Validate database connectivity: Test SSH tunnels manually
4. Contact DevOps team with workflow run ID

---

**Document Status:** ✅ Active  
**Last Updated:** January 4, 2026  
**Maintained By:** Infrastructure Team
