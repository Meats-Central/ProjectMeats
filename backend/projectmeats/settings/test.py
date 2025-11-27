"""
Test settings for ProjectMeats - enhanced for django-tenants multi-tenancy testing
"""
import os

import dj_database_url

from .base import *  # noqa

# Secret key for tests
SECRET_KEY = "test-secret-key-not-for-production-use-only-testing"

# Database configuration
# Enhanced to support django-tenants testing
database_url = os.environ.get("DATABASE_URL", "").strip()

if database_url:
    # Parse DATABASE_URL
    _db_config = dj_database_url.parse(database_url)

    # Use django-tenants PostgreSQL backend for multi-tenancy support
    if _db_config.get("ENGINE") == "django.db.backends.postgresql":
        _db_config["ENGINE"] = "django_tenants.postgresql_backend"

    DATABASES = {"default": _db_config}
    
    # Enable django-tenants for PostgreSQL
    INSTALLED_APPS = ["django_tenants"] + [app for app in INSTALLED_APPS if app != "django_tenants"]  # noqa
    
    # Ensure django-tenants middleware is first
    MIDDLEWARE = ["django_tenants.middleware.TenantMainMiddleware"] + [
        m for m in MIDDLEWARE if "django_tenants" not in m
    ]  # noqa
    
    # Use schema-based routing for django-tenants
    DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)
    
    # Tenant model configuration
    TENANT_MODEL = "tenants.Client"  # Use Client model for schema-based tenancy
    TENANT_DOMAIN_MODEL = "tenants.Domain"
    
else:
    # Use SQLite for testing (faster and doesn't require PostgreSQL)
    # Note: This disables multi-tenancy features for fast unit tests
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

# Allow all hosts for testing (including tenant domain tests)
ALLOWED_HOSTS = ["*"]

# Disable caching during tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Test-specific settings for tenant creation
if database_url:
    # Enable auto tenant creation for tests
    TENANT_CREATION_FAKES_MIGRATIONS = True
    # Ensure tenant schemas are created automatically
    AUTO_CREATE_SCHEMA = True
