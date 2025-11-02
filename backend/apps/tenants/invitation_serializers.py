"""
Serializers for tenant invitation system.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from apps.tenants.models import Tenant, TenantUser, TenantInvitation


class TenantInvitationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tenant invitations."""
    
    class Meta:
        model = TenantInvitation
        fields = ['id', 'email', 'role', 'message', 'expires_at', 'token', 'status', 'created_at']
        read_only_fields = ['id', 'token', 'status', 'created_at']
        extra_kwargs = {
            'expires_at': {'required': False},
            'message': {'required': False},
        }
    
    def validate_email(self, value):
        """Ensure email doesn't already belong to a user in this tenant."""
        tenant = self.context.get('tenant')
        if not tenant:
            raise serializers.ValidationError("Tenant context is required")
        
        # Check if user with this email already exists in the tenant
        existing_user = User.objects.filter(email=value).first()
        if existing_user:
            tenant_user = TenantUser.objects.filter(
                tenant=tenant,
                user=existing_user,
                is_active=True
            ).first()
            if tenant_user:
                raise serializers.ValidationError(
                    f"User with this email is already a member of {tenant.name}"
                )
        
        # Check for pending invitation
        pending_invitation = TenantInvitation.objects.filter(
            tenant=tenant,
            email=value,
            status='pending'
        ).first()
        if pending_invitation and not pending_invitation.is_expired:
            raise serializers.ValidationError(
                "A pending invitation already exists for this email"
            )
        
        return value
    
    def create(self, validated_data):
        """Create invitation with tenant and inviter from context."""
        tenant = self.context.get('tenant')
        request = self.context.get('request')
        invited_by = request.user if request else None
        
        invitation = TenantInvitation.objects.create(
            tenant=tenant,
            invited_by=invited_by,
            **validated_data
        )
        return invitation


class TenantInvitationListSerializer(serializers.ModelSerializer):
    """Serializer for listing invitations."""
    
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    invited_by_username = serializers.CharField(source='invited_by.username', read_only=True)
    is_expired_status = serializers.BooleanField(source='is_expired', read_only=True)
    is_valid_status = serializers.BooleanField(source='is_valid', read_only=True)
    
    class Meta:
        model = TenantInvitation
        fields = [
            'id', 'email', 'role', 'status', 'message',
            'created_at', 'expires_at', 'accepted_at',
            'tenant_name', 'invited_by_username',
            'is_expired_status', 'is_valid_status'
        ]
        read_only_fields = fields


class InvitationSignupSerializer(serializers.Serializer):
    """Serializer for user signup via invitation."""
    
    invitation_token = serializers.CharField(
        max_length=64,
        help_text="Invitation token received via email"
    )
    username = serializers.CharField(
        max_length=150,
        help_text="Desired username"
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Password (minimum 8 characters)"
    )
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    
    def validate_invitation_token(self, value):
        """Validate that invitation exists and is valid."""
        try:
            invitation = TenantInvitation.objects.get(token=value)
        except TenantInvitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token")
        
        # Check if already accepted
        if invitation.status == 'accepted':
            raise serializers.ValidationError("This invitation has already been accepted")
        
        # Check if expired
        if invitation.is_expired:
            invitation.status = 'expired'
            invitation.save()
            raise serializers.ValidationError("This invitation has expired")
        
        # Check if revoked
        if invitation.status == 'revoked':
            raise serializers.ValidationError("This invitation has been revoked")
        
        # Store for later use
        self.invitation = invitation
        return value
    
    def validate_username(self, value):
        """Ensure username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate(self, attrs):
        """Additional validation."""
        # Ensure email from invitation doesn't already have a user account
        if hasattr(self, 'invitation'):
            existing_user = User.objects.filter(email=self.invitation.email).first()
            if existing_user:
                raise serializers.ValidationError({
                    'invitation_token': 'A user account with this email already exists'
                })
        return attrs
    
    def create(self, validated_data):
        """
        Create user and associate with tenant from invitation.
        
        Returns:
            dict: Contains user, token, and tenant information
        """
        from rest_framework.authtoken.models import Token
        
        invitation_token = validated_data.pop('invitation_token')
        invitation = self.invitation
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=invitation.email,  # Use email from invitation
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        
        # Create auth token
        token, _ = Token.objects.get_or_create(user=user)
        
        # Create tenant-user association with role from invitation
        tenant_user = TenantUser.objects.create(
            tenant=invitation.tenant,
            user=user,
            role=invitation.role,
            is_active=True
        )
        
        # Mark invitation as accepted
        invitation.accept(user)
        
        return {
            'user': user,
            'token': token.key,
            'tenant': invitation.tenant,
            'tenant_user': tenant_user,
        }


class TenantInvitationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for invitation viewing."""
    
    tenant = serializers.StringRelatedField()
    invited_by = serializers.StringRelatedField()
    accepted_by = serializers.StringRelatedField()
    
    class Meta:
        model = TenantInvitation
        fields = '__all__'
