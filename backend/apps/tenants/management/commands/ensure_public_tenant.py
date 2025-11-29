"""
Management command to ensure public tenant exists with proper configuration.
This is used during deployment to initialize the public schema tenant.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.tenants.models import Client, Domain


class Command(BaseCommand):
    help = 'Ensure public tenant exists with proper domain configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost',
            help='Domain for the public tenant (default: localhost)',
        )

    def handle(self, *args, **options):
        domain_name = options['domain']
        
        try:
            with transaction.atomic():
                # Get or create public tenant
                public_tenant, created = Client.objects.get_or_create(
                    schema_name='public',
                    defaults={
                        'name': 'Public Schema',
                        'description': 'Public schema for shared tenant resources'
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created public tenant')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Public tenant already exists')
                    )
                
                # Ensure domain exists for public tenant
                domain, domain_created = Domain.objects.get_or_create(
                    domain=domain_name,
                    defaults={
                        'tenant': public_tenant,
                        'is_primary': True
                    }
                )
                
                if domain_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created domain: {domain_name}')
                    )
                else:
                    # Update tenant if domain exists but points to different tenant
                    if domain.tenant != public_tenant:
                        domain.tenant = public_tenant
                        domain.save()
                        self.stdout.write(
                            self.style.WARNING(f'! Updated domain {domain_name} to point to public tenant')
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(f'✓ Domain {domain_name} already configured')
                        )
                
                self.stdout.write(
                    self.style.SUCCESS('\n✓ Public tenant setup complete')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Error setting up public tenant: {e}')
            )
            raise
