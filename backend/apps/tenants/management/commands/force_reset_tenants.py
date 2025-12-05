"""
Django management command to force reset tenant tables.

This command drops all tenant-related tables and resets migration history.
It's designed for development/staging environments to recover from migration drift.

SAFETY: This command will NOT run in production environments.

Usage:
    python manage.py force_reset_tenants
    
    # Via Ops Workflow:
    # GitHub Actions → 🎮 Ops - Run Management Command
    # Environment: dev
    # Command: force_reset_tenants
"""
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'Force reset tenant tables (drops all tenant tables and migration history)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt (use with caution)',
        )

    def handle(self, *args, **options):
        # Safety check: Prevent running in production
        environment = os.environ.get('DJANGO_SETTINGS_MODULE', '')
        if 'production' in environment.lower() or getattr(settings, 'DEBUG', True) is False:
            raise CommandError(
                '❌ SAFETY CHECK FAILED: This command cannot run in production.\n'
                f'   Current environment: {environment}\n'
                f'   DEBUG setting: {settings.DEBUG}'
            )
        
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  WARNING: This will DROP all tenant tables and reset migration history!\n'
            )
        )
        
        # Confirm unless --force is used
        if not options['force']:
            confirm = input('Type "yes" to continue: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('❌ Operation cancelled.'))
                return
        
        self.stdout.write(self.style.WARNING('\n🔥 Starting force reset of tenant tables...\n'))
        
        # List of tables to drop (in dependency order)
        tables_to_drop = [
            'tenants_tenantdomain',    # Foreign key to tenant
            'tenants_invitation',       # Foreign key to tenant
            'tenants_tenant_user',      # Foreign key to tenant
            'tenants_tenant',           # Main tenant table
            'tenants_domain',           # django-tenants domain table
            'tenants_client',           # django-tenants client table (if exists)
        ]
        
        try:
            with connection.cursor() as cursor:
                # Drop each table with CASCADE
                for table in tables_to_drop:
                    self.stdout.write(f'  Dropping table: {table}')
                    try:
                        cursor.execute(f'DROP TABLE IF EXISTS {table} CASCADE;')
                        self.stdout.write(self.style.SUCCESS(f'    ✓ Dropped {table}'))
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'    ⚠️  Could not drop {table}: {str(e)}')
                        )
                
                # Reset migration history for tenants app
                self.stdout.write('\n  Resetting migration history for tenants app...')
                cursor.execute("DELETE FROM django_migrations WHERE app='tenants';")
                self.stdout.write(self.style.SUCCESS('    ✓ Migration history reset'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error during force reset: {str(e)}'))
            raise CommandError(f'Force reset failed: {str(e)}')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Force reset completed successfully!\n'
                '\nNext steps:\n'
                '  1. Run: python manage.py migrate\n'
                '  2. Run: python manage.py create_super_tenant\n'
                '  3. Run: python manage.py seed_tenants --count=5\n'
            )
        )
