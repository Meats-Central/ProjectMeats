"""
Contacts views for ProjectMeats.

Provides REST API endpoints for contact management.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from apps.contacts.models import Contact
from apps.contacts.serializers import ContactSerializer
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class ContactViewSet(viewsets.ModelViewSet):
    """ViewSet for managing contacts."""

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter contacts by current tenant."""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            return Contact.objects.for_tenant(self.request.tenant)
        return Contact.objects.none()

    def perform_create(self, serializer):
        """Set the tenant when creating a new contact."""
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            logger.error(
                'Contact creation attempted without tenant context',
                extra={
                    'user': self.request.user.username if self.request.user else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            raise ValidationError('Tenant context is required to create a contact.')
        serializer.save(tenant=self.request.tenant)

    def create(self, request, *args, **kwargs):
        """Create a new contact with enhanced error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except DRFValidationError as e:
            logger.error(
                f'Validation error creating contact: {str(e.detail)}',
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
                f'Validation error creating contact: {str(e)}',
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
                f'Error creating contact: {str(e)}',
                exc_info=True,
                extra={
                    'request_data': request.data,
                    'user': request.user.username if request.user else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            return Response(
                {'error': 'Failed to create contact', 'details': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
