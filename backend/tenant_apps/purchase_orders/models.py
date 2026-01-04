"""
Purchase Orders models for ProjectMeats.

Defines purchase order entities and related business logic.

Implements tenant ForeignKey field for shared-schema multi-tenancy.
"""
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.tenants.models import Tenant
from apps.core.models import (
    AccountingPaymentTermsChoices,
    AppointmentMethodChoices,
    CarrierReleaseFormatChoices,
    CreditLimitChoices,
    EdibleInedibleChoices,
    FreshOrFrozenChoices,
    NetOrCatchChoices,
    PackageTypeChoices,
    ProteinTypeChoices,
    TimestampModel,
    WeightUnitChoices,
    TenantManager,
)


class PurchaseOrderStatus(models.TextChoices):
    """Status choices for purchase orders."""

    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


class PurchaseOrder(TimestampModel):
    """Purchase Order model for managing purchase orders."""
    # Use custom manager for multi-tenancy
    objects = TenantManager()

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="purchase_orders",
        help_text="Tenant this purchase order belongs to"
    )

    order_number = models.CharField(max_length=50, unique=True, help_text="Unique order number")
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        help_text="Supplier for this purchase order",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Product being purchased",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Total Amount ($)",
        help_text="Total order amount",
    )
    status = models.CharField(
        max_length=20,
        choices=PurchaseOrderStatus.choices,
        default=PurchaseOrderStatus.PENDING,
        help_text="Current status of the purchase order",
    )
    order_date = models.DateField(help_text="Date the order was placed")
    delivery_date = models.DateField(blank=True, null=True, help_text="Expected delivery date")
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
        choices=CarrierReleaseFormatChoices.choices,
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
        verbose_name="Quantity",
        help_text="Quantity of items",
    )
    total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Total Weight (LBS)",
        help_text="Total weight",
    )
    weight_unit = models.CharField(
        max_length=10,
        choices=WeightUnitChoices.choices,
        default=WeightUnitChoices.LBS,
        verbose_name="Weight Unit",
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
    class Meta:
        ordering = ["-order_date", "-created_on"]
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        indexes = [
            models.Index(fields=['tenant', 'order_number']),
            models.Index(fields=['tenant', 'order_date']),
        ]

    def __str__(self):
        return f"PO-{self.order_number}"


class CarrierPurchaseOrder(TimestampModel):
    """Carrier Purchase Order model for managing carrier-specific purchase orders."""
    # Use custom manager for multi-tenancy
    objects = TenantManager()
    
    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="carrier_purchase_orders",
        help_text="Tenant this carrier purchase order belongs to"
    )

    # Generated timestamp
    date_time_stamp_created = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when carrier PO was created",
    )

    # Related entities
    carrier = models.ForeignKey(
        "carriers.Carrier",
        on_delete=models.CASCADE,
        help_text="Carrier for this purchase order",
    )
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        help_text="Supplier for this carrier purchase order",
    )
    plant = models.ForeignKey(
        "plants.Plant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Plant/facility for this order",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Product being ordered",
    )
    
    # CRITICAL: Logistics Bridge - Links CarrierPO to SupplierPO
    # This field answers "Who is hauling this meat?" directly from the Supplier PO
    linked_order = models.ForeignKey(
        "PurchaseOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carrier_logistics",
        help_text="Link to the associated Supplier Purchase Order (SupplierPO). "
                  "This creates the logistics bridge to track which carrier is hauling which supplier order."
    )
    
    # Logistics Bridge - Links CarrierPO to SalesOrder for tracking via Sales Order Number
    sales_order = models.ForeignKey(
        "sales_orders.SalesOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carrier_logistics",
        help_text="Link to the associated Sales Order for logistics tracking via Sales Order Number (spreadsheet #7)."
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
    our_carrier_po_num = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Our carrier purchase order number",
    )
    carrier_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Carrier company name",
    )

    # Payment and credit information
    payment_terms = models.CharField(
        max_length=50,
        choices=AccountingPaymentTermsChoices.choices,
        blank=True,
        default="",
        help_text="Payment terms (e.g., Wire, ACH, Check)",
    )
    credit_limits = models.CharField(
        max_length=50,
        choices=CreditLimitChoices.choices,
        blank=True,
        default="",
        help_text="Credit limits/terms",
    )

    # Product details
    type_of_protein = models.CharField(
        max_length=50,
        choices=ProteinTypeChoices.choices,
        blank=True,
        default="",
        help_text="Type of protein",
    )
    fresh_or_frozen = models.CharField(
        max_length=20,
        choices=FreshOrFrozenChoices.choices,
        blank=True,
        default="",
        help_text="Product state (Fresh or Frozen)",
    )
    package_type = models.CharField(
        max_length=50,
        choices=PackageTypeChoices.choices,
        blank=True,
        default="",
        help_text="Package type",
    )
    net_or_catch = models.CharField(
        max_length=20,
        choices=NetOrCatchChoices.choices,
        blank=True,
        default="",
        help_text="Weight type (Net or Catch)",
    )
    edible_or_inedible = models.CharField(
        max_length=50,
        choices=EdibleInedibleChoices.choices,
        blank=True,
        default="",
        help_text="Edible or inedible product",
    )

    # Weight and quantity
    total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Total Weight (LBS)",
        help_text="Total weight",
    )
    weight_unit = models.CharField(
        max_length=10,
        choices=WeightUnitChoices.choices,
        default=WeightUnitChoices.LBS,
        verbose_name="Weight Unit",
        help_text="Unit of weight (LBS or KG)",
    )
    quantity = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="Quantity",
        help_text="Quantity of items",
    )

    # Carrier appointment details
    how_carrier_make_appointment = models.CharField(
        max_length=50,
        choices=AppointmentMethodChoices.choices,
        blank=True,
        default="",
        help_text="How carrier makes appointments",
    )
    departments_of_carrier = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Departments (comma-separated: BOL, COA, POD, etc.)",
    )
    class Meta:
        ordering = ["-date_time_stamp_created", "-created_on"]
        verbose_name = "Carrier Purchase Order"
        verbose_name_plural = "Carrier Purchase Orders"
        indexes = [
            models.Index(fields=['tenant', 'our_carrier_po_num']),
        ]

    def __str__(self):
        return f"Carrier PO-{self.our_carrier_po_num or self.id}"


