# ProjectMeats

A business management application for meat sales brokers, migrated from PowerApps to Django REST Framework (backend) and React TypeScript (frontend). Manages suppliers, customers, purchase orders, accounts receivables, and related business entities with an AI Assistant featuring Copilot-style UI and document processing.

## 🚀 Quick Start (5 Minutes)

**🎯 TL;DR - Start Everything Now:**
```bash
./start_dev.sh
```

**📖 Essential Documentation:**
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - Setup instructions
- **[DEVELOPER_WORKFLOWS.md](DEVELOPER_WORKFLOWS.md)** - Builds, tests, debugging ⭐ NEW
- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Deployment instructions

**Prerequisites**: Python 3.9+, Node.js 16+, PostgreSQL 12+

### Quick Setup Options

```bash
# Option 1: Automated Startup Script (Recommended)
./start_dev.sh          # Starts PostgreSQL + Backend + Frontend
./stop_dev.sh           # Stops all servers

# Option 2: Using Make
make start              # Uses start_dev.sh
make stop               # Uses stop_dev.sh

# Option 3: Automated Setup
python setup_env.py

# Option 4: Centralized Environment Configuration
python config/manage_env.py setup development
```

The startup script (`start_dev.sh`) handles everything: PostgreSQL setup, dependencies, migrations, and server startup. See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for troubleshooting and advanced options.

## 🏗️ Technology Stack

- **Backend**: Django 4.2.7 + Django REST Framework + PostgreSQL (recommended) or SQLite (fallback)
- **Multi-tenancy**: django-tenants for schema-based isolation + shared-schema approach
- **Frontend**: React 18.2.0 + TypeScript + Styled Components  
- **AI Assistant**: OpenAI GPT-4 integration with modern Copilot-style interface
- **Authentication**: Django User system with profile management
- **API**: RESTful endpoints with OpenAPI documentation
- **Testing**: 95+ comprehensive backend tests

## 📁 Project Structure

```
ProjectMeats3/
├── backend/                    # Django REST Framework API
│   ├── apps/                  # Business entities (9 complete)
│   │   ├── accounts_receivables/  # Customer payments
│   │   ├── suppliers/            # Supplier management
│   │   ├── customers/            # Customer relationships
│   │   ├── purchase_orders/      # Order processing
│   │   ├── plants/              # Processing facilities
│   │   ├── contacts/            # Contact management
│   │   └── core/                # Shared utilities
│   └── requirements.txt
├── frontend/                   # React TypeScript application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── screens/           # Main application screens
│   │   ├── services/         # API communication
│   │   └── shared/           # Shared utilities (re-exports from /shared)
│   └── package.json
├── mobile/                     # React Native mobile app
│   └── src/
│       └── shared/            # Shared utilities (re-exports from /shared)
├── shared/                     # Cross-platform shared utilities
│   └── utils.ts              # Common TypeScript utilities
├── docs/                      # Documentation
├── archived/                  # Archived files (legacy docs, outdated code)
│   ├── docs/                  # Archived documentation
│   └── code/                  # Archived code/config files
└── config/                    # Centralized configuration
```

## 🚀 Quick Setup

### Recommended Setup (Centralized Configuration)
```bash
# 0. Set up PostgreSQL (recommended for environment parity)
# Option A: Install PostgreSQL locally
# macOS: brew install postgresql
# Ubuntu: sudo apt-get install postgresql postgresql-contrib
# Windows: Download from https://www.postgresql.org/download/windows/

# Option B: Use Docker
# docker run --name projectmeats-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15

# 1. Set up environment using centralized configuration
python config/manage_env.py setup development

# 2. Configure database (edit config/environments/development.env)
# For PostgreSQL:
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=projectmeats_dev
# DB_USER=postgres
# DB_PASSWORD=postgres
# DB_HOST=localhost
# DB_PORT=5432
#
# For SQLite (fallback):
# DB_ENGINE=django.db.backends.sqlite3

# 3. Install dependencies  
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 4. Set up pre-commit hooks (REQUIRED)
pre-commit install

# 5. Run database migrations
cd backend && python manage.py migrate && cd ..

# 6. Start development servers
make dev
```

