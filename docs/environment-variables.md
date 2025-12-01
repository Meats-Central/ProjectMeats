# Environment Variables Reference

**Last Updated**: November 2025

This document provides a comprehensive reference for all environment variables used in the ProjectMeats application.

---

## 🔐 Secure Handling with GitHub Secrets

### Why Use GitHub Secrets?

All sensitive environment variables for CI/CD should be stored in GitHub Secrets, not in code or configuration files:

- **Security**: Encrypted at rest, only exposed during workflow runs
- **Audit trail**: Access and changes are logged
- **Separation**: Different secrets per environment (dev/uat/prod)

### Setting Up GitHub Secrets

1. **Repository Secrets** (shared across all workflows):
   - Go to: Settings → Secrets and variables → Actions → Repository secrets
   - Add: `SSH_PASSWORD`, `GIT_TOKEN`, etc.

2. **Environment Secrets** (environment-specific):
   - Go to: Settings → Environments → [environment name]
   - Add secrets specific to that environment

### Example Workflow Usage

```yaml
# In .github/workflows/deploy.yml
- name: Deploy
  env:
    SECRET_KEY: ${{ secrets.STAGING_SECRET_KEY }}
    DB_PASSWORD: ${{ secrets.STAGING_DB_PASSWORD }}
  run: ./deploy.sh
```

---

## Database Configuration

Database configuration uses environment-specific variables to support different database backends across deployment environments.

### Database Engine Selection

| Variable | Description | Values | Default |
|----------|-------------|--------|---------|
| `DB_ENGINE` | Database backend engine | `django.db.backends.postgresql` | PostgreSQL (recommended) |

> **Note**: SQLite (`django.db.backends.sqlite3`) is **deprecated**. Use PostgreSQL for all environments.

### PostgreSQL Configuration

Required when `DB_ENGINE=django.db.backends.postgresql`:

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `DB_NAME` | Database name | `projectmeats_dev` | Yes |
| `DB_USER` | Database user | `postgres` | Yes |
| `DB_PASSWORD` | Database password | `secure_password` | Yes |
| `DB_HOST` | Database host | `localhost` or `db.example.com` | Yes |
| `DB_PORT` | Database port | `5432` | No (defaults to 5432) |

### Environment-Specific Database Configuration

#### Development Environment

**PostgreSQL (Recommended):**
```bash
# config/environments/development.env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=projectmeats_dev
DB_USER=postgres
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=5432
```

**⚠️ SQLite Fallback (DEPRECATED):**
```bash
# config/environments/development.env
DB_ENGINE=django.db.backends.sqlite3
```

**GitHub Secrets (for deployment):**
- Navigate to repository Settings → Environments → `dev-backend`
- Add secrets:
  - `DEVELOPMENT_DB_ENGINE` (e.g., `django.db.backends.postgresql`)
  - `DEVELOPMENT_DB_NAME`
  - `DEVELOPMENT_DB_USER`
  - `DEVELOPMENT_DB_PASSWORD`
  - `DEVELOPMENT_DB_HOST`
  - `DEVELOPMENT_DB_PORT`

#### Staging/UAT Environment

**PostgreSQL (Required):**
```bash
# config/environments/staging.env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=projectmeats_staging
DB_USER=postgres
DB_PASSWORD=change_me_in_secrets
DB_HOST=staging-db.example.com
DB_PORT=5432
```

**GitHub Secrets:**
- Navigate to repository Settings → Environments → `uat2-backend`
- Add secrets:
  - `STAGING_DB_ENGINE`
  - `STAGING_DB_NAME`
  - `STAGING_DB_USER`
  - `STAGING_DB_PASSWORD`
  - `STAGING_DB_HOST`
  - `STAGING_DB_PORT`

#### Production Environment

**PostgreSQL (Required):**
```bash
# config/environments/production.env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=projectmeats_prod
DB_USER=postgres
DB_PASSWORD=change_me_in_secrets
DB_HOST=prod-db.example.com
DB_PORT=5432
```

