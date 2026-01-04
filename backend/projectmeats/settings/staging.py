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
# Default includes wildcards for UAT subdomain and all meatscentral.com subdomains
env_allowed_hosts = config("ALLOWED_HOSTS", default="localhost,127.0.0.1,.uat.meatscentral.com,.meatscentral.com")
ALLOWED_HOSTS = [host.strip() for host in env_allowed_hosts.split(",") if host.strip()]

# Always include localhost for Docker health checks
if "localhost" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("localhost")
if "127.0.0.1" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("127.0.0.1")

# Ensure wildcard patterns are included for UAT
WILDCARD_HOSTS = [
    ".uat.meatscentral.com",  # Wildcard for *.uat.meatscentral.com
    ".meatscentral.com",  # Wildcard for *.meatscentral.com
]
for wildcard in WILDCARD_HOSTS:
    if wildcard not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(wildcard)

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

# Email backend for staging (SendGrid SMTP Relay)
# IMPORTANT: EMAIL_HOST_PASSWORD must be set as environment variable or GitHub secret
# Do not hardcode API keys in source code
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.sendgrid.net")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="apikey")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@meatscentral.com")
SERVER_EMAIL = config("SERVER_EMAIL", default="noreply@meatscentral.com")

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
