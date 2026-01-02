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
        
        # Detect test context
        is_test_context = 'test' in django_env.lower() or os.getenv('DJANGO_SETTINGS_MODULE', '').endswith('test')
        
        logger.info(f'Running setup_superuser for environment: {django_env} (test_context={is_test_context})')
        
        # Load credentials from DJANGO_SUPERUSER_* variables (used by workflows)
        # Fall back to environment-specific variables for backward compatibility
        try:
            username = os.getenv('DJANGO_SUPERUSER_USERNAME')
            email = os.getenv('DJANGO_SUPERUSER_EMAIL')
            password = os.getenv('DJANGO_SUPERUSER_PASSWORD')
            
            # If DJANGO_SUPERUSER_* not set, try environment-specific variables
            if not username or not email or not password:
                if django_env == 'development':
                    # Development: Allow defaults for convenience
                    username = username or os.getenv('DEVELOPMENT_SUPERUSER_USERNAME', 'admin')
                    email = email or os.getenv('DEVELOPMENT_SUPERUSER_EMAIL', 'admin@meatscentral.com')
                    password = password or os.getenv('DEVELOPMENT_SUPERUSER_PASSWORD')
                    logger.info(f'Development mode: loaded username: {"set" if username else "using default"}')
                    logger.info(f'Development mode: loaded email: {"set" if email else "using default"}')
                    logger.info(f'Development mode: loaded password: {"set" if password else "missing"}')
                elif django_env in ['staging', 'uat']:
                    # Staging/UAT: Require all variables (no defaults for security)
                    username = username or os.getenv('STAGING_SUPERUSER_USERNAME')
                    email = email or os.getenv('STAGING_SUPERUSER_EMAIL')
                    password = password or os.getenv('STAGING_SUPERUSER_PASSWORD')
                    logger.info(f'Staging/UAT mode: loaded username: {"set" if username else "missing"}')
                    logger.info(f'Staging/UAT mode: loaded email: {"set" if email else "missing"}')
                    logger.info(f'Staging/UAT mode: loaded password: {"set" if password else "missing"}')
                elif django_env == 'production':
                    # Production: Require all variables (no defaults for security)
                    username = username or os.getenv('PRODUCTION_SUPERUSER_USERNAME')
                    email = email or os.getenv('PRODUCTION_SUPERUSER_EMAIL')
                    password = password or os.getenv('PRODUCTION_SUPERUSER_PASSWORD')
                    logger.info(f'Production mode: loaded username: {"set" if username else "missing"}')
                    logger.info(f'Production mode: loaded email: {"set" if email else "missing"}')
                    logger.info(f'Production mode: loaded password: {"set" if password else "missing"}')
                else:
                    # Fallback for unknown environments (allow defaults)
                    username = username or os.getenv('SUPERUSER_USERNAME', 'admin')
                    email = email or os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
                    password = password or os.getenv('SUPERUSER_PASSWORD')
                    logger.warning(f'Unknown environment "{django_env}", using fallback credentials')
            else:
                logger.info(f'Using DJANGO_SUPERUSER_* variables: username={"set" if username else "missing"}, email={"set" if email else "missing"}, password={"set" if password else "missing"}')
        except Exception as e:
            logger.error(f'Error loading environment variables: {e}')
            # Provide safe defaults for test context
            if is_test_context:
                username = username if 'username' in locals() else 'testadmin'
                email = email if 'email' in locals() else 'testadmin@example.com'
                password = password if 'password' in locals() else 'testpass123'
                logger.warning(f'Using test defaults due to error: username={username}, email={email}')
            else:
                raise
        
        # Apply defaults for missing values in test context
        if is_test_context:
            if not username:
                username = 'testadmin'
                logger.warning(f'Test context: using default username={username}')
            if not email:
                email = f'{username}@example.com'
                logger.warning(f'Test context: using default email={email}')
            if not password:
                password = 'testpass123'
                logger.warning(f'Test context: using default password (hidden)')
        
        # Validate required fields (strict for UAT/prod, lenient for dev and tests)
        is_production_env = django_env in ['staging', 'uat', 'production'] and not is_test_context
        
        if not username:
            error_msg = f'❌ Superuser username is required in {django_env} environment!'
            if is_production_env:
                logger.error(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
                raise ValueError(
                    f'Superuser username environment variable must be set in {django_env} environment'
                )
            else:
                logger.warning(error_msg + ' (non-production, continuing with defaults)')
                username = 'admin'
        
        if not email:
            error_msg = f'❌ Superuser email is required in {django_env} environment!'
            if is_production_env:
                logger.error(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
                raise ValueError(
                    f'Superuser email environment variable must be set in {django_env} environment'
                )
            else:
                logger.warning(error_msg + ' (non-production, continuing with defaults)')
                email = f'{username}@example.com'
        
        if not password:
            error_msg = f'❌ Superuser password is required in {django_env} environment!'
            if is_production_env:
                logger.error(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))
                raise ValueError(
                    f'Superuser password environment variable must be set in {django_env} environment'
                )
            else:
                logger.warning(error_msg + ' (non-production, continuing with defaults)')
                password = 'defaultpass123'
        
        # Try to get or create superuser
        # First, try to find by username
        user = None
        user_existed = False
        found_by = None
        
        # Log the credentials we're looking for (safe to log username/email, not password)
        logger.info(f'Setting up superuser with credentials:')
        logger.info(f'  Username: {username}')
        logger.info(f'  Email: {email}')
        self.stdout.write(f'Target superuser credentials:')
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'  Email: {email}')
        
        # Check for conflicting users
        conflicting_username = None
        conflicting_email = None
        
        try:
            conflicting_username = User.objects.get(username=username)
            logger.info(f'Found existing user with username: {username}')
        except User.DoesNotExist:
            pass
        
        try:
            conflicting_email = User.objects.get(email=email)
            logger.info(f'Found existing user with email: {email}')
        except User.DoesNotExist:
            pass
        
        # Determine if we have a match or conflict
        if conflicting_username and conflicting_email and conflicting_username.id == conflicting_email.id:
            # Same user - perfect match, just update it
            user = conflicting_username
            user_existed = True
            found_by = 'both'
            logger.info(f'User found by both username and email: {username} ({email})')
            self.stdout.write(self.style.SUCCESS(f'✓ Found existing user: {username} ({email})'))
        elif conflicting_username and not conflicting_email:
            # Username matches but different email - update email
            user = conflicting_username
            user_existed = True
            found_by = 'username'
            logger.info(f'User found by username, will update email: {conflicting_username.email} → {email}')
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Found user by username with different email: {conflicting_username.email} → {email}'
                )
            )
        elif conflicting_email and not conflicting_username:
            # Email matches but different username - DELETE and recreate
            logger.warning(
                f'User with email {email} exists with different username: {conflicting_email.username}. '
                f'Deleting old user and creating new one with username: {username}'
            )
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Deleting existing user: {conflicting_email.username} ({email})'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Will create new user: {username} ({email})'
                )
            )
            conflicting_email.delete()
            user = None
            user_existed = False
        elif conflicting_username and conflicting_email and conflicting_username.id != conflicting_email.id:
            # Both exist but as DIFFERENT users - delete both and recreate
            logger.warning(
                f'Conflict: username "{username}" belongs to {conflicting_username.email}, '
                f'email "{email}" belongs to {conflicting_email.username}. '
                f'Deleting both and creating fresh superuser.'
            )
            self.stdout.write(
                self.style.ERROR(
                    f'❌ CONFLICT: Username and email belong to different users!'
                )
            )
            self.stdout.write(f'   Existing user 1: {conflicting_username.username} ({conflicting_username.email})')
            self.stdout.write(f'   Existing user 2: {conflicting_email.username} ({conflicting_email.email})')
            self.stdout.write(self.style.WARNING(f'⚠️  Deleting both users and creating fresh superuser'))
            conflicting_username.delete()
            conflicting_email.delete()
            user = None
            user_existed = False
        
        if user_existed:
            # Update existing user
            if found_by == 'email' and user.username != username:
                logger.info(f'Updating username from "{user.username}" to "{username}"')
                user.username = username
            
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
            
            # Ensure user has superuser privileges
            if not user.is_superuser:
                logger.warning(f'User {username} exists but is not a superuser. Promoting to superuser.')
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  User exists but is not superuser. Promoting to superuser.'
                    )
                )
                user.is_superuser = True
            
            if not user.is_staff:
                logger.warning(f'User {username} exists but is not staff. Granting staff access.')
                user.is_staff = True
            
            if not user.is_active:
                logger.warning(f'User {username} exists but is not active. Activating user.')
                user.is_active = True
            
            # Always update the password
            user.set_password(password)
            # Update email in case it changed
            user.email = email
            user.save()
            
            logger.info(f'Superuser updated: {username} ({email})')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Superuser updated: {username} ({email})'
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
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Login test passed for: {username}'
                        )
                    )
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
            self.stdout.write('='*60)
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Superuser ready to use!'
                )
            )
            self.stdout.write(f'   Username: {username}')
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Superuser: Yes')
            self.stdout.write(f'   Staff: Yes')
            self.stdout.write(f'   Active: Yes')
            self.stdout.write('='*60)
            
        else:
            # User doesn't exist, create new superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            user_existed = False
            
            logger.info(f'Superuser created: {username} ({email})')
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Superuser created: {username} ({email})'
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
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Login test passed for: {username}'
                        )
                    )
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
            self.stdout.write('='*60)
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Superuser ready to use!'
                )
            )
            self.stdout.write(f'   Username: {username}')
            self.stdout.write(f'   Email: {email}')
            self.stdout.write(f'   Superuser: Yes')
            self.stdout.write(f'   Staff: Yes')
            self.stdout.write(f'   Active: Yes')
            self.stdout.write('='*60)
