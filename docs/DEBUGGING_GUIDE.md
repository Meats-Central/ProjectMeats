# Debugging Guide for AI Agents

**Last Updated**: December 1, 2024  
**Purpose**: Systematic approach to diagnosing and fixing common issues

---

## 🎯 General Debugging Strategy

### The Debugging Process
```
1. REPRODUCE → 2. ISOLATE → 3. IDENTIFY → 4. FIX → 5. VERIFY → 6. PREVENT
```

1. **REPRODUCE**: Can you consistently trigger the issue?
2. **ISOLATE**: Where exactly is the problem? (Backend/Frontend/Database/Network)
3. **IDENTIFY**: What is the root cause?
4. **FIX**: Implement the solution
5. **VERIFY**: Test that it's actually fixed
6. **PREVENT**: Add tests to prevent regression

---

## 🔍 Quick Diagnostic Commands

### Health Check Commands
```bash
# Backend health
curl http://localhost:8000/health/

# Check Django settings
cd backend
python manage.py check

# Check migrations status
python manage.py showmigrations

# Check database connection
python manage.py dbshell

# Frontend build check
cd frontend
npm run type-check
```

### Log Locations
```bash
# Django logs (if configured)
tail -f logs/django.log

# Frontend console
# Open browser DevTools (F12) → Console tab

# PostgreSQL logs
# macOS: /usr/local/var/log/postgresql/
# Linux: /var/log/postgresql/
tail -f /var/log/postgresql/postgresql-*.log

# Gunicorn logs (production)
tail -f /var/log/gunicorn/error.log
```

---

## 🚨 Common Issues & Solutions

