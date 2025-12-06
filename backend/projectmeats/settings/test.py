"""
Test settings for ProjectMeats - with shared-schema multi-tenancy
ProjectMeats uses SHARED SCHEMA ONLY - no django-tenants schema isolation
"""
import os

import dj_database_url

from .base import *  # noqa

# Secret key for tests
SECRET_KEY = "test-secret-key-not-for-production-use-only-testing"

# Database configuration with standard PostgreSQL backend
database_url = os.environ.get("DATABASE_URL", "").strip()

if database_url:
    # Parse DATABASE_URL
    _db_config = dj_database_url.parse(database_url)

    # Use standard PostgreSQL backend for shared-schema multi-tenancy
    if _db_config.get("ENGINE") == "django.db.backends.postgresql":
        _db_config["ENGINE"] = "django.db.backends.postgresql"
        
        # Add connection timeout for database reliability
        if "OPTIONS" not in _db_config:
            _db_config["OPTIONS"] = {}
        _db_config["OPTIONS"]["connect_timeout"] = 10

    DATABASES = {"default": _db_config}
    
else:
    # Use PostgreSQL with standard backend for testing
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("TEST_DB_NAME", "test_projectmeats"),
            "USER": os.environ.get("TEST_DB_USER", os.environ.get("DB_USER", "postgres")),
            "PASSWORD": os.environ.get("TEST_DB_PASSWORD", os.environ.get("DB_PASSWORD", "postgres")),
            "HOST": os.environ.get("TEST_DB_HOST", os.environ.get("DB_HOST", "db")),
            "PORT": os.environ.get("TEST_DB_PORT", os.environ.get("DB_PORT", "5432")),
            "TEST": {
                "NAME": os.environ.get("TEST_DB_NAME", "test_projectmeats"),
            },
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
