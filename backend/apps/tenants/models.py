from django.db import models
from django.contrib.auth.models import User
import uuid


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
    contact_phone = models.CharField(max_length=20, blank=True)

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
