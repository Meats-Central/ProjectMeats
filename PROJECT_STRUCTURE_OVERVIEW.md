# ProjectMeats - Complete Project Structure Overview

**Generated:** 2025-12-01  
**Repository:** Meats-Central/ProjectMeats  
**Purpose:** Comprehensive documentation of project architecture, structure, and technical decisions

---

## 📋 Executive Summary

**ProjectMeats** is a full-stack business management application for meat sales brokers, migrated from Microsoft PowerApps to a modern web stack. The application manages suppliers, customers, purchase orders, accounts receivables, and related business entities with an integrated AI Assistant.

### Key Metrics
- **Backend:** 4,534+ lines of production code across 14 Django apps
- **Frontend:** Modern React TypeScript SPA with 30+ components
- **Testing:** 95+ comprehensive backend tests
- **Multi-Tenancy:** Custom shared-schema architecture (not using django-tenants schema-based isolation)
- **Documentation:** 80+ markdown files covering all aspects

---

## 🏗️ Technology Stack

### Backend
- **Framework:** Django 4.2.7 + Django REST Framework 3.14.0
- **Database:** PostgreSQL 12+ (recommended) with psycopg2-binary 2.9.9, SQLite fallback
- **Multi-Tenancy:** Custom shared-schema approach (django-tenants installed but not used)
- **API Documentation:** drf-spectacular 0.27.0 (OpenAPI/Swagger)
- **Authentication:** Django User system with Token Authentication
- **Testing:** pytest-django 4.7.0, factory-boy 3.3.0
- **Code Quality:** black 23.11.0, flake8 6.1.0, isort 5.12.0, pre-commit 3.5.0

### Frontend
- **Framework:** React 18.2.0 with TypeScript 4.9.5
- **UI Library:** Ant Design 5.27.3 + Styled Components 6.1.0
- **Routing:** React Router DOM 6.30.1
- **State Management:** React Contexts
- **Data Visualization:** Recharts 3.2.0, ReactFlow 11.11.4
- **HTTP Client:** Axios 1.6.0
- **Build Tool:** React App Rewired (CRA customization)

### Mobile
- **Framework:** React Native
- **Purpose:** Mobile companion app (108KB codebase)
- **Shared Code:** Uses `/shared` directory for cross-platform utilities

### Infrastructure
- **Version Control:** Git with GitFlow-inspired workflow
- **CI/CD:** GitHub Actions with multi-environment deployment
- **Deployment:** DigitalOcean App Platform (Docker-based)
- **Process Manager:** Gunicorn 21.2.0
- **Static Files:** WhiteNoise 6.6.0

---

## 📁 Repository Structure

