# Database Sync Workflow: Production to UAT

**Workflow:** `.github/workflows/db-sync-prod-to-uat.yml`  
**Schedule:** Daily at 00:00 UTC  
**Purpose:** Sync production business data to UAT environment for testing with realistic data

---

## Overview

This automated workflow copies production business data to the UAT environment while preserving:
- UAT system tables (auth, sessions, migrations)
- UAT test tenants (schema_name starting with 'test_')
- UAT superuser account

### Why This Exists

**Problem:** UAT needs realistic production data for testing, but:
- Manual database dumps are time-consuming
- Production contains sensitive data that needs filtering
- UAT test tenants must be preserved during sync

**Solution:** Automated daily sync that:
- Extracts only business data (excludes auth/system tables)
- Filters out test tenants from production
- Preserves UAT test tenants
- Fixes foreign key references to UAT users
- Validates data integrity after sync

---

## Architecture

### SSH Tunnel Strategy

The workflow uses **SSH tunnels** to securely connect to both databases:

```
GitHub Actions Runner (Ubuntu)
    ↓
    ├─ SSH Tunnel #1: localhost:5433 → Production DB (via SSH host)
    └─ SSH Tunnel #2: localhost:5434 → UAT DB (via SSH host)
```

**Why SSH Tunnels?**
- Production/UAT databases are not publicly accessible (security)
- SSH provides encrypted connection
- Port forwarding allows local PostgreSQL client to connect

### Retry Logic (NEW)

**Previous Behavior:**
- Fixed 5-second sleep
- Single connection attempt
- Failed if tunnel not ready immediately

**New Robust Logic:**
- 10 retry attempts with 3-second intervals (30 seconds total)
- Verbose SSH logging (`-v` flag) for debugging
- Process ID tracking for cleanup
- Graceful failure with clear error messages

**Implementation:**
```bash
for i in {1..10}; do
  if nc -zv localhost 5433 2>/dev/null; then
    echo "✅ Production tunnel established (attempt $i/10)"
    exit 0
  fi
  echo "⚠️  Tunnel not ready, retrying in 3 seconds... (attempt $i/10)"
  sleep 3
done

echo "❌ Production tunnel failed to establish after 10 attempts"
kill $SSH_PID 2>/dev/null || true
exit 1
```

---

## Workflow Steps

### 1. Setup Phase

**Install Dependencies:**
- `postgresql-client` - pg_dump, psql commands
- `sshpass` - Password-based SSH authentication
- `netcat` - Tunnel verification

**Setup SSH Tunnels:**
- Production DB: `localhost:5433`
- UAT DB: `localhost:5434`
- Retry logic ensures tunnels are fully established

### 2. Data Extraction Phase

**Extract Production Business Data:**
```bash
pg_dump \
  -h localhost -p 5433 \
  -U "$PROD_DB_USER" \
  -d "$PROD_DB_NAME" \
  --no-owner \
  --no-privileges \
  --data-only \
  --exclude-table='auth_user' \
  --exclude-table='auth_permission' \
  --exclude-table='auth_group*' \
  --exclude-table='django_session' \
  --exclude-table='authtoken_token' \
  --exclude-table='django_admin_log' \
  --exclude-table='django_content_type' \
  --exclude-table='django_migrations' \
  > /tmp/prod_data.sql
```

**Excluded Tables:**
- `auth_*` - User accounts, permissions, groups
- `django_session` - Active user sessions
- `authtoken_token` - API tokens
- `django_admin_log` - Admin action history
- `django_content_type` - Django ORM metadata
- `django_migrations` - Migration history

**Filter Test Tenants:**
```bash
# Remove any test tenant data from production dump
grep -v "^INSERT INTO.*apps_tenants_tenant.*'test_" /tmp/prod_data.sql > /tmp/filtered_data.sql
```

### 3. UAT Preparation Phase

**Backup UAT Database:**
```bash
pg_dump \
  -h localhost -p 5434 \
  -U "$UAT_DB_USER" \
  -d "$UAT_DB_NAME" \
  --format=custom \
  > /tmp/uat_backup_$(date +%Y%m%d_%H%M%S).dump
```

