"""
Tests for admin scripts and tenant initialization utilities.

This module tests:
- Tenant initialization via management command
- Invitation link generation utilities
- Tenant creation and query verification
"""
from datetime import timedelta
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.tenants.models import Tenant, TenantDomain, TenantInvitation, TenantUser
from apps.tenants.utils import (
    generate_invitation_link,
    get_invitation_by_token,
    validate_invitation,
)

# Test constants
TIMESTAMP_TOLERANCE_SECONDS = 60  # Tolerance for timestamp comparisons in tests


class InitTenantCommandTests(TestCase):
    """Tests for the init_tenant management command."""

    def test_init_tenant_basic(self):
        """Test basic tenant initialization with required fields."""
        out = StringIO()
        call_command(
            "init_tenant",
            "--schema-name=test_tenant",
            "--name=Test Tenant",
            "--domain=test.localhost",
            "--admin-email=admin@test.localhost",
            "--admin-password=testpass123",
            stdout=out,
        )

        # Verify tenant was created
        tenant = Tenant.objects.get(slug="test-tenant")
        self.assertEqual(tenant.name, "Test Tenant")
        self.assertEqual(tenant.schema_name, "test_tenant")
        self.assertTrue(tenant.is_active)

        # Verify domain was created
        domain = TenantDomain.objects.get(tenant=tenant)
        self.assertEqual(domain.domain, "test.localhost")
        self.assertTrue(domain.is_primary)

        # Verify admin user was created
        admin = User.objects.get(username="admin")
        self.assertEqual(admin.email, "admin@test.localhost")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_active)

        # Verify admin is associated with tenant as owner
        tenant_user = TenantUser.objects.get(tenant=tenant, user=admin)
        self.assertEqual(tenant_user.role, "owner")
        self.assertTrue(tenant_user.is_active)

        # Verify invitation was created
        invitation = TenantInvitation.objects.get(tenant=tenant)
        self.assertEqual(invitation.status, "pending")
        self.assertTrue(invitation.is_valid)

    def test_init_tenant_with_trial(self):
        """Test tenant initialization with trial period."""
        call_command(
            "init_tenant",
            "--schema-name=trial_tenant",
            "--name=Trial Tenant",
            "--domain=trial.localhost",
            "--admin-email=admin@trial.localhost",
            "--admin-password=testpass123",
            "--on-trial",
            "--trial-days=14",
            stdout=StringIO(),
        )

        tenant = Tenant.objects.get(slug="trial-tenant")
        self.assertTrue(tenant.is_trial)
        self.assertIsNotNone(tenant.trial_ends_at)

        # Check trial ends approximately 14 days from now
        expected_end = timezone.now() + timedelta(days=14)
        self.assertAlmostEqual(
            tenant.trial_ends_at.timestamp(),
            expected_end.timestamp(),
            delta=TIMESTAMP_TOLERANCE_SECONDS,
        )

    def test_init_tenant_skip_invitation(self):
        """Test tenant initialization without creating invitation."""
        call_command(
            "init_tenant",
            "--schema-name=no_invite_tenant",
            "--name=No Invite Tenant",
            "--domain=noinvite.localhost",
            "--admin-email=admin@noinvite.localhost",
            "--admin-password=testpass123",
            "--skip-invitation",
            stdout=StringIO(),
        )

        tenant = Tenant.objects.get(slug="no-invite-tenant")

        # Verify no invitation was created
        invitations = TenantInvitation.objects.filter(tenant=tenant)
        self.assertEqual(invitations.count(), 0)

    def test_init_tenant_custom_username(self):
        """Test tenant initialization with custom admin username."""
        call_command(
            "init_tenant",
            "--schema-name=custom_user_tenant",
            "--name=Custom User Tenant",
            "--domain=customuser.localhost",
            "--admin-email=admin@customuser.localhost",
            "--admin-password=testpass123",
            "--admin-username=superadmin",
            stdout=StringIO(),
        )

        # Verify user was created with custom username
        admin = User.objects.get(username="superadmin")
        self.assertEqual(admin.email, "admin@customuser.localhost")

    def test_init_tenant_duplicate_schema_fails(self):
        """Test that duplicate schema name raises error."""
        # Create first tenant
        call_command(
            "init_tenant",
            "--schema-name=dup_schema",
            "--name=First Tenant",
            "--domain=first.localhost",
            "--admin-email=admin1@first.localhost",
            "--admin-password=testpass123",
            stdout=StringIO(),
        )

        # Try to create second tenant with same schema
        with self.assertRaises(Exception):
            call_command(
                "init_tenant",
                "--schema-name=dup_schema",
                "--name=Second Tenant",
                "--domain=second.localhost",
                "--admin-email=admin2@second.localhost",
                "--admin-password=testpass123",
                stdout=StringIO(),
            )


