# Tenant Apps

This directory contains Django apps that are **tenant-specific** (isolated by tenant_id).

## Architecture: Shared Schema Multi-Tenancy

ProjectMeats uses **shared schema multi-tenancy** with row-level isolation via `tenant_id` foreign keys. All tenants share the same PostgreSQL schema.

❌ **NEVER** use `django-tenants` or schema-based isolation  
✅ **ALWAYS** use `tenant` ForeignKey for isolation

## Development Rules

### CRITICAL: TenantManager Requirement

**All tenant-specific models MUST explicitly use `objects = TenantManager()`**

```python
from apps.core.managers import TenantManager

class Supplier(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    
    # ✅ REQUIRED: Explicit TenantManager
    objects = TenantManager()
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'name']),
        ]
```

**Why This Matters:**
- `TenantManager` automatically filters queries by `request.tenant`
- Prevents cross-tenant data leaks
- Enforces tenant isolation at the ORM level
- Missing this creates a security vulnerability

### Model Requirements Checklist

For every model in `tenant_apps/`:

- [ ] Has `tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)`
- [ ] Uses `objects = TenantManager()` explicitly
- [ ] Has composite index on `['tenant', primary_query_field]`
- [ ] ViewSet filters by `tenant=request.tenant` in `get_queryset()`
- [ ] ViewSet assigns `tenant=request.tenant` in `perform_create()`

### Examples

#### ✅ Correct Implementation
```python
from django.db import models
from apps.core.managers import TenantManager

class Customer(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    
    objects = TenantManager()  # ✅ REQUIRED
    
    class Meta:
        indexes = [
            models.Index(fields=['tenant', 'email']),
        ]
```

#### ❌ Wrong Implementation
```python
class Customer(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    
    # ❌ MISSING: TenantManager not specified
    # This creates a security vulnerability!
```

### ViewSet Requirements

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # ✅ ALWAYS filter by request.tenant
        return super().get_queryset().filter(tenant=self.request.tenant)
    
    def perform_create(self, serializer):
        # ✅ ALWAYS assign request.tenant
        serializer.save(tenant=self.request.tenant)
```

## Migration Strategy

### Standard Django Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations (standard Django, NOT migrate_schemas)
python manage.py migrate --fake-initial --noinput
```

❌ **NEVER** use `migrate_schemas` or `migrate --tenant`  
✅ **ALWAYS** use standard `python manage.py migrate`

### Why Not django-tenants?

- **Complexity**: Schema-per-tenant adds operational overhead
- **Performance**: Shared schema scales better for small-medium tenants
- **Simplicity**: Standard Django migrations, no schema switching
- **Flexibility**: Easier to query across tenants when needed

## Current Apps in tenant_apps/

| App | Purpose | Models |
|-----|---------|--------|
| `accounts_receivables` | Invoice tracking | AccountsReceivable |
| `ai_assistant` | AI chatbot | ChatSession, ChatMessage |
| `bug_reports` | User bug reports | BugReport |
| `carriers` | Shipping carriers | Carrier |
| `cockpit` | Dashboard widgets | CockpitSlot |
| `contacts` | Contact management | Contact |
| `customers` | Customer records | Customer |
| `invoices` | Invoice generation | Invoice, InvoiceItem |
| `plants` | Production facilities | Plant |
| `products` | Product catalog | Product |
| `purchase_orders` | Purchase orders | PurchaseOrder, PurchaseOrderItem |
| `sales_orders` | Sales orders | SalesOrder, SalesOrderItem |
| `suppliers` | Supplier management | Supplier |

## Testing Tenant Isolation

```python
# Test tenant isolation in shell
python manage.py shell

>>> from apps.tenants.models import Tenant
>>> from tenant_apps.customers.models import Customer

# Create two tenants
>>> tenant1 = Tenant.objects.create(name="Tenant 1", slug="tenant1", schema_name="tenant1")
>>> tenant2 = Tenant.objects.create(name="Tenant 2", slug="tenant2", schema_name="tenant2")

# Create customers for each tenant
>>> customer1 = Customer.objects.create(tenant=tenant1, name="Customer A")
>>> customer2 = Customer.objects.create(tenant=tenant2, name="Customer B")

# Verify isolation
>>> Customer.objects.filter(tenant=tenant1).count()
1
>>> Customer.objects.filter(tenant=tenant2).count()
1
```

## Security Considerations

1. **Always filter by tenant**: Use `TenantManager` to enforce this automatically
2. **Never expose tenant_id**: Don't include in API responses unless needed
3. **Validate tenant ownership**: Check `request.tenant` matches object tenant
4. **Test cross-tenant access**: Ensure users can't access other tenants' data

## Related Documentation

- [GOLDEN_PIPELINE.md](../../docs/GOLDEN_PIPELINE.md) - Deployment architecture
- [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) - System architecture
- [TENANT_ACCESS_CONTROL.md](../../docs/TENANT_ACCESS_CONTROL.md) - Access control patterns
