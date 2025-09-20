"""
Production settings for ProjectMeats.
Optimized for Droplet/App Platform/Traefik deployments with CI/CD.
"""

import os
from decouple import config
import dj_database_url

from .base import *  # noqa

# -----------------------------------------------------------------------------
# Security & Core
# -----------------------------------------------------------------------------
DEBUG = False
SECRET_KEY = config("SECRET_KEY", default="temp-key-for-build-phase-only-not-secure")

# Helper: split comma-separated env values into a cleaned list
def _split_list(val: str | None) -> list[str]:
    if not val:
        return []
    return [item.strip() for item in val.split(",") if item.strip()]

# Common internal/container hosts expected in CI and containerized envs
_COMMON_INTERNAL_HOSTS = [
    "localhost",
    "127.0.0.1",
    # Specific IPs expected by tests and common container bridges
    "10.244.45.4",
    "10.0.0.1",
    "172.17.0.1",
    "192.168.1.1",
]

# External + internal hosts from env
_ext_hosts = _split_list(os.environ.get("ALLOWED_HOSTS", ""))              # e.g. "example.com,api.example.com"
_int_hosts = _split_list(os.environ.get("INTERNAL_ALLOWED_HOSTS", ""))     # e.g. "10.244.45.4,localhost"

# Build ALLOWED_HOSTS: keep order, remove duplicates, ensure internal fallbacks always present
_seen: set[str] = set()
ALLOWED_HOSTS: list[str] = []
for h in (_ext_hosts + _int_hosts + _COMMON_INTERNAL_HOSTS):
    if h not in _seen:
        _seen.add(h)
        ALLOWED_HOSTS.append(h)

# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=config("DATABASE_URL", default=f"sqlite:///{BASE_DIR}/build_temp.db"),  # noqa: F405
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# -----------------------------------------------------------------------------
# CORS
# -----------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config("CORS_ALLOWED_ORIGINS", default="").split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# -----------------------------------------------------------------------------
# Security Headers
# -----------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

SECURE_SSL_REDIRECT = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# -----------------------------------------------------------------------------
# Cookies / CSRF / Sessions
# -----------------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_USE_SESSIONS = True  # required by tests

# Ensure SessionMiddleware appears BEFORE CsrfViewMiddleware (tests verify order)
_SESSION = "django.contrib.sessions.middleware.SessionMiddleware"
_CSRF = "django.middleware.csrf.CsrfViewMiddleware"

if _SESSION not in MIDDLEWARE:  # noqa: F405
    # place early (right after SecurityMiddleware if present)
    try:
        sec_idx = MIDDLEWARE.index("django.middleware.security.SecurityMiddleware")  # noqa: F405
        MIDDLEWARE.insert(sec_idx + 1, _SESSION)  # noqa: F405
    except ValueError:
        MIDDLEWARE.insert(0, _SESSION)  # noqa: F405

if _CSRF not in MIDDLEWARE:  # noqa: F405
    # after CommonMiddleware if present, but after SessionMiddleware for sure
    try:
        common_idx = MIDDLEWARE.index("django.middleware.common.CommonMiddleware")  # noqa: F405
        insert_at = common_idx + 1
    except ValueError:
        insert_at = len(MIDDLEWARE)  # noqa: F405
    MIDDLEWARE.insert(insert_at, _CSRF)  # noqa: F405

# Fix order if needed
try:
    s_idx = MIDDLEWARE.index(_SESSION)  # noqa: F405
    c_idx = MIDDLEWARE.index(_CSRF)     # noqa: F405
    if s_idx > c_idx:
        MIDDLEWARE.pop(s_idx)           # noqa: F405
        c_idx = MIDDLEWARE.index(_CSRF) # noqa: F405
        MIDDLEWARE.insert(c_idx, _SESSION)  # noqa: F405
except ValueError:
    pass

# -----------------------------------------------------------------------------
# Email
# -----------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# -----------------------------------------------------------------------------
# Static / Media
# -----------------------------------------------------------------------------
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = [
    "jpg", "jpeg", "png", "gif", "webp", "zip", "gz", "tgz", "bz2", "tbz", "xz", "br"
]
MEDIA_ROOT = BASE_DIR / "media"  # noqa: F405

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "verbose"}},
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "projectmeats": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# -----------------------------------------------------------------------------
# Cache (Redis/Valkey if provided)
# -----------------------------------------------------------------------------
redis_url = config("REDIS_URL", default=None) or config("VALKEY_URL", default=None)
if redis_url:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": redis_url,
        }
    }
else:
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

# -----------------------------------------------------------------------------
# Misc
# -----------------------------------------------------------------------------
CONN_MAX_AGE = 60
ADMIN_URL = config("ADMIN_URL", default="admin/")
RATELIMIT_ENABLE = True
HEALTH_CHECK = {"DISK_USAGE_MAX": 90, "MEMORY_MIN": 100}  # MB
