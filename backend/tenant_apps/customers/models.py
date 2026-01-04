"""
Customers models for ProjectMeats.

Defines customer entities and related business logic.

Implements tenant ForeignKey field for shared-schema multi-tenancy.
"""
from django.db import models

from apps.tenants.models import Tenant
from tenant_apps.contacts.models import Contact
from apps.core.models import (
    AccountingPaymentTermsChoices,
    AccountLineOfCreditChoices,
    CertificateTypeChoices,
    CreditLimitChoices,
    EdibleInedibleChoices,
    IndustryChoices,
    OriginChoices,
    Protein,
    TimestampModel,
    TenantManager,
)
from tenant_apps.plants.models import Plant


class Customer(TimestampModel):
    """Customer model for managing customer information."""
    # Use custom manager for multi-tenancy
    objects = TenantManager()

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="customers",
        help_text="Tenant this customer belongs to"
    )

    # Basic information - keeping existing fields with same names
    name = models.CharField(max_length=255, help_text="Customer company name")
    contact_person = models.CharField(
        max_length=255, blank=True, null=True, help_text="Primary contact person name"
    )
    email = models.EmailField(blank=True, null=True, help_text="Primary contact email")
    phone = models.CharField(
        max_length=20, blank=True, null=True, help_text="Primary contact phone number"
    )

    # Address fields - keeping existing structure but adding street_address for clarity
    address = models.TextField(blank=True, null=True, help_text="Customer address")
    street_address = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Street address (alternative to address field)",
    )
    city = models.CharField(max_length=100, blank=True, null=True, help_text="City")
    state = models.CharField(
        max_length=100, blank=True, null=True, help_text="State or province"
    )
    zip_code = models.CharField(
        max_length=20, blank=True, null=True, help_text="ZIP or postal code"
    )
    country = models.CharField(
        max_length=100, blank=True, null=True, help_text="Country"
    )

    # New enhanced fields based on spreadsheet requirements
    plant = models.ForeignKey(
        Plant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Associated plant establishment",
    )
    proteins = models.ManyToManyField(
        Protein, blank=True, help_text="Protein types handled by this customer"
    )
    edible_inedible = models.CharField(
        max_length=50,
        choices=EdibleInedibleChoices.choices,
        blank=True,
        default='',
        help_text="Type of products handled",
    )
    type_of_plant = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Customer type of plant (e.g., Vertical, Processor)",
    )
    purchasing_preference_origin = models.CharField(
        max_length=100,
        choices=OriginChoices.choices,
        blank=True,
        default='',
        help_text="Purchasing preference origin (e.g., Domestic, Imported)",
    )
    industry = models.CharField(
        max_length=100,
        choices=IndustryChoices.choices,
        blank=True,
        default='',
        help_text="Industry sector (e.g., Pet Sector, Retail)",
    )
    contacts = models.ManyToManyField(
        Contact,
        related_name="customers",
        blank=True,
        help_text="Multiple contacts associated with this customer",
    )
    will_pickup_load = models.BooleanField(
        default=False, help_text="Will customer pickup load?"
    )
    
    # Enhanced payment/credit fields with standardized choices
    accounting_payment_terms = models.CharField(
        max_length=50,
        choices=AccountingPaymentTermsChoices.choices,
        blank=True,
        default='',
        help_text="Payment terms (e.g., Wire, ACH, Check)",
    )
    credit_limits = models.CharField(
        max_length=50,
        choices=CreditLimitChoices.choices,
        blank=True,
        default='',
        help_text="Credit limits/terms (e.g., Net 30, Wire 1 day prior)",
    )
    account_line_of_credit = models.CharField(
        max_length=50,
        choices=AccountLineOfCreditChoices.choices,
        blank=True,
        default='',
        help_text="Line of credit amount range",
    )
    
    # Additional buyer contact fields
    buyer_contact_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Buyer contact name",
    )
    contact_title = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="e.g., Vice President, Buyer",
    )
    buyer_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        default='',
        help_text="Buyer contact phone",
    )
    buyer_contact_email = models.EmailField(
        blank=True,
        default='',
        help_text="Buyer contact email",
    )
    
    type_of_certificate = models.CharField(
        max_length=100,
        choices=CertificateTypeChoices.choices,
        blank=True,
        default='',
        help_text="Certificate type required (e.g., 3rd Party, BRC)",
    )
    product_exportable = models.BooleanField(
        default=False,
        help_text="Does customer require exportable products?",
    )
    
    # Deprecated fields - keeping for backward compatibility
    accounting_terms = models.CharField(
        max_length=100, blank=True, default='', help_text="Accounting terms (deprecated, use accounting_payment_terms)"
    )
    accounting_line_of_credit = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Line of credit amount (deprecated, use account_line_of_credit)",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        indexes = [
            models.Index(fields=['tenant', 'name']),
        ]

    def __str__(self):
        return self.name
