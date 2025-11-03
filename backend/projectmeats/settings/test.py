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
    # Parse DATABASE_URL and update to use django-tenants backend if PostgreSQL
    _db_config = dj_database_url.parse(database_url)

    # Use django-tenants backend for PostgreSQL to enable schema-based multi-tenancy
    if _db_config.get("ENGINE") == "django.db.backends.postgresql":
        _db_config["ENGINE"] = "django_tenants.postgresql_backend"

    DATABASES = {"default": _db_config}
else:
    # Use SQLite for testing (faster and doesn't require PostgreSQL)
    # Note: django-tenants is incompatible with SQLite. We remove it from INSTALLED_APPS
    # and use only the shared-schema multi-tenancy approach for SQLite tests.
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
