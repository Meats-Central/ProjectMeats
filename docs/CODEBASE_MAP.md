# ProjectMeats Codebase Map

**Last Updated**: December 1, 2024  
**Purpose**: Visual map of critical files, their purposes, and relationships

---

## 🗺️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ProjectMeats                             │
│                    Multi-Tenant SaaS Platform                    │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
        ┌───────▼───────┐               ┌──────▼──────┐
        │   Backend     │               │  Frontend   │
        │ Django + DRF  │◄─────REST─────┤React + TS   │
        │   Port 8000   │   JSON API    │ Port 3000   │
        └───────┬───────┘               └─────────────┘
                │
        ┌───────▼────────┐
        │   PostgreSQL   │
        │ Multi-tenant   │
        │ Schema-based   │
        └────────────────┘
```

---

## 📁 Critical Files & Their Purposes

### Configuration & Setup

| File | Purpose | When to Edit |
|------|---------|--------------|
| `Makefile` | Development commands | Add new dev shortcuts |
| `start_dev.sh` | Start all servers | Modify startup sequence |
| `stop_dev.sh` | Stop all servers | Modify shutdown sequence |
| `pyproject.toml` | Python project config | Update Python tools config |
| `setup.py` | Python package setup | Change package metadata |
| `.pre-commit-config.yaml` | Backend pre-commit hooks | Add new code quality checks |
| `.pre-commit-config-frontend.yaml` | Frontend pre-commit hooks | Add frontend checks |
| `.gitignore` | Git ignore rules | Add new files to ignore |

### Environment Management

| File | Purpose | When to Edit |
|------|---------|--------------|
| `config/manage_env.py` | Environment setup tool | Add new env variables |
| `config/environments/development.env` | Dev environment vars | Change dev settings |
| `config/environments/staging.env` | Staging environment vars | Change staging settings |
| `config/environments/production.env` | Prod environment vars | Change prod settings |

### Backend Core

| File | Purpose | When to Edit |
|------|---------|--------------|
| `backend/manage.py` | Django management | Rarely (auto-generated) |
| `backend/requirements.txt` | Python dependencies | Add/update packages |
| `backend/projectmeats/settings/base.py` | Base Django settings | Add apps, middleware, shared config |
| `backend/projectmeats/settings/development.py` | Dev settings | Dev-specific config |
| `backend/projectmeats/settings/staging.py` | Staging settings | Staging-specific config |
| `backend/projectmeats/settings/production.py` | Production settings | Prod-specific config |
| `backend/projectmeats/urls.py` | Main URL routing | Add new app URLs |
| `backend/projectmeats/wsgi.py` | WSGI entry point | Deployment config |
| `backend/projectmeats/asgi.py` | ASGI entry point | Async features |
| `backend/projectmeats/health.py` | Health check endpoint | Modify health checks |

### Backend Apps Structure

Each app follows this pattern:

```
backend/apps/<app_name>/
├── __init__.py              # Package marker
├── models.py                # Database models
├── serializers.py           # DRF serializers (API data)
├── views.py                 # API views/viewsets
├── urls.py                  # App-specific URLs
├── admin.py                 # Django admin config
├── permissions.py           # DRF permissions
├── filters.py               # DRF filter backends
├── signals.py               # Django signals
├── managers.py              # Custom model managers
├── migrations/              # Database migrations
│   ├── 0001_initial.py
│   └── ...
└── tests/                   # Test suite
    ├── __init__.py
    ├── test_models.py
    ├── test_views.py
    ├── test_serializers.py
    └── factories.py         # Test fixtures