### Alternative Setup (Legacy)
```bash
# Use the legacy setup script
python setup_env.py
```

### Environment Configuration

This project uses a **centralized environment configuration system** for better maintainability:

- **📁 config/environments/** - Environment-specific configurations (dev/staging/prod)
- **🔧 config/manage_env.py** - Environment management script
- **📖 docs/ENVIRONMENT_GUIDE.md** - Complete configuration guide

**Quick Commands:**
```bash
python config/manage_env.py setup development  # Set up dev environment
python config/manage_env.py setup staging      # Set up staging environment  
python config/manage_env.py setup production   # Set up production environment
python config/manage_env.py validate           # Validate current configuration
```

**Prerequisites**: Python 3.9+, Node.js 16+, Git

### Option 1: Quick Setup (Automated)
```bash
# 1. Clone and enter directory
git clone https://github.com/Meats-Central/ProjectMeats3.git
cd ProjectMeats3

# 2. Run setup (handles everything automatically)
python setup_env.py

# 3. Set up pre-commit hooks (REQUIRED - run this after setup)
pre-commit install

# 4. Start development servers
make dev
# Windows: run backend and frontend in separate terminals
```

### Option 2: Centralized Environment Management
```bash
# 1. Set up environment using centralized configuration
python config/manage_env.py setup development

# 2. Install dependencies  
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 3. Set up pre-commit hooks (REQUIRED)
pre-commit install

# 4. Run database migrations
cd backend && python manage.py migrate && cd ..

# 5. Start development servers
make dev
```

**Access your application:**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

> **Note**: Default superuser credentials are set via environment variables. See `config/environments/development.env` for the `DEVELOPMENT_SUPERUSER_USERNAME`, `DEVELOPMENT_SUPERUSER_EMAIL`, and `DEVELOPMENT_SUPERUSER_PASSWORD` settings.

## 🔒 Pre-commit Hooks (REQUIRED)

**⚠️ CRITICAL**: After cloning the repository, you **MUST** run `pre-commit install` to set up Git hooks that prevent common errors.

```bash
# Install pre-commit hooks (run once after cloning)
pre-commit install
```

### What the hooks do:
- **Code formatting**: Automatically format Python code with Black and isort
- **Code quality**: Check Python syntax and style with flake8
- **Migration validation**: **Validate Django migrations on every commit** to prevent CI failures
- **File checks**: Prevent large files, merge conflicts, and syntax errors

### Why this is required:
The migration validation hook runs `python manage.py makemigrations --check --dry-run` on every commit. This **prevents CI pipeline failures** by ensuring:
1. All model changes have corresponding migration files
2. No unapplied migrations exist before pushing code
3. Migration files are committed with model changes

**If you skip this step**, your PRs will fail CI checks when unapplied migrations are detected.

### Testing your hooks:
```bash
# Test pre-commit hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run validate-django-migrations
```

## 🏢 Multi-Tenancy Configuration

ProjectMeats implements a **dual multi-tenancy architecture** using django-tenants for maximum flexibility:

### Architecture Overview

1. **Schema-Based Multi-Tenancy** (django-tenants)
   - Complete data isolation using PostgreSQL schemas
   - Each tenant gets its own database schema
   - Models: `Client` and `Domain` (inheriting from `TenantMixin` and `DomainMixin`)
   - Best for: Enterprise deployments requiring strict data isolation

2. **Shared-Schema Multi-Tenancy** (Legacy/Custom)
   - Data isolation via tenant foreign keys
   - All tenants share the same database schema
   - Models: `Tenant`, `TenantUser`, and `TenantDomain`
   - Best for: Simpler deployments and backward compatibility

### Django Settings Structure

The multi-tenancy settings are split between **SHARED_APPS** and **TENANT_APPS** as required by django-tenants:

**SHARED_APPS** (in `backend/projectmeats/settings/base.py`):
```python
SHARED_APPS = [
    "django_tenants",  # Must be first
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    # ... core Django apps
    "apps.core",
    "apps.tenants",  # Tenant management
]
```

**TENANT_APPS** (tenant-specific data):
```python
TENANT_APPS = [
    "django.contrib.admin",  # Tenant-specific admin
    "django.contrib.auth",   # Tenant-specific users
    # ... business apps
    "apps.suppliers",
    "apps.customers",
    "apps.purchase_orders",
    # ... other tenant-specific apps
]
```

### Middleware Configuration

The middleware stack includes django-tenants middleware for schema-based routing:

```python
MIDDLEWARE = [
    "django_tenants.middleware.TenantMainMiddleware",  # Must be first
    # ... other middleware
    "apps.tenants.middleware.TenantMiddleware",  # Custom middleware for additional features
]
```

### Database Configuration

**Development** (`projectmeats/settings/development.py`):
```python
# PostgreSQL with django-tenants backend
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",  # Required for schema-based multi-tenancy
        "NAME": "projectmeats_dev",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

**Production** (`projectmeats/settings/production.py`):
```python
# Automatically uses django_tenants.postgresql_backend when DATABASE_URL contains PostgreSQL
```

### Environment Variables for Multi-Tenancy

Configure these in your environment files (`config/environments/development.env`):

```bash
# Database Engine (automatically converted to django_tenants.postgresql_backend)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=projectmeats_dev
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### Tenant Models Reference

| Model | Purpose | Database Table |
|-------|---------|---------------|
| `Client` | Schema-based tenant (django-tenants) | `tenants_client` |
| `Domain` | Domain routing for Client | `tenants_domain` |
| `Tenant` | Shared-schema tenant (legacy) | `tenants_tenant` |
| `TenantDomain` | Domain routing for Tenant | `tenants_tenantdomain` |
| `TenantUser` | User-tenant associations | `tenants_tenant_user` |

### Creating Tenants

**Schema-Based Tenant:**
```python
from apps.tenants.models import Client, Domain

# Create client with schema
client = Client.objects.create(
    schema_name="acme_corp",
    name="ACME Corporation"
)

# Add domain
Domain.objects.create(
    domain="acme.example.com",
    tenant=client,
    is_primary=True
)
```

**Shared-Schema Tenant:**
```bash
# Using management command
python manage.py create_tenant \
    --schema-name=acme \
    --name="ACME Corp" \
    --domain=acme.example.com
```

For more details, see:
- [Multi-Tenancy Implementation Guide](MULTI_TENANCY_IMPLEMENTATION.md)
- [Django-Tenants Documentation](https://django-tenants.readthedocs.io/)

## 👤 Superuser Management

The application provides two management commands for superuser handling with environment-specific configuration.

### `setup_superuser` - Password & Credential Synchronization

Syncs superuser credentials (username, email, password) from environment-specific variables during deployment. **Always updates credentials** when user exists.

```bash
# Sync superuser credentials from environment
make sync-superuser

# Or directly (for development)
cd backend && DJANGO_ENV=development python manage.py setup_superuser
```

**Environment-Specific Variables:**

| Environment | Username Variable | Email Variable | Password Variable |
|-------------|-------------------|----------------|-------------------|
| Development | `DEVELOPMENT_SUPERUSER_USERNAME` | `DEVELOPMENT_SUPERUSER_EMAIL` | `DEVELOPMENT_SUPERUSER_PASSWORD` |
| Staging/UAT | `STAGING_SUPERUSER_USERNAME` | `STAGING_SUPERUSER_EMAIL` | `STAGING_SUPERUSER_PASSWORD` |
| Production | `PRODUCTION_SUPERUSER_USERNAME` | `PRODUCTION_SUPERUSER_EMAIL` | `PRODUCTION_SUPERUSER_PASSWORD` |

**Use Cases:**
- ✅ Deployment automation (runs on every deploy)
- ✅ Password rotation
- ✅ Dynamic username/email configuration per environment
- ✅ Environment-specific credential management

### `create_super_tenant` - Full Tenant Setup

Creates superuser, root tenant, and links them together. Idempotent and safe to run multiple times.

```bash
# Create or update superuser and tenant
make superuser

# Or directly
cd backend && python manage.py create_super_tenant
```

**Environment Configuration:**

**Development Environment:**
```bash
# Set in config/environments/development.env
DEVELOPMENT_SUPERUSER_USERNAME=admin
DEVELOPMENT_SUPERUSER_EMAIL=admin@meatscentral.com
DEVELOPMENT_SUPERUSER_PASSWORD=DevAdmin123!SecurePass
```

**Staging/Production Environments:**
Set these as GitHub Secrets in respective environments (`uat2-backend`, `prod2-backend`):
- `STAGING_SUPERUSER_USERNAME` / `PRODUCTION_SUPERUSER_USERNAME`
- `STAGING_SUPERUSER_EMAIL` / `PRODUCTION_SUPERUSER_EMAIL`
- `STAGING_SUPERUSER_PASSWORD` / `PRODUCTION_SUPERUSER_PASSWORD`

**Deployment Integration:**

Both commands run automatically during deployment:
1. `setup_superuser` - Syncs credentials from environment
2. `create_super_tenant` - Ensures tenant infrastructure exists

**For detailed configuration:** See [Environment Variables Reference](docs/environment-variables.md)

## 🔧 Development Guide

### Technology Stack
- **Backend**: Django 4.2.7 + REST Framework + SQLite/PostgreSQL
- **Frontend**: React 18.2.0 + TypeScript + Styled Components
- **AI Assistant**: OpenAI GPT-4 + Copilot-style interface
- **Testing**: 95+ backend tests

### Project Structure
```
ProjectMeats3/
├── backend/           # Django API with 9 business apps
├── frontend/          # React TypeScript application
├── Makefile          # Development commands
├── setup_env.py        # Development environment setup script
```

### Essential Commands
```bash
# Development
make dev              # Start both servers
make backend          # Backend only
make frontend         # Frontend only

# Database
make migrate          # Apply migrations
make migrations       # Create migrations

# Testing & Quality
make test             # Run all tests
make format           # Format code
make lint             # Lint code
make clean            # Clean artifacts
```

### AI Assistant Features
- **Chat Interface**: Natural language business queries
- **Document Processing**: Drag & drop file upload and analysis
- **Entity Extraction**: Automatic data extraction from documents
- **Business Intelligence**: Performance metrics and analysis

### Common Issues & Fixes

**Authentication errors**: 
```bash
python setup_env.py  # Recreates all configs
```

**Module not found errors**:
```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

**CORS errors**: Ensure both servers are running on correct ports (8000/3000)

## 🚀 Production Deployment

**📖 See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for complete step-by-step deployment instructions**

### Deployment Process
The application is deployed via SSH to development, UAT, and production servers. See the deployment guide for detailed instructions on:
- Environment setup and configuration
- SSH-based deployment process
- Database migrations and backups
- Monitoring and troubleshooting

**That's it!** The USER_DEPLOYMENT_GUIDE walks you through each step with a simple checklist format.

### Deployment Testing & Validation
```bash
# Test your deployment configuration before deploying
make deploy-test

# Run comprehensive deployment validation
make deploy-check

# Test a live deployment health
make health-check URL=https://your-app.ondigitalocean.app

# Simulate the full deployment process
python simulate_deployment.py --environment production
```

## 📋 Business Entities (Migration Status)

**Completed** ✅:
- **Accounts Receivables** - Customer payment tracking
- **Suppliers** - Supplier management  
- **Customers** - Customer relationships
- **Purchase Orders** - Order processing
- **Plants** - Processing facilities
- **Contacts** - Contact management
- **User Profiles** - Authentication system
- **AI Assistant** - Document processing and chat

## 🧪 Testing

```bash
make test              # All tests
make test-backend      # Django tests only  
make test-frontend     # React tests only
```

**Coverage**: 95+ backend tests covering all business logic, API endpoints, and data models.

## 🛠️ Deployment Tools

This repository includes comprehensive deployment tools:

- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Complete deployment documentation
- **[test_deployment.py](test_deployment.py)** - Automated deployment configuration validation
- **[health_check.py](health_check.py)** - Live application health verification  
- **[simulate_deployment.py](simulate_deployment.py)** - Full deployment process simulation
- **Makefile commands** - `make deploy-test`, `make deploy-check`, `make health-check`

## 🛠️ Contributing

1. **Setup**: Follow Quick Start guide above
2. **Branch Naming**: Use `<type>/<description>` format (e.g., `feature/add-export`, `fix/login-bug`)
3. **PR Title**: Follow Conventional Commits format (e.g., `feat(customers): add export functionality`)
4. **Standards**: Use existing patterns from implemented entities
5. **Testing**: Add tests for new functionality
6. **Code Quality**: Run `make format` and `make lint` before commits

See [Branch Workflow Checklist](branch-workflow-checklist.md) for detailed workflow guide and [Contributing Guide](CONTRIBUTING.md) for comprehensive contribution guidelines.

## 📚 Documentation

### Essential Documentation ⭐
- **[Documentation Hub](docs/README.md)** - Central navigation for all documentation
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** ⭐ NEW - Complete database migration guide
- **[Authentication Guide](docs/AUTHENTICATION_GUIDE.md)** ⭐ NEW - Auth, permissions & superuser management
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** ⭐ NEW - Common issues and solutions
- **[3-Month Retrospective](docs/lessons-learned/3-MONTH-RETROSPECTIVE.md)** ⭐ NEW - Lessons learned (Aug-Nov 2024)
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation

> **🎉 Documentation Refresh**: We've consolidated 67 scattered documentation files into comprehensive guides! See [archived-2024-11/](docs/archived-2024-11/) for historical reference.

### Architecture & Development
- **[Backend Architecture](docs/BACKEND_ARCHITECTURE.md)** - Django backend structure and patterns
- **[Frontend Architecture](docs/FRONTEND_ARCHITECTURE.md)** - React frontend structure and components
- **[Testing Strategy](docs/TESTING_STRATEGY.md)** - Comprehensive testing guide
- **[Repository Best Practices](docs/REPOSITORY_BEST_PRACTICES.md)** - Development workflow and standards
- **[Multi-Tenancy Guide](docs/MULTI_TENANCY_GUIDE.md)** - Multi-tenancy architecture

### Deployment & Infrastructure
- **[Environment Guide](docs/ENVIRONMENT_GUIDE.md)** - Environment configuration
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation

### CI/CD & Workflows
- **[Branch Workflow Checklist](branch-workflow-checklist.md)** - Branch naming conventions and workflow guide
- **[Unified Workflow](docs/workflows/unified-workflow.md)** - Main CI/CD workflow documentation
- **[CI/CD Infrastructure](docs/workflows/cicd-infrastructure.md)** - Infrastructure details
- **[Database Backup](docs/workflows/database-backup.md)** - Backup workflow documentation
- **[GitHub Actions Workflows](.github/workflows/README.md)** - Detailed workflow documentation

## 📚 Reference

### URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

### Default Credentials
- **Username**: admin
- **Password**: WATERMELON1219

### AI Assistant Demo Commands
- "Show me supplier performance metrics"
- "Help me analyze purchase orders"
- "Review customer order patterns" 
- Upload documents via drag & drop

---

**Need help?** Check the [Documentation Hub](docs/README.md) or create an issue - the setup script handles 99% of common problems automatically.
