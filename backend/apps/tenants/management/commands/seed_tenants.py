"""
Django management command to seed database with demo tenants.

This command wraps the existing batch_tenant_creator utility to enable
pipeline-friendly invocation via GitHub Actions or other CI/CD systems.

Usage:
    python manage.py seed_tenants --count=5 --env=development
    python manage.py seed_tenants --count=3 --env=uat
    python manage.py seed_tenants --count=2 --env=prod
"""
from django.core.management.base import BaseCommand
from apps.tenants.utils.batch_tenant_creator import create_demo_tenants


class Command(BaseCommand):
    help = 'Seed database with demo tenants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='Number of tenants to create (default: 3)'
        )
        parser.add_argument(
            '--env',
            type=str,
            default='development',
            help='Target environment config (default: development)'
        )

    def handle(self, *args, **options):
        count = options['count']
        environment = options['env']
        
        self.stdout.write(f"🌱 Seeding {count} tenants for {environment}...")
        
        try:
            tenants = create_demo_tenants(
                environment=environment,
                count=count,
                verbosity=1
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Seeding complete: {len(tenants)} tenants created"
                )
            )
            
            # Output tenant names for verification
            for tenant in tenants:
                self.stdout.write(f"  • {tenant.name} ({tenant.slug})")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Seeding failed: {str(e)}")
            )
            raise
