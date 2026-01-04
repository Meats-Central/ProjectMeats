"""
Development settings for ProjectMeats.
"""
import logging

import dj_database_url
from decouple import config

from .base import *

# Get logger for database configuration
logger = logging.getLogger(__name__)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "SECRET_KEY",
    default="django-insecure-dev-key-change-in-production-3k2j5h2k5j3h5k2j3h5k2j3",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Read additional ALLOWED_HOSTS from environment variable (comma-separated)
# This allows GitHub Secrets to override/extend the default list
_env_hosts = config("ALLOWED_HOSTS", default="", cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "testserver",
    "0.0.0.0",
    ".dev.meatscentral.com",  # Wildcard for *.dev.meatscentral.com
    ".meatscentral.com",  # Wildcard for all subdomains
    "dev.meatscentral.com",
    "dev-backend.meatscentral.com",
    "uat.meatscentral.com",
    "uat-backend.meatscentral.com",
    "157.245.114.182",
] + _env_hosts  # Append hosts from environment variable


# Database Configuration
# Development now uses PostgreSQL for environment parity with staging/production
# Falls back to SQLite if PostgreSQL environment variables are not configured

# Priority 1: Use DATABASE_URL if provided (common in CI/CD)
# Priority 2: Use DB_ENGINE with individual DB_* settings
# Priority 3: Fall back to SQLite

database_url = config("DATABASE_URL", default="").strip()

if database_url:
    # Parse DATABASE_URL
    _db_config = dj_database_url.parse(database_url)

    # Use standard Django PostgreSQL backend (shared-schema multi-tenancy)
    # No django-tenants - we use tenant_id foreign keys for isolation

    # Set connection settings for development
    _db_config.setdefault(
        "CONN_MAX_AGE", 0
    )  # Close connections after each request in development
    
    # Only add connect_timeout for PostgreSQL (not supported in SQLite)
    if "postgresql" in _db_config.get("ENGINE", ""):
        _db_config.setdefault("OPTIONS", {})
        _db_config["OPTIONS"].setdefault("connect_timeout", 10)

    DATABASES = {"default": _db_config}
else:
    # Get DB_ENGINE - PostgreSQL is hardcoded default (shared-schema multi-tenancy)
    # Using config() to read from .env file for local development
    DB_ENGINE = config("DB_ENGINE", default="django.db.backends.postgresql")

    if DB_ENGINE == "django.db.backends.postgresql":
        # PostgreSQL configuration with standard Django backend (shared-schema)
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",  # Standard Django backend
                "NAME": config("DB_NAME", default="projectmeats_dev"),
                "USER": config("DB_USER", default="postgres"),
                "PASSWORD": config("DB_PASSWORD", default="postgres"),
                "HOST": config("DB_HOST", default="localhost"),
                "PORT": config("DB_PORT", default="5432"),
                "CONN_MAX_AGE": 0,  # Close connections after each request in development
                "OPTIONS": {
                    "connect_timeout": 10,
                },
            }
        }
    else:
        # Log invalid DB_ENGINE value for debugging
        logger.error(
            f"Invalid DB_ENGINE value: '{DB_ENGINE}'. "
            f"Only 'django.db.backends.postgresql' is supported. "
            f"See Django database settings docs: https://docs.djangoproject.com/en/stable/ref/settings/#databases"
        )
        raise ValueError(
            f"Unsupported DB_ENGINE: '{DB_ENGINE}'. "
            f"Only 'django.db.backends.postgresql' is supported. "
            f"Ensure DB_ENGINE is set in GitHub Secrets (Settings → Environments → dev-backend) "
            f"or configure it in config/environments/development.env. "
            f"See Django docs: https://docs.djangoproject.com/en/stable/ref/settings/#databases"
        )

# ==============================================================================
# CODESPACES AUTO-CONFIGURATION
# ==============================================================================
# Codespaces environment - ensure standard PostgreSQL backend
if os.getenv('CODESPACES') == 'true':
    if 'default' in DATABASES:
        # Ensure standard PostgreSQL backend (no schema-based tenancy)
        if DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql':
            DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql'
            logger.info("Codespaces detected: Using django.db.backends.postgresql")

# Log which database backend is being used
logger.info(
    f"Development environment using database backend: {DATABASES['default']['ENGINE']}"
)

# CORS Settings for React development server
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://dev.meatscentral.com",
    "https://dev-backend.meatscentral.com",
    "https://uat.meatscentral.com",
    "https://uat-backend.meatscentral.com",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:3003",
    "http://127.0.0.1:3003",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # Temporarily enabled for debugging

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-tenant-id",
]
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# CSRF Settings - Required for cross-origin POST requests from frontend to backend admin
# When frontend and backend are on different domains/subdomains, Django's CSRF protection
# requires explicit configuration via CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://dev.meatscentral.com",
    "https://dev-backend.meatscentral.com",
    "https://uat.meatscentral.com",          
    "https://uat-backend.meatscentral.com",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:3003",
    "http://127.0.0.1:3003",
]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_ROOT = BASE_DIR / "media"

# Development-specific logging
# LOGGING["handlers"]["console"]["level"] = "DEBUG"
# LOGGING["loggers"]["django"]["level"] = "DEBUG"
# LOGGING["loggers"]["projectmeats"]["level"] = "DEBUG"

# Remove file handler in development to avoid directory issues
LOGGING["handlers"].pop("file", None)
LOGGING["loggers"]["django"]["handlers"] = ["console"]
LOGGING["loggers"]["projectmeats"]["handlers"] = ["console"]

# Django Extensions (for development)
if "django_extensions" in INSTALLED_APPS:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]

# Cache for development (dummy cache)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Disable secure cookies for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
