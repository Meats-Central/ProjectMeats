"""
Public schema URL configuration for ProjectMeats.

These URLs are accessible without a tenant context (in the public schema).
Used for health checks, system status, and other non-tenant-specific endpoints.
"""
from django.urls import path
from .health import health_check, health_detailed, ready_check

urlpatterns = [
    # Health check endpoints (no tenant required)
    path("api/v1/health/", health_check, name="health-check"),
    path("api/v1/health/detailed/", health_detailed, name="health-detailed"),
    path("api/v1/ready/", ready_check, name="ready-check"),
]
