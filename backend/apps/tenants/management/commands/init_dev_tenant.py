"""
Management command to initialize the Development Tenant and map dev domains.

This command creates a default development tenant and maps both frontend and backend
dev domains to it, ensuring the Dev environment works as a "Single Tenant" app.

SHARED-SCHEMA MULTI-TENANCY:
This command uses ProjectMeats' custom shared-schema multi-tenancy approach,
NOT django-tenants. All tenants share the same PostgreSQL schema with tenant_id
foreign keys for data isolation.

CRITICAL: This fixes the "No tenant for hostname 'dev-backend.meatscentral.com'" error
by mapping the domain to a tenant where the business tables exist in the shared schema.
"""
from django.core.management.base import BaseCommand
from apps.tenants.models import Tenant, TenantDomain


class Command(BaseCommand):
    help = 'Initialize the Development Tenant and map dev-backend domain (shared-schema approach)'

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
            '--tenant-slug',
            type=str,
            default='dev-corp',
            help='Slug for development tenant (default: dev-corp)',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        tenant_name = options.get('tenant_name')
        tenant_slug = options.get('tenant_slug')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        self.stdout.write(self.style.HTTP_INFO('='*70))
        self.stdout.write(self.style.HTTP_INFO('INITIALIZING DEVELOPMENT TENANT (Shared-Schema)'))
        self.stdout.write(self.style.HTTP_INFO('='*70))

        # 1. Create/Get the "Dev Tenant" in the shared schema
        self.stdout.write(f'\n1. Setting up tenant: {tenant_name} (slug: {tenant_slug})')
        
        if dry_run:
            exists = Tenant.objects.filter(slug=tenant_slug).exists()
            if exists:
                self.stdout.write(f"  [EXISTS] Tenant with slug {tenant_slug}")
            else:
                self.stdout.write(self.style.SUCCESS(f"  [WOULD CREATE] Tenant: {tenant_name} ({tenant_slug})"))
            tenant = Tenant.objects.filter(slug=tenant_slug).first()
        else:
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
                    self.style.SUCCESS(f"  ✓ Created Tenant: {tenant_name} ({tenant_slug})")
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
                exists = TenantDomain.objects.filter(domain=domain_url).exists()
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
                if not tenant:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  ✗ Cannot map domain {domain_url}: No tenant found"
                        )
                    )
                    continue
                    
                existing = TenantDomain.objects.filter(domain=domain_url).first()
                
                if existing:
                    # Check if it points to the correct tenant
                    if existing.tenant.slug != tenant_slug:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠️  Domain {domain_url} exists but points to {existing.tenant.slug}"
                            )
                        )
                        self.stdout.write(f"     Updating to point to {tenant_slug}...")
                        existing.tenant = tenant
                        existing.is_primary = is_primary
                        existing.save()
                        self.stdout.write(
                            self.style.SUCCESS(f"  ✓ Updated {domain_url} -> {tenant_slug}")
                        )
                    else:
                        self.stdout.write(
                            f"  - Domain {domain_url} already correctly mapped"
                        )
                else:
                    TenantDomain.objects.create(
                        domain=domain_url,
                        tenant=tenant,
                        is_primary=is_primary
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Mapped {domain_url} -> {tenant_slug} - {description}"
                        )
                    )

        # Summary
        self.stdout.write('\n' + '='*70)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - Run without --dry-run to apply'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ DEVELOPMENT TENANT INITIALIZATION COMPLETE'))
            self.stdout.write('\nNext steps:')
            self.stdout.write('  1. Ensure migrations are applied:')
            self.stdout.write('     python manage.py migrate --noinput')
            self.stdout.write('  2. Test the "Create Supplier" button in the frontend')
            self.stdout.write('  3. Expected result: 201 Created (no more 404 errors)')
            self.stdout.write('\nNote: This uses shared-schema multi-tenancy.')
            self.stdout.write('      All tenants share the same PostgreSQL schema.')
        self.stdout.write('='*70)
