"""
Suppliers views for ProjectMeats.

Provides REST API endpoints for supplier management.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from apps.suppliers.models import Supplier
from apps.suppliers.serializers import SupplierSerializer
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class SupplierViewSet(viewsets.ModelViewSet):
    """ViewSet for managing suppliers."""

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter suppliers by current tenant."""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Supplier.objects.for_tenant(self.request.tenant)
        return Supplier.objects.none()

    def perform_create(self, serializer):
        """Set the tenant when creating a new supplier."""
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            logger.error(
                'Supplier creation attempted without tenant context',
                extra={
                    'user': self.request.user.username if self.request.user else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            raise ValidationError('Tenant context is required to create a supplier.')
        serializer.save(tenant=self.request.tenant)

    def create(self, request, *args, **kwargs):
        """Create a new supplier with enhanced error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except DRFValidationError as e:
            logger.error(
                f'Validation error creating supplier: {str(e.detail)}',
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
                f'Validation error creating supplier: {str(e)}',
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
                f'Error creating supplier: {str(e)}',
                exc_info=True,
                extra={
                    'request_data': request.data,
                    'user': request.user.username if request.user else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            return Response(
                {'error': 'Failed to create supplier', 'details': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
