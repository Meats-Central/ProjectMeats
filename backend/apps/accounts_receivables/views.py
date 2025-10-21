from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError
from apps.accounts_receivables.models import AccountsReceivable
from apps.accounts_receivables.serializers import AccountsReceivableSerializer
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class AccountsReceivableViewSet(viewsets.ModelViewSet):
    queryset = AccountsReceivable.objects.all()
    serializer_class = AccountsReceivableSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "customer", "due_date"]
    search_fields = ["invoice_number", "description", "customer__name"]
    ordering_fields = ["due_date", "created_at", "amount"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Filter accounts receivables by current tenant."""
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = AccountsReceivable.objects.for_tenant(self.request.tenant)
            # Filter by customer if provided in query params
            customer_id = self.request.query_params.get("customer_id")
            if customer_id:
                queryset = queryset.filter(customer_id=customer_id)
            return queryset
        return AccountsReceivable.objects.none()

    def perform_create(self, serializer):
        """Set the tenant when creating a new accounts receivable."""
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
                'Accounts receivable creation attempted without tenant context',
                extra={
                    'user': self.request.user.username if self.request.user and self.request.user.is_authenticated else 'Anonymous',
                    'has_request_tenant': hasattr(self.request, 'tenant'),
                    'timestamp': timezone.now().isoformat()
                }
            )
            raise ValidationError('Tenant context is required to create an accounts receivable.')
        
        serializer.save(tenant=tenant)

    def create(self, request, *args, **kwargs):
        """Create a new accounts receivable record with enhanced error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except DRFValidationError as e:
            logger.error(
                f'Validation error creating accounts receivable: {str(e.detail)}',
                extra={
                    'request_data': request.data,
                    'user': request.user.username if request.user.is_authenticated else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            # Re-raise DRF validation errors to return 400
            raise
        except ValidationError as e:
            logger.error(
                f'Validation error creating accounts receivable: {str(e)}',
                extra={
                    'request_data': request.data,
                    'user': request.user.username if request.user.is_authenticated else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            return Response(
                {'error': 'Validation failed', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f'Error creating accounts receivable: {str(e)}',
                exc_info=True,
                extra={
                    'request_data': request.data,
                    'user': request.user.username if request.user.is_authenticated else 'Anonymous',
                    'timestamp': timezone.now().isoformat()
                }
            )
            return Response(
                {'error': 'Failed to create accounts receivable', 'details': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
