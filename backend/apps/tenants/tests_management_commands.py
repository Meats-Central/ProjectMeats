"""
Tests for the create_super_tenant management command.
"""
from io import StringIO
from unittest import mock
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.tenants.models import Tenant, TenantUser


User = get_user_model()


class CreateSuperTenantCommandTests(TestCase):
    """Test cases for create_super_tenant management command."""

    def setUp(self):
        """Set up test environment."""
        # Clean up any existing data
        User.objects.all().delete()
        Tenant.objects.all().delete()
        TenantUser.objects.all().delete()

    def test_creates_superuser_and_tenant_when_none_exist(self):
        """Test that command creates superuser and tenant when they don't exist."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_EMAIL': 'test@example.com',
            'SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('create_super_tenant', stdout=out)
        
        # Check superuser was created
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
        user = User.objects.get(email='test@example.com')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertTrue(user.check_password('testpass123'))
        
        # Check tenant was created
        self.assertTrue(Tenant.objects.filter(slug='root').exists())
        tenant = Tenant.objects.get(slug='root')
        self.assertEqual(tenant.name, 'Root')
        self.assertEqual(tenant.contact_email, 'test@example.com')
        self.assertFalse(tenant.is_trial)
        self.assertTrue(tenant.is_active)
        
        # Check user is linked to tenant
        self.assertTrue(
            TenantUser.objects.filter(tenant=tenant, user=user).exists()
        )
        tenant_user = TenantUser.objects.get(tenant=tenant, user=user)
        self.assertEqual(tenant_user.role, 'owner')
        self.assertTrue(tenant_user.is_active)
        
        # Check output messages
        output = out.getvalue()
        self.assertIn('Superuser created', output)
        self.assertIn('root tenant created', output)
        self.assertIn('linked to root tenant', output)

    def test_idempotent_when_superuser_already_exists(self):
        """Test that command syncs password when superuser exists."""
        # Create existing superuser
        User.objects.create_superuser(
            username='admin',
            email='test@example.com',
            password='oldpass'
        )
        
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_EMAIL': 'test@example.com',
            'SUPERUSER_PASSWORD': 'newpass'
        }):
            call_command('create_super_tenant', stdout=out)
        
        # Should only have one user
        self.assertEqual(User.objects.filter(email='test@example.com').count(), 1)
        
        # Password SHOULD be changed to sync with environment variable
        user = User.objects.get(email='test@example.com')
        self.assertTrue(user.check_password('newpass'))
        self.assertFalse(user.check_password('oldpass'))
        
        # Ensure superuser flags are set
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        
        # Check output indicates password sync
        output = out.getvalue()
        self.assertIn('synced/updated', output)

    def test_command_line_arguments_override_env_vars(self):
        """Test that command-line arguments override environment variables."""
        # Set environment variables
        with mock.patch.dict('os.environ', {
            'SUPERUSER_EMAIL': 'env@example.com',
            'SUPERUSER_PASSWORD': 'envpass',
            'SUPERUSER_USERNAME': 'envuser'
        }):
            out = StringIO()
            
            # Call command with command-line arguments that should override env vars
            call_command(
                'create_super_tenant',
                username='cmduser',
                email='cmd@example.com',
                password='cmdpass',
                stdout=out
            )
        
        # Check that command-line arguments were used
        self.assertTrue(User.objects.filter(username='cmduser').exists())
        self.assertTrue(User.objects.filter(email='cmd@example.com').exists())
        
        user = User.objects.get(username='cmduser')
        self.assertTrue(user.check_password('cmdpass'))
        self.assertTrue(user.is_superuser)
        
        # Check that env vars were NOT used
        self.assertFalse(User.objects.filter(username='envuser').exists())
        self.assertFalse(User.objects.filter(email='env@example.com').exists())

    def test_idempotent_when_tenant_already_exists(self):
        """Test that command is idempotent when tenant exists."""
        # Create existing user and tenant
        user = User.objects.create_superuser(
            username='admin',
            email='test@example.com',
            password='testpass'
        )
        tenant = Tenant.objects.create(
            name='ExistingRoot',
            slug='root',
            contact_email='old@example.com',
            created_by=user
        )
        
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_EMAIL': 'test@example.com',
            'SUPERUSER_PASSWORD': 'testpass'
        }):
            call_command('create_super_tenant', stdout=out)
        
        # Should only have one tenant
        self.assertEqual(Tenant.objects.filter(slug='root').count(), 1)
        
        # Tenant should not be modified
        tenant.refresh_from_db()
        self.assertEqual(tenant.name, 'ExistingRoot')
        self.assertEqual(tenant.contact_email, 'old@example.com')
        
        # Check output indicates existing tenant
        output = out.getvalue()
        self.assertIn('already exists', output)

    def test_uses_default_credentials_when_env_vars_not_set(self):
        """Test that command uses default credentials when env vars not set."""
        out = StringIO()
        
        # Ensure env vars are not set
        with mock.patch.dict('os.environ', {}, clear=True):
            call_command('create_super_tenant', stdout=out)
        
        # Check default email was used
        self.assertTrue(
            User.objects.filter(email='admin@meatscentral.com').exists()
        )
        user = User.objects.get(email='admin@meatscentral.com')
        self.assertTrue(user.is_superuser)

    def test_links_existing_user_to_new_tenant(self):
        """Test that existing user is properly linked to newly created tenant."""
        # Create user without tenant
        user = User.objects.create_superuser(
            username='admin',
            email='test@example.com',
            password='testpass'
        )
        
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_EMAIL': 'test@example.com',
            'SUPERUSER_PASSWORD': 'testpass'
        }):
            call_command('create_super_tenant', stdout=out)
        
        # Check tenant was created
        self.assertTrue(Tenant.objects.filter(slug='root').exists())
        
        # Check user is linked to tenant
        tenant = Tenant.objects.get(slug='root')
        self.assertTrue(
            TenantUser.objects.filter(tenant=tenant, user=user).exists()
        )

    def test_does_not_duplicate_tenant_user_link(self):
        """Test that existing tenant-user link is not duplicated."""
        # Create user, tenant, and link
        user = User.objects.create_superuser(
            username='admin',
            email='test@example.com',
            password='testpass'
        )
        tenant = Tenant.objects.create(
            name='Root',
            slug='root',
            contact_email='test@example.com',
            created_by=user
        )
        TenantUser.objects.create(
            tenant=tenant,
            user=user,
            role='owner'
        )
        
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_EMAIL': 'test@example.com',
            'SUPERUSER_PASSWORD': 'testpass'
        }):
            call_command('create_super_tenant', stdout=out)
        
        # Should only have one link
        self.assertEqual(
            TenantUser.objects.filter(tenant=tenant, user=user).count(),
            1
        )
        
        # Check output indicates existing link
        output = out.getvalue()
        self.assertIn('already linked', output)

    def test_handles_duplicate_username_scenario(self):
        """Test that command handles existing user with same username but different email."""
        # Create a user with username 'admin' but different email
        existing_user = User.objects.create_user(
            username='admin',
            email='different@example.com',
            password='existingpass'
        )
        
        out = StringIO()
        
        # Try to create super tenant with admin@meatscentral.com (username would be 'admin')
        with mock.patch.dict('os.environ', {
            'SUPERUSER_EMAIL': 'admin@meatscentral.com',
            'SUPERUSER_PASSWORD': 'newpass'
        }):
            # This should NOT raise IntegrityError
            call_command('create_super_tenant', stdout=out)
        
        # Should use the existing user with username 'admin'
        self.assertEqual(User.objects.filter(username='admin').count(), 1)
        
        # The existing user should be used (not create a new one)
        user = User.objects.get(username='admin')
        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.email, 'different@example.com')  # Email should not change
        
        # Password should be synced to the new password
        self.assertTrue(user.check_password('newpass'))
        self.assertFalse(user.check_password('existingpass'))
        
        # Superuser flags should be set
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        
        # Tenant should be created
        self.assertTrue(Tenant.objects.filter(slug='root').exists())
        
        # User should be linked to tenant
        tenant = Tenant.objects.get(slug='root')
        self.assertTrue(
            TenantUser.objects.filter(tenant=tenant, user=user).exists()
        )
        
        # Check output indicates password sync
        output = out.getvalue()
        self.assertIn('synced/updated', output)

    def test_handles_missing_env_vars(self):
        """Test that command works even when env vars are missing."""
        out = StringIO()
        
        # Ensure env vars are completely unset
        with mock.patch.dict('os.environ', {}, clear=True):
            # Should use defaults and not raise an error
            call_command('create_super_tenant', stdout=out)
        
        # Check default credentials were used
        self.assertTrue(
            User.objects.filter(email='admin@meatscentral.com').exists()
        )
        user = User.objects.get(email='admin@meatscentral.com')
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.username, 'admin')

    def test_password_rotation_on_existing_user(self):
        """Test that password can be rotated multiple times for existing user."""
        # Create initial superuser
        User.objects.create_superuser(
            username='admin',
            email='test@example.com',
            password='password1'
        )
        
        passwords = ['password2', 'password3', 'password4']
        
        for new_password in passwords:
            out = StringIO()
            
            with mock.patch.dict('os.environ', {
                'SUPERUSER_EMAIL': 'test@example.com',
                'SUPERUSER_PASSWORD': new_password
            }):
                call_command('create_super_tenant', stdout=out)
            
            # Should only have one user
            self.assertEqual(User.objects.filter(email='test@example.com').count(), 1)
            
            # Password should be updated to the new one
            user = User.objects.get(email='test@example.com')
            self.assertTrue(user.check_password(new_password))
            
            # Old passwords should not work
            self.assertFalse(user.check_password('password1'))
            for old_pass in passwords[:passwords.index(new_password)]:
                self.assertFalse(user.check_password(old_pass))
            
            # Superuser flags should be maintained
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_active)
            
            # Check output
            output = out.getvalue()
            self.assertIn('synced/updated', output)


    def test_verbosity_level_logging(self):
        """Test that verbosity level 2 produces detailed logging."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_EMAIL': 'verbose@example.com',
            'SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('create_super_tenant', stdout=out, verbosity=2)
        
        output = out.getvalue()
        
        # Check for detailed logging messages
        self.assertIn('Configuration:', output)
        self.assertIn('Email:', output)
        self.assertIn('Username:', output)
        self.assertIn('Attempting superuser creation', output)
        self.assertIn('Attempting root tenant creation', output)
        self.assertIn('Attempting to link superuser to tenant', output)

    def test_uses_superuser_username_env_var(self):
        """Test that SUPERUSER_USERNAME env var is used."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_USERNAME': 'customadmin',
            'SUPERUSER_EMAIL': 'custom@example.com',
            'SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('create_super_tenant', stdout=out)
        
        # Check custom username was used
        self.assertTrue(User.objects.filter(username='customadmin').exists())
        user = User.objects.get(username='customadmin')
        self.assertEqual(user.email, 'custom@example.com')
        self.assertTrue(user.is_superuser)

    def test_create_superuser_method_used(self):
        """Test that create_superuser method is used (password handling)."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_EMAIL': 'password@example.com',
            'SUPERUSER_PASSWORD': 'complexpass456!'
        }):
            call_command('create_super_tenant', stdout=out)
        
        user = User.objects.get(email='password@example.com')
        
        # Password should be properly hashed (not stored as plain text)
        self.assertNotEqual(user.password, 'complexpass456!')
        # Password should start with a hash algorithm identifier
        # In test settings, we use MD5 for speed; in production we use PBKDF2
        self.assertTrue(
            user.password.startswith('pbkdf2_sha256$') or 
            user.password.startswith('md5$') or
            user.password.startswith('argon2') or
            user.password.startswith('bcrypt'),
            f'Password does not appear to be hashed: {user.password[:20]}'
        )
        
        # Password should be verifiable
        self.assertTrue(user.check_password('complexpass456!'))


