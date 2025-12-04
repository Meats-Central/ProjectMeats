"""
Tests for UserPreferences model and API.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from unittest import skip
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from apps.core.models import UserPreferences


class UserPreferencesModelTest(TestCase):
    """Tests for UserPreferences model."""
    
    def setUp(self):
        """Set up test user."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_preferences(self):
        """Test creating user preferences."""
        preferences = UserPreferences.objects.create(
            user=self.user,
            theme='dark',
            sidebar_collapsed=True
        )
        self.assertEqual(preferences.user, self.user)
        self.assertEqual(preferences.theme, 'dark')
        self.assertTrue(preferences.sidebar_collapsed)
    
    def test_default_values(self):
        """Test default values for user preferences."""
        preferences = UserPreferences.objects.create(user=self.user)
        self.assertEqual(preferences.theme, 'light')
        self.assertFalse(preferences.sidebar_collapsed)
        self.assertEqual(preferences.dashboard_layout, {})
        self.assertEqual(preferences.quick_menu_items, [])
        self.assertEqual(preferences.widget_preferences, {})
    
    def test_json_field_storage(self):
        """Test JSON field storage."""
        preferences = UserPreferences.objects.create(
            user=self.user,
            dashboard_layout={'widgets': ['sales', 'inventory']},
            quick_menu_items=['/suppliers', '/customers'],
            widget_preferences={'sales': {'collapsed': False}}
        )
        self.assertEqual(len(preferences.dashboard_layout['widgets']), 2)
        self.assertEqual(len(preferences.quick_menu_items), 2)
        self.assertIn('sales', preferences.widget_preferences)
    
    def test_str_representation(self):
        """Test string representation."""
        preferences = UserPreferences.objects.create(user=self.user)
        self.assertEqual(str(preferences), f"Preferences for {self.user.username}")


@skip("Requires complex django-tenants test setup - UserPreferences is a shared model")
class UserPreferencesAPITest(APITestCase):
    """Tests for UserPreferences API endpoints."""
    
    def setUp(self):
        """Set up test users, authentication, and test tenant."""
        # Import here to avoid circular imports
        from apps.tenants.models import Client, Domain
        from django_tenants.utils import schema_context, get_public_schema_name
        
        # Create test tenant (Client) in the public schema
        with schema_context(get_public_schema_name()):
            self.tenant = Client.objects.create(
                schema_name='test',
                name='Test Tenant'
            )
            Domain.objects.create(
                domain='test.localhost',
                tenant=self.tenant,
                is_primary=True
            )
        
        # Create test users (in the current test schema)
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
    
    def _make_request(self, method, url, token, data=None):
        """Helper to make requests with tenant domain header."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}',
            HTTP_HOST='test.localhost'  # Required for django-tenants
        )
        if method == 'GET':
            return self.client.get(url)
        elif method == 'PATCH':
            return self.client.patch(url, data, format='json')
        elif method == 'PUT':
            return self.client.put(url, data, format='json')
    
    def test_get_or_create_preferences(self):
        """Test GET /api/v1/preferences/me/ creates preferences if not exists."""
        response = self._make_request('GET', '/api/v1/preferences/me/', self.token1)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user1.id)
        self.assertEqual(response.data['theme'], 'light')
        
        # Verify it was created in database
        self.assertTrue(
            UserPreferences.objects.filter(user=self.user1).exists()
        )
    
    def test_update_preferences_partial(self):
        """Test PATCH /api/v1/preferences/me/ updates preferences."""
        # First create preferences
        self._make_request('GET', '/api/v1/preferences/me/', self.token1)
        
        # Update theme only
        response = self._make_request(
            'PATCH',
            '/api/v1/preferences/me/',
            self.token1,
            {'theme': 'dark'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'dark')
        
        # Verify in database
        preferences = UserPreferences.objects.get(user=self.user1)
        self.assertEqual(preferences.theme, 'dark')
    
    def test_update_preferences_full(self):
        """Test PUT /api/v1/preferences/me/ updates all preferences."""
        data = {
            'theme': 'dark',
            'sidebar_collapsed': True,
            'dashboard_layout': {'widgets': ['sales']},
            'quick_menu_items': ['/suppliers'],
            'widget_preferences': {'sales': {'period': 'month'}}
        }
        
        response = self._make_request('PUT', '/api/v1/preferences/me/', self.token1, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['theme'], 'dark')
        self.assertTrue(response.data['sidebar_collapsed'])
        self.assertEqual(response.data['dashboard_layout'], {'widgets': ['sales']})
    
    def test_user_isolation(self):
        """Test users can only access their own preferences."""
        # User1 creates preferences
        response1 = self._make_request(
            'PATCH',
            '/api/v1/preferences/me/',
            self.token1,
            {'theme': 'dark'}
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data['theme'], 'dark')
        
        # User2 creates preferences
        response2 = self._make_request(
            'PATCH',
            '/api/v1/preferences/me/',
            self.token2,
            {'theme': 'light'}
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['theme'], 'light')
        
        # Verify users have different preferences
        pref1 = UserPreferences.objects.get(user=self.user1)
        pref2 = UserPreferences.objects.get(user=self.user2)
        self.assertEqual(pref1.theme, 'dark')
        self.assertEqual(pref2.theme, 'light')
    
    def test_unauthenticated_access_denied(self):
        """Test unauthenticated users cannot access preferences."""
        # Make request with tenant domain but no auth
        self.client.credentials(HTTP_HOST='test.localhost')
        response = self.client.get('/api/v1/preferences/me/')
        # DRF may return 401 or 403 depending on authentication configuration
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
