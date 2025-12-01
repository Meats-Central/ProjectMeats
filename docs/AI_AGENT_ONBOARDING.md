# AI Agent Onboarding Guide

**Last Updated**: December 1, 2024  
**Purpose**: Essential knowledge for AI agents to be immediately productive in the ProjectMeats codebase

---

## 🎯 Quick Start Essentials

### What is ProjectMeats?
A **multi-tenant SaaS platform** for meat sales brokers, managing suppliers, customers, purchase orders, and business operations. Migrated from PowerApps to a modern Django + React stack.

### Technology Stack
- **Backend**: Django 4.2.7 + Django REST Framework + PostgreSQL
- **Multi-tenancy**: django-tenants (schema-based isolation)
- **Frontend**: React 18.2.0 + TypeScript + Styled Components
- **Mobile**: React Native
- **Testing**: pytest-django (95+ tests), Jest/React Testing Library
- **Deployment**: SSH to Digital Ocean (dev/UAT/prod environments)
- **CI/CD**: GitHub Actions with strict branch promotion workflow

---

## 🚨 Critical Rules (Must Follow)

### Branch Workflow - NEVER VIOLATE THIS
```
feature/fix branch → development → UAT → main
        ↓              ↓          ↓       ↓
     Local PR     Auto PR    Auto PR   Production
```

**What you MUST do:**
1. ✅ Create feature/fix branch from `development`
2. ✅ PR to `development` first (with review)
3. ✅ Let automated workflows promote to UAT
4. ✅ Let automated workflows promote to main

**What you MUST NEVER do:**
1. ❌ Push directly to `UAT` or `main`
2. ❌ Skip the `development` branch
3. ❌ Bypass automated promotion workflows
4. ❌ Force push to protected branches

**Branch Naming**: `<type>/<description>`
- Valid types: `feature/`, `fix/`, `chore/`, `refactor/`, `hotfix/`, `docs/`, `test/`, `perf/`
- Example: `feature/add-supplier-export`, `fix/auth-token-expiry`

**PR Title Format**: `<type>(<scope>): <description>`
- Example: `feat(suppliers): add export functionality`
- Example: `fix(auth): resolve token expiration handling`

### Pre-commit Hooks - REQUIRED
```bash
# Run this ONCE after cloning
pre-commit install
```

**Why?** Validates Django migrations on every commit to prevent CI failures.

### Database Configuration - CRITICAL
- **Development**: Uses `django_tenants.postgresql_backend` (not standard PostgreSQL)
- **Production**: Automatically uses django-tenants backend
- **Never use**: `django.db.backends.postgresql` directly - it breaks multi-tenancy

---

## 📁 Repository Structure (Critical Paths)

```
ProjectMeats/
├── backend/
│   ├── apps/                           # 15 business apps
│   │   ├── tenants/                   # Multi-tenancy (Client, Domain, Tenant)
│   │   ├── core/                      # Shared utilities, base models
│   │   ├── suppliers/                 # Supplier management
│   │   ├── customers/                 # Customer relationships
│   │   ├── purchase_orders/           # Order processing
│   │   ├── accounts_receivables/      # Payments
│   │   ├── ai_assistant/              # AI chat & document processing
│   │   └── [others]/                  # plants, contacts, products, etc.
│   ├── projectmeats/
│   │   ├── settings/                  # Environment-specific settings
│   │   │   ├── base.py               # SHARED_APPS + TENANT_APPS
│   │   │   ├── development.py        # Dev config
│   │   │   ├── staging.py            # UAT config
│   │   │   └── production.py         # Prod config
│   │   ├── urls.py                   # API routing
│   │   └── health.py                 # Health checks
│   ├── manage.py                     # Django management
│   └── requirements.txt              # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/               # Reusable UI components
│   │   ├── pages/                    # Route pages
│   │   ├── services/                 # API clients
│   │   │   ├── api.ts               # Base API client
│   │   │   └── businessApi.ts       # Business entity APIs
│   │   ├── contexts/                # React contexts (tenant, auth)
│   │   └── types/                   # TypeScript types
│   ├── package.json                 # Node dependencies
│   └── tsconfig.json                # TypeScript config
│
├── config/                            # Centralized environment config
│   ├── environments/                 # Env-specific .env files
│   │   ├── development.env
│   │   ├── staging.env
│   │   └── production.env
│   └── manage_env.py                # Environment setup tool
│
├── docs/                             # 111 documentation files
│   ├── README.md                    # Documentation hub
│   ├── MIGRATION_GUIDE.md           # Database migrations
│   ├── AUTHENTICATION_GUIDE.md      # Auth & permissions
│   ├── TROUBLESHOOTING.md           # Common issues
│   ├── BACKEND_ARCHITECTURE.md      # Django patterns
│   ├── FRONTEND_ARCHITECTURE.md     # React patterns
│   └── [many more guides]
│
├── .github/
│   ├── workflows/                   # CI/CD pipelines
│   │   ├── 11-dev-deployment.yml   # Dev deployment
│   │   ├── 12-uat-deployment.yml   # UAT deployment
│   │   ├── 13-prod-deployment.yml  # Prod deployment
│   │   ├── promote-dev-to-uat.yml  # Auto PR dev→UAT
│   │   └── promote-uat-to-main.yml # Auto PR UAT→main
│   └── copilot-instructions.md     # Full Copilot instructions
│
├── Makefile                         # Development commands
├── start_dev.sh                     # Start all servers
├── stop_dev.sh                      # Stop all servers
└── branch-workflow-checklist.md    # Detailed branch guide
```

