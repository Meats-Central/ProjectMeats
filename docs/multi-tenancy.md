# Multi-Tenancy Guide

## Overview

ProjectMeats implements a multi-tenancy architecture that allows multiple organizations (tenants) to use the same application instance while maintaining data isolation. This guide covers the multi-tenancy setup, configuration, and usage.

## Architecture

The multi-tenancy implementation uses a **shared database, shared schema** approach with tenant-based data isolation:

- **Tenant Model**: Stores organization information and configuration
- **TenantUser Model**: Manages user-to-tenant associations with role-based access
- **Tenant Filtering**: Middleware and querysets automatically filter data by tenant
- **Superuser Access**: Superusers have cross-tenant capabilities

## Components

### Models

#### Tenant
- **Purpose**: Represents an organization/tenant in the system
- **Key Fields**:
  - `id`: UUID primary key
  - `name`: Organization name
  - `slug`: URL-friendly identifier (unique)
  - `contact_email`: Primary contact email
  - `is_active`: Active status
  - `is_trial`: Trial status
  - `settings`: JSON field for tenant-specific configuration

#### TenantUser
- **Purpose**: Links users to tenants with specific roles
- **Key Fields**:
  - `tenant`: Foreign key to Tenant
  - `user`: Foreign key to User
  - `role`: User role within tenant (owner, admin, manager, user, readonly)
  - `is_active`: Active status for this association

### Roles

The system supports five user roles per tenant:

1. **Owner**: Full control over tenant and all resources
2. **Admin**: Administrative access, can manage users
3. **Manager**: Can manage resources but not users
4. **User**: Standard user access
5. **Readonly**: Read-only access to resources

### Superuser Capabilities

Superusers have special privileges:
- Can access data across all tenants
- Bypass tenant filtering when `request.user.is_superuser` is True
- Automatically linked to the root tenant

## Automated Setup

### Management Command: `create_super_tenant`

The `create_super_tenant` management command automates the creation of:
1. A superuser account
2. A default "root" tenant
3. The association between the superuser and root tenant

#### Usage

```bash
# Run manually
python manage.py create_super_tenant

# Run during deployment (automatically called in CI/CD)
```

#### Configuration

The command uses environment variables for credentials:

- `SUPERUSER_EMAIL`: Email address for the superuser (default: `admin@meatscentral.com`)
- `SUPERUSER_PASSWORD`: Password for the superuser (default: `default_secure_pass`)

⚠️ **Security Note**: Always override default credentials in production environments!

#### Environment Variables

##### Development (`config/environments/development.env`)
```bash
SUPERUSER_EMAIL=admin@meatscentral.com
SUPERUSER_PASSWORD=DevAdmin123!SecurePass
```

##### Staging (`config/environments/staging.env`)
```bash
SUPERUSER_EMAIL=${STAGING_SUPERUSER_EMAIL}
SUPERUSER_PASSWORD=${STAGING_SUPERUSER_PASSWORD}
```

##### Production (`config/environments/production.env`)
```bash
SUPERUSER_EMAIL=${PRODUCTION_SUPERUSER_EMAIL}
SUPERUSER_PASSWORD=${PRODUCTION_SUPERUSER_PASSWORD}
```

**Important**: Use secure secret management for staging and production:
- Use GitHub Secrets for CI/CD pipelines
- Use environment-specific secret managers (AWS Secrets Manager, Azure Key Vault, etc.)
- Never commit actual passwords to version control

### Idempotency

The `create_super_tenant` command is idempotent:
- ✅ Safe to run multiple times
- ✅ Won't create duplicates
- ✅ Won't overwrite existing data
- ✅ Will link existing users to tenants if needed

## Deployment Integration

The command is automatically executed during deployment in the unified workflow:

```yaml
- Run database migrations
- Create superuser and root tenant  # ← Automated
- Collect static files
- Run Django checks
```

This happens in all environments:
- Development
- Staging (UAT)
- Production

## API Usage

### Tenant Management

#### List Tenants
```http
GET /api/v1/tenants/
Authorization: Token <your-token>
```

#### Create Tenant
```http
POST /api/v1/tenants/
Authorization: Token <your-token>
Content-Type: application/json

{
  "name": "New Organization",
  "slug": "new-org",
  "contact_email": "admin@neworg.com",
  "is_trial": true
}
```

### User-Tenant Association

#### Add User to Tenant
```http
POST /api/v1/tenants/{tenant_id}/add_user/
Authorization: Token <your-token>
Content-Type: application/json

{
  "user": 2,
  "role": "admin"
}
```

#### List Tenant Users
```http
GET /api/v1/tenant-users/
Authorization: Token <your-token>
```

## Security Best Practices

### Password Requirements

1. **Development**: Use strong passwords even in dev
2. **Staging**: Use randomly generated passwords stored in GitHub Secrets
3. **Production**: Use cryptographically secure passwords with:
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, and symbols
   - Stored in secure secret management system

### Secret Management

```bash
# Generate secure password (example)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use Django's secret key generator
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Environment Setup

For staging and production, set these as GitHub Secrets or in your environment:

```bash
# Staging
STAGING_SUPERUSER_EMAIL=admin@staging.meatscentral.com
STAGING_SUPERUSER_PASSWORD=<secure-random-password>

# Production
PRODUCTION_SUPERUSER_EMAIL=admin@meatscentral.com
PRODUCTION_SUPERUSER_PASSWORD=<secure-random-password>
```

## Testing

Run the management command tests:

```bash
# Run all tenant tests
python manage.py test apps.tenants

# Run only management command tests
python manage.py test apps.tenants.tests_management_commands

# Run with coverage
pytest apps/tenants/tests_management_commands.py --cov=apps.core.management.commands
```

## Troubleshooting

### Command Not Found

If `create_super_tenant` command is not found:

```bash
# Verify the command exists
python manage.py help | grep create_super_tenant

# Check directory structure
ls -la apps/core/management/commands/
```

### Superuser Already Exists

The command will display a warning but continue:
```
⚠️  Superuser already exists: admin@meatscentral.com
```

This is expected behavior and not an error.

### Permission Denied

Ensure the user running the command has:
- Database write permissions
- Proper Django settings configured
- Virtual environment activated

### Database Not Migrated

Run migrations before the command:
```bash
python manage.py migrate
python manage.py create_super_tenant
```

## Future Enhancements

Planned improvements for multi-tenancy:

1. **Tenant Isolation Middleware**: Automatic request-level tenant detection
2. **Tenant-Scoped Data**: Enhanced queryset filtering across all models
3. **Tenant Switching UI**: Admin interface for switching between tenants
4. **Subdomain Routing**: Route requests based on subdomain to tenant
5. **Tenant Analytics**: Dashboard for tenant usage metrics

## References

- [Django Multi-Tenancy Best Practices](https://docs.djangoproject.com/)
- [ProjectMeats Backend Architecture](BACKEND_ARCHITECTURE.md)
- [Environment Configuration Guide](ENVIRONMENT_GUIDE.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)