```

### Backend Apps Overview

| App | Purpose | Key Models | API Endpoint |
|-----|---------|------------|--------------|
| `tenants` | Multi-tenancy management | `Client`, `Domain`, `Tenant` | `/api/v1/tenants/` |
| `core` | Shared utilities | `BaseModel`, `UserPreferences` | N/A (utility) |
| `suppliers` | Supplier management | `Supplier` | `/api/v1/suppliers/` |
| `customers` | Customer relationships | `Customer` | `/api/v1/customers/` |
| `purchase_orders` | Order processing | `PurchaseOrder`, `POLineItem` | `/api/v1/purchase-orders/` |
| `accounts_receivables` | Payment tracking | `AccountReceivable` | `/api/v1/accounts-receivables/` |
| `invoices` | Invoice management | `Invoice`, `InvoiceLineItem` | `/api/v1/invoices/` |
| `products` | Product catalog | `Product` | `/api/v1/products/` |
| `plants` | Processing facilities | `Plant` | `/api/v1/plants/` |
| `carriers` | Shipping carriers | `Carrier` | `/api/v1/carriers/` |
| `contacts` | Contact management | `Contact` | `/api/v1/contacts/` |
| `sales_orders` | Sales order processing | `SalesOrder` | `/api/v1/sales-orders/` |
| `bug_reports` | User feedback | `BugReport` | `/api/v1/bug-reports/` |
| `ai_assistant` | AI chat & documents | `Conversation`, `Message` | `/api/v1/ai/` |

### Critical Backend Files by App

#### apps/tenants/ (Multi-tenancy Core)
```
tenants/
├── models.py                # Client, Domain (django-tenants)
│                           # Tenant, TenantDomain (shared-schema)
│                           # TenantUser (user-tenant association)
├── middleware.py           # TenantMiddleware (custom features)
├── permissions.py          # IsGuestOrAuthenticated
├── management/commands/
│   ├── create_tenant.py   # Create tenant command
│   └── create_super_tenant.py  # Setup superuser + tenant
└── migrations/             # 15+ migrations
```

#### apps/core/ (Shared Utilities)
```
core/
├── models.py              # BaseModel (created_at, updated_at)
│                          # UserPreferences
├── validators.py          # Custom validators
├── middleware.py          # Custom middleware
├── utils.py              # Utility functions
└── management/commands/
    └── setup_superuser.py # Sync superuser credentials
```

### Frontend Core

| File | Purpose | When to Edit |
|------|---------|--------------|
| `frontend/package.json` | Node dependencies & scripts | Add packages/scripts |
| `frontend/tsconfig.json` | TypeScript config | Change compiler options |
| `frontend/.eslintrc.json` | ESLint config | Modify linting rules |
| `frontend/.prettierrc.json` | Prettier config | Change formatting rules |
| `frontend/config-overrides.js` | Webpack overrides | Customize build process |
| `frontend/src/index.tsx` | App entry point | Change root setup |
| `frontend/src/App.tsx` | Root component | Modify app structure |

### Frontend Structure

```
frontend/src/
├── components/               # Reusable UI components
│   ├── common/              # Generic components (Button, Input, etc.)
│   ├── layout/              # Layout components (Header, Sidebar)
│   └── [domain]/            # Domain-specific components
│
├── pages/                   # Route pages (one per route)
│   ├── Dashboard/
│   ├── Suppliers/
│   ├── Customers/
│   └── ...
│
├── services/                # API communication layer
│   ├── api.ts              # Base API client (axios config)
│   ├── businessApi.ts      # Business entity APIs
│   ├── authService.ts      # Authentication
│   └── tenantService.ts    # Tenant operations
│
├── contexts/                # React contexts
│   ├── AuthContext.tsx     # Authentication state
│   ├── TenantContext.tsx   # Tenant state
│   └── ThemeContext.tsx    # Theme configuration
│
├── types/                   # TypeScript type definitions
│   ├── api.types.ts        # API response types
│   ├── business.types.ts   # Business entity types
│   └── common.types.ts     # Shared types
│
├── config/                  # Configuration files
│   ├── runtime.ts          # Runtime config (API URLs)
│   └── constants.ts        # App constants
│
├── shared/                  # Shared utilities
│   └── utils.ts            # Re-export from /shared/utils.ts
│
└── stories/                 # Storybook stories
    └── [component].stories.tsx
```

### Critical Frontend Files

| File | Purpose | Key Exports |
|------|---------|-------------|
| `services/api.ts` | Base API client | `api` (axios instance) |
| `services/businessApi.ts` | Business APIs | `supplierApi`, `customerApi`, etc. |
| `contexts/AuthContext.tsx` | Auth state | `useAuth` hook |
| `contexts/TenantContext.tsx` | Tenant state | `useTenant` hook |
| `types/business.types.ts` | Business types | `Supplier`, `Customer`, etc. |
| `config/runtime.ts` | Runtime config | `config` object |

### Shared Utilities

| File | Purpose | When to Edit |
|------|---------|--------------|
| `shared/utils.ts` | Cross-platform utilities | Add shared functions |

---

## 🔄 Data Flow Patterns

### API Request Flow
```
1. Frontend Component
   └─► Service Layer (businessApi.ts)
       └─► Base API Client (api.ts)
           └─► HTTP Request
               └─► Django URL Router (urls.py)
                   └─► ViewSet (views.py)
                       └─► Serializer (serializers.py)
                           └─► Model (models.py)
                               └─► PostgreSQL
```

### Multi-Tenancy Request Flow
```
1. HTTP Request with Host header
   └─► TenantMainMiddleware (django-tenants)
       └─► Domain lookup (apps.tenants.Domain)
           └─► Client lookup (apps.tenants.Client)
               └─► Schema activation (SET search_path)
                   └─► Request processing in tenant schema
                       └─► TenantMiddleware (custom features)
                           └─► View processing
