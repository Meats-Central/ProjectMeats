from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Tenant, TenantUser
import uuid


class TenantModelTests(TestCase):
    """Test cases for Tenant model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_tenant_creation(self):
        """Test basic tenant creation."""
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            created_by=self.user,
        )

        self.assertEqual(tenant.name, "Test Company")
        self.assertEqual(tenant.slug, "test-company")
        self.assertEqual(tenant.contact_email, "admin@testcompany.com")
        self.assertTrue(tenant.is_active)
        self.assertTrue(tenant.is_trial)
        self.assertIsInstance(tenant.id, uuid.UUID)

    def test_slug_lowercase_conversion(self):
        """Test that slug is automatically converted to lowercase."""
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="Test-COMPANY",
            contact_email="admin@testcompany.com",
            created_by=self.user,
        )

        self.assertEqual(tenant.slug, "test-company")

    def test_tenant_str_method(self):
        """Test string representation of tenant."""
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            created_by=self.user,
        )

        self.assertEqual(str(tenant), "Test Company (test-company)")


class TenantUserModelTests(TestCase):
    """Test cases for TenantUser model."""

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="testpass123"
        )
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            created_by=self.user1,
        )

    def test_tenant_user_creation(self):
        """Test creating tenant-user association."""
        tenant_user = TenantUser.objects.create(
            tenant=self.tenant, user=self.user1, role="owner"
        )

        self.assertEqual(tenant_user.tenant, self.tenant)
        self.assertEqual(tenant_user.user, self.user1)
        self.assertEqual(tenant_user.role, "owner")
        self.assertTrue(tenant_user.is_active)

    def test_tenant_user_unique_constraint(self):
        """Test that user cannot be associated with same tenant twice."""
        TenantUser.objects.create(tenant=self.tenant, user=self.user1, role="owner")

        # This should not raise an error but let's check uniqueness
        with self.assertRaises(Exception):
            TenantUser.objects.create(tenant=self.tenant, user=self.user1, role="admin")

    def test_tenant_user_str_method(self):
        """Test string representation of tenant user."""
        tenant_user = TenantUser.objects.create(
            tenant=self.tenant, user=self.user1, role="owner"
        )

        expected_str = f"{self.user1.username} @ {self.tenant.slug} (owner)"
        self.assertEqual(str(tenant_user), expected_str)


class TenantAPITests(APITestCase):
    """Test cases for Tenant API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            created_by=self.user,
        )

        # Associate user with tenant
        TenantUser.objects.create(tenant=self.tenant, user=self.user, role="owner")

    def test_list_tenants(self):
        """Test listing tenants for authenticated user."""
        url = reverse("tenants:tenant-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Company")

    def test_create_tenant(self):
        """Test creating a new tenant."""
        url = reverse("tenants:tenant-list")
        data = {
            "name": "New Company",
            "slug": "new-company",
            "contact_email": "admin@newcompany.com",
            "is_trial": True,
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tenant.objects.count(), 2)
        new_tenant = Tenant.objects.get(slug="new-company")
        self.assertEqual(new_tenant.name, "New Company")
        self.assertEqual(new_tenant.created_by, self.user)

    def test_my_tenants_endpoint(self):
        """Test getting current user's tenants."""
        url = reverse("tenants:tenant-my-tenants")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["tenant_name"], "Test Company")
        self.assertEqual(response.data[0]["role"], "owner")

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access tenant endpoints."""
        self.client.force_authenticate(user=None)

        url = reverse("tenants:tenant-list")
        response = self.client.get(url)

        # DRF returns 403 for unauthenticated users when authentication is required
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
