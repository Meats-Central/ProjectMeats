"""
Tests for Customers API endpoints.

Validates customer creation, validation, and error handling.
"""
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.customers.models import Customer
from apps.tenants.models import Tenant, TenantUser


class CustomerAPITests(APITestCase):
    """Test cases for Customer API endpoints."""

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

    def test_create_customer_success(self):
        """Test creating a customer with valid data."""
        url = reverse("customers:customer-list")
        data = {
            "name": "Test Customer",
            "email": "customer@example.com",
            "phone": "123-456-7890",
        }

        response = self.client.post(url, data, HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 1)
        customer = Customer.objects.first()
        self.assertEqual(customer.name, "Test Customer")
        self.assertEqual(customer.tenant, self.tenant)

    def test_create_customer_without_name(self):
        """Test that creating a customer without a name fails."""
        url = reverse("customers:customer-list")
        data = {
            "email": "customer@example.com",
            "phone": "123-456-7890",
        }

        response = self.client.post(url, data, HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Customer.objects.count(), 0)

    def test_create_customer_with_invalid_email(self):
        """Test that creating a customer with invalid email fails."""
        url = reverse("customers:customer-list")
        data = {
            "name": "Test Customer",
            "email": "invalid-email",
        }

        response = self.client.post(url, data, HTTP_X_TENANT_ID=str(self.tenant.id))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Customer.objects.count(), 0)
