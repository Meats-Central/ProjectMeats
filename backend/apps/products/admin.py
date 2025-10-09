"""
Django admin configuration for Products app.
"""
from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""

    list_display = (
        "product_code",
        "description_preview",
        "type_of_protein",
        "fresh_or_frozen",
        "package_type",
        "is_active",
        "created_on",
    )
    list_filter = (
        "type_of_protein",
        "fresh_or_frozen",
        "package_type",
        "edible_or_inedible",
        "tested_product",
        "is_active",
        "created_on",
    )
    search_fields = ("product_code", "description_of_product_item")
    readonly_fields = ("created_on", "modified_on")
    
    def description_preview(self, obj):
        """Return truncated description for list display."""
        return obj.description_of_product_item[:50] + "..." if len(obj.description_of_product_item) > 50 else obj.description_of_product_item
    
    description_preview.short_description = "Description"

    fieldsets = (
        (
            "Product Identification",
            {
                "fields": ("product_code", "description_of_product_item", "is_active")
            },
        ),
        (
            "Product Characteristics",
            {
                "fields": (
                    "type_of_protein",
                    "fresh_or_frozen",
                    "package_type",
                    "net_or_catch",
                    "edible_or_inedible",
                    "tested_product",
                )
            },
        ),
        (
            "Details",
            {
                "fields": ("unit_weight",)
            },
        ),
        (
            "Metadata",
            {
                "fields": ("tenant", "created_on", "modified_on"),
                "classes": ("collapse",),
            },
        ),
    )

