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

### Management Command: `setup_superuser`

The `setup_superuser` management command provides password synchronization functionality:
1. Creates a superuser if it doesn't exist
2. **Always syncs password** from environment variable when user exists
3. Designed for deployment automation and password rotation

#### Usage

```bash
# Run manually (requires ENVIRONMENT_SUPERUSER_PASSWORD)
ENVIRONMENT_SUPERUSER_PASSWORD=your_password python manage.py setup_superuser

# Run during deployment (automatically called in CI/CD)
python manage.py setup_superuser

# Makefile command
make sync-superuser
```

#### Key Differences from `create_super_tenant`

| Feature | `create_super_tenant` | `setup_superuser` |
|---------|----------------------|-------------------|
| Creates superuser | ✅ Yes | ✅ Yes |
| Creates tenant | ✅ Yes | ❌ No |
| Links to tenant | ✅ Yes | ❌ No |
| Updates password on existing user | ❌ No (idempotent) | ✅ Yes (always syncs) |
| Purpose | Initial setup | Password rotation/sync |

#### Configuration

The command uses environment variables:

- `SUPERUSER_USERNAME`: Username (default: `admin`)
- `SUPERUSER_EMAIL`: Email address (default: `admin@meatscentral.com`)
- `ENVIRONMENT_SUPERUSER_PASSWORD`: **Required** in production/staging, falls back to `SUPERUSER_PASSWORD` in development

⚠️ **Production/Staging Requirement**: `ENVIRONMENT_SUPERUSER_PASSWORD` must be set or the command will raise a `ValueError`

#### Environment Variables

##### Development (`config/environments/development.env`)
```bash
SUPERUSER_EMAIL=admin@meatscentral.com
SUPERUSER_PASSWORD=DevAdmin123!SecurePass
ENVIRONMENT_SUPERUSER_PASSWORD=DevAdmin123!SecurePass
```

##### Staging (`config/environments/staging.env`)
```bash
SUPERUSER_EMAIL=${STAGING_SUPERUSER_EMAIL}
SUPERUSER_PASSWORD=${STAGING_SUPERUSER_PASSWORD}
ENVIRONMENT_SUPERUSER_PASSWORD=${STAGING_SUPERUSER_PASSWORD}
```

