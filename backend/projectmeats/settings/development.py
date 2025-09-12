"""
Development settings for ProjectMeats.
"""
import os
from decouple import config
import dj_database_url

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "SECRET_KEY", 
    default="django-insecure-dev-key-change-in-production-3k2j5h2k5j3h5k2j3h5k2j3"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "testserver",
    "0.0.0.0",
]

# Database Configuration
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=f"sqlite:///{BASE_DIR}/db.sqlite3")
    )
}

# CORS Settings for React development server
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

CORS_ALLOW_CREDENTIALS = True

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_ROOT = BASE_DIR / "media"

# Development-specific logging
LOGGING["handlers"]["console"]["level"] = "DEBUG"
LOGGING["loggers"]["django"]["level"] = "DEBUG"
LOGGING["loggers"]["projectmeats"]["level"] = "DEBUG"

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