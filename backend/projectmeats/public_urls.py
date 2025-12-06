"""
Public schema URL configuration for ProjectMeats.

⚠️ WARNING: This file is NOT CURRENTLY USED ⚠️

This file was created for django-tenants' PUBLIC_SCHEMA_URLCONF setting,
which routes requests in the "public" schema (without tenant context).

CURRENT STATUS:
- TenantMainMiddleware is DISABLED in settings/base.py
- Using custom TenantMiddleware instead (shared schema pattern)
- ALL requests use projectmeats.urls (ROOT_URLCONF)
- This file is kept for reference but is not active

If you need to re-enable schema-based routing, you would need to:
1. Enable django_tenants.middleware.main.TenantMainMiddleware
2. Set PUBLIC_SCHEMA_URLCONF = "projectmeats.public_urls" in settings
3. Ensure database has proper schema structure

See: https://django-tenants.readthedocs.io/ for more information.
"""
from django.urls import path
from .health import health_check, health_detailed, ready_check

# Legacy public schema URLs (not currently used)
urlpatterns = [
    # Health check endpoints (no tenant required)
    path("api/v1/health/", health_check, name="health-check"),
    path("api/v1/health/detailed/", health_detailed, name="health-detailed"),
    path("api/v1/ready/", ready_check, name="ready-check"),
]
