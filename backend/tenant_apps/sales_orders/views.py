"""
Sales Orders views for ProjectMeats.

Provides REST API endpoints for sales order management.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from tenant_apps.sales_orders.models import SalesOrder
from tenant_apps.sales_orders.serializers import SalesOrderSerializer
import logging

logger = logging.getLogger(__name__)


class SalesOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sales orders."""

    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter sales orders by current tenant."""
        if hasattr(self.request, "tenant") and self.request.tenant:
            return SalesOrder.objects.for_tenant(self.request.tenant)
        return SalesOrder.objects.none()

    def perform_create(self, serializer):
        """Set the tenant and auto-generate our_sales_order_num when creating a new sales order."""
        tenant = None

        # First, try to get tenant from middleware (request.tenant)
        if hasattr(self.request, "tenant") and self.request.tenant:
            tenant = self.request.tenant

        # If middleware didn't set tenant, try to get user's default tenant
        elif self.request.user and self.request.user.is_authenticated:
            from apps.tenants.models import TenantUser

            tenant_user = (
                TenantUser.objects.filter(user=self.request.user, is_active=True)
                .select_related("tenant")
                .order_by("-role")  # Prioritize owner/admin roles
                .first()
            )
            if tenant_user:
                tenant = tenant_user.tenant

        # If still no tenant, raise error
        if not tenant:
            logger.error(
                "Sales order creation attempted without tenant context",
                extra={
                    "user": self.request.user.username
                    if self.request.user and self.request.user.is_authenticated
                    else "Anonymous",
                    "has_request_tenant": hasattr(self.request, "tenant"),
                    "timestamp": timezone.now().isoformat(),
                },
            )
            raise ValidationError(
                "Tenant context is required to create a sales order."
            )
        
        # Auto-generate our_sales_order_num if not provided (atomic to prevent duplicates)
        with transaction.atomic():
            if not serializer.validated_data.get('our_sales_order_num'):
                # Get all existing sales orders for this tenant with a lock
                existing_sos = SalesOrder.objects.filter(tenant=tenant).select_for_update()
                
                # Find the highest numeric sales order number
                max_order_num = 0
                for so in existing_sos:
                    try:
                        # Try to extract numeric value from our_sales_order_num
                        num = int(so.our_sales_order_num)
                        if num > max_order_num:
                            max_order_num = num
                    except (ValueError, TypeError):
                        # Skip non-numeric order numbers
                        continue
                
                # Increment and assign
                next_order_num = str(max_order_num + 1)
                serializer.validated_data['our_sales_order_num'] = next_order_num
                
                logger.info(
                    f"Auto-generated our_sales_order_num: {next_order_num} for tenant {tenant.name}",
                    extra={
                        "tenant_id": tenant.id,
                        "our_sales_order_num": next_order_num,
                        "timestamp": timezone.now().isoformat(),
                    }
                )

            serializer.save(tenant=tenant)

    def create(self, request, *args, **kwargs):
        """Create a new sales order with enhanced error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except DRFValidationError as e:
            logger.error(
                f"Validation error creating sales order: {str(e.detail)}",
                extra={
                    "request_data": request.data,
                    "user": request.user.username if request.user else "Anonymous",
                    "timestamp": timezone.now().isoformat(),
                },
            )
            # Re-raise DRF validation errors to return 400
            raise
        except ValidationError as e:
            logger.error(
                f"Validation error creating sales order: {str(e)}",
                extra={
                    "request_data": request.data,
                    "user": request.user.username if request.user else "Anonymous",
                    "timestamp": timezone.now().isoformat(),
                },
            )
            return Response(
                {"error": "Validation failed", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(
                f"Error creating sales order: {str(e)}",
                exc_info=True,
                extra={
                    "request_data": request.data,
                    "user": request.user.username if request.user else "Anonymous",
                    "timestamp": timezone.now().isoformat(),
                },
            )
            return Response(
                {
                    "error": "Failed to create sales order",
                    "details": "Internal server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
