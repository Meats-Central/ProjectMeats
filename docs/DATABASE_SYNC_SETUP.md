# Database Sync Setup Checklist

## Required GitHub Secrets Configuration

Before the workflow can run, ensure these secrets are configured in GitHub:

### Step 1: Verify Production Secrets (`production-backend` environment)

```bash
# Check existing secrets
gh secret list --env production-backend

# Required secrets:
# - PROD_DB_HOST (private database host)
# - PROD_DB_PORT (default: 5432, optional)
# - PROD_DB_USER (database username)
# - PROD_DB_PASSWORD (database password)
# - PROD_DB_NAME (database name)
# - SSH_HOST (bastion host)
# - SSH_USER (bastion username)
# - SSH_PASSWORD (bastion password)
```

**Note:** Most of these should already exist. You may need to add the `PROD_*` prefixed versions.

### Step 2: Verify UAT Secrets (`uat-backend` environment)

```bash
# Check existing secrets
gh secret list --env uat-backend

# Required secrets:
# - UAT_DB_HOST (private database host)
# - UAT_DB_PORT (default: 5432, optional)
# - UAT_DB_USER (database username)
# - UAT_DB_PASSWORD (database password)
# - UAT_DB_NAME (database name)
# - UAT_SSH_HOST (bastion host)
# - UAT_SSH_USER (bastion username)
# - UAT_SSH_PASSWORD (bastion password)
```

### Step 3: Add Missing Secrets

If any `PROD_*` or `UAT_*` prefixed secrets are missing, add them:

```bash
# Add production database secrets
gh secret set PROD_DB_HOST --env production-backend --body "your-prod-db-host"
gh secret set PROD_DB_USER --env production-backend --body "your-prod-db-user"
gh secret set PROD_DB_PASSWORD --env production-backend --body "your-prod-db-password"
gh secret set PROD_DB_NAME --env production-backend --body "your-prod-db-name"

# Add UAT database secrets
gh secret set UAT_DB_HOST --env uat-backend --body "your-uat-db-host"
gh secret set UAT_DB_USER --env uat-backend --body "your-uat-db-user"
gh secret set UAT_DB_PASSWORD --env uat-backend --body "your-uat-db-password"
gh secret set UAT_DB_NAME --env uat-backend --body "your-uat-db-name"
gh secret set UAT_SSH_HOST --env uat-backend --body "your-uat-ssh-host"
gh secret set UAT_SSH_USER --env uat-backend --body "your-uat-ssh-user"
gh secret set UAT_SSH_PASSWORD --env uat-backend --body "your-uat-ssh-password"
```

**Alternative:** If `DB_HOST`, `DB_USER`, etc. already exist in each environment, you can reference them in the workflow without the prefix:

```yaml
# Option 1: Use PROD_* prefixed secrets (recommended for clarity)
${{ secrets.PROD_DB_HOST }}

# Option 2: Use existing DB_HOST from production-backend environment
${{ secrets.DB_HOST }}  # Will resolve to production value when job uses production-backend environment
```

### Step 4: Update env.manifest.json (Optional)

If using `PROD_*` and `UAT_*` prefixed secrets, add them to the manifest:

```bash
cd /workspaces/ProjectMeats
nano config/env.manifest.json

# Add to environment_secrets section:
"PROD_DB_HOST": { ... },
"UAT_DB_HOST": { ... },
# etc.
```

Then run audit:
```bash
python config/manage_env.py audit
```

### Step 5: Test the Workflow

```bash
# Manually trigger the workflow
gh workflow run db-sync-prod-to-uat.yml

# Watch the run
gh run watch

# View logs if it fails
gh run view --log
```

### Step 6: Verify in UAT

After successful sync:

```bash
# SSH to UAT server
ssh $UAT_SSH_USER@$UAT_SSH_HOST

# Connect to UAT database
psql -h $UAT_DB_HOST -U $UAT_DB_USER -d $UAT_DB_NAME

# Check tenant count
SELECT COUNT(*) FROM apps_tenants_tenant;

# Verify test tenants preserved
SELECT COUNT(*) FROM apps_tenants_tenant WHERE schema_name LIKE 'test_%';

# Check for orphaned references
SELECT COUNT(*) FROM apps_suppliers_supplier WHERE owner_id NOT IN (SELECT id FROM auth_user);
-- Should be 0

# Try logging in with production credentials
# Should FAIL (credentials not synced)
```

## Troubleshooting

### SSH Tunnel Fails
```bash
# Test SSH connectivity manually
ssh $SSH_USER@$SSH_HOST "echo 'Connection successful'"

# Test database access through tunnel
ssh -N -L 5433:$PROD_DB_HOST:5432 $SSH_USER@$SSH_HOST &
psql -h localhost -p 5433 -U $PROD_DB_USER -d $PROD_DB_NAME -c "SELECT 1;"
```

### pg_dump Fails
- Check PostgreSQL client version: `pg_dump --version`
- Verify database credentials
- Check network connectivity to database

### Import Fails
- Check UAT database has enough space
- Verify schema matches (run migrations in UAT first)
- Check for conflicting data (primary key violations)

### Validation Fails (Orphaned References)
- Review post-restore fixup SQL
- Ensure UAT has at least one superuser
- Check for new models with user foreign keys

## Monitoring

### Daily Check
```bash
# View recent workflow runs
gh run list --workflow=db-sync-prod-to-uat.yml --limit 5

# Check last run status
gh run list --workflow=db-sync-prod-to-uat.yml --limit 1 --json status,conclusion
```

### Set Up Notifications
Edit `.github/workflows/db-sync-prod-to-uat.yml`:

```yaml
- name: Send notification on failure
  if: failure()
  run: |
    # Slack webhook
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"❌ Database sync failed: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"}'
```

## Security Checklist

- [ ] Production database credentials never logged
- [ ] SSH passwords passed via SSHPASS environment variable
- [ ] auth_user table excluded from sync
- [ ] authtoken_token table excluded from sync
- [ ] django_session table excluded from sync
- [ ] Test tenants (test_*) preserved in UAT
- [ ] Foreign key references remapped to UAT superuser
- [ ] Workflow uses environment-scoped secrets
- [ ] set -euo pipefail used in all bash steps
- [ ] Temp files cleaned up in always() step

## Performance Optimization

### If Sync Takes Too Long

1. **Increase timeout:**
```yaml
timeout-minutes: 60  # Increase from 30
```

2. **Use compression:**
```bash
pg_dump ... | gzip > prod_data.sql.gz
```

3. **Split by table:**
```bash
# Dump large tables separately
pg_dump --table=apps_purchase_orders_purchaseorder > po_data.sql
```

4. **Schedule during low-usage hours:**
```yaml
- cron: "0 3 * * *"  # 3 AM UTC instead of midnight
```

## Rollback Procedure

If sync corrupts UAT data:

```bash
# Download backup from GitHub Actions artifacts
gh run download $RUN_ID

# Restore backup
pg_restore -h $UAT_DB_HOST -U $UAT_DB_USER -d $UAT_DB_NAME uat_backup_*.dump
```

## Next Steps

After successful setup:

1. [ ] Run initial manual sync: `gh workflow run db-sync-prod-to-uat.yml`
2. [ ] Verify UAT data integrity (see Step 6)
3. [ ] Set up Slack/email notifications
4. [ ] Document sync schedule for team
5. [ ] Update runbooks with sync procedures
6. [ ] Schedule review after 1 week of automated syncs

---

**Document Status:** ✅ Active Setup Guide  
**Created:** January 4, 2026  
**For:** Database Sync Workflow v1.0
