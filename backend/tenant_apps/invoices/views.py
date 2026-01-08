"""
Invoices and Claims views for ProjectMeats.

Provides REST API endpoints for invoice and claim management with strict multi-tenant isolation.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from tenant_apps.invoices.models import Invoice, Claim, PaymentTransaction
from tenant_apps.invoices.serializers import InvoiceSerializer, ClaimSerializer, PaymentTransactionSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing invoices with strict tenant isolation."""
    
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter invoices by tenant."""
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            return Invoice.objects.none()
        
        queryset = Invoice.objects.filter(tenant=self.request.tenant)
        
        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('customer', 'sales_order', 'product')
    
    def perform_create(self, serializer):
        """Auto-assign tenant on invoice creation."""
        serializer.save(tenant=self.request.tenant)


class ClaimViewSet(viewsets.ModelViewSet):
    """ViewSet for managing claims with strict tenant isolation."""
    
    queryset = Claim.objects.all()
    serializer_class = ClaimSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter claims by tenant and optional filters."""
        if not hasattr(self.request, 'tenant') or not self.request.tenant:
            return Claim.objects.none()
        
        queryset = Claim.objects.filter(tenant=self.request.tenant)
        
        # Filter by claim type (payable/receivable)
        claim_type = self.request.query_params.get('type')
        if claim_type:
            queryset = queryset.filter(claim_type=claim_type)
        
        # Filter by status
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.select_related('supplier', 'customer', 'purchase_order', 'sales_order', 'invoice')
    
    def perform_create(self, serializer):
        """Auto-assign tenant and created_by on claim creation."""
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user
        )



class PaymentTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PaymentTransaction model.
    
    Handles creating payment transactions and automatically updating
    the related order/invoice payment status.
    """
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter payments by tenant."""
        return super().get_queryset().filter(tenant=self.request.tenant)
    
    def perform_create(self, serializer):
        """Set tenant and created_by when creating payment."""
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user
        )
