"""
Test settings for ProjectMeats - simplified for CI/CD testing without django-tenants complexity
"""
import os

import dj_database_url

from .base import *  # noqa

# Secret key for tests
SECRET_KEY = "test-secret-key-not-for-production-use-only-testing"

# Database configuration
# Simplified: Use standard PostgreSQL without django-tenants schema isolation
# This aligns with the custom shared-schema multi-tenancy approach used in base.py
database_url = os.environ.get("DATABASE_URL", "").strip()

if database_url:
    # Parse DATABASE_URL
    _db_config = dj_database_url.parse(database_url)

    # Use STANDARD PostgreSQL backend (not django-tenants backend)
    # This matches the production approach: custom shared-schema multi-tenancy
    # No schema isolation - all tenants share same schema with tenant_id filtering
    if _db_config.get("ENGINE") == "django.db.backends.postgresql":
        # Keep standard backend - do NOT switch to django_tenants.postgresql_backend
        pass  # Explicitly keep django.db.backends.postgresql

    DATABASES = {"default": _db_config}
    
    # Do NOT enable django-tenants - use custom shared-schema approach
    # Remove django-tenants from INSTALLED_APPS if it exists
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "django_tenants"]  # noqa
    
    # Do NOT add django-tenants middleware - use custom tenant middleware
    # The custom apps.tenants.middleware.TenantMiddleware is already in base.py
    MIDDLEWARE = [m for m in MIDDLEWARE if "django_tenants" not in m]  # noqa
    
    # No schema-based routing needed for shared-schema approach
    DATABASE_ROUTERS = []
    
else:
    # Use SQLite for testing (faster and doesn't require PostgreSQL)
    # Note: This is for local unit tests without multi-tenancy complexity
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test_db.sqlite3",  # noqa
        }
    }

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Allow all hosts for testing (including tenant domain tests)
ALLOWED_HOSTS = ["*"]

# Disable caching during tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}