---

## 🔧 Essential Commands

### Environment Setup
```bash
# Option 1: Automated (Recommended)
./start_dev.sh                              # Starts PostgreSQL + Django + React

# Option 2: Centralized Configuration
python config/manage_env.py setup development
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
pre-commit install
make migrate
make dev
```

### Development
```bash
make start                  # Start all servers (uses start_dev.sh)
make stop                   # Stop all servers
make backend                # Django only (port 8000)
make frontend               # React only (port 3000)
make migrate                # Apply migrations
make migrations             # Create migrations
make shell                  # Django shell
```

### Testing
```bash
make test                   # All tests
make test-backend           # Django tests only
make test-frontend          # React tests only
```

### Code Quality
```bash
make format                 # Format Python (black, isort)
make lint                   # Lint Python (flake8)
pre-commit run --all-files  # Run all pre-commit hooks
```

### Database Management
```bash
make superuser              # Create/update superuser + root tenant
make sync-superuser         # Sync superuser password from env
python manage.py migrate_schemas --shared  # Migrate shared apps
python manage.py migrate_schemas           # Migrate tenant apps
```

### Deployment Testing
```bash
make deploy-test            # Test deployment config
make deploy-check           # Comprehensive validation
make health-check URL=https://app.url  # Check live health
```

---

## 🏗️ Multi-Tenancy Architecture

### Critical Concepts

**Two Systems (Both Active):**
1. **Schema-Based** (django-tenants): Each tenant gets own PostgreSQL schema
2. **Shared-Schema** (legacy): Tenants share schema with FK isolation

**Models You'll Encounter:**
- `Client` + `Domain` - Schema-based tenants (django-tenants)
- `Tenant` + `TenantDomain` + `TenantUser` - Shared-schema tenants (legacy)

### Settings Structure (CRITICAL)

**In `backend/projectmeats/settings/base.py`:**
```python
SHARED_APPS = [
    "django_tenants",           # MUST BE FIRST
    "django.contrib.admin",
    "django.contrib.auth",
    # ... core apps
    "apps.core",
    "apps.tenants",             # Tenant management
]

TENANT_APPS = [
    "django.contrib.admin",     # Tenant-specific admin
    "django.contrib.auth",      # Tenant-specific users
    # ... business apps
    "apps.suppliers",
    "apps.customers",
    "apps.purchase_orders",
    # ... etc
]

INSTALLED_APPS = SHARED_APPS + [
    app for app in TENANT_APPS if app not in SHARED_APPS
]
```

### Database Backend
```python
# CORRECT - Development
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",  # Required!
        "NAME": "projectmeats_dev",
        # ...
    }
}

# WRONG - This breaks multi-tenancy
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",  # Don't use this!
    }
}
```

### Middleware Order (CRITICAL)
```python
MIDDLEWARE = [
    "django_tenants.middleware.TenantMainMiddleware",  # MUST BE FIRST
    "django.middleware.security.SecurityMiddleware",
    # ... other middleware
    "apps.tenants.middleware.TenantMiddleware",  # Custom tenant features
]
```

---

## 🔐 Authentication & Permissions

### Superuser Management

**Environment-Specific Variables:**
```bash
# Development (in config/environments/development.env)
DEVELOPMENT_SUPERUSER_USERNAME=admin
DEVELOPMENT_SUPERUSER_EMAIL=admin@meatscentral.com
DEVELOPMENT_SUPERUSER_PASSWORD=DevAdmin123!SecurePass

# Staging (GitHub Secrets: uat2-backend)
STAGING_SUPERUSER_USERNAME=...
STAGING_SUPERUSER_EMAIL=...
STAGING_SUPERUSER_PASSWORD=...

# Production (GitHub Secrets: prod2-backend)
PRODUCTION_SUPERUSER_USERNAME=...
PRODUCTION_SUPERUSER_EMAIL=...
PRODUCTION_SUPERUSER_PASSWORD=...
```

