"""
Management command to add a domain to a tenant.

This command adds or updates a TenantDomain entry for an existing tenant.
Useful for configuring custom domains for tenants in different environments.

Usage:
    python manage.py add_tenant_domain --domain=staging.meatscentral.com --tenant-slug=meatscentral
    python manage.py add_tenant_domain --domain=uat.meatscentral.com --tenant-slug=meatscentral --is-primary
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.tenants.models import Tenant, TenantDomain


class Command(BaseCommand):
    help = 'Add or update a domain entry for an existing tenant'

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            '--domain',
            type=str,
            required=True,
            help='Domain name (e.g., "staging.meatscentral.com")'
        )
        parser.add_argument(
            '--tenant-slug',
            type=str,
            required=True,
            help='Slug of the tenant to associate with this domain'
        )
        parser.add_argument(
            '--is-primary',
            action='store_true',
            default=False,
            help='Mark this domain as the primary domain for the tenant'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            default=False,
            help='Update existing domain if it already exists'
        )

    def handle(self, *args, **options):
        """Execute the command."""
        domain_name = options['domain'].lower().strip()
        tenant_slug = options['tenant_slug'].lower().strip()
        is_primary = options['is_primary']
        update = options['update']

        # Validate tenant exists
        try:
            tenant = Tenant.objects.get(slug=tenant_slug)
        except Tenant.DoesNotExist:
            raise CommandError(f"Tenant with slug '{tenant_slug}' does not exist")

        # Check if domain already exists
        try:
            domain_obj = TenantDomain.objects.get(domain=domain_name)
            
            if not update:
                self.stdout.write(
                    self.style.WARNING(
                        f"Domain '{domain_name}' already exists for tenant '{domain_obj.tenant.slug}'. "
                        f"Use --update to modify it."
                    )
                )
                return
            
            # Update existing domain
            old_tenant = domain_obj.tenant
            domain_obj.tenant = tenant
            domain_obj.is_primary = is_primary
            domain_obj.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated domain '{domain_name}' "
                    f"(moved from '{old_tenant.slug}' to '{tenant.slug}', "
                    f"primary={is_primary})"
                )
            )
            
        except TenantDomain.DoesNotExist:
            # Create new domain
            with transaction.atomic():
                domain_obj = TenantDomain.objects.create(
                    domain=domain_name,
                    tenant=tenant,
                    is_primary=is_primary
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully created domain '{domain_name}' for tenant '{tenant.slug}' "
                        f"(primary={is_primary})"
                    )
                )

        # Display tenant information
        self.stdout.write("\nTenant Information:")
        self.stdout.write(f"  Name: {tenant.name}")
        self.stdout.write(f"  Slug: {tenant.slug}")
        self.stdout.write(f"  ID: {tenant.id}")
        self.stdout.write(f"  Active: {tenant.is_active}")
        
        # List all domains for this tenant
        self.stdout.write("\nAll domains for this tenant:")
        tenant_domains = TenantDomain.objects.filter(tenant=tenant).order_by('-is_primary', 'domain')
        for td in tenant_domains:
            primary_marker = " [PRIMARY]" if td.is_primary else ""
            self.stdout.write(f"  - {td.domain}{primary_marker}")
