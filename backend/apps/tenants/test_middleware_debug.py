"""
Tests for TenantMiddleware debug logging functionality.

These tests verify that the temporary debug logging for staging.meatscentral.com
and uat.meatscentral.com doesn't interfere with normal middleware operation.
"""

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from apps.tenants.middleware import TenantMiddleware
from apps.tenants.models import Tenant, TenantUser, TenantDomain
from unittest.mock import Mock
import logging


class TenantMiddlewareDebugLoggingTests(TestCase):
    """Test that debug logging for staging.meatscentral.com and uat.meatscentral.com works correctly."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.get_response = Mock(return_value=Mock(status_code=200))
        self.middleware = TenantMiddleware(self.get_response)
        
        # Create test tenant
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test",
            contact_email="test@example.com"
        )
        
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass"
        )

    def test_middleware_works_without_debug_domains(self):
        """Test that middleware works normally for non-debug domains."""
        request = self.factory.get('/', HTTP_HOST='example.com')
        request.user = self.user
        
        response = self.middleware(request)
        
        # Should process request normally
        self.assertEqual(response.status_code, 200)
        self.get_response.assert_called_once()

    def test_middleware_works_with_staging_domain(self):
        """Test that middleware works for staging.meatscentral.com."""
        # Create domain entry for staging
        TenantDomain.objects.create(
            domain="staging.meatscentral.com",
            tenant=self.tenant,
            is_primary=True
        )
        
        request = self.factory.get('/', HTTP_HOST='staging.meatscentral.com')
        request.user = self.user
        
        # Capture logs
        with self.assertLogs('apps.tenants.middleware', level='INFO') as logs:
            response = self.middleware(request)
        
        # Should process request normally
        self.assertEqual(response.status_code, 200)
        self.get_response.assert_called_once()
        
        # Should have debug logs
        log_output = '\n'.join(logs.output)
        self.assertIn('[STAGING DEBUG]', log_output)
        self.assertIn('Request received', log_output)
        self.assertIn('staging.meatscentral.com', log_output)

    def test_middleware_logs_tenant_resolution_success(self):
        """Test that successful tenant resolution is logged for staging."""
        # Create domain entry
        TenantDomain.objects.create(
            domain="staging.meatscentral.com",
            tenant=self.tenant,
            is_primary=True
        )
        
        request = self.factory.get('/', HTTP_HOST='staging.meatscentral.com')
        request.user = self.user
        
        with self.assertLogs('apps.tenants.middleware', level='INFO') as logs:
            response = self.middleware(request)
        
        log_output = '\n'.join(logs.output)
        self.assertIn('Final tenant resolution SUCCESS', log_output)
        self.assertIn(f'tenant={self.tenant.slug}', log_output)

    def test_middleware_logs_tenant_resolution_failure(self):
        """Test that failed tenant resolution is logged for staging."""
        # No domain entry created, so resolution should fail
        request = self.factory.get('/', HTTP_HOST='staging.meatscentral.com')
        request.user = User.objects.create_user(
            username="notenantuser",
            email="notenant@example.com"
        )
        
        with self.assertLogs('apps.tenants.middleware', level='INFO') as logs:
            response = self.middleware(request)
        
        log_output = '\n'.join(logs.output)
        self.assertIn('Final tenant resolution FAILED', log_output)

    def test_middleware_sets_tenant_attribute(self):
        """Test that middleware sets request.tenant correctly."""
        TenantDomain.objects.create(
            domain="staging.meatscentral.com",
            tenant=self.tenant,
            is_primary=True
        )
        
        request = self.factory.get('/', HTTP_HOST='staging.meatscentral.com')
        request.user = self.user
        
        self.middleware(request)
        
        # Should have set tenant attribute
        self.assertEqual(request.tenant, self.tenant)

    def test_middleware_handles_exception_logging(self):
        """Test that exceptions during processing are logged for staging."""
        TenantDomain.objects.create(
            domain="staging.meatscentral.com",
            tenant=self.tenant,
            is_primary=True
        )
        
        # Make get_response raise an exception
        self.get_response.side_effect = ValueError("Test exception")
        
        request = self.factory.get('/', HTTP_HOST='staging.meatscentral.com')
        request.user = self.user
        
        with self.assertLogs('apps.tenants.middleware', level='INFO') as logs:
            with self.assertRaises(ValueError):
                self.middleware(request)
        
        log_output = '\n'.join(logs.output)
        self.assertIn('[STAGING DEBUG]', log_output)
        self.assertIn('Exception during request processing', log_output)
        self.assertIn('ValueError', log_output)

    def test_middleware_works_with_uat_domain(self):
        """Test that middleware works for uat.meatscentral.com."""
        # Create domain entry for UAT
        TenantDomain.objects.create(
            domain="uat.meatscentral.com",
            tenant=self.tenant,
            is_primary=True
        )
        
        request = self.factory.get('/', HTTP_HOST='uat.meatscentral.com')
        request.user = self.user
        
        # Capture logs
        with self.assertLogs('apps.tenants.middleware', level='INFO') as logs:
            response = self.middleware(request)
        
        # Should process request normally
        self.assertEqual(response.status_code, 200)
        
        # Should have UAT debug logs
        log_output = '\n'.join(logs.output)
        self.assertIn('[UAT DEBUG]', log_output)
        self.assertIn('Request received', log_output)
        self.assertIn('uat.meatscentral.com', log_output)

    def test_middleware_logs_uat_tenant_resolution_success(self):
        """Test that successful tenant resolution is logged for UAT."""
        # Create domain entry
        TenantDomain.objects.create(
            domain="uat.meatscentral.com",
            tenant=self.tenant,
            is_primary=True
        )
        
        request = self.factory.get('/', HTTP_HOST='uat.meatscentral.com')
        request.user = self.user
        
        with self.assertLogs('apps.tenants.middleware', level='INFO') as logs:
            response = self.middleware(request)
        
        log_output = '\n'.join(logs.output)
        self.assertIn('[UAT DEBUG]', log_output)
        self.assertIn('Final tenant resolution SUCCESS', log_output)
        self.assertIn(f'tenant={self.tenant.slug}', log_output)
