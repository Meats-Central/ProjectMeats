"""
Management command to initialize a new tenant with admin user and invitation.

This command creates a complete tenant setup including:
- Tenant with schema name
- Primary domain
- Initial admin user (as owner)
- Reusable invitation link

Usage:
    python manage.py init_tenant \\
        --schema-name=acme_corp \\
        --name="ACME Corporation" \\
        --domain=acme.example.com \\
        --admin-email=admin@acme.com \\
        --admin-password=secure_password

    python manage.py init_tenant \\
        --schema-name=demo_co \\
        --name="Demo Company" \\
        --domain=demo.localhost \\
        --admin-email=admin@demo.localhost \\
        --admin-password=demo_pass \\
        --on-trial \\
        --trial-days=30
"""
import re
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.tenants.models import Tenant, TenantDomain, TenantInvitation, TenantUser


class Command(BaseCommand):
    """Management command to initialize a new tenant with admin user."""

    help = (
        "Initialize a new tenant with domain, admin user, and invitation link. "
        "Creates a complete tenant setup for onboarding."
    )

    def add_arguments(self, parser):
        """Add command-line arguments."""
        # Required arguments
        parser.add_argument(
            "--schema-name",
            type=str,
            required=True,
            help=(
                "Database schema name (e.g., 'acme_corp'). "
                "Must be unique and PostgreSQL-compatible."
            ),
        )
        parser.add_argument(
            "--name",
            type=str,
            required=True,
            help="Tenant organization name (e.g., 'ACME Corporation')",
        )
        parser.add_argument(
            "--domain",
            type=str,
            required=True,
            help="Primary domain for the tenant (e.g., 'acme.example.com')",
        )
        parser.add_argument(
            "--admin-email",
            type=str,
            required=True,
            help="Email address for the initial admin user",
        )
        parser.add_argument(
            "--admin-password",
            type=str,
            required=True,
            help="Password for the initial admin user",
        )

        # Optional arguments
        parser.add_argument(
            "--admin-username",
            type=str,
            help="Username for admin (defaults to email prefix)",
        )
        parser.add_argument(
            "--slug",
            type=str,
            help="URL-friendly identifier (auto-generated from schema-name if not provided)",
        )
        parser.add_argument(
            "--contact-email",
            type=str,
            help="Primary contact email for the tenant (defaults to admin email)",
        )
        parser.add_argument(
            "--on-trial",
            action="store_true",
            help="Mark tenant as trial account",
        )
        parser.add_argument(
            "--trial-days",
            type=int,
            default=30,
            help="Number of trial days (default: 30)",
        )
        parser.add_argument(
            "--invitation-days",
            type=int,
            default=7,
            help="Days until invitation expires (default: 7)",
        )
        parser.add_argument(
            "--skip-invitation",
            action="store_true",
            help="Skip creating the invitation link",
        )

    def handle(self, *args, **options):
        """Execute the command."""
        verbosity = options.get("verbosity", 1)

        # Get required parameters
        slug = options["slug"]
        name = options["name"]
        domain = options["domain"].lower()
        admin_email = options["admin_email"]
        admin_password = options["admin_password"]

        # Get optional parameters with defaults
        admin_username = options.get("admin_username") or admin_email.split("@")[0]
        slug = options.get("slug") or slug.replace("_", "-")
        contact_email = options.get("contact_email") or admin_email
        on_trial = options.get("on_trial", False)
        trial_days = options.get("trial_days", 30)
        invitation_days = options.get("invitation_days", 7)
        skip_invitation = options.get("skip_invitation", False)

        # Validate slug
        if not self._validate_slug(slug):
            raise CommandError(
                f"Invalid schema name: {slug}. "
                f"Must start with a letter or underscore, contain only alphanumeric "
                f"characters and underscores, and be max 63 characters."
            )

        # Validate email format
        if not self._validate_email(admin_email):
            raise CommandError(f"Invalid email format: {admin_email}")

        if verbosity >= 2:
            self.stdout.write("\n🔧 Tenant Initialization Configuration:")
            self.stdout.write(f"   - Schema Name: {slug}")
            self.stdout.write(f"   - Name: {name}")
            self.stdout.write(f"   - Slug: {slug}")
            self.stdout.write(f"   - Domain: {domain}")
            self.stdout.write(f"   - Contact Email: {contact_email}")
            self.stdout.write(f"   - Admin Username: {admin_username}")
            self.stdout.write(f"   - Admin Email: {admin_email}")
            self.stdout.write(f"   - On Trial: {on_trial}")
            if on_trial:
                self.stdout.write(f"   - Trial Days: {trial_days}")
            self.stdout.write("")

        try:
            with transaction.atomic():
                # 1. Create Tenant
                tenant = self._create_tenant(
                    slug=slug,
                    name=name,
                    slug=slug,
                    contact_email=contact_email,
                    on_trial=on_trial,
                    trial_days=trial_days,
                    verbosity=verbosity,
                )

                # 2. Create Domain
                tenant_domain = self._create_domain(
                    tenant=tenant,
                    domain=domain,
                    verbosity=verbosity,
                )

                # 3. Create Admin User
                admin_user = self._create_admin_user(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    verbosity=verbosity,
                )

                # 4. Associate Admin with Tenant
                tenant_user = self._associate_user_with_tenant(
                    tenant=tenant,
                    user=admin_user,
                    role="owner",
                    verbosity=verbosity,
                )

                # 5. Create Invitation (optional)
                invitation = None
                invitation_url = None
                if not skip_invitation:
                    invitation, invitation_url = self._create_invitation(
                        tenant=tenant,
                        domain=domain,
                        invited_by=admin_user,
                        days_valid=invitation_days,
                        verbosity=verbosity,
                    )

                # Print summary
                self._print_summary(
                    tenant=tenant,
                    tenant_domain=tenant_domain,
                    admin_user=admin_user,
                    tenant_user=tenant_user,
                    invitation=invitation,
                    invitation_url=invitation_url,
                    verbosity=verbosity,
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error: {str(e)}"))
            if verbosity >= 2:
                import traceback

                self.stdout.write("\nFull traceback:")
                self.stdout.write(traceback.format_exc())
            raise

    def _validate_slug(self, slug: str) -> bool:
        """Validate schema name follows PostgreSQL identifier rules."""
        if len(slug) > 63:
            return False
        pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
        return pattern.match(slug) is not None

    def _validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return pattern.match(email) is not None

    def _create_tenant(
        self,
        slug: str,
        name: str,
        slug: str,
        contact_email: str,
        on_trial: bool,
        trial_days: int,
        verbosity: int,
    ) -> Tenant:
        """Create the tenant."""
        if verbosity >= 1:
            self.stdout.write(f"\n🏢 Creating tenant: {name}...")

        # Check for existing tenant
        if Tenant.objects.filter(slug=slug).exists():
            raise CommandError(f'Tenant with slug "{slug}" already exists')

        if Tenant.objects.filter(slug=slug).exists():
            raise CommandError(f'Tenant with slug "{slug}" already exists')

        trial_ends_at = None
        if on_trial:
            trial_ends_at = timezone.now() + timedelta(days=trial_days)

        tenant = Tenant.objects.create(
            name=name,
            slug=slug,
            slug=slug,
            contact_email=contact_email,
            is_active=True,
            is_trial=on_trial,
            trial_ends_at=trial_ends_at,
        )

        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(f"   ✅ Tenant created: {tenant.name} ({tenant.id})")
            )

        return tenant

    def _create_domain(
        self,
        tenant: Tenant,
        domain: str,
        verbosity: int,
    ) -> TenantDomain:
        """Create the tenant domain."""
        if verbosity >= 1:
            self.stdout.write(f"\n🌐 Creating domain: {domain}...")

        # Check for existing domain
        if TenantDomain.objects.filter(domain=domain).exists():
            raise CommandError(f'Domain "{domain}" already exists')

        tenant_domain = TenantDomain.objects.create(
            domain=domain,
            tenant=tenant,
            is_primary=True,
        )

        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(f"   ✅ Domain created: {tenant_domain.domain} (primary)")
            )

        return tenant_domain

    def _create_admin_user(
        self,
        username: str,
        email: str,
        password: str,
        verbosity: int,
    ) -> User:
        """Create the admin user."""
        if verbosity >= 1:
            self.stdout.write(f"\n👤 Creating admin user: {username}...")

        # Check for existing user
        if User.objects.filter(username=username).exists():
            raise CommandError(f'User with username "{username}" already exists')

        if User.objects.filter(email=email).exists():
            raise CommandError(f'User with email "{email}" already exists')

        admin_user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,  # Allow Django admin access
            is_active=True,
        )

        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(f"   ✅ Admin user created: {admin_user.username}")
            )

        return admin_user

    def _associate_user_with_tenant(
        self,
        tenant: Tenant,
        user: User,
        role: str,
        verbosity: int,
    ) -> TenantUser:
        """Associate user with tenant."""
        if verbosity >= 1:
            self.stdout.write(f"\n🔗 Associating admin as tenant {role}...")

        tenant_user = TenantUser.objects.create(
            tenant=tenant,
            user=user,
            role=role,
            is_active=True,
        )

        if verbosity >= 1:
            self.stdout.write(
                self.style.SUCCESS(f"   ✅ Admin associated with tenant as {role}")
            )

        return tenant_user

    def _create_invitation(
        self,
        tenant: Tenant,
        domain: str,
        invited_by: User,
        days_valid: int,
        verbosity: int,
    ) -> tuple:
        """Create a reusable invitation link."""
        if verbosity >= 1:
            self.stdout.write("\n📧 Creating reusable invitation link...")

        invitation = TenantInvitation.objects.create(
            tenant=tenant,
            email=f"invite@{domain}",
            role="user",
            invited_by=invited_by,
            expires_at=timezone.now() + timedelta(days=days_valid),
            message=f"Welcome to {tenant.name}! Use this link to join our organization.",
        )

        # Generate invitation URL
        protocol = "https" if not domain.startswith("localhost") else "http"
        invitation_url = f"{protocol}://{domain}/signup/?token={invitation.token}"

        if verbosity >= 1:
            self.stdout.write(self.style.SUCCESS("   ✅ Invitation created"))
            self.stdout.write(f"   📎 URL: {invitation_url}")

        return invitation, invitation_url

    def _print_summary(
        self,
        tenant: Tenant,
        tenant_domain: TenantDomain,
        admin_user: User,
        tenant_user: TenantUser,
        invitation,
        invitation_url: str,
        verbosity: int,
    ):
        """Print initialization summary."""
        if verbosity < 1:
            return

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("TENANT INITIALIZATION COMPLETE"))
        self.stdout.write("=" * 60)

        self.stdout.write("\nTenant Details:")
        self.stdout.write(f"  - ID: {tenant.id}")
        self.stdout.write(f"  - Name: {tenant.name}")
        self.stdout.write(f"  - Slug: {tenant.slug}")
        self.stdout.write(f"  - Schema: {tenant.slug}")
        self.stdout.write(f"  - Domain: {tenant_domain.domain}")
        self.stdout.write(f"  - Trial: {'Yes' if tenant.is_trial else 'No'}")
        if tenant.trial_ends_at:
            self.stdout.write(
                f"  - Trial Ends: {tenant.trial_ends_at.strftime('%Y-%m-%d')}"
            )

        self.stdout.write("\nAdmin User:")
        self.stdout.write(f"  - Username: {admin_user.username}")
        self.stdout.write(f"  - Email: {admin_user.email}")
        self.stdout.write(f"  - Role: {tenant_user.role}")

        if invitation:
            self.stdout.write("\nInvitation Link:")
            self.stdout.write(f"  - URL: {invitation_url}")
            self.stdout.write(f"  - Token: {invitation.token}")
            self.stdout.write(
                f"  - Expires: {invitation.expires_at.strftime('%Y-%m-%d %H:%M')}"
            )

        self.stdout.write("\nNext Steps:")
        self.stdout.write("  1. Configure tenant settings as needed")
        self.stdout.write("  2. Share the invitation link with team members")
        self.stdout.write("  3. Set up additional domains if needed")
        self.stdout.write("")
