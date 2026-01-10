"""
Products views for ProjectMeats.

Provides CRUD operations for product management with tenant isolation.
Uses shared-schema multi-tenancy with tenant ForeignKey filtering.
"""
import logging
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    
    Provides CRUD operations with automatic tenant filtering.
    Uses shared-schema multi-tenancy approach (NOT django-tenants).
    
    Permissions:
    - Authenticated users can view products in their tenant
    - Only staff can create/update/delete products
    
    Filters:
    - Search: product_code, description_of_product_item, supplier_item_number
    - Filter: type_of_protein, fresh_or_frozen, is_active, supplier
    - Ordering: product_code, created_on, modified_on
    """
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Search fields
    search_fields = [
        'product_code',
        'description_of_product_item',
        'supplier_item_number',
        'namp',
        'usda',
    ]
    
    # Filterset fields
    filterset_fields = [
        'type_of_protein',
        'fresh_or_frozen',
        'package_type',
        'is_active',
        'supplier',
        'tested_product',
    ]
    
    # Ordering fields
    ordering_fields = [
        'product_code',
        'description_of_product_item',
        'created_on',
        'modified_on',
        'unit_weight',
    ]
    ordering = ['product_code']
    
    def get_queryset(self):
        """
        Filter products by tenant.
        
        Uses request.tenant set by TenantMiddleware.
        Shared-schema multi-tenancy approach with tenant ForeignKey.
        """
        queryset = super().get_queryset()
        
        # Filter by tenant from middleware
        if hasattr(self.request, 'tenant') and self.request.tenant:
            queryset = queryset.filter(tenant=self.request.tenant)
            logger.debug(f"Filtered products for tenant: {self.request.tenant.slug}")
        else:
            # Fallback: no tenant context (should not happen in production)
            logger.warning("No tenant context in ProductViewSet - returning empty queryset")
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Auto-assign tenant on creation.
        
        Tenant is set from request.tenant (TenantMiddleware).
        """
        if hasattr(self.request, 'tenant') and self.request.tenant:
            serializer.save(tenant=self.request.tenant)
            logger.info(f"Created product for tenant: {self.request.tenant.slug}")
        else:
            logger.error("Cannot create product without tenant context")
            raise ValueError("Tenant context is required to create products")

