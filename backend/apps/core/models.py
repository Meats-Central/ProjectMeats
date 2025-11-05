"""
Core models for ProjectMeats.

Provides base models and common functionality used across all apps.
"""
from django.contrib.auth.models import User
from django.db import models


class TenantManager(models.Manager):
    """
    Custom manager that filters querysets by tenant.
    
    This manager automatically filters all queries by the current tenant
    when available in the context.
    """

    def get_queryset(self):
        """Override to filter by tenant if available in context."""
        return super().get_queryset()

    def for_tenant(self, tenant):
        """Filter queryset for a specific tenant."""
        if tenant:
            return self.filter(tenant=tenant)
        return self.none()


class Protein(models.Model):
    """Protein model for meat types used across suppliers and customers."""

    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Protein type (e.g., Beef, Pork, Chicken, Lamb)",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Protein"
        verbose_name_plural = "Proteins"

    def __str__(self):
        return self.name


class EdibleInedibleChoices(models.TextChoices):
    """Common choices for edible/inedible product types."""

    EDIBLE = "Edible", "Edible"
    INEDIBLE = "Inedible", "Inedible"
    BOTH = "Edible & Inedible", "Edible & Inedible"


class AccountingPaymentTermsChoices(models.TextChoices):
    """Common choices for payment terms."""

    WIRE = "Wire", "Wire"
    ACH = "ACH", "ACH"
    CHECK = "Check", "Check"
    CREDIT_CARD = "Credit Card", "Credit Card"


class CreditLimitChoices(models.TextChoices):
    """Common choices for credit limits."""

    WIRE_1_DAY_PRIOR = "Wire 1 day prior", "Wire 1 day prior"
    NET_7 = "Net 7", "Net 7"
    NET_15 = "Net 15", "Net 15"
    NET_30 = "Net 30", "Net 30"
    NET_45 = "Net 45", "Net 45"
    NET_60 = "Net 60", "Net 60"


class AccountLineOfCreditChoices(models.TextChoices):
    """Common choices for line of credit amounts."""

    RANGE_0_50K = "$0 - $50,000", "$0 - $50,000"
    RANGE_50K_100K = "$50,000 - $100,000", "$50,000 - $100,000"
    RANGE_100K_250K = "$100,000 - $250,000", "$100,000 - $250,000"
    RANGE_250K_500K = "$250,000 - $500,000", "$250,000 - $500,000"
    RANGE_500K_1M = "$500,000 - $1,000,000", "$500,000 - $1,000,000"
    RANGE_1M_PLUS = "$1,000,000+", "$1,000,000+"


class ProteinTypeChoices(models.TextChoices):
    """Common choices for protein types."""

    BEEF = "Beef", "Beef"
    CHICKEN = "Chicken", "Chicken"
    PORK = "Pork", "Pork"
    LAMB = "Lamb", "Lamb"
    TURKEY = "Turkey", "Turkey"
    FISH = "Fish", "Fish"
    HORSE = "Horse", "Horse"
    OTHER = "Other", "Other"


class FreshOrFrozenChoices(models.TextChoices):
    """Common choices for fresh or frozen products."""

    FRESH = "Fresh", "Fresh"
    FROZEN = "Frozen", "Frozen"


class PackageTypeChoices(models.TextChoices):
    """Common choices for package types."""

    BOXED_WAX_LINED = "Boxed wax lined", "Boxed wax lined"
    BOXED_CO2 = "Boxed CO2", "Boxed CO2"
    COMBO_BINS = "Combo bins", "Combo bins"
    TOTES = "Totes", "Totes"
    BAGS = "Bags", "Bags"
    BULK = "Bulk", "Bulk"
    POLY_MULTIPLE = "Poly-Multiple", "Poly-Multiple"
    NUDE = "Nude", "Nude"


class NetOrCatchChoices(models.TextChoices):
    """Common choices for net or catch weight."""

    NET = "Net", "Net"
    CATCH = "Catch", "Catch"


class PlantTypeChoices(models.TextChoices):
    """Common choices for plant types."""

    VERTICAL = "Vertical", "Vertical"
    PROCESSOR = "Processor", "Processor"
    DISTRIBUTOR = "Distributor", "Distributor"
    RENDERER = "Renderer", "Renderer"


class CertificateTypeChoices(models.TextChoices):
    """Common choices for certificate types."""

    THIRD_PARTY = "3rd Party", "3rd Party"
    BRC = "BRC", "BRC"
    SQF = "SQF", "SQF"
    HALAL = "Halal", "Halal"
    KOSHER = "Kosher", "Kosher"
    ORGANIC = "Organic", "Organic"


class OriginChoices(models.TextChoices):
    """Common choices for product origin."""

    DOMESTIC = "Domestic", "Domestic"
    IMPORTED = "Imported", "Imported"


class CountryOriginChoices(models.TextChoices):
    """Common choices for country of origin."""

    USA = "USA", "USA"
    CANADA = "CAN", "Canada"
    MEXICO = "MEX", "Mexico"
    BRAZIL = "BRA", "Brazil"
    AUSTRALIA = "AUS", "Australia"
    NEW_ZEALAND = "NZL", "New Zealand"


