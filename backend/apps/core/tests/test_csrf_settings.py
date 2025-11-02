"""
Tests for CSRF configuration in Django settings.

These tests verify that CSRF_TRUSTED_ORIGINS is properly configured
to allow cross-origin requests from frontend domains.
"""

from django.test import TestCase
from django.conf import settings
import os


class CSRFSettingsTestCase(TestCase):
    """Test CSRF configuration in Django settings."""

    def test_csrf_trusted_origins_exists(self):
        """Test that CSRF_TRUSTED_ORIGINS is defined in settings."""
        self.assertTrue(
            hasattr(settings, 'CSRF_TRUSTED_ORIGINS'),
            "CSRF_TRUSTED_ORIGINS should be defined in settings"
        )

    def test_csrf_trusted_origins_is_list(self):
        """Test that CSRF_TRUSTED_ORIGINS is a list."""
        self.assertIsInstance(
            settings.CSRF_TRUSTED_ORIGINS,
            list,
            "CSRF_TRUSTED_ORIGINS should be a list"
        )

    def test_csrf_trusted_origins_development(self):
        """Test CSRF_TRUSTED_ORIGINS in development environment."""
        # This test only applies to development settings
        if 'development' in os.environ.get('DJANGO_SETTINGS_MODULE', ''):
            expected_origins = [
                'http://localhost:3000',
                'http://127.0.0.1:3000',
                'https://dev.meatscentral.com',
                'https://dev-backend.meatscentral.com',
            ]
            
            for origin in expected_origins:
                self.assertIn(
                    origin,
                    settings.CSRF_TRUSTED_ORIGINS,
                    f"{origin} should be in CSRF_TRUSTED_ORIGINS for development"
                )

    def test_csrf_middleware_enabled(self):
        """Test that CSRF middleware is enabled."""
        self.assertIn(
            'django.middleware.csrf.CsrfViewMiddleware',
            settings.MIDDLEWARE,
            "CsrfViewMiddleware should be in MIDDLEWARE"
        )
