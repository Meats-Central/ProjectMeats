"""
Middleware for shared-schema multi-tenancy support in ProjectMeats.

Architecture: Shared Schema Multi-Tenancy
=========================================
This middleware sets the current tenant in the request context based on:
1. X-Tenant-ID header (for API requests) - HIGHEST PRIORITY
2. Full domain name match (via TenantDomain model)
3. Subdomain (if configured)
4. Authenticated user's default tenant association - FALLBACK

All tenant isolation is enforced via tenant_id foreign keys on business
models. There is NO PostgreSQL schema-based routing.

Tenant Resolution Order:
-----------------------
1. **X-Tenant-ID Header**: For explicit tenant selection in API requests
   - Format: UUID string
   - Validates user has access to requested tenant
   - Returns 403 Forbidden if user lacks permission
   
2. **Domain Match**: For multi-tenant domain routing
   - Matches full domain against TenantDomain model entries
   - Example: tenant.example.com → TenantDomain.objects.get(domain="tenant.example.com")
   
3. **Subdomain**: For multi-tenant web applications
   - Extracts subdomain from request host
   - Matches against tenant.slug field
   - Example: acme.meatscentral.com → tenant with slug="acme"
   
4. **User's Default Tenant**: Automatic fallback for authenticated users
   - Queries TenantUser association
   - Prioritizes owner/admin roles
   - Returns first active tenant for user

If no tenant can be resolved, request.tenant is set to None.
ViewSets should handle None tenant by returning empty querysets or raising validation errors.
"""

from django.http import HttpRequest, HttpResponseForbidden
from .models import Tenant, TenantUser, TenantDomain
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
        # Skip tenant resolution for health check and readiness endpoints
        if request.path.startswith('/api/v1/health/') or request.path.startswith('/api/v1/ready/'):
            request.tenant = None
            request.tenant_user = None
            return self.get_response(request)
        
        tenant = None
        resolution_method = None  # Track how tenant was resolved for logging
        
        # Temporary debugging for staging.meatscentral.com and uat.meatscentral.com
        host = request.get_host().split(":")[0]
        is_debug_host = host in ["staging.meatscentral.com", "uat.meatscentral.com"]
        debug_prefix = "[STAGING DEBUG]" if host == "staging.meatscentral.com" else "[UAT DEBUG]"
        if is_debug_host:
            logger.info(
                f"{debug_prefix} Request received - "
                f"host={host}, path={request.path}, "
                f"method={request.method}, "
                f"user={request.user.username if request.user.is_authenticated else 'Anonymous'}"
            )

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

        # 2. Try to get tenant from full domain match (via TenantDomain model)
        if not tenant:
            host = request.get_host().split(":")[0]  # Remove port if present
            
            if is_debug_host:
                logger.info(f"{debug_prefix} Attempting domain lookup for: {host}")
            
            try:
                domain_obj = TenantDomain.objects.select_related('tenant').get(
                    domain=host
                )
                if domain_obj.tenant.is_active:
                    tenant = domain_obj.tenant
                    resolution_method = f"domain ({host})"
                    if is_debug_host:
                        logger.info(
                            f"{debug_prefix} Tenant resolved via domain - "
                            f"tenant={tenant.slug}, tenant_id={tenant.id}"
                        )
                else:
                    if is_debug_host:
                        logger.info(
                            f"{debug_prefix} Domain found but tenant is inactive - "
                            f"tenant={domain_obj.tenant.slug}"
                        )
            except TenantDomain.DoesNotExist:
                if is_debug_host:
                    logger.info(
                        f"{debug_prefix} No TenantDomain entry found for: {host}"
                    )
                logger.debug(
                    f"No TenantDomain entry found for: {host}, "
                    f"path={request.path}"
                )

        # 3. Try to get tenant from subdomain
        if not tenant:
            host = request.get_host().split(":")[0]  # Remove port if present
            subdomain = host.split(".")[0] if "." in host else None

            if subdomain and subdomain != "www":
                if is_debug_host:
                    logger.info(f"{debug_prefix} Attempting subdomain lookup for: {subdomain}")
                
                try:
                    tenant = Tenant.objects.get(slug=subdomain, is_active=True)
                    resolution_method = f"subdomain ({subdomain})"
                    if is_debug_host:
                        logger.info(
                            f"{debug_prefix} Tenant resolved via subdomain - "
                            f"tenant={tenant.slug}, tenant_id={tenant.id}"
                        )
                except Tenant.DoesNotExist:
                    if is_debug_host:
                        logger.info(f"{debug_prefix} No tenant found for subdomain: {subdomain}")
                    logger.debug(
                        f"No tenant found for subdomain: {subdomain}, "
                        f"path={request.path}"
                    )

        # 4. Get user's default tenant if authenticated
        if not tenant and hasattr(request, 'user') and request.user.is_authenticated:
            if is_debug_host:
                logger.info(f"{debug_prefix} Attempting default tenant lookup for user: {request.user.username}")
            
            tenant_user = (
                TenantUser.objects.filter(user=request.user, is_active=True)
                .select_related("tenant")
                .order_by("-role")  # Prioritize owner/admin roles
                .first()
            )
            if tenant_user:
                tenant = tenant_user.tenant
                resolution_method = f"user default tenant (role={tenant_user.role})"
                if is_debug_host:
                    logger.info(
                        f"{debug_prefix} Tenant resolved via user default - "
                        f"tenant={tenant.slug}, tenant_id={tenant.id}, role={tenant_user.role}"
                    )
            else:
                if is_debug_host:
                    logger.info(
                        f"{debug_prefix} No default tenant found for user: {request.user.username}"
                    )

        # Final tenant resolution result for debug hosts
        if is_debug_host:
            if tenant:
                logger.info(
                    f"{debug_prefix} Final tenant resolution SUCCESS - "
                    f"tenant={tenant.slug}, method={resolution_method}"
                )
            else:
                logger.info(
                    f"{debug_prefix} Final tenant resolution FAILED - "
                    f"No tenant could be resolved for request"
                )

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
            
            if is_debug_host:
                logger.info(
                    f"{debug_prefix} Response generated - "
                    f"status_code={response.status_code if hasattr(response, 'status_code') else 'unknown'}"
                )
        except Exception as e:
            if is_debug_host:
                logger.error(
                    f"{debug_prefix} Exception during request processing - "
                    f"error_type={type(e).__name__}, error={str(e)}"
                )
            # Log session-related errors that may indicate readonly database
            if "readonly" in str(e).lower() or "read-only" in str(e).lower():
                logger.error(
                    f"Readonly database error detected: "
                    f"user={request.user.username if request.user.is_authenticated else 'Anonymous'}, "
                    f"path={request.path}, error={type(e).__name__}: {str(e)}"
                )
            raise
        
        return response
