# Deployment Database Secrets Configuration Guide

**Created:** 2025-12-04  
**Status:** ⚠️ **SUPERSEDED** - See `DATABASE_MIGRATION_GUIDE.md` for current implementation  
**Archived:** Historical reference only

---

## Current Implementation

**This document is archived.** The actual implementation uses SSH tunnel approach.

**See:** `DATABASE_MIGRATION_GUIDE.md` for current setup

---

## Historical Context

The deployment workflows require database credentials to run migrations. These credentials can be provided either as:
1. A single `DATABASE_URL` connection string (recommended)
2. Individual credential secrets (`DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`)

Currently, the `DEV_DB_URL` secret is not configured, causing migration failures with:
```
decouple.UndefinedValueError: DB_NAME not found
decouple.UndefinedValueError: DB_USER not found
```

---

## Solution Overview

The workflows now include a parsing step that:
1. Extracts DB credentials from `DATABASE_URL` if provided
2. Falls back to defaults (`defaultdb`, port `5432`) if parsing fails
3. Sets credentials as environment variables for Django

---

## Required Secrets Configuration

### Option 1: Single DATABASE_URL (Recommended)

Add the following secrets to each environment in GitHub:

#### Development Environment
```
Secret Name: DEV_DB_URL
Secret Value: postgresql://USERNAME:PASSWORD@HOST:PORT/DBNAME
Example: postgresql://doadmin:RANDOMLY_GENERATED_PASSWORD@db-postgresql-nyc3-12345-do-user-123456-0.b.db.ondigitalocean.com:25060/defaultdb
```

#### UAT Environment
```
Secret Name: UAT_DB_URL
Secret Value: postgresql://USERNAME:PASSWORD@HOST:PORT/DBNAME
```

#### Production Environment
```
Secret Name: PROD_DB_URL
Secret Value: postgresql://USERNAME:PASSWORD@HOST:PORT/DBNAME
```

### Option 2: Individual Credentials

If you prefer to set credentials individually:

#### Development Environment
```
DEV_DB_NAME=defaultdb
DEV_DB_USER=doadmin
DEV_DB_PASSWORD=your_password_here
DEV_DB_HOST=db-postgresql-nyc3-12345-do-user-123456-0.b.db.ondigitalocean.com
DEV_DB_PORT=25060
```

#### UAT Environment
```
UAT_DB_NAME=defaultdb
UAT_DB_USER=doadmin
UAT_DB_PASSWORD=your_password_here
UAT_DB_HOST=your_uat_db_host
UAT_DB_PORT=25060
```

#### Production Environment
```
PROD_DB_NAME=defaultdb
PROD_DB_USER=doadmin
PROD_DB_PASSWORD=your_password_here
PROD_DB_HOST=your_prod_db_host
PROD_DB_PORT=25060
```

---

## DigitalOcean Managed PostgreSQL Setup

### For DigitalOcean Managed Databases:

1. **Get Connection Details:**
   - Go to DigitalOcean Console → Databases
   - Select your PostgreSQL database
   - Click "Connection Details"
   - Choose "Connection String" mode

2. **Connection String Format:**
   ```
   postgresql://doadmin:RANDOM_PASSWORD@HOST:25060/defaultdb?sslmode=require
   ```

3. **Important Notes:**
   - Default database name is typically `defaultdb`
   - Default port for DigitalOcean is `25060`
   - Default user is `doadmin`
   - Password is randomly generated - copy it from the console

---

## How to Add Secrets to GitHub

### Via GitHub Web Interface:

1. **Navigate to Repository Settings:**
   - Go to https://github.com/Meats-Central/ProjectMeats/settings/secrets/actions

2. **Add Environment Secrets:**
   - Click "Environments" in the left sidebar
   - Select the environment (e.g., `dev-backend`, `uat-backend`, `prod-backend`)
   - Click "Add secret"
   - Enter secret name (e.g., `DEV_DB_URL`)
   - Paste the connection string
   - Click "Add secret"