class ColdStorageEntry(TimestampModel):
    """Cold Storage Entry model for tracking boxing and cold storage operations."""
    # Use custom manager for multi-tenancy
    objects = TenantManager()

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="cold_storage_entries",
        help_text="Tenant this cold storage entry belongs to"
    )

    # Generated timestamp
    date_time_stamp_created = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when entry was created",
    )

    # Related entities
    supplier_po = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cold_storage_entries",
        help_text="Related supplier purchase order",
    )
    customer_sales_order = models.ForeignKey(
        "sales_orders.SalesOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cold_storage_entries",
        help_text="Related customer sales order",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Product being stored",
    )

    # Status and dates
    status_of_load = models.CharField(
        max_length=50,
        choices=[("Matched", "Matched"), ("TBD - Not Matched", "TBD - Not Matched")],
        blank=True,
        default="",
        help_text="Load matching status",
    )
    item_production_date = models.DateField(
        blank=True,
        null=True,
        help_text="Item production date",
    )

    # Product details
    item_description = models.TextField(
        blank=True,
        default="",
        help_text="Description of item (e.g., 50% Beef Trim fresh - Tested)",
    )

    # Boxing fields (conditional based on status)
    finished_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Finished weight after boxing",
    )
    shrink = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Shrink amount",
    )
    boxing_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Cost of boxing",
    )

    # Cold storage costs
    cold_storage_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Cost of cold storage",
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Total cost (boxing + cold storage)",
    )

    notes = models.TextField(
        blank=True,
        default="",
        help_text="Additional notes",
    )
    class Meta:
        ordering = ["-date_time_stamp_created", "-created_on"]
        verbose_name = "Cold Storage Entry"
        verbose_name_plural = "Cold Storage Entries"
        indexes = [
            models.Index(fields=['tenant', 'date_time_stamp_created']),
        ]

    def __str__(self):
        return f"Cold Storage Entry-{self.id} ({self.status_of_load})"


class PurchaseOrderHistory(TimestampModel):
    """Version history for Purchase Order modifications."""
    # Use custom manager for multi-tenancy
    objects = TenantManager()

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="purchase_order_histories",
        help_text="Tenant this history entry belongs to"
    )

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
        tenant=instance.tenant,  # Inherit tenant from parent PurchaseOrder
        changed_data=changed_data,
        changed_by=user,
        change_type=change_type,
    )
