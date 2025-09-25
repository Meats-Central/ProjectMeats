"""
Customers models for ProjectMeats.

Defines customer entities and related business logic.
"""
from django.db import models

from apps.contacts.models import Contact
from apps.core.models import Protein, TimestampModel
from apps.plants.models import Plant


class Customer(TimestampModel):
    """Customer model for managing customer information."""

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
        choices=[
            ("Edible", "Edible"),
            ("Inedible", "Inedible"),
            ("Edible & Inedible", "Edible & Inedible"),
        ],
        blank=True,
        help_text="Type of products handled",
    )
    type_of_plant = models.CharField(
        max_length=100,
        blank=True,
        help_text="Customer type of plant (e.g., Vertical, Processor)",
    )
    purchasing_preference_origin = models.CharField(
        max_length=100,
        blank=True,
        help_text="Purchasing preference origin (e.g., Domestic, Imported)",
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
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
    accounting_terms = models.CharField(
        max_length=100, blank=True, help_text="Accounting terms (e.g., Wire, ACH)"
    )
    accounting_line_of_credit = models.CharField(
        max_length=100,
        blank=True,
        help_text="Line of credit amount (e.g., $50,000 - $100,000)",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return self.name
