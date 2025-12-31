# Tenant Onboarding Guide

This guide explains how to onboard new tenants and domains using the `create_tenant` management command and batch utilities.

## Table of Contents
- [Quick Start](#quick-start)
- [Management Command: create_tenant](#management-command-create_tenant)
- [Batch Utilities](#batch-utilities)
- [Examples](#examples)
- [Migration Notes](#migration-notes)

## Quick Start

### Creating a Single Tenant

```bash
# Minimal example - creates tenant with auto-generated defaults
python manage.py create_tenant \
  --schema-name=acme_corp \
  --name="ACME Corporation"

# Full example - with domain and trial period
python manage.py create_tenant \
  --schema-name=acme_corp \
  --name="ACME Corporation" \
  --domain=acme.example.com \
  --contact-email=admin@acme.com \
  --contact-phone="+1-555-ACME-00" \
  --on-trial \
  --paid-until=2024-12-31
```

### Creating Demo/Test Tenants

```python
# In Django shell or script
from apps.tenants.utils import create_demo_tenants

# Create 5 demo tenants for development
tenants = create_demo_tenants(environment='development', count=5)
```

## Management Command: create_tenant

The `create_tenant` command creates a new tenant with optional domain for multi-tenancy onboarding.

### Required Parameters

- `--schema-name`: Database schema name (unique identifier)
  - Must start with letter or underscore
  - Can contain letters, digits, underscores
  - Maximum 63 characters
  - Example: `acme_corp`, `test_tenant_01`

- `--name`: Tenant organization name
  - Display name for the tenant
  - Example: `"ACME Corporation"`, `"Test Company"`

### Optional Parameters

**Tenant Configuration:**
- `--slug`: URL-friendly identifier (auto-generated from schema-name if not provided)
- `--contact-email`: Primary contact email (defaults to `admin@{slug}.local`)
- `--contact-phone`: Primary contact phone number
- `--on-trial`: Mark tenant as trial account
- `--paid-until`: Paid until date in YYYY-MM-DD format (auto-set to 30 days if `--on-trial` without this)

**Domain Configuration:**
- `--domain`: Primary domain for tenant routing (e.g., `acme.example.com`)
- `--is-primary`: Mark domain as primary (default: True)

**Environment:**
- `--environment`: Environment context (`development`, `staging`, `uat`, `production`)

**Verbosity:**
- `-v 0`: Silent output
- `-v 1`: Normal output (default)
- `-v 2`: Verbose output with configuration details

### Output

The command provides:
- ✅ Confirmation of tenant creation
- ✅ Confirmation of domain creation (if domain provided)
- 📋 Summary of created tenant with all details
- 📝 Next steps for tenant setup

### Examples

#### Example 1: Minimal Tenant

```bash
python manage.py create_tenant \
  --schema-name=test_tenant \
  --name="Test Tenant"
```

**Result:**
- Schema Name: `test_tenant`
- Slug: `test-tenant` (auto-generated)
- Contact Email: `admin@test-tenant.local` (auto-generated)
- Trial: `False`
- Active: `True`

#### Example 2: Production Tenant with Domain

```bash
python manage.py create_tenant \
  --schema-name=acme_corp \
  --name="ACME Corporation" \
  --slug=acme \
  --domain=acme.meatscentral.com \
  --contact-email=admin@acme.com \
  --contact-phone="+1-555-ACME-00" \
  --environment=production
```

#### Example 3: Trial Tenant

```bash
python manage.py create_tenant \
  --schema-name=trial_co \
  --name="Trial Company" \
  --domain=trial.example.com \
  --on-trial \
  --paid-until=2024-12-31 \
  -v 2
```

#### Example 4: Development Tenant

```bash
python manage.py create_tenant \
  --schema-name=dev_test \
  --name="Dev Test Company" \
  --domain=dev-test.localhost \
  --on-trial \
  --environment=development
```

## Batch Utilities

The batch utilities allow creating multiple tenants programmatically. Located in `apps/tenants/utils/batch_tenant_creator.py`.

### Functions

#### `create_demo_tenants(environment, count, verbosity)`

Creates demo/test tenants for a specific environment.

**Parameters:**
- `environment` (str): 'development', 'staging', 'uat', or 'production'
- `count` (int): Number of demo tenants to create (default: 3)
- `verbosity` (int): Output level 0-2 (default: 1)

**Returns:** List of created Tenant objects

**Example:**
```python
from apps.tenants.utils import create_demo_tenants

# Create 5 demo tenants for development
tenants = create_demo_tenants(environment='development', count=5)
print(f'Created {len(tenants)} demo tenants')
```

**Generated Tenants:**
- `development_acme_corp` → "ACME Corporation (Development)"
- `development_globex_inc` → "Globex Inc (Development)"
- `development_initech_llc` → "Initech LLC (Development)"
- etc.

Each tenant gets:
- Unique schema_name with environment prefix
- Environment-appropriate domain (e.g., `acme.localhost` for dev)
- Auto-generated contact info
- Trial status based on environment
- Primary domain

#### `create_custom_tenants(tenant_configs, verbosity)`

Creates multiple tenants from custom configurations.

**Parameters:**
- `tenant_configs` (List[Dict]): List of tenant configuration dictionaries
- `verbosity` (int): Output level 0-2 (default: 1)

**Returns:** List of created Tenant objects

**Example:**
```python
from apps.tenants.utils import create_custom_tenants

configs = [
    {
        'schema_name': 'acme_corp',
        'name': 'ACME Corporation',
        'domain': 'acme.example.com',
        'contact_email': 'admin@acme.com',
        'on_trial': False,
    },
    {
        'schema_name': 'test_company',
        'name': 'Test Company',
        'domain': 'test.example.com',
        'on_trial': True,
    }
]

tenants = create_custom_tenants(configs)
```

#### `create_single_tenant(...)`

Low-level function to create a single tenant with full control.

**Parameters:**
- `schema_name` (str): Database schema name
- `name` (str): Tenant name
- `slug` (str, optional): URL slug
- `contact_email` (str, optional): Contact email
- `contact_phone` (str, optional): Contact phone
- `on_trial` (bool): Trial status (default: True)
- `trial_ends_at` (datetime, optional): Trial end date
- `domain` (str, optional): Domain name
- `is_primary` (bool): Primary domain flag (default: True)
- `verbosity` (int): Output level

**Returns:** Created Tenant object

**Example:**
```python
from apps.tenants.utils import create_single_tenant

tenant = create_single_tenant(
    schema_name='custom_tenant',
    name='Custom Tenant',
    domain='custom.example.com',
    on_trial=True,
    verbosity=1
)
```

#### `cleanup_demo_tenants(environment, verbosity, dry_run)`

Clean up demo tenants for a specific environment.

**Parameters:**
- `environment` (str): Environment name
- `verbosity` (int): Output level (default: 1)
- `dry_run` (bool): Preview without deleting (default: True)

**Returns:** Number of tenants deleted/to be deleted

**Example:**
```python
from apps.tenants.utils import cleanup_demo_tenants

# Preview what would be deleted
count = cleanup_demo_tenants('development', dry_run=True)
print(f'Would delete {count} tenants')

# Actually delete
count = cleanup_demo_tenants('development', dry_run=False)
print(f'Deleted {count} tenants')
```

### Usage in Scripts

**Example: Setup script for development environment**

```python
#!/usr/bin/env python
"""Setup demo tenants for development environment."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmeats.settings.development')
django.setup()

from apps.tenants.utils import create_demo_tenants, cleanup_demo_tenants

def setup_dev_tenants():
    """Setup development demo tenants."""
    # Clean up existing demo tenants
    print("Cleaning up existing demo tenants...")
    cleanup_demo_tenants('development', dry_run=False)
    
    # Create fresh demo tenants
    print("\nCreating fresh demo tenants...")
    tenants = create_demo_tenants(environment='development', count=3)
    
    print(f"\n✅ Setup complete! Created {len(tenants)} demo tenants")
    for tenant in tenants:
        print(f"  - {tenant.name} ({tenant.schema_name})")

if __name__ == '__main__':
    setup_dev_tenants()
```

## Architecture Notes

### ProjectMeats Multi-Tenancy

ProjectMeats uses a **shared-schema multi-tenancy** approach:

- **Single PostgreSQL schema** (`public`) for all tenants
- **Row-level isolation** via `tenant_id` foreign keys on business models
- **Application-level filtering** in ViewSets: `queryset.filter(tenant=request.tenant)`
- **Standard Django backend**: `django.db.backends.postgresql`
- **Standard migrations**: `python manage.py migrate` (NOT `migrate_schemas`)

### Database Migration

Tenant creation does NOT require schema-specific migrations. All tenants share the same database schema.

```bash
# Create tenant (no schema migration needed)
python manage.py create_tenant --schema-name=acme --name="ACME Corp"

# Run standard Django migrations (applies to all tenants)
python manage.py migrate --fake-initial --noinput
```

**Note**: The `schema_name` field exists for administrative naming purposes only. ProjectMeats uses shared-schema multi-tenancy and does NOT use PostgreSQL schemas for tenant isolation.

## Environment-Specific Configurations

### Development
- Domain base: `localhost`
- Trial period: 30 days
- Default trial: Yes
- Example: `acme.localhost`

### Staging/UAT
- Domain base: `staging.meatscentral.com` / `uat.meatscentral.com`
- Trial period: 60-90 days
- Default trial: Yes
- Example: `acme.staging.meatscentral.com`

### Production
- Domain base: `meatscentral.com`
- Trial period: 30 days
- Default trial: No
- Example: `acme.meatscentral.com`

## Best Practices

1. **Schema Name Field:**
   - Use descriptive, unique identifiers
   - Use underscores, not hyphens
   - Keep under 63 characters
   - Example: `acme_corp`, `test_tenant_01`
   - **Note**: This is an administrative identifier, not a PostgreSQL schema

2. **Slug Naming:**
   - URL-friendly
   - Use hyphens, not underscores
   - Lowercase
   - Example: `acme-corp`, `test-tenant-01`

3. **Domain Naming:**
   - Use fully qualified domain names
   - Development: `.localhost` or `.local`
   - Staging: `.staging.meatscentral.com`
   - Production: `.meatscentral.com`

4. **Trial Tenants:**
   - Always set `--paid-until` or let it auto-set
   - Monitor trial expiration
   - Convert to paid before expiration

5. **Contact Information:**
   - Use real email addresses for production
   - Use `.local` domains for development
   - Include phone numbers for production tenants

## Troubleshooting

### Error: "Invalid schema_name"

**Problem:** schema_name field doesn't meet identifier rules

**Solution:** Ensure schema_name:
- Starts with letter or underscore
- Contains only letters, digits, underscores
- Is 63 characters or less

**Note**: Despite the name, this is NOT a PostgreSQL schema - it's just an administrative identifier field.

### Error: "Tenant with schema_name already exists"

**Problem:** Trying to create duplicate tenant

**Solution:**
- Choose a different schema_name value
- Delete existing tenant if it's a test tenant
- Check with: `python manage.py shell` → `Tenant.objects.filter(schema_name='...')`

### Error: "Invalid date format"

**Problem:** `--paid-until` date not in YYYY-MM-DD format

**Solution:** Use correct format:
```bash
--paid-until=2024-12-31  # Correct
--paid-until=12/31/2024  # Wrong
```

## Additional Resources

- [Multi-Tenancy Implementation Guide](../../MULTI_TENANCY_IMPLEMENTATION.md)
- [Django-Tenants Alignment](../../DJANGO_TENANTS_ALIGNMENT.md)
- [Domain Model Documentation](../models.py)
- [Tenant Model Documentation](../models.py)

## Support

For issues or questions:
1. Check existing tenants: `Tenant.objects.all()`
2. Check existing domains: `Domain.objects.all()`
3. Review logs for detailed error messages
4. Use `-v 2` for verbose output during debugging
