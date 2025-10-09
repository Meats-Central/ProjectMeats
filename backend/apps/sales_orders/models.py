"""
Sales Orders models for ProjectMeats.

Defines sales order entities and related business logic.
"""
from django.db import models
from apps.core.models import (
    TimestampModel,
    TenantManager,
    WeightUnitChoices,
)
from apps.tenants.models import Tenant


class SalesOrderStatus(models.TextChoices):
    """Status choices for sales orders."""

    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    IN_TRANSIT = "in_transit", "In Transit"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class SalesOrder(TimestampModel):
    """Sales Order model for managing customer sales orders."""

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="sales_orders",
        help_text="Tenant that owns this sales order",
        null=True,
        blank=True,
    )

    # Order identification
    our_sales_order_num = models.CharField(
        max_length=100,
        unique=True,
        help_text="Our sales order number",
    )
    date_time_stamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when SO was created",
    )
    
    # Related entities
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        help_text="Supplier for this sales order",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        help_text="Customer for this sales order",
    )
    carrier = models.ForeignKey(
        "carriers.Carrier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Carrier for this sales order",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Product being sold",
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
    
    # Dates
    pick_up_date = models.DateField(
        blank=True,
        null=True,
        help_text="Scheduled pick up date",
    )
    delivery_date = models.DateField(
        blank=True,
        null=True,
        help_text="Scheduled delivery date",
    )
    
    # Order details
    delivery_po_num = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Delivery PO number",
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
    
    # Status and pricing
    status = models.CharField(
        max_length=20,
        choices=SalesOrderStatus.choices,
        default=SalesOrderStatus.PENDING,
        help_text="Current status of the sales order",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Total order amount",
    )
    notes = models.TextField(
        blank=True,
        default='',
        help_text="Additional notes",
    )

    # Custom manager for tenant filtering
    objects = TenantManager()

    class Meta:
        ordering = ["-date_time_stamp", "-created_on"]
        verbose_name = "Sales Order"
        verbose_name_plural = "Sales Orders"

    def __str__(self):
        return f"SO-{self.our_sales_order_num}"