```
ProjectMeats/
├── .github/                    # GitHub Actions workflows and configuration
│   ├── workflows/             # CI/CD pipelines (15 workflow files)
│   │   ├── 11-dev-deployment.yml       # Development deployment
│   │   ├── 12-uat-deployment.yml       # UAT/Staging deployment
│   │   ├── 13-prod-deployment.yml      # Production deployment
│   │   ├── 21-db-backup-restore-do.yml # Database backup automation
│   │   ├── 31-planner-*.yml            # Project management automation
│   │   ├── 51-cleanup-*.yml            # Cleanup workflows
│   │   ├── promote-dev-to-uat.yml      # Environment promotion
│   │   └── promote-uat-to-main.yml     # Production promotion
│   └── agents/                # Custom agent configurations
│
├── backend/                    # Django REST Framework API (1.4MB)
│   ├── apps/                  # Business logic applications (14 apps)
│   │   ├── accounts_receivables/   # AR management
│   │   ├── ai_assistant/           # GPT-4 integration
│   │   ├── bug_reports/            # In-app bug reporting
│   │   ├── carriers/               # Shipping carriers
│   │   ├── contacts/               # Contact management
│   │   ├── core/                   # Shared utilities & auth
│   │   ├── customers/              # Customer relationships
│   │   ├── invoices/               # Invoice generation
│   │   ├── plants/                 # Processing facilities
│   │   ├── products/               # Product catalog
│   │   ├── purchase_orders/        # PO processing (568 lines model)
│   │   ├── sales_orders/           # Sales order management
│   │   ├── suppliers/              # Supplier management (218 lines model)
│   │   └── tenants/                # Multi-tenancy (470 lines model)
│   │
│   ├── projectmeats/          # Django project configuration
│   │   ├── settings/          # Environment-specific settings
│   │   │   ├── base.py       # Shared configuration
│   │   │   ├── development.py # Dev environment
│   │   │   ├── staging.py    # UAT environment
│   │   │   ├── production.py # Production environment
│   │   │   └── test.py       # Test configuration
│   │   ├── urls.py           # URL routing
│   │   ├── wsgi.py           # WSGI application
│   │   ├── asgi.py           # ASGI application
│   │   └── health.py         # Health check endpoints
│   │
│   ├── requirements.txt       # Python dependencies
│   ├── manage.py              # Django management script
│   └── dockerfile             # Backend Docker configuration
│
├── frontend/                   # React TypeScript Application (2.2MB)
│   ├── src/
│   │   ├── components/        # Reusable UI components (30+)
│   │   │   ├── AIAssistant/   # Copilot-style AI interface
│   │   │   ├── Navigation/    # Navigation components
│   │   │   ├── ProfileDropdown/ # User profile menu
│   │   │   ├── Visualization/ # Charts and graphs
│   │   │   └── Workflow/      # Business process workflows
│   │   │
│   │   ├── pages/             # Main application screens
│   │   │   ├── AIAssistant.tsx    # AI chat interface
│   │   │   ├── Dashboard.tsx      # Main dashboard
│   │   │   ├── Suppliers.tsx      # Supplier management
│   │   │   ├── Customers.tsx      # Customer management
│   │   │   ├── PurchaseOrders.tsx # PO management
│   │   │   ├── AccountsReceivables.tsx # AR tracking
│   │   │   ├── Plants.tsx         # Plant management
│   │   │   ├── Carriers.tsx       # Carrier management
│   │   │   ├── Contacts.tsx       # Contact management
│   │   │   ├── Settings.tsx       # User settings
│   │   │   ├── Profile.tsx        # User profile
│   │   │   ├── Login.tsx          # Authentication
│   │   │   └── SignUp.tsx         # Registration
│   │   │
│   │   ├── services/          # API communication layer
│   │   │   ├── apiService.ts      # Base API client
│   │   │   ├── authService.ts     # Authentication
│   │   │   ├── tenantService.ts   # Multi-tenancy
│   │   │   ├── aiService.ts       # AI Assistant API
│   │   │   └── businessApi.ts     # Business entities API
│   │   │
│   │   ├── contexts/          # React Context providers
│   │   ├── types/             # TypeScript type definitions
│   │   ├── stories/           # Storybook stories
│   │   ├── config/            # Configuration files
│   │   ├── shared/            # Re-exports from /shared
│   │   ├── App.tsx            # Main application component
│   │   └── index.tsx          # Entry point
│   │
│   ├── public/                # Static assets
│   ├── .storybook/            # Storybook configuration
│   ├── package.json           # Node dependencies
│   ├── tsconfig.json          # TypeScript configuration
│   ├── config-overrides.js    # CRA customization
│   └── dockerfile             # Frontend Docker configuration
│
├── mobile/                     # React Native Mobile App (108KB)
│   ├── src/
│   │   └── shared/            # Re-exports from /shared
│   ├── App.tsx                # Main mobile component
│   ├── package.json           # Mobile dependencies
│   └── README.md              # Mobile setup guide
│
├── shared/                     # Cross-Platform Shared Code
│   └── utils.ts               # Common TypeScript utilities
│
├── docs/                       # Comprehensive Documentation (1.6MB)
│   ├── README.md              # Documentation hub
│   ├── MIGRATION_GUIDE.md     # Database migration guide
│   ├── AUTHENTICATION_GUIDE.md # Auth & permissions
│   ├── TROUBLESHOOTING.md     # Common issues & solutions
│   ├── BACKEND_ARCHITECTURE.md # Backend patterns
│   ├── FRONTEND_ARCHITECTURE.md # Frontend patterns
│   ├── TESTING_STRATEGY.md    # Testing guide
│   ├── DEPLOYMENT_GUIDE.md    # Deployment instructions
│   ├── ENVIRONMENT_GUIDE.md   # Environment configuration
│   ├── MULTI_TENANCY_GUIDE.md # Multi-tenancy architecture
│   ├── workflows/             # CI/CD workflow docs
│   ├── lessons-learned/       # Retrospectives
│   └── archived-2024-11/      # Historical documentation
│
├── config/                     # Centralized Configuration
│   ├── environments/          # Environment-specific configs
│   │   ├── development.env    # Dev environment variables
│   │   ├── staging.env        # UAT environment variables
│   │   └── production.env     # Production environment variables
│   └── manage_env.py          # Environment management script
│
├── deploy/                     # Deployment Scripts
│   └── (deployment configurations)
│
├── .devcontainer/             # VS Code Dev Container config
├── .vscode/                   # VS Code workspace settings
├── archived/                  # Archived code and documentation
│
├── Root-Level Scripts & Tools
├── setup_env.py               # Development environment setup
├── start_dev.sh               # Start all development servers
├── stop_dev.sh                # Stop all development servers
├── health_check.py            # Application health validation
├── test_deployment.py         # Deployment configuration testing
├── simulate_deployment.py     # Deployment simulation
├── query_accounts_summary.py  # Account querying utility
├── test_guest_mode.py         # Guest mode testing
├── test_invitations.py        # Invitation system testing
├── verify_staging_config.py   # Staging configuration validator
├── monitor_branch_health.sh   # Git branch health monitoring
│
├── Documentation Files (80+)
├── README.md                  # Main project documentation
├── QUICK_START.md             # 5-minute setup guide
├── LOCAL_DEVELOPMENT.md       # Local dev guide
├── CONTRIBUTING.md            # Contribution guidelines
├── branch-workflow-checklist.md # Git workflow guide
├── CHANGELOG.md               # Version history
├── (60+ implementation summaries and guides)
│
├── Configuration Files
├── Makefile                   # Development commands
├── pyproject.toml             # Python project metadata
├── setup.py                   # Package setup configuration
├── docker-compose.yml         # Docker Compose setup
├── .gitignore                 # Git ignore patterns
├── .pre-commit-config.yaml    # Pre-commit hooks (backend)
├── .pre-commit-config-frontend.yaml # Pre-commit hooks (frontend)
├── package-lock.json          # Root npm lock file
└── copilot-log.md            # GitHub Copilot interaction log (288KB)
```