### Issue Categories
1. [Backend Issues](#backend-issues)
2. [Frontend Issues](#frontend-issues)
3. [Database Issues](#database-issues)
4. [Multi-tenancy Issues](#multi-tenancy-issues)
5. [Authentication Issues](#authentication-issues)
6. [Deployment Issues](#deployment-issues)
7. [Performance Issues](#performance-issues)

---

## 🔧 Backend Issues

### Error: "Module not found" or Import Errors

**Symptoms:**
```
ImportError: No module named 'apps.suppliers'
ModuleNotFoundError: No module named 'rest_framework'
```

**Diagnosis:**
```bash
# Check if requirements are installed
cd backend
pip list | grep django

# Check Python path
python manage.py shell
>>> import sys
>>> print('\n'.join(sys.path))
```

**Solution:**
```bash
# Reinstall requirements
pip install -r requirements.txt

# If still failing, clear cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -delete

# Verify installation
python -c "import django; print(django.VERSION)"
```

---

### Error: "django.core.exceptions.ImproperlyConfigured"

**Symptoms:**
```
ImproperlyConfigured: Set the SECRET_KEY environment variable
ImproperlyConfigured: The SECRET_KEY setting must not be empty
```

**Diagnosis:**
```bash
# Check environment variables
cd backend
python manage.py shell
>>> from django.conf import settings
>>> print(f"SECRET_KEY set: {bool(settings.SECRET_KEY)}")
>>> print(f"DEBUG: {settings.DEBUG}")
```

**Solution:**
```bash
# Set up environment
python config/manage_env.py setup development

# Or manually
cd backend
cp .env.example .env
# Edit .env and set required variables

# Verify
python manage.py check
```

---

### Error: "CSRF verification failed"

**Symptoms:**
```
403 Forbidden
CSRF verification failed. Request aborted.
```

**Diagnosis:**
```python
# In views.py
from django.views.decorators.csrf import csrf_exempt

# Check if frontend is sending CSRF token
# In browser DevTools → Network → Headers
# Look for: X-CSRFToken header
```

**Solution:**
```python
# Option 1: Ensure CSRF token is sent from frontend
// frontend/src/services/api.ts
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

# Option 2: Exempt specific endpoint (dev only)
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

@csrf_exempt
@api_view(['POST'])
def my_view(request):
    pass

# Option 3: Use DRF's SessionAuthentication properly
# In settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}
```

---

### Error: "OperationalError: FATAL: database does not exist"

**Symptoms:**
```
django.db.utils.OperationalError: FATAL: database "projectmeats_dev" does not exist
```

**Diagnosis:**
```bash
# Check if database exists
psql -l | grep projectmeats

# Check database settings
cd backend
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES['default'])
```

**Solution:**
```bash
# Create database
createdb projectmeats_dev

# Or with psql
psql postgres
postgres=# CREATE DATABASE projectmeats_dev;
postgres=# \q

# Apply migrations
cd backend
python manage.py migrate_schemas
```

---

### Error: "Migration conflicts"

**Symptoms:**
```
CommandError: Conflicting migrations detected; multiple leaf nodes in the migration graph
```

**Diagnosis:**
```bash
cd backend
python manage.py showmigrations
# Look for branches in migration tree
```

**Solution:**
```bash
# Option 1: Squash migrations (careful!)
python manage.py squashmigrations app_name start_migration end_migration

# Option 2: Merge migrations
python manage.py makemigrations --merge

# Option 3: Reset migrations (DEVELOPMENT ONLY - DESTROYS DATA)
# Delete migration files
rm apps/*/migrations/0*.py
# Recreate
python manage.py makemigrations
python manage.py migrate_schemas
```

---

### Error: "Circular dependency in migrations"

**Symptoms:**
```
django.db.migrations.exceptions.CircularDependencyError
```

**Diagnosis:**
```bash
# Check migration dependencies
cd backend
grep -r "dependencies =" apps/*/migrations/*.py
```

**Solution:**
```python
# Fix migration dependencies
# In problematic migration file
class Migration(migrations.Migration):
    dependencies = [
        ('app1', '0002_previous'),  # Remove circular reference
        # ('app2', '0003_causes_cycle'),  # Comment out
    ]
```

---

## 🖥️ Frontend Issues

### Error: "npm ERR! code ELIFECYCLE"

**Symptoms:**
```
npm ERR! code ELIFECYCLE
npm ERR! errno 1
```

**Diagnosis:**
```bash
cd frontend
npm run type-check
npm run lint
```

**Solution:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# If still failing, check Node version
node --version  # Should be 16+
```

---

### Error: "Module not found: Can't resolve..."

**Symptoms:**
```
Module not found: Can't resolve './Component'
Module not found: Error: Can't resolve 'axios'
```

**Diagnosis:**
```bash
# Check if file exists
ls -la src/components/Component.tsx

# Check if package is installed
npm list axios
```

**Solution:**
```bash
# Install missing package
npm install axios

# Fix import path (case-sensitive on Linux!)
// WRONG
import { Component } from './component';

// CORRECT
import { Component } from './Component';

# Clear webpack cache
rm -rf node_modules/.cache
npm start
```

---

### Error: TypeScript Type Errors

**Symptoms:**
```
Type 'string' is not assignable to type 'number'
Property 'name' does not exist on type '{}'
```

**Diagnosis:**
```bash
cd frontend
npm run type-check
```

**Solution:**
```typescript
// Add proper type annotations

// WRONG
const data = {}; // Type: {}
data.name = 'test'; // Error!

// CORRECT
interface Data {
  name: string;
}
const data: Data = { name: 'test' };

// Or use type assertion (use sparingly)
const data = {} as Data;
data.name = 'test'; // OK
```

---

### Error: "CORS policy" errors

**Symptoms:**
```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Diagnosis:**
```bash
# Check backend CORS settings
cd backend
python manage.py shell
>>> from django.conf import settings
>>> print(settings.CORS_ALLOWED_ORIGINS)
```

**Solution:**
```python
# In backend/projectmeats/settings/development.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Restart backend
# CTRL+C then python manage.py runserver
```

---

### Error: "Cannot read property 'X' of undefined"

**Symptoms:**
```javascript
TypeError: Cannot read property 'name' of undefined
TypeError: Cannot read property 'map' of undefined
```

**Diagnosis:**
```typescript
// Add console.log to check data
console.log('Data:', data);
console.log('Type:', typeof data);
```

**Solution:**
```typescript
// Use optional chaining and nullish coalescing

// WRONG
const name = user.profile.name; // Error if user or profile is undefined

// CORRECT
const name = user?.profile?.name ?? 'Unknown';

// For arrays
const items = data?.items ?? [];
items.map(item => ...); // Safe even if data is undefined
```

---

## 💾 Database Issues

### Issue: "Too many connections"

**Symptoms:**
```
OperationalError: FATAL: sorry, too many clients already
```

**Diagnosis:**
```bash
# Check active connections
psql projectmeats_dev
SELECT count(*) FROM pg_stat_activity;

# Check max connections
SHOW max_connections;
```

**Solution:**
```python
# In settings.py, add connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'CONN_MAX_AGE': 60,  # Reuse connections for 60 seconds
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Or close idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'projectmeats_dev' 
  AND state = 'idle';
```

---

### Issue: Slow Queries

**Symptoms:**
- API responses take >1 second
- Database CPU usage high

**Diagnosis:**
```python
# Enable query logging
from django.db import connection
from django.conf import settings

settings.DEBUG = True
# ... run your code ...
for query in connection.queries:
    print(f"{query['time']}s: {query['sql']}")
```

**Solution:**
```python
# Fix N+1 queries with select_related/prefetch_related

# WRONG (N+1 query problem)
suppliers = Supplier.objects.all()
for supplier in suppliers:
    print(supplier.contact.name)  # Hits DB for each supplier!

# CORRECT
suppliers = Supplier.objects.select_related('contact').all()
for supplier in suppliers:
    print(supplier.contact.name)  # Single query!

# For reverse relationships, use prefetch_related
suppliers = Supplier.objects.prefetch_related('purchase_orders').all()
for supplier in suppliers:
    print(supplier.purchase_orders.count())  # Efficient!
```

---

### Issue: "Index not being used"

**Diagnosis:**
```sql
-- Explain query plan
EXPLAIN ANALYZE
SELECT * FROM suppliers_supplier WHERE code = 'SUP001';
```

**Solution:**
```python
# Add database index
class Supplier(models.Model):
    code = models.CharField(max_length=50, db_index=True)  # Add index
    name = models.CharField(max_length=255)

# Or add composite index
class Meta:
    indexes = [
        models.Index(fields=['code', 'is_active']),
    ]

# Create migration
python manage.py makemigrations
python manage.py migrate_schemas
```

---

## 🏢 Multi-tenancy Issues

### Issue: "Relation does not exist"

**Symptoms:**
```
relation "suppliers_supplier" does not exist
ProgrammingError: relation "public.suppliers_supplier" does not exist
```

**Diagnosis:**
```bash
# Check tenant schemas
cd backend
python manage.py shell

>>> from apps.tenants.models import Client
>>> clients = Client.objects.all()
>>> for client in clients:
...     print(f"{client.schema_name}: {client.name}")

# Check which schema you're in
>>> from django.db import connection
>>> print(connection.schema_name)
```

**Solution:**
```bash
# Migrate tenant apps
cd backend
python manage.py migrate_schemas

# Migrate specific tenant
python manage.py migrate_schemas --schema=tenant_name

# Migrate shared apps
python manage.py migrate_schemas --shared
```

---

### Issue: "Tenant not found"

**Symptoms:**
```
TenantNotFound: No tenant found for hostname 'localhost'
```

**Diagnosis:**
```bash
cd backend
python manage.py shell

>>> from apps.tenants.models import Client, Domain
>>> domains = Domain.objects.all()
>>> for domain in domains:
...     print(f"{domain.domain} → {domain.tenant.schema_name}")
```

**Solution:**
```bash
# Create tenant for localhost
cd backend
python manage.py shell

>>> from apps.tenants.models import Client, Domain
>>> client = Client.objects.create(
...     schema_name='public',
...     name='Default Tenant'
... )
>>> Domain.objects.create(
...     domain='localhost',
...     tenant=client,
...     is_primary=True
... )
```

---

### Issue: Data Leaking Between Tenants

**Symptoms:**
- User in tenant A can see tenant B's data
- Wrong tenant context

**Diagnosis:**
```python
# Check tenant middleware order
# In settings.py
MIDDLEWARE = [
    "django_tenants.middleware.TenantMainMiddleware",  # MUST BE FIRST!
    # ... other middleware
]

# Check query filtering
from django.db import connection
print(f"Current schema: {connection.schema_name}")
```

**Solution:**
```python
# Ensure models are in TENANT_APPS not SHARED_APPS
# In settings/base.py
TENANT_APPS = [
    'apps.suppliers',  # Tenant-specific data
    'apps.customers',
    # ...
]

SHARED_APPS = [
    'apps.core',      # Shared utilities
    'apps.tenants',   # Tenant management
]

# Add tenant filtering in views
class SupplierViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Automatically filtered by schema
        return Supplier.objects.all()
```

---

## 🔐 Authentication Issues

### Issue: "Invalid token" or "Token expired"

**Symptoms:**
```
401 Unauthorized
{"detail": "Invalid token."}
```

**Diagnosis:**
```typescript
// Check if token is being sent
// In frontend/src/services/api.ts
api.interceptors.request.use(config => {
    console.log('Auth Header:', config.headers.Authorization);
    return config;
});
```

**Solution:**
```typescript
// Ensure token is stored and sent correctly
// frontend/src/services/api.ts
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
});

// Add auth interceptor
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('authToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            // Token expired, redirect to login
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);
```

---

### Issue: Permissions Denied

**Symptoms:**
```
403 Forbidden
{"detail": "You do not have permission to perform this action."}
```

**Diagnosis:**
```python
# Check user permissions
cd backend
python manage.py shell

>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='testuser')
>>> print(f"Is staff: {user.is_staff}")
>>> print(f"Is superuser: {user.is_superuser}")
>>> print(f"Permissions: {list(user.user_permissions.all())}")
```

**Solution:**
```python
# Fix permission classes
# In views.py
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class SupplierViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]  # Allow authenticated users
    # Or
    permission_classes = [IsAdminUser]  # Only admins

# Custom permission
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class MyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
```

---

## 🚀 Deployment Issues

### Issue: "502 Bad Gateway" in Production

**Symptoms:**
- Site returns 502 error
- Nginx error: "upstream prematurely closed connection"

**Diagnosis:**
```bash
# Check if Gunicorn is running
sudo systemctl status gunicorn

# Check Gunicorn logs
sudo tail -f /var/log/gunicorn/error.log

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Test backend directly
curl http://localhost:8000/health/
```

**Solution:**
```bash
# Restart Gunicorn
sudo systemctl restart gunicorn

# Check Gunicorn config
cat /etc/systemd/system/gunicorn.service

# Ensure correct Python environment
which python
pip list | grep django

# Check socket file
ls -la /run/gunicorn.sock
```

---

### Issue: Static Files Not Loading

**Symptoms:**
- CSS/JS not loading in production
- 404 on /static/ URLs

**Diagnosis:**
```bash
# Check static files collected
ls -la /app/staticfiles/

# Check Nginx config
sudo cat /etc/nginx/sites-available/projectmeats
```

**Solution:**
```bash
# Collect static files
cd /app/backend
python manage.py collectstatic --noinput

# Check settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.STATIC_ROOT)
>>> print(settings.STATIC_URL)

# Restart Nginx
sudo systemctl restart nginx
```

---

### Issue: Environment Variables Not Set

**Symptoms:**
```
KeyError: 'SECRET_KEY'
ImproperlyConfigured
```

**Diagnosis:**
```bash
# Check environment file
cat .env

# Check if variables are loaded
python manage.py shell
>>> import os
>>> print(os.getenv('SECRET_KEY'))
```

**Solution:**
```bash
# Set environment variables
# In .env file
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/db

# Or export directly
export SECRET_KEY="your-secret-key"

# For systemd service
sudo nano /etc/systemd/system/gunicorn.service

[Service]
EnvironmentFile=/app/.env
# Or
Environment="SECRET_KEY=value"

sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```

---

## ⚡ Performance Issues

### Issue: Slow API Response

**Diagnosis:**
```python
# Add timing middleware
# backend/apps/core/middleware.py
import time
import logging

logger = logging.getLogger(__name__)

class TimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = time.time() - start
        
        if duration > 1.0:  # Log slow requests
            logger.warning(
                f"Slow request: {request.method} {request.path} "
                f"took {duration:.2f}s"
            )
        
        return response

# Add to MIDDLEWARE in settings.py
```

**Solution:**
```python
# 1. Optimize queries (see "Slow Queries" above)

# 2. Add caching
from django.core.cache import cache

def expensive_operation():
    result = cache.get('my_cache_key')
    if result is None:
        result = do_expensive_calculation()
        cache.set('my_cache_key', result, timeout=300)  # 5 minutes
    return result

# 3. Use pagination
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class SupplierViewSet(viewsets.ModelViewSet):
    pagination_class = StandardPagination
```

---

### Issue: High Memory Usage

**Diagnosis:**
```python
# Profile memory usage
import tracemalloc

tracemalloc.start()
# ... run your code ...
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

**Solution:**
```python
# 1. Use iterator() for large querysets
# WRONG
suppliers = Supplier.objects.all()  # Loads all into memory
for supplier in suppliers:
    process(supplier)

# CORRECT
for supplier in Supplier.objects.all().iterator():
    process(supplier)  # Loads in chunks

# 2. Use values() or values_list() when you don't need full objects
suppliers = Supplier.objects.values('id', 'name')  # Only these fields

# 3. Clean up after processing
import gc
gc.collect()
```

---

## 🛠️ Debugging Tools

### Django Debug Toolbar (Development)
```python
# Install
pip install django-debug-toolbar

# Add to INSTALLED_APPS (development.py only)
INSTALLED_APPS += ['debug_toolbar']

# Add middleware
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Configure
INTERNAL_IPS = ['127.0.0.1']

# Add to urls.py
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
```

### React DevTools
```bash
# Install browser extension
# Chrome: https://chrome.google.com/webstore
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/react-devtools/

# Use in browser
# F12 → Components/Profiler tabs
```

### Database Query Analyzer
```python
# In Django shell
from django.db import connection, reset_queries
from django.conf import settings

settings.DEBUG = True
reset_queries()

# ... execute your code ...

print(f"Total queries: {len(connection.queries)}")
for query in connection.queries:
    print(f"{query['time']}s: {query['sql'][:100]}")
```

---

## 📚 Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **DRF Documentation**: https://www.django-rest-framework.org/
- **React Documentation**: https://react.dev/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **django-tenants Documentation**: https://django-tenants.readthedocs.io/

---

## 💡 Debugging Best Practices

1. **Start with logs** - Check console, server, and database logs first
2. **Reproduce consistently** - Can you make it happen every time?
3. **Isolate the problem** - Backend? Frontend? Database? Network?
4. **Use version control** - git bisect to find when bug was introduced
5. **Add tests** - Write a failing test that reproduces the bug
6. **Document the fix** - Help future you (or AI) understand why
7. **Prevent regression** - Keep the test that caught the bug

---

**Last Updated**: December 1, 2024  
**Maintained by**: ProjectMeats Team  
**Version**: 1.0.0
