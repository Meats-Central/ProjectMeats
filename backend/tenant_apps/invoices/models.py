"""
Invoices models for ProjectMeats.

Defines invoice entities and related business logic.

Implements tenant ForeignKey field for shared-schema multi-tenancy.
"""
from decimal import Decimal
from django.db import models
from apps.tenants.models import Tenant
from apps.core.models import (
    AccountingPaymentTermsChoices,
    EdibleInedibleChoices,
    ProteinTypeChoices,
    TimestampModel,
    WeightUnitChoices,
    TenantManager,
)


class InvoiceStatus(models.TextChoices):
    """Status choices for invoices."""

    DRAFT = "draft", "Draft"
    SENT = "sent", "Sent"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    CANCELLED = "cancelled", "Cancelled"


class Invoice(TimestampModel):
    """Invoice model for customer invoices."""
    # Use custom manager for multi-tenancy
    objects = TenantManager()
    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="invoices",
        help_text="Tenant this invoice belongs to"
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
        default='',
        help_text="Our sales order number",
    )
    delivery_po_num = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Delivery PO number",
    )
    payment_terms = models.CharField(
        max_length=50,
        choices=AccountingPaymentTermsChoices.choices,
        blank=True,
        default='',
        help_text="Payment terms (e.g., Wire, ACH, Check)",
    )
    
    # Contact information
    accounting_payable_contact_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Accounting payable contact name",
    )
    accounting_payable_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text="Accounting payable contact phone",
    )
    accounting_payable_contact_email = models.EmailField(
        blank=True,
        default='',
        help_text="Accounting payable contact email",
    )
    
    # Product details
    type_of_protein = models.CharField(
        max_length=100,
        choices=ProteinTypeChoices.choices,
        blank=True,
        default='',
        help_text="Type of protein",
    )
    description_of_product_item = models.TextField(
        blank=True,
        default='',
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
        default='',
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
        default=Decimal('0.00'),
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
        default='',
        help_text="Additional notes",
    )
    class Meta:
        ordering = ["-date_time_stamp", "-created_on"]
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        indexes = [
            models.Index(fields=['tenant', 'invoice_number']),
            models.Index(fields=['tenant', 'status']),
        ]

    def __str__(self):
        return f"INV-{self.invoice_number}"


class ClaimType(models.TextChoices):
    """Type of claim (Payable or Receivable)."""
    PAYABLE = "payable", "Payable (Supplier Claim)"
    RECEIVABLE = "receivable", "Receivable (Customer Claim)"


class ClaimStatus(models.TextChoices):
    """Status choices for claims."""
    PENDING = "pending", "Pending Review"
    APPROVED = "approved", "Approved"
    DENIED = "denied", "Denied"
    SETTLED = "settled", "Settled/Paid"
    CANCELLED = "cancelled", "Cancelled"


class Claim(TimestampModel):
    """
    Claim model for tracking disputes and financial claims.
    
    Handles both:
    - Payables: Claims against suppliers (we owe them, they filed a claim)
    - Receivables: Claims against customers (they owe us, we filed a claim)
    """
    # Use custom manager for multi-tenancy
    objects = TenantManager()
    
    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="claims",
        help_text="Tenant this claim belongs to"
    )
    
    # Claim identification
    claim_number = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique claim number/reference"
    )
    claim_type = models.CharField(
        max_length=20,
        choices=ClaimType.choices,
        help_text="Is this a payable (supplier) or receivable (customer) claim?"
    )
    status = models.CharField(
        max_length=20,
        choices=ClaimStatus.choices,
        default=ClaimStatus.PENDING,
        help_text="Current status of the claim"
    )
    
    # Related entities
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claims",
        help_text="Related supplier (for payable claims)"
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claims",
        help_text="Related customer (for receivable claims)"
    )
    purchase_order = models.ForeignKey(
        "purchase_orders.PurchaseOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claims",
        help_text="Related purchase order"
    )
    sales_order = models.ForeignKey(
        "sales_orders.SalesOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claims",
        help_text="Related sales order"
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claims",
        help_text="Related invoice"
    )
    
    # Claim details
    reason = models.TextField(
        help_text="Reason for the claim (e.g., damaged goods, incorrect quantity, quality issue)"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Detailed description of the claim"
    )
    
    # Financial
    claimed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Amount being claimed"
    )
    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Approved amount (may differ from claimed)"
    )
    settled_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual amount paid/settled"
    )
    
    # Dates
    claim_date = models.DateField(
        help_text="Date claim was filed"
    )
    resolution_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date claim was resolved/settled"
    )
    
    # Resolution
    resolution_notes = models.TextField(
        blank=True,
        default='',
        help_text="Notes on how claim was resolved"
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_claims",
        help_text="User assigned to handle this claim"
    )
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_claims",
        help_text="User who filed this claim"
    )
    
    class Meta:
        ordering = ["-claim_date", "-created_on"]
        verbose_name = "Claim"
        verbose_name_plural = "Claims"
        indexes = [
            models.Index(fields=['tenant', 'claim_type', 'status']),
            models.Index(fields=['tenant', 'claim_number']),
            models.Index(fields=['tenant', '-claim_date']),
        ]
    
    def __str__(self):
        return f"Claim #{self.claim_number} ({self.get_claim_type_display()}) - {self.get_status_display()}"


