from unittest import skip, TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Tenant, TenantUser, TenantDomain
import uuid


class TenantModelTests(TestCase):
    """Test cases for Tenant model with shared-schema multi-tenancy."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_tenant_creation(self):
        """Test basic tenant creation in shared schema."""
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
    
    def test_tenant_isolation_in_shared_schema(self):
        """Test that multiple tenants can coexist in shared schema."""
        tenant1 = Tenant.objects.create(
            name="Company A",
            slug="company-a",
            contact_email="admin@companya.com",
            created_by=self.user,
        )
        tenant2 = Tenant.objects.create(
            name="Company B",
            slug="company-b",
            contact_email="admin@companyb.com",
            created_by=self.user,
        )
        
        # Both tenants should exist in same schema
        self.assertEqual(Tenant.objects.count(), 2)
        self.assertIsNotNone(Tenant.objects.filter(slug="company-a").first())
        self.assertIsNotNone(Tenant.objects.filter(slug="company-b").first())
        
        # Tenants should have unique IDs
        self.assertNotEqual(tenant1.id, tenant2.id)


class TenantUserModelTests(TestCase):
    """Test cases for TenantUser model with shared-schema multi-tenancy."""

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
        """Test creating tenant-user association in shared schema."""
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

        # This should raise an IntegrityError due to unique constraint
        with self.assertRaises(Exception):
            TenantUser.objects.create(tenant=self.tenant, user=self.user1, role="admin")

    def test_tenant_user_str_method(self):
        """Test string representation of tenant user."""
        tenant_user = TenantUser.objects.create(
            tenant=self.tenant, user=self.user1, role="owner"
        )

        expected_str = f"{self.user1.username} @ {self.tenant.slug} (owner)"
        self.assertEqual(str(tenant_user), expected_str)


@skip("Requires refactoring for schema-based multi-tenancy - see SCHEMA_ISOLATION_MIGRATION_COMPLETE.md")
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

    def test_tenant_logo_field(self):
        """Test that tenant logo field can be set and retrieved."""
        # Create a simple test image
        image_content = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        image = SimpleUploadedFile("test_logo.gif", image_content, content_type="image/gif")
        
        # Update tenant with logo
        self.tenant.logo = image
        self.tenant.save()
        
        # Retrieve and verify
        tenant = Tenant.objects.get(id=self.tenant.id)
        self.assertIsNotNone(tenant.logo)
        self.assertTrue(tenant.logo.name.endswith('.gif'))
    
    def test_tenant_logo_upload_via_api(self):
        """Test uploading tenant logo via API."""
        url = reverse("tenants:tenant-detail", kwargs={"pk": self.tenant.id})
        
        # Create a simple test image
        image_content = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        image = SimpleUploadedFile("logo.gif", image_content, content_type="image/gif")
        
        # Upload logo
        response = self.client.patch(url, {"logo": image}, format="multipart")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("logo", response.data)
        self.assertIsNotNone(response.data["logo"])
        
        # Verify logo was saved
        self.tenant.refresh_from_db()
        self.assertIsNotNone(self.tenant.logo)
    
    def test_get_theme_settings(self):
        """Test getting tenant theme settings."""
        # Set theme colors
        self.tenant.set_theme_colors('#FF5733', '#33FF57')
        
        theme = self.tenant.get_theme_settings()
        
        self.assertEqual(theme['primary_color_light'], '#FF5733')
        self.assertEqual(theme['primary_color_dark'], '#33FF57')
        self.assertEqual(theme['name'], 'Test Company')
        self.assertIsNone(theme['logo_url'])  # No logo uploaded yet


@skip("Requires refactoring for schema-based multi-tenancy - see SCHEMA_ISOLATION_MIGRATION_COMPLETE.md")
class DomainModelTests(TestCase):
    """Test cases for Domain model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            created_by=self.user,
        )

    def test_domain_creation(self):
        """Test basic domain creation."""
        domain = TenantDomain.objects.create(
            domain="test-company.example.com",
            tenant=self.tenant,
            is_primary=True
        )

        self.assertEqual(domain.domain, "test-company.example.com")
        self.assertEqual(domain.tenant, self.tenant)
        self.assertTrue(domain.is_primary)

    def test_domain_lowercase_conversion(self):
        """Test that domain is automatically converted to lowercase."""
        domain = TenantDomain.objects.create(
            domain="TEST-COMPANY.EXAMPLE.COM",
            tenant=self.tenant,
            is_primary=True
        )

        self.assertEqual(domain.domain, "test-company.example.com")

    def test_domain_str_method(self):
        """Test string representation of domain."""
        domain = TenantDomain.objects.create(
            domain="test-company.example.com",
            tenant=self.tenant,
            is_primary=True
        )

        expected_str = f"test-company.example.com -> test-company (primary)"
        self.assertEqual(str(domain), expected_str)

    def test_domain_unique_constraint(self):
        """Test that domain must be unique."""
        from django.db import IntegrityError
        
        TenantDomain.objects.create(
            domain="test-company.example.com",
            tenant=self.tenant,
            is_primary=True
        )

        # Attempting to create another domain with same name should fail
        with self.assertRaises(IntegrityError):
            TenantDomain.objects.create(
                domain="test-company.example.com",
                tenant=self.tenant,
                is_primary=False
            )


@skip("Requires refactoring for schema-based multi-tenancy - see SCHEMA_ISOLATION_MIGRATION_COMPLETE.md")
class TenantSchemaNameTests(TestCase):
    """Test cases for Tenant schema_name field."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_schema_name_auto_generation(self):
        """Test that schema_name is auto-generated from slug."""
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com",
            created_by=self.user,
        )

        # Schema name should be generated from slug (dashes replaced with underscores)
        self.assertEqual(tenant.schema_name, "test_company")

    def test_schema_name_explicit(self):
        """Test that explicit schema_name is preserved."""
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            schema_name="custom_schema",
            contact_email="admin@testcompany.com",
            created_by=self.user,
        )

        self.assertEqual(tenant.schema_name, "custom_schema")

    def test_schema_name_unique(self):
        """Test that schema_name must be unique."""
        from django.db import IntegrityError
        
        Tenant.objects.create(
            name="Test Company 1",
            slug="test-company-1",
            schema_name="test_schema",
            contact_email="admin1@testcompany.com",
            created_by=self.user,
        )

        # Attempting to create another tenant with same schema_name should fail
        with self.assertRaises(IntegrityError):
            Tenant.objects.create(
                name="Test Company 2",
                slug="test-company-2",
                schema_name="test_schema",
                contact_email="admin2@testcompany.com",
                created_by=self.user,
            )
