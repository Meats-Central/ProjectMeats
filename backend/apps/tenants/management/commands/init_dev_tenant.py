"""
Management command to initialize the Development Tenant and map dev domains.

This command creates a default development tenant and maps both frontend and backend
dev domains to it, ensuring the Dev environment works as a "Single Tenant" app.

CRITICAL: This fixes the "No tenant for hostname 'dev-backend.meatscentral.com'" error
by mapping the domain to a tenant schema where the Suppliers table actually exists.
"""
from django.core.management.base import BaseCommand
from django_tenants.utils import get_tenant_model, get_tenant_domain_model


class Command(BaseCommand):
    help = 'Initialize the Development Tenant and map dev-backend domain'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--tenant-name',
            type=str,
            default='Dev Corp',
            help='Name for the development tenant (default: Dev Corp)',
        )
        parser.add_argument(
            '--schema-name',
            type=str,
            default='dev_tenant',
            help='Schema name for development tenant (default: dev_tenant)',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        tenant_name = options.get('tenant_name')
        schema_name = options.get('schema_name')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        Tenant = get_tenant_model()
        Domain = get_tenant_domain_model()

        self.stdout.write(self.style.HTTP_INFO('='*70))
        self.stdout.write(self.style.HTTP_INFO('INITIALIZING DEVELOPMENT TENANT'))
        self.stdout.write(self.style.HTTP_INFO('='*70))

        # 1. Create/Get the "Dev Tenant" (Holds the Meat Data)
        self.stdout.write(f'\n1. Setting up tenant: {tenant_name} (schema: {schema_name})')
        
        if dry_run:
            exists = Tenant.objects.filter(schema_name=schema_name).exists()
            if exists:
                self.stdout.write(f"  [EXISTS] Tenant with schema {schema_name}")
            else:
                self.stdout.write(self.style.SUCCESS(f"  [WOULD CREATE] Tenant: {tenant_name} ({schema_name})"))
            tenant = Tenant.objects.filter(schema_name=schema_name).first()
        else:
            tenant, created = Tenant.objects.get_or_create(
                schema_name=schema_name,
                defaults={'name': tenant_name}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Created Tenant: {tenant_name} ({schema_name})")
                )
            else:
                self.stdout.write(f"  - Tenant {tenant_name} already exists")

        # 2. Map the Frontend/Backend Domains to this Tenant
        self.stdout.write('\n2. Mapping domains to tenant:')
        
        domains_to_map = [
            {
                'domain': 'dev-backend.meatscentral.com',
                'is_primary': True,
                'description': 'Backend API domain (FIXES 404 ERROR)'
            },
            {
                'domain': 'dev.meatscentral.com',
                'is_primary': False,
                'description': 'Frontend origin domain'
            },
        ]

        for domain_config in domains_to_map:
            domain_url = domain_config['domain']
            is_primary = domain_config['is_primary']
            description = domain_config['description']
            
            if dry_run:
                exists = Domain.objects.filter(domain=domain_url).exists()
                if exists:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  [EXISTS] {domain_url} - {description}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [WOULD CREATE] {domain_url} (primary: {is_primary}) - {description}"
                        )
                    )
            else:
                existing = Domain.objects.filter(domain=domain_url).first()
                
                if existing:
                    # Check if it points to the correct tenant
                    if existing.tenant.schema_name != schema_name:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠️  Domain {domain_url} exists but points to {existing.tenant.schema_name}"
                            )
                        )
                        self.stdout.write(f"     Updating to point to {schema_name}...")
                        existing.tenant = tenant
                        existing.is_primary = is_primary
                        existing.save()
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Updated {domain_url} -> {schema_name}")
                        )
                    else:
                        self.stdout.write(
                            f"  - Domain {domain_url} already correctly mapped"
                        )
                else:
                    Domain.objects.create(
                        domain=domain_url,
                        tenant=tenant,
                        is_primary=is_primary
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Mapped {domain_url} -> {schema_name} - {description}"
                        )
                    )

        # 3. Ensure Public Schema has localhost domain (for Admin)
        self.stdout.write('\n3. Ensuring public schema accessibility:')
        
        try:
            if dry_run:
                public_exists = Tenant.objects.filter(schema_name='public').exists()
                if public_exists:
                    localhost_exists = Domain.objects.filter(domain='localhost').exists()
                    if localhost_exists:
                        self.stdout.write("  [EXISTS] localhost -> public")
                    else:
                        self.stdout.write(
                            self.style.SUCCESS("  [WOULD CREATE] localhost -> public")
                        )
            else:
                public = Tenant.objects.get(schema_name='public')
                localhost_domain, created = Domain.objects.get_or_create(
                    domain='localhost',
                    defaults={'tenant': public, 'is_primary': True}
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS("  ✓ Ensured localhost maps to public schema")
                    )
                else:
                    self.stdout.write("  - localhost already mapped to public schema")
        except Tenant.DoesNotExist:
            self.stdout.write(
                self.style.WARNING("  ⚠️  Public schema tenant not found (expected in django-tenants)")
            )

        # Summary
        self.stdout.write('\n' + '='*70)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - Run without --dry-run to apply'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ DEVELOPMENT TENANT INITIALIZATION COMPLETE'))
            self.stdout.write('\nNext steps:')
            self.stdout.write('  1. Ensure migrations are applied:')
            self.stdout.write('     python manage.py migrate_schemas --tenant')
            self.stdout.write('  2. Test the "Create Supplier" button in the frontend')
            self.stdout.write('  3. Expected result: 201 Created (no more 404 errors)')
        self.stdout.write('='*70)
