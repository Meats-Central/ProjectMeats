"""
Purchase Orders models for ProjectMeats.

Defines purchase order entities and related business logic.
"""
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
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
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Total order amount",
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
        default="",
        help_text="Our internal purchase order number",
    )
    supplier_confirmation_order_num = models.CharField(
        max_length=100,
        blank=True,
        default="",
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
        default="",
        help_text="Carrier release format",
    )
    carrier_release_num = models.CharField(
        max_length=100,
        blank=True,
        default="",
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
        default="",
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


class PurchaseOrderHistory(TimestampModel):
    """Version history for Purchase Order modifications."""

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="history",
        help_text="Purchase order this history entry belongs to",
    )
    changed_data = models.JSONField(
        help_text="JSON representation of changed fields and their values",
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who made the change",
    )
    change_type = models.CharField(
        max_length=20,
        choices=[
            ("created", "Created"),
            ("updated", "Updated"),
            ("deleted", "Deleted"),
        ],
        default="updated",
        help_text="Type of change made",
    )

    class Meta:
        ordering = ["-created_on"]
        verbose_name = "Purchase Order History"
        verbose_name_plural = "Purchase Order Histories"
        indexes = [
            models.Index(fields=["purchase_order", "-created_on"]),
        ]

    def __str__(self):
        return f"History for {self.purchase_order.order_number} at {self.created_on}"


@receiver(post_save, sender=PurchaseOrder)
def create_purchase_order_history(sender, instance, created, **kwargs):
    """
    Signal handler to create history entry when a PurchaseOrder is saved.

    Args:
        sender: The model class (PurchaseOrder)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new record
        **kwargs: Additional signal arguments including 'update_fields'
    """
    # Skip if this is during migration or fixture loading
    if kwargs.get("raw", False):
        return

    # Determine the user from kwargs if available
    user = kwargs.get("user", None)

    # Prepare change data
    changed_data = {}
    change_type = "created" if created else "updated"

    if created:
        # For new records, store all field values
        for field in instance._meta.fields:
            if field.name not in ["id", "created_on", "modified_on"]:
                value = getattr(instance, field.name)
                # Convert to JSON-serializable format
                if value is None:
                    changed_data[field.name] = None
                elif hasattr(value, "pk"):
                    # Foreign key - store the ID
                    changed_data[field.name] = str(value.pk)
                elif isinstance(value, Decimal):
                    changed_data[field.name] = str(value)
                elif hasattr(value, "isoformat"):
                    # Date/DateTime - store ISO format
                    changed_data[field.name] = value.isoformat()
                else:
                    changed_data[field.name] = str(value)
    else:
        # For updates, we need to track what changed
        # Since we don't have the old values in post_save, store current state
        update_fields = kwargs.get("update_fields", None)
        if update_fields:
            for field_name in update_fields:
                value = getattr(instance, field_name)
                if value is None:
                    changed_data[field_name] = None
                elif hasattr(value, "pk"):
                    changed_data[field_name] = str(value.pk)
                elif isinstance(value, Decimal):
                    changed_data[field_name] = str(value)
                elif hasattr(value, "isoformat"):
                    changed_data[field_name] = value.isoformat()
                else:
                    changed_data[field_name] = str(value)
        else:
            # If update_fields not specified, log that an update occurred
            changed_data["note"] = "Update occurred but specific fields not tracked"

    # Create history entry
    PurchaseOrderHistory.objects.create(
        purchase_order=instance,
        changed_data=changed_data,
        changed_by=user,
        change_type=change_type,
    )
