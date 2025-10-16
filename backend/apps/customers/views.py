"""
Customers views for ProjectMeats.

Provides REST API endpoints for customer management with multi-tenant isolation.

SECURITY MODEL:
===============
Development (DEBUG=True):
    - Authentication is OPTIONAL to allow easier local testing
    - Returns all customers regardless of tenant context
    - ⚠️ WARNING: This is intentionally insecure for development convenience

Production/Staging (DEBUG=False):
    - Authentication is REQUIRED (IsAuthenticated permission)
    - Tenant context is MANDATORY from middleware or user association
    - Strict tenant isolation enforced
    - ✅ SECURE: Proper multi-tenant data isolation

IMPORTANT: The DEBUG setting controls this behavior. Never set DEBUG=True in production.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customers with environment-aware security.
    
    Authentication and permissions are dynamically configured based on DEBUG setting:
    - DEBUG=True (dev): No auth required for easier testing
    - DEBUG=False (prod/staging): Auth required, strict tenant isolation
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
    def get_authenticators(self):
        """
        Control authentication requirements based on environment.
        
        Development (DEBUG=True):
            Returns empty list to bypass authentication entirely.
            This allows frontend to make requests without valid tokens.
            
        Production (DEBUG=False):
            Uses default authenticators (SessionAuthentication, TokenAuthentication).
            All requests must have valid authentication credentials.
            
        Returns:
            list: Empty list in development, default authenticators in production
        """
        if settings.DEBUG:
            logger.debug('Development mode: Authentication disabled for customer endpoints')
            return []
        return super().get_authenticators()
    
    def get_permissions(self):
        """
        Control permission requirements based on environment.
        
        Development (DEBUG=True):
            AllowAny permission - no restrictions
            
        Production (DEBUG=False):
            IsAuthenticated permission - must be logged in
            
        Returns:
            list: Permission classes for this viewset
        """
        if settings.DEBUG:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Filter customers by tenant with environment-aware behavior.
        
        Tenant Resolution Order:
        1. request.tenant (set by TenantMiddleware)
        2. User's default tenant (from TenantUser relationship)
        3. Development fallback (all customers) if DEBUG=True
        4. Empty queryset if no tenant found and DEBUG=False
        
        Development (DEBUG=True):
            Returns all customers without tenant filtering for easier testing.
            
        Production (DEBUG=False):
            Strictly enforces tenant isolation. Returns empty queryset if no tenant context.
            
        Returns:
            QuerySet: Filtered customer queryset
        """
        # Primary: Use tenant from middleware
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Customer.objects.for_tenant(self.request.tenant)
        
        # Development fallback: Return all customers
        if settings.DEBUG:
            logger.debug('Development mode: returning all customers (no tenant filtering)')
            return Customer.objects.all()
        
        # Production: No tenant = no data (security)
        logger.warning('No tenant context available for authenticated request')
        return Customer.objects.none()

    def perform_create(self, serializer):
        """
        Set the tenant when creating a new customer.
        
        Tenant Resolution Strategy:
        1. Use request.tenant from TenantMiddleware
        2. Use user's default tenant from TenantUser association
        3. (Dev only) Auto-create "Development Tenant" if DEBUG=True
        4. (Prod) Raise ValidationError if no tenant found
        
        Args:
            serializer: Validated serializer instance
            
        Raises:
            ValidationError: If no tenant context is available (production only)
        """
        tenant = None
        
        # First, try to get tenant from middleware (request.tenant)
        if hasattr(self.request, 'tenant') and self.request.tenant:
            tenant = self.request.tenant
        
        # If middleware didn't set tenant, try to get user's default tenant
        elif self.request.user and self.request.user.is_authenticated:
            from apps.tenants.models import TenantUser
            tenant_user = (
                TenantUser.objects.filter(user=self.request.user, is_active=True)
                .select_related('tenant')
                .order_by('-role')  # Prioritize owner/admin roles
                .first()
            )
            if tenant_user:
                tenant = tenant_user.tenant
        
        # Development mode: Auto-create a default tenant for convenience
        # ⚠️ WARNING: This is intentionally insecure and only runs when DEBUG=True
        if not tenant and settings.DEBUG:
            from apps.tenants.models import Tenant
            # Get or create a development tenant (slug-based lookup for idempotency)
            tenant, created = Tenant.objects.get_or_create(
                slug='development',
                defaults={
                    'name': 'Development Tenant',
                    'contact_email': 'dev@projectmeats.local',
                    'is_active': True,
                    'is_trial': True,
                }
            )
            if created:
                logger.info(f'✅ Auto-created development tenant: {tenant.name} ({tenant.slug})')
            else:
                logger.debug(f'♻️  Using existing development tenant: {tenant.name} ({tenant.slug})')
        
        # Production: Require tenant or fail
        # This ensures proper multi-tenant isolation in production environments
        if not tenant:
            error_message = 'Tenant context is required to create a customer. Please ensure you are associated with a tenant.'
            logger.error(
                'Customer creation attempted without tenant context',
                extra={
                    'user': self.request.user.username if self.request.user and self.request.user.is_authenticated else 'Anonymous',
                    'has_request_tenant': hasattr(self.request, 'tenant'),
                    'is_authenticated': self.request.user.is_authenticated if hasattr(self.request, 'user') else False,
                    'timestamp': timezone.now().isoformat(),
                    'DEBUG': settings.DEBUG,
                }
            )
            raise ValidationError(error_message)
        
        # Save with tenant association
        serializer.save(tenant=tenant)
        logger.info(f'Created customer: {serializer.data.get("name")} for tenant: {tenant.name}')

    def create(self, request, *args, **kwargs):
        """Create a new customer with enhanced error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except DRFValidationError as e:
            logger.error(
                f'Validation error creating customer: {str(e.detail)}',
                extra={
                    'request_data': getattr(request, 'data', {}),
                    'user': request.user.username if request.user else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            # Re-raise DRF validation errors to return 400
            raise
        except ValidationError as e:
            logger.error(
                f'Validation error creating customer: {str(e)}',
                extra={
                    'request_data': getattr(request, 'data', {}),
                    'user': request.user.username if request.user else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            return Response(
                {'error': 'Validation failed', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f'Error creating customer: {str(e)}',
                exc_info=True,
                extra={
                    'request_data': getattr(request, 'data', {}),
                    'user': request.user.username if request.user else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            return Response(
                {'error': 'Failed to create customer', 'details': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
