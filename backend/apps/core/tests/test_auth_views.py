"""
Tests for authentication views.
"""
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.tenants.models import Tenant, TenantUser


class SignupViewTest(TestCase):
    """Test cases for the signup endpoint."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.signup_url = "/api/v1/auth/signup/"

    def test_signup_success(self):
        """Test successful user signup."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "firstName": "Test",
            "lastName": "User",
        }

        response = self.client.post(self.signup_url, data, format="json")

        # Check response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)

        # Check user created
        user = User.objects.get(username="testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

        # Check tenant created
        tenant = Tenant.objects.filter(created_by=user).first()
        self.assertIsNotNone(tenant)
        self.assertTrue(tenant.slug.startswith("testuser-"))
        self.assertTrue(tenant.is_trial)

        # Check tenant user association
        tenant_user = TenantUser.objects.filter(
            user=user, tenant=tenant
        ).first()
        self.assertIsNotNone(tenant_user)
        self.assertEqual(tenant_user.role, "owner")
        self.assertTrue(tenant_user.is_active)

        # Check token created
        token = Token.objects.get(user=user)
        self.assertEqual(response.data["token"], token.key)

    def test_signup_missing_username(self):
        """Test signup with missing username."""
        data = {
            "email": "test@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("Username", response.data["error"])

    def test_signup_missing_email(self):
        """Test signup with missing email."""
        data = {
            "username": "testuser",
            "password": "testpass123",
        }

        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("Email", response.data["error"])

    def test_signup_missing_password(self):
        """Test signup with missing password."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
        }

        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("Password", response.data["error"])

    def test_signup_duplicate_username(self):
        """Test signup with existing username."""
        # Create existing user
        User.objects.create_user(
            username="testuser", email="existing@example.com", password="pass"
        )

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("already exists", response.data["error"])

    def test_signup_duplicate_email(self):
        """Test signup with existing email."""
        # Create existing user
        User.objects.create_user(
            username="existing", email="test@example.com", password="pass"
        )

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.signup_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertIn("already exists", response.data["error"])

    def test_signup_without_optional_fields(self):
        """Test signup without first/last name."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }

        response = self.client.post(self.signup_url, data, format="json")

        # Should still succeed
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check user created with empty names
        user = User.objects.get(username="testuser")
        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")


class LoginViewTest(TestCase):
    """Test cases for the login endpoint."""

    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.login_url = "/api/v1/auth/login/"

        # Create test user with tenant
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant",
            contact_email="test@example.com",
        )

        TenantUser.objects.create(
            tenant=self.tenant,
            user=self.user,
            role="owner",
            is_active=True,
        )

    def test_login_success(self):
        """Test successful login."""
        data = {
            "username": "testuser",
            "password": "testpass123",
        }

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)
        self.assertIn("tenants", response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            "username": "testuser",
            "password": "wrongpassword",
        }

        response = self.client.post(self.login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("error", response.data)


class LogoutViewTest(TestCase):
    """Test cases for the logout endpoint."""

    def setUp(self):
        """Set up test client and authenticated user."""
        self.client = APIClient()
        self.logout_url = "/api/v1/auth/logout/"

        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Create token
        self.token = Token.objects.create(user=self.user)

    def test_logout_success(self):
        """Test successful logout."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check token deleted
        self.assertFalse(
            Token.objects.filter(user=self.user).exists()
        )
