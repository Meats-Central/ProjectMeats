"""
Products models for ProjectMeats.

Master product list and related business logic.
"""
from django.db import models
from apps.core.models import (
    CartonTypeChoices,
    EdibleInedibleChoices,
    FreshOrFrozenChoices,
    NetOrCatchChoices,
    OriginChoices,
    PackageTypeChoices,
    ProteinTypeChoices,
    TimestampModel,
    TenantManager,
)
from apps.tenants.models import Tenant


class Product(TimestampModel):
    """Product model for master product list."""

    # Multi-tenancy
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="products",
        help_text="Tenant that owns this product",
        null=True,
        blank=True,
    )

    # Product identification
    product_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique product code",
    )
    description_of_product_item = models.TextField(
        help_text="Detailed description of the product item",
    )
    
    # Product characteristics
    type_of_protein = models.CharField(
        max_length=50,
        choices=ProteinTypeChoices.choices,
        blank=True,
        default='',
        help_text="Type of protein (e.g., Beef, Chicken, Pork)",
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
    
    # Supplier and sourcing information
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        help_text="Supplier for this product",
    )
    supplier_item_number = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Supplier's item number",
    )
    plants_available = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text="Plants where product is available (e.g., TX, WI, MI)",
    )
    origin = models.CharField(
        max_length=100,
        choices=OriginChoices.choices,
        blank=True,
        default='',
        help_text="Product origin (Packer, Boxed Cold Storage)",
    )
    
    # Packaging details from Excel
    carton_type = models.CharField(
        max_length=50,
        choices=CartonTypeChoices.choices,
        blank=True,
        default='',
        help_text="Type of carton (e.g., Poly-Multiple, Waxed Lined)",
    )
    pcs_per_carton = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="Pieces per carton (e.g., 4/10)",
    )
    uom = models.CharField(
        max_length=10,
        blank=True,
        default='',
        help_text="Unit of measure (LB, KG)",
    )
    
    # Generated/pulled fields from Excel (USDA, NAMP, UB codes)
    namp = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="NAMP code",
    )
    usda = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="USDA code (auto-generated/pulled)",
    )
    ub = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="UB code (auto-generated/pulled)",
    )
    
    # Additional details
    unit_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Standard unit weight",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this product active?",
    )

    # Custom manager for tenant filtering
    objects = TenantManager()

    class Meta:
        ordering = ["product_code"]
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.product_code} - {self.description_of_product_item[:50]}"

