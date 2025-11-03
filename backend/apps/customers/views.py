"""
Customers views for ProjectMeats.

Provides REST API endpoints for customer management with strict multi-tenant isolation.

SECURITY MODEL:
===============
All Environments:
    - Authentication is REQUIRED (IsAuthenticated permission)
    - Tenant context is MANDATORY from middleware (X-Tenant-ID header or user association)
    - Strict tenant isolation enforced - users only see their tenant's data
    - ✅ SECURE: Proper multi-tenant data isolation across all environments
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from apps.customers.models import Customer
from apps.customers.serializers import CustomerSerializer
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customers with strict tenant isolation.
    
    Security Model:
    - Authentication is REQUIRED for all environments
    - Tenant context is MANDATORY - users only see their tenant's data
    - No DEBUG-based bypasses - consistent security across all environments
    """

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter customers by tenant - strict isolation enforced.
        
        Tenant Resolution:
        1. request.tenant (set by TenantMiddleware from X-Tenant-ID header or user association)
        2. Empty queryset if no tenant (security - no data exposure)
        
        Returns:
            QuerySet: Customers for the current tenant only
        """
        # Use tenant from middleware
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Customer.objects.for_tenant(self.request.tenant)
        
        # No tenant = no data (security)
        logger.warning(
            f'No tenant context for user {self.request.user.username} '
            f'accessing customers - returning empty queryset'
        )
        return Customer.objects.none()

    def perform_create(self, serializer):
        """
        Set the tenant when creating a new customer.
        
        Tenant Resolution:
        1. Use request.tenant from TenantMiddleware
        2. Raise ValidationError if no tenant found
        
        Args:
            serializer: Validated serializer instance
            
        Raises:
            ValidationError: If no tenant context is available
        """
        tenant = None
        
        # Get tenant from middleware (request.tenant)
        if hasattr(self.request, 'tenant') and self.request.tenant:
            tenant = self.request.tenant
        
        # Require tenant - no fallbacks or auto-creation
        if not tenant:
            error_message = 'Tenant context is required to create a customer. Please ensure you are associated with a tenant.'
            logger.error(
                'Customer creation attempted without tenant context',
                extra={
                    'user': self.request.user.username if self.request.user.is_authenticated else 'Anonymous',
                    'has_request_tenant': hasattr(self.request, 'tenant'),
                    'timestamp': timezone.now().isoformat(),
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
                    'request_data': request.data,
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
                    'request_data': request.data,
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
                    'request_data': request.data,
                    'user': request.user.username if request.user else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            return Response(
                {'error': 'Failed to create customer', 'details': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
