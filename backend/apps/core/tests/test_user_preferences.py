"""
Tests for user preferences API.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.core.models import UserPreferences


class UserPreferencesAPITestCase(TestCase):
    """Test user preferences API endpoints."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_preferences_creates_if_not_exists(self):
        """Test that getting preferences creates them if they don't exist."""
        # Ensure no preferences exist yet
        self.assertFalse(
            UserPreferences.objects.filter(user=self.user).exists()
        )
        
        # Get preferences (should create them)
        response = self.client.get('/api/v1/preferences/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'light')
        self.assertEqual(response.data['sidebar_open'], True)
        self.assertEqual(response.data['dashboard_layout'], {})
        
        # Verify preferences were created
        self.assertTrue(
            UserPreferences.objects.filter(user=self.user).exists()
        )

    def test_update_theme(self):
        """Test updating theme preference."""
        response = self.client.patch(
            '/api/v1/preferences/update_theme/',
            {'theme': 'dark'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'dark')
        
        # Verify in database
        preferences = UserPreferences.objects.get(user=self.user)
        self.assertEqual(preferences.theme, 'dark')

    def test_update_theme_invalid(self):
        """Test updating theme with invalid value."""
        response = self.client.patch(
            '/api/v1/preferences/update_theme/',
            {'theme': 'invalid'},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_sidebar(self):
        """Test updating sidebar preference."""
        response = self.client.patch(
            '/api/v1/preferences/update_sidebar/',
            {'sidebar_open': False},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sidebar_open'], False)
        
        # Verify in database
        preferences = UserPreferences.objects.get(user=self.user)
        self.assertFalse(preferences.sidebar_open)

    def test_update_dashboard_layout(self):
        """Test updating dashboard layout."""
        layout = {
            'widgets': ['chart1', 'chart2', 'metrics1'],
            'grid': {'cols': 3, 'rows': 2}
        }
        
        response = self.client.patch(
            '/api/v1/preferences/update_dashboard_layout/',
            {'dashboard_layout': layout},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['dashboard_layout'], layout)
        
        # Verify in database
        preferences = UserPreferences.objects.get(user=self.user)
        self.assertEqual(preferences.dashboard_layout, layout)

    def test_preferences_require_authentication(self):
        """Test that preferences endpoints require authentication."""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/v1/preferences/me/')
        # DRF returns 403 (Forbidden) when not authenticated with certain permission classes
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_user_can_only_access_own_preferences(self):
        """Test that users can only access their own preferences."""
        # Create another user with preferences
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        UserPreferences.objects.create(
            user=other_user,
            theme='dark',
            sidebar_open=False
        )
        
        # Get preferences as first user
        response = self.client.get('/api/v1/preferences/me/')
        
        # Should get own preferences (default light theme), not other user's dark theme
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'light')
