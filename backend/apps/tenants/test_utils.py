"""
Test utilities for django-tenants multi-tenancy testing.
"""
import os
from django.test import TestCase
from django.db import connection


def is_postgres_configured():
    """Check if PostgreSQL is configured for testing."""
    return "postgresql" in connection.settings_dict.get("ENGINE", "")


def is_django_tenants_enabled():
    """Check if django-tenants is enabled and configured."""
    try:
        from django_tenants.utils import get_tenant_model, get_tenant_domain_model
        from django.apps import apps
        return apps.is_installed("django_tenants")
    except ImportError:
        return False


class TenantTestMixin:
    """
    Mixin for test cases that need tenant support.
    Automatically sets up tenant context when django-tenants is available.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if is_django_tenants_enabled() and is_postgres_configured():
            cls._setup_tenant_context()
    
    @classmethod
    def _setup_tenant_context(cls):
        """Set up tenant context for tests."""
        try:
            from django_tenants.utils import get_tenant_model, schema_context
            from apps.tenants.models import Domain
            
            # Get or create test tenant
            Client = get_tenant_model()
            tenant, created = Client.objects.get_or_create(
                schema_name='test_tenant',
                defaults={
                    'name': 'Test Tenant',
                    'paid_until': '2099-12-31',
                    'on_trial': True
                }
            )
            
            # Create domain for test tenant
            domain, created = Domain.objects.get_or_create(
                domain='test.example.com',
                defaults={
                    'tenant': tenant,
                    'is_primary': True
                }
            )
            
            cls.tenant = tenant
            cls.domain = domain
            
        except Exception as e:
            print(f"Warning: Could not set up tenant context: {e}")
            cls.tenant = None
            cls.domain = None


class TenantTestCase(TenantTestMixin, TestCase):
    """
    TestCase with automatic tenant setup for django-tenants.
    Falls back gracefully when django-tenants is not configured.
    """
    pass


def with_tenant_context(test_func):
    """
    Decorator to run a test within a tenant context.
    Only applies when django-tenants is configured.
    """
    def wrapper(self, *args, **kwargs):
        if (hasattr(self, 'tenant') and 
            self.tenant and 
            is_django_tenants_enabled()):
            
            from django_tenants.utils import schema_context
            with schema_context(self.tenant.schema_name):
                return test_func(self, *args, **kwargs)
        else:
            return test_func(self, *args, **kwargs)
    
    return wrapper