**Clear UAT Business Data (Preserve Test Tenants):**
```sql
SET session_replication_role = 'replica';  -- Disable triggers

DO $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN (
    SELECT table_schema, table_name
    FROM information_schema.columns
    WHERE column_name = 'tenant_id'
      AND table_schema NOT IN ('pg_catalog', 'information_schema')
      AND table_name NOT LIKE 'auth_%'
      AND table_name NOT LIKE 'django_%'
  ) LOOP
    -- Delete only non-test tenant data
    EXECUTE format('DELETE FROM %I.%I WHERE tenant_id NOT IN (SELECT id FROM apps_tenants_tenant WHERE schema_name LIKE ''test_%%'');', 
      r.table_schema, r.table_name);
  END LOOP;
END $$;

SET session_replication_role = 'origin';  -- Re-enable triggers
```

### 4. Import Phase

**Import Filtered Production Data:**
```bash
psql \
  -h localhost -p 5434 \
  -U "$UAT_DB_USER" \
  -d "$UAT_DB_NAME" \
  -v ON_ERROR_STOP=1 \
  -f /tmp/filtered_data.sql
```

**Fix Foreign Key References:**

Production data references production user IDs. UAT has different user IDs.

```sql
-- Get UAT superuser ID
SELECT id FROM auth_user WHERE is_superuser = true LIMIT 1;

-- Update all owner_id fields to UAT superuser
UPDATE apps_suppliers_supplier SET owner_id = <UAT_SUPERUSER_ID> WHERE owner_id IS NOT NULL;
UPDATE apps_plants_plant SET owner_id = <UAT_SUPERUSER_ID> WHERE owner_id IS NOT NULL;
UPDATE apps_customers_customer SET owner_id = <UAT_SUPERUSER_ID> WHERE owner_id IS NOT NULL;

-- Update created_by_id and updated_by_id fields
...
```

### 5. Validation Phase

**Data Integrity Checks:**

1. **Tenant Count:**
   - Verify test tenants preserved
   - Count production tenants imported
   - Warn if no test tenants found

2. **Orphaned References:**
   - Check for `owner_id` not in `auth_user`
   - Fail workflow if orphans found

3. **Foreign Key Constraints:**
   - Verify all FK references valid
   - Ensure no constraint violations

### 6. Cleanup Phase

**Always Runs (even on failure):**
- Kill SSH tunnel processes
- Remove temporary files:
  - `/tmp/prod_data.sql`
  - `/tmp/filtered_data.sql`
  - `/tmp/clear_uat.sql`
  - `/tmp/fixup.sql`
  - `/tmp/uat_backup_*.dump`

---

## Required Secrets

### Production Database Secrets

**Environment:** `prod-backend` (or repository-level)

| Secret | Purpose | Example |
|--------|---------|---------|
| `PROD_DB_HOST` | Production database hostname | `localhost` |
| `PROD_DB_PORT` | Production database port | `5432` |
| `PROD_DB_USER` | Database username | `projectmeats_user` |
| `PROD_DB_PASSWORD` | Database password | `***` |
| `PROD_DB_NAME` | Database name | `projectmeats_prod` |

### UAT Database Secrets

**Environment:** `uat-backend` (or repository-level)

| Secret | Purpose | Example |
|--------|---------|---------|
| `UAT_DB_HOST` | UAT database hostname | `localhost` |
| `UAT_DB_PORT` | UAT database port | `5432` |
| `UAT_DB_USER` | Database username | `projectmeats_user` |
| `UAT_DB_PASSWORD` | Database password | `***` |
| `UAT_DB_NAME` | Database name | `projectmeats_uat` |

### SSH Secrets

| Secret | Purpose | Example |
|--------|---------|---------|
| `SSH_USER` | Production SSH username | `root` |
| `SSH_HOST` | Production SSH hostname | `prod.meatscentral.com` |
| `SSH_PASSWORD` | Production SSH password | `***` |
| `UAT_SSH_USER` | UAT SSH username | `root` |
| `UAT_SSH_HOST` | UAT SSH hostname | `uat.meatscentral.com` |
| `UAT_SSH_PASSWORD` | UAT SSH password | `***` |

