"""
Management command to create a new tenant with domain.

This command creates a tenant (Client) and associated domain objects following
django-tenants patterns while working with ProjectMeats' custom shared-schema
multi-tenancy implementation.

Usage:
    python manage.py create_tenant --schema-name=acme --name="ACME Corp" --domain=acme.example.com
    python manage.py create_tenant --schema-name=test --name="Test Co" --on-trial --paid-until=2024-12-31
"""
import os
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from apps.tenants.models import Tenant, TenantDomain


class Command(BaseCommand):
    help = 'Create a new tenant with associated domain for multi-tenancy onboarding'

    def add_arguments(self, parser):
        """Add command-line arguments."""
        # Required arguments
        parser.add_argument(
            '--schema-name',
            type=str,
            required=True,
            help='Database schema name (e.g., "acme_corp"). Must be unique and PostgreSQL-compatible.'
        )
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Tenant organization name (e.g., "ACME Corporation")'
        )
        
        # Optional tenant configuration
        parser.add_argument(
            '--slug',
            type=str,
            help='URL-friendly identifier (auto-generated from schema-name if not provided)'
        )
        parser.add_argument(
            '--contact-email',
            type=str,
            help='Primary contact email for the tenant'
        )
        parser.add_argument(
            '--contact-phone',
            type=str,
            default='',
            help='Primary contact phone number'
        )
        parser.add_argument(
            '--on-trial',
            action='store_true',
            help='Mark tenant as trial account'
        )
        parser.add_argument(
            '--paid-until',
            type=str,
            help='Paid until date (YYYY-MM-DD format) or trial end date if --on-trial is set'
        )
        
        # Domain configuration
        parser.add_argument(
            '--domain',
            type=str,
            help='Primary domain for the tenant (e.g., "acme.example.com")'
        )
        parser.add_argument(
            '--is-primary',
            action='store_true',
            default=True,
            help='Mark domain as primary (default: True)'
        )
        
        # Environment context
        parser.add_argument(
            '--environment',
            type=str,
            choices=['development', 'staging', 'uat', 'production'],
            help='Environment context for tenant creation'
        )
        
        # Migration options
        parser.add_argument(
            '--run-migrations',
            action='store_true',
            help='Run schema migrations for the new tenant (for true django-tenants compatibility)'
        )

    def handle(self, *args, **options):
        """Execute the command."""
        verbosity = options.get('verbosity', 1)
        
        # Get required parameters
        schema_name = options['schema_name']
        name = options['name']
        
        # Get optional parameters
        slug = options.get('slug') or schema_name.replace('_', '-')
        contact_email = options.get('contact_email') or f'admin@{slug}.local'
        contact_phone = options.get('contact_phone', '')
        on_trial = options.get('on_trial', False)
        domain_name = options.get('domain')
        is_primary = options.get('is_primary', True)
        environment = options.get('environment') or os.getenv('DJANGO_ENV', 'development')
        run_migrations = options.get('run_migrations', False)
        
        # Parse paid_until date
        paid_until = None
        if options.get('paid_until'):
            try:
                paid_until = datetime.strptime(options['paid_until'], '%Y-%m-%d')
                paid_until = timezone.make_aware(paid_until)
            except ValueError:
                raise CommandError(
                    f'Invalid date format for --paid-until: {options["paid_until"]}. '
                    f'Use YYYY-MM-DD format.'
                )
        elif on_trial:
            # Default to 30 days trial
            paid_until = timezone.now() + timedelta(days=30)
        
        # Validate schema_name (PostgreSQL identifier rules)
        if not self._validate_schema_name(schema_name):
            raise CommandError(
                f'Invalid schema name: {schema_name}. '
                f'Must start with a letter or underscore, contain only alphanumeric characters '
                f'and underscores, and be max 63 characters.'
            )
        
        if verbosity >= 2:
            self.stdout.write('🔧 Tenant Configuration:')
            self.stdout.write(f'   - Schema Name: {schema_name}')
            self.stdout.write(f'   - Name: {name}')
            self.stdout.write(f'   - Slug: {slug}')
            self.stdout.write(f'   - Contact Email: {contact_email}')
            self.stdout.write(f'   - Contact Phone: {contact_phone}')
            self.stdout.write(f'   - On Trial: {on_trial}')
            self.stdout.write(f'   - Paid Until: {paid_until}')
            self.stdout.write(f'   - Domain: {domain_name or "None"}')
            self.stdout.write(f'   - Environment: {environment}')
            self.stdout.write('')
        
        try:
            with transaction.atomic():
                # Create tenant (idempotent with get_or_create)
                if verbosity >= 1:
                    self.stdout.write(f'Creating tenant: {name} ({schema_name})...')
                
                # Use get_or_create for idempotency
                tenant, created = Tenant.objects.get_or_create(
                    schema_name=schema_name,
                    defaults={
                        'name': name,
                        'slug': slug,
                        'contact_email': contact_email,
                        'contact_phone': contact_phone,
                        'is_active': True,
                        'is_trial': on_trial,
                        'trial_ends_at': paid_until if on_trial else None,
                    }
                )
                
                if verbosity >= 1:
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Tenant created: {tenant.name} (ID: {tenant.id})')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  Tenant already exists: {tenant.name} (ID: {tenant.id})')
                        )
                
                # Create domain if provided (idempotent with get_or_create)
                if domain_name:
                    if verbosity >= 1:
                        self.stdout.write(f'Creating domain: {domain_name}...')
                    
                    domain, domain_created = TenantDomain.objects.get_or_create(
                        domain=domain_name.lower(),
                        defaults={
                            'tenant': tenant,
                            'is_primary': is_primary,
                        }
                    )
                    
                    if verbosity >= 1:
                        if domain_created:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✅ Domain created: {domain.domain} '
                                    f'{"(primary)" if domain.is_primary else ""}'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'⚠️  Domain already exists: {domain.domain}'
                                )
                            )
                
                # Run migrations if requested
                if run_migrations:
                    self._run_tenant_migrations(tenant, verbosity)
                else:
                    if verbosity >= 1:
                        self.stdout.write('')
                        self.stdout.write(
                            self.style.WARNING(
                                '⚠️  Schema migrations not run. ProjectMeats uses shared-schema '
                                'multi-tenancy.'
                            )
                        )
                        self.stdout.write(
                            'To run migrations for true django-tenants compatibility, use:'
                        )
                        self.stdout.write(
                            f'  python manage.py migrate_schemas --schema={schema_name}'
                        )
                        self.stdout.write('')
                
                # Summary
                if verbosity >= 1:
                    self.stdout.write(self.style.SUCCESS('=' * 60))
                    self.stdout.write(self.style.SUCCESS('TENANT CREATION COMPLETE'))
                    self.stdout.write(self.style.SUCCESS('=' * 60))
                    self.stdout.write('')
                    self.stdout.write(f'Tenant ID: {tenant.id}')
                    self.stdout.write(f'Schema Name: {tenant.schema_name}')
                    self.stdout.write(f'Name: {tenant.name}')
                    self.stdout.write(f'Slug: {tenant.slug}')
                    self.stdout.write(f'Contact: {tenant.contact_email}')
                    self.stdout.write(f'Trial: {tenant.is_trial}')
                    if tenant.trial_ends_at:
                        self.stdout.write(f'Trial Ends: {tenant.trial_ends_at.strftime("%Y-%m-%d")}')
                    if domain_name:
                        self.stdout.write(f'Domain: {domain_name} {"(primary)" if is_primary else ""}')
                    self.stdout.write('')
                    self.stdout.write('Next steps:')
                    self.stdout.write('  1. Create users for this tenant')
                    self.stdout.write('  2. Configure tenant settings')
                    if not domain_name:
                        self.stdout.write('  3. Add domain(s) for tenant routing')
                    self.stdout.write('')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating tenant: {str(e)}')
            )
            if verbosity >= 2:
                import traceback
                self.stdout.write('\nFull traceback:')
                self.stdout.write(traceback.format_exc())
            raise

    def _validate_schema_name(self, schema_name):
        """
        Validate schema name follows PostgreSQL identifier rules.
        
        Rules:
        - Must start with a letter (a-z) or underscore
        - Can contain letters, digits, and underscores
        - Maximum 63 characters
        """
        import re
        
        if len(schema_name) > 63:
            return False
        
        pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        return pattern.match(schema_name) is not None

    def _run_tenant_migrations(self, tenant, verbosity):
        """
        Run migrations for tenant schema.
        
        Note: This is a placeholder for true django-tenants compatibility.
        ProjectMeats uses shared-schema multi-tenancy, so this is not needed
        for normal operation.
        
        For true django-tenants setup, you would use:
            from django_tenants.utils import tenant_context
            from django.core.management import call_command
            
            with tenant_context(tenant):
                call_command('migrate_schemas', schema_name=tenant.schema_name)
        """
        if verbosity >= 1:
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Schema migration requested but ProjectMeats uses shared-schema '
                    'multi-tenancy.'
                )
            )
            self.stdout.write(
                'For true django-tenants compatibility with separate PostgreSQL schemas:'
            )
            self.stdout.write('')
            self.stdout.write('1. Install django-tenants database backend in settings:')
            self.stdout.write('   DATABASES = {')
            self.stdout.write('       "default": {')
            self.stdout.write('           "ENGINE": "django_tenants.postgresql_backend",')
            self.stdout.write('           ...')
            self.stdout.write('       }')
            self.stdout.write('   }')
            self.stdout.write('')
            self.stdout.write('2. Configure SHARED_APPS and TENANT_APPS in settings')
            self.stdout.write('')
            self.stdout.write('3. Run migrations:')
            self.stdout.write(f'   python manage.py migrate_schemas --schema={tenant.schema_name}')
            self.stdout.write('')
            self.stdout.write('Current setup uses application-level tenant filtering instead.')
            self.stdout.write('')