**GitHub Secrets:**
- Navigate to repository Settings → Environments → `prod2-backend`
- Add secrets:
  - `PRODUCTION_DB_ENGINE`
  - `PRODUCTION_DB_NAME`
  - `PRODUCTION_DB_USER`
  - `PRODUCTION_DB_PASSWORD`
  - `PRODUCTION_DB_HOST`
  - `PRODUCTION_DB_PORT`

### Database Security Best Practices

1. **Strong Passwords**: Use cryptographically secure passwords (minimum 16 characters)
2. **Connection Encryption**: Enable SSL/TLS for PostgreSQL connections in production
3. **Least Privilege**: Grant only necessary database permissions to application user
4. **Network Isolation**: Restrict database access to application servers only
5. **Regular Backups**: Implement automated backup and restoration procedures
6. **Password Rotation**: Rotate database credentials regularly (recommended: every 90 days)

### Database Troubleshooting

#### Error: "Database connection failed"

**Cause:** Incorrect database credentials or unreachable database host.

**Solution:**
1. Verify `DB_HOST` is accessible from deployment server
2. Check `DB_USER` and `DB_PASSWORD` are correct
3. Ensure database server is running and accepting connections
4. Verify firewall rules allow connection on `DB_PORT`

#### Error: "Readonly database" or "attempt to write a readonly database"

**Cause:** Database file permissions (SQLite) or database user lacks write permissions (PostgreSQL).

**Solution for SQLite (DEPRECATED):**
```bash
# Fix file permissions
sudo chown $USER:$USER db.sqlite3
chmod 664 db.sqlite3
```

**Solution for PostgreSQL:**
1. Verify `DB_USER` has `CREATE`, `INSERT`, `UPDATE`, `DELETE` permissions
2. Check database user grants: `GRANT ALL PRIVILEGES ON DATABASE dbname TO username;`
3. Ensure database is not in read-only mode

#### Error: "Missing database environment variables"

**Cause:** Required PostgreSQL variables not set.

**Solution:**
- Development: Set variables in `config/environments/development.env`
- Staging/Production: Ensure all `*_DB_*` secrets are configured in GitHub Environments

### Database Migration Commands

```bash
# Check database connectivity
python manage.py check --database default

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations
```

## Superuser Configuration

Superuser credentials are configured using environment-specific variables to support dynamic username, email, and password management across different deployment environments.

**Both the `setup_superuser` and `create_super_tenant` commands support environment-specific variables**, ensuring consistent credential management across all deployment operations.

### Development Environment

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DEVELOPMENT_SUPERUSER_USERNAME` | Admin username for development | `admin` | No |
| `DEVELOPMENT_SUPERUSER_EMAIL` | Admin email for development | `admin@meatscentral.com` | No |
| `DEVELOPMENT_SUPERUSER_PASSWORD` | Admin password for development | N/A | Yes |

**Example Configuration:**
```bash
# config/environments/development.env
DEVELOPMENT_SUPERUSER_USERNAME=admin
DEVELOPMENT_SUPERUSER_EMAIL=admin@meatscentral.com
DEVELOPMENT_SUPERUSER_PASSWORD=DevAdmin123!SecurePass
```

### Staging/UAT Environment

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `STAGING_SUPERUSER_USERNAME` | Admin username for staging | None | Yes |
| `STAGING_SUPERUSER_EMAIL` | Admin email for staging | None | Yes |
| `STAGING_SUPERUSER_PASSWORD` | Admin password for staging | None | Yes |

**Example Configuration:**
```bash
# config/environments/staging.env
# Set these in GitHub Secrets for uat2-backend environment
STAGING_SUPERUSER_USERNAME=change_me_in_secrets
STAGING_SUPERUSER_EMAIL=change_me_in_secrets
STAGING_SUPERUSER_PASSWORD=change_me_in_secrets
```

**GitHub Secrets Setup:**
- Navigate to repository Settings → Environments → `uat2-backend`
- Add secrets:
  - `STAGING_SUPERUSER_USERNAME`
  - `STAGING_SUPERUSER_EMAIL`
  - `STAGING_SUPERUSER_PASSWORD`

### Production Environment

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PRODUCTION_SUPERUSER_USERNAME` | Admin username for production | None | Yes |
| `PRODUCTION_SUPERUSER_EMAIL` | Admin email for production | None | Yes |
| `PRODUCTION_SUPERUSER_PASSWORD` | Admin password for production | None | Yes |

