"""
Tests for Suppliers API endpoints.

Validates supplier creation, validation, and error handling.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.suppliers.models import Supplier
from apps.tenants.models import Tenant, TenantUser


class SupplierAPITests(APITestCase):
    """Test cases for Supplier API endpoints."""

    def setUp(self):
        """Set up test data."""
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

    def test_create_supplier_success(self):
        """Test creating a supplier with valid data."""
        url = reverse("suppliers:supplier-list")
        data = {
            "name": "Test Supplier",
            "email": "supplier@example.com",
            "phone": "123-456-7890",
        }

        # Set tenant header
        response = self.client.post(url, data, HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 1)
        supplier = Supplier.objects.first()
        self.assertEqual(supplier.name, "Test Supplier")
        self.assertEqual(supplier.tenant, self.tenant)

    def test_create_supplier_without_name(self):
        """Test that creating a supplier without a name fails."""
        url = reverse("suppliers:supplier-list")
        data = {
            "email": "supplier@example.com",
            "phone": "123-456-7890",
        }

        response = self.client.post(url, data, HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Supplier.objects.count(), 0)

    def test_create_supplier_with_empty_name(self):
        """Test that creating a supplier with empty name fails."""
        url = reverse("suppliers:supplier-list")
        data = {
            "name": "",
            "email": "supplier@example.com",
        }

        response = self.client.post(url, data, HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Supplier.objects.count(), 0)

    def test_create_supplier_with_invalid_email(self):
        """Test that creating a supplier with invalid email fails."""
        url = reverse("suppliers:supplier-list")
        data = {
            "name": "Test Supplier",
            "email": "invalid-email",
        }

        response = self.client.post(url, data, HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Supplier.objects.count(), 0)

    def test_create_supplier_without_tenant(self):
        """Test that creating a supplier without tenant context fails."""
        url = reverse("suppliers:supplier-list")
        data = {
            "name": "Test Supplier",
        }

        # Don't send tenant header
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_list_suppliers_filtered_by_tenant(self):
        """Test that suppliers are filtered by tenant."""
        # Create supplier for this tenant
        Supplier.objects.create(name="Supplier 1", tenant=self.tenant)

        # Create another tenant and supplier
        other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="testpass123"
        )
        other_tenant = Tenant.objects.create(
            name="Other Company",
            slug="other-company",
            contact_email="admin@othercompany.com",
            created_by=other_user,
        )
        Supplier.objects.create(name="Supplier 2", tenant=other_tenant)

        url = reverse("suppliers:supplier-list")
        response = self.client.get(url, HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Supplier 1")
