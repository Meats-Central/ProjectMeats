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
