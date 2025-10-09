"""
Django admin configuration for Contacts app.
"""
from django.contrib import admin
from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """Admin interface for Contact model."""

    list_display = (
        "get_full_name",
        "email",
        "phone",
        "company",
        "position",
        "contact_type",
        "status",
        "created_at",
    )
    list_filter = ("status", "contact_type", "created_at")
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
        "main_phone",
        "direct_phone",
        "cell_phone",
        "company",
    )
    readonly_fields = ("created_on", "modified_on", "created_at", "updated_at")

    def get_full_name(self, obj):
        """Return full name of the contact."""
        return f"{obj.first_name} {obj.last_name}".strip()

    get_full_name.short_description = "Name"

    fieldsets = (
        (
            "Personal Information",
            {"fields": ("first_name", "last_name", "email", "phone", "status")},
        ),
        (
            "Additional Contact Methods",
            {"fields": ("main_phone", "direct_phone", "cell_phone")},
        ),
        (
            "Professional Information",
            {"fields": ("company", "position", "contact_title", "contact_type")},
        ),
        (
            "Metadata",
            {"fields": ("tenant", "created_on", "modified_on", "created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
