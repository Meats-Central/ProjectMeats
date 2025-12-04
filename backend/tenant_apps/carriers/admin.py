"""
Django admin configuration for Carriers app.
"""
from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import Carrier


@admin.register(Carrier)
class CarrierAdmin(TenantFilteredAdmin):
    """Admin interface for Carrier model with tenant filtering."""

    list_display = (
        "name",
        "code",
        "carrier_type",
        "contact_person",
        "phone",
        "city",
        "is_active",
        "created_at",
    )
    list_filter = ("carrier_type", "is_active", "country", "state", "created_at")
    search_fields = ("name", "code", "contact_person", "mc_number", "dot_number")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "code", "carrier_type", "contact_person")},
        ),
        ("Contact Information", {"fields": ("phone", "email")}),
        ("Address", {"fields": ("address", "city", "state", "zip_code", "country")}),
        ("Transportation Details", {"fields": ("mc_number", "dot_number")}),
        (
            "Enhanced Contact Information",
            {
                "fields": (
                    "my_customer_num_from_carrier",
                    "accounting_payable_contact_name",
                    "accounting_payable_contact_phone",
                    "accounting_payable_contact_email",
                    "sales_contact_name",
                    "sales_contact_phone",
                    "sales_contact_email",
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
                )
            },
        ),
        (
            "Operations",
            {
                "fields": (
                    "how_carrier_make_appointment",
                    "departments",
                )
            },
        ),
        (
            "Insurance Information",
            {
                "fields": (
                    "insurance_provider",
                    "insurance_policy_number",
                    "insurance_expiry",
                )
            },
        ),
        (
            "Relationships",
            {"fields": ("contacts",)},
        ),
        ("Status & Notes", {"fields": ("is_active", "notes")}),
        (
            "Metadata",
            {
                "fields": ("tenant", "created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
    filter_horizontal = ("contacts",)
