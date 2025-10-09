from django.db import models
from django.contrib.auth.models import User
from apps.tenants.models import Tenant
from apps.core.models import (
    AccountingPaymentTermsChoices,
    AccountLineOfCreditChoices,
    AppointmentMethodChoices,
    CreditLimitChoices,
    TenantManager,
)
from apps.contacts.models import Contact


class Carrier(models.Model):
    CARRIER_TYPE_CHOICES = [
        ("truck", "Truck"),
        ("rail", "Rail"),
        ("air", "Air"),
        ("sea", "Sea"),
        ("other", "Other"),
    ]

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="carriers",
        help_text="Tenant that owns this carrier",
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    carrier_type = models.CharField(
        max_length=20, choices=CARRIER_TYPE_CHOICES, default="truck"
    )
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default="USA")
    mc_number = models.CharField(
        max_length=50, blank=True, help_text="Motor Carrier Number"
    )
    dot_number = models.CharField(
        max_length=50, blank=True, help_text="Department of Transportation Number"
    )
    insurance_provider = models.CharField(max_length=200, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    # Enhanced fields from Excel requirements
    my_customer_num_from_carrier = models.CharField(
        max_length=100,
        blank=True,
        help_text="Our customer number with this carrier",
    )
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
    sales_contact_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Sales contact name",
    )
    sales_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Sales contact phone",
    )
    sales_contact_email = models.EmailField(
        blank=True,
        help_text="Sales contact email",
    )
    accounting_payment_terms = models.CharField(
        max_length=50,
        choices=AccountingPaymentTermsChoices.choices,
        blank=True,
        help_text="Payment terms (e.g., Wire, ACH, Check)",
    )
    credit_limits = models.CharField(
        max_length=50,
        choices=CreditLimitChoices.choices,
        blank=True,
        help_text="Credit limits/terms (e.g., Net 30, Wire 1 day prior)",
    )
    account_line_of_credit = models.CharField(
        max_length=50,
        choices=AccountLineOfCreditChoices.choices,
        blank=True,
        help_text="Line of credit amount range",
    )
    departments = models.CharField(
        max_length=255,
        blank=True,
        help_text="Departments (comma-separated: BOL, COA, POD, etc.)",
    )
    how_carrier_make_appointment = models.CharField(
        max_length=50,
        choices=AppointmentMethodChoices.choices,
        blank=True,
        help_text="How carrier makes appointments (e.g., Email, Phone)",
    )
    contacts = models.ManyToManyField(
        Contact,
        related_name="carriers",
        blank=True,
        help_text="Multiple contacts associated with this carrier",
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Custom manager for tenant filtering
    objects = TenantManager()

    class Meta:
        ordering = ["name"]
        verbose_name = "Carrier"
        verbose_name_plural = "Carriers"

    def __str__(self):
        return f"{self.code} - {self.name}"