```

### Authentication Flow
```
1. User Login (Frontend)
   └─► POST /api/auth/login
       └─► Django Authentication
           └─► Token Generation
               └─► Response with Token
                   └─► Store in AuthContext
                       └─► Include in API headers
```

---

## 🔐 Security-Critical Files

| File | Security Concern | Review When |
|------|------------------|-------------|
| `backend/projectmeats/settings/base.py` | SECRET_KEY, ALLOWED_HOSTS | Adding security settings |
| `backend/apps/tenants/middleware.py` | Tenant isolation | Multi-tenancy changes |
| `backend/apps/*/permissions.py` | Access control | Permission changes |
| `backend/apps/*/views.py` | Permission classes | API endpoint changes |
| `frontend/src/services/api.ts` | Token handling | Auth changes |
| `.env` files | Secrets management | Never commit! |

---

## 📊 Database Schema Relationships

### Tenant Models (Schema-Based)
```
Client (django-tenants)
├── schema_name (unique)
├── name
└── Domain (many)
    ├── domain (unique)
    ├── tenant (FK to Client)
    └── is_primary (bool)
```

### Tenant Models (Shared-Schema)
```
Tenant (legacy)
├── schema_name (unique)
├── name
├── TenantDomain (many)
│   ├── domain (unique)
│   ├── tenant (FK to Tenant)
│   └── is_primary (bool)
└── TenantUser (many)
    ├── user (FK to User)
    ├── tenant (FK to Tenant)
    └── role
```

### Core Business Models
```
User (Django)
└── UserPreferences
    ├── user (OneToOne to User)
    ├── theme
    └── preferences (JSON)

Supplier
├── name
├── code
├── contact_person
└── PurchaseOrder (many)

Customer
├── name
├── code
├── contact_person
└── SalesOrder (many)

PurchaseOrder
├── supplier (FK to Supplier)
├── order_number
├── order_date
├── status
└── POLineItem (many)
    ├── purchase_order (FK)
    ├── product (FK)
    ├── quantity
    └── price

Product
├── name
├── sku
├── category
└── price

Plant
├── name
├── code
└── location
```

---

## 🚀 Deployment Files

| File | Purpose | Environment |
|------|---------|-------------|
| `.github/workflows/11-dev-deployment.yml` | Dev CI/CD | development branch |
| `.github/workflows/12-uat-deployment.yml` | UAT CI/CD | UAT branch |
| `.github/workflows/13-prod-deployment.yml` | Prod CI/CD | main branch |
| `.github/workflows/promote-dev-to-uat.yml` | Auto PR dev→UAT | After dev merge |
| `.github/workflows/promote-uat-to-main.yml` | Auto PR UAT→main | After UAT merge |
| `backend/dockerfile` | Backend Docker image | All environments |
| `frontend/dockerfile` | Frontend Docker image | All environments |
| `docker-compose.yml` | Local Docker setup | Local development |
| `health_check.py` | Deployment health check | Post-deployment |

---

## 🧪 Testing Files

### Backend Tests
```
backend/apps/<app>/tests/
├── __init__.py
├── test_models.py          # Model logic tests
├── test_views.py           # API endpoint tests
├── test_serializers.py     # Serialization tests
├── test_permissions.py     # Permission tests
└── factories.py            # Test data factories
```

### Frontend Tests
```
frontend/src/
├── components/__tests__/
│   └── Component.test.tsx
├── services/__tests__/
│   └── api.test.ts
└── pages/__tests__/
    └── Page.test.tsx