**Example Configuration:**
```bash
# config/environments/production.env
# Set these in GitHub Secrets for prod2-backend environment
PRODUCTION_SUPERUSER_USERNAME=change_me_in_secrets
PRODUCTION_SUPERUSER_EMAIL=change_me_in_secrets
PRODUCTION_SUPERUSER_PASSWORD=change_me_in_secrets
```

**GitHub Secrets Setup:**
- Navigate to repository Settings → Environments → `prod2-backend`
- Add secrets:
  - `PRODUCTION_SUPERUSER_USERNAME`
  - `PRODUCTION_SUPERUSER_EMAIL`
  - `PRODUCTION_SUPERUSER_PASSWORD`

## Environment Detection

The `setup_superuser` management command automatically detects the environment using the `DJANGO_ENV` variable:

| DJANGO_ENV Value | Variables Used |
|------------------|----------------|
| `development` (default) | `DEVELOPMENT_SUPERUSER_*` |
| `staging` or `uat` | `STAGING_SUPERUSER_*` |
| `production` | `PRODUCTION_SUPERUSER_*` |

## Security Best Practices

### Password Requirements

1. **Development**: Use strong passwords even in development (minimum 12 characters)
2. **Staging**: Use randomly generated passwords (minimum 16 characters)
3. **Production**: Use cryptographically secure passwords (minimum 20 characters)

### Secret Management

- **Never commit secrets to version control**
- Use GitHub Secrets for CI/CD pipelines
- Use environment-specific secret managers in production (AWS Secrets Manager, Azure Key Vault, etc.)
- Rotate passwords regularly (recommended: every 90 days)

### Password Generation

```bash
# Generate a secure random password (Python)
python -c "import secrets; print(secrets.token_urlsafe(24))"

# Generate a secure random password (OpenSSL)
openssl rand -base64 24
```

## Command Usage

### setup_superuser Command

Syncs superuser credentials from environment variables.

**Local Development:**
```bash
# Using Makefile (sets DJANGO_ENV=development automatically)
make sync-superuser

# Direct command
cd backend && DJANGO_ENV=development python manage.py setup_superuser
```

**Deployment (Automatic):**
The command runs automatically during deployment via GitHub Actions workflow in all environments.

### Behavior by Environment

**Development:**
- Loads `DEVELOPMENT_SUPERUSER_*` variables
- Uses defaults if username/email not provided
- Raises error if password not provided

**Staging/Production:**
- Loads environment-specific variables (`STAGING_*` or `PRODUCTION_*`)
- **No defaults** - all fields required
- Raises `ValueError` if any required field is missing

## Troubleshooting

### Error: "Superuser username is required"

**Cause:** The environment-specific username variable is not set.

**Solution:**
- Development: Set `DEVELOPMENT_SUPERUSER_USERNAME` or use default
- Staging: Ensure `STAGING_SUPERUSER_USERNAME` is in GitHub Secrets
- Production: Ensure `PRODUCTION_SUPERUSER_USERNAME` is in GitHub Secrets

### Error: "Superuser email is required"

**Cause:** The environment-specific email variable is not set.

**Solution:**
- Development: Set `DEVELOPMENT_SUPERUSER_EMAIL` or use default
- Staging: Ensure `STAGING_SUPERUSER_EMAIL` is in GitHub Secrets
- Production: Ensure `PRODUCTION_SUPERUSER_EMAIL` is in GitHub Secrets

### Error: "Superuser password is required"

**Cause:** The environment-specific password variable is not set.

