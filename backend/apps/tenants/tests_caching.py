"""
Unit tests for tenant-aware caching isolation.

These tests verify that cache data is properly isolated between tenants
to prevent data leakage in a multi-tenant environment.
"""

from django.test import TestCase
from django.core.cache import cache
from django_tenants.utils import tenant_context, schema_context, get_public_schema_name
from apps.tenants.models import Tenant


class TenantCachingIsolationTestCase(TestCase):
    """Test cases for verifying tenant-aware caching isolation."""

    def setUp(self):
        """Set up test tenants for caching tests."""
        # Create test tenants
        self.tenant_a = Tenant.objects.create(
            name="Tenant A Test",
            slug="tenant-a-test",
            schema_name="tenant_a_test",
            contact_email="tenant-a@test.com",
            is_active=True,
        )
        
        self.tenant_b = Tenant.objects.create(
            name="Tenant B Test",
            slug="tenant-b-test",
            schema_name="tenant_b_test",
            contact_email="tenant-b@test.com",
            is_active=True,
        )

    def tearDown(self):
        """Clean up test data and cache."""
        # Clear cache to avoid interference with other tests
        cache.clear()
        
        # Delete test tenants
        self.tenant_a.delete()
        self.tenant_b.delete()

    def test_cache_is_tenant_isolated(self):
        """
        Test that cache data is isolated between tenants.
        
        This test verifies:
        1. Data cached in tenant A is not accessible from tenant B
        2. Data cached in tenant A is not accessible from public schema
        3. Data cached in tenant A persists within tenant A context
        """
        # Set cache data in Tenant A context
        with tenant_context(self.tenant_a):
            cache.set('key_1', 'Tenant A Exclusive Data', timeout=300)
            
            # Verify data is set in Tenant A
            cached_value_a = cache.get('key_1')
            self.assertEqual(
                cached_value_a,
                'Tenant A Exclusive Data',
                "Cache data should be accessible within Tenant A context"
            )

        # Verify cache isolation: Tenant B should NOT see Tenant A's data
        with tenant_context(self.tenant_b):
            cached_value_b = cache.get('key_1')
            self.assertIsNone(
                cached_value_b,
                "Cache data from Tenant A should NOT be accessible in Tenant B context"
            )
            
            # Set different data in Tenant B
            cache.set('key_1', 'Tenant B Different Data', timeout=300)
            cached_value_b2 = cache.get('key_1')
            self.assertEqual(
                cached_value_b2,
                'Tenant B Different Data',
                "Cache data should be accessible within Tenant B context"
            )

        # Verify cache isolation: Public schema should NOT see Tenant A's data
        with schema_context(get_public_schema_name()):
            cached_value_public = cache.get('key_1')
            self.assertIsNone(
                cached_value_public,
                "Cache data from Tenant A should NOT be accessible in public schema context"
            )

        # Verify persistence: Back to Tenant A, data should still be there
        with tenant_context(self.tenant_a):
            cached_value_a_persist = cache.get('key_1')
            self.assertEqual(
                cached_value_a_persist,
                'Tenant A Exclusive Data',
                "Cache data should persist within Tenant A context"
            )

    def test_cache_key_collision_prevention(self):
        """
        Test that identical cache keys in different tenants don't collide.
        
        This verifies that the caching backend properly namespaces keys
        by tenant to prevent key collisions.
        """
        test_key = 'shared_key_name'
        
        # Set different values for the same key in different tenants
        with tenant_context(self.tenant_a):
            cache.set(test_key, 'Value from Tenant A', timeout=300)
        
        with tenant_context(self.tenant_b):
            cache.set(test_key, 'Value from Tenant B', timeout=300)
        
        # Verify each tenant gets its own value
        with tenant_context(self.tenant_a):
            value_a = cache.get(test_key)
            self.assertEqual(
                value_a,
                'Value from Tenant A',
                "Tenant A should retrieve its own cached value"
            )
        
        with tenant_context(self.tenant_b):
            value_b = cache.get(test_key)
            self.assertEqual(
                value_b,
                'Value from Tenant B',
                "Tenant B should retrieve its own cached value, not Tenant A's"
            )

    def test_cache_deletion_is_tenant_isolated(self):
        """
        Test that deleting cache in one tenant doesn't affect other tenants.
        
        This verifies that cache invalidation is properly scoped to tenants.
        """
        test_key = 'deletion_test_key'
        
        # Set cache in both tenants
        with tenant_context(self.tenant_a):
            cache.set(test_key, 'Tenant A Data', timeout=300)
        
        with tenant_context(self.tenant_b):
            cache.set(test_key, 'Tenant B Data', timeout=300)
        
        # Delete from Tenant A
        with tenant_context(self.tenant_a):
            cache.delete(test_key)
            value_a = cache.get(test_key)
            self.assertIsNone(
                value_a,
                "Cache should be deleted in Tenant A"
            )
        
        # Verify Tenant B still has its data
        with tenant_context(self.tenant_b):
            value_b = cache.get(test_key)
            self.assertEqual(
                value_b,
                'Tenant B Data',
                "Tenant B's cache should not be affected by Tenant A's deletion"
            )