class SetupSuperuserCommandTests(TestCase):
    """Test cases for setup_superuser management command."""

    def setUp(self):
        """Set up test environment."""
        # Clean up any existing data
        User.objects.all().delete()

    def test_creates_superuser_when_none_exists_development(self):
        """Test that command creates superuser in development environment."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_USERNAME': 'devadmin',
            'DEVELOPMENT_SUPERUSER_EMAIL': 'devadmin@example.com',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Check superuser was created
        self.assertTrue(User.objects.filter(username='devadmin').exists())
        user = User.objects.get(username='devadmin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.email, 'devadmin@example.com')
        
        # Check output
        output = out.getvalue()
        self.assertIn('Superuser created', output)

    def test_creates_superuser_when_none_exists_staging(self):
        """Test that command creates superuser in staging environment."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'staging',
            'STAGING_SUPERUSER_USERNAME': 'stagingadmin',
            'STAGING_SUPERUSER_EMAIL': 'staging@example.com',
            'STAGING_SUPERUSER_PASSWORD': 'stagingpass123'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Check superuser was created
        self.assertTrue(User.objects.filter(username='stagingadmin').exists())
        user = User.objects.get(username='stagingadmin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('stagingpass123'))
        
        # Check output
        output = out.getvalue()
        self.assertIn('Superuser created', output)

    def test_creates_superuser_when_none_exists_production(self):
        """Test that command creates superuser in production environment."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'production',
            'PRODUCTION_SUPERUSER_USERNAME': 'prodadmin',
            'PRODUCTION_SUPERUSER_EMAIL': 'prod@example.com',
            'PRODUCTION_SUPERUSER_PASSWORD': 'prodpass123'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Check superuser was created
        self.assertTrue(User.objects.filter(username='prodadmin').exists())
        user = User.objects.get(username='prodadmin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('prodpass123'))
        
        # Check output
        output = out.getvalue()
        self.assertIn('Superuser created', output)

    def test_updates_password_when_user_exists(self):
        """Test that command updates password when superuser already exists."""
        # Create existing superuser with old password
        User.objects.create_superuser(
            username='devadmin',
            email='devadmin@example.com',
            password='oldpass123'
        )
        
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_USERNAME': 'devadmin',
            'DEVELOPMENT_SUPERUSER_EMAIL': 'devadmin@example.com',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'newpass456'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Should only have one user
        self.assertEqual(User.objects.filter(username='devadmin').count(), 1)
        
        # Password SHOULD be changed (this is the key difference from create_super_tenant)
        user = User.objects.get(username='devadmin')
        self.assertFalse(user.check_password('oldpass123'))
        self.assertTrue(user.check_password('newpass456'))
        
        # Check output
        output = out.getvalue()
        self.assertIn('password synced/updated', output)

    def test_updates_email_when_user_exists(self):
        """Test that command updates email when superuser already exists."""
        # Create existing superuser
        User.objects.create_superuser(
            username='admin',
            email='old@example.com',
            password='testpass'
        )
        
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_USERNAME': 'admin',
            'DEVELOPMENT_SUPERUSER_EMAIL': 'new@example.com',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'testpass'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Email should be updated
        user = User.objects.get(username='admin')
        self.assertEqual(user.email, 'new@example.com')

    def test_raises_error_when_username_missing_in_production(self):
        """Test that command raises error when username is missing in production."""
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'production',
            'PRODUCTION_SUPERUSER_EMAIL': 'admin@example.com',
            'PRODUCTION_SUPERUSER_PASSWORD': 'testpass'
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                call_command('setup_superuser')
            
            self.assertIn('username', str(context.exception).lower())

    def test_raises_error_when_email_missing_in_staging(self):
        """Test that command raises error when email is missing in staging."""
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'staging',
            'STAGING_SUPERUSER_USERNAME': 'admin',
            'STAGING_SUPERUSER_PASSWORD': 'testpass'
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                call_command('setup_superuser')
            
            self.assertIn('email', str(context.exception).lower())

    def test_raises_error_when_password_missing_in_production(self):
        """Test that command raises error when password is missing in production."""
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'production',
            'PRODUCTION_SUPERUSER_USERNAME': 'admin',
            'PRODUCTION_SUPERUSER_EMAIL': 'admin@example.com'
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                call_command('setup_superuser')
            
            self.assertIn('password', str(context.exception).lower())

    def test_raises_error_when_password_missing_in_staging(self):
        """Test that command raises error when password is missing in staging."""
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'staging',
            'STAGING_SUPERUSER_USERNAME': 'admin',
            'STAGING_SUPERUSER_EMAIL': 'admin@example.com'
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                call_command('setup_superuser')
            
            self.assertIn('password', str(context.exception).lower())

    def test_uses_defaults_in_development(self):
        """Test that command uses default values in development when not provided."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'testpass123'
        }, clear=True):
            call_command('setup_superuser', stdout=out)
        
        # Check default username and email were used
        self.assertTrue(User.objects.filter(username='admin').exists())
        user = User.objects.get(username='admin')
        self.assertEqual(user.email, 'admin@meatscentral.com')
        self.assertTrue(user.check_password('testpass123'))

    def test_uses_default_username_and_email(self):
        """Test that command uses default username and email when not provided."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'testpass123'
        }, clear=True):
            call_command('setup_superuser', stdout=out)
        
        # Check default username was used
        self.assertTrue(User.objects.filter(username='admin').exists())
        user = User.objects.get(username='admin')
        self.assertEqual(user.email, 'admin@meatscentral.com')

    def test_idempotent_password_sync(self):
        """Test that command can be run multiple times with same password."""
        # Create initial user
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'samepass123'
        }):
            call_command('setup_superuser')
        
        # Run again with same password
        out = StringIO()
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'samepass123'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Should still only have one user
        self.assertEqual(User.objects.filter(username='admin').count(), 1)
        
        # Password should still work
        user = User.objects.get(username='admin')
        self.assertTrue(user.check_password('samepass123'))

    def test_password_rotation_scenario(self):
        """Test password rotation scenario with multiple updates."""
        passwords = ['pass1', 'pass2', 'pass3']
        
        for password in passwords:
            with mock.patch.dict('os.environ', {
                'DJANGO_ENV': 'development',
                'DEVELOPMENT_SUPERUSER_PASSWORD': password
            }):
                call_command('setup_superuser')
            
            # Verify password was updated
            user = User.objects.get(username='admin')
            self.assertTrue(user.check_password(password))
            
            # Verify old passwords don't work
            for old_pass in passwords[:passwords.index(password)]:
                self.assertFalse(user.check_password(old_pass))
        
        # Should still only have one user
        self.assertEqual(User.objects.filter(username='admin').count(), 1)

    def test_dynamic_username_in_staging(self):
        """Test dynamic username assignment in staging environment."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'staging',
            'STAGING_SUPERUSER_USERNAME': 'custom_admin',
            'STAGING_SUPERUSER_EMAIL': 'custom@staging.com',
            'STAGING_SUPERUSER_PASSWORD': 'testpass'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Verify custom username was used
        self.assertTrue(User.objects.filter(username='custom_admin').exists())
        user = User.objects.get(username='custom_admin')
        self.assertEqual(user.email, 'custom@staging.com')

    def test_dynamic_username_in_production(self):
        """Test dynamic username assignment in production environment."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'production',
            'PRODUCTION_SUPERUSER_USERNAME': 'prod_superadmin',
            'PRODUCTION_SUPERUSER_EMAIL': 'superadmin@prod.com',
            'PRODUCTION_SUPERUSER_PASSWORD': 'prodpass'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Verify custom username was used
        self.assertTrue(User.objects.filter(username='prod_superadmin').exists())
        user = User.objects.get(username='prod_superadmin')
        self.assertEqual(user.email, 'superadmin@prod.com')

    def test_email_mismatch_warning(self):
        """Test that command warns when email changes for existing user."""
        # Create user with one email
        User.objects.create_superuser(
            username='admin',
            email='old@example.com',
            password='oldpass'
        )
        
        out = StringIO()
        
        # Update with different email
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_EMAIL': 'new@meatscentral.com',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'newpass123'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Check that warning was issued
        output = out.getvalue()
        self.assertIn('Email mismatch detected', output)
        self.assertIn('old@example.com', output)
        self.assertIn('new@meatscentral.com', output)
        
        # Verify email was updated
        user = User.objects.get(username='admin')
        self.assertEqual(user.email, 'new@meatscentral.com')

    def test_email_sync_fallback_to_default(self):
        """Test that email falls back to default in development."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'DEVELOPMENT_SUPERUSER_PASSWORD': 'testpass123'
        }, clear=True):
            call_command('setup_superuser', stdout=out)
        
        # Should use default email
        user = User.objects.get(username='admin')
        self.assertEqual(user.email, 'admin@meatscentral.com')

    def test_authentication_verification_after_password_sync(self):
        """Test that command verifies authentication after syncing password."""
        # Create existing superuser
        User.objects.create_superuser(
            username='uatadmin',
            email='uat@example.com',
            password='oldpass123'
        )
        
        out = StringIO()
        
        # Update password and verify authentication works
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'uat',
            'STAGING_SUPERUSER_USERNAME': 'uatadmin',
            'STAGING_SUPERUSER_EMAIL': 'uat@example.com',
            'STAGING_SUPERUSER_PASSWORD': 'newpass456'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Password should be updated
        user = User.objects.get(username='uatadmin')
        self.assertTrue(user.check_password('newpass456'))
        
        # Check output includes password verification
        output = out.getvalue()
        self.assertIn('Password verified', output)

    def test_authentication_verification_for_new_user(self):
        """Test that command verifies password for newly created user."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'staging',
            'STAGING_SUPERUSER_USERNAME': 'newtestuser',
            'STAGING_SUPERUSER_EMAIL': 'newtest@example.com',
            'STAGING_SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('setup_superuser', stdout=out)
        
        # User should be created and password should work
        user = User.objects.get(username='newtestuser')
        self.assertTrue(user.check_password('testpass123'))
        
        # Check output includes password verification
        output = out.getvalue()
        self.assertIn('Password verified', output)
        self.assertIn('Superuser created', output)

    def test_authentication_fails_with_mock_failure(self):
        """Test that password verification catches password issues."""
        out = StringIO()
        
        # Create a mock User model that always returns False for check_password
        from unittest.mock import patch, MagicMock
        
        def mock_create_superuser(*args, **kwargs):
            user = MagicMock()
            user.check_password = MagicMock(return_value=False)
            user.refresh_from_db = MagicMock()
            user.username = kwargs.get('username')
            user.email = kwargs.get('email')
            return user
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'staging',
            'STAGING_SUPERUSER_USERNAME': 'failtest',
            'STAGING_SUPERUSER_EMAIL': 'failtest@example.com',
            'STAGING_SUPERUSER_PASSWORD': 'testpass123'
        }):
            with patch.object(User.objects, 'create_superuser', side_effect=mock_create_superuser):
                with self.assertRaises(ValueError) as context:
                    call_command('setup_superuser', stdout=out)
                
                # Should raise ValueError about password verification failure
                self.assertIn('password', str(context.exception).lower())
                self.assertIn('verification', str(context.exception).lower())


