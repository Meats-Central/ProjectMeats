"""
Django admin configuration for Carriers app.
"""
from django.contrib import admin
from .models import Carrier


@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    """Admin interface for Carrier model."""

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
            "Insurance Information",
            {
                "fields": (
                    "insurance_provider",
                    "insurance_policy_number",
                    "insurance_expiry",
                )
            },
        ),
        ("Status & Notes", {"fields": ("is_active", "notes")}),
        (
            "Metadata",
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
