# Backend Development Instructions

## applyTo
- backend/**/*.py
- backend/**/models.py
- backend/**/views.py
- backend/**/serializers.py

## Django Multi-Tenancy Patterns

### CRITICAL: Shared-Schema Multi-Tenancy ONLY
**ProjectMeats uses SHARED SCHEMA multi-tenancy. NEVER use django-tenants patterns.**

- ❌ **NEVER** use `django-tenants` mixins (`TenantMixin`, `DomainMixin`)
- ❌ **NEVER** use `schema_context()` or `connection.schema_name`
- ❌ **NEVER** use `migrate_schemas` commands
- ❌ **NEVER** suggest separate public/tenant schemas
- ✅ **ALWAYS** use `tenant` ForeignKey on business models
- ✅ **ALWAYS** filter querysets with `tenant=request.tenant`
- ✅ **ALWAYS** use standard `python manage.py migrate`

### Migration Commands
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations (standard Django)
python manage.py migrate

# Check for unapplied migrations (CI gating)
python manage.py makemigrations --check

# Show migration status
python manage.py showmigrations
```

### Idempotent Migrations (Production)
```bash
# Use --fake-initial for production deployments
python manage.py migrate --fake-initial --noinput
```

## API Development

### Django REST Framework
- Use `ModelViewSet` for CRUD operations
- Override `get_queryset()` to filter by `tenant=request.tenant`
- Use `serializers.ModelSerializer` with explicit fields
- Add `permission_classes` to all views
- Override `perform_create()` to set tenant automatically

### Response Patterns
```python
# Success
return Response(data, status=status.HTTP_200_OK)

# Created
return Response(data, status=status.HTTP_201_CREATED)

# Error
return Response({"error": "message"}, status=status.HTTP_400_BAD_REQUEST)
```

## Testing

### Run Tests
```bash
# All tests
python manage.py test apps/ --verbosity=2

# Specific app
python manage.py test apps.accounts --verbosity=2

# With coverage
coverage run --source='apps' manage.py test apps/
coverage report
```

### Test Patterns
- Use `APITestCase` for API endpoints
- Use `TestCase` for model and business logic tests
- Create fixtures with `factory_boy`
- Test tenant isolation by filtering with `tenant=request.tenant`
- Ensure non-superusers can only see their tenant's data

## Code Quality

### Style Guidelines
- Follow PEP 8
- Max line length: 120 characters
- Use type hints for function parameters
- Docstrings for all public functions

### Linting
```bash
flake8 . --exclude=migrations --max-line-length=120
black --check . --exclude=migrations
```

## Security

### Always Validate
- Use Django forms/serializers for validation
- Never trust user input
- Use `@permission_classes([IsAuthenticated])`
- Filter querysets by tenant

### Environment Variables
- Never hardcode secrets
- Use `os.environ.get()` or django-environ
- Required vars: DATABASE_URL, SECRET_KEY, DJANGO_SETTINGS_MODULE

## Database

### Query Optimization
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for many-to-many
- Add `db_index=True` to frequently queried fields
- Use `only()` or `defer()` to limit fields

### Transactions
```python
from django.db import transaction

with transaction.atomic():
    # Your code here
```

## Common Patterns

### Tenant-Aware ViewSets
```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class MyViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # ALWAYS filter by tenant
        return super().get_queryset().filter(tenant=self.request.tenant)
    
    def perform_create(self, serializer):
        # ALWAYS set tenant on creation
        serializer.save(tenant=self.request.tenant)
```

### Custom Permissions
```python
from rest_framework import permissions

class IsTenantAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_tenant_admin
```

### Model with Tenant Isolation
```python
from django.db import models

class MyModel(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'name']),
        ]
```
