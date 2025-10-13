"""
Middleware for multi-tenancy support in ProjectMeats.

This middleware sets the current tenant in the request context based on:
1. X-Tenant-ID header (for API requests) - HIGHEST PRIORITY
2. Subdomain (if configured)
3. Authenticated user's default tenant association - FALLBACK

Tenant Resolution Order:
-----------------------
1. **X-Tenant-ID Header**: For explicit tenant selection in API requests
   - Format: UUID string
   - Validates user has access to requested tenant
   - Returns 403 Forbidden if user lacks permission
   
2. **Subdomain**: For multi-tenant web applications
   - Extracts subdomain from request host
   - Matches against tenant.slug field
   - Example: acme.meatscentral.com → tenant with slug="acme"
   
3. **User's Default Tenant**: Automatic fallback for authenticated users
   - Queries TenantUser association
   - Prioritizes owner/admin roles
   - Returns first active tenant for user

If no tenant can be resolved, request.tenant is set to None.
ViewSets should handle None tenant by returning empty querysets or raising validation errors.
"""

from django.http import HttpRequest, HttpResponseForbidden
from .models import Tenant, TenantUser
import logging

logger = logging.getLogger(__name__)


class TenantMiddleware:
    """
    Middleware to set the current tenant in the request context.
    
    Sets two request attributes:
    - request.tenant: The resolved Tenant instance or None
    - request.tenant_user: The TenantUser association or None
    
    Security:
    - Verifies user has TenantUser association when using X-Tenant-ID header
    - Superusers can access any tenant
    - Returns 403 Forbidden for unauthorized tenant access attempts
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Process the request and set tenant context."""
        tenant = None
        resolution_method = None  # Track how tenant was resolved for logging

        # 1. Try to get tenant from X-Tenant-ID header (for API requests)
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id, is_active=True)
                resolution_method = "X-Tenant-ID header"
                
                # Verify user has access to this tenant
                if request.user.is_authenticated:
                    if not request.user.is_superuser:
                        if not TenantUser.objects.filter(
                            user=request.user, tenant=tenant, is_active=True
                        ).exists():
                            logger.warning(
                                f"Unauthorized tenant access attempt: "
                                f"user={request.user.username}, tenant_id={tenant_id}, "
                                f"path={request.path}"
                            )
                            return HttpResponseForbidden(
                                "You do not have access to this tenant"
                            )
            except Tenant.DoesNotExist:
                logger.warning(
                    f"Invalid tenant ID in X-Tenant-ID header: {tenant_id}, "
                    f"path={request.path}"
                )
            except ValueError:
                logger.warning(
                    f"Invalid tenant ID format in X-Tenant-ID header: {tenant_id}, "
                    f"path={request.path}"
                )

        # 2. Try to get tenant from subdomain
        if not tenant:
            host = request.get_host().split(":")[0]  # Remove port if present
            subdomain = host.split(".")[0] if "." in host else None

            if subdomain and subdomain != "www":
                try:
                    tenant = Tenant.objects.get(slug=subdomain, is_active=True)
                    resolution_method = f"subdomain ({subdomain})"
                except Tenant.DoesNotExist:
                    logger.debug(
                        f"No tenant found for subdomain: {subdomain}, "
                        f"path={request.path}"
                    )

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
                resolution_method = f"user default tenant (role={tenant_user.role})"

        # Log tenant resolution for debugging (at DEBUG level to avoid noise)
        if tenant:
            logger.debug(
                f"Tenant resolved: tenant={tenant.slug}, method={resolution_method}, "
                f"user={request.user.username if request.user.is_authenticated else 'Anonymous'}, "
                f"path={request.path}"
            )
        elif request.user.is_authenticated and not request.path.startswith('/admin'):
            # Log when authenticated user has no tenant (but not for admin/static paths)
            logger.debug(
                f"No tenant resolved for authenticated user: "
                f"user={request.user.username}, path={request.path}"
            )

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
                logger.debug(
                    f"No TenantUser association found: "
                    f"user={request.user.username}, tenant={tenant.slug}"
                )
            except Exception as e:
                # Catch database errors (e.g., readonly database, connection issues)
                logger.error(
                    f"Database error when fetching TenantUser: "
                    f"user={request.user.username}, tenant={tenant.slug}, "
                    f"error={type(e).__name__}: {str(e)}"
                )

        try:
            response = self.get_response(request)
        except Exception as e:
            # Log session-related errors that may indicate readonly database
            if "readonly" in str(e).lower() or "read-only" in str(e).lower():
                logger.error(
                    f"Readonly database error detected: "
                    f"user={request.user.username if request.user.is_authenticated else 'Anonymous'}, "
                    f"path={request.path}, error={type(e).__name__}: {str(e)}"
                )
            raise
        
        return response
