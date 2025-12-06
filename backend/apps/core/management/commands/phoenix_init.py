"""
Management command for idempotent Phoenix initialization.

This command performs a complete environment reset and setup:
1. Creates/verifies superuser from environment variables
2. Creates public tenant (required for shared schema logic)
3. Creates demo tenant with demo.localhost domain
4. Links superuser to demo tenant as owner

This command is idempotent and can be run multiple times safely.
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.tenants.models import Tenant, TenantDomain, TenantUser


class Command(BaseCommand):
    help = 'Idempotent initialization for Phoenix reset'

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        # 1. Superuser
        if email and password and not User.objects.filter(email=email).exists():
            superuser = User.objects.create_superuser(
                username=email.split('@')[0],  # Use email prefix as username
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS('Superuser created.'))
        else:
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                self.stdout.write(self.style.SUCCESS('Superuser exists.'))
            else:
                self.stdout.write(
                    self.style.ERROR(
                        'No superuser found. Set DJANGO_SUPERUSER_EMAIL and '
                        'DJANGO_SUPERUSER_PASSWORD environment variables.'
                    )
                )
                return

        # 2. Public Tenant
        public_tenant, created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={
                'name': 'Public',
                'slug': 'public',
                'contact_email': email or 'admin@meatscentral.com',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Public Tenant created.'))

        # 3. Demo Tenant
        demo_tenant, created = Tenant.objects.get_or_create(
            name='demo',
            defaults={
                'schema_name': 'demo',
                'slug': 'demo',
                'contact_email': email or 'admin@meatscentral.com',
            }
        )
        if created:
            TenantDomain.objects.create(domain='demo.localhost', tenant=demo_tenant)
            self.stdout.write(self.style.SUCCESS('Demo Tenant and Domain created.'))
        else:
            # Ensure domain exists even if tenant already exists (idempotent)
            TenantDomain.objects.get_or_create(
                domain='demo.localhost',
                defaults={'tenant': demo_tenant}
            )

        # 4. Link User
        TenantUser.objects.get_or_create(
            tenant=demo_tenant,
            user=superuser,
            defaults={'role': 'owner'}
        )
        self.stdout.write(self.style.SUCCESS('Superuser linked to Demo Tenant.'))
