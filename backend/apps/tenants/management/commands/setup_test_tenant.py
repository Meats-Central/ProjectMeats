"""
Management command to set up test tenant for CI/CD environments.

SHARED-SCHEMA MULTI-TENANCY:
This command uses ProjectMeats' custom shared-schema multi-tenancy approach,
NOT django-tenants. All tenants share the same PostgreSQL schema with tenant_id
foreign keys for data isolation.
"""
from django.core.management.base import BaseCommand
from django.db import connection
from apps.tenants.models import Tenant, TenantDomain


class Command(BaseCommand):
    help = 'Set up test tenant for CI/CD environments (shared-schema approach)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-name',
            default='Test Tenant',
            help='Name of the test tenant (default: Test Tenant)'
        )
        parser.add_argument(
            '--tenant-slug',
            default='test-tenant',
            help='Slug of the test tenant (default: test-tenant)'
        )
        parser.add_argument(
            '--domain',
            default='test.example.com',
            help='Domain for the test tenant (default: test.example.com)'
        )

    def handle(self, *args, **options):
        # Check if PostgreSQL is configured
        if "postgresql" not in connection.settings_dict.get("ENGINE", ""):
            self.stdout.write(
                self.style.WARNING(
                    "Not using PostgreSQL - skipping tenant setup"
                )
            )
            return

        tenant_name = options['tenant_name']
        tenant_slug = options['tenant_slug']
        domain_name = options['domain']

        # Create tenant in shared schema (idempotent with get_or_create)
        tenant, created = Tenant.objects.get_or_create(
            slug=tenant_slug,
            defaults={
                'name': tenant_name,
                'contact_email': f'admin@{tenant_slug}.com',
                'is_active': True,
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created tenant: {tenant_name} ({tenant_slug})')
            )
        else:
            self.stdout.write(f'  Tenant already exists: {tenant_name}')

        # Create domain mapping
        domain, created = TenantDomain.objects.get_or_create(
            domain=domain_name,
            defaults={
                'tenant': tenant,
                'is_primary': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created domain: {domain_name} -> {tenant_slug}')
            )
        else:
            self.stdout.write(f'  Domain already exists: {domain_name}')

        # No schema migrations needed - we use shared schema
        # Standard migrations are run once for all tenants
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Test tenant setup complete: {tenant_name} -> {domain_name}'
            )
        )
        self.stdout.write(
            self.style.NOTICE(
                '\nNote: Using shared-schema multi-tenancy. '
                'Run "python manage.py migrate" for schema updates.'
            )
        )