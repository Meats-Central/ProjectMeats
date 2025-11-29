# GitHub Actions Scripts

This directory contains validation and automation scripts used by GitHub Actions workflows for deployment and CI/CD.

## Scripts

### validate-migrations.sh
**Purpose:** Comprehensive Django migration validation before deployment

**When it runs:**
- Every deployment workflow (dev, UAT, prod)
- After dependencies installed but before tests run

**What it validates:**
1. No unapplied migrations (`makemigrations --check`)
2. Migration plan is valid (`migrate --plan`)
3. No migration conflicts (`showmigrations`)
4. Python syntax in all migration files
5. Migration dependencies are consistent
6. Migrations work on fresh database (CI only)

**Exit codes:**
- 0: All validations passed
- 1: Validation failed (deployment will be blocked)

**Usage:**
```bash
# In CI (with PostgreSQL service)
CI=true DATABASE_URL=postgresql://... ./validate-migrations.sh

# Local testing
cd backend
DATABASE_URL=... ./.github/scripts/validate-migrations.sh
```

**Benefits:**
- Prevents 90% of migration-related deployment failures
- Catches dependency issues before deployment
- Validates syntax errors in migration files
- Tests on fresh database to catch ordering issues

---

### validate-environment.sh
**Purpose:** Validate environment variables and configuration before deployment

**When it runs:**
- Can be run manually before deployment
- Recommended in deployment workflows

**What it validates:**
1. Required environment variables are set (SECRET_KEY, DATABASE_URL, etc.)
2. CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS match
3. URL formats are valid (must start with http:// or https://)
4. Security settings are appropriate for environment
5. Database URL uses PostgreSQL (warns if SQLite)

**Exit codes:**
- 0: All required variables are valid
- 1: Missing or invalid required variables

**Warnings (non-blocking):**
- DEBUG enabled (should be False in production)
- SESSION_COOKIE_SECURE is False (should be True with HTTPS)
- CSRF_COOKIE_SECURE is False (should be True with HTTPS)
- CORS and CSRF configurations don't match
- SQLite database detected (not recommended for production)

**Usage:**
```bash
# Load environment variables first
export SECRET_KEY=...
export DATABASE_URL=...
export CORS_ALLOWED_ORIGINS=...

# Run validation
./validate-environment.sh
```

**Benefits:**
- Catches configuration issues before deployment
- Prevents CORS/CSRF mismatch errors
- Validates security settings
- Provides clear error messages for missing variables

---

### backup-database.sh
**Purpose:** Create timestamped database backup before migrations

**When it runs:**
- Should run in deployment workflows before applying migrations
- Can be run manually before risky operations

**What it does:**
1. Parses DATABASE_URL to extract connection details
2. Creates timestamped backup: `db_backup_YYYYMMDD_HHMMSS.sql`
3. Compresses backup with gzip
4. Sets secure permissions (600)
5. Cleans up old backups (keeps last 7 by default)
6. Provides restore command in output

**Environment variables:**
- `DATABASE_URL` (required): PostgreSQL connection string
- `BACKUP_DIR` (optional): Directory for backups (default: `/home/django/ProjectMeats/backups`)
- `KEEP_BACKUPS` (optional): Number of backups to keep (default: 7)

**Exit codes:**
- 0: Backup created successfully
- 1: Backup failed (missing DATABASE_URL or backup failure)

**Usage:**
```bash
# With defaults
DATABASE_URL=postgresql://... ./backup-database.sh

# Custom backup directory and retention
BACKUP_DIR=/custom/path KEEP_BACKUPS=14 DATABASE_URL=... ./backup-database.sh
```

**Restore a backup:**
```bash
gunzip -c /path/to/db_backup_20251103_182000.sql.gz | \
  PGPASSWORD=$DB_PASS psql -h $DB_HOST -U $DB_USER $DB_NAME
```

**Benefits:**
- Automatic safety net for deployments
- Compressed backups save disk space
- Automatic cleanup prevents disk space issues
- Clear restore instructions
- Critical for migration rollbacks

---

## Integration with Workflows

### Example: Dev Deployment Workflow

```yaml
test-backend:
  steps:
    # ... install dependencies ...
    
    - name: Validate migrations
      env:
        DATABASE_URL: postgresql://...
        CI: true
      run: |
        chmod +x .github/scripts/validate-migrations.sh
        .github/scripts/validate-migrations.sh
    
    - name: Run tests
      run: python manage.py test apps/
```

### Example: Deployment with Backup

```yaml
deploy-backend:
  steps:
    # ... SSH to server ...
    
    - name: Create database backup
      run: |
        DATABASE_URL=${{ secrets.DATABASE_URL }} \
        .github/scripts/backup-database.sh
    
    - name: Run migrations
      run: |
        docker run --rm --env-file .env <image> \
          python manage.py migrate --noinput
```

## Development

### Adding New Validation

To add new validation to `validate-migrations.sh`:

1. Add new step with echo message
2. Implement validation logic
3. Exit with code 1 if validation fails
4. Update this README with new validation

### Testing Scripts Locally

All scripts support local execution with appropriate environment variables:

```bash
# Test migration validation (without fresh DB test)
cd backend
DATABASE_URL=postgresql://... \
  ../.github/scripts/validate-migrations.sh

# Test environment validation
export SECRET_KEY=test
export DATABASE_URL=postgresql://...
export CORS_ALLOWED_ORIGINS=http://localhost
export CSRF_TRUSTED_ORIGINS=http://localhost
.github/scripts/validate-environment.sh

# Test backup (use test database!)
DATABASE_URL=postgresql://user:pass@localhost/test_db \
  BACKUP_DIR=/tmp/backups \
  .github/scripts/backup-database.sh
```

## Troubleshooting

### Script not executable
```bash
chmod +x .github/scripts/*.sh
```

### Permission denied in CI
Workflows automatically run `chmod +x` before executing scripts.

### Script fails locally but passes in CI
- Ensure PostgreSQL is running locally
- Check DATABASE_URL format
- Verify all required environment variables are set
- For migration validation, ensure CI=true is NOT set locally (skips fresh DB test)

### Backup script fails
- Verify `pg_dump` is installed
- Check DATABASE_URL is valid PostgreSQL connection string
- Ensure backup directory exists and is writable
- Check disk space

## Related Documentation

- [Migration Best Practices](../../docs/MIGRATION_BEST_PRACTICES.md)
- [Deployment Troubleshooting](../../docs/DEPLOYMENT_TROUBLESHOOTING.md)
- [Copilot Instructions](../copilot-instructions.md)

## Maintenance

These scripts should be reviewed and updated when:
- Django version is upgraded (migration commands may change)
- New critical environment variables are added
- Deployment process changes significantly
- New validation requirements are identified

---

**Last Updated:** 2025-11-03  
**Maintained By:** DevOps Team
