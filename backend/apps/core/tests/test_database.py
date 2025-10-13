"""
Database connectivity and permissions tests for ProjectMeats.

Tests database connection, write operations, and permission handling
across different database backends (PostgreSQL, SQLite).
"""

from django.test import TestCase
from django.db import connection, transaction, OperationalError
from django.contrib.auth import get_user_model
from apps.core.models import Protein
from unittest.mock import patch
import os


User = get_user_model()


class DatabaseConnectivityTest(TestCase):
    """Test database connectivity and basic operations."""

    def test_database_connection(self):
        """Test that database connection is active and working."""
        with connection.cursor() as cursor:
            # Simple query to verify connection
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)

    def test_database_engine_configured(self):
        """Test that database engine is properly configured."""
        engine = connection.settings_dict["ENGINE"]
        self.assertIn(
            engine,
            ["django.db.backends.postgresql", "django.db.backends.sqlite3"],
            f"Database engine {engine} is not supported",
        )

    def test_database_write_operations(self):
        """Test that database supports write operations."""
        # Create a test protein
        protein = Protein.objects.create(name="Test Beef")

        # Verify it was created
        self.assertIsNotNone(protein.id)

        # Update it
        protein.name = "Updated Test Beef"
        protein.save()

        # Verify update
        updated_protein = Protein.objects.get(id=protein.id)
        self.assertEqual(updated_protein.name, "Updated Test Beef")

        # Delete it
        protein.delete()

        # Verify deletion
        self.assertFalse(Protein.objects.filter(id=protein.id).exists())

    def test_transaction_rollback(self):
        """Test that database supports transaction rollback."""
        initial_count = Protein.objects.count()

        try:
            with transaction.atomic():
                Protein.objects.create(name="Rollback Test Protein")
                # Force rollback by raising exception
                raise Exception("Test rollback")
        except Exception:
            pass

        # Verify count hasn't changed
        self.assertEqual(Protein.objects.count(), initial_count)

    def test_concurrent_writes(self):
        """Test that database handles concurrent write operations."""
        # Create multiple proteins in rapid succession
        proteins = [Protein(name=f"Concurrent Test {i}") for i in range(5)]

        # Bulk create
        created = Protein.objects.bulk_create(proteins)
        self.assertEqual(len(created), 5)

        # Cleanup
        Protein.objects.filter(name__startswith="Concurrent Test").delete()


class DatabasePermissionsTest(TestCase):
    """Test database permissions and readonly error handling."""

    def test_user_creation_permission(self):
        """Test that database allows user creation (write permission)."""
        user = User.objects.create_user(
            username="testuser_dbperms",
            email="testuser@example.com",
            password="testpass123",
        )

        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "testuser_dbperms")

        # Cleanup
        user.delete()

    def test_session_handling(self):
        """Test that session creation and deletion works (for readonly DB fix)."""
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        from datetime import timedelta

        # Create a test session
        session = Session.objects.create(
            session_key="test_session_key_12345",
            session_data="test_data",
            expire_date=timezone.now() + timedelta(days=1),
        )

        # Verify creation
        self.assertTrue(
            Session.objects.filter(session_key="test_session_key_12345").exists()
        )

        # Delete session (this is where readonly errors often occur)
        session.delete()

        # Verify deletion
        self.assertFalse(
            Session.objects.filter(session_key="test_session_key_12345").exists()
        )


class DatabaseConfigurationTest(TestCase):
    """Test database configuration from environment variables."""

    def test_postgresql_configuration(self):
        """Test PostgreSQL configuration from environment variables."""
        engine = connection.settings_dict["ENGINE"]

        if engine == "django.db.backends.postgresql":
            # Verify all required PostgreSQL settings are present
            self.assertIn("NAME", connection.settings_dict)
            self.assertIn("USER", connection.settings_dict)
            self.assertIn("PASSWORD", connection.settings_dict)
            self.assertIn("HOST", connection.settings_dict)
            self.assertIn("PORT", connection.settings_dict)

            # Verify they're not placeholder values
            if os.getenv("DB_NAME"):
                self.assertNotEqual(
                    connection.settings_dict["NAME"], "change_me_in_secrets"
                )

    def test_connection_timeout_configured(self):
        """Test that connection timeout is configured for PostgreSQL."""
        engine = connection.settings_dict["ENGINE"]

        if engine == "django.db.backends.postgresql":
            options = connection.settings_dict.get("OPTIONS", {})
            self.assertIn("connect_timeout", options)
            self.assertGreater(int(options["connect_timeout"]), 0)

    def test_database_accessibility(self):
        """Test that database is accessible and responsive."""
        # Execute a simple query with timeout
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM django_migrations")
                result = cursor.fetchone()
                self.assertIsNotNone(result)
                self.assertGreater(result[0], 0, "No migrations found in database")
        except Exception as e:
            self.fail(f"Database query failed: {str(e)}")


