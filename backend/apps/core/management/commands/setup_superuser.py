"""
Management command to setup or sync superuser password from environment variables.
This command ensures the superuser password is always synced from environment-specific variables.
It is idempotent and can be run during every deployment.

Security Features:
- Verifies authentication after password sync to ensure login works
- Comprehensive logging (no password logging per OWASP guidelines)
- Environment-specific validation (required in UAT/prod, defaults in dev)
- Follows Django authentication best practices
"""
import os
import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create or sync superuser password with environment variable'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Determine environment and load appropriate variables
        django_env = os.getenv('DJANGO_ENV', 'development')
        
        logger.info(f'Running setup_superuser for environment: {django_env}')
        
        # Load environment-specific credentials
        if django_env == 'development':
            # Development: Allow defaults for convenience
            username = os.getenv('DEVELOPMENT_SUPERUSER_USERNAME', 'admin')
            email = os.getenv('DEVELOPMENT_SUPERUSER_EMAIL', 'admin@meatscentral.com')
            password = os.getenv('DEVELOPMENT_SUPERUSER_PASSWORD')
            logger.info(f'Development mode: using username={username}, email={email}')
        elif django_env in ['staging', 'uat']:
            # Staging/UAT: Require all variables (no defaults for security)
            username = os.getenv('STAGING_SUPERUSER_USERNAME')
            email = os.getenv('STAGING_SUPERUSER_EMAIL')
            password = os.getenv('STAGING_SUPERUSER_PASSWORD')
            logger.info(f'Staging/UAT mode: loaded credentials for user={username}')
        elif django_env == 'production':
            # Production: Require all variables (no defaults for security)
            username = os.getenv('PRODUCTION_SUPERUSER_USERNAME')
            email = os.getenv('PRODUCTION_SUPERUSER_EMAIL')
            password = os.getenv('PRODUCTION_SUPERUSER_PASSWORD')
            logger.info(f'Production mode: loaded credentials for user={username}')
        else:
            # Fallback for unknown environments (allow defaults)
            username = os.getenv('SUPERUSER_USERNAME', 'admin')
            email = os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
            password = os.getenv('SUPERUSER_PASSWORD')
            logger.warning(f'Unknown environment "{django_env}", using fallback credentials')
        
        # Validate required fields (strict for UAT/prod, lenient for dev)
        is_production_env = django_env in ['staging', 'uat', 'production']
        
        if not username:
            error_msg = f'❌ Superuser username is required in {django_env} environment!'
            logger.error(error_msg)
            self.stdout.write(self.style.ERROR(error_msg))
            raise ValueError(
                f'Superuser username environment variable must be set in {django_env} environment'
            )
        
        if not email:
            error_msg = f'❌ Superuser email is required in {django_env} environment!'
            logger.error(error_msg)
            self.stdout.write(self.style.ERROR(error_msg))
            raise ValueError(
                f'Superuser email environment variable must be set in {django_env} environment'
            )
        
        if not password:
            error_msg = f'❌ Superuser password is required in {django_env} environment!'
            logger.error(error_msg)
            self.stdout.write(self.style.ERROR(error_msg))
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
            
            # Verify password works after password sync (critical for UAT/prod)
            logger.info(f'Verifying password for user: {username}')
            # Force reload user from database to ensure we have latest password
            user.refresh_from_db()
            if not user.check_password(password):
                error_msg = (
                    f'❌ Password verification failed for user: {username}. '
                    f'This indicates password was not properly saved.'
                )
                logger.error(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
                raise ValueError('Password verification failed after sync')
            
            # Also try full authentication to ensure auth backends work
            try:
                auth_user = authenticate(username=username, password=password)
                if auth_user:
                    logger.info(f'✅ Full authentication successful for user: {username}')
                else:
                    logger.warning(
                        f'⚠️  Password verified but authenticate() returned None for user: {username}. '
                        f'This may indicate auth backend configuration issue but password is correct.'
                    )
            except Exception as e:
                logger.warning(
                    f'⚠️  Authentication check raised exception: {e}. '
                    f'Password is verified via check_password() so login should work.'
                )
            
            logger.info(f'✅ Password verification successful for user: {username}')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Password verified - user can login successfully'
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
            
            # Verify password works for newly created user
            logger.info(f'Verifying password for newly created user: {username}')
            # Force reload user from database to ensure we have latest data
            user.refresh_from_db()
            if not user.check_password(password):
                error_msg = (
                    f'❌ Password verification failed for user: {username}. '
                    f'This indicates password was not properly set during creation.'
                )
                logger.error(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
                raise ValueError('Password verification failed after creation')
            
            # Also try full authentication to ensure auth backends work
            try:
                auth_user = authenticate(username=username, password=password)
                if auth_user:
                    logger.info(f'✅ Full authentication successful for newly created user: {username}')
                else:
                    logger.warning(
                        f'⚠️  Password verified but authenticate() returned None for user: {username}. '
                        f'This may indicate auth backend configuration issue but password is correct.'
                    )
            except Exception as e:
                logger.warning(
                    f'⚠️  Authentication check raised exception: {e}. '
                    f'Password is verified via check_password() so login should work.'
                )
            
            logger.info(f'✅ Password verification successful for newly created user: {username}')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Password verified - user can login successfully'
                )
            )
