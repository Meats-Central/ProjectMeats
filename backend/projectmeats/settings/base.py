"""
Base settings for ProjectMeats.
Common configuration shared across all environments.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ==============================================================================
# SHARED SCHEMA CONFIGURATION (django-tenants DISABLED for routing)
# ==============================================================================
# We use a custom TenantMiddleware (apps.tenants.middleware.TenantMiddleware)
# for tenant resolution based on domain/subdomain/headers, but ALL apps run
# in a shared PostgreSQL schema. This avoids the "Public vs Tenant World" split
# that causes 404s on business endpoints.

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
    # NOTE: django_tenants is kept for model definitions (Tenant, TenantDomain)
    # but its middleware is DISABLED to prevent schema-based routing
    "django_tenants",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
]

# ProjectMeats apps (all in shared schema)
_PROJECT_APPS = [
    "apps.core",
    "apps.tenants",  # Tenant management
    # Business apps (previously in TENANT_APPS, now in shared schema)
    "tenant_apps.accounts_receivables",
    "tenant_apps.suppliers",
    "tenant_apps.customers",
    "tenant_apps.contacts",
    "tenant_apps.purchase_orders",
    "tenant_apps.plants",
    "tenant_apps.carriers",
    "tenant_apps.bug_reports",
    "tenant_apps.ai_assistant",
    "tenant_apps.products",
    "tenant_apps.sales_orders",
    "tenant_apps.invoices",
    "tenant_apps.cockpit",
]

# All apps in one shared schema (no SHARED_APPS/TENANT_APPS split)
INSTALLED_APPS = (
    _THIRD_PARTY_APPS[:1]  # django_tenants must be first if present
    + _DJANGO_CORE_APPS
    + ["django.contrib.staticfiles"]
    + _THIRD_PARTY_APPS[1:]  # Rest of third-party apps
    + _PROJECT_APPS
)

# Legacy django-tenants configuration (kept for reference, NOT USED for routing)
# These are preserved to avoid migration issues but are not actively used

# ==============================================================================
# DJANGO-TENANTS REQUIRED SETTINGS
# ==============================================================================
SHARED_APPS = [
    "django_tenants",
] + _DJANGO_CORE_APPS + [
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "apps.core",
    "apps.tenants",
]

TENANT_APPS = _DJANGO_CORE_APPS + [
    "tenant_apps.accounts_receivables",
    "tenant_apps.suppliers",
    "tenant_apps.customers",
    "tenant_apps.contacts",
    "tenant_apps.purchase_orders",
    "tenant_apps.plants",
    "tenant_apps.carriers",
    "tenant_apps.bug_reports",
    "tenant_apps.ai_assistant",
    "tenant_apps.products",
    "tenant_apps.sales_orders",
    "tenant_apps.invoices",
    "tenant_apps.cockpit",
]



MIDDLEWARE = [MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # Must be first for CORS headers
    # CRITICAL: Custom TenantMiddleware (NOT django_tenants.middleware.main.TenantMainMiddleware)
    "apps.tenants.middleware.TenantMiddleware",  # Sets request.tenant without schema routing
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static files middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "projectmeats.urls"

# NOTE: PUBLIC_SCHEMA_URLCONF is NOT used when TenantMainMiddleware is disabled
# All requests use ROOT_URLCONF regardless of tenant

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
        "rest_framework.authentication.SessionAuthentication",
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
        "apps.suppliers.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.customers.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.contacts.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.purchase_orders.views": {
            "handlers": ["console", "debug_file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "apps.accounts_receivables.views": {
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

# Django-tenants configuration for schema-based multi-tenancy
TENANT_MODEL = "tenants.Client"
TENANT_DOMAIN_MODEL = "tenants.Domain"

# Database router for schema-based multi-tenancy
DATABASE_ROUTERS = ["django_tenants.routers.TenantSyncRouter"]
