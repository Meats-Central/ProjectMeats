"""
Base settings for ProjectMeats.
Common configuration shared across all environments.

Multi-Tenancy Architecture: SHARED SCHEMA ONLY
==============================================
ProjectMeats uses a shared-schema multi-tenancy approach:
- All tenants share the same PostgreSQL schema
- Tenant isolation is enforced via `tenant_id` foreign keys
- Custom TenantMiddleware resolves tenant from domain/subdomain/header
- NO django-tenants schema-based isolation
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==============================================================================
# SHARED SCHEMA MULTI-TENANCY CONFIGURATION
# ==============================================================================
# We use a custom TenantMiddleware (apps.tenants.middleware.TenantMiddleware)
# for tenant resolution based on domain/subdomain/headers. ALL apps run
# in a shared PostgreSQL schema with tenant_id foreign keys for isolation.

# Row-level security flag for auditing and future PostgreSQL RLS implementation
ROW_LEVEL_SECURITY = True

# Common Django apps used across the application
_DJANGO_CORE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
]

# Third-party apps
_THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
]

# ProjectMeats apps (all in shared schema with tenant_id isolation)
_PROJECT_APPS = [
    "apps.core",
    "apps.tenants",  # Tenant management (shared-schema approach)
    # Business apps (all use tenant_id for data isolation)
    "tenant_apps.accounts_receivables",
    "tenant_apps.ai_assistant",
    "tenant_apps.bug_reports",
    "tenant_apps.carriers",
    "tenant_apps.cockpit",
    "tenant_apps.contacts",
    "tenant_apps.customers",
    "tenant_apps.invoices",
    "tenant_apps.plants",
    "tenant_apps.products",
    "tenant_apps.purchase_orders",
    "tenant_apps.sales_orders",
    "tenant_apps.suppliers",
]

# All apps in one shared schema
INSTALLED_APPS = (
    _DJANGO_CORE_APPS
    + ["django.contrib.staticfiles"]
    + _THIRD_PARTY_APPS
    + _PROJECT_APPS
)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be first for CORS headers
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static files middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.tenants.middleware.TenantMiddleware",  # Must be after AuthenticationMiddleware to access request.user
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "projectmeats.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "projectmeats.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# URL Configuration
APPEND_SLASH = True  # Ensure trailing slash handling for API endpoints

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = Path(os.environ.get("STATIC_ROOT", BASE_DIR / "staticfiles"))
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))

# Static files storage - WhiteNoise for production
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FileUploadParser",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.core.exceptions.exception_handler",
}

# API Documentation
SPECTACULAR_SETTINGS = {
    "TITLE": "ProjectMeats API",
    "DESCRIPTION": "REST API for meat sales broker management system",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
}

# Ensure logs directory exists for file handlers
# Reference: https://docs.python.org/3/library/logging.html#logging.FileHandler
# This ensures the logs directory is created before Django configures logging,
# preventing FileNotFoundError in CI/CD environments and local development.
os.makedirs(BASE_DIR / "logs", exist_ok=True)

# Logging Configuration
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
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "verbose",
        },
        "debug_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "debug.log",
            "formatter": "verbose",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "projectmeats": {
            "handlers": ["console", "file", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "tenant_apps.suppliers.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "tenant_apps.customers.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "tenant_apps.contacts.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "tenant_apps.purchase_orders.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "tenant_apps.accounts_receivables.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.core.exceptions": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email Configuration (SendGrid)
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.sendgrid.net')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'apikey')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'no-reply@meatscentral.com'
SERVER_EMAIL = 'no-reply@meatscentral.com'
