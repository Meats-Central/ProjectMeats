# Dev Domain Mapping Fix

## Problem

API requests to `dev-backend.meatscentral.com` are failing with **403 Forbidden** errors.

### Root Cause

`TenantMiddleware` cannot resolve a tenant from the subdomain `dev-backend` because there's no domain mapping in the database.

**Tenant Resolution Flow:**
```
Request: dev-backend.meatscentral.com
  ↓
TenantMiddleware checks TenantDomain table
  ↓
No mapping found for "dev-backend.meatscentral.com"
  ↓
request.tenant = None
  ↓
Permission checks fail
  ↓
403 Forbidden
```

## Solution

Map the domain `dev-backend.meatscentral.com` to the existing `root` tenant.

## Usage

### Option 1: Run Inside Container (Recommended)

```bash
# SSH into the dev backend server
ssh user@dev-backend-server

# Run the fix script inside the container
docker exec pm-backend python /app/scripts/fix_dev_domain.py
```

### Option 2: Run via Django Shell

```bash
docker exec -it pm-backend python manage.py shell

# In Python shell:
from apps.tenants.models import Tenant, TenantDomain

root_tenant = Tenant.objects.get(slug='root')
TenantDomain.objects.update_or_create(
    domain='dev-backend.meatscentral.com',
    defaults={'tenant': root_tenant, 'is_primary': True}
)
```

### Option 3: Run via Management Command (Future)

```bash
docker exec pm-backend python manage.py map_domain dev-backend.meatscentral.com root
```

## Expected Output

```
============================================================
Fixing Dev Domain Mapping
============================================================

Step 1: Looking for root tenant...
✅ Found Root Tenant:
   ID: 1
   Name: Root Organization
   Slug: root

Step 2: Creating domain mapping...
✅ Created new domain mapping:
   Domain: dev-backend.meatscentral.com
   Tenant: Root Organization (slug: root)
   Primary: True

Step 3: Verifying mapping...
✅ Mapping verified successfully!

============================================================
Domain mapping complete!
============================================================

Next steps:
1. Restart the backend container
2. Try accessing dev-backend.meatscentral.com
3. 403 errors should be resolved

============================================================
Current Domain Mappings
============================================================
  dev-backend.meatscentral.com → Root Organization (slug: root, primary: True)
============================================================
```

## Verification

### Test API Access

```bash
# Should return 200 OK instead of 403
curl https://dev-backend.meatscentral.com/api/v1/health/

# Expected response:
{"status": "healthy"}
```

### Check Logs

```bash
docker logs pm-backend --tail 50

# Should see successful tenant resolution:
# [INFO] Tenant resolved: root (from domain: dev-backend.meatscentral.com)
```

## Troubleshooting

### Error: "Root tenant not found"

**Problem**: The root tenant doesn't exist in the database.

**Solution**:
```bash
docker exec pm-backend python manage.py create_super_tenant
```

### Error: "Django setup failed"

**Problem**: Script can't find Django settings.

**Solution**: Run from inside container where Django is properly configured.

### Error: Still getting 403 after fix

**Possible causes:**
1. Container not restarted after mapping
2. Wrong domain in request (check DNS)
3. Permission issue with user account

**Debug steps:**
```bash
# Check domain mappings
docker exec pm-backend python manage.py shell
>>> from apps.tenants.models import TenantDomain
>>> TenantDomain.objects.all().values('domain', 'tenant__slug')

# Check tenant middleware logs
docker logs pm-backend | grep -i tenant

# Restart container
docker restart pm-backend
```

## Alternative Domains

If you need to map additional domains:

```python
# In Django shell or modify script:
domains = [
    'dev-backend.meatscentral.com',
    'dev.meatscentral.com',
    'localhost:8000',  # For local development
]

for domain in domains:
    TenantDomain.objects.update_or_create(
        domain=domain,
        defaults={'tenant': root_tenant, 'is_primary': False}
    )
```

## Related Documentation

- **Multi-tenancy Architecture**: docs/GOLDEN_PIPELINE.md
- **TenantMiddleware Implementation**: apps/tenants/middleware.py
- **Tenant Models**: apps/tenants/models.py

## Technical Details

### TenantMiddleware Resolution Order

1. **X-Tenant-ID header** (explicit selection)
2. **Domain matching** (TenantDomain lookup) ← This fix
3. **Subdomain matching** (tenant.slug)
4. **User's default tenant** (authenticated user fallback)

### Database Schema

```python
class TenantDomain(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
```

### Why This Works

When a request comes to `dev-backend.meatscentral.com`:
1. TenantMiddleware extracts domain from request
2. Looks up domain in `TenantDomain` table
3. Finds mapping to `root` tenant
4. Sets `request.tenant = root`
5. Permission checks use root tenant context
6. Request succeeds ✅

---

**Last Updated**: December 10, 2025  
**Related PRs**: #1326 (TenantMiddleware ordering fix)
