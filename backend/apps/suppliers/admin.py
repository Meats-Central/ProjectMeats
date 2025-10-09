"""
Django admin configuration for Suppliers app.
"""
from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    """Admin interface for Supplier model."""

    list_display = (
        "name",
        "contact_person",
        "email",
        "phone",
        "city",
        "origin",
        "created_on",
    )
    list_filter = (
        "country",
        "origin",
        "country_origin",
        "type_of_plant",
        "shipping_offered",
        "tested_product",
        "offer_contracts",
        "created_on",
    )
    search_fields = ("name", "contact_person", "email", "phone")
    readonly_fields = ("created_on", "modified_on")
    filter_horizontal = ("proteins", "contacts")

    fieldsets = (
        (
            "Company Information",
            {"fields": ("name", "contact_person", "email", "phone")},
        ),
        (
            "Address",
            {"fields": ("address", "street_address", "city", "state", "zip_code", "country")},
        ),
        (
            "Product Details",
            {
                "fields": (
                    "type_of_plant",
                    "origin",
                    "country_origin",
                    "fresh_or_frozen",
                    "package_type",
                    "net_or_catch",
                    "edible_inedible",
                    "tested_product",
                )
            },
        ),
        (
            "Certifications & Capabilities",
            {
                "fields": (
                    "type_of_certificate",
                    "shipping_offered",
                    "how_to_book_pickup",
                    "offer_contracts",
                    "offers_export_documents",
                    "departments",
                )
            },
        ),
        (
            "Payment & Credit",
            {
                "fields": (
                    "accounting_payment_terms",
                    "credit_limits",
                    "account_line_of_credit",
                    "accounting_terms",
                    "accounting_line_of_credit",
                    "credit_app_sent",
                    "credit_app_set_up",
                )
            },
        ),
        (
            "Relationships",
            {"fields": ("plant", "proteins", "contacts")},
        ),
        (
            "Metadata",
            {"fields": ("tenant", "created_on", "modified_on"), "classes": ("collapse",)},
        ),
    )