---

## 🎯 Core Business Applications

### 1. **Suppliers** (`apps.suppliers`)
- **Purpose:** Supplier relationship management
- **Models:** 218 lines - Supplier, SupplierContact, SupplierPerformance
- **Views:** 158 lines - CRUD operations, performance metrics
- **Key Features:**
  - Supplier profiles with contact information
  - Performance tracking and ratings
  - Multi-tenancy support
  - Audit trail

### 2. **Customers** (`apps.customers`)
- **Purpose:** Customer relationship management
- **Models:** Customer, CustomerContact, CustomerPreferences
- **Views:** 158 lines - CRUD operations, customer insights
- **Key Features:**
  - Customer profiles and preferences
  - Order history tracking
  - Credit management
  - Multi-tenancy isolation

### 3. **Purchase Orders** (`apps.purchase_orders`)
- **Purpose:** Purchase order processing and tracking
- **Models:** 568 lines - PurchaseOrder, PurchaseOrderItem, PurchaseOrderStatus
- **Views:** 136 lines - Complex PO workflows
- **Key Features:**
  - Multi-item purchase orders
  - Status workflow (Draft → Submitted → Approved → Fulfilled)
  - Financial calculations
  - Supplier integration
  - Version history

### 4. **Sales Orders** (`apps.sales_orders`)
- **Purpose:** Sales order management
- **Models:** 163 lines - SalesOrder, SalesOrderItem
- **Views:** 3 lines (minimal - likely using generic views)
- **Key Features:**
  - Customer order processing
  - Inventory tracking
  - Pricing management

