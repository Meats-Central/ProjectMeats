"""
Products views for ProjectMeats.

Provides CRUD operations for product management with tenant isolation.
Uses shared-schema multi-tenancy with tenant ForeignKey filtering.
"""
import logging
from rest_framework import viewsets, permissions, filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products with tenant filtering.
    
    Provides CRUD operations with automatic tenant filtering.
    Uses shared-schema multi-tenancy approach (NOT django-tenants).
    
    Permissions:
    - Authenticated users can view products in their tenant
    - Only authenticated users can create/update/delete products
    
    Filters:
    - Search: product_code, description_of_product_item, supplier_item_number, namp, usda
    - Filter: type_of_protein, fresh_or_frozen, package_type, is_active, supplier, tested_product
    - Ordering: product_code, description_of_product_item, created_on, modified_on, unit_weight
    - Custom: customer (M2M filter via query param)
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
        'supplier',
        'type_of_protein',
        'fresh_or_frozen',
        'package_type',
        'edible_or_inedible',
        'is_active',
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
        Filter products by tenant with support for M2M relationships.
        
        Uses request.tenant set by TenantMiddleware.
        Shared-schema multi-tenancy approach with tenant ForeignKey.
        
        Custom filtering:
        - ?customer={id} - Filter by M2M customer relationship
        - ?protein=Beef&protein=Chicken - Filter by protein types (multiple)
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
        
        # Custom filtering for M2M relationships
        customer_id = self.request.query_params.get('customer', None)
        if customer_id:
            queryset = queryset.filter(customers__id=customer_id)
            logger.debug(f"Filtered products by customer: {customer_id}")
        
        # Protein type filtering (supports multiple values)
        protein_types = self.request.query_params.getlist('protein', None)
        if protein_types:
            queryset = queryset.filter(type_of_protein__in=protein_types)
            logger.debug(f"Filtered products by protein types: {protein_types}")
        
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
