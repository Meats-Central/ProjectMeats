from django.db import models
from django.contrib.auth.models import User
from apps.tenants.models import Tenant
from apps.core.models import TenantManager


class Plant(models.Model):
    PLANT_TYPE_CHOICES = [
        ("processing", "Processing Plant"),
        ("distribution", "Distribution Center"),
        ("warehouse", "Warehouse"),
        ("retail", "Retail Location"),
        ("other", "Other"),
    ]

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="plants",
        help_text="Tenant that owns this plant",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    plant_est_num = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Plant establishment number",
    )
    plant_type = models.CharField(
        max_length=20, choices=PLANT_TYPE_CHOICES, default="processing"
    )
    address = models.TextField(default='')
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')
    zip_code = models.CharField(max_length=20, default='')
    country = models.CharField(max_length=100, default="USA")
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    manager = models.CharField(max_length=100, blank=True, default='')
    capacity = models.PositiveIntegerField(
        help_text="Capacity in units", null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Custom manager for tenant filtering
    objects = TenantManager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Plant"
        verbose_name_plural = "Plants"

    def __str__(self):
        return f"{self.code} - {self.name}"