class ShippingOfferedChoices(models.TextChoices):
    """Common choices for shipping offered."""

    YES_DOMESTIC = "Yes - Domestic", "Yes - Domestic"
    YES_INTERNATIONAL = "Yes - International", "Yes - International"
    NO = "No", "No"


class IndustryChoices(models.TextChoices):
    """Common choices for customer industry."""

    PET_SECTOR = "Pet Sector", "Pet Sector"
    PROCESSOR = "Processor", "Processor"
    RETAIL = "Retail", "Retail"
    FOOD_SERVICE = "Food Service", "Food Service"
    EXPORT = "Export", "Export"


class WeightUnitChoices(models.TextChoices):
    """Common choices for weight units."""

    LBS = "LBS", "LBS"
    KG = "KG", "KG"


class AppointmentMethodChoices(models.TextChoices):
    """Common choices for how carriers make appointments."""

    EMAIL = "Email", "Email"
    PHONE = "Phone", "Phone"
    WEBSITE = "Website", "Website"
    FAX = "Fax", "Fax"
    FCFS = "FCFS", "FCFS"


class ContactTypeChoices(models.TextChoices):
    """Common choices for contact types."""

    SALES = "Sales", "Sales"
    ACCOUNTING = "Accounting", "Accounting"
    SHIPPING = "Shipping", "Shipping"
    RECEIVING = "Receiving", "Receiving"
    OPERATIONS = "Operations", "Operations"
    QUALITY = "Quality", "Quality"
    EXECUTIVE = "Executive", "Executive"
    DOCS_BOL = "Doc's BOL", "Doc's BOL"
    COA = "COA", "COA"
    POD = "POD", "POD"


class CartonTypeChoices(models.TextChoices):
    """Common choices for carton types."""

    POLY_MULTIPLE = "Poly-Multiple", "Poly-Multiple"
    WAXED_LINED = "Waxed Lined", "Waxed Lined"
    CARDBOARD = "Cardboard", "Cardboard"
    PLASTIC = "Plastic", "Plastic"


class ItemProductionDateChoices(models.TextChoices):
    """Common choices for item production date."""

    FIVE_DAY_NEWER = "5 day newer", "5 day newer"
    TEN_DAY_NEWER = "10 day newer", "10 day newer"
    FIFTEEN_DAY_NEWER = "15 day newer", "15 day newer"
    THIRTY_DAY_NEWER = "30 day newer", "30 day newer"


class CarrierReleaseFormatChoices(models.TextChoices):
    """Common choices for carrier release format."""

    SUPPLIER_CONFIRMATION_ORDER_NUMBER = "Supplier Confirmation Order Number", "Supplier Confirmation Order Number"
    CARRIER_RELEASE_NUMBER = "Carrier Release Number", "Carrier Release Number"
    BOTH = "Both", "Both"


class LoadStatusChoices(models.TextChoices):
    """Common choices for load status in cold storage."""

    MATCHED = "Matched", "Matched"
    TBD_NOT_MATCHED = "TBD - Not Matched", "TBD - Not Matched"


class StatusChoices(models.TextChoices):
    """Common status choices for entities."""

    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    ARCHIVED = "archived", "Archived"


class StatusModel(models.Model):
    """Abstract base model for entities with status."""

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Current status of the entity",
    )

    class Meta:
        abstract = True


class TimestampModel(models.Model):
    """Abstract base model for entities with timestamps."""

    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OwnedModel(TimestampModel):
    """Abstract base model for entities with ownership."""

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who owns this entity",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_created",
        help_text="User who created this entity",
    )
    modified_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="%(class)s_modified",
        help_text="User who last modified this entity",
    )

    class Meta:
        abstract = True


class UserPreferences(models.Model):
    """
    User-specific preferences for UI customization.
    
    Stores theme preferences, layout configurations, widget arrangements,
    and other user-specific UI settings.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferences',
        help_text="User for these preferences"
    )
    
    # Theme preferences
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
        default='light',
        help_text="UI theme preference"
    )
    
    # Layout and widget configuration (JSON format)
    dashboard_layout = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dashboard widget layout configuration"
    )
    
    sidebar_collapsed = models.BooleanField(
        default=False,
        help_text="Whether sidebar is collapsed by default"
    )
    
    # Quick menu favorites (stored as list of route paths)
    quick_menu_items = models.JSONField(
        default=list,
        blank=True,
        help_text="User's favorite quick menu items"
    )
    
    # Custom widget settings
    widget_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="Widget-specific preferences and configurations"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Preferences for {self.user.username}"


class QuotaModel(models.Model):
    """
    Quota model for sales quotas and targets.
    
    This is a placeholder model for the sales quota management system.
    Used by Client model for M2M relationships.
    """
    
    name = models.CharField(
        max_length=255,
        help_text="Name of the quota (e.g., 'Q4 2024 Sales Target')"
    )
    target_amount = models.IntegerField(
        default=0,
        help_text="Target amount for this quota (in applicable units)"
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text="Optional description of the quota"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Quota"
        verbose_name_plural = "Quotas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} (Target: {self.target_amount})"
