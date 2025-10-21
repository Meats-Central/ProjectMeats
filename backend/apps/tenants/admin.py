from django.contrib import admin
from .models import Tenant, TenantUser, TenantInvitation


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin interface for Tenant model."""

    list_display = [
        "name",
        "slug",
        "domain",
        "is_active",
        "is_trial",
        "trial_ends_at",
        "created_at",
    ]
    list_filter = ["is_active", "is_trial", "created_at"]
    search_fields = ["name", "slug", "domain", "contact_email"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = [
        ("Basic Information", {"fields": ("name", "slug", "domain")}),
        ("Contact Information", {"fields": ("contact_email", "contact_phone")}),
        ("Status & Trial", {"fields": ("is_active", "is_trial", "trial_ends_at")}),
        ("Configuration", {"fields": ("settings",), "classes": ["collapse"]}),
        (
            "Metadata",
            {
                "fields": ("id", "created_by", "created_at", "updated_at"),
                "classes": ["collapse"],
            },
        ),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("created_by")


@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    """Admin interface for TenantUser associations."""

    list_display = ["user", "tenant", "role", "is_active", "created_at"]
    list_filter = ["role", "is_active", "tenant"]
    search_fields = ["user__username", "user__email", "tenant__name", "tenant__slug"]
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = [
        ("Association", {"fields": ("tenant", "user", "role")}),
        ("Status", {"fields": ("is_active",)}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ["collapse"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "tenant")


@admin.register(TenantInvitation)
class TenantInvitationAdmin(admin.ModelAdmin):
    """Admin interface for TenantInvitation model."""

    list_display = [
        "email",
        "tenant",
        "role",
        "status",
        "invited_by",
        "created_at",
        "expires_at",
        "is_expired",
        "is_valid",
    ]
    list_filter = ["status", "role", "tenant", "created_at"]
    search_fields = ["email", "tenant__name", "invited_by__username"]
    readonly_fields = ["id", "token", "created_at", "accepted_at", "accepted_by"]
    
    fieldsets = [
        ("Invitation Details", {
            "fields": ("tenant", "email", "role", "message")
        }),
        ("Status", {
            "fields": ("status", "token", "expires_at")
        }),
        ("Tracking", {
            "fields": ("invited_by", "created_at", "accepted_by", "accepted_at"),
            "classes": ["collapse"]
        }),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "tenant", "invited_by", "accepted_by"
        )
