# Database Credentials Fix - Complete Summary

**Date:** 2025-12-04  
**Status:** ✅ **COMPLETED** - See `DATABASE_MIGRATION_GUIDE.md` for current implementation  
**Archived:** Historical reference only

---

## Current Implementation

**This document is archived.** The SSH tunnel approach was successfully implemented.

**See:** `DATABASE_MIGRATION_GUIDE.md` for operational guide

---

## Historical Summary

Deployment workflows were failing during the `migrate` job with:
```
decouple.UndefinedValueError: DB_NAME not found. Declare it as envvar or define a default value.
```

**Root Cause:**
- Django settings require database credentials (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
- These credentials were not provided as environment variables
- GitHub Actions secrets were not configured for database connections

**Failed Workflow Runs:**
- https://github.com/Meats-Central/ProjectMeats/actions/runs/19854751426 (DB_NAME missing)
- https://github.com/Meats-Central/ProjectMeats/actions/runs/19915410755 (DB_USER missing)
- https://github.com/Meats-Central/ProjectMeats/actions/runs/19915535746 (DATABASE_URL empty)

---

## Solution Implemented

### Phase 1: Add DB_NAME Default (PR #892)

**Changes:**
- Added `DB_NAME: defaultdb` as environment variable in migrate jobs
- Added fallback logic to parse DB_NAME from DATABASE_URL
- Applied to all three deployment workflows (dev, UAT, prod)

**Result:** Partially fixed - DB_NAME now available, but other credentials still missing

**PR:** https://github.com/Meats-Central/ProjectMeats/pull/892

---

### Phase 2: Parse All DB Credentials (PR #894)

**Problem:** Django settings load before shell script runs, so parsing DATABASE_URL inside the migration script was too late.

**Solution:**
- Added separate "Parse DATABASE_URL" step that runs **before** migrations
- Extracts all credentials (USER, PASSWORD, HOST, PORT, NAME) using sed
- Exports as step outputs
- Migration step uses step outputs as environment variables

**Workflow Changes:**
```yaml
- name: Parse DATABASE_URL and set DB credentials
  id: parse_db
  run: |
    if [ -n "${{ secrets.DEV_DB_URL }}" ]; then
      DB_USER=$(echo "${{ secrets.DEV_DB_URL }}" | sed -n 's|postgresql://\([^:]*\):.*|\1|p')
      DB_PASSWORD=$(echo "${{ secrets.DEV_DB_URL }}" | sed -n 's|postgresql://[^:]*:\([^@]*\)@.*|\1|p')
      DB_HOST=$(echo "${{ secrets.DEV_DB_URL }}" | sed -n 's|.*@\([^:]*\):.*|\1|p')
      DB_PORT=$(echo "${{ secrets.DEV_DB_URL }}" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
      DB_NAME=$(echo "${{ secrets.DEV_DB_URL }}" | sed -n 's|.*/\([^?]*\).*|\1|p')
      
      echo "db_user=$DB_USER" >> $GITHUB_OUTPUT
      echo "db_password=$DB_PASSWORD" >> $GITHUB_OUTPUT
      echo "db_host=$DB_HOST" >> $GITHUB_OUTPUT
      echo "db_port=${DB_PORT:-5432}" >> $GITHUB_OUTPUT
      echo "db_name=${DB_NAME:-defaultdb}" >> $GITHUB_OUTPUT
    else
      # Defaults
      echo "db_port=5432" >> $GITHUB_OUTPUT
      echo "db_name=defaultdb" >> $GITHUB_OUTPUT
    fi

- name: Run idempotent migrations
  env:
    DATABASE_URL: ${{ secrets.DEV_DB_URL }}
    DB_NAME: ${{ steps.parse_db.outputs.db_name }}
    DB_USER: ${{ steps.parse_db.outputs.db_user }}
    DB_PASSWORD: ${{ steps.parse_db.outputs.db_password }}
    DB_HOST: ${{ steps.parse_db.outputs.db_host }}
    DB_PORT: ${{ steps.parse_db.outputs.db_port }}
```

**Result:** Workflow logic fixed, but DATABASE_URL secret not configured

**PR:** https://github.com/Meats-Central/ProjectMeats/pull/894

---

### Phase 3: Documentation & Helper Script (PR #896)

**Created Files:**

1. **DEPLOYMENT_DB_SECRETS_SETUP.md**
   - Complete configuration guide
   - DATABASE_URL vs individual credentials options
   - DigitalOcean specific instructions
   - GitHub secrets setup (web UI and CLI)
   - Verification steps
   - Troubleshooting guide
   - Security best practices

2. **scripts/setup-db-secrets.sh**
   - Interactive configuration script
   - Validates DATABASE_URL format
   - Prompts for each environment (dev, UAT, prod)
   - Parses and displays credentials for verification
   - Sets secrets using GitHub CLI
   - Provides next steps

**Usage:**
```bash
./scripts/setup-db-secrets.sh
```

**PR:** https://github.com/Meats-Central/ProjectMeats/pull/896

---

## Current Status

### ✅ Completed

1. **Workflow Logic Fixed**
   - All three deployment workflows updated (dev, UAT, prod)
   - DATABASE_URL parsing step added
   - Environment variables properly set for Django
   - Defaults provided (defaultdb, port 5432)

2. **Documentation Created**
   - Comprehensive setup guide
   - Interactive helper script
   - Troubleshooting section
   - Security best practices

3. **PRs Merged**
   - #892: Add DB_NAME default
   - #894: Parse all DB credentials
   - #896: Documentation and setup script

### 🔄 Pending Action Required

**Configure DATABASE_URL secrets in GitHub:**

1. **Get Database Credentials from DigitalOcean:**
   - Go to DigitalOcean Console → Databases
   - Select your PostgreSQL database
   - Copy the "Connection String"

2. **Run Setup Script:**
   ```bash
   cd /workspaces/ProjectMeats
   ./scripts/setup-db-secrets.sh
   ```

3. **Or Manually Add via GitHub UI:**
   - Go to: https://github.com/Meats-Central/ProjectMeats/settings/secrets/actions
   - Select "Environments"
   - For each environment (dev-backend, uat2-backend, prod2-backend):
     - Add secret name: `DEV_DB_URL`, `UAT_DB_URL`, `PROD_DB_URL`
     - Paste connection string
     - Save

4. **Verify Configuration:**
   ```bash
   # Trigger deployment
   gh workflow run "Deploy Dev (Frontend + Backend via DOCR and GHCR)" --ref development
   
   # Monitor
   gh run watch
   ```

---

## Expected DATABASE_URL Format

```
postgresql://USERNAME:PASSWORD@HOST:PORT/DBNAME
```

**DigitalOcean Example:**
```
postgresql://doadmin:RANDOMLY_GENERATED_PASSWORD@db-postgresql-nyc3-12345-do-user-123456-0.b.db.ondigitalocean.com:25060/defaultdb?sslmode=require
```

**Components:**
- `USERNAME`: Usually `doadmin` for DigitalOcean
- `PASSWORD`: Random generated password (copy from DO console)
- `HOST`: Database host URL
- `PORT`: Usually `25060` for DigitalOcean
- `DBNAME`: Usually `defaultdb`
- `?sslmode=require`: Required for DigitalOcean connections

---

## Verification Checklist

After configuring secrets:

- [ ] DATABASE_URL secrets added for all three environments
  - [ ] `DEV_DB_URL` in `dev-backend` environment
  - [ ] `UAT_DB_URL` in `uat2-backend` environment
  - [ ] `PROD_DB_URL` in `prod2-backend` environment

- [ ] Deployment workflow triggered and monitored

- [ ] Migrate job logs show parsed credentials:
  ```
  Database configuration:
    DB_HOST: db-postgresql-nyc3-12345-do-user-123456-0.b.db.ondigitalocean.com
    DB_PORT: 25060
    DB_NAME: defaultdb
    DB_USER: doadmin
  ```

- [ ] Migrate job completes successfully:
  ```
  ✓ Migrations completed successfully
  ```

- [ ] Backend deployment succeeds

- [ ] Health checks pass

---

## Files Modified

### Workflows Updated:
- `.github/workflows/11-dev-deployment.yml` (dev environment)
- `.github/workflows/12-uat-deployment.yml` (UAT environment)
- `.github/workflows/13-prod-deployment.yml` (production environment)

### Documentation Added:
- `DEPLOYMENT_DB_SECRETS_SETUP.md` (complete guide)
- `scripts/setup-db-secrets.sh` (interactive setup)
- `DB_CREDENTIALS_FIX_SUMMARY.md` (this file)

---

## Troubleshooting

### Issue: Empty credentials in logs
```
DB_HOST: 
DB_USER: 
```

**Cause:** DATABASE_URL secret not configured  
**Fix:** Run `./scripts/setup-db-secrets.sh`

---

### Issue: Parsing fails
```
DB_NAME: 
```

**Cause:** Invalid DATABASE_URL format  
**Fix:** Ensure format is `postgresql://user:password@host:port/database`

---

### Issue: SSL connection errors
```
connection failed: SSL required
```

**Cause:** DigitalOcean requires SSL  
**Fix:** Append `?sslmode=require` to DATABASE_URL

---

## Next Steps

1. **Immediate:** Configure DATABASE_URL secrets
   ```bash
   ./scripts/setup-db-secrets.sh
   ```

2. **Test:** Trigger deployment workflow
   ```bash
   gh workflow run "Deploy Dev (Frontend + Backend via DOCR and GHCR)" --ref development
   ```

3. **Verify:** Monitor migrate job logs
   ```bash
   gh run watch
   ```

4. **Document:** Update team wiki with DATABASE_URL configuration

5. **Security:** Schedule quarterly password rotation

---

## References

- **Setup Guide:** `DEPLOYMENT_DB_SECRETS_SETUP.md`
- **Setup Script:** `scripts/setup-db-secrets.sh`
- **PR #892:** https://github.com/Meats-Central/ProjectMeats/pull/892
- **PR #894:** https://github.com/Meats-Central/ProjectMeats/pull/894
- **PR #896:** https://github.com/Meats-Central/ProjectMeats/pull/896
- **Failed Workflow:** https://github.com/Meats-Central/ProjectMeats/actions/runs/19854751426

---

## Contact

For assistance with database configuration:
1. Review `DEPLOYMENT_DB_SECRETS_SETUP.md`
2. Run `./scripts/setup-db-secrets.sh`
3. Check workflow logs for specific errors
4. Contact DevOps team or repository maintainers
