from django.contrib import admin
from django.contrib import messages
from .models import Tenant, TenantUser, TenantInvitation
from .email_utils import send_invitation_email


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
    actions = ["resend_invitation_emails"]
    
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
    
    def save_model(self, request, obj, form, change):
        """Override save to send email when invitation is created."""
        is_new = obj._state.adding
        
        # Set invited_by to current user if not set and this is a new invitation
        if is_new and not obj.invited_by:
            obj.invited_by = request.user
        
        super().save_model(request, obj, form, change)
        
        # Send email for new invitations with pending status
        if is_new and obj.status == 'pending':
            try:
                if send_invitation_email(obj):
                    messages.success(
                        request, 
                        f"Invitation created and email sent to {obj.email}"
                    )
                else:
                    messages.warning(
                        request,
                        f"Invitation created but email failed to send to {obj.email}"
                    )
            except Exception as e:
                messages.error(
                    request,
                    f"Invitation created but email error: {str(e)}"
                )
    
    def resend_invitation_emails(self, request, queryset):
        """Admin action to resend invitation emails."""
        from django.utils import timezone
        
        sent_count = 0
        error_count = 0
        
        for invitation in queryset:
            if invitation.status != 'pending':
                continue
            
            # Extend expiration by 7 days
            invitation.expires_at = timezone.now() + timezone.timedelta(days=7)
            invitation.save()
            
            # Send email
            try:
                if send_invitation_email(invitation):
                    sent_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1
        
        if sent_count > 0:
            messages.success(request, f"Successfully resent {sent_count} invitation(s)")
        if error_count > 0:
            messages.warning(request, f"Failed to resend {error_count} invitation(s)")
    
    resend_invitation_emails.short_description = "Resend invitation emails (extends expiration)"
