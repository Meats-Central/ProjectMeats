# ProjectMeats - Big Picture Architecture

**Last Updated**: December 1, 2025

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Major Components](#major-components)
4. [Service Boundaries](#service-boundaries)
5. [Data Flow Patterns](#data-flow-patterns)
6. [Multi-Tenancy Architecture](#multi-tenancy-architecture)
7. [Authentication & Authorization](#authentication--authorization)
8. [Deployment Architecture](#deployment-architecture)
9. [Infrastructure & Environments](#infrastructure--environments)
10. [Key Architectural Decisions](#key-architectural-decisions)
11. [Integration Points](#integration-points)
12. [Scalability & Performance](#scalability--performance)
13. [Security Architecture](#security-architecture)

---

## System Overview

ProjectMeats is a comprehensive business management application for meat sales brokers, originally migrated from Microsoft PowerApps to a modern, custom-built solution. The system manages the complete business lifecycle including suppliers, customers, purchase orders, accounts receivables, plants, and contacts, with an integrated AI Assistant for document processing and business intelligence.

### Business Context

The application serves as the operational backbone for meat brokerage businesses, handling:
- **Supplier Management**: Track suppliers, their capabilities, quality ratings, and contact information
- **Customer Management**: Manage customer relationships, preferences, and plant associations
- **Order Processing**: Create, track, and manage purchase orders from suppliers to customers
- **Financial Tracking**: Monitor accounts receivables and payment statuses
- **Facility Management**: Track processing plants, distribution centers, and warehouses
- **AI-Powered Assistance**: Natural language queries and document processing for business intelligence

### Technical Context

**Technology Stack**:
- **Backend**: Django 4.2.7 + Django REST Framework
- **Frontend**: React 18.2.0 + TypeScript
- **Mobile**: React Native (planned/in development)
- **Database**: PostgreSQL 15 (production) / SQLite (development fallback)
- **AI**: OpenAI GPT-4 integration
- **Deployment**: DigitalOcean App Platform (containerized)
- **CI/CD**: GitHub Actions

---

## High-Level Architecture

ProjectMeats follows a **three-tier architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   React Web  │  │ React Native │  │  Third-Party │          │
│  │  (Frontend)  │  │   (Mobile)   │  │  API Clients │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                            │
                    HTTPS / REST API
                            │
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           Django REST Framework (Backend API)              │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐      │ │
│  │  │   Business  │  │     Core     │  │     AI      │      │ │
│  │  │   Entities  │  │  Middleware  │  │  Assistant  │      │ │
│  │  │    (Apps)   │  │  & Services  │  │   Service   │      │ │
│  │  └─────────────┘  └──────────────┘  └─────────────┘      │ │
│  │                                                             │ │
│  │  Authentication │ Tenant Isolation │ Authorization        │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                            │
                    PostgreSQL Protocol
                            │
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │            PostgreSQL Database (Multi-Tenant)              │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │   Shared     │  │   Tenant     │  │   Business   │    │ │
│  │  │   Tables     │  │   Tables     │  │    Data      │    │ │
│  │  │ (Auth, Core) │  │ (Tenants)    │  │  (Scoped)    │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **Separation of Concerns**: Clear boundaries between presentation, business logic, and data layers
2. **RESTful Design**: Stateless API following REST principles
3. **Multi-Tenancy First**: All business data is tenant-isolated by design
4. **Modular Applications**: Each business domain is a separate Django app
5. **Shared-Schema Multi-Tenancy**: Single database with tenant-scoped queries for operational efficiency
6. **API-First**: Backend exposes all functionality through REST API
7. **Progressive Enhancement**: Core functionality works, enhanced by AI features

---

## Major Components

### 1. Frontend Application (React)

**Location**: `/frontend`  
**Technology**: React 18.2.0 + TypeScript + Ant Design + Styled Components

**Responsibilities**:
- User interface and interaction
- Form validation and user input
- Client-side routing (React Router)
- API consumption and data presentation
- Real-time updates (planned: WebSockets)
- Responsive design for desktop and tablet

**Key Features**:
- Dashboard with KPIs and visualizations
- CRUD interfaces for all business entities
- AI Assistant chat interface with Copilot-style UI
- Document upload and processing
- User profile and settings management

**Architecture Pattern**: Component-based with functional components and React Hooks

### 2. Backend API (Django + DRF)

**Location**: `/backend`  
**Technology**: Django 4.2.7 + Django REST Framework + PostgreSQL

**Responsibilities**:
- Business logic and validation
- Data persistence and retrieval
- Authentication and authorization
- Multi-tenancy enforcement
- API endpoint provision
- Background task processing (planned: Celery)

**Django Apps (Business Entities)**:
- `apps.suppliers` - Supplier management
- `apps.customers` - Customer relationships
- `apps.purchase_orders` - Order processing
- `apps.accounts_receivables` - Payment tracking
- `apps.contacts` - Contact directory
- `apps.plants` - Facility management
- `apps.carriers` - Transportation providers
- `apps.products` - Product catalog
- `apps.sales_orders` - Sales order management
- `apps.invoices` - Invoice generation

**Django Apps (Core/Infrastructure)**:
- `apps.core` - Shared utilities, base models, protein types
- `apps.tenants` - Multi-tenancy management
- `apps.ai_assistant` - AI integration and document processing
- `apps.bug_reports` - Issue tracking

**Architecture Pattern**: Django apps as bounded contexts with shared utilities

### 3. Database Layer (PostgreSQL)

**Technology**: PostgreSQL 15

**Responsibilities**:
- Data persistence and ACID transactions
- Query optimization and indexing
- Data integrity and constraints
- Multi-tenant data isolation (application-level)
- Backup and recovery

**Schema Organization**:
- **Shared Tables**: Authentication (Django User), Core data (Protein types)
- **Tenant Tables**: Tenant definitions, domains, user associations
- **Business Tables**: All business entities (tenant-scoped via FK)

**Multi-Tenancy Approach**: Shared-schema with tenant foreign keys (not schema-per-tenant)

### 4. AI Assistant Service

**Location**: `/backend/apps/ai_assistant`  
**Technology**: OpenAI GPT-4 API

**Responsibilities**:
- Natural language processing
- Document text extraction and analysis
- Entity recognition and data extraction
- Conversational interface
- Business intelligence queries

**Key Features**:
- Chat-based interface with conversation history
- Document upload (PDF, images, documents)
- Context-aware responses
- Integration with business data

### 5. Mobile Application (React Native)

**Location**: `/mobile`  
**Status**: In development  
**Technology**: React Native + TypeScript

**Responsibilities**:
- Mobile-optimized UI
- Offline capabilities (planned)
- Push notifications (planned)
- Camera integration for document capture
- Shared business logic with web frontend

---

## Service Boundaries

### Internal Service Boundaries

ProjectMeats uses a **modular monolith** architecture with clear internal boundaries:

```
┌─────────────────────────────────────────────────────────────┐
│                    Django Monolith                           │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Business Entity Apps                       │ │
│  │  (Suppliers, Customers, Orders, etc.)                  │ │
│  │                                                         │ │
│  │  Each app is self-contained:                           │ │
│  │  • Models (data schema)                                │ │
│  │  • Views/ViewSets (API endpoints)                      │ │
│  │  • Serializers (data transformation)                   │ │
│  │  • Business logic (validations, calculations)          │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Core/Infrastructure Apps                     │ │
│  │  • apps.core - Shared utilities                        │ │
│  │  • apps.tenants - Multi-tenancy                        │ │
│  │  • apps.ai_assistant - AI integration                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   Middleware Layer                      │ │
│  │  • TenantMiddleware - Tenant context                   │ │
│  │  • AuthenticationMiddleware - User identity            │ │
│  │  • CORS - Cross-origin requests                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Boundary Enforcement**:
- **Import Rules**: Business apps should not import from each other; use Core for shared code
- **API-Only Communication**: Frontend and mobile only interact via REST API
- **Database Access**: Direct database access only through Django ORM
- **Tenant Isolation**: All business data queries filtered by tenant

### External Service Boundaries

```
ProjectMeats Application
       │
       ├── OpenAI API (GPT-4)
       │   └── AI Assistant functionality
       │
       ├── Email Service (SMTP)
       │   └── User notifications (planned)
       │
       └── File Storage (Local/Cloud)
           └── Document storage
```

**Integration Points**:
- **OpenAI API**: Synchronous HTTP calls for AI features
- **Email**: Async task queue (planned: Celery + Redis)
- **Storage**: Local filesystem (dev), Object storage (production planned)

---

## Data Flow Patterns

### 1. Standard CRUD Operation Flow

```
User Action (Frontend)
       │
       ↓
   API Request (HTTP/REST)
       │
       ↓
   Authentication Middleware ────→ Verify User
       │
       ↓
   Tenant Middleware ────────────→ Set Tenant Context
       │
       ↓
   ViewSet (DRF) ────────────────→ Authorization Check
       │
       ↓
   Serializer ───────────────────→ Validate Input
       │
       ↓
   Model Manager ────────────────→ Tenant-Scoped Query
       │
       ↓
   Database (PostgreSQL) ────────→ Execute Query
       │
       ↓
   Response ←────────────────────← JSON Response
       │
       ↓
   Frontend Update
```

**Key Points**:
- Every request authenticated and authorized
- Tenant context set from header or user association
- All queries automatically filtered by tenant
- Serializers handle validation and transformation

### 2. AI Assistant Document Processing Flow

```
User Uploads Document (Frontend)
       │
       ↓
   POST /api/v1/ai_assistant/documents/
       │
       ↓
   Store Document ──────────────→ File System
       │
       ↓
   Extract Text ────────────────→ PDF/Image Processing
       │
       ↓
   Send to OpenAI API ──────────→ GPT-4 Analysis
       │
       ↓
   Parse Response ──────────────→ Extract Entities
       │
       ↓
   Create Database Records ─────→ Suppliers, Orders, etc.
       │
       ↓
   Return Results ──────────────→ JSON Response
       │
       ↓
   Frontend Display
```

### 3. Multi-Tenant Data Access Pattern

```
Incoming Request
       │
       ↓
   Tenant Resolution (Middleware):
       │
       ├─→ Check X-Tenant-ID Header (Priority 1)
       ├─→ Check Subdomain (Priority 2)
       └─→ Check User's Default Tenant (Priority 3)
       │
       ↓
   Request Object Enhanced:
       ├─→ request.tenant = Tenant instance
       └─→ request.tenant_user = TenantUser instance
       │
       ↓
   ViewSet Query:
       └─→ Model.objects.for_tenant(request.tenant)
       │
       ↓
   Database Query:
       └─→ SELECT * FROM table WHERE tenant_id = ?
```

**Why This Approach?**:
- **Operational Efficiency**: Single database, simpler management
- **Cost Effective**: No separate database per tenant
- **Query Performance**: Indexed tenant_id for fast filtering
- **Application-Level Control**: Flexible tenant switching

---

## Multi-Tenancy Architecture

### Architectural Choice: Shared-Schema Multi-Tenancy

ProjectMeats implements a **shared database, shared schema** multi-tenancy model.

```
Single PostgreSQL Database
│
├── Shared Tables (No tenant_id)
│   ├── auth_user
│   ├── auth_group
│   ├── core_protein
│   └── django_migrations
│
├── Tenant Management Tables
│   ├── tenants_tenant
│   ├── tenants_tenantdomain
│   └── tenants_tenantuser (junction table)
│
└── Business Tables (With tenant_id FK)
    ├── suppliers_supplier
    ├── customers_customer
    ├── purchase_orders_purchaseorder
    ├── contacts_contact
    ├── plants_plant
    └── ... (all business entities)
```

### Why Shared-Schema?

**Advantages**:
1. **Simplicity**: Single database to manage, backup, and monitor
2. **Cost Efficiency**: No separate database infrastructure per tenant
3. **Easier Migrations**: Run migrations once, affect all tenants
4. **Cross-Tenant Reporting**: Superusers can query across tenants (with proper authorization)
5. **Resource Sharing**: Efficient use of database connections and memory
6. **Faster Tenant Provisioning**: Create tenant record, no schema creation needed

**Trade-offs**:
1. **Data Isolation**: Application-level (less strict than schema-per-tenant)
2. **Security Responsibility**: Must correctly filter by tenant in all queries
3. **Performance**: Large tenants can impact smaller ones (mitigated by indexing)
4. **Customization**: Limited per-tenant schema customization

### Alternative Considered: django-tenants (Schema-Based)

The project includes `django-tenants` in dependencies but **does not actively use it**:

```python
# settings/base.py
THIRD_PARTY_APPS = [
    # Note: django_tenants is available but not actively used
    # "django_tenants",  # Commented out
]
```

**Why Not Schema-Based?**:
- **Complexity**: Requires schema management, migration per tenant
- **Migration Overhead**: Slower deployments with many tenants
- **Development Friction**: More complex local development setup
- **Cost**: Not justified for current tenant count and isolation needs

**When to Reconsider**:
- Regulatory requirements demand strict data isolation
- Tenant count exceeds 100+
- Performance issues with shared schema
- Custom schema per tenant needed

### Tenant Context Resolution

The `TenantMiddleware` resolves tenant context in this order:

1. **Explicit Header** (`X-Tenant-ID`): API clients specify tenant
2. **Subdomain Routing**: `tenant-slug.projectmeats.com` → `tenant-slug`
3. **User Default Tenant**: First active tenant from user's associations
4. **No Tenant**: Return 403 for tenant-required endpoints

### Tenant-Aware Query Pattern

All ViewSets follow this pattern:

```python
class SupplierViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Supplier.objects.for_tenant(self.request.tenant)
        return Supplier.objects.none()
    
    def perform_create(self, serializer):
        tenant = self.request.tenant or self._get_user_default_tenant()
        if not tenant:
            raise ValidationError('Tenant context required')
        serializer.save(tenant=tenant)
```

---

## Authentication & Authorization

### Authentication Flow

```
User Login (Frontend)
       │
       ↓
   POST /api/auth/login/
       │
       ├─→ Username/Email
       └─→ Password
       │
       ↓
   Django Authentication
       │
       ├─→ Verify Credentials
       └─→ Check is_active
       │
       ↓
   Create Session/Token
       │
       ├─→ Session Cookie (Web)
       └─→ Auth Token (API/Mobile)
       │
       ↓
   Return User Data + Token
       │
       ↓
   Store in Frontend
       │
       ├─→ localStorage (Token)
       └─→ Context/State (User)
       │
       ↓
   Subsequent Requests Include:
       └─→ Authorization: Token <token>
```

### Authentication Methods

1. **Session Authentication** (Web Frontend):
   - Django session cookies
   - CSRF protection enabled
   - Cookie-based, httpOnly

2. **Token Authentication** (API/Mobile):
   - DRF Token Authentication
   - Token stored in `Authorization` header
   - Stateless, suitable for mobile/SPA

3. **Superuser Authentication**:
   - Environment-specific credentials
   - Separate superuser per environment (dev/staging/prod)
   - Password rotation via `setup_superuser` command

### Authorization Model

**Levels of Authorization**:

1. **Authentication Required**: Most endpoints require authenticated user
2. **Tenant Membership**: User must belong to tenant (via TenantUser)
3. **Role-Based**: TenantUser.role defines permissions
4. **Object-Level**: User can only access their tenant's data

**Roles** (in TenantUser):
- `owner`: Full control, tenant management
- `admin`: User management, full data access
- `manager`: Data management, limited user access
- `user`: Standard data access, create/edit own data
- `readonly`: View-only access

**Permission Flow**:

```
Authenticated Request
       │
       ↓
   Check Authentication ───────→ 401 if not authenticated
       │
       ↓
   Check Tenant Membership ────→ 403 if not in tenant
       │
       ↓
   Check Role Permissions ─────→ 403 if insufficient role
       │
       ↓
   Tenant-Scoped Query ────────→ Only returns user's tenant data
       │
       ↓
   Allow Access
```

### Superuser Management

**Environment-Specific Configuration**:

| Environment | Username Variable | Password Variable |
|-------------|-------------------|-------------------|
| Development | `DEVELOPMENT_SUPERUSER_USERNAME` | `DEVELOPMENT_SUPERUSER_PASSWORD` |
| Staging | `STAGING_SUPERUSER_USERNAME` | `STAGING_SUPERUSER_PASSWORD` |
| Production | `PRODUCTION_SUPERUSER_USERNAME` | `PRODUCTION_SUPERUSER_PASSWORD` |

**Management Commands**:
1. `setup_superuser`: Syncs superuser credentials from environment
2. `create_super_tenant`: Creates superuser + root tenant + associations

**Why Environment-Specific?**:
- Different credentials per environment (security)
- Automatic credential rotation in deployments
- No shared passwords across environments

---

## Deployment Architecture

### Three-Environment Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                      PRODUCTION                              │
│  Domain: projectmeats.com                                   │
│  Branch: main                                               │
│  Purpose: Live customer data                                │
│  Deploy: Manual approval required                           │
└─────────────────────────────────────────────────────────────┘
                          ↑
                  Promote from UAT
                          │
┌─────────────────────────────────────────────────────────────┐
│                         UAT                                  │
│  Domain: uat.projectmeats.com                               │
│  Branch: uat                                                │
│  Purpose: Pre-production testing                            │
│  Deploy: Auto from workflow                                 │
└─────────────────────────────────────────────────────────────┘
                          ↑
                 Promote from Dev
                          │
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT                               │
│  Domain: dev.projectmeats.com                               │
│  Branch: development                                        │
│  Purpose: Active development & testing                      │
│  Deploy: Auto on push to development                        │
└─────────────────────────────────────────────────────────────┘
```

### Promotion Workflow

**Critical Rule**: Never push directly to `uat` or `main` branches.

**Workflow**:
1. Feature branch → PR to `development`
2. Merge to `development` → Auto-creates PR to `uat`
3. Test in UAT → Approve PR
4. Merge to `uat` → Auto-creates PR to `main`
5. Final approval → Merge to `main` → Production deploy

**Why This Workflow?**:
- **Quality Gates**: Each environment is a quality gate
- **Testing**: Features tested in dev before UAT, UAT before production
- **Rollback Safety**: Can revert PR instead of force-push
- **Audit Trail**: Clear history of what was promoted when

### Container Architecture (DigitalOcean)

```
DigitalOcean App Platform
│
├── Frontend Service (Container)
│   ├── Image: registry.digitalocean.com/projectmeats/frontend:tag
│   ├── Port: 80 (NGINX)
│   ├── Build: Docker build from /frontend
│   └── Environment: Node.js production build
│
├── Backend Service (Container)
│   ├── Image: registry.digitalocean.com/projectmeats/backend:tag
│   ├── Port: 8000 (Gunicorn)
│   ├── Build: Docker build from /backend
│   ├── Environment: Django production settings
│   └── WSGI: Gunicorn workers
│
└── Managed PostgreSQL Database
    ├── Version: PostgreSQL 15
    ├── Connection: DATABASE_URL environment variable
    ├── Backup: Daily automated backups
    └── High Availability: DO managed service
```

### Deployment Process

**GitHub Actions Workflow**:

1. **Build Phase**:
   - Lint and type-check code
   - Run tests (frontend + backend)
   - Build Docker images
   - Push to DigitalOcean Container Registry

2. **Deploy Phase**:
   - Pull latest images
   - Run database migrations
   - Execute `setup_superuser` (sync credentials)
   - Execute `create_super_tenant` (ensure root tenant)
   - Deploy containers with zero-downtime
   - Health check verification

3. **Verification**:
   - HTTP health check (`/health/`)
   - Database connectivity check
   - Smoke tests (planned)

**Environment Variables**:
- Stored in GitHub Secrets per environment
- Injected at deployment time
- Different secrets for dev/staging/production

---

## Infrastructure & Environments

### Development Environment

**Setup**: Local development with minimal infrastructure

```
Developer Machine
│
├── Backend: Django dev server (./start_dev.sh)
│   ├── Host: localhost:8000
│   ├── Database: PostgreSQL (local) or SQLite (fallback)
│   ├── Settings: projectmeats.settings.development
│   └── Hot Reload: Django auto-reload enabled
│
├── Frontend: React dev server (npm start)
│   ├── Host: localhost:3000
│   ├── Proxy: Backend API at localhost:8000
│   ├── Hot Reload: React hot module replacement
│   └── Build: Development build with source maps
│
└── Database Options:
    ├── PostgreSQL: Local install or Docker
    │   └── Recommended for environment parity
    └── SQLite: Fallback for quick setup
        └── File: backend/db.sqlite3
```

**Development Tools**:
- `start_dev.sh`: Start all services
- `stop_dev.sh`: Stop all services
- `Makefile`: Common development commands
- `pre-commit`: Git hooks for code quality

### Staging/UAT Environment

**Purpose**: Pre-production testing environment

```
DigitalOcean App Platform (UAT)
│
├── Frontend Container
│   ├── URL: https://uat-frontend.ondigitalocean.app
│   └── Environment: Production build, staging API
│
├── Backend Container
│   ├── URL: https://uat-backend.ondigitalocean.app
│   ├── Settings: projectmeats.settings.staging
│   └── Workers: Gunicorn with 2 workers
│
└── PostgreSQL Database (Managed)
    ├── Size: Shared CPU, 1GB RAM
    ├── Backup: Daily automated
    └── Data: Test data, safe to reset
```

**UAT Purpose**:
- Test features in production-like environment
- Validate migrations before production
- Performance testing
- User acceptance testing
- Integration testing with external services

### Production Environment

**Purpose**: Live customer environment

```
DigitalOcean App Platform (Production)
│
├── Frontend Container
│   ├── URL: https://projectmeats.com
│   ├── CDN: Cloudflare (planned)
│   └── Environment: Optimized production build
│
├── Backend Container
│   ├── URL: https://api.projectmeats.com
│   ├── Settings: projectmeats.settings.production
│   ├── Workers: Gunicorn with 4 workers
│   └── Monitoring: Health checks every 60s
│
└── PostgreSQL Database (Managed)
    ├── Size: 2 vCPU, 4GB RAM (scalable)
    ├── Backup: Daily automated + manual before deploys
    ├── Retention: 7 days
    └── High Availability: Standby replica (planned)
```

**Production Safeguards**:
- Debug mode disabled (`DEBUG=False`)
- Strict CORS settings
- Database backup before deployment
- Health checks before cutover
- Rollback plan documented

### Environment Configuration

**Centralized Configuration**: `/config/environments/`

```
config/
├── manage_env.py            # Environment management CLI
└── environments/
    ├── development.env      # Local development config
    ├── staging.env.example  # UAT config template
    └── production.env.example  # Production config template
```

**Key Environment Variables**:
- `DJANGO_ENV`: Environment name (development/staging/production)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Django secret key (unique per environment)
- `ALLOWED_HOSTS`: Allowed domain names
- `CORS_ALLOWED_ORIGINS`: Frontend URLs for CORS
- `OPENAI_API_KEY`: AI Assistant API key
- Superuser credentials (environment-specific)

---

## Key Architectural Decisions

### 1. Shared-Schema Multi-Tenancy

**Decision**: Use shared database with tenant foreign keys instead of schema-per-tenant

**Context**:
- Need multi-tenant support for multiple brokerage companies
- Moderate number of tenants (< 50 expected)
- Cost and operational simplicity important

**Rationale**:
- **Simpler Operations**: Single database to manage, backup, monitor
- **Faster Migrations**: Run once, not per tenant
- **Cost Effective**: Single database instance
- **Developer Experience**: Simpler local development
- **Adequate Isolation**: Application-level filtering sufficient for business needs

**Trade-offs Accepted**:
- Less strict data isolation than schema-per-tenant
- Requires disciplined query filtering
- Large tenant can impact performance (mitigated by indexing)

**When to Revisit**:
- Tenant count > 100
- Regulatory requirements change
- Performance issues arise

### 2. Monolithic Architecture

**Decision**: Single Django monolith instead of microservices

**Context**:
- Team size: Small (< 5 developers)
- Business domain: Cohesive (meat brokerage)
- Deployment frequency: Weekly to bi-weekly

**Rationale**:
- **Simplicity**: Single codebase, single deployment
- **Team Size**: No need for microservices with small team
- **Shared Database**: Business entities are highly interconnected
- **Development Speed**: Faster iteration without distributed system complexity
- **Cost**: Single infrastructure, lower operational cost

**Modular Monolith Pattern**:
- Clear app boundaries (Django apps as bounded contexts)
- Shared utilities in `apps.core`
- Can extract to microservices later if needed

**When to Revisit**:
- Team grows > 10 developers
- Independent scaling needs emerge
- Different deployment frequencies required

### 3. React + Django REST (Not Server-Side Rendering)

**Decision**: SPA (React) + REST API instead of Django templates or Next.js

**Context**:
- Need rich, interactive UI
- Mobile app planned
- Multiple clients (web, mobile, potential third-party)

**Rationale**:
- **API-First**: Same API serves web, mobile, and third-party clients
- **Rich Interactions**: React provides better UX for complex forms and dashboards
- **Team Skills**: Team experienced with React and Django REST
- **Mobile Reuse**: Share API and some business logic with React Native

**Trade-offs Accepted**:
- SEO less important (business application, not public website)
- More complex frontend setup
- Client-side routing complexity

**Not Chosen**:
- **Django Templates**: Limited interactivity, harder mobile story
- **Next.js/SSR**: Overkill for private business app, adds complexity

### 4. PostgreSQL (Not NoSQL)

**Decision**: PostgreSQL as primary database

**Context**:
- Relational business data (suppliers, customers, orders)
- Need for complex queries and joins
- ACID compliance important for financial data

**Rationale**:
- **Relational Data**: Business entities are highly relational
- **Data Integrity**: Foreign keys, constraints, transactions
- **Query Power**: SQL for complex reports and analytics
- **Proven Technology**: Well-understood, stable, performant
- **Multi-Tenancy**: Excellent support for tenant isolation

**Trade-offs Accepted**:
- Scaling writes harder than NoSQL (not a current concern)
- Schema migrations required (acceptable with good process)

### 5. OpenAI API Integration (Not Self-Hosted LLM)

**Decision**: Use OpenAI API instead of self-hosted model

**Context**:
- AI Assistant feature for document processing
- Limited ML expertise in team
- Cost vs. value trade-off

**Rationale**:
- **Quality**: GPT-4 is state-of-the-art
- **Time to Market**: Immediate integration, no training
- **Operational Simplicity**: No GPU infrastructure to manage
- **Cost Effective**: Pay-per-use, no upfront infrastructure cost

**Trade-offs Accepted**:
- Data sent to third-party (mitigated: no PII in documents)
- Ongoing API costs
- Latency (acceptable for current use case)

**When to Revisit**:
- Privacy/compliance requirements change
- Cost becomes prohibitive
- Need for customization increases

### 6. DigitalOcean App Platform (Not AWS/GCP)

**Decision**: Deploy to DigitalOcean App Platform

**Context**:
- Need managed platform (limited DevOps resources)
- Cost sensitivity
- Moderate scale requirements

**Rationale**:
- **Simplicity**: Managed containers, database, networking
- **Cost**: Predictable pricing, lower than AWS/GCP for this scale
- **Developer Experience**: Simple deployment from Git
- **Sufficient Features**: Meets current scaling needs

**Trade-offs Accepted**:
- Less ecosystem than AWS/GCP
- Fewer advanced services
- Potential migration needed at large scale

**When to Revisit**:
- Need advanced services (ML, data warehouse, etc.)
- Scale exceeds DO capabilities
- Multi-region deployment needed

### 7. Session + Token Authentication (Not OAuth2)

**Decision**: Django session (web) + DRF token (API) instead of OAuth2/JWT

**Context**:
- Internal business application
- No third-party login needed (yet)
- Team familiar with Django auth

**Rationale**:
- **Simplicity**: Built-in Django auth, well-understood
- **Sufficient**: Meets current requirements
- **Easy to Upgrade**: Can add OAuth2 later if needed

**Trade-offs Accepted**:
- No SSO (not required yet)
- Stateful sessions (acceptable for web)
- Manual token management (acceptable for API)

**When to Revisit**:
- Need SSO integration (Google, Azure AD)
- Mobile app requires refresh tokens
- Third-party API access needed

---

## Integration Points

### 1. OpenAI API Integration

**Purpose**: AI Assistant functionality

**Integration Type**: REST API (synchronous)

**Endpoints Used**:
- `POST /v1/chat/completions` - Chat interface
- `POST /v1/embeddings` - Document embeddings (planned)

**Data Flow**:
```
User Message → Backend → OpenAI API → Response → Backend → User
```

**Error Handling**:
- Timeout: 30 seconds
- Retry: 3 attempts with exponential backoff
- Fallback: Return error message to user

**Cost Management**:
- Token limits per request
- Usage tracking per tenant (planned)
- Model selection (GPT-4 vs GPT-3.5 based on query)

### 2. Email Service Integration (Planned)

**Purpose**: User notifications, password reset

**Integration Type**: SMTP (asynchronous)

**Planned Architecture**:
```
Event → Celery Task → Email Queue → SMTP Server → User
```

**Use Cases**:
- Password reset emails
- Order confirmations
- Payment reminders
- System notifications

### 3. File Storage Integration

**Current**: Local filesystem  
**Planned**: S3-compatible object storage

**Purpose**: Document uploads, exports

**Migration Path**:
- Abstract storage with Django Storage API
- Switch to django-storages + S3/DigitalOcean Spaces
- Migrate existing files

---

## Scalability & Performance

### Current Scale

- **Users**: < 100 concurrent users
- **Tenants**: < 20 active tenants
- **Database**: < 10 GB data
- **Requests**: < 100 req/min average

### Performance Optimizations

1. **Database**:
   - Indexed `tenant_id` on all business tables
   - `select_related()` and `prefetch_related()` for N+1 prevention
   - Database connection pooling

2. **API**:
   - DRF pagination (default 100 items)
   - Field filtering (only return needed fields)
   - Gzip compression enabled

3. **Frontend**:
   - Code splitting (React.lazy())
   - Production build optimization
   - Asset minification and tree-shaking

### Scaling Strategy

**Vertical Scaling** (Current):
- Increase container resources (CPU, RAM)
- Scale database instance size

**Horizontal Scaling** (Future):
- Multiple backend containers (load balanced)
- Read replicas for database
- Redis for session storage and caching

**Caching Strategy** (Planned):
```
Redis Cache Layer
├── Session storage
├── API response caching (read-heavy endpoints)
├── Query result caching
└── Static data caching (proteins, choices)
```

### Performance Monitoring

**Current**:
- Health check endpoint (`/health/`)
- DigitalOcean metrics (CPU, RAM, response time)

**Planned**:
- APM tool (New Relic, Sentry)
- Query performance monitoring
- User-facing latency tracking
- Error rate monitoring

---

## Security Architecture

### Defense in Depth

```
Layer 1: Network
├── HTTPS only (enforced)
├── CORS restrictions
└── Rate limiting (planned)

Layer 2: Application
├── Authentication required
├── Tenant isolation enforced
├── Role-based authorization
└── Input validation (serializers)

Layer 3: Data
├── Tenant-scoped queries
├── SQL injection prevention (ORM)
├── XSS prevention (React escaping)
└── CSRF protection (Django)

Layer 4: Infrastructure
├── Environment variables for secrets
├── No secrets in code
├── Separate credentials per environment
└── Principle of least privilege
```

### Security Best Practices

1. **Secrets Management**:
   - GitHub Secrets for CI/CD
   - Environment variables in production
   - No secrets committed to repository
   - Separate secrets per environment

2. **Database Security**:
   - Tenant isolation in queries
   - Parameterized queries (ORM)
   - Database user with minimal permissions
   - Encrypted connections

3. **API Security**:
   - Authentication required for all endpoints (except login)
   - CORS whitelist (no wildcard)
   - CSRF protection for state-changing requests
   - Input validation and sanitization

4. **Frontend Security**:
   - React's built-in XSS protection
   - Content Security Policy (planned)
   - Secure token storage
   - Logout on token expiry

### Compliance Considerations

**Data Privacy**:
- Tenant data isolation
- No PII in logs
- Audit trail (planned)
- Data export capability (planned)

**Business Continuity**:
- Daily database backups
- Backup before deployments
- 7-day retention
- Documented rollback procedure

---

## Related Documentation

### Architecture Documentation
- **[Backend Architecture](BACKEND_ARCHITECTURE.md)** - Django backend details
- **[Frontend Architecture](FRONTEND_ARCHITECTURE.md)** - React frontend details
- **[Multi-Tenancy Guide](MULTI_TENANCY_GUIDE.md)** - Detailed multi-tenancy implementation

### Setup & Deployment
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Comprehensive deployment instructions
- **[Environment Guide](ENVIRONMENT_GUIDE.md)** - Environment configuration
- **[Main README](../README.md)** - Quick start and overview

### Development
- **[Authentication Guide](AUTHENTICATION_GUIDE.md)** - Auth system details
- **[Migration Guide](MIGRATION_GUIDE.md)** - Database migrations
- **[Testing Strategy](TESTING_STRATEGY.md)** - Testing approach
- **[Repository Best Practices](REPOSITORY_BEST_PRACTICES.md)** - Development workflow

### Operations
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Common issues and solutions
- **[3-Month Retrospective](lessons-learned/3-MONTH-RETROSPECTIVE.md)** - Lessons learned

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-12-01 | 1.0 | Initial comprehensive architecture document | GitHub Copilot |

---

**For Questions or Updates**: Create an issue or contact the development team.
