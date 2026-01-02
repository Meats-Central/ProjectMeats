from django.contrib import admin, messages
from django.utils.html import format_html
from django.conf import settings
from apps.core.admin import TenantFilteredAdmin
from .models import Tenant, TenantUser, TenantInvitation, TenantDomain


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Admin interface for Tenant model.
    
    Note: This uses base ModelAdmin, not TenantFilteredAdmin, because:
    - The Tenant model itself doesn't have a 'tenant' field (it IS the tenant)
    - Instead, we filter by user association in get_queryset
    """

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
    
    actions = ['generate_team_invite']

    fieldsets = [
        ("Basic Information", {"fields": ("name", "slug", "schema_name", "domain")}),
        ("Contact Information", {"fields": ("contact_email", "contact_phone")}),
        ("Branding", {"fields": ("logo",)}),
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
        """
        Filter tenants by user association.
        
        - Superusers see all tenants
        - Staff users only see tenants they are associated with
        """
        qs = super().get_queryset(request).select_related("created_by")
        
        # Superusers see all tenants
        if request.user.is_superuser:
            return qs
        
        # Get tenant IDs the user is associated with
        tenant_ids = TenantUser.objects.filter(
            user=request.user,
            is_active=True
        ).values_list('tenant_id', flat=True)
        
        # Filter to only show associated tenants
        return qs.filter(id__in=tenant_ids)
    
    @admin.action(description="⚡ Generate Team Invite Link (Reusable)")
    def generate_team_invite(self, request, queryset):
        """Generate a reusable Golden Ticket invitation link."""
        if queryset.count() != 1:
            self.message_user(
                request,
                "Please select exactly one tenant.",
                level=messages.ERROR
            )
            return

        tenant = queryset.first()
        
        # Create the Golden Ticket
        invitation = TenantInvitation.objects.create(
            tenant=tenant,
            email=None,  # No specific email
            role='user',  # Default role
            invited_by=request.user,
            is_reusable=True,
            max_uses=50,  # Default limit
            status='pending'
        )

        # Determine environment URL
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        # Fallback: detect from request host if setting not available
        if not base_url or base_url == 'http://localhost:3000':
            host = request.get_host()
            if 'dev' in host or 'localhost' in host:
                base_url = "https://dev.meatscentral.com"
            elif 'uat' in host:
                base_url = "https://uat.meatscentral.com"
            else:
                base_url = "https://meatscentral.com"
            
        link = f"{base_url}/signup?token={invitation.token}"

        # Show the link to the Superuser immediately
        self.message_user(
            request,
            format_html(
                '<strong>✅ Success!</strong> Reusable team invite created (50 uses max).<br><br>'
                '<div style="background: #f0f0f0; padding: 10px; border-radius: 4px; margin: 10px 0;">'
                '<strong>Copy this link:</strong><br>'
                '<input type="text" value="{}" style="width: 500px; padding: 8px; margin-top: 5px; '
                'font-family: monospace; font-size: 12px;" readonly onclick="this.select();">'
                '</div>'
                '<small>💡 Users can share this link with team members. Each use will be tracked.</small>',
                link
            ),
            level=messages.SUCCESS
        )


@admin.register(TenantUser)
class TenantUserAdmin(TenantFilteredAdmin):
    """Admin interface for TenantUser associations with tenant filtering."""

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
        # Get base queryset from TenantFilteredAdmin (which filters by tenant)
        qs = super().get_queryset(request)
        return qs.select_related("user", "tenant")


@admin.register(TenantInvitation)
class TenantInvitationAdmin(TenantFilteredAdmin):
    """Admin interface for TenantInvitation model with tenant filtering."""

    list_display = [
        "email_or_type",
        "tenant",
        "role",
        "status",
        "usage_info",
        "invited_by",
        "created_at",
        "expires_at",
        "is_expired",
        "is_valid",
    ]
    list_filter = ["status", "role", "is_reusable", "tenant", "created_at"]
    search_fields = ["email", "tenant__name", "invited_by__username"]
    readonly_fields = ["id", "token", "created_at", "accepted_at", "accepted_by"]
    
    fieldsets = [
        ("Invitation Details", {
            "fields": ("tenant", "email", "role", "message")
        }),
        ("Reusability Settings", {
            "fields": ("is_reusable", "max_uses", "uses_count"),
            "classes": ["collapse"]
        }),
        ("Status", {
            "fields": ("status", "token", "expires_at")
        }),
        ("Tracking", {
            "fields": ("invited_by", "created_at", "accepted_by", "accepted_at"),
            "classes": ["collapse"]
        }),
    ]
    
    def email_or_type(self, obj):
        """Display email or 'Reusable Link' label."""
        if obj.is_reusable:
            return format_html(
                '<strong style="color: #0066cc;">🔗 Reusable Link</strong>'
            )
        return obj.email or "—"
    email_or_type.short_description = "Email / Type"
    
    def usage_info(self, obj):
        """Display usage statistics for reusable links."""
        if obj.is_reusable:
            percentage = (obj.usage_count / obj.max_uses * 100) if obj.max_uses > 0 else 0
            color = "#28a745" if percentage < 80 else "#ffc107" if percentage < 100 else "#dc3545"
            return format_html(
                '<span style="color: {};">{} / {} uses ({:.0f}%)</span>',
                color,
                obj.usage_count,
                obj.max_uses,
                percentage
            )
        return "—"
    usage_info.short_description = "Usage"
    
    def get_queryset(self, request):
        # Get base queryset from TenantFilteredAdmin (which filters by tenant)
        qs = super().get_queryset(request)
        return qs.select_related("tenant", "invited_by", "accepted_by")


# Note: Client and Domain admin classes have been removed as these models
# are not currently defined in models.py. They were intended for django-tenants
# schema-based multi-tenancy but are not implemented in the current shared-schema approach.


@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    """
    Admin interface for TenantDomain model (shared-schema approach).
    
    Manages domain-to-tenant mappings for shared-schema multi-tenancy.
    """

    list_display = ["domain", "tenant", "is_primary", "created_at"]
    list_filter = ["is_primary", "created_at"]
    search_fields = ["domain", "tenant__name", "tenant__slug"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = [
        ("Domain Information", {"fields": ("domain", "tenant", "is_primary")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ["collapse"]}),
    ]
    
    def get_queryset(self, request):
        """Optimize queries by selecting related tenant."""
        qs = super().get_queryset(request)
        return qs.select_related("tenant")
