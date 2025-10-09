"""
Middleware for multi-tenancy support in ProjectMeats.

This middleware sets the current tenant in the request context based on:
1. Authenticated user's tenant association
2. Subdomain (if configured)
3. X-Tenant-ID header (for API requests)
"""

from django.http import HttpRequest, HttpResponseForbidden
from .models import Tenant, TenantUser
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """
    Middleware to set the current tenant in the request context.
    
    This middleware determines the tenant from:
    - X-Tenant-ID header for API requests
    - User's default tenant from TenantUser association
    - Subdomain (if domain is configured)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Process the request and set tenant context."""
        tenant = None

        # 1. Try to get tenant from X-Tenant-ID header (for API requests)
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
                # Verify user has access to this tenant
                if request.user.is_authenticated:
                    if not request.user.is_superuser:
                        if not TenantUser.objects.filter(
                            user=request.user, tenant=tenant, is_active=True
                        ).exists():
                            logger.warning(
                                f"User {request.user.username} attempted to access "
                                f"tenant {tenant_id} without permission"
                            )
                            return HttpResponseForbidden(
                                "You do not have access to this tenant"
                            )
            except Tenant.DoesNotExist:
                logger.warning(f"Invalid tenant ID in header: {tenant_id}")
            except ValueError:
                logger.warning(f"Invalid tenant ID format in header: {tenant_id}")

        # 2. Try to get tenant from subdomain
        if not tenant:
            host = request.get_host().split(":")[0]  # Remove port if present
            subdomain = host.split(".")[0] if "." in host else None

            if subdomain and subdomain != "www":
                try:
                    tenant = Tenant.objects.get(slug=subdomain, is_active=True)
                except Tenant.DoesNotExist:
                    pass

        # 3. Get user's default tenant if authenticated
        if not tenant and request.user.is_authenticated:
            tenant_user = (
                TenantUser.objects.filter(user=request.user, is_active=True)
                .select_related("tenant")
                .order_by("-role")  # Prioritize owner/admin roles
                .first()
            )
            if tenant_user:
                tenant = tenant_user.tenant

        # Set tenant in request
        request.tenant = tenant
        request.tenant_user = None

        # Set tenant_user if we have both tenant and authenticated user
        if tenant and request.user.is_authenticated:
            try:
                request.tenant_user = TenantUser.objects.get(
                    user=request.user, tenant=tenant, is_active=True
                )
            except TenantUser.DoesNotExist:
                # User is superuser or accessing via header without association
                pass

        response = self.get_response(request)
        return response
