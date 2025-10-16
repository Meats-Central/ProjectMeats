# Multi-Tenancy Guide for ProjectMeats

## Overview

ProjectMeats implements a **shared database, shared schema** multi-tenancy architecture. This approach provides data isolation between tenants while maintaining operational efficiency through a single database instance.

## Architecture

### Tenant Model

The `Tenant` model (located in `backend/apps/tenants/models.py`) serves as the foundation for multi-tenancy:

```python
class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    contact_email = models.EmailField()
    is_active = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    settings = models.JSONField(default=dict)
```

### Tenant-User Association

Users can belong to multiple tenants with different roles through the `TenantUser` model:

```python
class TenantUser(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Administrator"),
        ("manager", "Manager"),
        ("user", "User"),
        ("readonly", "Read Only"),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")
    is_active = models.BooleanField(default=True)
```

### Data Isolation

All business entity models include a `tenant` ForeignKey field:

- **Suppliers** (`apps.suppliers.models.Supplier`)
- **Customers** (`apps.customers.models.Customer`)
- **Purchase Orders** (`apps.purchase_orders.models.PurchaseOrder`)
- **Plants** (`apps.plants.models.Plant`)
- **Contacts** (`apps.contacts.models.Contact`)
- **Carriers** (`apps.carriers.models.Carrier`)
- **Accounts Receivable** (`apps.accounts_receivables.models.AccountsReceivable`)

## Automated Setup

### Management Command: `create_super_tenant`

The `create_super_tenant` management command automates the creation of:
1. A superuser account
2. A default "root" tenant
3. The association between the superuser and root tenant

#### Usage

```bash
# Run manually
python manage.py create_super_tenant

# Run during deployment (automatically called in CI/CD)
```

#### Configuration

The command uses environment variables for credentials:

- `SUPERUSER_EMAIL`: Email address for the superuser (default: `admin@meatscentral.com`)
- `SUPERUSER_PASSWORD`: Password for the superuser (default: `default_secure_pass`)

⚠️ **Security Note**: Always override default credentials in production environments!

#### Environment Variables

##### Development (`config/environments/development.env`)
```bash
SUPERUSER_EMAIL=admin@meatscentral.com
SUPERUSER_PASSWORD=DevAdmin123!SecurePass
```

##### Staging (`config/environments/staging.env`)
```bash
SUPERUSER_EMAIL=${STAGING_SUPERUSER_EMAIL}
SUPERUSER_PASSWORD=${STAGING_SUPERUSER_PASSWORD}
```

##### Production (`config/environments/production.env`)
```bash
SUPERUSER_EMAIL=${PRODUCTION_SUPERUSER_EMAIL}
SUPERUSER_PASSWORD=${PRODUCTION_SUPERUSER_PASSWORD}
```

**Important**: Use secure secret management for staging and production:
- Use GitHub Secrets for CI/CD pipelines
- Use environment-specific secret managers (AWS Secrets Manager, Azure Key Vault, etc.)
- Never commit actual passwords to version control

### Idempotency

The `create_super_tenant` command is idempotent:
- ✅ Safe to run multiple times
- ✅ Won't create duplicates
- ✅ Won't overwrite existing data
- ✅ Will link existing users to tenants if needed

### Deployment Integration

The command is automatically executed during deployment in the unified workflow:

```yaml
- Run database migrations
- Create superuser and root tenant  # ← Automated
- Collect static files
- Run Django checks
```

This happens in all environments:
- Development
- Staging (UAT)
- Production

### Security Best Practices

#### Password Requirements

1. **Development**: Use strong passwords even in dev
2. **Staging**: Use randomly generated passwords stored in GitHub Secrets
3. **Production**: Use cryptographically secure passwords with:
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, and symbols
   - Stored in secure secret management system

#### Secret Generation

```bash
# Generate secure password (example)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use Django's secret key generator
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Environment Setup

For staging and production, set these as GitHub Secrets or in your environment:

```bash
# Staging
STAGING_SUPERUSER_EMAIL=admin@staging.meatscentral.com
STAGING_SUPERUSER_PASSWORD=<secure-random-password>

