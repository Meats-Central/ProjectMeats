"""
Staging settings for ProjectMeats.
Used for pre-production testing and validation.
"""

from .production import *

# Override production settings for staging
DEBUG = config("DEBUG", default=False, cast=bool)

# Staging-specific allowed hosts - read from environment
env_allowed_hosts = config("ALLOWED_HOSTS", default="localhost,127.0.0.1")
ALLOWED_HOSTS = [host.strip() for host in env_allowed_hosts.split(",") if host.strip()]

# Add default staging hosts if not already included
STAGING_HOSTS = [
    "staging.meatscentral.com",  # Primary staging domain
    "uat.meatscentral.com",  # UAT environment
    "staging-projectmeats.ondigitalocean.app",
    "projectmeats-staging.herokuapp.com",  # Fallback
]

# Merge with environment hosts, avoiding duplicates
for host in STAGING_HOSTS:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# Less restrictive CORS for staging testing
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=False, cast=bool)

# Email backend for staging (console or file)
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend"
)

# Staging-specific cache (can be less robust)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "staging-cache",
    }
}

# Allow less secure cookies for staging testing
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)

# Staging health checks (more lenient)
HEALTH_CHECK = {
    "DISK_USAGE_MAX": 95,  # percent
    "MEMORY_MIN": 50,  # MB
}

STATIC_URL = "/static/"
MEDIA_URL = "/media/"
