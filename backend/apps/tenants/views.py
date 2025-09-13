from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Tenant, TenantUser
from .serializers import (
    TenantSerializer, TenantCreateSerializer, 
    TenantUserSerializer, UserTenantSerializer
)


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants.
    Provides CRUD operations for tenant management.
    """
    
    queryset = Tenant.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_trial']
    search_fields = ['name', 'slug', 'contact_email', 'domain']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return TenantCreateSerializer
        return TenantSerializer
    
    def get_queryset(self):
        """Filter tenants based on user permissions."""
        user = self.request.user
        if user.is_superuser:
            return Tenant.objects.all()
        
        # Regular users can only see tenants they belong to
        tenant_ids = TenantUser.objects.filter(
            user=user, is_active=True
        ).values_list('tenant_id', flat=True)
        return Tenant.objects.filter(id__in=tenant_ids)
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get all users for a specific tenant."""
        tenant = self.get_object()
        tenant_users = TenantUser.objects.filter(
            tenant=tenant, is_active=True
        ).select_related('user')
        
        serializer = TenantUserSerializer(tenant_users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_user(self, request, pk=None):
        """Add a user to a tenant."""
        tenant = self.get_object()
        
        # Check if user has permission to manage this tenant
        if not TenantUser.objects.filter(
            tenant=tenant, user=request.user, 
            role__in=['owner', 'admin'], is_active=True
        ).exists() and not request.user.is_superuser:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TenantUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tenant=tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_tenants(self, request):
        """Get all tenants for the current user."""
        tenant_users = TenantUser.objects.filter(
            user=request.user, is_active=True
        ).select_related('tenant')
        
        serializer = UserTenantSerializer(tenant_users, many=True)
        return Response(serializer.data)


class TenantUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenant-user associations.
    """
    
    queryset = TenantUser.objects.all()
    serializer_class = TenantUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['tenant', 'user', 'role', 'is_active']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter based on user permissions."""
        user = self.request.user
        if user.is_superuser:
            return TenantUser.objects.select_related('user', 'tenant')
        
        # Users can only see associations for tenants they have admin access to
        admin_tenant_ids = TenantUser.objects.filter(
            user=user, role__in=['owner', 'admin'], is_active=True
        ).values_list('tenant_id', flat=True)
        
        return TenantUser.objects.filter(
            tenant_id__in=admin_tenant_ids
        ).select_related('user', 'tenant')
    
    def perform_create(self, serializer):
        """Ensure user has permission to create associations."""
        tenant = serializer.validated_data['tenant']
        
        # Check if user has admin access to the tenant
        if not TenantUser.objects.filter(
            tenant=tenant, user=self.request.user,
            role__in=['owner', 'admin'], is_active=True
        ).exists() and not self.request.user.is_superuser:
            raise permissions.PermissionDenied(
                "You don't have permission to manage users for this tenant."
            )
        
        serializer.save()
    
    def perform_update(self, serializer):
        """Ensure user has permission to update associations."""
        instance = self.get_object()
        
        # Check if user has admin access to the tenant
        if not TenantUser.objects.filter(
            tenant=instance.tenant, user=self.request.user,
            role__in=['owner', 'admin'], is_active=True
        ).exists() and not self.request.user.is_superuser:
            raise permissions.PermissionDenied(
                "You don't have permission to manage users for this tenant."
            )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete by setting is_active to False."""
        instance.is_active = False
        instance.save()