# Production
PRODUCTION_SUPERUSER_EMAIL=admin@meatscentral.com
PRODUCTION_SUPERUSER_PASSWORD=<secure-random-password>
```

## Middleware

### TenantMiddleware

The `TenantMiddleware` (in `backend/apps/tenants/middleware.py`) automatically sets the current tenant context for each request. It determines the tenant from:

1. **X-Tenant-ID header** (for API requests)
2. **Subdomain** (if configured)
3. **User's default tenant** (from TenantUser association)

The middleware adds two attributes to the request object:
- `request.tenant` - The current Tenant instance (or None)
- `request.tenant_user` - The TenantUser association (or None)

### Configuration

The middleware is enabled in `settings.py`:

```python
MIDDLEWARE = [
    ...
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.tenants.middleware.TenantMiddleware",  # Must come after authentication
    ...
]
```

## Queryset Filtering

### TenantManager

All tenant-aware models use the `TenantManager` which provides the `for_tenant()` method:

```python
from apps.core.models import TenantManager

class Supplier(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    # ... other fields ...
    
    objects = TenantManager()
```

### Usage in Views

To filter data by tenant in your views:

```python
# Get all suppliers for the current tenant
suppliers = Supplier.objects.for_tenant(request.tenant)

# Get a specific supplier (will return None if not in current tenant)
supplier = Supplier.objects.for_tenant(request.tenant).filter(id=supplier_id).first()
```

## API Integration

### Setting Tenant Context

When making API requests, include the tenant ID in the `X-Tenant-ID` header:

```javascript
fetch('/api/v1/suppliers/', {
    headers: {
        'Authorization': 'Token abc123...',
        'X-Tenant-ID': 'uuid-of-tenant',
    }
})
```

### Getting User's Tenants

Use the `/api/v1/api/tenants/my_tenants/` endpoint to get all tenants for the current user:

```javascript
const response = await fetch('/api/v1/api/tenants/my_tenants/', {
    headers: { 'Authorization': 'Token abc123...' }
});
const tenants = await response.json();
```

## Creating Multi-Tenant Data

### Backend (Django)

When creating new entities, always set the tenant:

```python
def create_supplier(request):
    supplier = Supplier.objects.create(
        tenant=request.tenant,
        name="New Supplier",
        email="supplier@example.com",
    )
    return supplier
```

### Frontend (React/React Native)

Ensure the tenant context is set before making API calls:

```typescript
// In your API service
const createSupplier = async (supplierData: SupplierData, tenantId: string) => {
    const response = await fetch('/api/v1/suppliers/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Tenant-ID': tenantId,
        },
        body: JSON.stringify(supplierData),
    });
    return response.json();
};
```

## Testing

### Running Tenant Isolation Tests

```bash
cd backend
python manage.py test apps.tenants.test_isolation
```

### Writing Tests

When writing tests, always create test tenants and verify data isolation:

```python
def test_my_feature(self):
    # Create tenants
    tenant1 = Tenant.objects.create(name="Tenant 1", slug="tenant-1")
    tenant2 = Tenant.objects.create(name="Tenant 2", slug="tenant-2")
    
    # Create data for each tenant
    supplier1 = Supplier.objects.create(tenant=tenant1, name="Supplier 1")
    supplier2 = Supplier.objects.create(tenant=tenant2, name="Supplier 2")
    
    # Verify isolation
    assert Supplier.objects.for_tenant(tenant1).count() == 1
    assert Supplier.objects.for_tenant(tenant2).count() == 1
```

## Best Practices

### 1. Always Filter by Tenant

When querying data, always use the `for_tenant()` method:

```python
# Good
suppliers = Supplier.objects.for_tenant(request.tenant)

# Bad - exposes data from all tenants
suppliers = Supplier.objects.all()
```

### 2. Validate Tenant Access

Before allowing operations, verify the user has access to the tenant:

```python
def update_supplier(request, supplier_id):
    # Get supplier filtered by tenant
    supplier = Supplier.objects.for_tenant(request.tenant).filter(id=supplier_id).first()
    
    if not supplier:
        return HttpResponseNotFound()
    
    # Update supplier
    supplier.name = request.POST['name']
    supplier.save()
```

### 3. Set Tenant on Create

Always set the tenant when creating new entities:

```python
def create_customer(request):
    customer = Customer.objects.create(
        tenant=request.tenant,  # Always set tenant
        name=request.POST['name'],
        email=request.POST['email'],
    )
