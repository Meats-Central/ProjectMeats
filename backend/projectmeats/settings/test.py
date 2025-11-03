"""
Test settings for ProjectMeats - uses SQLite for fast testing.
"""
from .base import *  # noqa

# Secret key for tests
SECRET_KEY = 'test-secret-key-not-for-production-use-only-testing'

# Use SQLite for testing (faster and doesn't require PostgreSQL)
# Note: django-tenants requires its router, but Client/Domain models won't be
# fully functional with SQLite (schemas not supported). Use PostgreSQL for
# testing schema-based multi-tenancy features.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',  # noqa
    }
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable migrations for faster tests
# class DisableMigrations:
#     def __contains__(self, item):
#         return True
#     def __getitem__(self, item):
#         return None
# MIGRATION_MODULES = DisableMigrations()
