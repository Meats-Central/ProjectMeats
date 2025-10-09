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
        """Test that command is idempotent when superuser exists."""
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
        
        # Password should NOT be changed
        user = User.objects.get(email='test@example.com')
        self.assertTrue(user.check_password('oldpass'))
        
        # Check output indicates existing user
        output = out.getvalue()
        self.assertIn('already exists', output)

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
        
        # Tenant should be created
        self.assertTrue(Tenant.objects.filter(slug='root').exists())
        
        # User should be linked to tenant
        tenant = Tenant.objects.get(slug='root')
        self.assertTrue(
            TenantUser.objects.filter(tenant=tenant, user=user).exists()
        )
        
        # Check output indicates existing user
        output = out.getvalue()
        self.assertIn('already exists', output)

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
        
        # Password should be properly hashed
        self.assertNotEqual(user.password, 'complexpass456!')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        
        # Password should be verifiable
        self.assertTrue(user.check_password('complexpass456!'))


class SetupSuperuserCommandTests(TestCase):
    """Test cases for setup_superuser management command."""

    def setUp(self):
        """Set up test environment."""
        # Clean up any existing data
        User.objects.all().delete()

    def test_creates_superuser_when_none_exists(self):
        """Test that command creates superuser when none exists."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_USERNAME': 'admin',
            'SUPERUSER_EMAIL': 'admin@example.com',
            'ENVIRONMENT_SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Check superuser was created
        self.assertTrue(User.objects.filter(username='admin').exists())
        user = User.objects.get(username='admin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('testpass123'))
        
        # Check output
        output = out.getvalue()
        self.assertIn('Superuser created', output)

    def test_updates_password_when_user_exists(self):
        """Test that command updates password when superuser already exists."""
        # Create existing superuser with old password
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='oldpass123'
        )
        
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'SUPERUSER_USERNAME': 'admin',
            'SUPERUSER_EMAIL': 'admin@example.com',
            'ENVIRONMENT_SUPERUSER_PASSWORD': 'newpass456'
        }):
            call_command('setup_superuser', stdout=out)
        
        # Should only have one user
        self.assertEqual(User.objects.filter(username='admin').count(), 1)
        
        # Password SHOULD be changed (this is the key difference from create_super_tenant)
        user = User.objects.get(username='admin')
        self.assertFalse(user.check_password('oldpass123'))
        self.assertTrue(user.check_password('newpass456'))
        
        # Check output
        output = out.getvalue()
        self.assertIn('password synced/updated', output)

    def test_raises_error_when_password_missing_in_production(self):
        """Test that command raises error when ENVIRONMENT_SUPERUSER_PASSWORD is missing in production."""
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'production',
            'SUPERUSER_USERNAME': 'admin',
            'SUPERUSER_EMAIL': 'admin@example.com'
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                call_command('setup_superuser')
            
            self.assertIn('ENVIRONMENT_SUPERUSER_PASSWORD', str(context.exception))

    def test_raises_error_when_password_missing_in_staging(self):
        """Test that command raises error when ENVIRONMENT_SUPERUSER_PASSWORD is missing in staging."""
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'staging',
            'SUPERUSER_USERNAME': 'admin',
            'SUPERUSER_EMAIL': 'admin@example.com'
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                call_command('setup_superuser')
            
            self.assertIn('ENVIRONMENT_SUPERUSER_PASSWORD', str(context.exception))

    def test_falls_back_to_superuser_password_in_dev(self):
        """Test that command falls back to SUPERUSER_PASSWORD in development."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'development',
            'SUPERUSER_USERNAME': 'admin',
            'SUPERUSER_EMAIL': 'admin@example.com',
            'SUPERUSER_PASSWORD': 'fallbackpass'
        }, clear=True):
            call_command('setup_superuser', stdout=out)
        
        # User should be created with fallback password
        user = User.objects.get(username='admin')
        self.assertTrue(user.check_password('fallbackpass'))
        
        # Check warning message
        output = out.getvalue()
        self.assertIn('fallback', output)

    def test_uses_default_username_and_email(self):
        """Test that command uses default username and email when not provided."""
        out = StringIO()
        
        with mock.patch.dict('os.environ', {
            'ENVIRONMENT_SUPERUSER_PASSWORD': 'testpass123'
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
            'ENVIRONMENT_SUPERUSER_PASSWORD': 'samepass123'
        }):
            call_command('setup_superuser')
        
        # Run again with same password
        out = StringIO()
        with mock.patch.dict('os.environ', {
            'ENVIRONMENT_SUPERUSER_PASSWORD': 'samepass123'
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
                'ENVIRONMENT_SUPERUSER_PASSWORD': password
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