**Note:** If production and UAT use the same SSH host, `UAT_SSH_*` can reuse `SSH_*` values.

---

## Usage

### Automatic Execution

**Schedule:** Daily at 00:00 UTC (midnight)

The workflow runs automatically via cron trigger:
```yaml
on:
  schedule:
    - cron: "0 0 * * *"  # Daily at 00:00 UTC
```

### Manual Execution

**Trigger manually via GitHub UI:**

1. Go to **Actions** tab
2. Select **"🔄 Daily Production-to-UAT Database Sync"**
3. Click **"Run workflow"** dropdown
4. Select branch (usually `main`)
5. Click **"Run workflow"** button

**Trigger via GitHub CLI:**
```bash
gh workflow run "db-sync-prod-to-uat.yml" --ref main
```

### Monitoring

**View workflow runs:**
```bash
gh run list --workflow=db-sync-prod-to-uat.yml --limit 10
```

**View specific run logs:**
```bash
gh run view <RUN_ID> --log
```

---

## Troubleshooting

### SSH Tunnel Failures

**Symptom:**
```
❌ Production tunnel failed to establish after 10 attempts
```

**Possible Causes:**
1. SSH credentials incorrect
2. SSH host unreachable
3. Firewall blocking connection
4. Database host/port incorrect

**Debug Steps:**
1. Check workflow logs for SSH verbose output (`-v` flag)
2. Verify SSH secrets in GitHub Settings → Secrets
3. Test SSH connection manually:
   ```bash
   ssh -v $SSH_USER@$SSH_HOST
   ```
4. Test port forwarding manually:
   ```bash
   ssh -L 5433:$PROD_DB_HOST:5432 $SSH_USER@$SSH_HOST
   nc -zv localhost 5433
   ```

### Data Import Failures

**Symptom:**
```
ERROR: duplicate key value violates unique constraint
```

**Cause:** Duplicate data or constraint violation

**Solution:**
1. Check UAT database for existing data:
   ```sql
   SELECT COUNT(*) FROM apps_tenants_tenant;
   ```
2. Manually clear UAT database:
   ```sql
   TRUNCATE TABLE apps_tenants_tenant CASCADE;
   ```
3. Re-run workflow

### Orphaned Foreign Keys

**Symptom:**
```
❌ Found 5 orphaned owner_id references
```

**Cause:** Foreign key fixup failed or incomplete

**Solution:**
1. Check UAT superuser exists:
   ```sql
   SELECT id FROM auth_user WHERE is_superuser = true;
   ```
2. Manually fix orphaned references:
   ```sql
   UPDATE apps_suppliers_supplier 
   SET owner_id = (SELECT id FROM auth_user WHERE is_superuser = true LIMIT 1)
   WHERE owner_id NOT IN (SELECT id FROM auth_user);
   ```

### Test Tenant Loss

**Symptom:**
```
⚠️ Warning: No test tenants found in UAT
```

**Impact:** UAT test data lost

**Prevention:**
- Workflow preserves test tenants with `schema_name LIKE 'test_%'`
- Ensure test tenants follow naming convention

**Recovery:**
1. Restore from backup:
   ```bash
   pg_restore -h $UAT_DB_HOST -U $UAT_DB_USER -d $UAT_DB_NAME /tmp/uat_backup_*.dump
   ```
2. Manually recreate test tenants via Django admin

---

## Security Considerations

### Sensitive Data Handling

**Excluded from Sync:**
- User passwords (auth_user table excluded)
- API tokens (authtoken_token excluded)
- Session data (django_session excluded)

**Included in Sync:**
- Tenant business data (suppliers, customers, orders)
- Tenant metadata (names, slugs, domains)

**Recommendation:** Review production data for PII before enabling sync.

### Secret Management

**Best Practices:**
- Use environment-scoped secrets (not repository secrets)
- Rotate SSH passwords regularly
- Use SSH keys instead of passwords (future enhancement)
- Restrict database user permissions (read-only for production extract)

