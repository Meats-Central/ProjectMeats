# Migration Fix: Duplicate tenant_id Columns

## Problem

The migration `0002_*_tenant_*.py` files are trying to add `tenant_id` columns that **already exist** in the production/dev databases. This causes the error:

```
django.db.utils.ProgrammingError: column "tenant_id" of relation "..." already exists
```

## Root Cause

The `tenant` foreign key fields were previously added to the database (either manually or through an earlier migration that was later removed from the codebase). When we regenerated migrations for the Shared-Schema architecture, Django created new `0002` migrations that try to add these columns again.

## Solution

We need to **fake** these migrations, telling Django that they've been applied without actually executing the SQL.

### Quick Fix (Recommended)

Run the automated fix script inside the backend container:

```bash
# Option 1: Via Docker (from host machine)
docker exec pm-backend bash /app/scripts/fix_duplicate_tenant_migrations.sh

# Option 2: Via SSH (in production/staging)
ssh user@host
docker exec pm-backend bash /app/scripts/fix_duplicate_tenant_migrations.sh
```

### Manual Fix (If script fails)

If the automated script doesn't work, manually fake each migration:

```bash
# Enter the container
docker exec -it pm-backend bash

# Fake each app's 0002 migration
python manage.py migrate accounts_receivables 0002 --fake
python manage.py migrate ai_assistant 0002 --fake
python manage.py migrate bug_reports 0002 --fake
python manage.py migrate carriers 0002 --fake
python manage.py migrate contacts 0002 --fake
python manage.py migrate customers 0002 --fake
python manage.py migrate invoices 0002 --fake
python manage.py migrate plants 0002 --fake
python manage.py migrate products 0002 --fake
python manage.py migrate purchase_orders 0002 --fake
python manage.py migrate sales_orders 0002 --fake
python manage.py migrate suppliers 0002 --fake
```

### Verification

After faking the migrations, verify the state:

```bash
# Check migration status
python manage.py showmigrations

# All tenant_apps should show [X] for 0002 migrations
```

## Long-Term Solution

To prevent this issue in the future:

1. **Never manually add columns** - always use Django migrations
2. **Never delete migration files** from the codebase without also rolling them back in all environments
3. **Use version control** for database schema changes
4. **Document schema changes** in CHANGELOG.md

## For New Environments

For **fresh database installations** (new environments that don't have the columns yet):

```bash
# Run migrations normally (don't fake)
python manage.py migrate
```

The `0002` migrations will execute successfully because the columns don't exist yet.

## Technical Details

### What `--fake` Does

The `--fake` flag tells Django:
- ✅ Mark the migration as applied in `django_migrations` table
- ❌ DO NOT execute the SQL operations
- ✅ Allow subsequent migrations to run normally

### Affected Apps

All `tenant_apps` business models:
- accounts_receivables
- ai_assistant  
- bug_reports
- carriers
- contacts
- customers
- invoices
- plants
- products
- purchase_orders
- sales_orders
- suppliers

### Migration Pattern

All 0002 migrations follow this pattern:

```python
operations = [
    migrations.AddField(
        model_name='...',
        name='tenant',
        field=models.ForeignKey(
            on_delete=django.db.models.deletion.CASCADE,
            to='tenants.tenant',
        ),
    ),
    # ... optional indexes ...
]
```

## References

- Django Migration Documentation: https://docs.djangoproject.com/en/stable/topics/migrations/
- Shared-Schema Architecture: `docs/ARCHITECTURE.md`
- Golden Pipeline: `docs/GOLDEN_PIPELINE.md`
