# ProjectMeats Backend Architecture

## Overview

ProjectMeats backend is built with Django 4.2.7 and Django REST Framework, providing a comprehensive API for meat market operations with multi-tenant support.

## Technology Stack

- **Framework**: Django 4.2.7
- **API**: Django REST Framework
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Documentation**: drf-spectacular (OpenAPI/Swagger)
- **Authentication**: Django Auth + JWT (planned)

## Project Structure

```
backend/
├── apps/                          # Business domain applications
│   ├── accounts_receivables/      # Customer payment tracking
│   ├── ai_assistant/              # AI-powered chatbot and document processing
│   ├── bug_reports/               # Bug tracking system
│   ├── carriers/                  # Transportation and logistics
│   ├── contacts/                  # Contact management (shared)
│   ├── core/                      # Shared utilities and base models
│   ├── customers/                 # Customer management
│   ├── plants/                    # Processing facilities and locations
│   ├── purchase_orders/           # Order processing and management
│   ├── suppliers/                 # Supplier relationships
│   └── tenants/                   # Multi-tenancy support
├── projectmeats/                  # Django project configuration
│   ├── settings/                  # Environment-specific settings
│   │   ├── __init__.py           # Settings loader
│   │   ├── base.py               # Common settings
│   │   ├── development.py        # Development overrides
│   │   ├── staging.py            # Staging overrides
│   │   └── production.py         # Production overrides
│   ├── health.py                 # Health check endpoints
│   ├── urls.py                   # URL routing
│   ├── wsgi.py                   # WSGI application
│   └── asgi.py                   # ASGI application
├── static/                        # Static files (collectstatic)
├── requirements.txt               # Python dependencies
└── manage.py                     # Django management script
```

## Application Domains

### Core Apps

#### 1. **core** - Foundation Layer
- **Purpose**: Shared utilities, base models, and common functionality
- **Key Models**:
  - `Protein`: Meat types and categories
  - `TimestampModel`: Base model with created/updated timestamps
- **Usage**: Inherited by other apps for consistency

#### 2. **tenants** - Multi-tenancy
- **Purpose**: Manage multiple customers/organizations in a single deployment
- **Key Models**:
  - `Tenant`: Organization/company entity
- **Pattern**: Shared database, tenant-scoped queries
- **Features**:
  - Tenant isolation
  - Tenant-specific data filtering
  - Subdomain or path-based routing (planned)

### Business Entity Apps

#### 3. **customers** - Customer Management
- **Purpose**: Manage customer relationships and data
- **Key Models**:
  - `Customer`: Customer entity with contact and plant associations
- **Dependencies**: contacts, core, plants
- **Features**:
  - Customer profiles
  - Contact management
  - Plant/location tracking
  - Protein preferences

#### 4. **suppliers** - Supplier Management
- **Purpose**: Manage supplier relationships and procurement
- **Key Models**:
  - `Supplier`: Supplier entity with capabilities
- **Dependencies**: contacts, core, plants
- **Features**:
  - Supplier profiles
  - Capability tracking
  - Contact management
  - Quality ratings

#### 5. **purchase_orders** - Order Processing
- **Purpose**: Handle purchase orders and fulfillment
- **Key Models**:
  - `PurchaseOrder`: Order tracking and management
  - `OrderItem`: Line items and details
- **Dependencies**: customers, suppliers, core
- **Features**:
  - Order creation and tracking
  - Status management
  - Line item details
  - Pricing and totals

#### 6. **contacts** - Contact Management
- **Purpose**: Centralized contact information for customers and suppliers
- **Key Models**:
  - `Contact`: Person or role contact details
- **Dependencies**: core
- **Features**:
  - Email and phone tracking
  - Role-based contacts
  - Shared across customers and suppliers

#### 7. **plants** - Facility Management
- **Purpose**: Manage processing plants and distribution centers
- **Key Models**:
  - `Plant`: Physical location and capabilities
- **Dependencies**: core
- **Features**:
  - Location tracking
  - Facility types (processing, distribution, warehouse, retail)
  - Capacity management

#### 8. **carriers** - Transportation
- **Purpose**: Manage transportation and logistics
- **Key Models**:
  - `Carrier`: Transportation provider
- **Dependencies**: core
- **Features**:
  - Carrier types (truck, rail, air, sea)
  - Contact management
  - Service tracking

### Supporting Apps

#### 9. **accounts_receivables** - Financial Tracking
- **Purpose**: Track customer payments and receivables
- **Key Models**:
  - `AccountsReceivable`: Payment tracking
- **Dependencies**: customers
- **Features**:
  - Payment status tracking
  - Due date management
  - Amount tracking

#### 10. **ai_assistant** - AI Integration
- **Purpose**: AI-powered chatbot and document processing
- **Key Models**:
  - `Conversation`: Chat sessions
  - `Message`: Individual chat messages
  - `Document`: Uploaded documents
- **Dependencies**: All business apps
- **Features**:
  - Natural language queries
  - Document upload and analysis
  - Entity extraction
  - Business intelligence

#### 11. **bug_reports** - Issue Tracking
- **Purpose**: Internal bug tracking and user feedback
- **Key Models**:
  - `BugReport`: Issue tracking
- **Features**:
  - Bug submission
  - Status tracking
  - Priority management

## Settings Architecture

The project uses a modular settings structure for different environments:

### Settings Hierarchy

1. **base.py** - Common settings for all environments
   - Installed apps
   - Middleware
   - Database configuration (via DATABASE_URL)
   - Static files
   - Templates
   - REST Framework configuration
   - CORS settings

