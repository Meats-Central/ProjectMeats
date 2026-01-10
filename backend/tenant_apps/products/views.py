"""
ViewSets for Products app.
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model with tenant filtering.
    
    Supports:
    - List all products for the current tenant
    - Filter by supplier, customer, protein type, etc.
    - Create/Update/Delete products (tenant-scoped)
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'supplier',
        'type_of_protein',
        'fresh_or_frozen',
        'package_type',
        'edible_or_inedible',
        'is_active',
    ]
    search_fields = ['product_code', 'description_of_product_item', 'supplier_item_number']
    ordering_fields = ['product_code', 'created_on', 'modified_on']
    ordering = ['product_code']
    
    def get_queryset(self):
        """Filter products by tenant."""
        queryset = super().get_queryset().filter(tenant=self.request.tenant)
        
        # Custom filtering for M2M relationships
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(customers__id=customer_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set tenant on creation."""
        serializer.save(tenant=self.request.tenant)
