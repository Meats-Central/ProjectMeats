"""
Purchase Orders views for ProjectMeats.

Provides REST API endpoints for purchase order management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from tenant_apps.purchase_orders.models import PurchaseOrder, PurchaseOrderHistory
from tenant_apps.purchase_orders.serializers import (
    PurchaseOrderSerializer,
    PurchaseOrderHistorySerializer,
)
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing purchase orders."""

    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter purchase orders by current tenant."""
        if hasattr(self.request, "tenant") and self.request.tenant:
            return PurchaseOrder.objects.for_tenant(self.request.tenant)
        return PurchaseOrder.objects.none()

    def perform_create(self, serializer):
        """Set the tenant and auto-generate order_number when creating a new purchase order."""
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
                "Purchase order creation attempted without tenant context",
                extra={
                    "user": self.request.user.username
                    if self.request.user and self.request.user.is_authenticated
                    else "Anonymous",
                    "has_request_tenant": hasattr(self.request, "tenant"),
                    "timestamp": timezone.now().isoformat(),
                },
            )
            raise ValidationError(
                "Tenant context is required to create a purchase order."
            )
        
        # Auto-generate order_number if not provided
        if not serializer.validated_data.get('order_number'):
            # Get all existing purchase orders for this tenant
            existing_pos = PurchaseOrder.objects.filter(tenant=tenant)
            
            # Find the highest numeric order number
            max_order_num = 0
            for po in existing_pos:
                try:
                    # Try to extract numeric value from order_number
                    num = int(po.order_number)
                    if num > max_order_num:
                        max_order_num = num
                except (ValueError, TypeError):
                    # Skip non-numeric order numbers
                    continue
            
            # Increment and assign
            next_order_num = str(max_order_num + 1)
            serializer.validated_data['order_number'] = next_order_num
            
            logger.info(
                f"Auto-generated order_number: {next_order_num} for tenant {tenant.name}",
                extra={
                    "tenant_id": tenant.id,
                    "order_number": next_order_num,
                    "timestamp": timezone.now().isoformat(),
                }
            )

        serializer.save(tenant=tenant)

    def create(self, request, *args, **kwargs):
        """Create a new purchase order with enhanced error handling."""
        try:
            return super().create(request, *args, **kwargs)
        except DRFValidationError as e:
            logger.error(
                f"Validation error creating purchase order: {str(e.detail)}",
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
                f"Validation error creating purchase order: {str(e)}",
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
                f"Error creating purchase order: {str(e)}",
                exc_info=True,
                extra={
                    "request_data": request.data,
                    "user": request.user.username if request.user else "Anonymous",
                    "timestamp": timezone.now().isoformat(),
                },
            )
            return Response(
                {
                    "error": "Failed to create purchase order",
                    "details": "Internal server error",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """
        Retrieve version history for a specific purchase order.

        GET /api/v1/purchase-orders/{id}/history/

        Returns a list of all historical changes made to the purchase order.
        """
        purchase_order = self.get_object()
        history_entries = PurchaseOrderHistory.objects.filter(
            purchase_order=purchase_order
        ).order_by("-created_on")

        serializer = PurchaseOrderHistorySerializer(history_entries, many=True)
        return Response(serializer.data)
