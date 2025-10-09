"""
Purchase Orders models for ProjectMeats.

Defines purchase order entities and related business logic.
"""
from decimal import Decimal
from django.db import models
from apps.core.models import (
    TimestampModel,
    TenantManager,
    WeightUnitChoices,
    AppointmentMethodChoices,
)
from apps.tenants.models import Tenant


class PurchaseOrderStatus(models.TextChoices):
    """Status choices for purchase orders."""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class PurchaseOrder(TimestampModel):
    """Purchase Order model for managing purchase orders."""

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="purchase_orders",
        help_text="Tenant that owns this purchase order",
        null=True,
        blank=True,
    )

    order_number = models.CharField(
        max_length=50, unique=True, help_text="Unique order number"
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        help_text="Supplier for this purchase order",
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Total order amount"
    )
    status = models.CharField(
        max_length=20,
        choices=PurchaseOrderStatus.choices,
        default=PurchaseOrderStatus.PENDING,
        help_text="Current status of the purchase order",
    )
    order_date = models.DateField(help_text="Date the order was placed")
    delivery_date = models.DateField(
        blank=True, null=True, help_text="Expected delivery date"
    )
    notes = models.TextField(blank=True, null=True, help_text="Additional notes")
    
    # Enhanced fields from Excel requirements
    date_time_stamp = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        help_text="Date and time when PO was created",
    )
    pick_up_date = models.DateField(
        blank=True,
        null=True,
        help_text="Scheduled pick up date",
    )
    our_purchase_order_num = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Our internal purchase order number",
    )
    supplier_confirmation_order_num = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Supplier's confirmation order number",
    )
    carrier = models.ForeignKey(
        "carriers.Carrier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Carrier for this purchase order",
    )
    carrier_release_format = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Carrier release format",
    )
    carrier_release_num = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Carrier release number",
    )
    quantity = models.IntegerField(
        blank=True,
        null=True,
        help_text="Quantity of items",
    )
    total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Total weight",
    )
    weight_unit = models.CharField(
        max_length=10,
        choices=WeightUnitChoices.choices,
        default=WeightUnitChoices.LBS,
        help_text="Unit of weight (LBS or KG)",
    )
    how_carrier_make_appointment = models.CharField(
        max_length=50,
        choices=AppointmentMethodChoices.choices,
        blank=True,
        default='',
        help_text="How carrier makes appointments",
    )
    plant = models.ForeignKey(
        "plants.Plant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Plant/facility for this order",
    )
    contact = models.ForeignKey(
        "contacts.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Primary contact for this order",
    )

    # Custom manager for tenant filtering
    objects = TenantManager()

    class Meta:
        ordering = ["-order_date", "-created_on"]
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"

    def __str__(self):
        return f"PO-{self.order_number}"
