# ProjectMeats - Project-Specific Conventions and Patterns

**Last Updated:** 2024-12-01

## Overview

This document highlights conventions and patterns specific to ProjectMeats that **differ from common practices** in typical Django/React projects. These unique patterns were developed to meet the specific requirements of our multi-tenant SaaS platform and deployment workflow.

> **Important:** If you're familiar with standard Django/React development, read this document carefully to understand ProjectMeats-specific approaches before contributing.

---

## Table of Contents

1. [Multi-Tenancy Architecture](#1-multi-tenancy-architecture)
2. [Migration Workflow](#2-migration-workflow)
3. [Branch and Deployment Strategy](#3-branch-and-deployment-strategy)
4. [Environment Configuration](#4-environment-configuration)
5. [Admin Panel Customization](#5-admin-panel-customization)
6. [Superuser Management](#6-superuser-management)
7. [Directory Structure](#7-directory-structure)
8. [CI/CD and Automation](#8-cicd-and-automation)
9. [Pre-commit Hooks](#9-pre-commit-hooks)
10. [Testing Patterns](#10-testing-patterns)

---

## 1. Multi-Tenancy Architecture

### ❗ Differs from Common Practice

**Standard Django:** Single-tenant application with one database schema.

**ProjectMeats:** Dual multi-tenancy architecture using both django-tenants (schema-based) and custom shared-schema approach.

### How It Works

ProjectMeats implements **two parallel multi-tenancy systems**:

1. **Schema-Based Multi-Tenancy (django-tenants)**
   - Each tenant gets its own PostgreSQL schema
   - Models: `Client` and `Domain` (inheriting from `TenantMixin` and `DomainMixin`)
   - Complete data isolation at the database level
   - Used for: Enterprise deployments requiring strict isolation

2. **Shared-Schema Multi-Tenancy (Custom)**
   - All tenants share the same database schema
   - Models: `Tenant`, `TenantUser`, and `TenantDomain`
   - Data isolation via `tenant_id` foreign keys
   - Used for: Backward compatibility and simpler deployments

### Key Implications

#### TENANT_APPS vs SHARED_APPS

In `backend/projectmeats/settings/base.py`, apps are split into two categories:

```python
SHARED_APPS = [
    "django_tenants",  # Must be first
    "django.contrib.admin",
    "django.contrib.auth",
    # ... other Django core apps
    "apps.core",
    "apps.tenants",  # Tenant management
]

TENANT_APPS = [
    "django.contrib.admin",  # Tenant-specific admin
    "django.contrib.auth",   # Tenant-specific users
    "apps.suppliers",
    "apps.customers",
    "apps.purchase_orders",
    "apps.accounts_receivables",
    "apps.contacts",
    "apps.plants",
    "apps.carriers",
    "apps.products",
    "apps.sales_orders",
    "apps.invoices",
    "apps.bug_reports",
    "apps.ai_assistant",
]
```

**Critical Rule:** Apps in `TENANT_APPS` require special migration handling.

### Database Engine Configuration

**Standard Django:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ...
    }
}
```

**ProjectMeats:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',  # Special backend
        # ...
    }
}
```

### References

- [MULTI_TENANCY_GUIDE.md](MULTI_TENANCY_GUIDE.md)
- [django-tenants documentation](https://django-tenants.readthedocs.io/)

---

## 2. Migration Workflow

### ❗ Differs from Common Practice

**Standard Django:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**ProjectMeats:**
```bash
# For apps in TENANT_APPS:
python manage.py makemigrations <app_name>
python manage.py migrate_schemas  # NOT migrate!

# For apps in SHARED_APPS (core, tenants):
python manage.py makemigrations <app_name>
python manage.py migrate  # Standard migrate is OK
```

### Why This Matters

When you change a model in a `TENANT_APPS` app:

1. **ALWAYS** run `makemigrations` and commit the migration file
2. Use `migrate_schemas` instead of `migrate` to apply migrations
3. `migrate_schemas` applies migrations to **all tenant schemas**, not just the public schema

### Pre-commit Hook Enforcement

**Unique to ProjectMeats:** We have a pre-commit hook that fails commits if:
- Unapplied migrations are detected
- Migration files have syntax errors
- Model changes exist without corresponding migrations

**Standard Django projects** typically don't enforce this automatically.

### Migration Best Practices for ProjectMeats

1. **Minimal Dependencies:** Only depend on migrations that create models/fields you actually reference
2. **CharField Defaults:** Always use `default=''` with `blank=True` for PostgreSQL compatibility
3. **Never Modify Applied Migrations:** Create a new migration instead
4. **Test on Fresh Database:** Run `dropdb test_db && createdb test_db && python manage.py migrate_schemas` before PRs

### References

- [MIGRATION_BEST_PRACTICES.md](MIGRATION_BEST_PRACTICES.md)
- [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- [.github/copilot-instructions.md](../.github/copilot-instructions.md#migration-verification-checklist)

---

## 3. Branch and Deployment Strategy

### ❗ Differs from Common Practice

**Standard Git Flow:**
```
feature → develop → main
```

**ProjectMeats:**
```
feature/fix → development → UAT → main
```

### The Three-Branch System

1. **development** - Active development, all features merge here first
2. **UAT** - User Acceptance Testing / Staging environment
3. **main** - Production

### Critical Deployment Rules

**NEVER:**
- ❌ Push directly to `UAT` or `main`
- ❌ Create manual PRs between `development → UAT` or `UAT → main`
- ❌ Bypass the automated promotion workflows
- ❌ Skip the `development` branch

**ALWAYS:**
- ✅ Start with feature/fix branch from `development`
- ✅ Merge to `development` first via PR
- ✅ Let automated workflows handle promotion PRs
- ✅ Wait for UAT testing before promoting to production

### Automated PR Promotion

**Unique to ProjectMeats:** After merging to `development`, an automated workflow:

1. Closes any existing stale PRs between the same branches
2. Creates a fresh PR from `development` to `UAT`
3. Assigns reviewers automatically
4. Waits for manual approval and testing

The same process repeats for `UAT → main`.

**Workflows:**
- `.github/workflows/promote-dev-to-uat.yml`
- `.github/workflows/promote-uat-to-main.yml`

**Why:** This ensures only tested, reviewed code progresses through environments and prevents duplicate/conflicting PRs.

### Branch Protection

All three main branches have:
- Required status checks
- Required reviews (1 for development, 2 for UAT/main)
- Linear history enforcement
- No force-push allowed

### References

- [branch-workflow-checklist.md](../branch-workflow-checklist.md)
- [.github/copilot-instructions.md](../.github/copilot-instructions.md#-branch-organization-naming-tagging-and-promotion)

---

## 4. Environment Configuration

### ❗ Differs from Common Practice

**Standard Django Projects:**
- Individual `.env` files per developer
- Manual configuration
- django-environ or python-decouple

**ProjectMeats:**
- Centralized environment management via `config/manage_env.py`
- Environment templates in `config/environments/`
- Automated setup and validation scripts

### The Centralized Configuration System

```bash
# Setup development environment
python config/manage_env.py setup development

# Setup staging environment
python config/manage_env.py setup staging

# Setup production environment
python config/manage_env.py setup production

# Validate current configuration
python config/manage_env.py validate
```

### Environment Files Structure

```
config/
├── manage_env.py           # Management script
└── environments/
    ├── development.env     # Development config
    ├── staging.env         # Staging config
    └── production.env      # Production config
```

### Why This Approach

1. **Consistency:** All team members use the same configuration
2. **Validation:** Automatic checking of required variables
3. **Documentation:** Environment templates serve as documentation
4. **Safety:** Prevents missing configuration in production

### Environment-Specific Variables

ProjectMeats uses **environment-specific prefixes** for certain variables:

```bash
# Development
DEVELOPMENT_SUPERUSER_USERNAME=admin
DEVELOPMENT_SUPERUSER_EMAIL=admin@example.com
DEVELOPMENT_SUPERUSER_PASSWORD=DevPassword123!

# Staging
STAGING_SUPERUSER_USERNAME=staging_admin
STAGING_SUPERUSER_EMAIL=admin@staging.example.com
STAGING_SUPERUSER_PASSWORD=StagingPassword123!

# Production
PRODUCTION_SUPERUSER_USERNAME=prod_admin
PRODUCTION_SUPERUSER_EMAIL=admin@production.example.com
PRODUCTION_SUPERUSER_PASSWORD=ProdPassword123!
```

**Standard Django projects** typically use generic variable names like `DJANGO_SUPERUSER_USERNAME`.

### References

- [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md)
- [config/manage_env.py](../config/manage_env.py)

---

## 5. Admin Panel Customization

### ❗ Differs from Common Practice

**Standard Django Admin:**
```python
from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email']
```

**ProjectMeats (for tenant-aware models):**
```python
from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(TenantFilteredAdmin):  # Not admin.ModelAdmin!
    list_display = ['name', 'email']
    tenant_field = 'tenant'  # Optional: defaults to 'tenant'
```

### The TenantFilteredAdmin Pattern

`TenantFilteredAdmin` is a custom base class that:

1. **Filters queryset by tenant** for non-superuser staff
2. **Shows all data** for superusers
3. **Automatically assigns tenant** on object creation
4. **Prevents cross-tenant data access**

**Location:** `backend/apps/core/admin.py`

### When to Use It

**Use TenantFilteredAdmin for:**
- ✅ All models with a `tenant` foreign key
- ✅ Models in `TENANT_APPS`
- ✅ Any model where staff should only see their tenant's data

**Don't use it for:**
- ❌ Models in `SHARED_APPS` (core, tenants)
- ❌ Models without tenant relationships
- ❌ Superuser-only models

### Example

```python
from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import Supplier

@admin.register(Supplier)
class SupplierAdmin(TenantFilteredAdmin):
    list_display = ['name', 'code', 'status', 'tenant']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
    
    # tenant_field = 'tenant'  # Default, can be omitted
```

### References

- [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md)
- [backend/apps/core/admin.py](../backend/apps/core/admin.py)

---

## 6. Superuser Management

### ❗ Differs from Common Practice

**Standard Django:**
```bash
python manage.py createsuperuser
# Prompts for username, email, password interactively
```

**ProjectMeats:**
```bash
# Two specialized commands:

# 1. Sync credentials from environment (runs on every deploy)
python manage.py setup_superuser

# 2. Create superuser + tenant infrastructure
python manage.py create_super_tenant
```

### Why Two Commands?

1. **setup_superuser**
   - Syncs username, email, and password from environment-specific variables
   - Updates existing superuser if credentials changed
   - Idempotent - safe to run multiple times
   - Runs automatically on every deployment

2. **create_super_tenant**
   - Creates superuser + root tenant + links them together
   - Sets up complete multi-tenant infrastructure
   - Also idempotent
   - Typically run once or after database resets

### Environment-Specific Credentials

The `DJANGO_ENV` environment variable determines which credentials to use:

```python
# In settings or management command
if os.getenv('DJANGO_ENV') == 'production':
    username = os.getenv('PRODUCTION_SUPERUSER_USERNAME')
elif os.getenv('DJANGO_ENV') == 'staging':
    username = os.getenv('STAGING_SUPERUSER_USERNAME')
else:  # development
    username = os.getenv('DEVELOPMENT_SUPERUSER_USERNAME')
```

### Deployment Integration

Both commands run automatically during deployment:

```bash
# In deployment script
python manage.py setup_superuser        # Sync credentials
python manage.py create_super_tenant    # Ensure tenant exists
```

**Standard Django projects** typically create superusers manually or with a single `createsuperuser` command.

### References

- [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)
- [backend/apps/core/management/commands/setup_superuser.py](../backend/apps/core/management/commands/setup_superuser.py)
- [backend/apps/tenants/management/commands/create_super_tenant.py](../backend/apps/tenants/management/commands/create_super_tenant.py)

---

## 7. Directory Structure

### ❗ Differs from Common Practice

**Standard Django/React Monorepo:**
```
project/
├── backend/
├── frontend/
├── docs/
└── README.md
```

**ProjectMeats:**
```
ProjectMeats/
├── backend/              # Django API
├── frontend/             # React Web App
├── mobile/               # React Native (future)
├── shared/               # Cross-platform utilities
├── config/               # Centralized environment config
├── archived/             # Legacy infrastructure
├── docs/                 # Documentation
├── deploy/               # Deployment configurations
└── [many root-level docs and scripts]
```

### Unique Directories

#### `shared/`
**Purpose:** Cross-platform TypeScript/JavaScript utilities shared between frontend and mobile.

**Pattern:**
- `shared/utils.ts` - Source of truth for shared utilities
- `frontend/src/shared/` - Re-exports from `/shared`
- `mobile/src/shared/` - Re-exports from `/shared`

**Why:** Ensures consistency across web and mobile apps without code duplication.

**Standard projects** typically duplicate utility code or use npm packages.

#### `archived/`
**Purpose:** Stores legacy infrastructure code (Docker, Terraform) that's no longer actively used but kept for reference.

**Structure:**
```
archived/
├── code/                 # Archived code snippets
├── docs/                 # Outdated documentation
│   ├── implementation-summaries/
│   └── fixes/
└── infrastructure/       # Docker, Terraform configs
```

**Policy:**
- Don't delete - archive
- Move docs here after 3+ months of stability (for fixes)
- Current deployment uses DigitalOcean App Platform (no Docker/Terraform)

**Standard projects** usually delete old code or rely on git history.

#### `config/`
**Purpose:** Centralized environment configuration management.

**Contents:**
- `manage_env.py` - Environment setup script
- `environments/` - Environment templates

**Typical projects** put config in `backend/` or use scattered `.env.example` files.

### Root-Level Documentation

ProjectMeats has **many documentation files at the root level**:

```
README.md
CONTRIBUTING.md
CHANGELOG.md
LOCAL_DEVELOPMENT.md
QUICK_START.md
AUTHENTICATION_EXPLANATION.md
DEPLOYMENT_GUIDE.md
GUEST_MODE_IMPLEMENTATION.md
INVITE_ONLY_SYSTEM.md
MULTI_TENANCY_IMPLEMENTATION.md
[50+ more implementation summaries and fix documentation]
```

**Rationale:**
- Active bugs and fixes documented at root for visibility
- Implementation summaries for major features
- After 3+ months of stability, moved to `archived/docs/`

**Standard projects** keep most docs in `docs/` subdirectory.

### References

- [README.md](../README.md) (Project Structure section)
- [docs/DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

## 8. CI/CD and Automation

### ❗ Differs from Common Practice

**Standard GitHub Actions:**
- Run tests on PR
- Deploy on merge to main
- Manual approval for production

**ProjectMeats:**
- Automated PR creation between environments
- Migration validation in CI
- Database backup before deployments
- Environment validation scripts
- Automatic stale PR cleanup

### Unique CI/CD Features

#### 1. Automated Environment Promotion

**Workflow Files:**
- `.github/workflows/promote-dev-to-uat.yml`
- `.github/workflows/promote-uat-to-main.yml`

**Behavior:**
- Triggered automatically on merge to source branch
- Closes existing stale PRs before creating new one
- Creates fresh PR with latest commits
- Assigns reviewers
- Waits for manual approval

**Why:** Prevents duplicate PRs and ensures only the latest code is promoted.

#### 2. Migration Validation Script

**Location:** `.github/scripts/validate-migrations.sh`

**Checks:**
- Migration file syntax
- Dependency consistency
- Conflicting migrations
- Fresh database test

**Runs:** On every PR to main branches

**Why:** Prevents 90% of migration-related deployment failures.

#### 3. Database Backup Script

**Location:** `.github/scripts/backup-database.sh`

**Behavior:**
- Automatic backups before migrations
- Keeps last 7 backups
- Compresses to save space
- Integrated into deployment workflows

**Standard projects** often require manual backups.

#### 4. Environment Validation Script

**Location:** `.github/scripts/validate-environment.sh`

**Validates:**
- Required environment variables
- CORS/CSRF consistency
- Security settings
- Database configuration

**Runs:** Before deployment

**Why:** Catches configuration errors before they reach production.

### Workflow Organization

```
.github/
├── workflows/
│   ├── promote-dev-to-uat.yml       # Auto-promotion
│   ├── promote-uat-to-main.yml      # Auto-promotion
│   ├── deploy-*.yml                 # Deployment workflows
│   ├── test-*.yml                   # Testing workflows
│   └── cleanup-branches-tags.yml    # Automated cleanup
└── scripts/
    ├── validate-migrations.sh
    ├── validate-environment.sh
    └── backup-database.sh
```

### References

- [docs/workflows/unified-workflow.md](workflows/unified-workflow.md)
- [docs/workflows/cicd-infrastructure.md](workflows/cicd-infrastructure.md)
- [.github/workflows/README.md](../.github/workflows/README.md)

---

## 9. Pre-commit Hooks

### ❗ Differs from Common Practice

**Standard Pre-commit Hooks:**
- Code formatting (Black, Prettier)
- Linting (flake8, ESLint)
- Trailing whitespace removal

**ProjectMeats Pre-commit Hooks:**
All of the above, PLUS:
- **Migration validation** ⭐ (unique to ProjectMeats)
- **Unapplied migration detection** ⭐
- **Migration syntax checking** ⭐

### Installation

```bash
# Install pre-commit (included in requirements.txt)
pip install pre-commit

# Install the git hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

### Configuration

**File:** `.pre-commit-config.yaml`

**Key Hooks:**

1. **validate-django-migrations** (custom)
   - Runs `python manage.py makemigrations --check --dry-run`
   - Fails if unapplied migrations detected
   - Prevents CI failures from forgotten migrations

2. **check-migration-syntax** (custom)
   - Validates Python syntax in migration files
   - Catches migration errors before commit

3. **Standard hooks:**
   - Black (formatting)
   - isort (import sorting)
   - flake8 (linting)
   - Trailing whitespace, EOF fixes
   - Large file prevention
   - Merge conflict detection

### Why This Matters

**Problem:** Developers often forget to run `makemigrations` after changing models.

**Solution:** Pre-commit hook catches this automatically and prevents commit.

**Result:** PR CI checks pass on first try, deployment pipeline doesn't break.

**Standard Django projects** typically don't enforce migration validation at commit time.

### Frontend Pre-commit Hooks

**File:** `.pre-commit-config-frontend.yaml` (separate)

**Hooks:**
- Prettier formatting
- ESLint
- TypeScript type checking (optional)

**Note:** Frontend hooks are optional and separate to avoid slowing down backend-only changes.

### References

- [.pre-commit-config.yaml](../.pre-commit-config.yaml)
- [.github/copilot-instructions.md](../.github/copilot-instructions.md#code-quality--security-standards)

---

## 10. Testing Patterns

### ❗ Differs from Common Practice

**Standard Django Testing:**
```python
from django.test import TestCase

class CustomerTestCase(TestCase):
    def test_customer_creation(self):
        customer = Customer.objects.create(name="Test")
        self.assertEqual(customer.name, "Test")
```

**ProjectMeats Multi-Tenant Testing:**
```python
from django.test import TestCase
from apps.tenants.models import Tenant

class CustomerTestCase(TestCase):
    def setUp(self):
        # Create tenant for each test
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            schema_name="test_tenant"
        )
        
    def test_customer_creation(self):
        customer = Customer.objects.create(
            name="Test",
            tenant=self.tenant  # Always include tenant
        )
        self.assertEqual(customer.name, "Test")
        self.assertEqual(customer.tenant, self.tenant)
```

### Multi-Tenant Testing Requirements

For models in `TENANT_APPS`, tests must:

1. **Create tenant(s) in setUp()**
2. **Associate all test objects with a tenant**
3. **Test tenant isolation** - verify users can't access other tenants' data
4. **Test tenant filtering** - verify querysets are properly filtered

### Test Organization

**Backend:**
```
apps/customers/tests/
├── __init__.py
├── test_models.py          # Model logic and validation
├── test_views.py           # View layer (if using Django views)
├── test_serializers.py     # DRF serializers
├── test_api_endpoints.py   # API integration tests
└── test_tenant_isolation.py  # Multi-tenancy tests (unique to ProjectMeats)
```

**Frontend:**
```
src/components/CustomerList/
├── CustomerList.tsx
├── CustomerList.test.tsx
└── CustomerList.stories.tsx  # Storybook (unique pattern)
```

### Testing Multi-Tenancy

**Example tenant isolation test:**

```python
def test_user_cannot_access_other_tenant_data(self):
    # Create two tenants
    tenant1 = Tenant.objects.create(name="Tenant 1", schema_name="tenant1")
    tenant2 = Tenant.objects.create(name="Tenant 2", schema_name="tenant2")
    
    # Create customers for each tenant
    customer1 = Customer.objects.create(name="Customer 1", tenant=tenant1)
    customer2 = Customer.objects.create(name="Customer 2", tenant=tenant2)
    
    # User from tenant1 should only see tenant1 customers
    user = User.objects.create(username="user1", tenant=tenant1)
    self.client.force_authenticate(user=user)
    
    response = self.client.get('/api/v1/customers/')
    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]['name'], "Customer 1")
```

### Coverage Requirements

**Standard projects:** ~70-80% coverage

**ProjectMeats:**
- Overall: 80%+ (same as standard)
- Critical paths: **95%+** (higher than standard)
- Multi-tenant features: **100%** tenant isolation tests (unique requirement)

### Test Commands

```bash
# Run all tests
make test

# Backend only
make test-backend
cd backend && python manage.py test

# With coverage
cd backend && coverage run --source='.' manage.py test
coverage report
coverage html

# Frontend only
make test-frontend
cd frontend && npm test
```

### References

- [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
- [.github/copilot-instructions.md](../.github/copilot-instructions.md#-testing-strategy--coverage)

---

## Quick Reference: ProjectMeats vs Standard Practices

| Aspect | Standard Practice | ProjectMeats Approach |
|--------|------------------|----------------------|
| **Multi-tenancy** | Single tenant or simple foreign keys | Dual system: django-tenants + custom shared-schema |
| **Migrations** | `python manage.py migrate` | `python manage.py migrate_schemas` for TENANT_APPS |
| **Branches** | feature → develop → main | feature → development → UAT → main |
| **Environment Config** | Manual `.env` files | Centralized `config/manage_env.py` |
| **Superuser Creation** | `createsuperuser` command | `setup_superuser` + `create_super_tenant` |
| **Admin Classes** | Extend `admin.ModelAdmin` | Extend `TenantFilteredAdmin` for tenant models |
| **PR Promotion** | Manual PR creation | Automated workflows with stale PR cleanup |
| **Pre-commit Hooks** | Formatting + linting | + Migration validation (unique) |
| **Directory Structure** | Minimal root docs | Many root-level docs + `archived/` directory |
| **Testing** | Standard test cases | Must test tenant isolation for all tenant-aware models |

---

## Getting Started Checklist

If you're new to ProjectMeats, complete these steps:

- [ ] Read this document completely
- [ ] Read [.github/copilot-instructions.md](../.github/copilot-instructions.md)
- [ ] Read [branch-workflow-checklist.md](../branch-workflow-checklist.md)
- [ ] Read [MIGRATION_BEST_PRACTICES.md](MIGRATION_BEST_PRACTICES.md)
- [ ] Set up environment: `python config/manage_env.py setup development`
- [ ] Install pre-commit hooks: `pre-commit install`
- [ ] Run tests to verify setup: `make test`
- [ ] Review an existing PR to see conventions in action
- [ ] Create a small test branch to practice the workflow

---

## Key Takeaways

1. **Multi-tenancy is everywhere** - Always think about tenant context
2. **Use migrate_schemas** - Not `migrate` for TENANT_APPS
3. **Follow the three-branch workflow** - Never push directly to UAT or main
4. **Let automation work** - Don't create manual promotion PRs
5. **Extend TenantFilteredAdmin** - For all tenant-aware admin classes
6. **Environment-specific credentials** - Use DEVELOPMENT_, STAGING_, PRODUCTION_ prefixes
7. **Pre-commit hooks catch mistakes** - Run `pre-commit install` first thing
8. **Test tenant isolation** - Always test that tenants can't access each other's data
9. **Archive, don't delete** - Move old code/docs to `archived/`
10. **Centralized configuration** - Use `config/manage_env.py` for environment setup

---

## Questions or Clarifications?

If you encounter patterns not documented here or need clarification:

1. Check [.github/copilot-instructions.md](../.github/copilot-instructions.md) for detailed guidelines
2. Search [docs/DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for related documentation
3. Review [copilot-log.md](../copilot-log.md) for historical context and lessons learned
4. Open a GitHub Discussion for architectural questions
5. Create an issue if documentation is unclear or incomplete

---

**Remember:** These conventions exist for good reasons - they solve specific problems we encountered while building a multi-tenant SaaS platform with complex deployment requirements. Understanding *why* they exist will help you work more effectively with the codebase.

**Last Updated:** 2024-12-01
