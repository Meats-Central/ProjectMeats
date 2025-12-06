# Phoenix Init Management Command

## Overview

The `phoenix_init` management command provides an idempotent initialization script for ProjectMeats environments. It sets up the essential components needed for a fresh environment or Phoenix-style reset.

## What It Does

The command performs the following operations in order:

1. **Superuser Creation/Verification**
   - Checks for superuser credentials in environment variables
   - Creates a new superuser if credentials are provided and user doesn't exist
   - Uses existing superuser if found

2. **Public Tenant Creation**
   - Creates a tenant with `schema_name='public'`
   - Required for shared schema multi-tenancy logic
   - Idempotent: won't create duplicates

3. **Demo Tenant Creation**
   - Creates a 'demo' tenant with appropriate schema configuration
   - Sets up `demo.localhost` domain mapping via TenantDomain
   - Idempotent: reuses existing tenant if found

4. **User-Tenant Linking**
   - Links the superuser to the demo tenant with 'owner' role
   - Uses TenantUser model for the association

## Usage

### Basic Usage

```bash
# Set required environment variables
export DJANGO_SUPERUSER_EMAIL=admin@example.com
export DJANGO_SUPERUSER_PASSWORD=securepassword123

# Run the command
python manage.py phoenix_init
```

### Expected Output

```
Superuser created.
Public Tenant created.
Demo Tenant and Domain created.
Superuser linked to Demo Tenant.
```

### Idempotent Behavior

Running the command multiple times is safe:

```bash
# First run
python manage.py phoenix_init
# Output: Creates all resources

# Second run
python manage.py phoenix_init
# Output: 
#   Superuser exists.
#   Demo Tenant and Domain created.
#   Superuser linked to Demo Tenant.
```

## Environment Variables

### Required for New Superuser Creation

- `DJANGO_SUPERUSER_EMAIL`: Email address for the superuser account
- `DJANGO_SUPERUSER_PASSWORD`: Password for the superuser account

### Optional

If environment variables are not provided, the command will:
- Use the first existing superuser if available
- Skip superuser creation if no credentials are provided

## Integration with Deployment

### Development Environment

```bash
# In .env file
DJANGO_SUPERUSER_EMAIL=dev@meatscentral.com
DJANGO_SUPERUSER_PASSWORD=devpass123

# Run after migrations
python manage.py migrate
python manage.py phoenix_init
```

### CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
- name: Initialize Phoenix Environment
  env:
    DJANGO_SUPERUSER_EMAIL: ${{ secrets.SUPERUSER_EMAIL }}
    DJANGO_SUPERUSER_PASSWORD: ${{ secrets.SUPERUSER_PASSWORD }}
  run: |
    python manage.py migrate --noinput
    python manage.py phoenix_init
```

### Docker Compose

```yaml
services:
  backend:
    command: >
      sh -c "
        python manage.py migrate --noinput &&
        python manage.py phoenix_init &&
        python manage.py runserver 0.0.0.0:8000
      "
    environment:
      - DJANGO_SUPERUSER_EMAIL=admin@example.com
      - DJANGO_SUPERUSER_PASSWORD=password123
```

## Technical Details

### Models Used

- `User` (Django's auth user model via `get_user_model()`)
- `apps.tenants.models.Tenant`: Multi-tenancy tenant model
- `apps.tenants.models.TenantDomain`: Domain mapping for tenants
- `apps.tenants.models.TenantUser`: User-tenant association with roles

### Tenant Configuration

**Public Tenant:**
```python
{
    'schema_name': 'public',
    'name': 'Public',
    'slug': 'public',
    'contact_email': '<superuser_email or default>'
}
```

**Demo Tenant:**
```python
{
    'name': 'demo',
    'schema_name': 'demo',
    'slug': 'demo',
    'contact_email': '<superuser_email or default>'
}
```

**Demo Domain:**
```python
{
    'domain': 'demo.localhost',
    'tenant': <demo_tenant>,
    'is_primary': True
}
```

### Shared-Schema Architecture

This command is designed for ProjectMeats' **shared-schema multi-tenancy** architecture:

- All tenants share the same PostgreSQL schema
- Tenant isolation via `tenant_id` foreign keys
- No django-tenants schema-based isolation
- TenantMiddleware resolves tenant from domain/subdomain/header

## Troubleshooting

### No Superuser Found

If you see a warning about no superuser being found, ensure:
1. Environment variables are set correctly
2. Database migrations are applied
3. Previous superuser creation didn't fail

### Domain Already Exists Error

If `demo.localhost` domain already exists pointing to a different tenant:
- Manually delete the conflicting domain mapping
- Or update the existing domain to point to the demo tenant

### Permission Issues

Ensure the database user has sufficient permissions to create and modify tables:
```sql
-- For PostgreSQL, grant specific permissions needed:
GRANT CONNECT ON DATABASE projectmeats TO your_db_user;
GRANT USAGE ON SCHEMA public TO your_db_user;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO your_db_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_db_user;
```

## Testing

The command includes comprehensive unit tests in:
`backend/apps/core/tests/test_phoenix_init.py`

Run tests with:
```bash
python manage.py test apps.core.tests.test_phoenix_init
```

## See Also

- `setup_superuser`: Alternative command for superuser management
- `create_tenant`: Create custom tenants
- `init_dev_tenant`: Development-specific tenant setup
