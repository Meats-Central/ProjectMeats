"""
Tests for tenant-based access control and role permissions.
"""
from django.test import TestCase
from django.contrib.auth.models import User, Group
from apps.tenants.models import Tenant, TenantUser


class RolePermissionsTests(TestCase):
    """Test role-based permissions and Django admin access."""
    
    def setUp(self):
        """Set up test data."""
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            contact_email="admin@testcompany.com"
        )
    
    def test_owner_gets_staff_status(self):
        """Test that owners automatically get is_staff=True."""
        user = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="testpass"
        )
        self.assertFalse(user.is_staff)
        
        # Create TenantUser with owner role
        TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="owner",
            is_active=True
        )
        
        # Refresh user from DB
        user.refresh_from_db()
        
        # Should now have staff status
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_admin_gets_staff_status(self):
        """Test that admins automatically get is_staff=True."""
        user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass"
        )
        self.assertFalse(user.is_staff)
        
        # Create TenantUser with admin role
        TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="admin",
            is_active=True
        )
        
        # Refresh user from DB
        user.refresh_from_db()
        
        # Should now have staff status
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_manager_gets_staff_status(self):
        """Test that managers automatically get is_staff=True."""
        user = User.objects.create_user(
            username="manager",
            email="manager@test.com",
            password="testpass"
        )
        self.assertFalse(user.is_staff)
        
        # Create TenantUser with manager role
        TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="manager",
            is_active=True
        )
        
        # Refresh user from DB
        user.refresh_from_db()
        
        # Should now have staff status
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_regular_user_no_staff_status(self):
        """Test that regular users do NOT get is_staff."""
        user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass"
        )
        self.assertFalse(user.is_staff)
        
        # Create TenantUser with user role
        TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="user",
            is_active=True
        )
        
        # Refresh user from DB
        user.refresh_from_db()
        
        # Should NOT have staff status
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_readonly_user_no_staff_status(self):
        """Test that readonly users do NOT get is_staff."""
        user = User.objects.create_user(
            username="readonly",
            email="readonly@test.com",
            password="testpass"
        )
        self.assertFalse(user.is_staff)
        
        # Create TenantUser with readonly role
        TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="readonly",
            is_active=True
        )
        
        # Refresh user from DB
        user.refresh_from_db()
        
        # Should NOT have staff status
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_user_added_to_tenant_group(self):
        """Test that users are added to tenant-specific groups."""
        user = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="testpass"
        )
        
        # Create TenantUser with owner role
        TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="owner",
            is_active=True
        )
        
        # Should be in tenant-specific group
        group_name = f"{self.tenant.slug}_owner"
        self.assertTrue(user.groups.filter(name=group_name).exists())
    
    def test_staff_status_removed_when_no_admin_roles(self):
        """Test that is_staff is removed when user loses all admin-level roles."""
        user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass"
        )
        
        # Create TenantUser with admin role
        tenant_user = TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="admin",
            is_active=True
        )
        
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        
        # Change role to regular user
        tenant_user.role = "user"
        tenant_user.save()
        
        user.refresh_from_db()
        
        # Should lose staff status
        self.assertFalse(user.is_staff)
    
    def test_staff_status_removed_when_tenant_user_deleted(self):
        """Test that is_staff is removed when TenantUser is deleted."""
        user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass"
        )
        
        # Create TenantUser with admin role
        tenant_user = TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="admin",
            is_active=True
        )
        
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        
        # Delete TenantUser
        tenant_user.delete()
        
        user.refresh_from_db()
        
        # Should lose staff status
        self.assertFalse(user.is_staff)
    
    def test_staff_status_removed_when_tenant_user_deactivated(self):
        """Test that is_staff is removed when TenantUser is deactivated."""
        user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass"
        )
        
        # Create TenantUser with admin role
        tenant_user = TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="admin",
            is_active=True
        )
        
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        
        # Deactivate TenantUser
        tenant_user.is_active = False
        tenant_user.save()
        
        user.refresh_from_db()
        
        # Should lose staff status
        self.assertFalse(user.is_staff)
    
    def test_superuser_status_preserved(self):
        """Test that superusers keep their status even without tenant roles."""
        user = User.objects.create_superuser(
            username="superuser",
            email="superuser@test.com",
            password="testpass"
        )
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
        # Create and delete TenantUser - shouldn't affect superuser
        tenant_user = TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="user",
            is_active=True
        )
        tenant_user.delete()
        
        user.refresh_from_db()
        
        # Should still be superuser and staff
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
    
    def test_user_with_multiple_tenants_keeps_staff(self):
        """Test that user with admin role in multiple tenants keeps is_staff."""
        user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass"
        )
        
        tenant2 = Tenant.objects.create(
            name="Second Company",
            slug="second-company",
            contact_email="admin@secondcompany.com"
        )
        
        # Create TenantUser for both tenants with admin role
        tu1 = TenantUser.objects.create(
            tenant=self.tenant,
            user=user,
            role="admin",
            is_active=True
        )
        TenantUser.objects.create(
            tenant=tenant2,
            user=user,
            role="admin",
            is_active=True
        )
        
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        
        # Delete one tenant association
        tu1.delete()
        
        user.refresh_from_db()
        
        # Should STILL have staff status because of second tenant
        self.assertTrue(user.is_staff)
