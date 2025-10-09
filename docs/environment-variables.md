# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in the ProjectMeats application.

## Superuser Configuration

Superuser credentials are configured using environment-specific variables to support dynamic username, email, and password management across different deployment environments.

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

Creates superuser, root tenant, and links them together. Uses legacy environment variables for backward compatibility.

| Variable | Description |
|----------|-------------|
| `SUPERUSER_EMAIL` | Email for tenant creation |
| `SUPERUSER_PASSWORD` | Password for tenant creation |
| `SUPERUSER_USERNAME` | Username for tenant creation |

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
