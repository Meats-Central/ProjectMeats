from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import secrets


class Tenant(models.Model):
    """
    Tenant model for multi-tenancy support.
    Uses shared database, shared schema approach with tenant_id for isolation.
    """

    # Basic tenant information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Tenant organization name")
    slug = models.SlugField(
        max_length=100, unique=True, help_text="URL-friendly identifier"
    )

    # Contact information
    domain = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Custom domain for the tenant (optional)",
    )
    contact_email = models.EmailField(help_text="Primary contact email")
    contact_phone = models.CharField(max_length=20, blank=True, default='')

    # Status and configuration
    is_active = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who created this tenant",
    )

    # Configuration (JSON field for settings)
    settings = models.JSONField(
        default=dict, help_text="Tenant-specific configuration settings"
    )

    class Meta:
        db_table = "tenants_tenant"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.slug})"

    @property
    def is_trial_expired(self):
        """Check if trial period has expired."""
        if not self.is_trial or not self.trial_ends_at:
            return False
        from django.utils import timezone

        return timezone.now() > self.trial_ends_at

    def save(self, *args, **kwargs):
        """Override save to ensure slug is always lowercase."""
        if self.slug:
            self.slug = self.slug.lower()
        super().save(*args, **kwargs)


class TenantUser(models.Model):
    """
    Association between Users and Tenants with role information.
    Users can belong to multiple tenants with different roles.
    """

    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Administrator"),
        ("manager", "Manager"),
        ("user", "User"),
        ("readonly", "Read Only"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="users")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tenants")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="user")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants_tenant_user"
        unique_together = ["tenant", "user"]
        indexes = [
            models.Index(fields=["tenant", "is_active"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        return f"{self.user.username} @ {self.tenant.slug} ({self.role})"


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
        Tenant,
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
