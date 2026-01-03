from django.contrib import admin, messages
from django.utils.html import format_html
from django.conf import settings
from django.shortcuts import render, redirect
from django import forms
from django.contrib.auth.models import User
from apps.core.admin import TenantFilteredAdmin
from .models import Tenant, TenantUser, TenantInvitation, TenantDomain


class InviteUserForm(forms.Form):
    email = forms.EmailField(label="User Email", required=True)
    role = forms.ChoiceField(
        choices=TenantInvitation.ROLE_CHOICES, 
        initial='user',
        label="Role"
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), 
        required=False,
        initial="Join us on Project Meats!"
    )


class OnboardOwnerForm(forms.Form):
    first_name = forms.CharField(label="Owner First Name", required=True)
    last_name = forms.CharField(label="Owner Last Name", required=True)
    email = forms.EmailField(label="Owner Email", required=True)


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Admin interface for Tenant model with tiered actions.
    
    Actions:
    1. Generate Team Invite (Superuser Only): Create generic reusable link.
    2. Onboard Owner (Superuser Only): Invite specific owner with personalized message.
    3. Send Individual Invite (Tenant Admin+): Invite specific email.
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
    
    actions = ['generate_team_invite', 'onboard_tenant_owner', 'send_individual_invite']

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
        Superusers see all; Staff see only their associated tenants.
        """
        qs = super().get_queryset(request).select_related("created_by")
        if request.user.is_superuser:
            return qs
        
        tenant_ids = TenantUser.objects.filter(
            user=request.user,
            is_active=True
        ).values_list('tenant_id', flat=True)
        return qs.filter(id__in=tenant_ids)
    
    @admin.action(description="⚡ Generate Team Invite Link (Superuser Only)")
    def generate_team_invite(self, request, queryset):
        """Generate a reusable Golden Ticket invitation link."""
        if not request.user.is_superuser:
            self.message_user(request, "⛔ Permission Denied: This action is for Superusers only.", level=messages.ERROR)
            return

        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one tenant.", level=messages.ERROR)
            return

        tenant = queryset.first()
        
        invitation = TenantInvitation.objects.create(
            tenant=tenant,
            email=None,
            role='user',
            invited_by=request.user,
            is_reusable=True,
            max_uses=50,
            status='pending',
            message="Join your team on Project Meats!"
        )

        link = self._get_invite_link(request, invitation)
        
        self.message_user(
            request,
            format_html(
                '<strong>✅ Golden Ticket Created!</strong><br>'
                '<input type="text" value="{}" style="width: 100%; padding: 8px; margin-top: 5px;" readonly onclick="this.select();">',
                link
            ),
            level=messages.SUCCESS
        )

    @admin.action(description="🚀 Onboard New Tenant Owner (Superuser Only)")
    def onboard_tenant_owner(self, request, queryset):
        """
        Wizard to onboard a specific owner for a tenant.
        Captures Name/Email -> Creates Admin Invite -> Personalized Message.
        """
        if not request.user.is_superuser:
            self.message_user(request, "⛔ Permission Denied: Only Superusers can onboard owners.", level=messages.ERROR)
            return

        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one tenant to onboard.", level=messages.ERROR)
            return

        tenant = queryset.first()

        # Handle Form Submission
        if 'apply' in request.POST:
            form = OnboardOwnerForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                first_name = form.cleaned_data['first_name']
                last_name = form.cleaned_data['last_name']
                
                # Check for existing user
                if User.objects.filter(email=email).exists():
                    self.message_user(request, f"User {email} already exists!", level=messages.WARNING)
                    return redirect(request.get_full_path())

                # Create personalized invitation
                invitation = TenantInvitation.objects.create(
                    tenant=tenant,
                    email=email,
                    role='admin',  # FORCE ADMIN ROLE
                    invited_by=request.user,
                    is_reusable=False,
                    status='pending',
                    message=f"Hi {first_name} {last_name},\n\nYour new tenant workspace '{tenant.name}' is ready. Click the link to set up your admin account."
                )

                link = self._get_invite_link(request, invitation)

                self.message_user(
                    request,
                    format_html(
                        '<strong>✅ Owner Onboarded!</strong> Invitation created for <strong>{} {}</strong> ({})<br>'
                        'Send them this link:<br>'
                        '<input type="text" value="{}" style="width: 100%; padding: 8px;" readonly onclick="this.select();">',
                        first_name, last_name, email, link
                    ),
                    level=messages.SUCCESS
                )
                return redirect(request.get_full_path())
        else:
            form = OnboardOwnerForm()

        return render(request, 'admin/form_intermediate.html', {
            'title': f'Onboard Owner for: {tenant.name}',
            'objects': queryset,
            'form': form,
            'action': 'onboard_tenant_owner',
            'opts': self.model._meta,
        })

    @admin.action(description="📧 Send Individual Invite")
    def send_individual_invite(self, request, queryset):
        """
        Action for Tenant Admins to send specific single-use invites.
        """
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one tenant.", level=messages.ERROR)
            return

        tenant = queryset.first()

        # Handle Form Submission
        if 'apply' in request.POST:
            form = InviteUserForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                role = form.cleaned_data['role']
                message = form.cleaned_data['message']

                # Create invitation
                invitation = TenantInvitation.objects.create(
                    tenant=tenant,
                    email=email,
                    role=role,
                    invited_by=request.user,
                    is_reusable=False,
                    status='pending',
                    message=message
                )

                link = self._get_invite_link(request, invitation)

                self.message_user(
                    request,
                    format_html(
                        '<strong>✅ Invite Created!</strong> Link for {}:<br>'
                        '<input type="text" value="{}" style="width: 100%; padding: 8px;" readonly onclick="this.select();">',
                        email, link
                    ),
                    level=messages.SUCCESS
                )
                return redirect(request.get_full_path())
        else:
            form = InviteUserForm()

        return render(request, 'admin/form_intermediate.html', {
            'title': f'Invite User to {tenant.name}',
            'objects': queryset,
            'form': form,
            'action': 'send_individual_invite',
            'opts': self.model._meta,
        })

    def _get_invite_link(self, request, invitation):
        """Helper to construct the frontend signup URL."""
        base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        
        # Smart fallback based on host header
        if not base_url or base_url == 'http://localhost:3000':
            host = request.get_host()
            if 'dev' in host:
                base_url = "https://dev.meatscentral.com"
            elif 'uat' in host:
                base_url = "https://uat.meatscentral.com"
            elif 'meatscentral.com' in host:
                base_url = "https://meatscentral.com"
            
        return f"{base_url}/signup?token={invitation.token}"


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
