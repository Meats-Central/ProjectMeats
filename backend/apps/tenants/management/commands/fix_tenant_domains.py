"""
DEPRECATED: This command was used for django-tenants schema-based multi-tenancy.

ProjectMeats has migrated to SHARED-SCHEMA multi-tenancy where:
- All tenants share one PostgreSQL schema
- Tenant isolation is via tenant_id ForeignKeys
- No Client/Domain models from django-tenants

This command is preserved for historical reference only.
Use TenantDomain model for domain-to-tenant mappings instead.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'DEPRECATED: Schema-based domain management removed. Use TenantDomain model.'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                '\n'
                '=' * 60 + '\n'
                'DEPRECATED COMMAND\n'
                '=' * 60 + '\n'
                '\n'
                'This command was used for django-tenants schema-based multi-tenancy.\n'
                'ProjectMeats now uses shared-schema multi-tenancy.\n'
                '\n'
                'To add domain mappings, use the TenantDomain model directly:\n'
                '\n'
                '  from apps.tenants.models import Tenant, TenantDomain\n'
                '  tenant = Tenant.objects.get(slug="my-tenant")\n'
                '  TenantDomain.objects.create(\n'
                '      tenant=tenant,\n'
                '      domain="my-tenant.example.com",\n'
                '      is_primary=True\n'
                '  )\n'
                '\n'
                '=' * 60
            )
        )
