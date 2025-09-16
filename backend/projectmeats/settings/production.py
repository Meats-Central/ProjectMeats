"""
Production settings for ProjectMeats.
Optimized for Digital Ocean App Platform deployment.
"""

import os
from decouple import config
import dj_database_url

from .base import *

# Security Settings
SECRET_KEY = config("SECRET_KEY", default="temp-key-for-build-phase-only-not-secure")
DEBUG = True

# ALLOWED_HOSTS Configuration for Digital Ocean App Platform
# Use wildcard for now to allow internal IPs (like 10.244.32.208) for health checks
# For better security, set ALLOWED_HOSTS env var in DO to include meatscentral.com, .meatscentral.com
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# Database Configuration - PostgreSQL via Digital Ocean managed database
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=f"sqlite:///{BASE_DIR}/build_temp.db"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in config("CORS_ALLOWED_ORIGINS", default="").split(",")
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_SSL_REDIRECT = True

X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Security
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_USE_SESSIONS = True

# Email Configuration (configure as needed)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# Static files configuration with WhiteNoise
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# WhiteNoise Configuration
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp", "zip", "gz", "tgz", "bz2", "tbz", "xz", "br"]

# Media files (consider using object storage like AWS S3 or Digital Ocean Spaces)
MEDIA_ROOT = BASE_DIR / "media"

# Production Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "projectmeats": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Cache Configuration (Redis recommended for production)
redis_url = config("REDIS_URL", default=None)
if redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": redis_url,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# Performance Optimizations
CONN_MAX_AGE = 60

# Admin Security
ADMIN_URL = config("ADMIN_URL", default="admin/")

# Rate Limiting (if using django-ratelimit)
RATELIMIT_ENABLE = True

# Health Check Endpoint
HEALTH_CHECK = {
    "DISK_USAGE_MAX": 90,  # percent
    "MEMORY_MIN": 100,     # MB
}