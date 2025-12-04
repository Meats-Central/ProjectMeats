# Backend Development Instructions

## applyTo
- backend/**/*.py
- backend/**/models.py
- backend/**/views.py
- backend/**/serializers.py

## Django Multi-Tenancy Patterns

### Always Use django-tenants
- Use `migrate_schemas --shared` for shared tables (public schema)
- Use `migrate_schemas --tenant` for tenant-specific tables
- Models must inherit from `TenantMixin` for tenant models
- Use `schema_context(tenant)` for cross-tenant operations

### Migration Commands
```bash
# Shared schema (tables in public schema)
python manage.py migrate_schemas --shared --fake-initial --noinput

# Tenant schemas (tables in each tenant's schema)
python manage.py migrate_schemas --tenant --noinput

# Create super tenant
python manage.py create_super_tenant --no-input
```

## API Development

### Django REST Framework
- Use `ModelViewSet` for CRUD operations
- Apply `TenantFilterMixin` for tenant isolation
- Use `serializers.ModelSerializer` with explicit fields
- Add `permission_classes` to all views

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
- Use `TransactionTestCase` for multi-tenancy tests
- Create fixtures with `factory_boy`
- Test both shared and tenant contexts

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

### Tenant-Aware Views
```python
from apps.tenants.mixins import TenantFilterMixin

class MyViewSet(TenantFilterMixin, viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MySerializer
```

### Custom Permissions
```python
from rest_framework import permissions

class IsTenantAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_tenant_admin
```
