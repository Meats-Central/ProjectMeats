"""
Management command to test invitation creation and email sending.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.tenants.models import Tenant, TenantInvitation
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Test invitation creation and email delivery'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email address to send test invitation to',
        )
        parser.add_argument(
            '--tenant-slug',
            type=str,
            default='test-tenant',
            help='Tenant slug (creates if not exists)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Create invitation but don\'t actually save (tests signal registration)',
        )

    def handle(self, *args, **options):
        email = options['email']
        tenant_slug = options['tenant_slug']
        dry_run = options['dry_run']
        
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("🧪 Invitation Creation Test"))
        self.stdout.write("=" * 60)
        
        # Check email configuration first
        self.stdout.write("\n🔧 Email Configuration Check:")
        self.stdout.write(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        self.stdout.write(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        self.stdout.write(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        
        password_status = '✅ SET' if settings.EMAIL_HOST_PASSWORD else '❌ NOT SET'
        self.stdout.write(f"  EMAIL_HOST_PASSWORD: {password_status}")
        self.stdout.write(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        
        if not settings.EMAIL_HOST_PASSWORD:
            self.stdout.write(self.style.WARNING(
                "\n⚠️  EMAIL_HOST_PASSWORD not set - emails will fail to send!"
            ))
        
        # Check for test tenant
        self.stdout.write(f"\n🏢 Checking for tenant: {tenant_slug}")
        tenant, created = Tenant.objects.get_or_create(
            slug=tenant_slug,
            defaults={
                'name': 'Test Tenant',
                'schema_name': f'{tenant_slug}_schema',
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f"  ✅ Created tenant: {tenant.name}"))
        else:
            self.stdout.write(f"  ✅ Found tenant: {tenant.name}")
        
        # Get or create invited_by user (for the signal)
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@meatscentral.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        # Create invitation
        self.stdout.write(f"\n📧 Creating invitation for: {email}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("  🔸 DRY RUN - Not saving invitation"))
            invitation = TenantInvitation(
                tenant=tenant,
                email=email,
                role='user',
                invited_by=admin_user,
                expires_at=timezone.now() + timedelta(days=7),
                message="Test invitation from management command",
                status='pending',
            )
            self.stdout.write("  ℹ️  Invitation created but not saved (signal won't fire)")
            self.stdout.write(f"  Token: {invitation.token}")
        else:
            try:
                # Check if invitation already exists
                existing = TenantInvitation.objects.filter(
                    email=email,
                    tenant=tenant,
                    status='pending'
                ).first()
                
                if existing:
                    self.stdout.write(self.style.WARNING(
                        f"  ⚠️  Pending invitation already exists (created {existing.created_at})"
                    ))
                    self.stdout.write(f"  Token: {existing.token}")
                    self.stdout.write(f"  Expires: {existing.expires_at}")
                    
                    revoke = input("\nRevoke old invitation and create new one? (y/N): ")
                    if revoke.lower() == 'y':
                        existing.status = 'revoked'
                        existing.save()
                        self.stdout.write(self.style.SUCCESS("  ✅ Old invitation revoked"))
                    else:
                        self.stdout.write("  Keeping existing invitation")
                        return
                
                # Create new invitation (signal will fire on save)
                self.stdout.write("\n  📤 Creating invitation (signal will trigger email)...")
                invitation = TenantInvitation.objects.create(
                    tenant=tenant,
                    email=email,
                    role='user',
                    invited_by=admin_user,
                    expires_at=timezone.now() + timedelta(days=7),
                    message="Test invitation - if you receive this email, the integration is working!",
                    status='pending',
                )
                
                self.stdout.write(self.style.SUCCESS("\n✅ Invitation created successfully!"))
                self.stdout.write(f"  ID: {invitation.id}")
                self.stdout.write(f"  Token: {invitation.token}")
                self.stdout.write(f"  Expires: {invitation.expires_at}")
                self.stdout.write(f"  Status: {invitation.status}")
                
                # Check logs for email sending
                self.stdout.write("\n📬 Email Status:")
                if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                    self.stdout.write(self.style.WARNING(
                        "  ⚠️  Using console backend - check logs for email output"
                    ))
                elif not settings.EMAIL_HOST_PASSWORD:
                    self.stdout.write(self.style.ERROR(
                        "  ❌ EMAIL_HOST_PASSWORD not set - email send will fail"
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        "  ✅ SMTP configured - check recipient inbox"
                    ))
                    self.stdout.write(f"  From: {settings.DEFAULT_FROM_EMAIL}")
                    self.stdout.write(f"  To: {email}")
                
                # Build invite link
                frontend_url = getattr(settings, 'FRONTEND_URL', 'https://meatscentral.com')
                invite_url = f"{frontend_url}/signup?token={invitation.token}"
                self.stdout.write(f"\n🔗 Invitation Link:")
                self.stdout.write(f"  {invite_url}")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"\n❌ Failed to create invitation: {e}"))
                import traceback
                traceback.print_exc()