### 5. **Accounts Receivables** (`apps.accounts_receivables`)
- **Purpose:** Payment and AR tracking
- **Views:** 112 lines - Payment processing, AR reports
- **Key Features:**
  - Payment tracking
  - Outstanding balance management
  - Payment history
  - Aging reports

### 6. **Invoices** (`apps.invoices`)
- **Purpose:** Customer invoice generation
- **Views:** 3 lines (minimal - likely using generic views)
- **Key Features:**
  - Invoice creation from sales orders
  - PDF generation
  - Payment tracking integration

### 7. **Products** (`apps.products`)
- **Purpose:** Master product catalog
- **Models:** 177 lines - Product, ProductCategory, ProductPricing
- **Views:** 3 lines (minimal)
- **Key Features:**
  - Centralized product definitions
  - NAMP (North American Meat Processors) codes
  - Carton types and specifications
  - Origin tracking
  - Multi-tenancy support

### 8. **Plants** (`apps.plants`)
- **Purpose:** Processing facility management
- **Views:** 112 lines - Plant operations, capacity tracking
- **Key Features:**
  - Plant profiles and locations
  - Capacity management
  - Production tracking

### 9. **Carriers** (`apps.carriers`)
- **Purpose:** Shipping carrier management
- **Views:** 120 lines - Carrier CRUD, shipping tracking
- **Key Features:**
  - Carrier profiles
  - Shipping rate management
  - Delivery tracking

### 10. **Contacts** (`apps.contacts`)
- **Purpose:** Contact management across entities
- **Views:** 107 lines - Contact CRUD, relationship mapping
- **Key Features:**
  - Unified contact database
  - Multi-entity relationships
  - Contact history

### 11. **AI Assistant** (`apps.ai_assistant`)
- **Purpose:** GPT-4 powered business intelligence
- **Views:** 212 lines - Chat interface, document processing
- **Key Features:**
  - Natural language queries
  - Document upload and analysis
  - Entity extraction
  - Business intelligence insights
  - Copilot-style UI

### 12. **Tenants** (`apps.tenants`)
- **Purpose:** Multi-tenancy and user management
- **Models:** 470 lines - Tenant, TenantUser, TenantDomain, Invitation system
- **Views:** 231 lines - Tenant management, user roles, invitations
- **Key Features:**
  - Shared-schema multi-tenancy (NOT schema-based)
  - User-tenant associations
  - Role-based permissions (Owner, Admin, Manager, Member, Guest)
  - Invitation system with email validation
  - Guest mode with read-only access
  - Domain management
  - Tenant isolation middleware

### 13. **Bug Reports** (`apps.bug_reports`)
- **Purpose:** In-application bug reporting
- **Views:** 27 lines - Bug submission, tracking
- **Key Features:**
  - User-submitted bug reports
  - GitHub integration
  - Screenshot attachments

### 14. **Core** (`apps.core`)
- **Purpose:** Shared utilities, authentication, user management
- **Views:** 218 lines - User profiles, preferences, superuser management
- **Key Features:**
  - User authentication and authorization
  - User preferences and settings
  - Superuser management commands
  - Database utilities
  - Validators and helpers
  - Health checks

---

## 🔐 Multi-Tenancy Architecture

### Important Architectural Decision

**ProjectMeats uses a CUSTOM SHARED-SCHEMA multi-tenancy approach, NOT django-tenants schema-based isolation.**

Despite having `django-tenants==3.5.0` in `requirements.txt`, the application:
- **Does NOT use** `TenantMixin` or `DomainMixin`
- **Does NOT use** `django_tenants.postgresql_backend`
- **Does NOT use** schema-based isolation
- **Does NOT use** `SHARED_APPS` / `TENANT_APPS` separation

