from django.db import models
from django.contrib.auth.models import User
from apps.tenants.models import Tenant
from apps.core.models import TenantManager


class Carrier(models.Model):
    CARRIER_TYPE_CHOICES = [
        ("truck", "Truck"),
        ("rail", "Rail"),
        ("air", "Air"),
        ("sea", "Sea"),
        ("other", "Other"),
    ]

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="carriers",
        help_text="Tenant that owns this carrier",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    carrier_type = models.CharField(
        max_length=20, choices=CARRIER_TYPE_CHOICES, default="truck"
    )
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="USA")
    mc_number = models.CharField(
        max_length=50, blank=True, help_text="Motor Carrier Number"
    )
    dot_number = models.CharField(
        max_length=50, blank=True, help_text="Department of Transportation Number"
    )
    insurance_provider = models.CharField(max_length=200, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Custom manager for tenant filtering
    objects = TenantManager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Carrier"
        verbose_name_plural = "Carriers"

    def __str__(self):
        return f"{self.code} - {self.name}"
