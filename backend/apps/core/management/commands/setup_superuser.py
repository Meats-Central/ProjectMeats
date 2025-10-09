"""
Management command to setup or sync superuser password from environment variables.
This command ensures the superuser password is always synced with ENVIRONMENT_SUPERUSER_PASSWORD.
It is idempotent and can be run during every deployment.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create or sync superuser password with environment variable'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get credentials from environment variables
        username = os.getenv('SUPERUSER_USERNAME', 'admin')
        email = os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
        password = os.getenv('ENVIRONMENT_SUPERUSER_PASSWORD')
        
        # Validate that password is provided
        if not password:
            # Check if we're in production-like environment
            django_env = os.getenv('DJANGO_ENV', 'development')
            if django_env in ['production', 'staging', 'uat']:
                self.stdout.write(
                    self.style.ERROR(
                        '❌ ENVIRONMENT_SUPERUSER_PASSWORD is required in non-dev environments!'
                    )
                )
                raise ValueError(
                    'ENVIRONMENT_SUPERUSER_PASSWORD environment variable must be set in '
                    f'{django_env} environment'
                )
            else:
                # In dev, fall back to SUPERUSER_PASSWORD
                password = os.getenv('SUPERUSER_PASSWORD', 'default_secure_pass')
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  ENVIRONMENT_SUPERUSER_PASSWORD not set, using SUPERUSER_PASSWORD fallback'
                    )
                )
        
        try:
            # Try to get existing user
            user = User.objects.get(username=username)
            
            # Always update the password
            user.set_password(password)
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Superuser password synced/updated for: {user.email}'
                )
            )
            
        except User.DoesNotExist:
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Superuser created: {email}'
                )
            )