### Custom Multi-Tenancy Implementation

**Location:** `backend/apps/tenants/`

**Key Models:**
1. **Tenant** - Organization entity with metadata
2. **TenantUser** - User-tenant many-to-many relationship with roles
3. **TenantDomain** - Domain-to-tenant mapping
4. **TenantInvitation** - Invitation system for user onboarding

**Roles:**
- `OWNER` - Full control
- `ADMIN` - Administrative access
- `MANAGER` - Management permissions
- `MEMBER` - Standard user
- `GUEST` - Read-only access

**Middleware:** `apps.tenants.middleware.TenantMiddleware`
- Resolves tenant from HTTP headers (`X-Tenant-ID`, `X-Tenant-Domain`)
- Attaches tenant to request object
- Provides tenant context for database queries

**Benefits of Shared-Schema Approach:**
- Simpler database management
- Easier to implement and maintain
- Good performance for moderate scale
- Flexible tenant isolation via foreign keys
- No complex schema migrations

**Tradeoffs:**
- Less strict data isolation than schema-based
- Requires careful query filtering
- All tenant data in same database schema

---

## 🧪 Testing Infrastructure

### Backend Tests (95+ tests)

**Test Framework:** pytest-django 4.7.0  
**Fixtures:** factory-boy 3.3.0  
**Coverage:** pytest-cov 4.1.0

**Test Locations:**
```
backend/apps/
├── core/tests/
│   ├── test_validators.py
│   ├── test_setup_superuser.py
│   ├── test_database.py
│   └── test_user_preferences.py
├── tenants/
│   ├── tests.py
│   ├── test_middleware_debug.py
│   ├── test_isolation.py
│   ├── test_utils.py
│   ├── tests_role_permissions.py
│   └── tests_management_commands.py
├── suppliers/tests.py
├── customers/tests.py
├── contacts/tests.py
├── sales_orders/tests.py
└── products/tests.py
```

**Running Tests:**
```bash
# All tests
make test

# Backend only
make test-backend
cd backend && python manage.py test

# With coverage
cd backend && pytest --cov
```

### Frontend Tests

**Test Framework:** Jest + React Testing Library  
**Configuration:** `test:ci` script for CI/CD

**Running Tests:**
```bash
# All tests
cd frontend && npm test

# CI mode
npm run test:ci
```

---

## 🚀 CI/CD & Deployment

### Branch Strategy

**Main Branches:**
- `development` - Feature integration and testing
- `UAT` - Staging/acceptance testing (mirrors production)
- `main` - Production releases

**Feature Branches:**
```
feature/<description>
fix/<description>
hotfix/<description>
```

### GitHub Actions Workflows

**1. Development Deployment** (`11-dev-deployment.yml`)
- Triggers: Push to `development` branch
- Builds Docker images (frontend + backend)
- Deploys to dev environment
- Runs migration and superuser setup

**2. UAT Deployment** (`12-uat-deployment.yml`)
- Triggers: Push to `UAT` branch
- Comprehensive testing suite
- Staging environment deployment
- Pre-production validation

**3. Production Deployment** (`13-prod-deployment.yml`)
- Triggers: Push to `main` branch
- Production-grade health checks
- Zero-downtime deployment
- Automatic rollback on failure

**4. Environment Promotion**
- `promote-dev-to-uat.yml` - Auto-creates PR from development → UAT
- `promote-uat-to-main.yml` - Auto-creates PR from UAT → main

**5. Database Backup** (`21-db-backup-restore-do.yml`)
- Scheduled backups
- DigitalOcean Spaces integration
- Point-in-time recovery

**6. Project Management Automation**
- `31-planner-auto-add-issue.yml` - Auto-add issues to project
- `32-planner-Auto-Assign-to-Copilot.yml` - Auto-assign to Copilot
- `33-planner-review-and-test` - Review automation
- `34-planner-sprint-gen.yml` - Sprint generation

