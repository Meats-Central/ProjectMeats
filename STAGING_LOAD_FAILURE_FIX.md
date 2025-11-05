# Staging Environment Load Failure Fix

## Problem
The staging.meatscentral.com environment was experiencing persistent load failures with no content or error messages displayed.

## Root Causes Identified

1. **Missing ALLOWED_HOSTS Entry**: `staging.meatscentral.com` was not included in Django's ALLOWED_HOSTS configuration for the staging environment.

2. **Missing TenantDomain Entry**: The custom TenantMiddleware attempts to resolve tenants via domain lookup using the TenantDomain model. If no entry exists for `staging.meatscentral.com`, the middleware cannot resolve a tenant, resulting in a failed request.

## Solution Implemented

### 1. Debug Logging Added
Added comprehensive debug logging to `apps/tenants/middleware.py` that activates specifically for `staging.meatscentral.com`:

- Logs incoming request details (host, path, method, authenticated user)
- Traces each tenant resolution attempt:
  - Domain lookup via TenantDomain model
  - Subdomain extraction and lookup
  - User's default tenant association
- Logs final resolution status (SUCCESS or FAILED)
- Logs response status code
- Logs any exceptions during request processing

All debug logs use the `[STAGING DEBUG]` prefix for easy filtering in log aggregation tools.

### 2. ALLOWED_HOSTS Fix
Added `staging.meatscentral.com` to the STAGING_HOSTS list in `backend/projectmeats/settings/staging.py`.

```python
STAGING_HOSTS = [
    "staging.meatscentral.com",  # Primary staging domain
    "staging-projectmeats.ondigitalocean.app",
    "projectmeats-staging.herokuapp.com",  # Fallback
]
```

### 3. Management Command Created
Created `add_tenant_domain.py` management command to add/update TenantDomain entries.

## Deployment Instructions

### Step 1: Deploy Code Changes
Deploy the updated code to the staging environment through the normal CI/CD pipeline.

### Step 2: Add TenantDomain Entry
SSH into the staging server and run the management command to create the TenantDomain entry:

```bash
# Connect to staging
ssh staging.meatscentral.com  # or use your deployment method

# Navigate to project directory
cd /path/to/projectmeats/backend

# Activate virtual environment (if applicable)
source venv/bin/activate

# Add the domain entry (replace 'meatscentral' with actual tenant slug if different)
python manage.py add_tenant_domain --domain=staging.meatscentral.com --tenant-slug=meatscentral

# Verify the entry was created
python manage.py shell
>>> from apps.tenants.models import TenantDomain
>>> TenantDomain.objects.filter(domain='staging.meatscentral.com')
>>> exit()
```

**Note**: Replace `meatscentral` with the actual tenant slug if it's different in your staging environment.

### Step 3: Restart Application
Restart the Django application to ensure all settings are reloaded:

```bash
# For systemd service
sudo systemctl restart projectmeats

# For Docker
docker-compose restart web

# For Kubernetes
kubectl rollout restart deployment/projectmeats-backend
```

### Step 4: Test Access
1. Open a browser with JavaScript enabled
2. Navigate to https://staging.meatscentral.com
3. Verify the application loads correctly
4. Check that you can log in and access tenant-specific data

### Step 5: Review Logs
Check the application logs for `[STAGING DEBUG]` entries to understand the tenant resolution flow:

```bash
# View recent logs
tail -f /var/log/projectmeats/django.log | grep "STAGING DEBUG"

# Or for Docker
docker-compose logs -f web | grep "STAGING DEBUG"

# Or for Kubernetes
kubectl logs -f deployment/projectmeats-backend | grep "STAGING DEBUG"
```

Example expected log output:
```
INFO [STAGING DEBUG] Request received - host=staging.meatscentral.com, path=/, method=GET, user=Anonymous
INFO [STAGING DEBUG] Attempting domain lookup for: staging.meatscentral.com
INFO [STAGING DEBUG] Tenant resolved via domain - tenant=meatscentral, tenant_id=<uuid>
INFO [STAGING DEBUG] Final tenant resolution SUCCESS - tenant=meatscentral, method=domain (staging.meatscentral.com)
INFO [STAGING DEBUG] Response generated - status_code=200
```

## Cleanup (After Verification)

Once the staging environment is working correctly and the issue is resolved, create a follow-up PR to remove the temporary debug logging:

1. Remove all logging statements with the `[STAGING DEBUG]` prefix
2. Remove the `is_staging` variable and conditional checks
3. Keep the ALLOWED_HOSTS fix and TenantDomain entry

Search for this pattern in `backend/apps/tenants/middleware.py`:
```python
if is_staging:
    logger.info(f"[STAGING DEBUG] ...")
```

## Troubleshooting

### Issue: Domain Entry Not Found
If the management command fails to find the tenant:
```bash
# List all tenants
python manage.py shell
>>> from apps.tenants.models import Tenant
>>> Tenant.objects.all().values('slug', 'name', 'is_active')
>>> exit()
```

Then use the correct slug in the management command.

### Issue: Still Getting Load Failures
1. Verify ALLOWED_HOSTS includes the domain:
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.ALLOWED_HOSTS)
   ```

2. Verify TenantDomain entry exists:
   ```bash
   python manage.py shell
   >>> from apps.tenants.models import TenantDomain
   >>> TenantDomain.objects.filter(domain='staging.meatscentral.com').values()
   ```

3. Check for errors in Django logs
4. Verify the tenant is active:
   ```bash
   python manage.py shell
   >>> from apps.tenants.models import Tenant, TenantDomain
   >>> td = TenantDomain.objects.get(domain='staging.meatscentral.com')
   >>> print(f"Tenant: {td.tenant.slug}, Active: {td.tenant.is_active}")
   ```

### Issue: Logs Not Showing
Ensure the logging level is set to INFO or DEBUG in your staging environment settings.

## Files Modified
- `backend/apps/tenants/middleware.py` - Added debug logging
- `backend/projectmeats/settings/staging.py` - Added staging.meatscentral.com to ALLOWED_HOSTS
- `backend/apps/tenants/management/commands/add_tenant_domain.py` - New management command (created)

## Related Documentation
- Multi-tenancy implementation: `backend/apps/tenants/TENANT_ONBOARDING.md`
- Environment guide: `docs/ENVIRONMENT_GUIDE.md`
- Deployment guide: `DEPLOYMENT_GUIDE.md`
