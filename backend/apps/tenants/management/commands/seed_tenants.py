"""
Django management command to seed database with TEST tenants and data.
Generates tenants, users, and business data for testing purposes.
"""
from django.core.management.base import BaseCommand
from apps.tenants.utils.test_data_seeder import seed_test_data


class Command(BaseCommand):
    help = 'Seed database with comprehensive test tenants and data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='Number of test tenants to create (default: 3)'
        )
        parser.add_argument(
            '--env',
            type=str,
            default='development',
            help='Target environment context (development, uat, staging)'
        )
        # Note: Django already provides -v/--verbosity, so we use it from options

    def handle(self, *args, **options):
        count = options['count']
        environment = options['env']
        verbosity = options['verbosity']
        
        self.stdout.write(f"🌱 Seeding {count} FULL test tenants for {environment}...")
        
        try:
            tenants = seed_test_data(
                environment=environment,
                count=count,
                verbosity=verbosity
            )
            
            self.stdout.write(self.style.SUCCESS(f"\n✅ Seeding Complete! Created {len(tenants)} tenants."))
            self.stdout.write("\n🔑 Test Credentials:")
            self.stdout.write("="*60)
            for t in tenants:
                creds = t.test_credentials
                self.stdout.write(f"Tenant: {t.name}")
                self.stdout.write(f"  Slug: {t.slug}")
                self.stdout.write(f"  User: {creds['username']}")
                self.stdout.write(f"  Pass: {creds['password']}")
                self.stdout.write(f"  Role: {creds['role']}")
                self.stdout.write("-" * 20)
            self.stdout.write("="*60)
            self.stdout.write("\n💡 Tip: Log in as superuser and view these credentials in Django Admin → Tenants")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Seeding failed: {str(e)}"))
            import traceback
            if verbosity >= 2:
                traceback.print_exc()
            raise
