# ProjectMeats - Project Structure Overview

**Last Updated**: 2025-12-01  
**Purpose**: Comprehensive guide to the ProjectMeats workspace structure for developers and GitHub Copilot

---

## 📖 Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Repository Structure](#repository-structure)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Mobile Application](#mobile-application)
7. [Multi-Tenancy Implementation](#multi-tenancy-implementation)
8. [Development Workflow](#development-workflow)
9. [Testing Strategy](#testing-strategy)
10. [CI/CD Pipeline](#cicd-pipeline)
11. [Documentation Structure](#documentation-structure)
12. [Key Configuration Files](#key-configuration-files)

---

## Project Overview

**ProjectMeats** is a business management application for meat sales brokers, migrated from PowerApps to a modern Django REST Framework backend with React TypeScript frontend. The application manages suppliers, customers, purchase orders, accounts receivables, and related business entities with an AI Assistant featuring Copilot-style UI and document processing.

### Core Business Features
- **Supplier Management**: Track meat suppliers and their products
- **Customer Management**: Manage customer relationships and orders
- **Purchase Orders**: Create and track purchase orders with version history
- **Sales Orders**: Manage customer sales orders
- **Accounts Receivables**: Track customer payments and outstanding balances
- **Plants**: Manage processing facilities and locations
- **Carriers**: Track shipping carriers and logistics
- **AI Assistant**: OpenAI GPT-4 powered assistant for document processing and business intelligence
- **Invoice Management**: Generate and track invoices
- **Contact Management**: Centralized contact database

---

## Technology Stack

### Backend
- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL (recommended) with django-tenants 3.5.0 for multi-tenancy
- **Authentication**: Django User system with JWT support
- **API Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Testing**: pytest-django with 95+ comprehensive tests
- **Code Quality**: black, flake8, isort, pre-commit hooks
- **Server**: Gunicorn with Whitenoise for static files

### Frontend
- **Framework**: React 18.2.0
- **Language**: TypeScript 4.9.5
- **UI Library**: Ant Design 5.27.3 with styled-components 6.1.0
- **Routing**: React Router DOM 6.30.1
- **State Management**: React Context API
- **HTTP Client**: Axios 1.6.0
- **Data Visualization**: Recharts 3.2.0, ReactFlow 11.11.4
- **Build Tool**: Create React App with custom webpack overrides

### Mobile
- **Framework**: React Native
- **Shared Utilities**: Cross-platform TypeScript utilities in `/shared`

### DevOps & Infrastructure
- **Containerization**: Docker with docker-compose
- **CI/CD**: GitHub Actions (11 workflows for dev/uat/prod)
- **Deployment**: DigitalOcean with automated promotion pipeline
- **Version Control**: Git with GitFlow-inspired workflow
- **Environment Management**: Centralized configuration in `/config`

---

## Repository Structure

```
ProjectMeats/
├── .github/                       # GitHub configuration
│   ├── workflows/                # CI/CD workflows (11 files)
│   │   ├── 11-dev-deployment.yml    # Development deployment
│   │   ├── 12-uat-deployment.yml    # UAT/Staging deployment
│   │   ├── 13-prod-deployment.yml   # Production deployment
│   │   ├── promote-dev-to-uat.yml   # Auto-PR dev → UAT
│   │   ├── promote-uat-to-main.yml  # Auto-PR UAT → main
│   │   ├── 21-db-backup-restore-do.yml  # Database backups
│   │   └── 51-cleanup-branches-tags.yml # Maintenance
│   ├── copilot-instructions.md   # **ESSENTIAL** - Coding standards
│   ├── PULL_REQUEST_TEMPLATE.md  # PR template
│   └── ISSUE_TEMPLATE/           # Issue templates
│
├── backend/                       # Django REST API
│   ├── apps/                     # Business domain apps (14 apps)
│   │   ├── accounts_receivables/ # Customer payment tracking
│   │   ├── ai_assistant/         # OpenAI GPT-4 integration
│   │   ├── bug_reports/          # In-app bug reporting
│   │   ├── carriers/             # Shipping carrier management
│   │   ├── contacts/             # Contact database
│   │   ├── core/                 # Shared utilities & base models
│   │   ├── customers/            # Customer management
│   │   ├── invoices/             # Invoice generation & tracking
│   │   ├── plants/               # Processing facility management
│   │   ├── products/             # Product catalog
│   │   ├── purchase_orders/      # Purchase order processing
│   │   ├── sales_orders/         # Sales order management
│   │   ├── suppliers/            # Supplier database
│   │   └── tenants/              # Multi-tenancy implementation
│   ├── projectmeats/             # Django project settings
│   │   ├── settings.py           # Core settings
│   │   ├── settings_*.py         # Environment-specific settings
│   │   ├── urls.py               # URL routing
│   │   └── wsgi.py               # WSGI application
│   ├── manage.py                 # Django management script
│   ├── requirements.txt          # Python dependencies
│   └── dockerfile                # Backend Docker image
│
├── frontend/                      # React TypeScript UI
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── common/           # Shared components
│   │   │   ├── forms/            # Form components
│   │   │   └── layout/           # Layout components
│   │   ├── pages/                # Main application screens
│   │   │   ├── Dashboard.tsx     # Main dashboard
│   │   │   ├── Suppliers.tsx     # Supplier management
│   │   │   ├── Customers.tsx     # Customer management
│   │   │   ├── PurchaseOrders.tsx # PO management
│   │   │   ├── AccountsReceivables.tsx # AR tracking
│   │   │   ├── AIAssistant.tsx   # AI chat interface
│   │   │   ├── Login.tsx         # Authentication
│   │   │   └── Settings.tsx      # User settings
│   │   ├── services/             # API communication layer
│   │   │   ├── api.ts            # Base API client
│   │   │   └── *Service.ts       # Domain-specific services
│   │   ├── contexts/             # React Context providers
│   │   ├── types/                # TypeScript type definitions
│   │   ├── shared/               # Shared utilities (re-exports)
│   │   └── App.tsx               # Root component
│   ├── public/                   # Static assets
│   ├── package.json              # Node dependencies
│   ├── tsconfig.json             # TypeScript configuration
│   └── dockerfile                # Frontend Docker image
│
├── mobile/                        # React Native mobile app
│   └── src/
│       └── shared/               # Shared utilities (re-exports)
│
├── shared/                        # Cross-platform utilities
│   └── utils.ts                  # Common TypeScript utilities
│
├── config/                        # Centralized environment config
│   ├── environments/             # Environment-specific configs
│   │   ├── development.env       # Local development
│   │   ├── uat.env              # Staging environment
│   │   └── production.env       # Production environment
│   └── manage_env.py            # Environment management script
│
├── docs/                          # Documentation hub
│   ├── DOCUMENTATION_INDEX.md    # Central navigation
│   ├── BACKEND_ARCHITECTURE.md   # Backend design docs
│   ├── FRONTEND_ARCHITECTURE.md  # Frontend design docs
│   ├── MULTI_TENANCY_GUIDE.md    # Multi-tenancy patterns
│   ├── DEPLOYMENT_GUIDE.md       # Deployment instructions
│   ├── TESTING_STRATEGY.md       # Testing guidelines
│   └── TROUBLESHOOTING.md        # Common issues & solutions
│
├── deploy/                        # Deployment scripts
│   └── scripts/                  # Deployment automation
│
├── archived/                      # Archived files
│   ├── docs/                     # Old documentation
│   └── code/                     # Deprecated code
│
├── docker-compose.yml             # Local development orchestration
├── Makefile                       # Common development commands
├── start_dev.sh                  # Development startup script
├── stop_dev.sh                   # Development shutdown script
├── setup_env.py                  # Environment setup automation
├── health_check.py               # Application health monitoring
├── branch-workflow-checklist.md  # Git workflow guide
├── CONTRIBUTING.md               # Contribution guidelines
├── README.md                     # Project overview
└── CHANGELOG.md                  # Version history

**Key Directories**:
- `/backend/apps/` - 14 Django apps, each a business domain
- `/frontend/src/pages/` - 13 main application screens
- `/docs/` - 30+ documentation files
- `/.github/workflows/` - 11 CI/CD workflows
- `/config/environments/` - Environment-specific configurations
```

---

## Backend Architecture

### Django Apps Structure

The backend is organized into 14 Django apps following domain-driven design:

#### Core Business Apps
1. **suppliers** - Supplier management with contact info and product catalog
2. **customers** - Customer database with relationship tracking
3. **purchase_orders** - PO creation, tracking, version history
4. **sales_orders** - Customer order management
5. **accounts_receivables** - Payment tracking and outstanding balances
6. **invoices** - Invoice generation and status tracking
7. **products** - Product catalog and inventory
8. **plants** - Processing facility management
9. **carriers** - Shipping carrier database
10. **contacts** - Centralized contact management

#### Support Apps
11. **ai_assistant** - OpenAI GPT-4 integration with chat sessions
12. **tenants** - Multi-tenancy implementation (schema-based)
13. **core** - Shared models, utilities, validators
14. **bug_reports** - In-app bug reporting system

### Key Backend Patterns

#### Base Models (in `core/models.py`)
- **TimestampModel** - Automatic created_at/updated_at
- **StatusModel** - Status field with choices
- **OwnedModel** - User ownership tracking
- **TenantAwareModel** - Multi-tenancy support

#### API Design
- RESTful endpoints with DRF
- ViewSet-based architecture
- Serializer-based validation
- Pagination, filtering, searching
- OpenAPI/Swagger documentation at `/api/schema/`

#### Multi-Tenancy
- Schema-based isolation using django-tenants
- Automatic tenant routing via middleware
- Shared public schema for common data
- Per-tenant database schemas

#### Authentication & Permissions
- Django User model with profile extension
- Token-based authentication (JWT)
- Role-based access control (RBAC)
- Tenant-aware permissions
- Guest mode support with limited access
- Invite-only registration system

---

## Frontend Architecture

### Component Structure

```
src/
├── components/
│   ├── common/           # Reusable UI elements
│   │   ├── Button/
│   │   ├── Table/
│   │   ├── Form/
│   │   └── Modal/
│   ├── forms/           # Domain-specific forms
│   │   ├── SupplierForm/
│   │   ├── CustomerForm/
│   │   └── PurchaseOrderForm/
│   └── layout/          # Layout components
│       ├── Header/
│       ├── Sidebar/
│       └── Footer/
├── pages/               # Route-level components
│   └── [Feature]/       # One page per feature
├── services/            # API communication
│   ├── api.ts          # Axios instance & interceptors
│   └── *Service.ts     # Domain service modules
├── contexts/           # Global state management
│   ├── AuthContext.tsx
│   └── TenantContext.tsx
└── types/              # TypeScript interfaces
    └── *.types.ts
```

### Key Frontend Patterns

#### Styling
- **styled-components** for component-level styles
- **Ant Design** for UI components
- Theme-based design system
- Responsive design patterns

#### State Management
- React Context API for global state
- Local state with useState/useReducer
- API data fetching with custom hooks
- Optimistic UI updates

#### Routing
- React Router v6 with nested routes
- Protected routes with auth guards
- Lazy loading for code splitting
- Route-based code splitting

#### API Integration
- Axios-based service layer
- Request/response interceptors
- Automatic token refresh
- Error handling & retry logic
- Loading states & error boundaries

---

## Mobile Application

### Structure
```
mobile/
└── src/
    └── shared/    # Re-exports from /shared for cross-platform utils
```

The mobile app uses **React Native** and shares TypeScript utilities with the web frontend through the `/shared` directory, ensuring code consistency across platforms.

---

## Multi-Tenancy Implementation

### Architecture
- **Strategy**: Schema-based isolation via django-tenants
- **Routing**: Subdomain-based tenant identification (e.g., `tenant1.projectmeats.com`)
- **Database**: One PostgreSQL database, multiple schemas per tenant
- **Shared Data**: Public schema for shared reference data
- **Middleware**: Automatic tenant detection and schema switching

### Tenant Models
- **Client** - Tenant configuration (schema_name, domain)
- **Domain** - Maps domains to tenants
- **TenantAwareModel** - Base class for tenant-scoped data

### Frontend Multi-Tenancy
- Tenant context provider
- Automatic tenant routing
- Tenant-specific branding
- Tenant-aware API calls

---

## Development Workflow

### Branch Strategy (GitFlow-Inspired)

**Three main branches**:
1. **development** - Active development branch
2. **UAT** - Staging/testing environment
3. **main** - Production-ready code

### Branch Workflow
```
feature/new-feature → development (via PR)
                      ↓ (automated PR)
                    UAT (review & test)
                      ↓ (automated PR)
                    main (production deploy)
```

### Branch Naming Convention
- `feature/` - New features
- `fix/` - Bug fixes
- `chore/` - Infrastructure/tooling
- `refactor/` - Code refactoring
- `hotfix/` - Emergency production fixes
- `docs/` - Documentation updates
- `test/` - Test improvements
- `perf/` - Performance optimizations

### Development Commands

```bash
# Start everything
./start_dev.sh

# Stop all services
./stop_dev.sh

# Using Make
make start
make stop

# Backend only
cd backend
python manage.py runserver

# Frontend only
cd frontend
npm start

# Run tests
cd backend && pytest
cd frontend && npm test

# Code quality
cd backend && black . && flake8 && isort .
cd frontend && npm run lint && npm run format
```

### Environment Setup
```bash
# Automated setup
python setup_env.py

# Centralized config
python config/manage_env.py setup development
```

---

## Testing Strategy

### Backend Testing (95+ tests)
- **Framework**: pytest-django
- **Coverage**: Unit, integration, and API tests
- **Fixtures**: factory-boy for test data
- **Locations**: `backend/apps/*/tests.py` or `tests/test_*.py`

**Test Categories**:
- Model tests (validation, methods, constraints)
- API endpoint tests (CRUD operations, permissions)
- Authentication tests (login, permissions, tokens)
- Multi-tenancy tests (isolation, routing)
- Business logic tests (calculations, workflows)

### Frontend Testing
- **Framework**: Jest + React Testing Library
- **Command**: `npm test` or `npm run test:ci`
- **Location**: `src/**/__tests__/` or `*.test.tsx`

**Test Categories**:
- Component rendering tests
- User interaction tests
- API integration tests
- Routing tests

### Test Execution
```bash
# Backend
cd backend
pytest                          # All tests
pytest apps/suppliers/          # Specific app
pytest --cov                    # With coverage
pytest -v                       # Verbose

# Frontend
cd frontend
npm test                        # Interactive mode
npm run test:ci                 # CI mode with coverage
```

---

## CI/CD Pipeline

### Workflow Structure

**11 GitHub Actions workflows** organized by purpose:

#### Deployment Workflows (11-13)
- **11-dev-deployment.yml** - Deploy to development (on push to `development`)
- **12-uat-deployment.yml** - Deploy to UAT (on push to `UAT`)
- **13-prod-deployment.yml** - Deploy to production (on push to `main`)

#### Promotion Workflows
- **promote-dev-to-uat.yml** - Auto-create PR from development → UAT
- **promote-uat-to-main.yml** - Auto-create PR from UAT → main

#### Infrastructure Workflows (21-51)
- **21-db-backup-restore-do.yml** - Database backup automation
- **31-planner-auto-add-issue.yml** - Project management automation
- **51-cleanup-branches-tags.yml** - Repository maintenance

### Deployment Pipeline

```
1. Developer commits to feature branch
2. Create PR to development
3. CI runs: linting, tests, security checks
4. After approval and merge to development:
   → Triggers dev deployment (11)
   → Triggers auto-PR to UAT (promote-dev-to-uat)
5. Review and test in UAT environment
6. Merge UAT PR:
   → Triggers UAT deployment (12)
   → Triggers auto-PR to main (promote-uat-to-main)
7. Final review and merge to main:
   → Triggers production deployment (13)
```

### CI Checks
- Linting (flake8, black, eslint)
- Unit tests (pytest, jest)
- Type checking (mypy, TypeScript)
- Security scanning (CodeQL)
- Dependency audit
- Build validation

---

## Documentation Structure

### Documentation Hub: `/docs/`

**30+ documentation files** organized by category:

#### Core Documentation (Start Here)
- **DOCUMENTATION_INDEX.md** - Central navigation hub
- **README.md** - Project overview (also in root)
- **CONTRIBUTING.md** - Contribution guidelines (also in root)
- **.github/copilot-instructions.md** - **ESSENTIAL** - Coding standards

#### Architecture & Design
- **BACKEND_ARCHITECTURE.md** - Django backend patterns
- **FRONTEND_ARCHITECTURE.md** - React frontend patterns
- **MULTI_TENANCY_GUIDE.md** - Multi-tenancy implementation
- **DATA_GUIDE.md** - Data models and relationships

#### Development Guides
- **LOCAL_DEVELOPMENT.md** - Setup and development
- **TESTING_STRATEGY.md** - Testing guidelines
- **MIGRATION_GUIDE.md** - Database migrations
- **AUTHENTICATION_GUIDE.md** - Auth implementation
- **ENVIRONMENT_GUIDE.md** - Environment configuration

#### Deployment & Operations
- **DEPLOYMENT_GUIDE.md** - Deployment procedures
- **DEPLOYMENT_TROUBLESHOOTING.md** - Common deployment issues
- **TROUBLESHOOTING.md** - General troubleshooting

#### Reference Documentation
- **branch-workflow-checklist.md** - Git workflow reference
- **CHANGELOG.md** - Version history
- **REPOSITORY_BEST_PRACTICES.md** - Repository standards

### Root Documentation Files

**60+ markdown files** in the root directory covering:
- Implementation summaries
- Bug fix documentation
- Feature implementation guides
- Migration fixes
- Deployment enhancements
- Security summaries

**Archived**: Historical documentation moved to `/archived/docs/`

---

## Key Configuration Files

### Backend Configuration
- **backend/projectmeats/settings.py** - Core Django settings
- **backend/projectmeats/settings_*.py** - Environment overrides
- **backend/requirements.txt** - Python dependencies
- **backend/.env.example** - Environment variable template
- **backend/dockerfile** - Backend Docker image
- **pyproject.toml** - Python project metadata (root)

### Frontend Configuration
- **frontend/package.json** - Node dependencies & scripts
- **frontend/tsconfig.json** - TypeScript compiler config
- **frontend/.eslintrc.json** - ESLint rules
- **frontend/.prettierrc.json** - Prettier formatting rules
- **frontend/config-overrides.js** - Webpack customizations
- **frontend/dockerfile** - Frontend Docker image

### DevOps Configuration
- **docker-compose.yml** - Local development orchestration
- **Makefile** - Common development commands
- **.github/workflows/*.yml** - CI/CD pipelines
- **.pre-commit-config.yaml** - Pre-commit hooks (backend)
- **.pre-commit-config-frontend.yaml** - Pre-commit hooks (frontend)

### Environment Management
- **config/manage_env.py** - Centralized environment setup
- **config/environments/*.env** - Per-environment configurations
- **setup_env.py** - Automated environment setup (root)

### Utility Scripts
- **start_dev.sh** - Start all development services
- **stop_dev.sh** - Stop all development services
- **health_check.py** - Application health monitoring
- **simulate_deployment.py** - Test deployment process
- **test_deployment.sh** - Deployment validation

---

## Quick Reference

### Essential Files to Read First
1. **README.md** - Project overview
2. **.github/copilot-instructions.md** - **CRITICAL** - Coding standards
3. **docs/DOCUMENTATION_INDEX.md** - Documentation navigation
4. **CONTRIBUTING.md** - How to contribute
5. **branch-workflow-checklist.md** - Git workflow

### Common Tasks

#### Starting Development
```bash
./start_dev.sh
# OR
make start
```

#### Running Tests
```bash
cd backend && pytest
cd frontend && npm test
```

#### Code Quality
```bash
cd backend && black . && flake8 && isort .
cd frontend && npm run lint:fix && npm run format
```

#### Creating a Feature
```bash
git checkout development
git pull origin development
git checkout -b feature/my-feature
# Make changes
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
# Create PR to development
```

#### Deployment Process
1. Merge to `development` → auto-deploys to dev
2. Auto-PR created to `UAT` → review & merge → deploys to staging
3. Auto-PR created to `main` → review & merge → deploys to production

---

## Technology Highlights

### Key Frameworks & Libraries
- **Django 4.2.7** - Backend framework
- **Django REST Framework 3.14.0** - API layer
- **django-tenants 3.5.0** - Multi-tenancy
- **React 18.2.0** - Frontend framework
- **TypeScript 4.9.5** - Type safety
- **Ant Design 5.27.3** - UI components
- **PostgreSQL** - Primary database
- **pytest-django** - Backend testing
- **Jest + RTL** - Frontend testing

### Development Tools
- **Docker** - Containerization
- **GitHub Actions** - CI/CD
- **pre-commit** - Git hooks
- **black, flake8, isort** - Python code quality
- **eslint, prettier** - JavaScript/TypeScript code quality
- **Storybook** - Component development

---

## Project Statistics

- **Backend Apps**: 14 Django apps
- **Frontend Pages**: 13 main screens
- **Backend Tests**: 95+ test cases
- **Documentation Files**: 90+ markdown files
- **CI/CD Workflows**: 11 GitHub Actions
- **Dependencies**: 35+ Python packages, 20+ npm packages
- **Supported Environments**: Development, UAT, Production
- **Database**: PostgreSQL with multi-tenant schemas

---

## Getting Help

### Documentation Resources
- Start with [DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md)
- Read [.github/copilot-instructions.md](.github/copilot-instructions.md) for standards
- Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues
- Review [DEPLOYMENT_TROUBLESHOOTING.md](docs/DEPLOYMENT_TROUBLESHOOTING.md) for deployment issues

### Quick Links
- **Setup**: [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Git Workflow**: [branch-workflow-checklist.md](branch-workflow-checklist.md)
- **Testing**: [docs/TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)
- **Deployment**: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)

---

**Note**: This document provides a high-level overview of the ProjectMeats workspace structure. For detailed implementation specifics, refer to the individual documentation files linked throughout this guide.
