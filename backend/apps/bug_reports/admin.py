"""
Bug Reports admin configuration.
"""
from django.contrib import admin
from .models import BugReport


@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    """Admin interface for BugReport model."""

    list_display = [
        "title",
        "category",
        "severity",
        "status",
        "reporter",
        "created_at",
    ]
    list_filter = ["status", "severity", "category", "created_at"]
    search_fields = ["title", "description", "reporter__username"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        (
            "Basic Information",
            {"fields": ["title", "description", "category", "severity", "status"]},
        ),
        ("Reporter Information", {"fields": ["reporter", "reporter_email"]}),
        (
            "Technical Details",
            {
                "fields": ["browser", "os", "screen_resolution", "url"],
                "classes": ["collapse"],
            },
        ),
        (
            "Reproduction",
            {
                "fields": [
                    "steps_to_reproduce",
                    "expected_behavior",
                    "actual_behavior",
                ],
                "classes": ["collapse"],
            },
        ),
        (
            "Metadata",
            {
                "fields": ["created_at", "updated_at", "resolved_at"],
                "classes": ["collapse"],
            },
        ),
    ]
