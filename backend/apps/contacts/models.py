"""
Contacts models for ProjectMeats.

Defines contact entities and related business logic.
"""
from django.db import models
from apps.core.models import TimestampModel, TenantManager
from apps.tenants.models import Tenant


class Contact(TimestampModel):
    """Contact model for managing contact information."""

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="contacts",
        help_text="Tenant that owns this contact",
        null=True,
        blank=True,
    )

    first_name = models.CharField(max_length=100, help_text="Contact's first name")
    last_name = models.CharField(max_length=100, help_text="Contact's last name")
    email = models.EmailField(blank=True, null=True, help_text="Contact email address")
    phone = models.CharField(
        max_length=20, blank=True, null=True, help_text="Contact phone number"
    )
    company = models.CharField(
        max_length=255, blank=True, null=True, help_text="Company or organization"
    )
    position = models.CharField(
        max_length=100, blank=True, null=True, help_text="Job position or title"
    )

    # Custom manager for tenant filtering
    objects = TenantManager()

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
