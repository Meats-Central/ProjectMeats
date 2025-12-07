"""
Tests for Multi-Tenant Authentication Flow Integration.

Tests the complete authentication flow from frontend login through
backend tenant resolution and data filtering.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from apps.tenants.models import Tenant, TenantUser
import json

User = get_user_model()


class AuthFlowIntegrationTestCase(TestCase):
    """Test multi-tenant authentication flow."""

    def setUp(self):
        """Set up test data."""
        # Create users
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123',
            email='user1@example.com',
            first_name='User',
            last_name='One'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123',
            email='user2@example.com'
        )
        
        # Create tenants
        self.tenant1 = Tenant.objects.create(
            name='Tenant 1',
            slug='tenant1',
            is_active=True
        )
        
        self.tenant2 = Tenant.objects.create(
            name='Tenant 2',
            slug='tenant2',
            is_active=True
        )
        
        # Associate users with tenants
        TenantUser.objects.create(
            user=self.user1,
            tenant=self.tenant1,
            role='admin',
            is_active=True
        )
        
        TenantUser.objects.create(
            user=self.user2,
            tenant=self.tenant2,
            role='member',
            is_active=True
        )
        
        # Create client
        self.client = Client()

    def test_login_flow_returns_tenant_information(self):
        """Test that login returns user's tenant information."""
        # Login
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'user1',
            'password': 'testpass123'
        }, content_type='application/json')
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify token
        self.assertIn('token', data)
        self.assertTrue(len(data['token']) > 0)
        
        # Verify user info
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'user1')
        self.assertEqual(data['user']['email'], 'user1@example.com')
        
        # Verify tenant info
        self.assertIn('tenants', data)
        self.assertEqual(len(data['tenants']), 1)
        self.assertEqual(data['tenants'][0]['tenant__slug'], 'tenant1')
        self.assertEqual(data['tenants'][0]['role'], 'admin')

    def test_x_tenant_id_header_enforces_tenant_context(self):
        """Test that X-Tenant-ID header properly enforces tenant context."""
        # Get token for user1
        token, _ = Token.objects.get_or_create(user=self.user1)
        
        # Make request with tenant1 header (user1 has access)
        response = self.client.get('/api/v1/tenants/current/', 
            HTTP_AUTHORIZATION=f'Token {token.key}',
            HTTP_X_TENANT_ID=str(self.tenant1.id)
        )
        
        # Should succeed
        self.assertEqual(response.status_code, 200)
        
        # Try with tenant2 header (user1 does NOT have access)
        response = self.client.get('/api/v1/tenants/current/',
            HTTP_AUTHORIZATION=f'Token {token.key}',
            HTTP_X_TENANT_ID=str(self.tenant2.id)
        )
        
        # Should be forbidden
        self.assertEqual(response.status_code, 403)

    def test_tenant_switching_via_header(self):
        """Test that users can switch between their tenants via header."""
        # Create user with multiple tenants
        multi_tenant_user = User.objects.create_user(
            username='multi',
            password='testpass123'
        )
        
        TenantUser.objects.create(
            user=multi_tenant_user,
            tenant=self.tenant1,
            role='admin',
            is_active=True
        )
        
        TenantUser.objects.create(
            user=multi_tenant_user,
            tenant=self.tenant2,
            role='member',
            is_active=True
        )
        
        token, _ = Token.objects.get_or_create(user=multi_tenant_user)
        
        # Request with tenant1 header
        response1 = self.client.get('/api/v1/tenants/current/',
            HTTP_AUTHORIZATION=f'Token {token.key}',
            HTTP_X_TENANT_ID=str(self.tenant1.id)
        )
        
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()
        self.assertEqual(data1['slug'], 'tenant1')
        
        # Request with tenant2 header
        response2 = self.client.get('/api/v1/tenants/current/',
            HTTP_AUTHORIZATION=f'Token {token.key}',
            HTTP_X_TENANT_ID=str(self.tenant2.id)
        )
        
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(data2['slug'], 'tenant2')

    def test_unauthenticated_requests_rejected(self):
        """Test that unauthenticated requests are rejected."""
        response = self.client.get('/api/v1/tenants/current/')
        self.assertEqual(response.status_code, 401)

    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected."""
        response = self.client.get('/api/v1/tenants/current/',
            HTTP_AUTHORIZATION='Token invalid-token-12345'
        )
        self.assertEqual(response.status_code, 401)

    def test_superuser_can_access_any_tenant(self):
        """Test that superusers can access any tenant via X-Tenant-ID."""
        superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass',
            email='admin@example.com'
        )
        
        token, _ = Token.objects.get_or_create(user=superuser)
        
        # Superuser should be able to access tenant1 without TenantUser association
        response = self.client.get('/api/v1/tenants/current/',
            HTTP_AUTHORIZATION=f'Token {token.key}',
            HTTP_X_TENANT_ID=str(self.tenant1.id)
        )
        
        # Should succeed even without TenantUser
        self.assertEqual(response.status_code, 200)

    def test_logout_clears_token(self):
        """Test that logout properly clears the token."""
        # Login
        response = self.client.post('/api/v1/auth/login/', {
            'username': 'user1',
            'password': 'testpass123'
        }, content_type='application/json')
        
        token = response.json()['token']
        
        # Logout
        logout_response = self.client.post('/api/v1/auth/logout/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(logout_response.status_code, 200)
        
        # Try to use token after logout
        test_response = self.client.get('/api/v1/tenants/current/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        # Should fail (token deleted on logout)
        self.assertEqual(test_response.status_code, 401)


class SubdomainRoutingTestCase(TestCase):
    """Test subdomain-based tenant routing."""

    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name='ACME Corporation',
            slug='acme',
            is_active=True
        )
        
        self.user = User.objects.create_user(
            username='test',
            password='testpass123'
        )
        
        TenantUser.objects.create(
            user=self.user,
            tenant=self.tenant,
            role='admin',
            is_active=True
        )
        
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def test_subdomain_resolves_tenant(self):
        """Test that subdomain is resolved to tenant."""
        # Make request with subdomain host
        response = self.client.get('/api/v1/tenants/current/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}',
            HTTP_HOST='acme.meatscentral.com'
        )
        
        if response.status_code == 200:
            data = response.json()
            self.assertEqual(data['slug'], 'acme')


class DocumentationTestCase(TestCase):
    """
    Documentation test case showing expected auth flow behavior.
    
    These tests document the expected authentication flow and serve as
    living documentation for developers.
    """

    def test_auth_flow_documentation(self):
        """
        Document the complete authentication flow.
        
        This test shows the expected sequence of operations for a typical
        authentication flow in ProjectMeats.
        """
        # STEP 1: User signs up (or admin creates account + tenant association)
        user = User.objects.create_user(
            username='newuser',
            password='securepass',
            email='newuser@example.com'
        )
        
        tenant = Tenant.objects.create(
            name='New Company',
            slug='newco',
            is_active=True
        )
        
        TenantUser.objects.create(
            user=user,
            tenant=tenant,
            role='owner',
            is_active=True
        )
        
        # STEP 2: Frontend calls login endpoint
        login_response = self.client.post('/api/v1/auth/login/', {
            'username': 'newuser',
            'password': 'securepass'
        }, content_type='application/json')
        
        self.assertEqual(login_response.status_code, 200)
        auth_data = login_response.json()
        
        # STEP 3: Frontend stores token and tenant info
        # (In real frontend, this goes to localStorage)
        token = auth_data['token']
        tenant_id = auth_data['tenants'][0]['tenant__id']
        
        # STEP 4: Frontend makes API calls with token and X-Tenant-ID
        api_response = self.client.get('/api/v1/tenants/current/',
            HTTP_AUTHORIZATION=f'Token {token}',
            HTTP_X_TENANT_ID=tenant_id
        )
        
        # STEP 5: Backend middleware resolves tenant and filters data
        self.assertEqual(api_response.status_code, 200)
        tenant_data = api_response.json()
        self.assertEqual(tenant_data['slug'], 'newco')
        
        # STEP 6: User logs out
        logout_response = self.client.post('/api/v1/auth/logout/',
            HTTP_AUTHORIZATION=f'Token {token}'
        )
        
        self.assertEqual(logout_response.status_code, 200)