**7. Cleanup** (`51-cleanup-branches-tags.yml`)
- Removes stale branches
- Cleans up old tags
- Maintains repository hygiene

### Deployment Targets

**Platform:** DigitalOcean App Platform  
**Container Registry:** DigitalOcean Container Registry (DOCR)  
**Database:** DigitalOcean Managed PostgreSQL

**Environments:**
- **Dev:** `dev2-backend.ondigitalocean.app`, `dev2-frontend.ondigitalocean.app`
- **UAT:** `uat2-backend.ondigitalocean.app`, `uat2-frontend.ondigitalocean.app`
- **Production:** `prod2-backend.ondigitalocean.app`, `prod2-frontend.ondigitalocean.app`

---

## 🔧 Development Workflow

### Quick Start (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/Meats-Central/ProjectMeats.git
cd ProjectMeats

# 2. Install pre-commit hooks (REQUIRED)
pre-commit install

# 3. Start all servers (PostgreSQL + Backend + Frontend)
./start_dev.sh

# 4. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs/
# Admin: http://localhost:8000/admin/
```

### Development Commands

**Via Makefile:**
```bash
make help              # Show all commands
make start             # Start all servers (uses start_dev.sh)
make stop              # Stop all servers
make dev               # Start backend + frontend (manual)
make migrate           # Run database migrations
make migrations        # Create new migrations
make test              # Run all tests
make format            # Format code (black, isort)
make lint              # Lint code (flake8)
make superuser         # Create superuser and tenant
make sync-superuser    # Sync superuser from environment
```

**Via Scripts:**
```bash
./start_dev.sh         # Automated startup with PostgreSQL
./stop_dev.sh          # Stop all services
python setup_env.py    # Environment setup
```

### Environment Management

**Centralized Configuration:**
```bash
python config/manage_env.py setup development
python config/manage_env.py setup staging
python config/manage_env.py setup production
python config/manage_env.py validate
python config/manage_env.py generate-secrets
```

**Environment Files:**
- `config/environments/development.env`
- `config/environments/staging.env`
- `config/environments/production.env`

### Pre-commit Hooks (REQUIRED)

**Why Required:**
- Prevents CI failures
- Validates migrations before commit
- Enforces code style
- Prevents syntax errors

**Setup:**
```bash
pre-commit install