class GenerateInvitationLinkTests(TestCase):
    """Tests for the generate_invitation_link utility function."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            username="testowner",
            email="owner@example.com",
            password="testpass123",
        )
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            schema_name="test_company",
            contact_email="admin@testcompany.com",
            created_by=self.user,
        )
        self.domain = TenantDomain.objects.create(
            domain="testcompany.example.com",
            tenant=self.tenant,
            is_primary=True,
        )

    def test_generate_invitation_link_basic(self):
        """Test basic invitation link generation."""
        invitation, url = generate_invitation_link(self.tenant)

        self.assertIsNotNone(invitation)
        self.assertIsNotNone(url)
        self.assertEqual(invitation.tenant, self.tenant)
        self.assertEqual(invitation.role, "user")
        self.assertEqual(invitation.status, "pending")
        self.assertIn("testcompany.example.com", url)
        self.assertIn(invitation.token, url)

    def test_generate_invitation_link_with_role(self):
        """Test invitation link generation with custom role."""
        invitation, url = generate_invitation_link(self.tenant, role="admin")

        self.assertEqual(invitation.role, "admin")

    def test_generate_invitation_link_with_days_valid(self):
        """Test invitation link generation with custom validity period."""
        invitation, url = generate_invitation_link(self.tenant, days_valid=30)

        expected_expiry = timezone.now() + timedelta(days=30)
        self.assertAlmostEqual(
            invitation.expires_at.timestamp(),
            expected_expiry.timestamp(),
            delta=TIMESTAMP_TOLERANCE_SECONDS,
        )

    def test_generate_invitation_link_with_message(self):
        """Test invitation link generation with custom message."""
        custom_message = "Welcome to our team!"
        invitation, url = generate_invitation_link(
            self.tenant, message=custom_message
        )

        self.assertEqual(invitation.message, custom_message)

    def test_generate_invitation_link_with_invited_by(self):
        """Test invitation link generation with invited_by user."""
        invitation, url = generate_invitation_link(
            self.tenant, invited_by=self.user
        )

        self.assertEqual(invitation.invited_by, self.user)

    def test_generate_invitation_link_invalid_role(self):
        """Test that invalid role raises ValueError."""
        with self.assertRaises(ValueError):
            generate_invitation_link(self.tenant, role="invalid_role")

    def test_generate_invitation_link_localhost_uses_http(self):
        """Test that localhost domain uses http protocol."""
        # Create tenant with localhost domain
        localhost_tenant = Tenant.objects.create(
            name="Localhost Company",
            slug="localhost-company",
            schema_name="localhost_company",
            contact_email="admin@localhost",
        )
        TenantDomain.objects.create(
            domain="localhost:8000",
            tenant=localhost_tenant,
            is_primary=True,
        )

        invitation, url = generate_invitation_link(localhost_tenant)

        self.assertTrue(url.startswith("http://"))


class GetInvitationByTokenTests(TestCase):
    """Tests for the get_invitation_by_token utility function."""

    def setUp(self):
        """Set up test fixtures."""
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            schema_name="test_company",
            contact_email="admin@testcompany.com",
        )

    def test_get_invitation_by_token_valid(self):
        """Test retrieving a valid invitation by token."""
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email="test@example.com",
            role="user",
            expires_at=timezone.now() + timedelta(days=7),
        )

        result = get_invitation_by_token(invitation.token)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, invitation.id)

    def test_get_invitation_by_token_not_found(self):
        """Test retrieving non-existent invitation returns None."""
        result = get_invitation_by_token("nonexistent_token")

        self.assertIsNone(result)

    def test_get_invitation_by_token_updates_expired_status(self):
        """Test that expired invitation status is updated."""
        # Create an expired invitation
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email="test@example.com",
            role="user",
            expires_at=timezone.now() - timedelta(days=1),
            status="pending",
        )

        result = get_invitation_by_token(invitation.token)

        self.assertIsNotNone(result)
        self.assertEqual(result.status, "expired")


class ValidateInvitationTests(TestCase):
    """Tests for the validate_invitation utility function."""

    def setUp(self):
        """Set up test fixtures."""
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            schema_name="test_company",
            contact_email="admin@testcompany.com",
        )

    def test_validate_invitation_valid(self):
        """Test validating a valid invitation."""
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email="test@example.com",
            role="admin",
            expires_at=timezone.now() + timedelta(days=7),
        )

        result = validate_invitation(invitation.token)

        self.assertTrue(result["valid"])
        self.assertIsNone(result["error"])
        self.assertEqual(result["tenant_name"], "Test Company")
        self.assertEqual(result["role"], "admin")

    def test_validate_invitation_not_found(self):
        """Test validating non-existent invitation."""
        result = validate_invitation("nonexistent_token")

        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "Invitation not found")

    def test_validate_invitation_expired(self):
        """Test validating an expired invitation."""
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email="test@example.com",
            role="user",
            expires_at=timezone.now() - timedelta(days=1),
            status="pending",
        )

        result = validate_invitation(invitation.token)

        self.assertFalse(result["valid"])
        self.assertIn("expired", result["error"].lower())

    def test_validate_invitation_already_accepted(self):
        """Test validating an already accepted invitation."""
        invitation = TenantInvitation.objects.create(
            tenant=self.tenant,
            email="test@example.com",
            role="user",
            expires_at=timezone.now() + timedelta(days=7),
            status="accepted",
        )

        result = validate_invitation(invitation.token)

        self.assertFalse(result["valid"])
        self.assertEqual(result["error"], "Invitation is accepted")


class TenantQueryTests(TestCase):
    """Tests to verify tenant query results as documented in admin-quick-reference.md."""

    def setUp(self):
        """Set up test data."""
        # Create users
        self.owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="testpass123",
            is_staff=True,
        )
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
        )
        self.superuser = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@example.com",
            password="testpass123",
        )

        # Create tenants
        self.tenant1 = Tenant.objects.create(
            name="Company One",
            slug="company-one",
            schema_name="company_one",
            contact_email="admin@company-one.com",
            is_active=True,
            is_trial=True,
            trial_ends_at=timezone.now() + timedelta(days=30),
        )
        self.tenant2 = Tenant.objects.create(
            name="Company Two",
            slug="company-two",
            schema_name="company_two",
            contact_email="admin@company-two.com",
            is_active=True,
            is_trial=False,
        )

        # Create domains
        TenantDomain.objects.create(
            domain="company-one.example.com",
            tenant=self.tenant1,
            is_primary=True,
        )
        TenantDomain.objects.create(
            domain="company-two.example.com",
            tenant=self.tenant2,
            is_primary=True,
        )

        # Create tenant-user associations
        TenantUser.objects.create(
            tenant=self.tenant1,
            user=self.owner,
            role="owner",
            is_active=True,
        )
        TenantUser.objects.create(
            tenant=self.tenant1,
            user=self.admin,
            role="admin",
            is_active=True,
        )
        TenantUser.objects.create(
            tenant=self.tenant2,
            user=self.owner,
            role="manager",
            is_active=True,
        )

    def test_list_all_tenants(self):
        """Test listing all tenants."""
        tenants = Tenant.objects.all()
        self.assertEqual(tenants.count(), 2)

    def test_find_active_tenants_on_trial(self):
        """Test finding active tenants on trial."""
        tenants = Tenant.objects.filter(
            is_active=True,
            is_trial=True,
        )
        self.assertEqual(tenants.count(), 1)
        self.assertEqual(tenants.first().slug, "company-one")

    def test_list_superusers(self):
        """Test listing superusers."""
        superusers = User.objects.filter(is_superuser=True)
        self.assertEqual(superusers.count(), 1)
        self.assertEqual(superusers.first().username, "superadmin")

    def test_list_staff_users(self):
        """Test listing staff users."""
        staff = User.objects.filter(is_staff=True)
        # owner and superadmin are staff
        self.assertEqual(staff.count(), 2)

    def test_tenant_owners_query(self):
        """Test finding tenant owners."""
        owners = TenantUser.objects.filter(role="owner")
        self.assertEqual(owners.count(), 1)
        self.assertEqual(owners.first().user.username, "owner")
        self.assertEqual(owners.first().tenant.slug, "company-one")

    def test_users_with_multiple_tenants(self):
        """Test finding users with multiple tenant memberships."""
        from django.db.models import Count

        users_with_multiple = (
            TenantUser.objects.filter(is_active=True)
            .values("user")
            .annotate(tenant_count=Count("tenant"))
            .filter(tenant_count__gt=1)
        )
        self.assertEqual(users_with_multiple.count(), 1)

    def test_role_distribution_per_tenant(self):
        """Test getting role distribution per tenant."""
        from django.db.models import Count

        role_distribution = (
            TenantUser.objects.filter(is_active=True)
            .values("tenant__name", "role")
            .annotate(count=Count("id"))
            .order_by("tenant__name", "role")
        )

        # Should have owner and admin for Company One, manager for Company Two
        self.assertEqual(role_distribution.count(), 3)
