"""
Management command to create a superuser and default root tenant.
This command is idempotent and can be run multiple times without creating duplicates.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.tenants.models import Tenant, TenantUser


class Command(BaseCommand):
    help = 'Create superuser and default root tenant if they do not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get credentials from environment variables with defaults
        email = os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
        password = os.getenv('SUPERUSER_PASSWORD', 'default_secure_pass')
        
        # Create superuser if it doesn't exist
        try:
            with transaction.atomic():
                user, user_created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': email.split('@')[0],
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                    }
                )
                
                if user_created:
                    user.set_password(password)
                    user.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Superuser created: {email}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Superuser already exists: {email}')
                    )
                
                # Create root tenant if it doesn't exist
                tenant, tenant_created = Tenant.objects.get_or_create(
                    slug='root',
                    defaults={
                        'name': 'Root',
                        'contact_email': email,
                        'is_active': True,
                        'is_trial': False,
                        'created_by': user,
                    }
                )
                
                if tenant_created:
                    self.stdout.write(
                        self.style.SUCCESS('✅ Default root tenant created')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('⚠️  Default root tenant already exists')
                    )
                
                # Link superuser to root tenant with owner role if not already linked
                tenant_user, link_created = TenantUser.objects.get_or_create(
                    tenant=tenant,
                    user=user,
                    defaults={
                        'role': 'owner',
                        'is_active': True,
                    }
                )
                
                if link_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Superuser linked to root tenant as owner')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Superuser already linked to root tenant')
                    )
                
                self.stdout.write(
                    self.style.SUCCESS('\n🎉 Super tenant setup complete!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during super tenant creation: {str(e)}')
            )
            raise
