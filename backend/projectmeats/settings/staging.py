"""
Staging settings for ProjectMeats.
Used for pre-production testing and validation.

IMPORTANT: This configuration file is maintained for UAT environment (uat.meatscentral.com).
The domain staging.meatscentral.com is DEPRECATED. UAT is the active middle environment
per the pipeline configuration. Please use uat.meatscentral.com for all staging/UAT operations.
"""

import logging
from decouple import config
from .production import *

# Log deprecation warning if old staging domain is detected
logger = logging.getLogger(__name__)

# Override production settings for staging
DEBUG = config("DEBUG", default=False, cast=bool)

# Staging-specific allowed hosts - read from environment
env_allowed_hosts = config("ALLOWED_HOSTS", default="localhost,127.0.0.1")
ALLOWED_HOSTS = [host.strip() for host in env_allowed_hosts.split(",") if host.strip()]

# Always include localhost for Docker health checks
if "localhost" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("localhost")
if "127.0.0.1" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("127.0.0.1")

# Add UAT hosts (primary) and legacy staging hosts (deprecated)
STAGING_HOSTS = [
    "uat.meatscentral.com",  # PRIMARY - Use this for UAT/staging
    "staging-projectmeats.ondigitalocean.app",
    "projectmeats-staging.herokuapp.com",  # Fallback
]

# Check for deprecated staging domain and log warning
if any("staging.meatscentral.com" in host for host in ALLOWED_HOSTS):
    logger.warning(
        "DEPRECATION WARNING: staging.meatscentral.com is deprecated. "
        "Please use uat.meatscentral.com as the primary middle environment. "
        "UAT is the active staging environment per pipeline configuration."
    )

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
