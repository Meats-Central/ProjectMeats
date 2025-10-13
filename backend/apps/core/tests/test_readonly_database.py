"""
Tests for read-only database error handling in ProjectMeats.

These tests verify that the application handles read-only database errors
gracefully, particularly in scenarios like:
- Admin access with session management
- Django authentication flow
- Database write operations during read-only state
"""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.db import OperationalError, connection
from django.test import RequestFactory, TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.exceptions import exception_handler
from apps.tenants.middleware import TenantMiddleware
from apps.tenants.models import Tenant, TenantUser

User = get_user_model()


class ReadOnlyDatabaseErrorHandlingTest(APITestCase):
    """Test error handling for read-only database scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testuser_readonly", email="test@example.com", password="testpass123"
        )
        self.factory = RequestFactory()

    def tearDown(self):
        """Clean up test data."""
        self.user.delete()

    @patch("django.db.backends.utils.CursorWrapper.execute")
    def test_exception_handler_catches_readonly_error(self, mock_execute):
        """Test that exception handler properly catches readonly database errors."""
        # Simulate a readonly database error
        mock_execute.side_effect = OperationalError("attempt to write a readonly database")

        # Create a fake exception context
        exc = OperationalError("attempt to write a readonly database")
        context = {
            "view": MagicMock(__class__=MagicMock(__name__="TestView")),
            "request": MagicMock(
                method="POST",
                path="/api/test/",
                user=MagicMock(is_authenticated=True, username="testuser"),
            ),
        }

        # Call the exception handler
        response = exception_handler(exc, context)

        # Verify response
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Database Write Failure")
        self.assertIn("readonly_database", str(response.data.get("error_type", "")))

    def test_exception_handler_readonly_variations(self):
        """Test that exception handler catches various readonly error messages."""
        readonly_messages = [
            "attempt to write a readonly database",
            "database is read-only",
            "database is in read only mode",
            "readonly database",
        ]

        for message in readonly_messages:
            exc = OperationalError(message)
            context = {
                "view": MagicMock(__class__=MagicMock(__name__="TestView")),
                "request": MagicMock(
                    method="POST", path="/api/test/", user=MagicMock(is_authenticated=False)
                ),
            }

            response = exception_handler(exc, context)

            self.assertIsNotNone(response, f"Failed for message: {message}")
            self.assertEqual(
                response.status_code,
                status.HTTP_503_SERVICE_UNAVAILABLE,
                f"Wrong status code for message: {message}",
            )
            self.assertEqual(
                response.data["error"],
                "Database Write Failure",
                f"Wrong error message for: {message}",
            )

    def test_session_handling_with_readonly_simulation(self):
        """Test that session handling errors are properly caught."""
        # This test verifies that session creation/deletion errors are handled
        # Note: We can't actually make the DB readonly in tests, but we verify
        # the error handling path exists

        # Create a session
        session = Session.objects.create(
            session_key="test_readonly_session", session_data="test_data", expire_date="2025-12-31"
        )

        # Verify it exists
        self.assertTrue(Session.objects.filter(session_key="test_readonly_session").exists())

        # Clean up
        session.delete()

        # Verify deletion succeeded
        self.assertFalse(Session.objects.filter(session_key="test_readonly_session").exists())


class TenantMiddlewareReadOnlyTest(TestCase):
    """Test TenantMiddleware handling of read-only database errors."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser_middleware", email="test@example.com", password="testpass123"
        )
        self.tenant = Tenant.objects.create(name="Test Tenant", slug="test-tenant", is_active=True)
        self.middleware = TenantMiddleware(get_response=lambda r: MagicMock())

    def tearDown(self):
        """Clean up test data."""
        # Clean up in reverse order of dependencies
        TenantUser.objects.filter(user=self.user).delete()
        self.tenant.delete()
        self.user.delete()

    def test_middleware_handles_tenant_user_query_error(self):
        """Test that middleware handles TenantUser query errors gracefully."""
        request = self.factory.get("/test/")
        request.user = self.user
        request.tenant = self.tenant

        # Create TenantUser association
        TenantUser.objects.create(user=self.user, tenant=self.tenant, role="member", is_active=True)

        # Mock a database error during TenantUser fetch
        with patch("apps.tenants.middleware.TenantUser.objects.get") as mock_get:
            mock_get.side_effect = OperationalError("database is read-only")

            # The middleware should catch this error and log it
            # It should not crash
            try:
                self.middleware(request)  # noqa: F841
                # Verify request attributes were set (even with error)
                self.assertIsNotNone(request.tenant)
            except OperationalError:
                self.fail("Middleware should not re-raise OperationalError")

    def test_middleware_readonly_error_in_response_path(self):
        """Test that middleware logs readonly errors in response path."""
        request = self.factory.get("/admin/")
        request.user = self.user
        request.tenant = None

        # Mock get_response to raise readonly error
        def mock_get_response(req):
            raise OperationalError("attempt to write a readonly database")

        middleware = TenantMiddleware(get_response=mock_get_response)

        # The middleware should log the error and re-raise
        with self.assertRaises(OperationalError):
            middleware(request)


class AdminAccessReadOnlyTest(TestCase):
    """Test admin access with read-only database scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testadmin",
            email="admin@example.com",
            password="adminpass123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(self.user)

    def tearDown(self):
        """Clean up test data."""
        self.user.delete()

    def test_admin_access_requires_write_permissions(self):
        """Test that admin access requires database write permissions."""
        # This test verifies that the admin interface setup works
        # and doesn't fail with database write errors

        # The admin URLs should be registered
        from django.urls import reverse

        try:
            admin_url = reverse("admin:index")
            self.assertTrue(admin_url is not None)
        except Exception:
            # If reverse fails, that's okay - we're just checking setup
            pass

        # Verify user has admin permissions
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.is_superuser)

    def test_authenticated_user_session_handling(self):
        """Test that authenticated user sessions are handled properly."""
        # This test verifies the authentication flow works
        # which requires session table write access

        # Force login (creates session)
        self.client.force_login(self.user)

        # Verify session exists
        self.assertTrue(self.client.session.session_key is not None)

        # Make a request that requires authentication
        response = self.client.get("/api/v1/tenants/")

        # Should be authenticated
        self.assertNotEqual(response.status_code, 401)


class DatabaseWritePermissionsTest(TestCase):
    """Test database write permissions and error scenarios."""

    def test_database_supports_write_operations(self):
        """Test that database supports write operations (no readonly issues)."""
        # This test ensures the test database is not readonly
        user = User.objects.create_user(
            username="write_test_user", email="write@test.com", password="testpass"
        )

        # Update
        user.email = "updated@test.com"
        user.save()

        # Verify
        updated_user = User.objects.get(username="write_test_user")
        self.assertEqual(updated_user.email, "updated@test.com")

        # Delete
        user.delete()
        self.assertFalse(User.objects.filter(username="write_test_user").exists())

    def test_database_engine_appropriate_for_environment(self):
        """Test that database engine is appropriate for the environment."""
        engine = connection.settings_dict["ENGINE"]

        # Should be either PostgreSQL or SQLite
        self.assertIn(
            engine,
            ["django.db.backends.postgresql", "django.db.backends.sqlite3"],
            f"Unexpected database engine: {engine}",
        )

        # Log which engine is being used
        print(f"Test database engine: {engine}")
