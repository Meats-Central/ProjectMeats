"""
DEPRECATED: This command was used for django-tenants schema-based multi-tenancy.

ProjectMeats has migrated to SHARED-SCHEMA multi-tenancy where:
- All tenants share one PostgreSQL schema
- Tenant isolation is via tenant_id ForeignKeys
- No Client/Domain models from django-tenants

This command is preserved for historical reference only.
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'DEPRECATED: Schema-based public tenant management removed.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost',
            help='Ignored (deprecated)',
        )

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
                'There is no "public tenant" in shared-schema architecture.\n'
                'All tenants share the same PostgreSQL schema.\n'
                '\n'
                'To create a tenant, use:\n'
                '  python manage.py create_tenant\n'
                '\n'
                '=' * 60
            )
        )
