"""
Management command to set up test tenant for CI/CD environments.
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Set up test tenant for CI/CD environments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant-name',
            default='test_tenant',
            help='Name of the test tenant schema (default: test_tenant)'
        )
        parser.add_argument(
            '--domain',
            default='test.example.com',
            help='Domain for the test tenant (default: test.example.com)'
        )

    def handle(self, *args, **options):
        # Check if django-tenants is configured
        if "postgresql" not in connection.settings_dict.get("ENGINE", ""):
            self.stdout.write(
                self.style.WARNING(
                    "Not using PostgreSQL - skipping tenant setup"
                )
            )
            return

        try:
            from django_tenants.utils import get_tenant_model, schema_context
            from apps.tenants.models import Domain
        except ImportError:
            self.stdout.write(
                self.style.WARNING(
                    "django-tenants not installed - skipping tenant setup"
                )
            )
            return

        tenant_name = options['tenant_name']
        domain_name = options['domain']

        # Create tenant
        Client = get_tenant_model()
        tenant, created = Client.objects.get_or_create(
            schema_name=tenant_name,
            defaults={
                'name': f'Test Tenant ({tenant_name})',
                'paid_until': '2099-12-31',
                'on_trial': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created tenant: {tenant_name}')
            )
        else:
            self.stdout.write(f'Tenant already exists: {tenant_name}')

        # Create domain
        domain, created = Domain.objects.get_or_create(
            domain=domain_name,
            defaults={
                'tenant': tenant,
                'is_primary': True
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f'Created domain: {domain_name}')
            )
        else:
            self.stdout.write(f'Domain already exists: {domain_name}')

        # Migrate tenant schema
        try:
            with schema_context(tenant.schema_name):
                from django.core.management import call_command
                call_command('migrate_schemas', schema_name=tenant.schema_name, verbosity=0)
                self.stdout.write(
                    self.style.SUCCESS(f'Migrated tenant schema: {tenant_name}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not migrate tenant schema: {e}')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Test tenant setup complete: {tenant_name} -> {domain_name}'
            )
        )