### Access Control

**Who Can Trigger:**
- Anyone with `write` access to repository
- Manual triggers require GitHub authentication

**Audit Trail:**
- All workflow runs logged in GitHub Actions
- Workflow run ID included in failure notifications

---

## Performance

### Typical Execution Time

| Phase | Duration | Notes |
|-------|----------|-------|
| Setup SSH tunnels | 5-30 seconds | Depends on network |
| Extract production data | 2-10 minutes | Depends on data size |
| Filter test tenants | < 10 seconds | Grep operation |
| Backup UAT database | 1-5 minutes | Safety precaution |
| Clear UAT business data | 30 seconds - 2 minutes | Depends on data volume |
| Import production data | 2-10 minutes | Depends on data size |
| Fix foreign keys | < 30 seconds | Simple UPDATE queries |
| Validate integrity | < 30 seconds | COUNT queries |
| Cleanup | < 10 seconds | Kill processes, remove files |

**Total:** 10-30 minutes typically

### Timeout

**Workflow Timeout:** 30 minutes

If sync takes longer, increase timeout in workflow:
```yaml
timeout-minutes: 60  # Increase to 60 minutes
```

---

## Future Enhancements

### Planned Improvements

1. **SSH Key Authentication:**
   - Replace password-based SSH with key-based
   - More secure, no password in secrets

2. **Slack/Email Notifications:**
   - Send notification on sync completion
   - Alert on failure with error details

3. **Incremental Sync:**
   - Only sync changed data since last sync
   - Use timestamp-based filtering
   - Reduces sync time for large databases

4. **Data Anonymization:**
   - Anonymize sensitive fields (names, emails, addresses)
   - Use tools like `postgresql-anonymizer`
   - Comply with GDPR/privacy regulations

5. **Backup Retention:**
   - Upload UAT backups to S3/DigitalOcean Spaces
   - Retain last 7 backups for rollback
   - Automatic cleanup of old backups

6. **Parallel Dump/Restore:**
   - Use `pg_dump --jobs=4` for parallel extraction
   - Use `pg_restore --jobs=4` for parallel import
   - Significantly faster for large databases

---

## Rollback Procedure

If sync causes issues in UAT:

### 1. Identify Backup

**Backup Location:** `/tmp/uat_backup_YYYYMMDD_HHMMSS.dump`

**Latest Backup:**
```bash
ls -lt /tmp/uat_backup_*.dump | head -1
```

### 2. Restore Backup

**Via SSH:**
```bash
ssh $UAT_SSH_USER@$UAT_SSH_HOST
pg_restore \
  -h $UAT_DB_HOST \
  -U $UAT_DB_USER \
  -d $UAT_DB_NAME \
  --clean \
  --if-exists \
  /tmp/uat_backup_YYYYMMDD_HHMMSS.dump
```

### 3. Verify Restoration

**Check tenant count:**
```sql
SELECT COUNT(*) FROM apps_tenants_tenant;
```

**Check test tenants:**
```sql
SELECT * FROM apps_tenants_tenant WHERE schema_name LIKE 'test_%';
```

### 4. Notify Team

**Post in Slack/email:**
```
⚠️ UAT Database Restored to Backup (YYYYMMDD_HHMMSS)
Reason: [sync failure reason]
Action: [steps taken]
Impact: [any data loss]
```

---

## Related Documentation

- **Configuration & Secrets:** `/docs/CONFIGURATION_AND_SECRETS.md`
- **Multi-Tenancy Architecture:** `/docs/ARCHITECTURE.md`
- **CI/CD Workflows:** `/.github/workflows/README.md`
- **Golden Standard CI/CD:** `/docs/GOLDEN_STANDARD_ACHIEVEMENT.md`

---

## Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-05 | v2.0 | Added robust SSH tunnel retry logic with 10 attempts |
| 2025-12-XX | v1.0 | Initial implementation with basic SSH tunnels |

---

**Status:** ✅ Production-Ready  
**Last Updated:** January 5, 2026  
**Maintained By:** Infrastructure Team
