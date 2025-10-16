"""
Core admin for ProjectMeats.

Admin interface for core models.
"""
from django.contrib import admin
from apps.core.models import Protein, UserPreferences


@admin.register(Protein)
class ProteinAdmin(admin.ModelAdmin):
    """Admin interface for Protein model."""

    list_display = ["name"]
    search_fields = ["name"]
    ordering = ["name"]


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    """Admin interface for UserPreferences model."""

    list_display = ["user", "theme", "sidebar_open", "updated_at"]
    list_filter = ["theme", "sidebar_open"]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("User", {
            "fields": ("user",)
        }),
        ("UI Preferences", {
            "fields": ("theme", "sidebar_open", "dashboard_layout")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

