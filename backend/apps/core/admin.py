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

    list_display = ["user", "theme", "sidebar_collapsed", "updated_at"]
    search_fields = ["user__username", "user__email"]
    list_filter = ["theme", "sidebar_collapsed", "created_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("User", {
            "fields": ("user",)
        }),
        ("Theme Settings", {
            "fields": ("theme", "sidebar_collapsed")
        }),
        ("Layout Configuration", {
            "fields": ("dashboard_layout", "widget_preferences", "quick_menu_items"),
            "classes": ("collapse",)
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
