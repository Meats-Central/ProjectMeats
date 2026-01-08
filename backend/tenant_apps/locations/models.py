"""
Locations models for ProjectMeats.

Defines location entities for suppliers and customers.

Implements tenant ForeignKey field for shared-schema multi-tenancy.
Row-level security (RLS) enabled for additional isolation at PostgreSQL level.
"""
from django.db import models

from apps.tenants.models import Tenant
from apps.core.models import (
    AppointmentMethodChoices,
    TenantManager,
    TimestampModel,
)


class Location(TimestampModel):
    """Location model for supplier and customer addresses."""

    # Use the custom TenantManager to support .for_tenant() queries
    objects = TenantManager()

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="locations",
        help_text="Tenant this location belongs to"
    )

    # Basic information
    name = models.CharField(
        max_length=255,
        help_text="Location name or identifier"
    )
    address = models.TextField(
        blank=True,
        default='',
        help_text="Full street address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="City"
    )
    state_zip = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="State and ZIP code"
    )

    # Contact information
    contact_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Contact person name"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text="Contact phone number"
    )
    contact_email = models.EmailField(
        blank=True,
        default='',
        help_text="Contact email address"
    )

    # Appointment method
    how_make_appointment = models.CharField(
        max_length=50,
        choices=AppointmentMethodChoices.choices,
        blank=True,
        default='',
        help_text="How to make an appointment"
    )

    # Plant establishment number
    plant_est_number = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Plant establishment number"
    )

    # Relationships to Supplier and Customer
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locations',
        help_text="Associated supplier"
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locations',
        help_text="Associated customer"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'
        indexes = [
            models.Index(fields=['tenant', 'name']),
            models.Index(fields=['tenant', 'supplier']),
            models.Index(fields=['tenant', 'customer']),
        ]

    def __str__(self):
        return f"{self.name} ({self.city})"
