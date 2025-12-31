"""
Legacy public schema URL configuration for ProjectMeats.

⚠️ WARNING: This file is NOT CURRENTLY USED ⚠️

This file is a legacy artifact from a previous django-tenants implementation
that used schema-based multi-tenancy. ProjectMeats now uses a shared-schema
approach with tenant_id foreign keys for data isolation.

CURRENT ARCHITECTURE:
- Using custom TenantMiddleware (apps.tenants.middleware.TenantMiddleware)
- ALL requests use projectmeats.urls (ROOT_URLCONF)
- Tenant isolation via tenant_id foreign keys on business models
- NO django-tenants or schema-based routing

This file is kept for historical reference but serves no active purpose.
It can be safely deleted in future cleanup efforts.
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
