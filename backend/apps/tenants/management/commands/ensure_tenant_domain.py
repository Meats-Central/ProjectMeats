"""
Management command to ensure a TenantDomain entry exists for a specific domain.

This command is useful for fixing staging/production domain issues where
a domain entry may be missing from the database.

Usage:
    python manage.py ensure_tenant_domain staging.meatscentral.com --tenant-slug=default
    python manage.py ensure_tenant_domain example.com --tenant-id=<uuid>
"""

from django.core.management.base import BaseCommand, CommandError
from apps.tenants.models import Tenant, TenantDomain


class Command(BaseCommand):
    help = "Ensure a TenantDomain entry exists for a specific domain"

    def add_arguments(self, parser):
        parser.add_argument(
            "domain",
            type=str,
            help="The domain name to ensure exists (e.g., staging.meatscentral.com)",
        )
        parser.add_argument(
            "--tenant-slug",
            type=str,
            help="The slug of the tenant to associate with this domain",
        )
        parser.add_argument(
            "--tenant-id",
            type=str,
            help="The UUID of the tenant to associate with this domain",
        )
        parser.add_argument(
            "--is-primary",
            action="store_true",
            default=True,
            help="Set this domain as the primary domain for the tenant (default: True)",
        )
        parser.add_argument(
            "--create-tenant",
            action="store_true",
            help="Create the tenant if it doesn't exist (requires --tenant-slug)",
        )

    def handle(self, *args, **options):
        domain = options["domain"].lower()
        tenant_slug = options.get("tenant_slug")
        tenant_id = options.get("tenant_id")
        is_primary = options.get("is_primary", True)
        create_tenant = options.get("create_tenant", False)

        # Validate inputs
        if not tenant_slug and not tenant_id:
            raise CommandError(
                "You must provide either --tenant-slug or --tenant-id"
            )

        # Find or create the tenant
        tenant = None
        if tenant_id:
            try:
                tenant = Tenant.objects.get(id=tenant_id)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found tenant by ID: {tenant.name} ({tenant.slug})"
                    )
                )
            except Tenant.DoesNotExist:
                raise CommandError(f"Tenant with ID {tenant_id} does not exist")
        elif tenant_slug:
            try:
                tenant = Tenant.objects.get(slug=tenant_slug)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Found tenant by slug: {tenant.name} ({tenant.slug})"
                    )
                )
            except Tenant.DoesNotExist:
                if create_tenant:
                    # Create a new tenant
                    tenant = Tenant.objects.create(
                        name=tenant_slug.replace("-", " ").title(),
                        slug=tenant_slug,
                        contact_email=f"admin@{domain}",
                        is_active=True,
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created new tenant: {tenant.name} ({tenant.slug})"
                        )
                    )
                else:
                    raise CommandError(
                        f"Tenant with slug '{tenant_slug}' does not exist. "
                        f"Use --create-tenant to create it."
                    )

        # Check if domain entry already exists
        try:
            domain_obj = TenantDomain.objects.get(domain=domain)
            if domain_obj.tenant == tenant:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Domain entry already exists and is correctly configured:\n"
                        f"  Domain: {domain_obj.domain}\n"
                        f"  Tenant: {domain_obj.tenant.name} ({domain_obj.tenant.slug})\n"
                        f"  Primary: {domain_obj.is_primary}"
                    )
                )
                return
            else:
                # Domain exists but points to different tenant
                self.stdout.write(
                    self.style.WARNING(
                        f"Domain entry exists but points to different tenant:\n"
                        f"  Current: {domain_obj.tenant.name} ({domain_obj.tenant.slug})\n"
                        f"  Requested: {tenant.name} ({tenant.slug})"
                    )
                )
                
                # Ask for confirmation to update
                confirm = input("Update domain to point to requested tenant? [y/N]: ")
                if confirm.lower() == "y":
                    domain_obj.tenant = tenant
                    domain_obj.is_primary = is_primary
                    domain_obj.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated domain entry to point to {tenant.name}"
                        )
                    )
                else:
                    self.stdout.write("No changes made")
                return
        except TenantDomain.DoesNotExist:
            pass

        # Create the domain entry
        domain_obj = TenantDomain.objects.create(
            domain=domain,
            tenant=tenant,
            is_primary=is_primary,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Created TenantDomain entry:\n"
                f"  Domain: {domain_obj.domain}\n"
                f"  Tenant: {domain_obj.tenant.name} ({domain_obj.tenant.slug})\n"
                f"  Primary: {domain_obj.is_primary}"
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Domain {domain} is now configured to route to tenant {tenant.slug}"
            )
        )