##### Production (`config/environments/production.env`)
```bash
SUPERUSER_EMAIL=${PRODUCTION_SUPERUSER_EMAIL}
SUPERUSER_PASSWORD=${PRODUCTION_SUPERUSER_PASSWORD}
ENVIRONMENT_SUPERUSER_PASSWORD=${PRODUCTION_SUPERUSER_PASSWORD}
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

The `setup_superuser` command behavior:
- ✅ Safe to run multiple times
- ✅ Won't create duplicate users
- ✅ **WILL update password** on every run (by design)
- ✅ Ideal for password rotation scenarios

## Deployment Integration

Both commands are automatically executed during deployment in the unified workflow:

```yaml
- Run database migrations
- Sync superuser password        # ← setup_superuser (NEW)
- Create superuser and root tenant  # ← create_super_tenant
- Collect static files
- Run Django checks
```

**Deployment Order**: `setup_superuser` runs BEFORE `create_super_tenant` to ensure:
1. Password is synced from environment first
2. Tenant setup happens with correct credentials
3. Both commands work together harmoniously

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

### Common Issues and Solutions

#### 1. Superuser Not Created

**Symptoms:**
- Command completes but no superuser exists
- Can't log into Django admin

**Possible Causes and Fixes:**

**a) Argument Mismatch in User Creation**
- **Issue**: Code uses `User.objects.create()` instead of `create_superuser()`
- **Solution**: Update to use `User.objects.create_superuser(username=..., email=..., password=...)`
- **Verification**: Check if password is hashed in database (should start with `pbkdf2_sha256$`)

**b) Missing Environment Variables**
- **Issue**: `SUPERUSER_EMAIL`, `SUPERUSER_PASSWORD`, or `SUPERUSER_USERNAME` not set
- **Solution**: 
  ```bash
  # Development
  export SUPERUSER_USERNAME=admin
  export SUPERUSER_EMAIL=admin@meatscentral.com
  export SUPERUSER_PASSWORD=YourSecurePassword
  
  # Or update config/environments/development.env
  ```
- **Verification**: Run with verbosity to see configuration:
  ```bash
  python manage.py create_super_tenant --verbosity 2
  ```

**c) Silent Failures**
- **Issue**: Exceptions caught but not displayed
- **Solution**: Run command with `--verbosity 2` for detailed output
- **Example**:
  ```bash
  python manage.py create_super_tenant --verbosity 2
  ```
  
#### 2. Tenant Model Import Error

**Symptoms:**
- Error: "Tenant model missing—ensure Multi-Tenancy base is implemented"

**Solution:**
- Ensure `apps.tenants` is in `INSTALLED_APPS` in Django settings
- Run migrations: `python manage.py migrate tenants`
- Verify models exist: `python manage.py showmigrations tenants`

#### 3. Django Admin Not Accessible

**Symptoms:**
- `/admin/` returns 404 or shows frontend page
- Admin interface not loading

**Possible Causes and Fixes:**

**a) URL Routing Conflict**
- **Issue**: Catch-all route intercepts `/admin/` before Django can handle it
- **Solution**: Ensure `path('admin/', admin.site.urls)` comes BEFORE any catch-all patterns in `urls.py`
  ```python
  urlpatterns = [
      path("admin/", admin.site.urls),  # Must be first!
      # ... other specific paths ...
      re_path(r'^.*', catch_all_view),  # Catch-all last
  ]
  ```
- **Verification**: Check `backend/projectmeats/urls.py` pattern order

**b) Superuser Not Properly Created**
- **Issue**: User exists but is_superuser or is_staff is False
- **Solution**: Use `create_superuser()` method which sets these automatically
- **Verification**:
  ```bash
  python manage.py shell
  >>> from django.contrib.auth import get_user_model
  >>> User = get_user_model()
  >>> user = User.objects.get(email='admin@meatscentral.com')
  >>> user.is_superuser, user.is_staff
  (True, True)  # Should both be True
  ```

#### 4. Database Integrity Errors

**Symptoms:**
- Error: "UNIQUE constraint failed: auth_user.username"
- Command fails with IntegrityError

**Solution:**
- Command is idempotent but checks username and email separately
- If a user exists with same username but different email, existing user is used
- To force new username, set `SUPERUSER_USERNAME` explicitly:
  ```bash
  export SUPERUSER_USERNAME=superadmin
  python manage.py create_super_tenant
  ```

#### 5. GitHub Actions Deployment Failures

**Symptoms:**
- Workflow step "Create Super Tenant" fails
- No detailed error message in logs

**Solutions:**

**a) Check Environment Secrets**
- Ensure GitHub Secrets are set:
  - `STAGING_SUPERUSER_USERNAME`
  - `STAGING_SUPERUSER_EMAIL`
  - `STAGING_SUPERUSER_PASSWORD`
  - `PRODUCTION_SUPERUSER_USERNAME`
  - `PRODUCTION_SUPERUSER_EMAIL`
  - `PRODUCTION_SUPERUSER_PASSWORD`

**b) Enable Verbose Logging**
- Workflow now includes `--verbosity 2` flag
- Check GitHub Actions logs for detailed output
- Look for emoji indicators:
  - 🔧 Configuration
  - 🔍 Attempting superuser creation
  - 🏢 Attempting root tenant creation
  - 🔗 Linking user to tenant
  - ✅ Success messages
  - ❌ Error messages

**c) Verify Migrations**
- Ensure migrations run before `create_super_tenant`
- Check workflow order:
  1. Pull code
  2. Install dependencies
  3. **Run migrations** ← Must happen first
  4. Create super tenant
  5. Collect static files

### Debugging Commands

```bash
# 1. Test with maximum verbosity
python manage.py create_super_tenant --verbosity 2

# 2. Check if user exists
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(email='admin@meatscentral.com').exists())"

# 3. Check if tenant exists
python manage.py shell -c "from apps.tenants.models import Tenant; print(Tenant.objects.filter(slug='root').exists())"

# 4. Verify user is superuser
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.get(email='admin@meatscentral.com'); print(f'Superuser: {u.is_superuser}, Staff: {u.is_staff}')"

# 5. Check tenant-user link
python manage.py shell -c "from apps.tenants.models import TenantUser; print(TenantUser.objects.all().values('tenant__slug', 'user__email', 'role'))"

# 6. Manually verify admin access
curl http://localhost:8000/admin/
# Should return Django admin login page HTML
```

### Best Practices for Troubleshooting

1. **Always run with verbosity first**: `--verbosity 2` provides detailed insights
2. **Check logs in order**:
   - Configuration values (redacted passwords)
   - User creation attempts
   - Tenant creation attempts
   - Linking attempts
   - Final success/error messages
3. **Verify environment variables** are loaded before running command
4. **Test locally first** before deploying to UAT/production
5. **Use atomic transactions**: Command wraps operations in `transaction.atomic()` for rollback on failure

### Getting Help

If issues persist:
1. Run command with `--verbosity 2` and capture full output
2. Check Django logs for additional error details
3. Verify database state manually using Django shell
4. Review GitHub Actions logs for deployment-specific issues
5. Check that all migrations are applied: `python manage.py showmigrations`

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
