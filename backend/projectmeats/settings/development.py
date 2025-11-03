"""
Development settings for ProjectMeats.
"""
import os
import logging
from decouple import config
import dj_database_url

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

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "testserver",
    "0.0.0.0",
    "dev.meatscentral.com",
    "dev-backend.meatscentral.com",
    "157.245.114.182",
]


# Database Configuration
# Development now uses PostgreSQL for environment parity with staging/production
# Falls back to SQLite if PostgreSQL environment variables are not configured
# Get DB_ENGINE with fallback for empty values
# Using config() to read from .env file for local development
# The .strip() or pattern handles empty strings from GitHub Secrets
DB_ENGINE = config("DB_ENGINE", default="").strip() or "django.db.backends.sqlite3"

if DB_ENGINE == "django.db.backends.postgresql":
    # PostgreSQL configuration - requires all environment variables
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": config("DB_NAME"),
            "USER": config("DB_USER"),
            "PASSWORD": config("DB_PASSWORD"),
            "HOST": config("DB_HOST"),
            "PORT": config("DB_PORT", default="5432"),
            "CONN_MAX_AGE": 0,  # Close connections after each request in development
            "OPTIONS": {
                "connect_timeout": 10,
            },
        }
    }
elif DB_ENGINE == "django.db.backends.sqlite3":
    # SQLite fallback - DEPRECATED: Use PostgreSQL for environment parity
    # This is maintained for backward compatibility during migration period
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # Log invalid DB_ENGINE value for debugging
    logger.error(
        f"Invalid DB_ENGINE value: '{DB_ENGINE}'. "
        f"Supported values are 'django.db.backends.postgresql' or 'django.db.backends.sqlite3'. "
        f"See Django database settings docs: https://docs.djangoproject.com/en/stable/ref/settings/#databases"
    )
    raise ValueError(
        f"Unsupported DB_ENGINE: '{DB_ENGINE}'. "
        f"Supported values are 'django.db.backends.postgresql' or 'django.db.backends.sqlite3'. "
        f"Ensure DB_ENGINE is set in GitHub Secrets (Settings → Environments → dev-backend) "
        f"or configure it in config/environments/development.env. "
        f"See Django docs: https://docs.djangoproject.com/en/stable/ref/settings/#databases"
    )

# Log which database backend is being used
logger.info(f"Development environment using database backend: {DB_ENGINE}")

# CORS Settings for React development server
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://dev.meatscentral.com",
    "https://dev-backend.meatscentral.com",
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
