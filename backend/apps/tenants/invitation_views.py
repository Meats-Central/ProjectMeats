"""
Views for tenant invitation system.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from typing import Any, Type
from rest_framework.serializers import Serializer
from django.db.models import QuerySet
import logging

from apps.tenants.models import Tenant, TenantUser, TenantInvitation
from apps.tenants.invitation_serializers import (
    TenantInvitationCreateSerializer,
    TenantInvitationListSerializer,
    TenantInvitationDetailSerializer,
    InvitationSignupSerializer
)
from apps.tenants.email_utils import send_invitation_email

logger = logging.getLogger(__name__)


class TenantInvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenant invitations.
    
    Only tenant admins/owners can create and manage invitations.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self) -> QuerySet[TenantInvitation]:
        """
        Return invitations for user's tenant(s).
        
        Admins/Owners see all invitations for their tenants.
        Regular users see only their own invitations (if any).
        """
        user = self.request.user
        
        # Get user's tenants where they are admin or owner
        admin_tenants = TenantUser.objects.filter(
            user=user,
            role__in=['admin', 'owner'],
            is_active=True
        ).values_list('tenant_id', flat=True)
        
        if admin_tenants:
            # Admin/Owner: see all invitations for their tenants
            return TenantInvitation.objects.filter(tenant_id__in=admin_tenants)
        
        # Regular user: see only invitations they sent (if they invited someone)
        return TenantInvitation.objects.filter(invited_by=user)
    
    def get_serializer_class(self) -> Type[Serializer]:
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return TenantInvitationCreateSerializer
        elif self.action == 'list':
            return TenantInvitationListSerializer
        return TenantInvitationDetailSerializer
    
    def get_serializer_context(self) -> dict[str, Any]:
        """Add tenant to serializer context."""
        context = super().get_serializer_context()
        
        # Try to get tenant from request (added by middleware)
        if hasattr(self.request, 'tenant') and getattr(self.request, 'tenant', None):  # type: ignore
            context['tenant'] = getattr(self.request, 'tenant')  # type: ignore
        # Or from user's default tenant (first admin/owner tenant)
        else:
            tenant_user = TenantUser.objects.filter(
                user=self.request.user,
                role__in=['admin', 'owner'],
                is_active=True
            ).select_related('tenant').first()
            if tenant_user:
                context['tenant'] = tenant_user.tenant
        
        return context
    
    def create(self, request, *args, **kwargs):
        """
        Create a new invitation.
        
        Only admins/owners can create invitations.
        """
        # Check if user is admin/owner of any tenant
        tenant = self.get_serializer_context().get('tenant')
        if not tenant:
            return Response(
                {'error': 'You must be an admin or owner of a tenant to invite users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify user is admin/owner of this tenant
        tenant_user = TenantUser.objects.filter(
            tenant=tenant,
            user=request.user,
            role__in=['admin', 'owner'],
            is_active=True
        ).first()
        
        if not tenant_user:
            return Response(
                {'error': 'You do not have permission to invite users to this tenant'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Save the invitation and send email notification."""
        invitation = serializer.save()
        
        # Send email notification
        try:
            send_invitation_email(invitation)
        except Exception as e:
            logger.error(f"Failed to send invitation email: {str(e)}", exc_info=True)
            # Don't fail the request if email fails
    
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend an invitation email (updates expiration and sends email)."""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response(
                {'error': 'Can only resend pending invitations'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extend expiration by 7 days
        from django.utils import timezone
        invitation.expires_at = timezone.now() + timezone.timedelta(days=7)
        invitation.save()
        
        # Send email notification
        try:
            send_invitation_email(invitation)
            logger.info(f"Resent invitation {invitation.id} to {invitation.email}")
        except Exception as e:
            logger.error(f"Failed to send invitation email on resend: {str(e)}", exc_info=True)
            # Don't fail the request if email fails, but inform the user
            serializer = self.get_serializer(invitation)
            response_data = serializer.data
            response_data['warning'] = 'Invitation expiration updated, but email notification failed to send'
            return Response(response_data)
        
        serializer = self.get_serializer(invitation)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke an invitation."""
        invitation = self.get_object()
        
        try:
            invitation.revoke()
            return Response({'status': 'Invitation revoked'})
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_with_invitation(request):
    """
    User signup endpoint that requires an invitation token.
    
    This replaces the open signup and ensures all users are tied to a tenant.
    """
    serializer = InvitationSignupSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            result = serializer.save()
            
            # Extract values from result dictionary
            user_obj = result.get('user')  # type: ignore
            tenant_obj = result.get('tenant')  # type: ignore
            token_obj = result.get('token')  # type: ignore
            tenant_user_obj = result.get('tenant_user')  # type: ignore
            
            logger.info(
                f"User {user_obj.username} created via invitation "  # type: ignore
                f"for tenant {tenant_obj.name}"  # type: ignore
            )
            
            return Response(
                {
                    'token': token_obj,  # type: ignore
                    'user': {
                        'id': user_obj.id,  # type: ignore
                        'username': user_obj.username,  # type: ignore
                        'email': user_obj.email,  # type: ignore
                        'first_name': user_obj.first_name,  # type: ignore
                        'last_name': user_obj.last_name,  # type: ignore
                    },
                    'tenant': {
                        'id': str(tenant_obj.id),  # type: ignore
                        'name': tenant_obj.name,  # type: ignore
                        'slug': tenant_obj.slug,  # type: ignore
                    },
                    'role': tenant_user_obj.role,  # type: ignore
                },
                status=status.HTTP_201_CREATED
            )
    
    except Exception as e:
        logger.error(f"Error in invitation signup: {str(e)}", exc_info=True)
        return Response(
            {'error': 'Failed to create user account'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def validate_invitation(request):
    """
    Validate an invitation token without accepting it.
    
    Useful for frontend to show invitation details before signup.
    """
    token = request.query_params.get('token')
    
    if not token:
        return Response(
            {'error': 'Token parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        invitation = TenantInvitation.objects.select_related('tenant').get(token=token)
    except TenantInvitation.DoesNotExist:
        return Response(
            {'error': 'Invalid invitation token'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check status
    if invitation.status == 'accepted':
        return Response(
            {'error': 'This invitation has already been accepted'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if invitation.is_expired:
        invitation.status = 'expired'
        invitation.save()
        return Response(
            {'error': 'This invitation has expired'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if invitation.status == 'revoked':
        return Response(
            {'error': 'This invitation has been revoked'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Return invitation details
    return Response({
        'valid': True,
        'email': invitation.email,
        'role': invitation.role,
        'tenant': {
            'name': invitation.tenant.name,
            'slug': invitation.tenant.slug,
        },
        'message': invitation.message,
        'expires_at': invitation.expires_at,
    })
