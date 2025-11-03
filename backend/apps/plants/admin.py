"""
Django admin configuration for Plants app.
"""
from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import Plant


@admin.register(Plant)
class PlantAdmin(TenantFilteredAdmin):
    """Admin interface for Plant model with tenant filtering."""

    list_display = (
        "name",
        "code",
        "plant_est_num",
        "plant_type",
        "city",
        "state",
        "manager",
        "is_active",
        "created_at",
    )
    list_filter = ("plant_type", "is_active", "country", "state", "created_at")
    search_fields = ("name", "code", "manager", "city")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("name", "code", "plant_est_num", "plant_type", "manager")},
        ),
        ("Address", {"fields": ("address", "city", "state", "zip_code", "country")}),
        ("Contact Information", {"fields": ("phone", "email")}),
        ("Operational Details", {"fields": ("capacity", "is_active")}),
        (
            "Metadata",
            {
                "fields": ("tenant", "created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
