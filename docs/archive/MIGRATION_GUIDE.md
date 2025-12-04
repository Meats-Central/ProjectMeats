# Database Migrations Guide

**Last Updated**: November 29, 2024  
**Tech Stack**: Django 4.2.7, PostgreSQL 15, django-tenants 3.5.0

---

## Table of Contents

1. [Overview](#overview)
2. [Django-Tenants Migration Architecture](#django-tenants-migration-architecture)
3. [Creating Migrations](#creating-migrations)
4. [Common Patterns](#common-patterns)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)
7. [CI/CD Integration](#cicd-integration)

---

## Overview

ProjectMeats uses **django-tenants** for schema-based multi-tenancy, which requires special consideration for migrations. This guide consolidates lessons learned from extensive migration work over the past 3 months.

### Key Concepts

- **SHARED_APPS**: Apps whose tables exist in the public schema (shared across all tenants)
- **TENANT_APPS**: Apps whose tables exist in each tenant's schema
- **Public Schema**: Contains shared data and tenant metadata
- **Tenant Schemas**: Contain tenant-specific business data

---

## Django-Tenants Migration Architecture

### App Organization

```python
# backend/projectmeats/settings/base.py

SHARED_APPS = [
    "django_tenants",  # Must be first!
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.core",
    "apps.tenants",  # Tenant management models
]

TENANT_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "apps.suppliers",
    "apps.customers",
    "apps.purchase_orders",
    "apps.accounts_receivables",
    "apps.plants",
    "apps.contacts",
    "apps.products",
    "apps.profiles",
]

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]
```

### Migration Commands

```bash
# Run migrations for public schema (SHARED_APPS)
python manage.py migrate_schemas --shared

# Run migrations for all tenant schemas (TENANT_APPS)
python manage.py migrate_schemas --tenant

# Run migrations for specific tenant
python manage.py migrate_schemas --schema=tenant_name

# Check for missing migrations (use in CI)
python manage.py makemigrations --check --dry-run
```

---

## Creating Migrations

### Standard Process

```bash
# 1. Create migrations
python manage.py makemigrations

# 2. Review generated migrations
cat backend/apps/YOUR_APP/migrations/0001_initial.py

# 3. Test locally
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant

# 4. Commit
git add backend/apps/YOUR_APP/migrations/
git commit -m "feat(YOUR_APP): Add initial migrations"
```

### Model Changes Requiring Migrations

Always create migrations when:
- Adding/removing models
- Adding/removing fields
- Changing field types
- Adding/removing indexes
- Changing model Meta options

---

## Common Patterns

### 1. Idempotent Migrations

Always check if objects exist before creating them:

```python
from django.db import migrations, models

def create_if_not_exists(apps, schema_editor):
    """Idempotent data migration"""
    MyModel = apps.get_model('myapp', 'MyModel')
    if not MyModel.objects.filter(name='default').exists():
        MyModel.objects.create(
            name='default',
            description='Default instance'
        )

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0001_initial'),
    ]
    
    operations = [
        migrations.RunPython(
            create_if_not_exists,
            reverse_code=migrations.RunPython.noop
        ),
    ]
```

### 2. Schema-Safe Operations

Use `IF NOT EXISTS` for raw SQL:

```python
class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS my_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255)
            );
            """,
            reverse_sql="DROP TABLE IF EXISTS my_table;"
        ),
    ]
```

### 3. Tenant-Aware Data Migrations

For data migrations in TENANT_APPS:

```python
def populate_tenant_data(apps, schema_editor):
    """This runs for each tenant schema"""
    MyModel = apps.get_model('myapp', 'MyModel')
    
    # This data exists only in current tenant's schema
    MyModel.objects.get_or_create(
        name='tenant_specific_data',
        defaults={'value': 'default'}
    )
```

### 4. Handling Foreign Keys

Ensure proper ordering for models with foreign keys:

```python
class Migration(migrations.Migration):
    dependencies = [
        ('otherapp', '0001_initial'),  # Ensure referenced model exists
        ('myapp', '0001_initial'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='mymodel',
            name='other',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                to='otherapp.othermodel',
                null=True,  # Allow null during migration
                blank=True
            ),
        ),
    ]
```

---

## Troubleshooting

### Issue: "Table already exists"

**Symptom**:
```
django.db.utils.ProgrammingError: relation "app_model" already exists
```

**Causes**:
1. Non-idempotent migration
2. Migration run multiple times
3. Manual table creation

**Solutions**:
```python
# Option 1: Use IF NOT EXISTS (PostgreSQL)
migrations.RunSQL(
    "CREATE TABLE IF NOT EXISTS app_model (...)",
    reverse_sql="DROP TABLE IF EXISTS app_model;"
)

# Option 2: Check and create in Python
def safe_create(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'app_model'
            );
        """)
        exists = cursor.fetchone()[0]
        if not exists:
            # Create table
            pass
```

### Issue: "No such table" in Tests

**Symptom**:
```
django.db.utils.OperationalError: no such table: app_model
```

**Causes**:
1. Migrations not run in test setup
2. Test database not created properly
3. Missing `django_tenants` configuration

**Solutions**:
```python
# In test settings
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',  # Required!
        'NAME': 'test_db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
        'TEST': {
            'NAME': 'test_projectmeats',
        }
    }
}

# Ensure migrations run
python manage.py migrate_schemas --shared
python manage.py test
```

### Issue: "Role does not exist"

**Symptom**:
```
django.db.utils.OperationalError: role "root" does not exist
```

**Cause**: Hardcoded database user in configuration

**Solution**:
```python
# Use environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': os.getenv('DB_NAME', 'projectmeats'),
        'USER': os.getenv('DB_USER', 'postgres'),  # Default to 'postgres'
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

### Issue: Migration Dependency Conflicts

**Symptom**:
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution**:
```bash
# 1. Check migration status
python manage.py showmigrations

# 2. Identify conflicting migrations
python manage.py migrate --plan

# 3. Squash migrations if needed (caution!)
python manage.py squashmigrations myapp 0001 0005

# 4. Or reset migrations (development only!)
# Delete migration files (keep __init__.py)
rm backend/apps/myapp/migrations/0*.py
python manage.py makemigrations myapp
```

---

## Best Practices

### 1. Pre-Commit Validation

Always validate migrations before committing:

```bash
# Installed via pre-commit hooks
python manage.py makemigrations --check --dry-run
```

This prevents CI failures due to missing migrations.

### 2. Migration Naming

Use descriptive names:

```bash
python manage.py makemigrations myapp --name add_customer_email_field
# Creates: 0002_add_customer_email_field.py
```

### 3. Review Before Committing

Always review generated migrations:

```bash
# View migration SQL
python manage.py sqlmigrate myapp 0002

# Test migration
python manage.py migrate --fake-initial
```

### 4. Separate Schema Changes from Data

Create separate migrations for:
1. Schema changes (models, fields)
2. Data migrations (populating data)

```bash
# First migration: schema
python manage.py makemigrations myapp

# Second migration: data
python manage.py makemigrations myapp --empty --name populate_defaults
# Edit the empty migration to add data operations
```

### 5. Zero-Downtime Migrations

For production:

1. **Add nullable field**
   ```python
   field = models.CharField(max_length=100, null=True, blank=True)
   ```

2. **Deploy and populate**
   ```python
   # Data migration to populate field
   ```

3. **Make field non-nullable**
   ```python
   field = models.CharField(max_length=100)  # Remove null=True
   ```

### 6. Document Complex Migrations

Add comments explaining non-obvious logic:

```python
class Migration(migrations.Migration):
    """
    Migrates customer data from old to new schema.
    
    This migration:
    1. Creates new CustomerProfile model
    2. Copies data from Customer.extra_data JSON field
    3. Links profiles to customers via FK
    
    Reversing this migration will lose profile data.
    """
    dependencies = [...]
    operations = [...]
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/validate-migrations.yml
name: Validate Migrations

on: [push, pull_request]

jobs:
  check-migrations:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Check for missing migrations
        working-directory: ./backend
        env:
          DB_ENGINE: django_tenants.postgresql_backend
          DB_NAME: test_db
          DB_USER: postgres
          DB_PASSWORD: postgres
          DB_HOST: localhost
          DB_PORT: 5432
        run: |
          python manage.py makemigrations --check --dry-run
      
      - name: Run migrations
        working-directory: ./backend
        env:
          DB_ENGINE: django_tenants.postgresql_backend
          DB_NAME: test_db
          DB_USER: postgres
          DB_PASSWORD: postgres
          DB_HOST: localhost
          DB_PORT: 5432
        run: |
          python manage.py migrate_schemas --shared
          # Test migrations work
```

### Pre-Commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-django-migrations
        name: Validate Django Migrations
        entry: bash -c 'cd backend && python manage.py makemigrations --check --dry-run'
        language: system
        pass_filenames: false
        files: '\.(py)$'
```

---

## Quick Reference

### Common Commands

```bash
# Check migration status
python manage.py showmigrations

# Create migrations
python manage.py makemigrations

# Apply migrations (public schema)
python manage.py migrate_schemas --shared

# Apply migrations (all tenants)
python manage.py migrate_schemas --tenant

# View migration SQL
python manage.py sqlmigrate app_name 0001

# Fake migration (mark as applied without running)
python manage.py migrate --fake app_name 0001

# Reverse migration
python manage.py migrate app_name 0001  # Migrates to 0001, reversing all after

# Check for unapplied migrations
python manage.py makemigrations --check --dry-run
```

### Environment Variables

```bash
# Required for django-tenants
DB_ENGINE=django_tenants.postgresql_backend
DB_NAME=projectmeats_dev
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

---

## Migration Checklist

Before committing migrations:

- [ ] Generated migrations reviewed
- [ ] Migrations tested locally
- [ ] SQL output reviewed (`sqlmigrate`)
- [ ] Migrations are idempotent
- [ ] Dependencies correctly specified
- [ ] Data migrations separated from schema changes
- [ ] Comments added for complex logic
- [ ] Pre-commit validation passed
- [ ] CI pipeline tested

---

## Additional Resources

- [Django Migrations Official Docs](https://docs.djangoproject.com/en/4.2/topics/migrations/)
- [django-tenants Documentation](https://django-tenants.readthedocs.io/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
- Internal: `docs/lessons-learned/3-MONTH-RETROSPECTIVE.md`

---

**Maintainer**: Development Team  
**Review Cycle**: Monthly  
**Related Docs**: 
- `docs/MULTI_TENANCY_GUIDE.md`
- `docs/DEPLOYMENT_GUIDE.md`
- `docs/TROUBLESHOOTING.md`
