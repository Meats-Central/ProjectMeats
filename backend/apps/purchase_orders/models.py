"""
Purchase Orders models for ProjectMeats.

Defines purchase order entities and related business logic.
"""
from django.db import models
from apps.core.models import TimestampModel


class PurchaseOrderStatus(models.TextChoices):
    """Status choices for purchase orders."""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class PurchaseOrder(TimestampModel):
    """Purchase Order model for managing purchase orders."""

    order_number = models.CharField(
        max_length=50, unique=True, help_text="Unique order number"
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        help_text="Supplier for this purchase order",
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Total order amount"
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

    class Meta:
        ordering = ["-order_date", "-created_on"]
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"

    def __str__(self):
        return f"PO-{self.order_number}"
