"""
Tenant invitation models for invite-only user creation.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import secrets


class TenantInvitation(models.Model):
    """
    Invitation model for invite-only user registration.
    
    Tenants can invite users via email. Users must use the invitation
    token to complete signup, ensuring all users are tied to a tenant.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Administrator"),
        ("manager", "Manager"),
        ("user", "User"),
        ("readonly", "Read Only"),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(
        max_length=64,
        unique=True,
        help_text="Unique invitation token sent to invitee"
    )
    
    # Invitation details
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.CASCADE,
        related_name='invitations',
        help_text="Tenant extending the invitation"
    )
    email = models.EmailField(
        help_text="Email address of the person being invited"
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text="Role the user will have upon acceptance"
    )
    
    # Who created the invitation
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sent_invitations',
        help_text="User who sent this invitation"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        help_text="When this invitation expires"
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    # User who accepted (if accepted)
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accepted_invitations',
        help_text="User created from this invitation"
    )
    
    # Optional personal message
    message = models.TextField(
        blank=True,
        help_text="Optional message from inviter"
    )
    
    class Meta:
        db_table = "tenants_invitation"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['email', 'status']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['expires_at']),
        ]
        # Prevent duplicate pending invitations for same email in same tenant
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'email'],
                condition=models.Q(status='pending'),
                name='unique_pending_invitation_per_tenant_email'
            )
        ]
    
    def __str__(self):
        return f"Invitation for {self.email} to {self.tenant.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Generate token and set expiration if not set."""
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        
        if not self.expires_at:
            # Default: 7 days expiration
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if invitation has expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if invitation is valid (pending and not expired)."""
        return self.status == 'pending' and not self.is_expired
    
    def accept(self, user):
        """
        Mark invitation as accepted by a user.
        
        Args:
            user: The User instance that accepted the invitation
        """
        if not self.is_valid:
            raise ValueError("Invitation is not valid")
        
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.accepted_by = user
        self.save()
    
    def revoke(self):
        """Revoke the invitation."""
        if self.status == 'accepted':
            raise ValueError("Cannot revoke an accepted invitation")
        
        self.status = 'revoked'
        self.save()
    
    def check_and_update_expiration(self):
        """Check if expired and update status if needed."""
        if self.status == 'pending' and self.is_expired:
            self.status = 'expired'
            self.save()
            return True
        return False