**Solution:**
- Development: Set `DEVELOPMENT_SUPERUSER_PASSWORD` in `.env`
- Staging: Ensure `STAGING_SUPERUSER_PASSWORD` is in GitHub Secrets
- Production: Ensure `PRODUCTION_SUPERUSER_PASSWORD` is in GitHub Secrets

## Related Commands

### create_super_tenant Command

Creates superuser, root tenant, and links them together. **Now supports environment-specific variables** (as of this update).

#### Environment-Specific Variables (Recommended)

The command automatically detects the environment using `DJANGO_ENV` and loads the appropriate credentials:

| DJANGO_ENV Value | Variables Used |
|------------------|----------------|
| `development` (default) | `DEVELOPMENT_SUPERUSER_*` |
| `staging` or `uat` | `STAGING_SUPERUSER_*` |
| `production` | `PRODUCTION_SUPERUSER_*` |

**Example Usage:**
```bash
# Development
DJANGO_ENV=development \
DEVELOPMENT_SUPERUSER_USERNAME=admin \
DEVELOPMENT_SUPERUSER_EMAIL=admin@meatscentral.com \
DEVELOPMENT_SUPERUSER_PASSWORD=DevPass123! \
python manage.py create_super_tenant

# Staging
DJANGO_ENV=staging \
STAGING_SUPERUSER_USERNAME=stagingadmin \
STAGING_SUPERUSER_EMAIL=admin@staging.example.com \
STAGING_SUPERUSER_PASSWORD=StagePass456! \
python manage.py create_super_tenant

# Production
DJANGO_ENV=production \
PRODUCTION_SUPERUSER_USERNAME=prodadmin \
PRODUCTION_SUPERUSER_EMAIL=admin@example.com \
PRODUCTION_SUPERUSER_PASSWORD=ProdPass789! \
python manage.py create_super_tenant
```

#### Legacy Variables (Backward Compatibility)

For backward compatibility, the command still supports generic variables:

| Variable | Description |
|----------|-------------|
| `SUPERUSER_EMAIL` | Email for tenant creation |
| `SUPERUSER_PASSWORD` | Password for tenant creation |
| `SUPERUSER_USERNAME` | Username for tenant creation |

**Fallback Behavior:**
- If environment-specific variables are not set, the command falls back to generic `SUPERUSER_*` variables
- If neither are set, uses default values (development) or raises error (production/staging)

**Note:** The `create_super_tenant` command runs AFTER `setup_superuser` during deployment to ensure credentials are synced before tenant setup.

## Migration from Legacy Variables

If you're migrating from the legacy `ENVIRONMENT_SUPERUSER_PASSWORD` and `SUPERUSER_*` variables:

**Old Configuration (Deprecated):**
```bash
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@example.com
ENVIRONMENT_SUPERUSER_PASSWORD=password123
```

**New Configuration:**
```bash
# Development
DEVELOPMENT_SUPERUSER_USERNAME=admin
DEVELOPMENT_SUPERUSER_EMAIL=admin@example.com
DEVELOPMENT_SUPERUSER_PASSWORD=password123

# Staging (in GitHub Secrets)
STAGING_SUPERUSER_USERNAME=admin
STAGING_SUPERUSER_EMAIL=admin@staging.example.com
STAGING_SUPERUSER_PASSWORD=<secure-password>

# Production (in GitHub Secrets)
PRODUCTION_SUPERUSER_USERNAME=admin
PRODUCTION_SUPERUSER_EMAIL=admin@example.com
PRODUCTION_SUPERUSER_PASSWORD=<secure-password>
```

## Compliance

This implementation follows:
- **12-Factor App**: Configuration in environment
- **OWASP**: Secure password storage and handling
- **Django Best Practices**: Proper password hashing via `set_password()`
- **GDPR**: No password logging (only usernames for audit trail)

## See Also

- [Multi-Tenancy Guide](./multi-tenancy.md) - Tenant management and superuser setup
- [Deployment Guide](./DEPLOYMENT_GUIDE.md) - Deployment procedures
- [Environment Guide](./ENVIRONMENT_GUIDE.md) - General environment configuration
