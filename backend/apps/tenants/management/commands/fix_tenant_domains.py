"""
Management command to fix tenant domains by adding backend subdomain variants.

This command ensures all tenants have corresponding backend subdomains in the Domain model,
preventing 404 errors in multi-tenant lookups while respecting schema isolation.
"""
from django.core.management.base import BaseCommand
from apps.tenants.models import Client, Domain


class Command(BaseCommand):
    help = 'Fix tenant domains by adding backend subdomain variants idempotently'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating domains',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        tenants = Client.objects.all()
        total_tenants = tenants.count()
        
        if total_tenants == 0:
            self.stdout.write(self.style.WARNING('No tenants found in the database'))
            return
        
        self.stdout.write(f'Processing {total_tenants} tenant(s)...\n')
        
        created_count = 0
        existing_count = 0
        
        for tenant in tenants:
            # Create backend subdomain for each tenant
            backend_domain_str = f"{tenant.schema_name}-backend.meatscentral.com"
            
            if dry_run:
                exists = Domain.objects.filter(
                    tenant=tenant,
                    domain=backend_domain_str
                ).exists()
                
                if exists:
                    self.stdout.write(
                        f"  [EXISTS] Domain {backend_domain_str} for tenant {tenant.schema_name}"
                    )
                    existing_count += 1
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [WOULD CREATE] Domain {backend_domain_str} for tenant {tenant.schema_name}"
                        )
                    )
                    created_count += 1
            else:
                domain, created = Domain.objects.get_or_create(
                    tenant=tenant,
                    domain=backend_domain_str,
                    defaults={'is_primary': False}
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Created domain {backend_domain_str} for tenant {tenant.schema_name}"
                        )
                    )
                    created_count += 1
                else:
                    self.stdout.write(
                        f"  - Domain {backend_domain_str} already exists for tenant {tenant.schema_name}"
                    )
                    existing_count += 1
        
        # Summary
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN SUMMARY:'))
            self.stdout.write(f'  Would create: {created_count} domain(s)')
        else:
            self.stdout.write(self.style.SUCCESS('COMPLETED SUCCESSFULLY:'))
            self.stdout.write(f'  Created: {created_count} domain(s)')
        
        self.stdout.write(f'  Already existed: {existing_count} domain(s)')
        self.stdout.write(f'  Total tenants processed: {total_tenants}')
        self.stdout.write('='*60)
