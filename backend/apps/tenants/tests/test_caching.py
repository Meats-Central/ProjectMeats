"""
Tests for tenant-aware caching isolation.

This module verifies that cache operations are properly isolated between tenants
when using django-tenants utilities, ensuring no key collisions occur.

Note: These tests require PostgreSQL with django-tenants backend to run in a full
schema-based multi-tenancy setup. Due to Django test runner limitations with
django-tenants, these tests serve as documentation and reference implementation.

For actual testing of cache isolation:
1. Deploy with django-tenants backend configured
2. Create test tenants via management commands
3. Run manual integration tests with real tenant schemas

To simulate these tests locally with PostgreSQL:
  DATABASE_URL="postgresql://user:pass@localhost/db" python manage.py shell
  # Then run the test logic interactively with real tenants
"""

from django.test import TestCase
from django.core.cache import cache
from django.conf import settings


def is_django_tenants_available():
    """
    Check if django-tenants is available and properly configured.
    
    Returns True if:
    - django_tenants can be imported
    - Database backend is django_tenants.postgresql_backend
    - Required models are available
    
    Note: This check may return False in Django test environment even when
    django-tenants is configured, due to test database setup limitations.
    """
    try:
        from django_tenants.utils import tenant_context, schema_context, get_public_schema_name
        from apps.tenants.models import Client, Domain
        
        # Check if the database backend supports django-tenants
        engine = settings.DATABASES['default'].get('ENGINE', '')
        return 'django_tenants' in engine
    except (ImportError, AttributeError):
        return False