**Management Commands:**
```bash
# Sync credentials from environment (runs on every deploy)
make sync-superuser
cd backend && python manage.py setup_superuser

# Create superuser + root tenant (idempotent)
make superuser
cd backend && python manage.py create_super_tenant
```

### Guest Mode
- **Demo users**: Allow access without authentication
- **Permissions**: Read-only for specific entities
- **Implementation**: `apps.tenants.permissions.IsGuestOrAuthenticated`

---

## 🧪 Testing Strategy

### Backend Testing (pytest-django)
```bash
cd backend

# Run all tests
python manage.py test

# Run specific app
python manage.py test apps.suppliers

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/suppliers/tests/test_models.py
```

**Test Organization:**
```
apps/suppliers/
├── tests/
│   ├── __init__.py
│   ├── test_models.py      # Model tests
│   ├── test_views.py       # View/API tests
│   ├── test_serializers.py # Serializer tests
│   └── factories.py        # Factory Boy fixtures
```

**Test Patterns:**
```python
from django.test import TestCase
from rest_framework.test import APITestCase

class SupplierModelTest(TestCase):
    def test_creation(self):
        # Test model creation
        pass

class SupplierAPITest(APITestCase):
    def test_list_suppliers(self):
        # Test API endpoint
        response = self.client.get('/api/v1/suppliers/')
        self.assertEqual(response.status_code, 200)
```

### Frontend Testing (Jest + React Testing Library)
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- src/components/Suppliers.test.tsx
```

---

## 🔍 Common Development Tasks

### Adding a New Django App
```bash
cd backend
python manage.py startapp new_app apps/new_app

# 1. Add to TENANT_APPS in settings/base.py
TENANT_APPS = [
    # ...
    "apps.new_app",
]

# 2. Create models.py
# 3. Create serializers.py
# 4. Create views.py
# 5. Create urls.py
# 6. Register in projectmeats/urls.py
# 7. Create migrations
python manage.py makemigrations new_app

# 8. Apply migrations
python manage.py migrate_schemas
```

### Adding a New API Endpoint
```bash
# 1. Define model (if needed)
# apps/entity/models.py

# 2. Create serializer
# apps/entity/serializers.py
from rest_framework import serializers

class EntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = '__all__'

# 3. Create ViewSet
# apps/entity/views.py
from rest_framework import viewsets

class EntityViewSet(viewsets.ModelViewSet):
    queryset = Entity.objects.all()
    serializer_class = EntitySerializer

# 4. Register URL
# apps/entity/urls.py
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('entities', EntityViewSet)

# 5. Include in main urls.py
# projectmeats/urls.py
path('api/v1/', include('apps.entity.urls')),
```

### Creating Database Migration
```bash
cd backend

# 1. Modify models.py
# 2. Create migration
python manage.py makemigrations app_name

# 3. Check migration
python manage.py sqlmigrate app_name 0001

# 4. Apply to shared schema
python manage.py migrate_schemas --shared

# 5. Apply to all tenant schemas
python manage.py migrate_schemas
```

### Adding Frontend Component
```typescript
// 1. Create component file
// frontend/src/components/NewComponent.tsx

import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  // styles
`;

export const NewComponent: React.FC<Props> = ({ prop }) => {
  return <Container>{/* JSX */}</Container>;
};

// 2. Create test file
// frontend/src/components/NewComponent.test.tsx

import { render, screen } from '@testing-library/react';
import { NewComponent } from './NewComponent';

describe('NewComponent', () => {
  it('renders correctly', () => {
    render(<NewComponent />);
    // assertions
  });
});

// 3. Export from index
// frontend/src/components/index.ts
export * from './NewComponent';
```

---

## 🐛 Debugging & Troubleshooting

### Common Issues

**1. Migration Errors**
```bash
# Check migration status
python manage.py showmigrations

# Reset migrations (DANGEROUS - dev only)
python manage.py migrate_schemas --shared --fake-initial
python manage.py migrate_schemas --fake-initial

# See MIGRATION_GUIDE.md for comprehensive help
```

**2. Multi-tenancy Issues**
```bash
# List all tenants
python manage.py shell
>>> from apps.tenants.models import Client
>>> Client.objects.all()

# Create test tenant
python manage.py create_tenant \
  --schema-name=test \
  --name="Test Corp" \
  --domain=test.localhost
```

**3. Authentication Errors**
```bash
# Verify DEBUG setting
python manage.py shell
>>> from django.conf import settings
>>> print(f"DEBUG: {settings.DEBUG}")

# Reset superuser password
python manage.py changepassword admin

# Sync from environment
make sync-superuser
```

