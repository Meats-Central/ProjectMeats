"""
Management command to create a superuser and default root tenant.
This command is idempotent and can be run multiple times without creating duplicates.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.utils import IntegrityError

# Verify Tenant model is available
try:
    from apps.tenants.models import Tenant, TenantUser
except ImportError as e:
    raise ImportError(
        'Tenant model missing—ensure Multi-Tenancy base is implemented. '
        f'Original error: {str(e)}'
    ) from e


class Command(BaseCommand):
    help = 'Create superuser and default root tenant if they do not exist'

    def add_arguments(self, parser):
        """Add command-line arguments."""
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser (overrides environment variable)',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the superuser (overrides environment variable)',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser (overrides environment variable)',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get verbosity level
        verbosity = options.get('verbosity', 1)
        
        # Determine environment and load appropriate credentials
        django_env = os.getenv('DJANGO_ENV', 'development')
        is_test_context = 'test' in django_env.lower() or os.getenv('DJANGO_SETTINGS_MODULE', '').endswith('test')
        
        if verbosity >= 2:
            self.stdout.write(f'🌍 Running in environment: {django_env} (test_context={is_test_context})')
        
        # Get credentials from command-line arguments or environment-specific variables
        # Command-line arguments take precedence
        if options.get('email') or options.get('password') or options.get('username'):
            email = options.get('email') or os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
            password = options.get('password') or os.getenv('SUPERUSER_PASSWORD', 'default_secure_pass')
            username = options.get('username') or os.getenv('SUPERUSER_USERNAME', email.split('@')[0])
        else:
            # Use environment-specific variables with fallback to generic SUPERUSER_* vars
            if django_env == 'development':
                email = os.getenv('DEVELOPMENT_SUPERUSER_EMAIL') or os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
                password = os.getenv('DEVELOPMENT_SUPERUSER_PASSWORD') or os.getenv('SUPERUSER_PASSWORD', 'default_secure_pass')
                username = os.getenv('DEVELOPMENT_SUPERUSER_USERNAME') or os.getenv('SUPERUSER_USERNAME', email.split('@')[0])
            elif django_env in ['staging', 'uat']:
                email = os.getenv('STAGING_SUPERUSER_EMAIL') or os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
                password = os.getenv('STAGING_SUPERUSER_PASSWORD') or os.getenv('SUPERUSER_PASSWORD', 'default_secure_pass')
                username = os.getenv('STAGING_SUPERUSER_USERNAME') or os.getenv('SUPERUSER_USERNAME', email.split('@')[0])
            elif django_env == 'production':
                email = os.getenv('PRODUCTION_SUPERUSER_EMAIL') or os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
                password = os.getenv('PRODUCTION_SUPERUSER_PASSWORD') or os.getenv('SUPERUSER_PASSWORD', 'default_secure_pass')
                username = os.getenv('PRODUCTION_SUPERUSER_USERNAME') or os.getenv('SUPERUSER_USERNAME', email.split('@')[0])
            else:
                # Fallback for unknown environments or test contexts
                email = os.getenv('SUPERUSER_EMAIL', 'admin@meatscentral.com')
                password = os.getenv('SUPERUSER_PASSWORD', 'default_secure_pass')
                username = os.getenv('SUPERUSER_USERNAME', email.split('@')[0])
        
        if verbosity >= 2:
            self.stdout.write('🔧 Configuration:')
            self.stdout.write(f'   - Email: {email}')
            self.stdout.write(f'   - Username: {username}')
            self.stdout.write(f'   - Password: {"*" * len(password)}')
            self.stdout.write('')
        
        # Create superuser if it doesn't exist
        try:
            if verbosity >= 2:
                self.stdout.write('🔍 Attempting superuser creation...')
            
            with transaction.atomic():
                # Try to get existing user by username or email
                # This prevents UNIQUE constraint errors on username
                user = None
                user_created = False
                
                if verbosity >= 2:
                    self.stdout.write(f'   - Checking for existing user with username: {username}')
                
                # First, try to find by username (most likely to cause constraint issues)
                # Use filter() instead of get() to handle potential duplicates
                users_by_username = User.objects.filter(username=username)
                
                if users_by_username.count() > 1:
                    # Handle duplicate users - keep first, delete extras
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Multiple users found with username "{username}" ({users_by_username.count()} total). '
                            f'Using first user and deleting duplicates.'
                        )
                    )
                    # Delete all but the first user
                    users_to_delete = list(users_by_username[1:])
                    for duplicate_user in users_to_delete:
                        if verbosity >= 2:
                            self.stdout.write(f'   - Deleting duplicate user: {duplicate_user.id} ({duplicate_user.email})')
                        duplicate_user.delete()
                    
                    user = users_by_username.first()
                    user_created = False
                    if verbosity >= 2:
                        self.stdout.write(f'   - Using first user: {user.username} ({user.email})')
                
                elif users_by_username.count() == 1:
                    user = users_by_username.first()
                    user_created = False
                    if verbosity >= 2:
                        self.stdout.write(f'   - Found existing user by username: {user.username}')
                
                else:
                    # No user found by username, check by email
                    if verbosity >= 2:
                        self.stdout.write(f'   - Username not found, checking email: {email}')
                    
                    users_by_email = User.objects.filter(email=email)
                    
                    if users_by_email.count() > 1:
                        # Handle duplicate users by email - keep first, delete extras
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠️  Multiple users found with email "{email}" ({users_by_email.count()} total). '
                                f'Using first user and deleting duplicates.'
                            )
                        )
                        # Delete all but the first user
                        users_to_delete = list(users_by_email[1:])
                        for duplicate_user in users_to_delete:
                            if verbosity >= 2:
                                self.stdout.write(f'   - Deleting duplicate user: {duplicate_user.id} ({duplicate_user.username})')
                            duplicate_user.delete()
                        
                        user = users_by_email.first()
                        user_created = False
                        if verbosity >= 2:
                            self.stdout.write(f'   - Using first user: {user.email}')
                    
                    elif users_by_email.count() == 1:
                        user = users_by_email.first()
                        user_created = False
                        if verbosity >= 2:
                            self.stdout.write(f'   - Found existing user by email: {user.email}')
                    
                    else:
                        # User doesn't exist, create it using create_superuser
                        if verbosity >= 2:
                            self.stdout.write('   - No existing user found, creating new superuser...')
                        
                        user = User.objects.create_superuser(
                            username=username,
                            email=email,
                            password=password
                        )
                        user_created = True
                        
                        if verbosity >= 2:
                            self.stdout.write('   - Superuser created successfully')
                
                if user_created:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Superuser created: {email}')
                    )
                else:
                    # Update password and ensure superuser flags are set
                    user.set_password(password)
                    user.is_superuser = True
                    user.is_staff = True
                    user.is_active = True
                    user.save()
                    
                    if verbosity >= 2:
                        self.stdout.write(f'   - Updated password for existing superuser')
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Superuser password synced/updated: {user.email}')
                    )
                
                # Create root tenant if it doesn't exist
                if verbosity >= 2:
                    self.stdout.write('\n🏢 Attempting root tenant creation...')
                
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
                    if verbosity >= 2:
                        self.stdout.write('   - Root tenant created successfully')
                    self.stdout.write(
                        self.style.SUCCESS('✅ Default root tenant created')
                    )
                else:
                    if verbosity >= 2:
                        self.stdout.write(f'   - Root tenant already exists: {tenant.slug}')
                    self.stdout.write(
                        self.style.WARNING('⚠️  Default root tenant already exists')
                    )
                
                # Link superuser to root tenant with owner role if not already linked
                if verbosity >= 2:
                    self.stdout.write('\n🔗 Attempting to link superuser to tenant...')
                
                tenant_user, link_created = TenantUser.objects.get_or_create(
                    tenant=tenant,
                    user=user,
                    defaults={
                        'role': 'owner',
                        'is_active': True,
                    }
                )
                
                if link_created:
                    if verbosity >= 2:
                        self.stdout.write(f'   - Created link: user {user.username} -> tenant {tenant.slug}')
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Superuser linked to root tenant as owner')
                    )
                else:
                    if verbosity >= 2:
                        self.stdout.write(f'   - Link already exists: user {user.username} -> tenant {tenant.slug}')
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Superuser already linked to root tenant')
                    )
                
                self.stdout.write(
                    self.style.SUCCESS('\n🎉 Super tenant setup complete!')
                )
                
        except ImportError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Import error: {str(e)}\n'
                    f'Ensure the Tenant and TenantUser models are properly configured.'
                )
            )
            raise
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Database integrity error: {str(e)}\n'
                    f'This usually means a user with username "{username}" or email "{email}" '
                    f'already exists with different attributes.'
                )
            )
            raise
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error during super tenant creation: {str(e)}')
            )
            if verbosity >= 2:
                import traceback
                self.stdout.write('\nFull traceback:')
                self.stdout.write(traceback.format_exc())
            raise
