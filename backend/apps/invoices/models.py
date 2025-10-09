"""
Invoices models for ProjectMeats.

Defines invoice entities and related business logic.
"""
from django.db import models
from apps.core.models import (
    EdibleInedibleChoices,
    TimestampModel,
    TenantManager,
    WeightUnitChoices,
)
from apps.tenants.models import Tenant


class InvoiceStatus(models.TextChoices):
    """Status choices for invoices."""

    DRAFT = "draft", "Draft"
    SENT = "sent", "Sent"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"


class Invoice(TimestampModel):
    """Invoice model for customer invoices."""

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="invoices",
        help_text="Tenant that owns this invoice",
        null=True,
        blank=True,
    )

    # Invoice identification
    invoice_number = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique invoice number",
    )
    date_time_stamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when invoice was created",
    )
    
    # Related entities
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.CASCADE,
        help_text="Customer for this invoice",
    )
    sales_order = models.ForeignKey(
        "sales_orders.SalesOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Related sales order",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Product being invoiced",
    )
    
    # Dates
    pick_up_date = models.DateField(
        blank=True,
        null=True,
        help_text="Pick up date",
    )
    delivery_date = models.DateField(
        blank=True,
        null=True,
        help_text="Delivery date",
    )
    due_date = models.DateField(
        blank=True,
        null=True,
        help_text="Payment due date",
    )
    
    # Order references
    our_sales_order_num = models.CharField(
        max_length=100,
        blank=True,
        help_text="Our sales order number",
    )
    delivery_po_num = models.CharField(
        max_length=100,
        blank=True,
        help_text="Delivery PO number",
    )
    
    # Contact information
    accounting_payable_contact_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Accounting payable contact name",
    )
    accounting_payable_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Accounting payable contact phone",
    )
    accounting_payable_contact_email = models.EmailField(
        blank=True,
        help_text="Accounting payable contact email",
    )
    
    # Product details
    type_of_protein = models.CharField(
        max_length=100,
        blank=True,
        help_text="Type of protein",
    )
    description_of_product_item = models.TextField(
        blank=True,
        help_text="Description of product item",
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
    edible_or_inedible = models.CharField(
        max_length=50,
        choices=EdibleInedibleChoices.choices,
        blank=True,
        help_text="Edible or inedible product",
    )
    tested_product = models.BooleanField(
        default=False,
        help_text="Is this a tested product?",
    )
    
    # Financial details
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Price per unit",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total invoice amount",
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Tax amount",
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        help_text="Current status of the invoice",
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional notes",
    )

    # Custom manager for tenant filtering
    objects = TenantManager()

    class Meta:
        ordering = ["-date_time_stamp", "-created_on"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self):
        return f"INV-{self.invoice_number}"