3. **Repeat for Each Environment:**
   - `dev-backend` → `DEV_DB_URL`
   - `uat2-backend` → `UAT_DB_URL`
   - `prod2-backend` → `PROD_DB_URL`

### Via GitHub CLI:

```bash
# Add development DB URL
gh secret set DEV_DB_URL --env dev-backend --body "postgresql://user:pass@host:port/dbname"

# Add UAT DB URL
gh secret set UAT_DB_URL --env uat2-backend --body "postgresql://user:pass@host:port/dbname"

# Add production DB URL
gh secret set PROD_DB_URL --env prod2-backend --body "postgresql://user:pass@host:port/dbname"
```

---

## Verification

### 1. Check Secrets Are Set

```bash
# List secrets for an environment
gh secret list --env dev-backend
```

Expected output should include `DEV_DB_URL` (or individual credentials).

### 2. Trigger Deployment

Push a commit to `development` branch or manually trigger the workflow:

```bash
gh workflow run "Deploy Dev (Frontend + Backend via DOCR and GHCR)" --ref development
```

### 3. Monitor Migration Job

```bash
# Watch the workflow
gh run watch

# Or check specific job logs
gh run view --log | grep -A 20 "Database configuration"
```

Expected output in logs:
```
=== Running idempotent schema migrations ===
Database configuration:
  DB_HOST: db-postgresql-nyc3-12345-do-user-123456-0.b.db.ondigitalocean.com
  DB_PORT: 25060
  DB_NAME: defaultdb
  DB_USER: doadmin
```

---

## Workflow Changes Summary

### What Was Fixed:

1. **PR #892** - Added `DB_NAME=defaultdb` default value
2. **PR #894** - Added DATABASE_URL parsing step to extract all credentials

### How It Works:

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
      # Fallback to defaults
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

---

## Troubleshooting

### Issue: Empty DB credentials in logs

**Symptom:**
```
DB_HOST: 
DB_USER: 
DB_PASSWORD: 
```

**Cause:** `DATABASE_URL` secret is not configured or is empty.

**Fix:** Add the `DEV_DB_URL` secret (see "How to Add Secrets" above).

---

### Issue: Parsing fails with invalid format

**Symptom:**
```
DB_NAME: 
DB_USER: 
```

**Cause:** DATABASE_URL is not in the expected format.

**Fix:** Ensure format is `postgresql://user:password@host:port/database`

---

### Issue: SSL connection errors

**Symptom:**
```
connection to server at "host" failed: SSL required
```

**Cause:** DigitalOcean requires SSL connections.

**Fix:** Append `?sslmode=require` to DATABASE_URL:
```
postgresql://user:pass@host:port/dbname?sslmode=require
```

---

## Security Best Practices

1. **Never commit database credentials to code**
   - Always use GitHub Secrets
   - Never hardcode in workflows or settings files

2. **Use environment-specific credentials**
   - Each environment (dev, UAT, prod) should have separate databases
   - Never use production credentials in development

3. **Rotate credentials regularly**
   - Update secrets when team members leave
   - Rotate passwords quarterly

4. **Use strong passwords**
   - Let DigitalOcean generate random passwords
   - Minimum 32 characters for production

5. **Restrict database access**
   - Use DigitalOcean's trusted sources feature
   - Add GitHub Actions IP ranges if possible

---

## Related Files

- `.github/workflows/11-dev-deployment.yml` - Development deployment
- `.github/workflows/12-uat-deployment.yml` - UAT deployment
- `.github/workflows/13-prod-deployment.yml` - Production deployment
- `backend/projectmeats/settings/development.py` - Django settings that require DB credentials

---

## Additional Resources

- [DigitalOcean Managed Databases Documentation](https://docs.digitalocean.com/products/databases/)
- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Django Database Configuration](https://docs.djangoproject.com/en/4.2/ref/settings/#databases)

---

## Contact

For questions or issues with database configuration:
1. Check workflow run logs
2. Review this document
3. Contact DevOps team or repository maintainers
