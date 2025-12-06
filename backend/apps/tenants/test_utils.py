"""
Test utilities for shared-schema multi-tenancy testing.

ProjectMeats uses shared-schema multi-tenancy where:
- All tenants share one PostgreSQL schema
- Tenant isolation is via tenant_id ForeignKey
- No django-tenants schema_context needed
"""
import os
from django.test import TestCase
from django.db import connection


def is_postgres_configured():
    """Check if PostgreSQL is configured for testing."""
    return "postgresql" in connection.settings_dict.get("ENGINE", "")


class TenantTestMixin:
    """
    Mixin for test cases that need tenant support.
    Sets up a test tenant for shared-schema multi-tenancy tests.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_tenant_context()
    
    @classmethod
    def _setup_tenant_context(cls):
        """Set up tenant context for tests."""
        try:
            from apps.tenants.models import Tenant, TenantDomain
            
            # Get or create test tenant
            tenant, created = Tenant.objects.get_or_create(
                slug='test-tenant',
                defaults={
                    'name': 'Test Tenant',
                    'contact_email': 'test@example.com',
                    'is_active': True,
                    'is_trial': True
                }
            )
            
            # Create domain for test tenant
            domain, created = TenantDomain.objects.get_or_create(
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
    TestCase with automatic tenant setup for shared-schema multi-tenancy.
    """
    pass


def with_tenant_context(test_func):
    """
    Decorator to run a test with a tenant in the request context.
    For shared-schema, this just ensures self.tenant is available.
    """
    def wrapper(self, *args, **kwargs):
        if hasattr(self, 'tenant') and self.tenant:
            return test_func(self, *args, **kwargs)
        else:
            return test_func(self, *args, **kwargs)
    
    return wrapper