# Database Backup and Restore Workflow Documentation

## Overview
The Database Backup and Restore workflow automates the process of backing up the production PostgreSQL database and restoring it to the staging environment. This ensures that the staging environment has recent production data for realistic testing while maintaining data isolation between environments.

This workflow runs weekly on Sundays at 2:00 AM UTC and can also be triggered manually when needed.

## Table of Contents
1. [Workflow Purpose](#workflow-purpose)
2. [How It Works](#how-it-works)
3. [Schedule and Triggers](#schedule-and-triggers)
4. [Prerequisites](#prerequisites)
5. [Required Secrets](#required-secrets)
6. [Workflow Steps Explained](#workflow-steps-explained)
7. [Manual Execution](#manual-execution)
8. [Monitoring and Verification](#monitoring-and-verification)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Workflow Purpose

### Why This Workflow Exists
- **Realistic Testing**: Staging environment needs production-like data to test features accurately
- **Data Refresh**: Keeps staging data up-to-date with production trends and volumes
- **Automated Process**: Eliminates manual database backup/restore operations
- **Safe Testing**: Developers can test against real data without risking production
- **Compliance**: Maintains separate staging database while keeping it synchronized

### What It Does
1. Connects to DigitalOcean to view managed database backups
2. Creates a fresh backup of the production database
3. Cleans the staging database (removes all data)
4. Restores production backup to staging
5. Verifies the restore was successful
6. Saves backup as GitHub artifact for 30 days

---

## How It Works

### High-Level Flow
```
┌─────────────────────────────────────┐
│  Trigger (Weekly or Manual)         │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Install DigitalOcean CLI (doctl)   │
│  Authenticate with API Token        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Verify Cluster ID & List Databases │
│  Show DigitalOcean Managed Backups  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Install PostgreSQL 17 Client       │
│  Create Production Backup (pg_dump) │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Clean Staging Database             │
│  (DROP SCHEMA public CASCADE)       │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Restore Backup to Staging (psql)   │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Verify Tables Exist in Staging     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Upload Backup as GitHub Artifact   │
│  (Retained for 30 days)             │
└─────────────────────────────────────┘
```

### Architecture Diagram
```
┌──────────────────────────────────────────────────────────┐
│                    GitHub Actions Runner                  │
│                                                           │
│  ┌─────────────┐        ┌──────────────┐                │
│  │   doctl     │───────▶│ DigitalOcean │                │
│  │    CLI      │        │     API      │                │
│  └─────────────┘        └──────────────┘                │
│                                                           │
│  ┌─────────────┐                                         │
│  │  pg_dump    │─────────┐                              │
│  │PostgreSQL 17│         │                              │
│  └─────────────┘         │                              │
│                          │                              │
│  ┌─────────────┐         │                              │
│  │    psql     │         │                              │
│  │PostgreSQL 17│         │                              │
│  └─────────────┘         │                              │
└──────────────────────────┼──────────────────────────────┘
                           │
           ┌───────────────┴──────────────┐
           │                              │
           ▼                              ▼
┌────────────────────┐        ┌────────────────────┐
│  Production DB     │        │   Staging DB       │
│  PostgreSQL 17.6   │        │  PostgreSQL 17.6   │
│  (DigitalOcean)    │        │  (DigitalOcean)    │
│                    │        │                    │
│  Read-Only Access  │        │  Write Access      │
│  Backup Source     │        │  Restore Target    │
└────────────────────┘        └────────────────────┘
```

---

## Schedule and Triggers

### Automatic Schedule
- **Frequency**: Weekly
- **Day**: Every Sunday
- **Time**: 2:00 AM UTC
- **Cron Expression**: `0 2 * * 0`

### Time Zone Conversions
| Time Zone | When It Runs |
|-----------|--------------|
| UTC | Sunday 2:00 AM |
| EST (UTC-5) | Saturday 9:00 PM |
| CST (UTC-6) | Saturday 8:00 PM |
| PST (UTC-8) | Saturday 6:00 PM |
| GMT+5 | Sunday 7:00 AM |
| IST (UTC+5:30) | Sunday 7:30 AM |

### Manual Trigger
The workflow can be triggered manually at any time:
1. Go to **Actions** → **Weekly DB Backup - Using DigitalOcean Backups**
2. Click **Run workflow**
3. Select branch (usually `main` or `development`)
4. Click **Run workflow** button

---

## Prerequisites

### Production and Staging Databases
Before using this workflow, ensure:

1. **Separate Databases**: Production and staging MUST use different databases
   - ✅ Different database clusters (recommended)
   - ✅ Different databases on same cluster (acceptable)
   - ❌ Same database for both (will cause data loss!)

2. **Database Versions**: Both should run PostgreSQL 17 (or same major version)

3. **Access Credentials**: Valid connection strings for both databases

### DigitalOcean Setup
- DigitalOcean account with PostgreSQL managed databases
- API token with database read/write permissions
- Production database cluster ID

---

## Required Secrets

All secrets are stored at the **Repository level** (Settings → Secrets and variables → Actions → Repository secrets).

### Secret Configuration Table

| Secret Name | Description | Example Value | Where to Get It |
|-------------|-------------|---------------|-----------------|
| `DO_API_TOKEN` | DigitalOcean API token | `dop_v1_abc123...` | DigitalOcean → API → Generate Token |
| `PROD_DB_CLUSTER_ID` | Production DB cluster UUID | `3dd4f852-539e-45c2-b3a1-7649432bb1c4` | DigitalOcean → Databases → Cluster ID |
| `PRODUCTION_DB_URL` | Production PostgreSQL connection string | `postgresql://user:pass@host:25060/db?sslmode=require` | DigitalOcean → Databases → Connection Details |
| `STAGING_DB_URL` | Staging PostgreSQL connection string | `postgresql://user:pass@host:25060/staging_db?sslmode=require` | DigitalOcean → Databases → Connection Details |

### How to Add Secrets

1. **Navigate to Repository Settings**:
   ```
   GitHub Repository → Settings → Secrets and variables → Actions → Repository secrets
   ```

2. **Click**: `New repository secret`

3. **Add Each Secret**:
   - Enter **Name** (exactly as shown in table above)
   - Enter **Secret value**
   - Click **Add secret**

### How to Get DigitalOcean API Token

1. Log into **DigitalOcean**
2. Go to **API** → **Tokens** (https://cloud.digitalocean.com/account/api/tokens)
3. Click **Generate New Token**
4. **Name**: `GitHub Actions - DB Backup`
5. **Scopes**: Check both **Read** and **Write**
6. Click **Generate Token**
7. **Copy immediately** (can't view again)
8. Add to GitHub secrets as `DO_API_TOKEN`

### How to Get Database Cluster ID

**Method 1: From Dashboard**
1. Go to **DigitalOcean** → **Databases**
2. Click on your production database
3. Look at the URL:
   ```
   https://cloud.digitalocean.com/databases/[CLUSTER-ID-HERE]?i=abc
   ```
4. The UUID between `/databases/` and `?i=` is your cluster ID

**Method 2: Using doctl CLI**
```bash
# Install doctl
brew install doctl  # macOS
# or download from: https://github.com/digitalocean/doctl/releases

# Authenticate
doctl auth init

# List databases
doctl databases list

# Copy the ID from the output
```

### Database Connection Strings

Connection strings format:
```
postgresql://[username]:[password]@[host]:[port]/[database]?sslmode=require
```

Get from **DigitalOcean Dashboard**:
1. Go to **Databases** → Select your database
2. Click **Connection Details**
3. Select **Connection String** from dropdown
4. Copy the full connection string

**Important**: Staging and production MUST have different connection strings!

---

## Workflow Steps Explained

### Step 1: Install DigitalOcean CLI (doctl)

**What it does**:
- Downloads and installs `doctl` (DigitalOcean command-line tool)
- Version 1.104.0 is used for compatibility

**Command**:
```bash
wget https://github.com/digitalocean/doctl/releases/download/v1.104.0/doctl-1.104.0-linux-amd64.tar.gz
tar xf doctl-1.104.0-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin
```

**Why it's needed**: To interact with DigitalOcean API for viewing managed backups

---

### Step 2: Authenticate with DigitalOcean

**What it does**:
- Authenticates doctl with your DigitalOcean API token
- Enables access to database resources

**Command**:
```bash
doctl auth init --access-token "$DO_API_TOKEN"
```

**Security**: Token is stored securely in GitHub Secrets, never exposed in logs

---

### Step 3: Verify Cluster ID and List Databases

**What it does**:
- Verifies the cluster ID is correct
- Lists all databases in your account
- Shows the cluster ID being used

**Commands**:
```bash
echo "Cluster ID: $PROD_DB_CLUSTER_ID"
doctl databases list
```

**Purpose**: Debugging and verification before backup starts

---

### Step 4: List Production Database Backups

**What it does**:
- Shows DigitalOcean's automatic daily backups
- Displays most recent backup info

**Command**:
```bash
doctl databases backups list $PROD_DB_CLUSTER_ID
```

**Note**: DigitalOcean creates automatic daily backups. This step shows them for reference.

---

### Step 5: Backup Production Database

**What it does**:
- Installs PostgreSQL 17 client (matches your database version)
- Creates a fresh backup using `pg_dump`
- Saves to timestamped SQL file

**Commands**:
```bash
# Install PostgreSQL 17
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get remove -y postgresql-client postgresql-client-16
sudo apt-get install -y postgresql-client-17

# Create backup
/usr/lib/postgresql/17/bin/pg_dump "$PROD_DB_URL" \
  --no-owner \
  --no-privileges \
  --clean \
  --if-exists \
  -f "prod_backup_20250105_020000.sql"
```

**Backup Options Explained**:
- `--no-owner`: Don't include ownership commands (allows restore to different user)
- `--no-privileges`: Don't include GRANT/REVOKE commands
- `--clean`: Include DROP commands before CREATE (clean slate)
- `--if-exists`: Use IF EXISTS in DROP commands (prevents errors)

**Why PostgreSQL 17?**: Must match the database server version (17.6) to avoid compatibility issues

---

### Step 6: Clean Staging Database

**What it does**:
- Drops all tables, functions, and data in staging database
- Creates a clean public schema
- Prepares for fresh production data

**Command**:
```bash
/usr/lib/postgresql/17/bin/psql "$STAGING_DB_URL" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

**⚠️ Warning**: This is DESTRUCTIVE! All staging data is permanently deleted.

**Why CASCADE?**: Removes all objects in the schema (tables, views, functions, sequences)

---

### Step 7: Restore Backup to Staging

**What it does**:
- Restores production backup to staging database
- Recreates all tables, data, indexes, and constraints

**Command**:
```bash
/usr/lib/postgresql/17/bin/psql "$STAGING_DB_URL" < "prod_backup_20250105_020000.sql"
```

**Duration**: Depends on database size (could be seconds to minutes)

**What gets restored**:
- ✅ All tables and table structures
- ✅ All data/records
- ✅ Indexes and constraints
- ✅ Sequences and their current values
- ✅ Views and functions
- ❌ User accounts/roles (excluded with --no-owner)
- ❌ Permissions (excluded with --no-privileges)

---

### Step 8: Verify Staging Database

**What it does**:
- Counts tables in staging database
- Confirms restore was successful
- Fails workflow if no tables found

**Command**:
```bash
TABLE_COUNT=$(/usr/lib/postgresql/17/bin/psql "$STAGING_DB_URL" -t -c \
  "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")

if [ "$TABLE_COUNT" -gt 0 ]; then
  echo "✅ Staging database verified successfully"
else
  echo "⚠️ Warning: No tables found in staging"
  exit 1
fi
```

**Success criteria**: At least 1 table exists in staging database

---

### Step 9: Cleanup

**What it does**:
- Removes temporary backup file from GitHub runner
- Frees up disk space

**Command**:
```bash
rm -f prod_backup_*.sql
```

**Note**: Runs even if previous steps failed (using `if: always()`)

---

### Step 10: Notification

**What it does**:
- Displays success or failure message
- Shows backup metadata
- Indicates next scheduled run

**Output on Success**:
```
🎉 Production database successfully backed up and restored to staging!
📅 Backup date: 2025-01-05 02:00:00 UTC
🔄 Next scheduled backup: Next Sunday at 2:00 AM UTC
📊 Latest DO backup: 2025-01-04 16:23:45 (Size: 125 MB)
```

**Output on Failure**:
```
❌ Database backup/restore failed!
📅 Failed at: 2025-01-05 02:15:33 UTC
⚠️ Please check logs
```

---

### Step 11: Upload Backup Artifact

**What it does**:
- Saves backup SQL file as GitHub artifact
- Retains for 30 days
- Allows manual download if needed

**Configuration**:
```yaml
uses: actions/upload-artifact@v4
with:
  name: production-db-backup-123
  path: prod_backup_*.sql
  retention-days: 30
```

**Access artifacts**:
1. Go to **Actions** → Select workflow run
2. Scroll down to **Artifacts** section
3. Click to download backup SQL file

**Use cases**:
- Emergency restore from specific date
- Manual inspection of backup
- Restore to local development database

---

## Manual Execution

### When to Run Manually

Run the workflow manually when you need to:
- Refresh staging data immediately (don't wait for Sunday)
- Test the backup process
- Restore production data after testing destructive changes in staging
- Prepare staging for a demo or presentation

### How to Trigger Manually

**Step-by-step**:

1. **Go to GitHub Repository**

2. **Navigate to Actions**:
   ```
   Actions tab → Weekly DB Backup - Using DigitalOcean Backups
   ```

3. **Click "Run workflow"** button (top-right)

4. **Select branch**:
   - Choose `main` or `development` (doesn't matter for this workflow)

5. **Click "Run workflow"** to confirm

6. **Monitor progress**:
   - Click on the running workflow
   - Watch each step in real-time
   - Check for errors or warnings

### What Branch to Select?

**Answer**: Any branch works!

This workflow doesn't use code from the repository, so the branch selection doesn't affect the outcome. It only:
- Connects to databases
- Backs up production
- Restores to staging

**Recommendation**: Use `main` for consistency.

---

## Monitoring and Verification

### During Workflow Execution

**Real-time monitoring**:
1. Go to **Actions** tab
2. Click on the running workflow
3. Watch live logs as each step executes

**What to watch for**:
- ✅ Green checkmarks indicate success
- ❌ Red X indicates failure
- ⚠️ Yellow indicates warnings (may still succeed)

### After Workflow Completion

**Check the logs**:
1. Click on completed workflow run
2. Review each step's output
3. Look for:
   - Backup file size
   - Number of tables restored
   - Verification results

**Example successful output**:
```
✅ Backup created: prod_backup_20250105_020000.sql (Size: 125M)
✅ Staging database cleaned
✅ Backup restored to staging
📊 Tables in staging: 47
✅ Staging database verified successfully
```

### Verify Staging Database Manually

**Connect to staging database**:
```bash
# Using psql
psql "postgresql://user:pass@staging-host:25060/staging_db?sslmode=require"

# Check tables
\dt

# Check row counts
SELECT
  schemaname,
  tablename,
  n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

# Check last update time (if you have timestamps)
SELECT MAX(updated_at) FROM your_table_name;
```

**Verify in Django application**:
```bash
# SSH to staging server
ssh django@staging-server

# Activate Django environment
cd /home/django/ProjectMeats/backend
source venv/bin/activate

# Check database
python manage.py dbshell

# Or use Django shell
python manage.py shell
>>> from your_app.models import YourModel
>>> YourModel.objects.count()
>>> YourModel.objects.latest('created_at')
```

### Email Notifications (Optional)

To get email notifications when the workflow runs, you can:

1. **GitHub's built-in notifications**:
   - Go to repository **Settings** → **Notifications**
   - Enable "Actions" notifications

2. **Add email step to workflow** (custom):
   ```yaml
   - name: Send Email Notification
     if: failure()
     uses: dawidd6/action-send-mail@v3
     with:
       server_address: smtp.gmail.com
       server_port: 465
       username: ${{ secrets.EMAIL_USERNAME }}
       password: ${{ secrets.EMAIL_PASSWORD }}
       subject: Database Backup Failed
       body: The weekly database backup failed. Check GitHub Actions for details.
       to: admin@yourdomain.com
   ```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Cluster not found" Error

**Error message**:
```
Error: GET https://api.digitalocean.com/v2/databases/[id]/backups: 404
cluster not found
```

**Causes**:
- Wrong cluster ID
- Invalid API token
- Token doesn't have database permissions

**Solutions**:
1. Verify cluster ID is correct (UUID format: `3dd4f852-539e-45c2-b3a1-7649432bb1c4`)
2. Regenerate API token with **Read** and **Write** permissions
3. Update `DO_API_TOKEN` secret in GitHub
4. Verify token locally:
   ```bash
   export DO_TOKEN="your-token-here"
   curl -X GET \
     -H "Authorization: Bearer $DO_TOKEN" \
     "https://api.digitalocean.com/v2/databases"
   ```

---

#### Issue 2: PostgreSQL Version Mismatch

**Error message**:
```
pg_dump: error: aborting because of server version mismatch
pg_dump: detail: server version: 17.6; pg_dump version: 16.10
```

**Cause**: Client tools version doesn't match database server version

**Solution**: Already fixed in workflow! It explicitly uses PostgreSQL 17 client.

If you still see this:
1. Check workflow is using latest version
2. Verify explicit paths are used: `/usr/lib/postgresql/17/bin/pg_dump`

---

#### Issue 3: Connection Timeout

**Error message**:
```
psql: error: connection to server at "host" (IP), port 25060 failed: timeout
```

**Causes**:
- Database firewall blocking GitHub Actions IP
- Wrong connection string
- Database is down

**Solutions**:
1. **Check DigitalOcean Trusted Sources**:
   - Go to Database → Settings → Trusted Sources
   - Add "All IPv4" temporarily to test (not recommended for production)
   - Or add GitHub Actions IP ranges

2. **Verify connection string**:
   - Check for typos in `PRODUCTION_DB_URL` or `STAGING_DB_URL`
   - Ensure `?sslmode=require` is included

3. **Test connection locally**:
   ```bash
   psql "your-connection-string-here"
   ```

---

#### Issue 4: Authentication Failed

**Error message**:
```
psql: error: FATAL: password authentication failed for user "doadmin"
```

**Causes**:
- Wrong password in connection string
- Password was reset in DigitalOcean

**Solutions**:
1. Get fresh connection string from DigitalOcean Dashboard
2. Update `PRODUCTION_DB_URL` and `STAGING_DB_URL` secrets
3. Ensure special characters in password are properly URL-encoded

---

#### Issue 5: Insufficient Permissions

**Error message**:
```
ERROR: permission denied to create database
```

**Causes**:
- Database user doesn't have required permissions
- Using read-only user for restore

**Solutions**:
1. Ensure connection string uses admin user (`doadmin`)
2. Check user has CREATE and DROP permissions
3. For DigitalOcean managed databases, use the default admin user

---

#### Issue 6: Disk Space Issues

**Error message**:
```
No space left on device
```

**Cause**: GitHub Actions runner ran out of disk space during backup

**Solutions**:
1. Large databases may need optimization
2. Add cleanup step before backup:
   ```bash
   df -h  # Check available space
   docker system prune -af  # Clean up Docker
   ```

---

#### Issue 7: Backup Taking Too Long

**Symptom**: Workflow times out or runs very slowly

**Causes**:
- Very large database
- Slow network connection
- Database under heavy load

**Solutions**:
1. Check database size in DigitalOcean Dashboard
2. Run backup during off-peak hours (already scheduled for 2 AM)
3. Consider compressing backup:
   ```bash
   pg_dump "$PROD_DB_URL" | gzip > backup.sql.gz
   ```
4. Increase workflow timeout:
   ```yaml
   jobs:
     restore-from-do-backup:
       timeout-minutes: 60  # Default is 30
   ```

---

#### Issue 8: Staging and Production Use Same Database

**Symptom**: Production data gets deleted when cleaning staging

**This is CRITICAL!**: You'll lose production data!

**Immediate action**:
1. **STOP** running the workflow
2. Create separate staging database:
   - **Option A**: New database cluster (recommended)
   - **Option B**: New database on same cluster
     ```sql
     CREATE DATABASE staging_db;
     ```
3. Update `STAGING_DB_URL` secret with new connection string
4. Verify they're different:
   ```bash
   echo "$PRODUCTION_DB_URL"
   echo "$STAGING_DB_URL"
   # These MUST be different!
   ```

---

### Debug Mode

To enable more verbose output, add debug steps to the workflow:

```yaml
- name: Debug Database Connections
  run: |
    echo "Testing production connection..."
    /usr/lib/postgresql/17/bin/psql "$PRODUCTION_DB_URL" -c "\l"

    echo "Testing staging connection..."
    /usr/lib/postgresql/17/bin/psql "$STAGING_DB_URL" -c "\l"

    echo "Checking database sizes..."
    /usr/lib/postgresql/17/bin/psql "$PRODUCTION_DB_URL" -c \
      "SELECT pg_size_pretty(pg_database_size(current_database()));"
```

---

## Best Practices

### Security

1. **Protect Secrets**:
   - ✅ Store all credentials in GitHub Secrets
   - ❌ Never commit passwords or connection strings to code
   - ✅ Use environment-specific secrets

2. **API Token Permissions**:
   - ✅ Only grant necessary permissions (database read/write)
   - ✅ Rotate tokens periodically (every 90 days)
   - ✅ Use token expiration when possible

3. **Database Access**:
   - ✅ Use SSL/TLS connections (`sslmode=require`)
   - ✅ Limit database user permissions
   - ✅ Configure DigitalOcean Trusted Sources

4. **Backup Security**:
   - ✅ Backups in GitHub Artifacts are private
   - ✅ Only accessible to repository collaborators
   - ✅ Automatically deleted after 30 days

### Data Management

1. **Separate Environments**:
   - ✅ Always use different databases for production and staging
   - ✅ Never point both to the same database
   - ✅ Test connection strings before enabling workflow

2. **Backup Retention**:
   - ✅ GitHub artifacts: 30 days (configurable)
   - ✅ DigitalOcean backups: Automatic daily backups
   - ✅ Download important backups for long-term storage

3. **Data Sanitization** (Optional):
   - Consider sanitizing sensitive data in staging:
     ```sql
     -- After restore, anonymize user emails
     UPDATE users SET email = CONCAT('user', id, '@example.com');

     -- Clear sensitive fields
     UPDATE users SET phone_number = NULL;
     ```

### Workflow Optimization

1. **Schedule Timing**:
   - ✅ Run during off-peak hours (current: 2 AM UTC Sunday)
   - ✅ Avoid business hours to minimize impact
   - ✅ Consider database size when scheduling

2. **Monitoring**:
   - ✅ Check workflow results weekly
   - ✅ Review logs for warnings
   - ✅ Monitor backup file sizes for trends

3. **Testing**:
   - ✅ Test workflow manually after setup
   - ✅ Verify staging data after first run
   - ✅ Confirm applications work with restored data

### Disaster Recovery

1. **Backup Verification**:
   - ✅ Periodically test restoring backups
   - ✅ Verify data integrity after restore
   - ✅ Keep multiple backup copies

2. **Rollback Plan**:
   - Know how to restore staging from DigitalOcean's managed backups
   - Document recovery procedures
   - Test rollback process

3. **Emergency Access**:
   - Keep database credentials in secure location (not just GitHub)
   - Document manual backup/restore procedures
   - Have alternative access methods

### Documentation

1. **Keep Updated**:
   - ✅ Document any workflow modifications
   - ✅ Update secrets when credentials change
   - ✅ Note any special configuration requirements

2. **Team Communication**:
   - ✅ Notify team when backup runs
   - ✅ Inform developers of staging data refresh schedule
   - ✅ Document any data sanitization applied

3. **Change Log**:
   - Track workflow changes
   - Note when secrets are updated
   - Record any failures and resolutions

---

## Summary

### What This Workflow Does
✅ Automatically backs up production database weekly
✅ Restores production data to staging environment
✅ Verifies successful restoration
✅ Saves backup artifacts for 30 days
✅ Can be triggered manually anytime
✅ Uses DigitalOcean managed database features
✅ Ensures staging has realistic test data

### What This Workflow Does NOT Do
❌ Backup staging database (only production)
❌ Modify production database (read-only access)
❌ Automatically restore to production
❌ Send email notifications (can be added)
❌ Compress backups (uses plain SQL)
❌ Sanitize sensitive data (needs manual configuration)

### Quick Reference

| Item | Value |
|------|-------|
| **Workflow Name** | Weekly DB Backup - Using DigitalOcean Backups |
| **Schedule** | Every Sunday at 2:00 AM UTC |
| **File Location** | `.github/workflows/db-backup-restore-do.yml` |
| **Runtime** | ~5-15 minutes (depends on database size) |
| **Artifact Retention** | 30 days |
| **Required Secrets** | 4 (DO_API_TOKEN, PROD_DB_CLUSTER_ID, PRODUCTION_DB_URL, STAGING_DB_URL) |
| **PostgreSQL Version** | 17 |

---

**Last Updated**: January 2025
**Maintained By**: Development Team
**Workflow Version**: 1.0
**PostgreSQL Version**: 17.6
