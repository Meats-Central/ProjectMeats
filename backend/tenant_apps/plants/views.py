from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from tenant_apps.plants.models import Plant
from tenant_apps.plants.serializers import PlantSerializer
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class PlantViewSet(viewsets.ModelViewSet):
    queryset = Plant.objects.all()
    serializer_class = PlantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["plant_type", "is_active", "city", "state"]
    search_fields = ["name", "code", "address", "city", "state", "manager"]
    ordering_fields = ["name", "code", "created_at", "capacity"]
    ordering = ["name"]

    def get_queryset(self):
        """Filter plants by current tenant."""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = Plant.objects.for_tenant(self.request.tenant)
            # Filter by active plants by default unless specified
            is_active = self.request.query_params.get("is_active")
            if is_active is None:
                queryset = queryset.filter(is_active=True)
            return queryset
        return Plant.objects.none()

    def perform_create(self, serializer):
        """Set the tenant when creating a new plant."""
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
        
        # If still no tenant, raise error
        if not tenant:
            logger.error(
                'Plant creation attempted without tenant context',
                extra={
                    'user': self.request.user.username if self.request.user and self.request.user.is_authenticated else 'Anonymous',
                    'has_request_tenant': hasattr(self.request, 'tenant'),
                    'timestamp': timezone.now().isoformat()
                }
            )
            raise ValidationError('Tenant context is required to create a plant.')
        
        serializer.save(tenant=tenant)

    def create(self, request, *args, **kwargs):
        """Create a new plant with enhanced error handling."""
        # Log incoming request for debugging
        logger.info(
            f'Creating plant with data: {request.data}',
            extra={
                'user': request.user.username if request.user and request.user.is_authenticated else 'Anonymous',
                'tenant': getattr(request, 'tenant', None),
                'has_tenant_attr': hasattr(request, 'tenant')
            }
        )
        
        try:
            return super().create(request, *args, **kwargs)
        except DRFValidationError as e:
            logger.error(
                f'Validation error creating plant: {str(e.detail)}',
                extra={
                    'request_data': request.data,
                    'user': request.user.username if request.user and request.user.is_authenticated else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            # Re-raise DRF validation errors to return 400
            raise
        except ValidationError as e:
            logger.error(
                f'Django validation error creating plant: {str(e)}',
                extra={
                    'request_data': request.data,
                    'user': request.user.username if request.user and request.user.is_authenticated else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            return Response(
                {'error': 'Validation failed', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f'Unexpected error creating plant: {str(e)}',
                exc_info=True,
                extra={
                    'request_data': request.data,
                    'user': request.user.username if request.user and request.user.is_authenticated else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            return Response(
                {'error': 'Failed to create plant', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