2. **development.py** - Development overrides
   - DEBUG=True
   - SQLite database
   - Console email backend
   - Relaxed security settings
   - Django Debug Toolbar (optional)

3. **staging.py** - Staging overrides
   - DEBUG=False
   - PostgreSQL database
   - Production-like security
   - Separate domain/subdomain

4. **production.py** - Production overrides
   - DEBUG=False
   - PostgreSQL database
   - Full security hardening
   - ALLOWED_HOSTS configuration
   - Static file serving optimization
   - Error logging

### Environment Selection

Settings are loaded via `DJANGO_SETTINGS_MODULE` environment variable:
- Development: `projectmeats.settings.development`
- Staging: `projectmeats.settings.staging`
- Production: `projectmeats.settings.production`

## API Design

### RESTful Conventions

- **List**: `GET /api/v1/resource/`
- **Create**: `POST /api/v1/resource/`
- **Retrieve**: `GET /api/v1/resource/{id}/`
- **Update**: `PUT /api/v1/resource/{id}/`
- **Partial Update**: `PATCH /api/v1/resource/{id}/`
- **Delete**: `DELETE /api/v1/resource/{id}/`

### API Versioning

- Current version: `v1`
- Base path: `/api/v1/`
- Future versions will use `/api/v2/`, etc.

### Authentication

- Current: Django session authentication
- Planned: JWT tokens for mobile/SPA

### Documentation

- **OpenAPI Schema**: Generated via drf-spectacular
- **Interactive Docs**: Available at `/api/schema/swagger-ui/`
- **ReDoc**: Available at `/api/schema/redoc/`

## Multi-Tenancy Pattern

### Current Implementation

- **Model**: Shared database, shared schema
- **Approach**: Tenant-scoped queries using middleware
- **Isolation**: Tenant ID filtering on queries

### Tenant Context

All models that need tenant isolation should:
1. Include a `tenant` foreign key
2. Use tenant-aware managers
3. Filter queries by current tenant context

### Future Enhancements

- Subdomain-based tenant routing
- Tenant-specific customization
- Cross-tenant reporting (admin only)

## Database Schema

### Core Tables

- **core_protein**: Meat types and categories
- **tenants_tenant**: Organization/company entities

### Business Tables

- **customers_customer**: Customer profiles
- **suppliers_supplier**: Supplier profiles
- **purchase_orders_purchaseorder**: Order tracking
- **contacts_contact**: Contact information
- **plants_plant**: Facility locations
- **carriers_carrier**: Transportation providers

### Supporting Tables

- **accounts_receivables_accountsreceivable**: Payment tracking
- **ai_assistant_conversation**: Chat sessions
- **ai_assistant_message**: Chat messages
- **ai_assistant_document**: Uploaded documents
- **bug_reports_bugreport**: Issue tracking

## Security Considerations

### Data Isolation

- Tenant-scoped queries prevent cross-tenant data access
- Row-level security through tenant filtering
- User permissions tied to tenant membership

### Authentication & Authorization

- Django's built-in authentication system
- Permission classes on API views
- Future: JWT for stateless authentication

### CORS & CSRF

- CORS configured for known frontend origins
- CSRF protection enabled for session auth
- CSRF exempt for JWT endpoints (when implemented)

### Environment Variables

- Secrets stored in environment variables
- Never committed to version control
- Different secrets per environment

## Testing Strategy

### Current Tests

- Basic model tests (minimal)
- API endpoint tests for purchase_orders
- Settings configuration tests

### Testing Approach

- Unit tests for models and utilities
- Integration tests for API endpoints
- Test fixtures for complex scenarios
- CI/CD integration via GitHub Actions

### Running Tests

```bash
# All tests
python manage.py test

# Specific app
python manage.py test apps.purchase_orders

# With coverage
coverage run --source='.' manage.py test
coverage report
```

## Deployment

### Environment Setup

1. **Development**: SQLite, minimal config
2. **Staging**: PostgreSQL, production-like
3. **Production**: PostgreSQL, full optimization

### Static Files

- Development: Served by Django
- Production: Collected to `staticfiles/` and served by web server

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Rollback if needed
python manage.py migrate app_name migration_name
```

### Health Checks

Health check endpoint at `/health/` provides:
- Database connectivity
- Application status
- Version information

## Performance Optimization

### Database

- Indexed fields on commonly queried columns
- Select/prefetch related for N+1 query prevention
- Database connection pooling in production

### Caching

- Planned: Redis for session and data caching
- Cache API responses for read-heavy operations
- Cache invalidation on updates

### Query Optimization

- Use `.only()` and `.defer()` for large models
- Aggregate queries for reporting
- Avoid select_related/prefetch_related overuse

## Future Enhancements

1. **Authentication**
   - JWT token authentication
   - OAuth2 integration
   - Two-factor authentication

2. **Multi-tenancy**
   - Subdomain routing
   - Tenant customization
   - White-labeling support

3. **Advanced Features**
   - Real-time notifications (WebSockets)
   - Advanced reporting and analytics
   - Integration APIs (QuickBooks, etc.)
   - Mobile API optimization

4. **DevOps**
   - Automated testing suite expansion
   - Performance monitoring
   - Log aggregation
   - Database backup automation

## References

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [drf-spectacular](https://drf-spectacular.readthedocs.io/)
- [Multi-tenancy Patterns](https://django-tenants.readthedocs.io/)
