from django.contrib import admin
from apps.core.admin import TenantFilteredAdmin
from .models import Tenant, TenantUser, TenantInvitation, TenantDomain, Client, Domain


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
        # Get base queryset from TenantFilteredAdmin (which filters by tenant)
        qs = super().get_queryset(request)
        return qs.select_related("tenant", "invited_by", "accepted_by")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    Admin interface for Client model (schema-based multi-tenancy).
    
    Manages clients in the schema-based multi-tenancy approach where each
    client gets its own PostgreSQL schema.
    """

    list_display = [
        "name",
        "schema_name",
        "meat_specialty",
        "logistics_integration_active",
        "created_at",
    ]
    list_filter = ["meat_specialty", "logistics_integration_active", "created_at"]
    search_fields = ["name", "schema_name", "description"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["sales_quota_m2m"]

    fieldsets = [
        ("Basic Information", {"fields": ("name", "schema_name", "description")}),
        (
            "Business Settings",
            {
                "fields": (
                    "meat_specialty",
                    "logistics_integration_active",
                    "sales_quota_m2m",
                )
            },
        ),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ["collapse"]}),
    ]

    def get_queryset(self, request):
        """Optimize queries by prefetching related quotas."""
        qs = super().get_queryset(request)
        return qs.prefetch_related("sales_quota_m2m")


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """
    Admin interface for Domain model (schema-based multi-tenancy).
    
    Manages domain-to-client mappings for schema-based multi-tenancy routing.
    """

    list_display = ["domain", "tenant", "is_primary"]
    list_filter = ["is_primary"]
    search_fields = ["domain", "tenant__name", "tenant__schema_name"]
    
    fieldsets = [
        ("Domain Information", {"fields": ("domain", "tenant", "is_primary")}),
    ]
    
    def get_queryset(self, request):
        """Optimize queries by selecting related client."""
        qs = super().get_queryset(request)
        return qs.select_related("tenant")


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