```

### Key Test Files
| File | Purpose | Coverage |
|------|---------|----------|
| `backend/apps/core/tests/test_database.py` | DB config validation | Core DB |
| `backend/apps/tenants/test_isolation.py` | Tenant isolation | Multi-tenancy |
| `backend/apps/suppliers/tests/` | Supplier CRUD | Business logic |
| `frontend/src/config/runtime.test.ts` | Config loading | Runtime config |

---

## 📚 Documentation Files

### Primary Documentation
| File | Audience | Focus |
|------|----------|-------|
| `README.md` | Everyone | Quick start, overview |
| `docs/AI_AGENT_ONBOARDING.md` | AI Agents | Essential knowledge |
| `docs/CODEBASE_MAP.md` | Developers | Code structure |
| `.github/copilot-instructions.md` | Copilot | Full instructions |
| `CONTRIBUTING.md` | Contributors | Contribution workflow |

### Guides
| File | Topic | When to Read |
|------|-------|--------------|
| `docs/MIGRATION_GUIDE.md` | Database migrations | Before migrating |
| `docs/AUTHENTICATION_GUIDE.md` | Auth & permissions | Auth work |
| `docs/TROUBLESHOOTING.md` | Common issues | When stuck |
| `docs/BACKEND_ARCHITECTURE.md` | Django patterns | Backend dev |
| `docs/FRONTEND_ARCHITECTURE.md` | React patterns | Frontend dev |
| `docs/DEPLOYMENT_GUIDE.md` | Deployment | Before deploying |
| `docs/MULTI_TENANCY_GUIDE.md` | Multi-tenancy | Tenant work |
| `docs/TESTING_STRATEGY.md` | Testing approach | Writing tests |

### Implementation Summaries
```
docs/implementation-summaries/
├── dashboard-enhancement.md
├── deployment-optimization.md
└── allowed-hosts-fix.md
```

---

## 🔧 Build & Dev Tools

| File | Purpose | Technology |
|------|---------|------------|
| `Makefile` | Dev commands | Make |
| `pyproject.toml` | Python tooling | Black, isort |
| `pytest.ini` | pytest config | pytest |
| `package.json` | Node scripts | npm |
| `tsconfig.json` | TypeScript | TypeScript |
| `.eslintrc.json` | Linting | ESLint |
| `.prettierrc.json` | Formatting | Prettier |

---

## 🎯 Quick Reference: "Where do I...?"

### Add a new feature?
1. Create branch: `feature/feature-name` from `development`
2. Backend: Add to `backend/apps/<app>/`
3. Frontend: Add to `frontend/src/pages/` or `components/`
4. Test: Add to `tests/` directories
5. PR to `development` branch

### Fix a bug?
1. Create branch: `fix/bug-description` from `development`
2. Locate bug in relevant app/component
3. Add test reproducing bug
4. Fix bug
5. Verify test passes
6. PR to `development` branch

### Add a new API endpoint?
1. Model: `backend/apps/<app>/models.py`
2. Serializer: `backend/apps/<app>/serializers.py`
3. ViewSet: `backend/apps/<app>/views.py`
4. URL: `backend/apps/<app>/urls.py`
5. Test: `backend/apps/<app>/tests/test_views.py`

### Add a new frontend page?
1. Component: `frontend/src/pages/<Page>/`
2. Types: `frontend/src/types/`
3. Service: `frontend/src/services/businessApi.ts`
4. Route: `frontend/src/App.tsx`
5. Test: `frontend/src/pages/<Page>/__tests__/`

### Change database schema?
1. Model: `backend/apps/<app>/models.py`
2. Migration: `python manage.py makemigrations`
3. Review: Check generated migration file
4. Apply: `python manage.py migrate_schemas`
5. Test: Verify in tests

### Update dependencies?
- **Backend**: `backend/requirements.txt` → `pip install -r requirements.txt`
- **Frontend**: `frontend/package.json` → `npm install`

### Change environment config?
- **Development**: `config/environments/development.env`
- **Staging**: `config/environments/staging.env`
- **Production**: `config/environments/production.env` + GitHub Secrets

### Update CI/CD?
- **Dev**: `.github/workflows/11-dev-deployment.yml`
- **UAT**: `.github/workflows/12-uat-deployment.yml`
- **Prod**: `.github/workflows/13-prod-deployment.yml`

---

## 🚨 Files You Should NEVER Directly Edit

| File | Why Not | What to Do Instead |
|------|---------|-------------------|
| `UAT` branch | Protected | Let automation create PR |
| `main` branch | Protected | Let automation create PR |
| `.env` in repo | Security risk | Use `.env.example` as template |
| `migrations/0001_initial.py` | Already applied | Create new migration |
| `node_modules/` | Generated | Use `npm install` |
| `__pycache__/` | Generated | Auto-created by Python |
| `.git/` | Version control | Use git commands |

---

## 📝 File Naming Conventions

### Backend
- **Models**: `models.py` (singular class names: `Supplier`, not `Suppliers`)
- **Views**: `views.py` (viewset names: `SupplierViewSet`)
- **Serializers**: `serializers.py` (serializer names: `SupplierSerializer`)
- **Tests**: `test_*.py` or `*_test.py`
- **Migrations**: Auto-generated `XXXX_description.py`

### Frontend
- **Components**: `PascalCase.tsx` (e.g., `SupplierList.tsx`)
- **Services**: `camelCase.ts` (e.g., `businessApi.ts`)
- **Types**: `*.types.ts` (e.g., `business.types.ts`)
- **Tests**: `*.test.tsx` or `*.test.ts`
- **Styles**: `*.styles.ts` (Styled Components)

---

**Last Updated**: December 1, 2024  
**Maintained by**: ProjectMeats Team  
**Version**: 1.0.0
