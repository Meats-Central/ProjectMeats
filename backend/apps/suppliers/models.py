"""
Suppliers models for ProjectMeats.

Defines supplier entities and related business logic.

Schema-based multi-tenancy active – tenant isolation is handled automatically by django-tenants.
Data is isolated by PostgreSQL schemas, NOT by tenant_id columns.
"""
from django.db import models

from apps.contacts.models import Contact
from apps.core.models import (
    AccountingPaymentTermsChoices,
    AccountLineOfCreditChoices,
    CertificateTypeChoices,
    CountryOriginChoices,
    CreditLimitChoices,
    EdibleInedibleChoices,
    FreshOrFrozenChoices,
    NetOrCatchChoices,
    OriginChoices,
    PackageTypeChoices,
    PlantTypeChoices,
    Protein,
    ProteinTypeChoices,
    ShippingOfferedChoices,
    TimestampModel,
)
from apps.plants.models import Plant


class Supplier(TimestampModel):
    """Supplier model for managing supplier information."""

    # Basic information - keeping existing fields with same names
    name = models.CharField(max_length=255, help_text="Supplier company name")
    contact_person = models.CharField(
        max_length=255, blank=True, null=True, help_text="Primary contact person name"
    )
    email = models.EmailField(blank=True, null=True, help_text="Primary contact email")
    phone = models.CharField(
        max_length=20, blank=True, null=True, help_text="Primary contact phone number"
    )

    # Address fields - keeping existing structure but adding street_address for clarity
    address = models.TextField(blank=True, null=True, help_text="Supplier address")
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
        Protein, blank=True, help_text="Protein types supplied by this supplier"
    )
    edible_inedible = models.CharField(
        max_length=50,
        choices=EdibleInedibleChoices.choices,
        blank=True,
        default='',
        help_text="Type of products supplied",
    )
    type_of_plant = models.CharField(
        max_length=100,
        choices=PlantTypeChoices.choices,
        blank=True,
        default='',
        help_text="Type of plant (e.g., Vertical, Processor)",
    )
    type_of_certificate = models.CharField(
        max_length=100,
        choices=CertificateTypeChoices.choices,
        blank=True,
        default='',
        help_text="Certificate type (e.g., 3rd Party, BRC)",
    )
    tested_product = models.BooleanField(
        default=False, help_text="Does supplier provide tested products?"
    )
    origin = models.CharField(
        max_length=100,
        choices=OriginChoices.choices,
        blank=True,
        default='',
        help_text="Product origin (e.g., Domestic, Imported)",
    )
    country_origin = models.CharField(
        max_length=100,
        choices=CountryOriginChoices.choices,
        blank=True,
        default='',
        help_text="Country of origin (e.g., USA, CAN)",
    )
    contacts = models.ManyToManyField(
        Contact,
        related_name="suppliers",
        blank=True,
        help_text="Multiple contacts associated with this supplier",
    )
    shipping_offered = models.CharField(
        max_length=100,
        choices=ShippingOfferedChoices.choices,
        blank=True,
        default='',
        help_text="Shipping services offered (e.g., Yes - Domestic)",
    )
    how_to_book_pickup = models.CharField(
        max_length=100, blank=True, default='', help_text="How to book pickup (e.g., Website, Call)"
    )
    offer_contracts = models.BooleanField(
        default=False, help_text="Does supplier offer contracts?"
    )
    offers_export_documents = models.BooleanField(
        default=False, help_text="Does supplier offer export documents?"
    )
    
    # Additional fields from Excel requirements
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
    fresh_or_frozen = models.CharField(
        max_length=20,
        choices=FreshOrFrozenChoices.choices,
        blank=True,
        default='',
        help_text="Product state (Fresh or Frozen)",
    )
    package_type = models.CharField(
        max_length=50,
        choices=PackageTypeChoices.choices,
        blank=True,
        default='',
        help_text="Package type (e.g., Boxed wax lined, Combo bins)",
    )
    net_or_catch = models.CharField(
        max_length=20,
        choices=NetOrCatchChoices.choices,
        blank=True,
        default='',
        help_text="Weight type (Net or Catch)",
    )
    departments = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Departments (comma-separated: Sales, BOL, COA, etc.)",
    )
    
    # Deprecated fields - keeping for backward compatibility
    accounting_terms = models.CharField(
        max_length=100, blank=True, default='', help_text="Accounting terms (deprecated, use accounting_payment_terms)"
    )
    accounting_line_of_credit = models.CharField(
        max_length=100, blank=True, default='', help_text="Line of credit amount (deprecated, use account_line_of_credit)"
    )
    credit_app_sent = models.BooleanField(
        default=False, help_text="Has credit application been sent?"
    )
    credit_app_set_up = models.BooleanField(
        default=False, help_text="Has credit application been set up?"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name
