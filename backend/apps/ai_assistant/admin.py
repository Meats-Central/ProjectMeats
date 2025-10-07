"""
Django admin configuration for AI Assistant app.
"""
from django.contrib import admin
from .models import ChatSession, ChatMessage, AIConfiguration


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """Admin interface for ChatSession model."""

    list_display = (
        "title",
        "owner",
        "session_status",
        "get_message_count",
        "last_activity",
        "created_on",
    )
    list_filter = ("session_status", "status", "created_on", "last_activity")
    search_fields = ("title", "owner__username")
    readonly_fields = ("id", "created_on", "modified_on", "last_activity")

    def get_message_count(self, obj):
        """Return the number of messages in this session."""
        return obj.chatmessage_set.count()

    get_message_count.short_description = "Messages"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "owner", "session_status", "status")},
        ),
        ("Context & Data", {"fields": ("context_data",), "classes": ("collapse",)}),
        (
            "Metadata",
            {
                "fields": ("id", "created_on", "modified_on", "last_activity"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for ChatMessage model."""

    list_display = (
        "get_content_preview",
        "session",
        "message_type",
        "owner",
        "is_processed",
        "created_on",
    )
    list_filter = ("message_type", "is_processed", "created_on")
    search_fields = ("content", "session__title", "owner__username")
    readonly_fields = ("id", "created_on", "modified_on")

    def get_content_preview(self, obj):
        """Return a preview of the message content."""
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    get_content_preview.short_description = "Content Preview"

    fieldsets = (
        (
            "Message Information",
            {"fields": ("session", "message_type", "owner", "is_processed")},
        ),
        ("Content", {"fields": ("content",)}),
        ("Metadata", {"fields": ("metadata",), "classes": ("collapse",)}),
        (
            "System Information",
            {"fields": ("id", "created_on", "modified_on"), "classes": ("collapse",)},
        ),
    )


@admin.register(AIConfiguration)
class AIConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for AIConfiguration model."""

    list_display = (
        "name",
        "provider",
        "model_name",
        "is_active",
        "is_default",
        "created_at",
    )
    list_filter = ("provider", "is_active", "is_default", "created_at")
    search_fields = ("name", "model_name")
    readonly_fields = ("created_at",)

    fieldsets = (
        ("Configuration", {"fields": ("name", "provider", "model_name")}),
        ("Settings", {"fields": ("is_active", "is_default")}),
        ("Metadata", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