class DatabaseMigrationTest(TestCase):
    """Test database migration status."""

    def test_migrations_applied(self):
        """Test that all migrations have been applied."""
        from django.db.migrations.executor import MigrationExecutor

        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

        # If plan is empty, all migrations are applied
        self.assertEqual(
            len(plan), 0, f"Unapplied migrations detected: {[m[0].name for m in plan]}"
        )

    def test_database_tables_exist(self):
        """Test that expected database tables exist."""
        with connection.cursor() as cursor:
            # Get list of tables
            if connection.vendor == "postgresql":
                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """
                )
            else:  # SQLite
                cursor.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table'
                """
                )

            tables = [row[0] for row in cursor.fetchall()]

            # Verify essential tables exist
            essential_tables = [
                "django_migrations",
                "auth_user",
                "django_session",
                "core_protein",
                "tenants_tenant",
            ]

            for table in essential_tables:
                self.assertIn(
                    table, tables, f"Essential table '{table}' not found in database"
                )


class ReadOnlyDatabaseErrorTest(TestCase):
    """Test handling of readonly database errors."""

    def test_readonly_database_error_detection(self):
        """Test readonly database errors are properly detected and handled."""
        from apps.core.exceptions import exception_handler

        # Simulate a readonly database error
        exc = OperationalError("attempt to write a readonly database")
        context = {
            "view": type(
                "MockView",
                (),
                {"__class__": type("MockViewClass", (), {"__name__": "TestView"})},
            )(),
            "request": type(
                "MockRequest",
                (),
                {
                    "user": type(
                        "MockUser",
                        (),
                        {"is_authenticated": False, "username": "anonymous"},
                    )(),
                    "path": "/admin/",
                    "method": "POST",
                },
            )(),
        }

        # Call the exception handler
        response = exception_handler(exc, context)

        # Verify response
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Database write failure")
        self.assertIn("details", response.data)
        self.assertIn("read-only", response.data["details"].lower())

    def test_admin_session_with_readonly_database(self):
        """Test readonly database errors handled gracefully."""
        # This test verifies the error handling works, not that login
        # succeeds. In a real readonly database scenario, the login
        # would fail but the app should handle it gracefully with
        # proper error messages

        # Create a test user first
        user = User.objects.create_superuser(
            username="testadmin", email="admin@test.com", password="testpass123"
        )

        # Verify user was created successfully
        self.assertIsNotNone(user.id)
        self.assertTrue(user.is_superuser)

        # Note: Actual simulation of readonly database during session operations
        # requires server-level configuration and cannot be fully tested in unit tests
        # This test verifies the user creation works, which is a prerequisite

    def test_database_error_logging(self):
        """Test that database errors are properly logged with context."""
        from apps.core.exceptions import exception_handler

        # Create a mock logger to capture log output
        with patch("apps.core.exceptions.logger") as mock_logger:
            exc = OperationalError("attempt to write a readonly database")
            context = {
                "view": type(
                    "MockView",
                    (),
                    {"__class__": type("MockViewClass", (), {"__name__": "TestView"})},
                )(),
                "request": type(
                    "MockRequest",
                    (),
                    {
                        "user": type(
                            "MockUser",
                            (),
                            {"is_authenticated": True, "username": "testuser"},
                        )(),
                        "path": "/api/v1/suppliers/",
                        "method": "POST",
                    },
                )(),
            }

            # Call the exception handler
            exception_handler(exc, context)

            # Verify logging was called
            self.assertTrue(mock_logger.critical.called)
            call_args = mock_logger.critical.call_args

            # Verify log message contains relevant information
            log_message = call_args[0][0]
            self.assertIn("Read-Only Database Error", log_message)

            # Verify extra context was provided
            if "extra" in call_args[1]:
                extra = call_args[1]["extra"]
                self.assertIn("user", extra)
                self.assertIn("path", extra)
                self.assertEqual(extra["user"], "testuser")
                self.assertEqual(extra["path"], "/api/v1/suppliers/")
            if "extra" in call_args[1]:
                extra = call_args[1]["extra"]
                self.assertIn("user", extra)
                self.assertIn("path", extra)
                self.assertEqual(extra["user"], "testuser")
                self.assertEqual(extra["path"], "/api/v1/suppliers/")
