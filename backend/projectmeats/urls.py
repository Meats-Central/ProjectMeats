"""
URL configuration for ProjectMeats.

Main URL routing for the Django REST API backend.
Provides versioned API endpoints and documentation.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .health import health_check, health_detailed, ready_check

urlpatterns = [
    # Health check endpoints
    path("api/v1/health/", health_check, name="health-check"),
    path("api/v1/health/detailed/", health_detailed, name="health-detailed"),
    path("api/v1/ready/", ready_check, name="ready-check"),
    # Admin interface
    path("admin/", admin.site.urls),
    # API v1 endpoints
    path("api/v1/", include("apps.tenants.urls")),  # Multi-tenancy endpoints (shared)
    path("api/v1/", include("tenant_apps.accounts_receivables.urls")),
    path("api/v1/", include("tenant_apps.suppliers.urls")),
    path("api/v1/", include("tenant_apps.customers.urls")),
    path("api/v1/", include("tenant_apps.contacts.urls")),
    path("api/v1/", include("tenant_apps.purchase_orders.urls")),
    path("api/v1/", include("tenant_apps.plants.urls")),
    path("api/v1/", include("tenant_apps.carriers.urls")),
    path("api/v1/ai-assistant/", include("tenant_apps.ai_assistant.urls")),
    path("api/v1/", include("apps.core.urls")),  # Core shared utilities
    path("api/v1/bug-reports/", include("tenant_apps.bug_reports.urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