**4. Frontend Build Errors**
```bash
cd frontend

# Clear cache
rm -rf node_modules package-lock.json
npm install

# Type check
npm run type-check

# Lint
npm run lint
```

### Debug Mode
```bash
# Backend - Enable DEBUG logging
# In settings/development.py
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

# Frontend - Enable verbose logging
# In .env.local
REACT_APP_DEBUG=true
```

---

## 📚 Key Documentation Files

**Read These First:**
- `README.md` - Project overview, quick start
- `docs/README.md` - Documentation hub
- `.github/copilot-instructions.md` - Detailed Copilot guidelines
- `branch-workflow-checklist.md` - Branch workflow details

**Essential Guides:**
- `docs/MIGRATION_GUIDE.md` - Database migrations with django-tenants
- `docs/AUTHENTICATION_GUIDE.md` - Auth, permissions, superuser
- `docs/TROUBLESHOOTING.md` - Common issues and solutions
- `docs/BACKEND_ARCHITECTURE.md` - Django patterns and structure
- `docs/FRONTEND_ARCHITECTURE.md` - React patterns and components

**Workflow & Deployment:**
- `docs/DEPLOYMENT_GUIDE.md` - Deployment process
- `docs/ENVIRONMENT_GUIDE.md` - Environment configuration
- `.github/workflows/README.md` - CI/CD workflows

**Reference:**
- `CONTRIBUTING.md` - Contribution guidelines
- `docs/TESTING_STRATEGY.md` - Testing approaches
- `docs/MULTI_TENANCY_GUIDE.md` - Multi-tenancy deep dive

---

## 🎓 Best Practices

### Code Style
- **Python**: PEP 8, formatted with Black, sorted with isort
- **TypeScript**: ESLint + Prettier configuration
- **Commits**: Conventional Commits format
- **PRs**: Clear description, linked issues, review required

### Security
- **Never commit secrets** - Use environment variables
- **Always validate input** - Use Django/DRF validators
- **Check permissions** - Use DRF permission classes
- **Sanitize data** - Use parameterized queries
- **Review django-tenants isolation** - Ensure tenant data separation

### Performance
- **Use select_related/prefetch_related** - Avoid N+1 queries
- **Index database fields** - Add db_index=True for lookups
- **Paginate large datasets** - Use DRF pagination
- **Cache expensive queries** - Use Django cache framework
- **Optimize React renders** - Use React.memo, useMemo, useCallback

### Testing
- **Write tests first** - TDD when possible
- **Test edge cases** - Not just happy paths
- **Mock external services** - Use pytest fixtures
- **Maintain 80%+ coverage** - Currently at 95+ for backend
- **Run tests before commit** - Pre-commit hooks help

---

## 🚀 Deployment Workflow

### Environments
1. **Development** - Local/dev branch, PostgreSQL, DEBUG=True
2. **UAT/Staging** - uat2-backend.ondigitalocean.app, DEBUG=False
3. **Production** - prod2-backend.ondigitalocean.app, DEBUG=False

### Deployment Steps
```bash
# 1. Create feature branch
git checkout -b feature/new-feature development

# 2. Make changes, test locally
make test

# 3. Commit with conventional format
git commit -m "feat(scope): description"

# 4. Push and create PR to development
git push origin feature/new-feature

# 5. After merge to development:
#    - Automated PR to UAT created by promote-dev-to-uat.yml
#    - Review and merge to UAT
#    - Test in UAT environment

# 6. After UAT approval:
#    - Automated PR to main created by promote-uat-to-main.yml
#    - Review and merge to main
#    - Deploys to production

# NEVER skip steps or push directly to UAT/main!
```

---

## 💡 Quick Tips for AI Agents

1. **Always start by reading the issue description carefully**
2. **Check existing patterns** in similar apps before creating new code
3. **Run tests early and often** - Don't wait until the end
4. **Follow the branch workflow strictly** - It's enforced by CI/CD
5. **Use type hints** in Python and TypeScript for better code clarity
6. **Document non-obvious decisions** - Future you (or AI) will thank you
7. **Check multi-tenancy implications** - Will this affect tenant isolation?
8. **Validate migrations** - Pre-commit hooks check, but test manually too
9. **Review security impact** - Does this expose sensitive data?
10. **Keep changes focused** - Small PRs are easier to review

---

## 📞 Getting Help

- **Documentation Hub**: `docs/README.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`
- **Branch Workflow**: `branch-workflow-checklist.md`
- **Copilot Instructions**: `.github/copilot-instructions.md`
- **Issue Templates**: `.github/ISSUE_TEMPLATE/`

---

**Last Updated**: December 1, 2024  
**Maintained by**: ProjectMeats Team  
**Version**: 1.0.0
