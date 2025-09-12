"""
Suppliers models for ProjectMeats.

Defines supplier entities and related business logic.
"""
from django.db import models
from apps.core.models import TimestampModel


class Supplier(TimestampModel):
    """Supplier model for managing supplier information."""

    name = models.CharField(
        max_length=255,
        help_text="Supplier company name"
    )
    contact_person = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Primary contact person name"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Primary contact email"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Primary contact phone number"
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Supplier address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="State or province"
    )
    zip_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="ZIP or postal code"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Country"
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return self.name