```

### 4. Handle Missing Tenant

Some requests may not have a tenant (e.g., public endpoints). Handle this gracefully:

```python
def my_view(request):
    if not request.tenant:
        return HttpResponseForbidden("Tenant required")
    
    # Proceed with tenant-scoped operations
    suppliers = Supplier.objects.for_tenant(request.tenant)
```

## Admin Configuration

### Superuser Access

Superusers can view and manage all tenants. Regular admins can only manage their own tenant's data.

### Creating Tenants

Tenants can be created through:

1. **Django Admin** - Navigate to `/admin/tenants/tenant/`
2. **API** - POST to `/api/v1/api/tenants/`
3. **Management Command** - Create a custom management command if needed

Example API request:

```bash
curl -X POST http://localhost:8000/api/v1/api/tenants/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token abc123..." \
  -d '{
    "name": "New Company",
    "slug": "new-company",
    "contact_email": "admin@newcompany.com",
    "is_trial": true
  }'
```

## Migration Considerations

### Existing Data

The tenant field on all models is currently nullable to accommodate existing data. Consider:

1. **Data Migration** - Create a script to assign existing data to a default tenant
2. **Make Required** - After migration, make tenant field required (remove `null=True, blank=True`)

Example migration script:

```python
# Create a management command: backend/apps/core/management/commands/assign_default_tenant.py
from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant
from apps.suppliers.models import Supplier
from apps.customers.models import Customer
# ... import other models

class Command(BaseCommand):
    help = 'Assign all existing data to a default tenant'

    def handle(self, *args, **options):
        # Get or create default tenant
        tenant, _ = Tenant.objects.get_or_create(
            slug='default',
            defaults={
                'name': 'Default Company',
                'contact_email': 'admin@example.com',
            }
        )
        
        # Assign to all entities
        Supplier.objects.filter(tenant__isnull=True).update(tenant=tenant)
        Customer.objects.filter(tenant__isnull=True).update(tenant=tenant)
        # ... update other models
        
        self.stdout.write(self.style.SUCCESS(f'Assigned all data to tenant: {tenant.name}'))
```

## Troubleshooting

### Management Command Issues

#### Command Not Found

If `create_super_tenant` command is not found:

```bash
# Verify the command exists
python manage.py help | grep create_super_tenant

# Check directory structure
ls -la apps/core/management/commands/
```

#### Superuser Already Exists

The command will display a warning but continue:
```
⚠️  Superuser already exists: admin@meatscentral.com
```

This is expected behavior and not an error.

#### Permission Denied

Ensure the user running the command has:
- Database write permissions
- Proper Django settings configured
- Virtual environment activated

#### Database Not Migrated

Run migrations before the command:
```bash
python manage.py migrate
python manage.py create_super_tenant
```

### No Tenant in Request

If `request.tenant` is None:

1. Verify middleware is enabled in settings
2. Check that user is authenticated
3. Verify user has a TenantUser association
4. Check that X-Tenant-ID header is being sent (for API requests)

### Cross-Tenant Data Visibility

If data from other tenants is visible:

1. Ensure you're using `for_tenant()` method
2. Check that the tenant field is set on all entities
3. Verify middleware is setting `request.tenant` correctly

### Permission Denied

If users can't access their tenant's data:

1. Verify TenantUser association exists and is active
2. Check user's role in TenantUser
3. Ensure tenant is active (`is_active=True`)

## Future Enhancements

### Planned Features

1. **Tenant-specific settings** - Use the `settings` JSONField for customization
2. **Tenant branding** - Theme colors, logos, etc.
3. **Usage tracking** - Monitor resource usage per tenant
4. **Billing integration** - Track usage for billing purposes
5. **Data export** - Allow tenants to export their data

### Schema per Tenant (Alternative)

For larger deployments, consider migrating to a schema-per-tenant approach using Django tenant schemas. This provides stronger data isolation but increases complexity.

## References

- Tenant Model: `backend/apps/tenants/models.py`
- Tenant Middleware: `backend/apps/tenants/middleware.py`
- Tenant Manager: `backend/apps/core/models.py` (TenantManager)
- Isolation Tests: `backend/apps/tenants/test_isolation.py`
- API Views: `backend/apps/tenants/views.py`

## Support

For questions or issues with multi-tenancy:

1. Check this documentation
2. Review the test cases in `test_isolation.py`
3. Consult the Django multi-tenancy documentation
4. Contact the development team
