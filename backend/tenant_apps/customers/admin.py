"""
Django admin configuration for Customers app.
"""
from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(TenantFilteredAdmin):
    """Admin interface for Customer model with tenant filtering."""

    list_display = (
        "name",
        "contact_person",
        "email",
        "phone",
        "city",
        "industry",
        "created_on",
    )
    list_filter = (
        "country",
        "industry",
        "purchasing_preference_origin",
        "will_pickup_load",
        "product_exportable",
        "created_on",
    )
    search_fields = (
        "name",
        "contact_person",
        "email",
        "phone",
        "buyer_contact_name",
        "buyer_contact_email",
    )
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
            "Buyer Contact",
            {
                "fields": (
                    "buyer_contact_name",
                    "buyer_contact_phone",
                    "buyer_contact_email",
                )
            },
        ),
        (
            "Business Details",
            {
                "fields": (
                    "industry",
                    "purchasing_preference_origin",
                    "type_of_plant",
                    "type_of_certificate",
                    "product_exportable",
                    "will_pickup_load",
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
                )
            },
        ),
        (
            "Relationships",
            {"fields": ("plant", "proteins", "contacts", "edible_inedible")},
        ),
        (
            "Metadata",
            {"fields": ("tenant", "created_on", "modified_on"), "classes": ("collapse",)},
        ),
    )
