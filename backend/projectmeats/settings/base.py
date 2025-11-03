"""
Base settings for ProjectMeats.
Common configuration shared across all environments.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    # Note: django_tenants is available in requirements but not actively used
    # ProjectMeats uses custom shared-schema multi-tenancy instead of schema-based isolation
    # "django_tenants",  # Commented out - not using schema-based multi-tenancy
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
]

LOCAL_APPS = [
    "apps.core",
    "apps.accounts_receivables",
    "apps.suppliers",
    "apps.customers",
    "apps.contacts",
    "apps.purchase_orders",
    "apps.plants",
    "apps.carriers",
    "apps.bug_reports",
    "apps.ai_assistant",
    "apps.tenants",  # Multi-tenancy support
    "apps.products",  # Master product list
    "apps.sales_orders",  # Sales orders
    "apps.invoices",  # Customer invoices
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static files middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Multi-tenancy middleware - currently using shared-schema approach
    # For schema-based routing, replace with: django_tenants.middleware.TenantMainMiddleware
    # This will be configured in future PRs based on deployment needs
    "apps.tenants.middleware.TenantMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "projectmeats.urls"

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

# Django-Tenants Configuration
# Schema-based multi-tenancy settings
# Reference: https://django-tenants.readthedocs.io/
#
# NOTE: This is a DUAL multi-tenancy setup:
# 1. Schema-based (django-tenants): Client/Domain models for complete isolation
# 2. Shared-schema (legacy): Tenant/TenantUser models for simpler setups
#
# INSTALLED_APPS is kept for backward compatibility with shared-schema approach.
# SHARED_APPS/TENANT_APPS configure schema-based routing.
# Middleware routing (choosing TenantMiddleware vs TenantMainMiddleware) will be
# handled in future PRs based on deployment needs.

# Tenant and domain models for custom shared-schema multi-tenancy
# NOTE: ProjectMeats uses custom shared-schema multi-tenancy with the Tenant model
# rather than django-tenants' schema-based isolation.
# These settings are kept for reference but not used by django-tenants
TENANT_MODEL = "tenants.Tenant"
TENANT_DOMAIN_MODEL = "tenants.Domain"

# Common Django apps used in both shared and tenant schemas
# These are required for basic Django functionality
_DJANGO_CORE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
]

# Apps available in all schemas (shared across all tenants)
SHARED_APPS = [
    "django_tenants",  # Must be first
] + _DJANGO_CORE_APPS + [
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "drf_spectacular",
    "django_filters",
    "apps.core",
    "apps.tenants",  # Tenant management is shared
]

# Apps that will be created in each tenant schema
# Include Django core apps for tenant-specific data (users, permissions, etc.)
TENANT_APPS = _DJANGO_CORE_APPS + [
    "apps.accounts_receivables",
    "apps.suppliers",
    "apps.customers",
    "apps.contacts",
    "apps.purchase_orders",
    "apps.plants",
    "apps.carriers",
    "apps.bug_reports",
    "apps.ai_assistant",
    "apps.products",
    "apps.sales_orders",
    "apps.invoices",
]

# Database router for multi-tenancy
# NOTE: Using custom shared-schema multi-tenancy, not django-tenants schema-based routing
# DATABASE_ROUTERS = []  # No special routing needed for shared-schema approach