# Test hooks
pre-commit run --all-files
```

**Hooks:**
- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
- Migration validation (`makemigrations --check --dry-run`)
- Trailing whitespace removal
- YAML/JSON syntax validation

---

## 📚 Documentation Overview

### Essential Documentation (⭐ Priority)

1. **[README.md](README.md)** - Main project documentation
2. **[docs/README.md](docs/README.md)** - Documentation hub
3. **[docs/MIGRATION_GUIDE.md](docs/MIGRATION_GUIDE.md)** - Database migrations
4. **[docs/AUTHENTICATION_GUIDE.md](docs/AUTHENTICATION_GUIDE.md)** - Auth & permissions
5. **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues
6. **[branch-workflow-checklist.md](branch-workflow-checklist.md)** - Git workflow
7. **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guide
8. **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - Local dev setup

### Architecture Documentation

- **[docs/BACKEND_ARCHITECTURE.md](docs/BACKEND_ARCHITECTURE.md)** - Django patterns
- **[docs/FRONTEND_ARCHITECTURE.md](docs/FRONTEND_ARCHITECTURE.md)** - React structure
- **[docs/MULTI_TENANCY_GUIDE.md](docs/MULTI_TENANCY_GUIDE.md)** - Multi-tenancy
- **[docs/TESTING_STRATEGY.md](docs/TESTING_STRATEGY.md)** - Testing approach

### Operational Documentation

- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Deployment instructions
- **[docs/ENVIRONMENT_GUIDE.md](docs/ENVIRONMENT_GUIDE.md)** - Environment config
- **[.github/workflows/README.md](.github/workflows/README.md)** - CI/CD workflows

### Implementation Summaries (60+ files)

ProjectMeats maintains detailed implementation summaries for major features:
- `IMPLEMENTATION_SUMMARY_*.md` - Feature implementation details
- `*_FIX_SUMMARY.md` - Bug fix documentation
- `*_GUIDE.md` - Feature-specific guides
- `MIGRATION_FIX_*.md` - Database migration fixes

### Historical Documentation

- **[docs/lessons-learned/3-MONTH-RETROSPECTIVE.md](docs/lessons-learned/3-MONTH-RETROSPECTIVE.md)** - Aug-Nov 2024 retrospective
- **[docs/archived-2024-11/](docs/archived-2024-11/)** - Archived documentation (67 files consolidated)

---

## 🔍 Key Technical Decisions

### 1. Multi-Tenancy Approach

**Decision:** Custom shared-schema multi-tenancy  
**Rationale:**
- Simpler than schema-based isolation
- Easier database management
- Good performance for target scale
- Flexible and maintainable
- No complex schema migrations

**Implementation:**
- Tenant foreign keys on all models
- Custom middleware for tenant resolution
- Role-based access control
- Invitation system for user onboarding

### 2. Database Strategy

**Decision:** PostgreSQL with SQLite fallback  
**Rationale:**
- PostgreSQL for production (environment parity)
- SQLite for quick local development
- psycopg2-binary for compatibility
- Managed PostgreSQL on DigitalOcean

### 3. API Documentation

**Decision:** drf-spectacular (OpenAPI 3.0)  
**Rationale:**
- Automatic schema generation
- Interactive Swagger UI
- Better than drf-yasg
- TypeScript client generation support

### 4. Frontend Framework

**Decision:** React + TypeScript (not Next.js)  
**Rationale:**
- SPA architecture (not SSR needed)
- Type safety with TypeScript
- Mature ecosystem
- Team expertise

### 5. State Management

**Decision:** React Context (not Redux)  
**Rationale:**
- Simpler for application scale
- Built-in React feature
- Sufficient for tenant/auth state
- Less boilerplate

### 6. UI Library

**Decision:** Ant Design + Styled Components  
**Rationale:**
- Professional component library
- Customizable theming
- Good TypeScript support
- CSS-in-JS flexibility

### 7. Testing Strategy

**Decision:** pytest-django + Jest  
**Rationale:**
- pytest is more Pythonic
- Better fixtures with factory-boy
- Jest is React standard
- Good CI integration

### 8. CI/CD Platform

**Decision:** GitHub Actions  
**Rationale:**
- Native GitHub integration
- Free for public repos
- Good documentation
- Flexible workflow composition

### 9. Deployment Platform

**Decision:** DigitalOcean App Platform  
**Rationale:**
- Managed infrastructure
- Docker-based deployment
- Integrated database
- Cost-effective
- Good performance

### 10. Code Quality

**Decision:** Pre-commit hooks + black + flake8  
**Rationale:**
- Enforce quality before commit
- Prevent CI failures
- Consistent code style
- Migration validation

---

## 📊 Project Metrics

### Codebase Statistics

- **Total Backend Code:** 4,534+ lines (models + views)
- **Total Frontend Components:** 30+
- **Database Models:** 20+ major models
- **API Endpoints:** 50+ REST endpoints
- **Tests:** 95+ comprehensive tests
- **Documentation Files:** 80+
- **GitHub Actions Workflows:** 15

### Key Files by Size

1. `copilot-log.md` - 288KB (interaction history)
2. `frontend/` - 2.2MB
3. `docs/` - 1.6MB
4. `backend/` - 1.4MB
5. `mobile/` - 108KB

### Most Complex Components

**Backend:**
1. `apps.tenants.models` - 470 lines
2. `apps.purchase_orders.models` - 568 lines
3. `apps.tenants.views` - 231 lines
4. `apps.suppliers.models` - 218 lines
5. `apps.core.views` - 218 lines

**Frontend:**
- AI Assistant components
- Purchase Order Workflow
- Data visualization components
- Multi-tenant context management

---

## 🛠️ Utility Scripts

### Development Utilities

- **setup_env.py** - Automated development environment setup
- **start_dev.sh** - Start all development servers
- **stop_dev.sh** - Stop all development servers

### Testing Utilities

- **test_deployment.py** - Deployment configuration validation
- **simulate_deployment.py** - Full deployment simulation
- **health_check.py** - Application health monitoring
- **test_guest_mode.py** - Guest mode testing
- **test_invitations.py** - Invitation system testing

### Operational Utilities

- **verify_staging_config.py** - Staging configuration validator
- **query_accounts_summary.py** - Account querying utility
- **query_remote_accounts.sh** - Remote account queries
- **monitor_branch_health.sh** - Git branch health monitoring
- **remove_debug_logging.py** - Debug log cleanup

---

## 🔐 Security Considerations

### Authentication

- Token-based authentication (DRF)
- Secure password hashing (Django default)
- CSRF protection enabled
- Session security configured

### Multi-Tenancy Security

- Tenant isolation at query level
- User-tenant relationship validation
- Role-based access control
- Guest mode with read-only restrictions
- Invitation system with email validation

### Environment Security

- Environment-specific secrets
- GitHub Secrets for sensitive data
- No credentials in code
- Separate dev/staging/prod configs

### Production Security Settings

- `SECURE_SSL_REDIRECT` enabled
- `SECURE_HSTS_SECONDS` configured
- `SESSION_COOKIE_SECURE` enabled
- `CSRF_COOKIE_SECURE` enabled
- Debug mode disabled in production

---

## 📈 Future Considerations

### Scalability

- Current shared-schema multi-tenancy scales to 100s of tenants
- For 1000+ tenants, consider:
  - Schema-based multi-tenancy (django-tenants)
  - Database sharding
  - Caching layer (Redis)

### Performance Optimization

- Implement database query optimization
- Add Redis caching
- Consider CDN for static assets
- Implement database connection pooling

### Feature Enhancements

- Real-time notifications (WebSockets)
- Advanced reporting and analytics
- Mobile app feature parity
- API rate limiting
- Audit logging system

### Technical Debt

- Consolidate some implementation summary docs
- Standardize test patterns across apps
- Complete frontend test coverage
- API versioning strategy
- Database query optimization

---

## 🎓 Learning Resources

### Django & DRF

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)

### React & TypeScript

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Ant Design](https://ant.design/)

### Multi-Tenancy

- [Multi-Tenancy Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/multi-tenancy)
- [Django Multi-Tenancy](https://books.agiliq.com/projects/django-multi-tenant/en/latest/)

### CI/CD

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)

---

## 📞 Support & Contribution

### Getting Help

1. Check **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)**
2. Review **[docs/README.md](docs/README.md)** documentation hub
3. Search existing GitHub issues
4. Create a new issue with detailed description

### Contributing

1. Read **[CONTRIBUTING.md](CONTRIBUTING.md)**
2. Follow **[branch-workflow-checklist.md](branch-workflow-checklist.md)**
3. Install pre-commit hooks: `pre-commit install`
4. Write tests for new features
5. Update documentation

### Code Style

- **Backend:** black, isort, flake8
- **Frontend:** ESLint, Prettier
- **Pre-commit:** Required for all commits
- **Testing:** Required for new features

---

## 📝 Version History

- **v1.0.0** - Initial production release
- Migration from PowerApps complete
- 14 business apps implemented
- Multi-tenancy system operational
- AI Assistant integrated
- 95+ tests passing
- Comprehensive documentation

---

## 🙏 Acknowledgments

- **Original Platform:** Microsoft PowerApps
- **Migration Target:** Django + React full-stack
- **Team:** ProjectMeats development team
- **AI Assistance:** GitHub Copilot
- **Hosting:** DigitalOcean

---

**Last Updated:** 2025-12-01  
**Document Version:** 1.0  
**Maintainer:** ProjectMeats Team
