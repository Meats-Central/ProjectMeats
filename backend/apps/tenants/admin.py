from django.contrib import admin, messages
from django.utils.html import format_html
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import path
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


class FullOnboardForm(forms.Form):
    """Form to create Tenant + Owner Invite simultaneously from scratch."""
    tenant_name = forms.CharField(label="Company Name", max_length=255, required=True)
    slug = forms.SlugField(
        label="URL Slug (e.g. acme-corp)", 
        help_text="Unique identifier for the tenant URL",
        required=True
    )
    contact_email = forms.EmailField(label="Company Contact Email", required=True)
    
    owner_email = forms.EmailField(
        label="Owner Email", 
        help_text="We will send the invitation here immediately.",
        required=True
    )
    owner_first_name = forms.CharField(label="Owner First Name", required=True)
    owner_last_name = forms.CharField(label="Owner Last Name", required=True)
    
    on_trial = forms.BooleanField(
        label="Start 30-Day Trial?", 
        initial=True, 
        required=False
    )


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """
    Admin interface for Tenant model with tiered actions.
    
    Actions:
    1. Generate Team Invite (Superuser Only): Create generic reusable link.
    2. Onboard Owner (Superuser Only): Invite specific owner with personalized message.
    3. Send Individual Invite (Tenant Admin+): Invite specific email.
    """
    
    # Custom template with "Onboard New Tenant Wizard" button
    change_list_template = "admin/tenants/tenant/change_list.html"

    list_display = [
        "name",
        "slug",
        "test_account_info",  # NEW: Show test credentials in list
        "domain",
        "is_active",
        "is_trial",
        "trial_ends_at",
        "created_at",
    ]
    list_filter = ["is_active", "is_trial", "created_at"]
    search_fields = ["name", "slug", "domain", "contact_email"]
    readonly_fields = ["id", "created_at", "updated_at", "test_credentials_display"]  # NEW: Added test_credentials_display
    
    actions = ['generate_team_invite', 'onboard_tenant_owner', 'send_individual_invite']

    fieldsets = [
        ("Basic Information", {"fields": ("name", "slug", "schema_name", "domain")}),
        ("Test Access (Dev/UAT Only)", {"fields": ("test_credentials_display",)}),  # NEW: Test credentials section
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
                    return

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
    
    def get_urls(self):
        """Add custom URL for onboard wizard."""
        urls = super().get_urls()
        custom_urls = [
            path('onboard/', self.admin_site.admin_view(self.onboard_view), name='tenant-onboard'),
        ]
        return custom_urls + urls
    
    def onboard_view(self, request):
        """
        Onboard New Tenant from Scratch wizard.
        Creates Tenant + Domain + Owner Invitation in one flow.
        """
        from django.utils import timezone
        
        if request.method == 'POST':
            form = FullOnboardForm(request.POST)
            if form.is_valid():
                try:
                    # 1. Create Tenant
                    tenant = Tenant.objects.create(
                        name=form.cleaned_data['tenant_name'],
                        slug=form.cleaned_data['slug'],
                        contact_email=form.cleaned_data['contact_email'],
                        is_trial=form.cleaned_data['on_trial'],
                        trial_ends_at=timezone.now() + timezone.timedelta(days=30) if form.cleaned_data['on_trial'] else None,
                        created_by=request.user
                    )
                    
                    # 2. Create Default Domain
                    TenantDomain.objects.create(
                        tenant=tenant,
                        domain=f"{tenant.slug}.localhost",  # Adjust based on environment
                        is_primary=True
                    )

                    # 3. Create Owner Invitation (Signal will handle Email)
                    first_name = form.cleaned_data['owner_first_name']
                    last_name = form.cleaned_data['owner_last_name']
                    owner_email = form.cleaned_data['owner_email']
                    
                    invitation = TenantInvitation.objects.create(
                        tenant=tenant,
                        email=owner_email,
                        role='owner',
                        invited_by=request.user,
                        message=f"Welcome {first_name} {last_name}, your new workspace '{tenant.name}' is ready! Click the link to set up your account."
                    )

                    self.message_user(
                        request, 
                        f"✅ Tenant '{tenant.name}' created and invite sent to {owner_email}!", 
                        messages.SUCCESS
                    )
                    return redirect('admin:tenants_tenant_changelist')
                    
                except Exception as e:
                    self.message_user(request, f"❌ Error: {str(e)}", messages.ERROR)
        else:
            form = FullOnboardForm()

        context = {
            **self.admin_site.each_context(request),
            'title': '🚀 Onboard New Tenant From Scratch',
            'form': form,
            'opts': self.model._meta,
            'action': 'onboard',
            'objects': [],  # No selected objects for this wizard
        }
        return render(request, 'admin/form_intermediate.html', context)
    
    def test_account_info(self, obj):
        """
        Show quick login info in list view for superusers on test tenants.
        Only displays for tenants with schema_name starting with 'test_'.
        """
        if not obj.schema_name or not obj.schema_name.startswith('test_'):
            return "—"
            
        # Try to find the admin user for this tenant
        admin_user = User.objects.filter(
            tenants__tenant=obj, 
            tenants__role='admin',
            tenants__is_active=True
        ).first()
        
        if admin_user:
            return format_html(
                '<span style="color: green; font-weight: bold;">U: {}</span><br>'
                '<span style="font-family: monospace; font-size: 11px;">P: password123!</span>',
                admin_user.username
            )
        return "No Admin"
    test_account_info.short_description = "Test Creds"
    
    def test_credentials_display(self, obj):
        """
        Detailed read-only field for object view showing test credentials.
        Only displays for test tenants (schema_name starts with 'test_').
        """
        if not obj.schema_name or not obj.schema_name.startswith('test_'):
            return format_html(
                '<div style="background: #f5f5f5; padding: 15px; border-radius: 5px; border: 1px solid #ddd;">'
                '<p style="color: #666;"><em>Not a test tenant. This section only applies to tenants '
                'created via the seed_tenants management command.</em></p>'
                '</div>'
            )
            
        admin_user = User.objects.filter(
            tenants__tenant=obj, 
            tenants__role='admin',
            tenants__is_active=True
        ).first()
        
        if admin_user:
            return format_html(
                '<div style="background: #e8f5e9; padding: 15px; border-radius: 5px; border: 1px solid #c8e6c9;">'
                '<h3 style="margin-top: 0;">🧪 Test Account Credentials</h3>'
                '<table style="width: 100%; border-collapse: collapse;">'
                '<tr><td style="padding: 8px 0; font-weight: bold;">Username:</td><td style="padding: 8px 0; font-family: monospace;">{}</td></tr>'
                '<tr><td style="padding: 8px 0; font-weight: bold;">Password:</td><td style="padding: 8px 0; font-family: monospace;">password123!</td></tr>'
                '<tr><td style="padding: 8px 0; font-weight: bold;">Role:</td><td style="padding: 8px 0;">Tenant Admin</td></tr>'
                '<tr><td style="padding: 8px 0; font-weight: bold;">Email:</td><td style="padding: 8px 0;">{}</td></tr>'
                '</table>'
                '<p style="margin-bottom: 0; margin-top: 10px; color: #2e7d32;"><em><strong>Note:</strong> This user has full Tenant Admin privileges.</em></p>'
                '</div>',
                admin_user.username,
                admin_user.email
            )
        return format_html(
            '<div style="background: #fff3cd; padding: 15px; border-radius: 5px; border: 1px solid #ffc107;">'
            '<p style="margin: 0;">⚠️ No admin user found for this test tenant.</p>'
            '</div>'
        )
    test_credentials_display.short_description = "Test Login Credentials"


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
            "fields": ("is_reusable", "max_uses", "usage_count"),
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
        if obj.is_reusable:
            return format_html('<strong style="color: #0066cc;">{}</strong>', '🔗 Reusable Link')
        return obj.email or "—"
    email_or_type.short_description = "Email / Type"
    
    def usage_info(self, obj):
        if obj.is_reusable:
            percentage = (obj.usage_count / obj.max_uses * 100) if obj.max_uses > 0 else 0
            color = "#28a745" if percentage < 80 else "#ffc107" if percentage < 100 else "#dc3545"
            return format_html(
                '<span style="color: {};">{} / {} uses ({}%)</span>',
                color, obj.usage_count, obj.max_uses, int(percentage)
            )
        return "—"
    usage_info.short_description = "Usage"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("tenant", "invited_by", "accepted_by")


@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    """Admin interface for TenantDomain model."""

    list_display = ["domain", "tenant", "is_primary", "created_at"]
    list_filter = ["is_primary", "created_at"]
    search_fields = ["domain", "tenant__name", "tenant__slug"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = [
        ("Domain Information", {"fields": ("domain", "tenant", "is_primary")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ["collapse"]}),
    ]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("tenant")
