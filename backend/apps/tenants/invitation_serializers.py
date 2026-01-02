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
        fields = ['email', 'role', 'message', 'expires_at', 'is_reusable', 'max_uses']
        extra_kwargs = {
            'expires_at': {'required': False},
            'message': {'required': False},
            'email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'is_reusable': {'required': False},
            'max_uses': {'required': False},
        }
    
    def validate_email(self, value):
        """Ensure email doesn't already belong to a user in this tenant."""
        tenant = self.context.get('tenant')
        if not tenant:
            raise serializers.ValidationError("Tenant context is required")
        
        # Skip email validation for reusable invitations
        # (checked via initial_data to avoid needing email field to be passed)
        is_reusable = self.initial_data.get('is_reusable', False)
        if is_reusable:
            return value  # Allow None/blank for reusable
        
        # For regular invitations, email is required
        if not value:
            raise serializers.ValidationError("Email is required for non-reusable invitations")
        
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
            'is_expired_status', 'is_valid_status',
            'is_reusable', 'max_uses', 'usage_count'
        ]
        read_only_fields = (
            'id', 'email', 'role', 'status', 'message',
            'created_at', 'expires_at', 'accepted_at',
            'tenant_name', 'invited_by_username',
            'is_expired_status', 'is_valid_status',
            'is_reusable', 'max_uses', 'usage_count'
        )


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
    
    # NEW: Accept email from frontend form
    email = serializers.EmailField(
        required=True,
        help_text="User's email address"
    )
    
    def validate_invitation_token(self, value):
        """Validate that invitation exists and is valid."""
        try:
            invitation = TenantInvitation.objects.get(token=value)
        except TenantInvitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token")
        
        # Check validity (using updated model logic)
        if not invitation.is_valid:
            raise serializers.ValidationError("This invitation is no longer valid")
        
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
        invitation = self.invitation
        input_email = attrs.get('email')

        # Determine which email to use for the new account
        # If reusable: use Input Email. If 1:1: use Invite Email.
        target_email = input_email if invitation.is_reusable else invitation.email

        # 1. Validation: If 1:1, input email must match invite email (security check)
        if not invitation.is_reusable and input_email != invitation.email:
            raise serializers.ValidationError({
                'email': f"This invitation is exclusive to {invitation.email}. Please use that email or request a new invite."
            })

        # 2. Validation: Check if user already exists
        if User.objects.filter(email=target_email).exists():
            raise serializers.ValidationError({
                'email': 'A user account with this email already exists'
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
        # Use input email if reusable, otherwise enforce invite email
        email = validated_data['email'] if invitation.is_reusable else invitation.email
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=email,
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
        read_only_fields = (
            'id', 'token', 'tenant', 'email', 'role', 'invited_by', 
            'status', 'created_at', 'expires_at', 'accepted_at', 
            'accepted_by', 'message'
        )
