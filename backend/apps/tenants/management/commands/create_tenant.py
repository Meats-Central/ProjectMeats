"""
Management command to create a new tenant with domain.

SHARED-SCHEMA MULTI-TENANCY:
This command creates a tenant and associated domain objects using ProjectMeats'
custom shared-schema multi-tenancy implementation. All tenants share the same
PostgreSQL schema with tenant_id foreign keys for data isolation.

Usage:
    python manage.py create_tenant --slug=acme --name="ACME Corp" --domain=acme.example.com
    python manage.py create_tenant --slug=test-co --name="Test Co" --on-trial --paid-until=2024-12-31
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
            '--slug',
            type=str,
            required=True,
            help='URL-friendly identifier (e.g., "acme-corp"). Must be unique.'
        )
        parser.add_argument(
            '--name',
            type=str,
            required=True,
            help='Tenant organization name (e.g., "ACME Corporation")'
        )
        
        # Optional tenant configuration
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

    def handle(self, *args, **options):
        """Execute the command."""
        verbosity = options.get('verbosity', 1)
        
        # Get required parameters
        slug = options['slug']
        name = options['name']
        
        # Get optional parameters
        contact_email = options.get('contact_email') or f'admin@{slug}.com'
        contact_phone = options.get('contact_phone', '')
        on_trial = options.get('on_trial', False)
        domain_name = options.get('domain')
        is_primary = options.get('is_primary', True)
        environment = options.get('environment') or os.getenv('DJANGO_ENV', 'development')
        
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
        
        # Validate slug (URL-friendly identifier rules)
        if not self._validate_slug(slug):
            raise CommandError(
                f'Invalid slug: {slug}. '
                f'Must contain only lowercase letters, numbers, and hyphens, '
                f'and be max 100 characters.'
            )
        
        if verbosity >= 2:
            self.stdout.write('🔧 Tenant Configuration:')
            self.stdout.write(f'   - Slug: {slug}')
            self.stdout.write(f'   - Name: {name}')
            self.stdout.write(f'   - Contact Email: {contact_email}')
            self.stdout.write(f'   - Contact Phone: {contact_phone}')
            self.stdout.write(f'   - On Trial: {on_trial}')
            self.stdout.write(f'   - Paid Until: {paid_until}')
            self.stdout.write(f'   - Domain: {domain_name or "None"}')
            self.stdout.write(f'   - Environment: {environment}')
            self.stdout.write('')
        
        try:
            with transaction.atomic():
                # Create tenant in shared schema (raises IntegrityError on duplicate slug)
                if verbosity >= 1:
                    self.stdout.write(f'Creating tenant: {name} ({slug})...')
                
                # Check for duplicate slug first
                if Tenant.objects.filter(slug=slug).exists():
                    raise CommandError(
                        f'Tenant with slug "{slug}" already exists. '
                        f'Use a unique slug.'
                    )
                
                # Create new tenant in shared schema
                tenant = Tenant.objects.create(
                    slug=slug,
                    name=name,
                    contact_email=contact_email,
                    contact_phone=contact_phone,
                    is_active=True,
                    is_trial=on_trial,
                    trial_ends_at=paid_until if on_trial else None,
                )
                
                if verbosity >= 1:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Tenant created: {tenant.name} (ID: {tenant.id})')
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
                
                # Summary
                if verbosity >= 1:
                    self.stdout.write(self.style.SUCCESS('=' * 60))
                    self.stdout.write(self.style.SUCCESS('TENANT CREATION COMPLETE (Shared-Schema)'))
                    self.stdout.write(self.style.SUCCESS('=' * 60))
                    self.stdout.write('')
                    self.stdout.write(f'Tenant ID: {tenant.id}')
                    self.stdout.write(f'Slug: {tenant.slug}')
                    self.stdout.write(f'Name: {tenant.name}')
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
                    self.stdout.write(self.style.NOTICE(
                        'Note: Using shared-schema multi-tenancy. '
                        'No schema migrations needed.'
                    ))
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating tenant: {str(e)}')
            )
            if verbosity >= 2:
                import traceback
                self.stdout.write('\nFull traceback:')
                self.stdout.write(traceback.format_exc())
            raise

    def _validate_slug(self, slug):
        """
        Validate slug follows URL-friendly identifier rules.
        
        Rules:
        - Must contain only lowercase letters, numbers, and hyphens
        - Maximum 100 characters
        """
        import re
        
        if len(slug) > 100:
            return False
        
        pattern = re.compile(r'^[a-z0-9-]+$')
        return pattern.match(slug) is not None
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
