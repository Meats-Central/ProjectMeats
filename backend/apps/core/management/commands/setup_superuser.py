"""
Management command to setup or sync superuser password from environment variables.
This command ensures the superuser password is always synced from environment-specific variables.
It is idempotent and can be run during every deployment.
"""
import os
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create or sync superuser password with environment variable'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Determine environment and load appropriate variables
        django_env = os.getenv('DJANGO_ENV', 'development')
        
        # Load environment-specific credentials
        if django_env == 'development':
            username = os.getenv('DEVELOPMENT_SUPERUSER_USERNAME', 'admin')
            email = os.getenv('DEVELOPMENT_SUPERUSER_EMAIL', 'admin@meatscentral.com')
            password = os.getenv('DEVELOPMENT_SUPERUSER_PASSWORD')
        elif django_env in ['staging', 'uat']:
            username = os.getenv('STAGING_SUPERUSER_USERNAME')
            email = os.getenv('STAGING_SUPERUSER_EMAIL')
            password = os.getenv('STAGING_SUPERUSER_PASSWORD')
        elif django_env == 'production':
            username = os.getenv('PRODUCTION_SUPERUSER_USERNAME')
            email = os.getenv('PRODUCTION_SUPERUSER_EMAIL')
            password = os.getenv('PRODUCTION_SUPERUSER_PASSWORD')
        else:
            # Fallback for unknown environments
            username = os.getenv('SUPERUSER_USERNAME', 'admin')
            email = os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
            password = os.getenv('SUPERUSER_PASSWORD')
        
        # Validate required fields
        if not username:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Superuser username is required in {django_env} environment!'
                )
            )
            raise ValueError(
                f'Superuser username environment variable must be set in {django_env} environment'
            )
        
        if not email:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Superuser email is required in {django_env} environment!'
                )
            )
            raise ValueError(
                f'Superuser email environment variable must be set in {django_env} environment'
            )
        
        if not password:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Superuser password is required in {django_env} environment!'
                )
            )
            raise ValueError(
                f'Superuser password environment variable must be set in {django_env} environment'
            )
        
        # Try to get or create superuser
        try:
            user = User.objects.get(username=username)
            user_existed = True
            
            # Check for email mismatch and log a warning
            if user.email != email:
                logger.warning(
                    f'Email mismatch detected for user {username}: '
                    f'current={user.email}, new={email}. Updating to new email.'
                )
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Email mismatch detected! Updating from {user.email} to {email}'
                    )
                )
            
            # Always update the password
            user.set_password(password)
            # Update email in case it changed
            user.email = email
            user.save()
            
            logger.info(f'Superuser password synced for: {username}')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Superuser password synced/updated for: {email}'
                )
            )
            
        except User.DoesNotExist:
            # Create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            user_existed = False
            
            logger.info(f'Superuser created: {username} ({email})')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Superuser created: {email}'
                )
            )
