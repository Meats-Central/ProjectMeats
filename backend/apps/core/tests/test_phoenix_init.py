"""
Tests for the phoenix_init management command.
"""
from io import StringIO
from unittest import mock
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.tenants.models import Tenant, TenantDomain, TenantUser


User = get_user_model()


class PhoenixInitCommandTests(TestCase):
    """Test cases for phoenix_init management command."""

    def setUp(self):
        """Set up test environment."""
        # Clean up any existing data
        User.objects.all().delete()
        Tenant.objects.all().delete()
        TenantDomain.objects.all().delete()
        TenantUser.objects.all().delete()

    def test_command_creates_superuser_when_credentials_provided(self):
        """Test that command creates superuser with environment credentials."""
        out = StringIO()

        with mock.patch.dict('os.environ', {
            'DJANGO_SUPERUSER_EMAIL': 'admin@example.com',
            'DJANGO_SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('phoenix_init', stdout=out)

        # Check superuser was created
        self.assertTrue(User.objects.filter(email='admin@example.com').exists())
        user = User.objects.get(email='admin@example.com')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('testpass123'))

        # Check output
        output = out.getvalue()
        self.assertIn('Superuser created', output)

    def test_command_uses_existing_superuser_when_no_credentials(self):
        """Test that command uses existing superuser when credentials not provided."""
        # Create an existing superuser
        User.objects.create_superuser(
            username='existing',
            email='existing@example.com',
            password='existingpass'
        )

        out = StringIO()

        with mock.patch.dict('os.environ', {}, clear=True):
            call_command('phoenix_init', stdout=out)

        # Check that existing superuser was used
        output = out.getvalue()
        self.assertIn('Superuser exists', output)

        # Verify no new superuser was created
        self.assertEqual(User.objects.filter(is_superuser=True).count(), 1)

    def test_command_creates_public_tenant(self):
        """Test that command creates public tenant."""
        out = StringIO()

        with mock.patch.dict('os.environ', {
            'DJANGO_SUPERUSER_EMAIL': 'admin@example.com',
            'DJANGO_SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('phoenix_init', stdout=out)

        # Check public tenant was created
        self.assertTrue(Tenant.objects.filter(schema_name='public').exists())
        public_tenant = Tenant.objects.get(schema_name='public')
        self.assertEqual(public_tenant.name, 'Public')
        self.assertEqual(public_tenant.slug, 'public')

        # Check output
        output = out.getvalue()
        self.assertIn('Public Tenant', output)

    def test_command_creates_demo_tenant_and_domain(self):
        """Test that command creates demo tenant and domain."""
        out = StringIO()

        with mock.patch.dict('os.environ', {
            'DJANGO_SUPERUSER_EMAIL': 'admin@example.com',
            'DJANGO_SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('phoenix_init', stdout=out)

        # Check demo tenant was created
        self.assertTrue(Tenant.objects.filter(name='demo').exists())
        demo_tenant = Tenant.objects.get(name='demo')
        self.assertEqual(demo_tenant.schema_name, 'demo')
        self.assertEqual(demo_tenant.slug, 'demo')

        # Check demo domain was created
        self.assertTrue(TenantDomain.objects.filter(domain='demo.localhost').exists())
        demo_domain = TenantDomain.objects.get(domain='demo.localhost')
        self.assertEqual(demo_domain.tenant, demo_tenant)

        # Check output
        output = out.getvalue()
        self.assertIn('Demo Tenant', output)

    def test_command_links_superuser_to_demo_tenant(self):
        """Test that command links superuser to demo tenant as owner."""
        out = StringIO()

        with mock.patch.dict('os.environ', {
            'DJANGO_SUPERUSER_EMAIL': 'admin@example.com',
            'DJANGO_SUPERUSER_PASSWORD': 'testpass123'
        }):
            call_command('phoenix_init', stdout=out)

        # Get superuser and demo tenant
        user = User.objects.get(email='admin@example.com')
        demo_tenant = Tenant.objects.get(name='demo')

        # Check link was created
        self.assertTrue(TenantUser.objects.filter(tenant=demo_tenant, user=user).exists())
        tenant_user = TenantUser.objects.get(tenant=demo_tenant, user=user)
        self.assertEqual(tenant_user.role, 'owner')

        # Check output
        output = out.getvalue()
        self.assertIn('Superuser linked to Demo Tenant', output)

    def test_command_is_idempotent(self):
        """Test that command can be run multiple times without errors."""
        out1 = StringIO()
        out2 = StringIO()

        with mock.patch.dict('os.environ', {
            'DJANGO_SUPERUSER_EMAIL': 'admin@example.com',
            'DJANGO_SUPERUSER_PASSWORD': 'testpass123'
        }):
            # Run command first time
            call_command('phoenix_init', stdout=out1)

            # Run command second time
            call_command('phoenix_init', stdout=out2)

        # Check that only one of each entity was created
        self.assertEqual(User.objects.filter(email='admin@example.com').count(), 1)
        self.assertEqual(Tenant.objects.filter(schema_name='public').count(), 1)
        self.assertEqual(Tenant.objects.filter(name='demo').count(), 1)
        self.assertEqual(TenantDomain.objects.filter(domain='demo.localhost').count(), 1)

        # Check that second run showed existing items
        output2 = out2.getvalue()
        self.assertIn('Superuser exists', output2)
