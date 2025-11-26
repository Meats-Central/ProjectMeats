"""
Test settings for ProjectMeats - uses SQLite for fast testing, or PostgreSQL if DATABASE_URL is provided.
"""
import os

import dj_database_url

from .base import *  # noqa

# Secret key for tests
SECRET_KEY = "test-secret-key-not-for-production-use-only-testing"

# Database configuration
# If DATABASE_URL is provided (e.g., in CI), use it with django-tenants support
# Otherwise, fall back to SQLite for fast local testing
database_url = os.environ.get("DATABASE_URL", "").strip()

if database_url:
    # Parse DATABASE_URL
    _db_config = dj_database_url.parse(database_url)

    # Use standard PostgreSQL backend (not django-tenants)
    # ProjectMeats uses custom shared-schema multi-tenancy
    # if _db_config.get("ENGINE") == "django.db.backends.postgresql":
    #     _db_config["ENGINE"] = "django_tenants.postgresql_backend"

    DATABASES = {"default": _db_config}
    
    # If using standard PostgreSQL backend (not django_tenants.postgresql_backend),
    # remove django-tenants middleware as it requires schema-based features
    if _db_config.get("ENGINE") == "django.db.backends.postgresql":
        MIDDLEWARE = [m for m in MIDDLEWARE if "django_tenants" not in m]  # noqa
        DATABASE_ROUTERS = []
else:
    # Use SQLite for testing (faster and doesn't require PostgreSQL)
    # Note: For full multi-tenancy testing with PostgreSQL schemas,
    # use PostgreSQL with DATABASE_URL environment variable
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test_db.sqlite3",  # noqa
        }
    }
    
    # Remove django-tenants from installed apps for SQLite
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django_tenants"]  # noqa
    
    # Remove django-tenants middleware for SQLite
    MIDDLEWARE = [m for m in MIDDLEWARE if "django_tenants" not in m]  # noqa
    
    # Disable django-tenants router for SQLite
    DATABASE_ROUTERS = []

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable migrations for faster tests
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()

# Allow all hosts for testing (including middleware tests with various domains)
ALLOWED_HOSTS = ["*"]