class TenantCacheIsolationTests(TestCase):
    """
    Test cases for verifying cache isolation between tenants.
    
    These tests document the expected behavior of tenant-aware caching
    when using django-tenants with schema-based multi-tenancy.
    
    **Implementation Notes:**
    - Each tenant gets its own cache namespace based on schema
    - Cache keys are automatically prefixed with tenant schema name
    - No manual key prefixing required in application code
    - Cache operations respect tenant context
    
    **Testing Requirements:**
    - PostgreSQL database
    - django-tenants backend configured
    - Schemas created for test tenants
    - Cache backend supporting tenant isolation (e.g., Redis with key prefixing)
    """

    def setUp(self):
        """
        Set up test tenants with their schemas.
        
        Note: This setup requires django-tenants to be fully configured.
        If not available, tests will be skipped with explanation.
        """
        # Skip if django-tenants is not available
        if not is_django_tenants_available():
            self.skipTest(
                "django-tenants with PostgreSQL backend required for cache isolation tests. "
                "\n\n"
                "These tests demonstrate tenant-aware caching patterns but cannot run "
                "in standard Django test environment due to schema isolation requirements.\n\n"
                "To test cache isolation manually:\n"
                "1. Configure django-tenants backend in settings\n"
                "2. Create test tenants with schemas\n"
                "3. Use Django shell to test cache operations:\n"
                "   >>> from django_tenants.utils import tenant_context\n"
                "   >>> from apps.tenants.models import Client\n"
                "   >>> from django.core.cache import cache\n"
                "   >>> client_a = Client.objects.get(schema_name='tenant_a')\n"
                "   >>> with tenant_context(client_a):\n"
                "   ...     cache.set('key', 'value')\n"
                "   ...     print(cache.get('key'))  # 'value'\n"
            )
        
        # Import django-tenants utilities (only when available)
        from django_tenants.utils import tenant_context, schema_context, get_public_schema_name
        from apps.tenants.models import Client, Domain
        
        # Store for use in tests
        self.tenant_context = tenant_context
        self.schema_context = schema_context
        self.get_public_schema_name = get_public_schema_name
        self.Client = Client
        self.Domain = Domain
        
        # Create tenant A
        self.client_a = Client.objects.create(
            schema_name='tenant_a',
            name='Tenant A Corporation'
        )
        Domain.objects.create(
            domain='tenant-a.test.com',
            tenant=self.client_a,
            is_primary=True
        )

        # Create tenant B
        self.client_b = Client.objects.create(
            schema_name='tenant_b',
            name='Tenant B Corporation'
        )
        Domain.objects.create(
            domain='tenant-b.test.com',
            tenant=self.client_b,
            is_primary=True
        )

    def tearDown(self):
        """Clean up cache after each test."""
        cache.clear()

    def test_cache_is_tenant_isolated(self):
        """
        Test that cache data is isolated between different tenants.

        This test verifies:
        1. Data cached in tenant A is not accessible from tenant B
        2. Data cached in tenant A is not accessible from public schema
        3. Data cached in tenant A persists when switching back to tenant A
        
        **Expected Behavior:**
        - cache.set() in tenant A context stores data with tenant-specific prefix
        - cache.get() in tenant B context returns None (different prefix)
        - cache.get() in public schema returns None (different prefix)
        - cache.get() back in tenant A context returns original value
        
        **Cache Key Patterns:**
        - Tenant A: tenant_a:key_1 -> 'Tenant A Exclusive Data'
        - Tenant B: tenant_b:key_1 -> None
        - Public: public:key_1 -> None
        """
        # Set cache value in tenant A context
        with self.tenant_context(self.client_a):
            cache.set('key_1', 'Tenant A Exclusive Data', timeout=300)

        # Verify tenant B cannot access tenant A's cache
        with self.tenant_context(self.client_b):
            value_in_tenant_b = cache.get('key_1')
            self.assertIsNone(
                value_in_tenant_b,
                "Tenant B should not be able to access Tenant A's cached data"
            )

        # Verify public schema cannot access tenant A's cache
        with self.schema_context(self.get_public_schema_name()):
            value_in_public = cache.get('key_1')
            self.assertIsNone(
                value_in_public,
                "Public schema should not be able to access Tenant A's cached data"
            )

        # Verify tenant A can still access its own cached data
        with self.tenant_context(self.client_a):
            value_in_tenant_a = cache.get('key_1')
            self.assertEqual(
                value_in_tenant_a,
                'Tenant A Exclusive Data',
                "Tenant A should be able to access its own cached data"
            )

    def test_multiple_tenants_same_key(self):
        """
        Test that multiple tenants can use the same cache key without collision.

        This ensures that each tenant has its own isolated cache namespace.
        
        **Expected Behavior:**
        - Both tenants can use 'shared_key' without conflicts
        - Each tenant's value is isolated by schema prefix
        - Values remain independent when accessed in respective contexts
        
        **Cache Key Patterns:**
        - Tenant A: tenant_a:shared_key -> 'Value from Tenant A'
        - Tenant B: tenant_b:shared_key -> 'Value from Tenant B'
        """
        # Set different values for the same key in different tenants
        with self.tenant_context(self.client_a):
            cache.set('shared_key', 'Value from Tenant A', timeout=300)

        with self.tenant_context(self.client_b):
            cache.set('shared_key', 'Value from Tenant B', timeout=300)

        # Verify each tenant gets its own value
        with self.tenant_context(self.client_a):
            value_a = cache.get('shared_key')
            self.assertEqual(
                value_a,
                'Value from Tenant A',
                "Tenant A should get its own value for shared_key"
            )

        with self.tenant_context(self.client_b):
            value_b = cache.get('shared_key')
            self.assertEqual(
                value_b,
                'Value from Tenant B',
                "Tenant B should get its own value for shared_key"
            )

    def test_cache_delete_only_affects_current_tenant(self):
        """
        Test that deleting a cache key only affects the current tenant.

        Verifies that cache.delete() operations are tenant-scoped.
        
        **Expected Behavior:**
        - cache.delete() in tenant A removes only tenant A's key
        - Tenant B's key with same name remains intact
        - Deletion respects tenant context isolation
        
        **Cache Operations:**
        1. Set tenant_a:deletable_key and tenant_b:deletable_key
        2. Delete in tenant A context
        3. Verify tenant A's key deleted, tenant B's key persists
        """
        # Set the same key in both tenants
        with self.tenant_context(self.client_a):
            cache.set('deletable_key', 'Tenant A Data', timeout=300)

        with self.tenant_context(self.client_b):
            cache.set('deletable_key', 'Tenant B Data', timeout=300)

        # Delete from tenant A
        with self.tenant_context(self.client_a):
            cache.delete('deletable_key')
            # Verify it's deleted in tenant A
            self.assertIsNone(cache.get('deletable_key'))

        # Verify tenant B still has its data
        with self.tenant_context(self.client_b):
            value_b = cache.get('deletable_key')
            self.assertEqual(
                value_b,
                'Tenant B Data',
                "Tenant B's data should not be affected by Tenant A's delete operation"
            )

    def test_cache_timeout_per_tenant(self):
        """
        Test that cache timeouts are respected per tenant.

        Verifies that expired cache entries in one tenant don't affect another.
        
        **Expected Behavior:**
        - Each tenant can set different timeouts for same key name
        - Timeout expiration is tenant-specific
        - One tenant's expiration doesn't affect other tenants
        
        **Test Flow:**
        1. Tenant A sets key with 1 second timeout
        2. Tenant B sets key with 300 second timeout
        3. Wait 2 seconds
        4. Verify tenant A's key expired, tenant B's key valid
        """
        # Set short-lived cache in tenant A
        with self.tenant_context(self.client_a):
            cache.set('timeout_key', 'Short-lived data', timeout=1)

        # Set long-lived cache in tenant B
        with self.tenant_context(self.client_b):
            cache.set('timeout_key', 'Long-lived data', timeout=300)

        # Verify both have their values initially
        with self.tenant_context(self.client_a):
            self.assertIsNotNone(cache.get('timeout_key'))

        with self.tenant_context(self.client_b):
            self.assertIsNotNone(cache.get('timeout_key'))

        # Wait for tenant A's cache to expire
        import time
        time.sleep(2)

        # Verify tenant A's cache expired
        with self.tenant_context(self.client_a):
            self.assertIsNone(
                cache.get('timeout_key'),
                "Tenant A's cached data should have expired"
            )

        # Verify tenant B's cache is still valid
        with self.tenant_context(self.client_b):
            value_b = cache.get('timeout_key')
            self.assertEqual(
                value_b,
                'Long-lived data',
                "Tenant B's cached data should still be valid"
            )
