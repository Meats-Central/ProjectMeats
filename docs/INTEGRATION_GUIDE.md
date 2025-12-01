# ProjectMeats Integration Guide

**Last Updated**: December 1, 2024

This guide provides a comprehensive overview of integration points, external dependencies, and cross-component communication patterns in ProjectMeats.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Integration Points](#integration-points)
3. [External Dependencies](#external-dependencies)
4. [Cross-Component Communication](#cross-component-communication)
5. [API Integration Patterns](#api-integration-patterns)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [Security & Authentication](#security--authentication)
8. [Error Handling](#error-handling)
9. [Performance Considerations](#performance-considerations)
10. [Future Enhancements](#future-enhancements)

---

## Architecture Overview

ProjectMeats follows a **three-tier architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  React 18.2.0 + TypeScript + Ant Design + Styled Components│
│                    Port: 3000                               │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API (HTTP/HTTPS)
                       │ JSON over HTTP
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend Layer                           │
│     Django 4.2.7 + Django REST Framework + Multi-tenancy   │
│                    Port: 8000                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  PostgreSQL  │ │ OpenAI   │ │ File Storage │
│   Database   │ │   API    │ │  (Media)     │
│   Port: 5432 │ │ (HTTPS)  │ │  (Local/S3)  │
└──────────────┘ └──────────┘ └──────────────┘
```

### Component Responsibilities

- **Frontend**: User interface, client-side validation, state management, API consumption
- **Backend**: Business logic, data validation, API endpoints, authentication, multi-tenancy
- **Database**: Data persistence, ACID compliance, multi-tenant data isolation
- **External Services**: AI processing, file storage, email delivery (future)

---

## Integration Points

### 1. Frontend ↔ Backend Integration

#### Communication Protocol
- **Protocol**: REST API over HTTP/HTTPS
- **Format**: JSON
- **Base URL**: `http://localhost:8000/api/v1` (dev) / `https://api.projectmeats.com/api/v1` (prod)
- **Authentication**: Token-based authentication (Django REST Framework tokens)

#### API Client Configuration

**Frontend API Client** (`frontend/src/services/apiService.ts`):

```typescript
const apiClient = axios.create({
  baseURL: API_BASE_URL,  // http://localhost:8000/api/v1
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - adds auth token and tenant context
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  
  const tenantId = localStorage.getItem('tenantId');
  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId;
  }
  
  return config;
});
```

#### API Endpoints Mapping

| Frontend Service | Backend Endpoint | Purpose |
|-----------------|------------------|---------|
| `apiService.getSuppliers()` | `GET /api/v1/suppliers/` | List suppliers |
| `apiService.createSupplier()` | `POST /api/v1/suppliers/` | Create supplier |
| `apiService.getCustomers()` | `GET /api/v1/customers/` | List customers |
| `apiService.getPurchaseOrders()` | `GET /api/v1/purchase-orders/` | List purchase orders |
| `authService.login()` | `POST /api/v1/auth/login/` | User authentication |
| `aiService.chat()` | `POST /api/v1/ai-assistant/chat/` | AI chat interactions |

**Complete API Reference**: See [Backend Architecture](BACKEND_ARCHITECTURE.md#api-design)

### 2. Backend ↔ Database Integration

#### Database Configuration

**Development** (SQLite fallback):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Production** (PostgreSQL):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'projectmeats'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

#### ORM Usage Pattern

```python
# Example: Tenant-scoped query
from apps.suppliers.models import Supplier

# All queries are automatically scoped to current tenant via middleware
suppliers = Supplier.objects.filter(is_active=True)
```

**Multi-Tenancy Pattern**: See [Multi-Tenancy Guide](MULTI_TENANCY_GUIDE.md)

### 3. Backend ↔ External Services Integration

#### AI Services (OpenAI)

**Current Status**: Mock implementation for AI assistant
**Future Integration**: OpenAI GPT-4 API

```python
# apps/ai_assistant/views.py (simplified)
class ChatBotAPIViewSet(viewsets.ViewSet):
    def chat(self, request):
        user_message = request.data['message']
        
        # Future: OpenAI API integration
        # response = openai.ChatCompletion.create(
        #     model="gpt-4o-mini",
        #     messages=[{"role": "user", "content": user_message}]
        # )
        
        # Current: Mock response
        response_text = self._generate_mock_response(user_message)
        return Response({'response': response_text})
```

**Environment Variables**:
- `OPENAI_API_KEY` - OpenAI API key (optional, not yet implemented)
- `ANTHROPIC_API_KEY` - Anthropic API key (optional, future)

#### File Storage

**Current**: Local file storage
**Future**: AWS S3 or similar cloud storage

```python
# settings/base.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Future: S3 configuration
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
```

---

## External Dependencies

### Backend Dependencies

#### Core Framework Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| Django | 4.2.7 | Web framework | Framework |
| djangorestframework | 3.14.0 | REST API framework | Framework |
| django-cors-headers | 4.3.1 | CORS handling | Middleware |
| django-filter | 23.3 | API filtering | API |
| drf-spectacular | 0.27.0 | API documentation (OpenAPI) | Documentation |

#### Database Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| psycopg2-binary | 2.9.9 | PostgreSQL adapter | Database |
| dj-database-url | 2.1.0 | Database URL parsing | Configuration |

#### Multi-Tenancy Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| django-tenants | 3.5.0 | Schema-based multi-tenancy (available, not actively used) | Multi-tenancy |

**Note**: ProjectMeats uses a **custom shared-schema multi-tenancy** approach instead of django-tenants' schema-based isolation. See [Multi-Tenancy Guide](MULTI_TENANCY_GUIDE.md) for details.

#### Development & Testing Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| pytest-django | 4.7.0 | Testing framework | Testing |
| pytest-cov | 4.1.0 | Code coverage | Testing |
| factory-boy | 3.3.0 | Test fixtures | Testing |
| black | 23.11.0 | Code formatter | Code Quality |
| flake8 | 6.1.0 | Linter | Code Quality |
| isort | 5.12.0 | Import sorter | Code Quality |
| pre-commit | 3.5.0 | Git hooks | Code Quality |

#### Production Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| gunicorn | 21.2.0 | WSGI HTTP server | Server |
| whitenoise | 6.6.0 | Static file serving | Server |
| django-environ | 0.11.2 | Environment variable handling | Configuration |

#### Utility Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| Pillow | ≥10.2.0 | Image processing | Utility |
| psutil | ≥5.9.0 | System health monitoring | Utility |
| requests | ≥2.31.0 | HTTP client (GitHub API) | Utility |

### Frontend Dependencies

#### Core Framework Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| react | 18.2.0 | UI library | Framework |
| react-dom | 18.2.0 | React DOM renderer | Framework |
| react-scripts | 5.0.1 | Build tooling (CRA) | Build Tool |
| typescript | 4.9.5 | Type safety | Language |

#### UI Component Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| antd | 5.27.3 | UI component library | UI |
| @ant-design/icons | 6.0.2 | Icon library | UI |
| styled-components | 6.1.0 | CSS-in-JS styling | Styling |

#### Routing & State Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| react-router-dom | 6.30.1 | Client-side routing | Routing |

#### API & Data Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| axios | 1.6.0 | HTTP client | API |

#### Data Visualization Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| recharts | 3.2.0 | Charts library | Visualization |
| reactflow | 11.11.4 | Workflow diagrams | Visualization |
| react-table | 7.8.0 | Table component | Data Display |

#### Development Dependencies

| Package | Version | Purpose | Type |
|---------|---------|---------|------|
| @testing-library/react | 16.3.0 | Testing utilities | Testing |
| @testing-library/jest-dom | 6.6.3 | Jest matchers | Testing |
| eslint | 8.57.1 | Linter | Code Quality |
| prettier | 3.6.2 | Code formatter | Code Quality |
| storybook | 9.1.5 | Component documentation | Documentation |
| react-app-rewired | 2.2.1 | CRA configuration override | Build Tool |

### External Service Dependencies

#### AI Services (Future)

- **OpenAI API** (not yet integrated)
  - Model: GPT-4o-mini
  - Purpose: AI assistant chat, document processing
  - Status: Mock implementation in place

#### Infrastructure Services

- **PostgreSQL** (Production)
  - Version: 12+
  - Purpose: Primary database
  - Connection: psycopg2-binary

- **File Storage**
  - Current: Local filesystem
  - Future: AWS S3 or similar

#### CI/CD Services

- **GitHub Actions**
  - Purpose: Continuous integration and deployment
  - Workflows: Build, test, lint, deploy
  - See [CI/CD Infrastructure](workflows/cicd-infrastructure.md)

---

## Cross-Component Communication

### 1. Frontend Service Layer Architecture

#### Service Hierarchy

```
┌────────────────────────────────────────────┐
│         React Components                   │
│  (Pages, UI Components, Features)          │
└─────────────────┬──────────────────────────┘
                  │
                  │ uses
                  ▼
┌────────────────────────────────────────────┐
│         Service Layer                      │
│  ┌──────────────────────────────────────┐ │
│  │ authService.ts                       │ │
│  │ - login(), logout(), register()      │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │ apiService.ts (Generic HTTP Client)  │ │
│  │ - axios wrapper, interceptors        │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │ businessApi.ts                       │ │
│  │ - getSuppliers(), getCustomers()     │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │ aiService.ts                         │ │
│  │ - chat(), uploadDocument()           │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │ tenantService.ts                     │ │
│  │ - getTenants(), switchTenant()       │ │
│  └──────────────────────────────────────┘ │
└─────────────────┬──────────────────────────┘
                  │
                  │ HTTP/HTTPS
                  ▼
┌────────────────────────────────────────────┐
│         Backend API                        │
│         Django REST Framework              │
└────────────────────────────────────────────┘
```

#### Communication Pattern: Request Flow

```
1. User Action (e.g., Click "Add Supplier")
   ↓
2. React Component Handler
   ↓
3. Service Call (apiService.createSupplier())
   ↓
4. Axios Request Interceptor
   - Add auth token
   - Add tenant context
   - Set headers
   ↓
5. HTTP POST to Backend
   ↓
6. Django Middleware Stack
   - CORS handling
   - Authentication
   - Tenant resolution
   ↓
7. Django REST Framework View
   - Validation
   - Business logic
   - Database operations
   ↓
8. Response (JSON)
   ↓
9. Axios Response Interceptor
   - Error handling
   - Token refresh (future)
   ↓
10. Service Returns Data
    ↓
11. Component Updates State
    ↓
12. UI Re-renders
```

### 2. Backend Request Processing

#### Middleware Stack

```python
# projectmeats/settings/base.py
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",        # 1. CORS handling
    "django.middleware.security.SecurityMiddleware", # 2. Security headers
    "whitenoise.middleware.WhiteNoiseMiddleware",   # 3. Static files
    "django.contrib.sessions.middleware.SessionMiddleware", # 4. Session management
    "django.middleware.common.CommonMiddleware",    # 5. Common processing
    "django.middleware.csrf.CsrfViewMiddleware",    # 6. CSRF protection
    "django.contrib.auth.middleware.AuthenticationMiddleware", # 7. Authentication
    "apps.tenants.middleware.TenantMiddleware",     # 8. Multi-tenancy
    "django.contrib.messages.middleware.MessageMiddleware", # 9. Flash messages
    "django.middleware.clickjacking.XFrameOptionsMiddleware", # 10. Clickjacking protection
]
```

#### Request Processing Flow

```
1. HTTP Request arrives
   ↓
2. CORS Middleware
   - Validate origin
   - Add CORS headers
   ↓
3. Security Middleware
   - Add security headers
   - Enforce HTTPS (production)
   ↓
4. Session Middleware
   - Load session data
   ↓
5. Authentication Middleware
   - Validate auth token
   - Load user object
   ↓
6. Tenant Middleware (Custom)
   - Extract tenant context
   - Set current tenant
   ↓
7. URL Routing
   - Match URL pattern
   - Route to view
   ↓
8. DRF View Processing
   - Permission checks
   - Serializer validation
   - Business logic
   - Database queries
   ↓
9. Response Generation
   - Serialize data
   - Format as JSON
   ↓
10. Response Middleware (reverse order)
    ↓
11. HTTP Response sent
```

### 3. Multi-Tenant Communication Pattern

#### Tenant Context Resolution

```python
# apps/tenants/middleware.py (simplified)
class TenantMiddleware:
    def __call__(self, request):
        # Extract tenant from header or user
        tenant_id = request.headers.get('X-Tenant-ID')
        
        if not tenant_id and request.user.is_authenticated:
            tenant_id = request.user.tenant_id
        
        # Set tenant context
        request.tenant = Tenant.objects.get(id=tenant_id)
        
        response = self.get_response(request)
        return response
```

#### Tenant-Scoped Queries

All model queries are automatically scoped to the current tenant:

```python
# Automatic tenant filtering via model manager
class TenantAwareManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            tenant=get_current_tenant()
        )

class Supplier(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    
    objects = TenantAwareManager()  # Use tenant-aware manager
```

### 4. API Communication Patterns

#### RESTful API Conventions

| HTTP Method | Endpoint Pattern | Purpose | Response Code |
|-------------|------------------|---------|---------------|
| GET | `/api/v1/resource/` | List resources | 200 OK |
| POST | `/api/v1/resource/` | Create resource | 201 Created |
| GET | `/api/v1/resource/{id}/` | Retrieve single resource | 200 OK |
| PUT | `/api/v1/resource/{id}/` | Full update | 200 OK |
| PATCH | `/api/v1/resource/{id}/` | Partial update | 200 OK |
| DELETE | `/api/v1/resource/{id}/` | Delete resource | 204 No Content |

#### Request/Response Format

**Request Example** (Create Supplier):
```http
POST /api/v1/suppliers/
Authorization: Token abc123...
X-Tenant-ID: tenant-uuid
Content-Type: application/json

{
  "name": "Quality Meats Inc",
  "contact_person": "John Doe",
  "email": "john@qualitymeats.com",
  "phone": "+1-555-0100"
}
```

**Response Example**:
```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "id": 42,
  "name": "Quality Meats Inc",
  "contact_person": "John Doe",
  "email": "john@qualitymeats.com",
  "phone": "+1-555-0100",
  "created_at": "2024-12-01T12:00:00Z",
  "updated_at": "2024-12-01T12:00:00Z"
}
```

---

## API Integration Patterns

### 1. Pagination

**Backend Implementation**:
```python
# DRF Pagination (settings/base.py)
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25
}
```

**Response Format**:
```json
{
  "count": 100,
  "next": "http://api.example.com/api/v1/suppliers/?page=2",
  "previous": null,
  "results": [
    { "id": 1, "name": "Supplier 1" },
    { "id": 2, "name": "Supplier 2" }
  ]
}
```

**Frontend Usage**:
```typescript
async getSuppliers(page: number = 1): Promise<{results: Supplier[], count: number}> {
  const response = await apiClient.get(`/suppliers/?page=${page}`);
  return response.data;
}
```

### 2. Filtering and Search

**Backend Configuration**:
```python
from django_filters import rest_framework as filters

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_fields = ['name', 'is_active']
    search_fields = ['name', 'contact_person', 'email']
```

**Frontend Usage**:
```typescript
// Filter by status
await apiClient.get('/suppliers/?is_active=true');

// Search by name
await apiClient.get('/suppliers/?search=quality');
```

### 3. Error Handling

**Backend Error Response**:
```python
# Validation error response
{
  "email": ["Enter a valid email address."],
  "phone": ["This field is required."]
}

# Generic error response
{
  "detail": "Not found."
}
```

**Frontend Error Handling**:
```typescript
try {
  await apiService.createSupplier(data);
} catch (error) {
  if (error.response?.status === 400) {
    // Validation errors
    const errors = error.response.data;
    displayValidationErrors(errors);
  } else if (error.response?.status === 401) {
    // Authentication error
    redirectToLogin();
  } else {
    // Generic error
    showErrorMessage('An error occurred. Please try again.');
  }
}
```

### 4. Authentication Flow

```
┌─────────────┐                      ┌─────────────┐
│  Frontend   │                      │   Backend   │
└──────┬──────┘                      └──────┬──────┘
       │                                    │
       │ POST /api/v1/auth/login/           │
       │ { username, password }             │
       │───────────────────────────────────>│
       │                                    │
       │                           Verify credentials
       │                           Create/get token
       │                                    │
       │           200 OK                   │
       │ { token: "abc123...", user: {...} }│
       │<───────────────────────────────────│
       │                                    │
Store token in                              │
localStorage                                │
       │                                    │
       │ GET /api/v1/suppliers/             │
       │ Authorization: Token abc123...     │
       │───────────────────────────────────>│
       │                                    │
       │                         Validate token
       │                         Return data
       │                                    │
       │           200 OK                   │
       │ { results: [...] }                 │
       │<───────────────────────────────────│
       │                                    │
```

---

## Data Flow Diagrams

### Complete Request-Response Cycle

```
┌──────────────────────────────────────────────────────────────┐
│                    User Action                                │
│              (e.g., Create Supplier)                          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                React Component                                │
│  - Form validation                                            │
│  - Collect form data                                          │
│  - Call service method                                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│            apiService.createSupplier(data)                    │
│  - Format request                                             │
│  - Add authentication                                         │
│  - Add tenant context                                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼ HTTP POST
┌──────────────────────────────────────────────────────────────┐
│                  Django Backend                               │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Middleware Stack                                     │   │
│  │ - CORS validation                                    │   │
│  │ - Authentication check                               │   │
│  │ - Tenant resolution                                  │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ SupplierViewSet.create()                            │   │
│  │ - Permission check                                   │   │
│  │ - Serializer validation                              │   │
│  │ - Business logic                                     │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Database (PostgreSQL)                               │   │
│  │ - INSERT INTO suppliers_supplier                     │   │
│  │ - Return created record                              │   │
│  └──────────────────────┬───────────────────────────────┘   │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼ JSON Response
┌──────────────────────────────────────────────────────────────┐
│            Frontend Receives Response                         │
│  - Parse JSON                                                 │
│  - Update local state                                         │
│  - Show success message                                       │
│  - Refresh supplier list                                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   UI Updates                                  │
│  - Close form modal                                           │
│  - Show new supplier in list                                  │
│  - Display success notification                               │
└──────────────────────────────────────────────────────────────┘
```

### Multi-Tenant Data Isolation

```
┌─────────────────────────────────────────────────────────────┐
│                   HTTP Request                               │
│  Header: X-Tenant-ID: tenant-123                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              TenantMiddleware                                │
│  - Extract tenant ID from header                            │
│  - Validate tenant exists                                   │
│  - Set request.tenant = Tenant(id=123)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  View Processing                             │
│  - Access request.tenant                                    │
│  - All queries filtered by tenant                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Database Query                                  │
│  SELECT * FROM suppliers                                    │
│  WHERE tenant_id = 123                                      │
│  AND is_active = true                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               Response (Tenant Data Only)                    │
│  [ { id: 1, name: "Supplier A", tenant_id: 123 } ]         │
└─────────────────────────────────────────────────────────────┘
```

---

## Security & Authentication

### 1. Authentication Mechanism

**Token-Based Authentication**:
- Django REST Framework Token Authentication
- Token stored in browser localStorage
- Token sent in Authorization header
- Token validated on every request

### 2. CORS Configuration

```python
# settings/base.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:3000",
]

# Production
CORS_ALLOWED_ORIGINS = [
    "https://app.projectmeats.com",
]
```

### 3. CSRF Protection

- Enabled for all state-changing operations
- Exempted for API endpoints (token auth used instead)
- Double-submit cookie pattern

### 4. Data Isolation

**Multi-Tenant Security**:
- All queries automatically filtered by tenant
- Row-level security via tenant foreign key
- Middleware ensures tenant context
- No cross-tenant data access possible

---

## Error Handling

### Backend Error Responses

| Status Code | Meaning | Example Response |
|-------------|---------|------------------|
| 400 Bad Request | Validation error | `{"field": ["Error message"]}` |
| 401 Unauthorized | Authentication required | `{"detail": "Authentication credentials were not provided."}` |
| 403 Forbidden | Permission denied | `{"detail": "You do not have permission to perform this action."}` |
| 404 Not Found | Resource not found | `{"detail": "Not found."}` |
| 500 Server Error | Internal server error | `{"detail": "Internal server error"}` |

### Frontend Error Handling Strategy

```typescript
// apiService.ts response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth state and redirect to login
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

---

## Performance Considerations

### 1. API Response Optimization

- **Pagination**: Limit response size to 25 items per page
- **Field Selection**: Future enhancement to allow field filtering
- **Caching**: Browser caching via Cache-Control headers
- **Compression**: gzip compression enabled in production

### 2. Database Query Optimization

- **Select Related**: Use `select_related()` for foreign keys
- **Prefetch Related**: Use `prefetch_related()` for many-to-many
- **Database Indexes**: Indexes on frequently queried fields
- **Query Monitoring**: Django Debug Toolbar in development

### 3. Frontend Performance

- **Code Splitting**: Lazy loading of routes
- **Memoization**: React.memo for expensive components
- **Debouncing**: Search input debouncing
- **Virtual Scrolling**: For large data lists (future)

---

## Future Enhancements

### Planned Integration Improvements

1. **WebSocket Support**
   - Real-time updates for collaborative features
   - Live notifications
   - Chat presence indicators

2. **GraphQL API**
   - Alternative to REST for complex queries
   - Reduce over-fetching
   - Better frontend flexibility

3. **OpenAI Integration**
   - Replace mock AI responses with real GPT-4 calls
   - Document processing with GPT-4 Vision
   - Entity extraction from uploaded documents

4. **Background Tasks**
   - Celery for asynchronous processing
   - Email notifications
   - Report generation
   - Data imports/exports

5. **Event-Driven Architecture**
   - Message queue (RabbitMQ/Redis)
   - Event bus for cross-service communication
   - Webhook support for external integrations

6. **API Rate Limiting**
   - Throttling to prevent abuse
   - Per-user/per-tenant rate limits
   - Graceful degradation

7. **Caching Layer**
   - Redis for session storage
   - Cache frequently accessed data
   - Cache invalidation strategy

8. **File Storage**
   - AWS S3 integration
   - CDN for static assets
   - Document versioning

9. **Email Service**
   - SendGrid or AWS SES integration
   - Transactional emails
   - Email templates

10. **Monitoring & Logging**
    - Sentry for error tracking
    - Application Performance Monitoring (APM)
    - Structured logging
    - Metrics dashboard

---

## Related Documentation

- **[Backend Architecture](BACKEND_ARCHITECTURE.md)** - Detailed backend structure and patterns
- **[Frontend Architecture](FRONTEND_ARCHITECTURE.md)** - Frontend architecture and components
- **[Multi-Tenancy Guide](MULTI_TENANCY_GUIDE.md)** - Multi-tenancy implementation details
- **[Authentication Guide](AUTHENTICATION_GUIDE.md)** - Authentication and authorization
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Deployment and infrastructure
- **[Testing Strategy](TESTING_STRATEGY.md)** - Testing approaches and patterns
- **[Environment Guide](ENVIRONMENT_GUIDE.md)** - Environment configuration

---

**Questions or Issues?** See [Troubleshooting Guide](TROUBLESHOOTING.md) or create an issue.

**Last Updated**: December 1, 2024
