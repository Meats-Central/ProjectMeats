"""
Quick test script for the invitation system.
Run with: python backend/test_invitations.py
"""
import os
import django
import sys

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmeats.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.tenants.models import Tenant, TenantUser, TenantInvitation
from datetime import timedelta
from django.utils import timezone


def test_invitation_system():
    """Test the invitation system end-to-end."""
    
    print("=" * 60)
    print("TESTING INVITATION SYSTEM")
    print("=" * 60)
    
    # 1. Create a test tenant
    print("\n1. Creating test tenant...")
    tenant, created = Tenant.objects.get_or_create(
        slug='test-tenant',
        defaults={
            'name': 'Test Tenant',
            'contact_email': 'admin@test.com',
            'is_active': True
        }
    )
    if created:
        print(f"   ✓ Created tenant: {tenant.name}")
    else:
        print(f"   ✓ Using existing tenant: {tenant.name}")
    
    # 2. Create admin user
    print("\n2. Creating admin user...")
    admin_user, created = User.objects.get_or_create(
        username='testadmin',
        defaults={
            'email': 'admin@test.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True
        }
    )
    if created:
        admin_user.set_password('testpass123')
        admin_user.save()
        print(f"   ✓ Created admin user: {admin_user.username}")
    else:
        print(f"   ✓ Using existing admin user: {admin_user.username}")
    
    # 3. Create TenantUser for admin
    print("\n3. Linking admin to tenant...")
    tenant_user, created = TenantUser.objects.get_or_create(
        tenant=tenant,
        user=admin_user,
        defaults={
            'role': 'admin',
            'is_active': True
        }
    )
    if created:
        print(f"   ✓ Created TenantUser: {admin_user.username} → {tenant.name} (admin)")
    else:
        print(f"   ✓ Using existing TenantUser: {admin_user.username} → {tenant.name} ({tenant_user.role})")
    
    # 4. Create invitation
    print("\n4. Creating invitation...")
    invitation_email = 'newuser@test.com'
    
    # Delete any existing invitations for this email
    TenantInvitation.objects.filter(
        tenant=tenant,
        email=invitation_email
    ).delete()
    
    invitation = TenantInvitation.objects.create(
        tenant=tenant,
        email=invitation_email,
        role='manager',
        invited_by=admin_user,
        message='Welcome to the team!',
        expires_at=timezone.now() + timedelta(days=7)
    )
    print(f"   ✓ Created invitation for: {invitation.email}")
    print(f"     - Token: {invitation.token[:20]}...")
    print(f"     - Role: {invitation.role}")
    print(f"     - Expires: {invitation.expires_at}")
    print(f"     - Status: {invitation.status}")
    
    # 5. Validate invitation
    print("\n5. Validating invitation...")
    print(f"   - Is expired: {invitation.is_expired}")
    print(f"   - Is valid: {invitation.is_valid}")
    
    if invitation.is_valid:
        print("   ✓ Invitation is valid!")
    else:
        print("   ✗ Invitation is NOT valid")
        return
    
    # 6. Simulate user signup (without actually creating user)
    print("\n6. Simulating signup process...")
    print(f"   - User would sign up with email: {invitation.email}")
    print(f"   - User would be assigned role: {invitation.role}")
    print(f"   - User would be linked to tenant: {tenant.name}")
    print(f"   - Invitation would be marked as 'accepted'")
    
    # 7. Test invitation queries
    print("\n7. Testing invitation queries...")
    
    # Pending invitations for tenant
    pending_count = TenantInvitation.objects.filter(
        tenant=tenant,
        status='pending'
    ).count()
    print(f"   - Pending invitations for {tenant.name}: {pending_count}")
    
    # Invitations sent by admin
    admin_invites_count = TenantInvitation.objects.filter(
        invited_by=admin_user
    ).count()
    print(f"   - Invitations sent by {admin_user.username}: {admin_invites_count}")
    
    # 8. Test expiration
    print("\n8. Testing expiration...")
    expired_invitation = TenantInvitation(
        tenant=tenant,
        email='expired@test.com',
        role='user',
        invited_by=admin_user,
        expires_at=timezone.now() - timedelta(days=1)  # Yesterday
    )
    print(f"   - Expired invitation is_expired: {expired_invitation.is_expired}")
    print(f"   - Expired invitation is_valid: {expired_invitation.is_valid}")
    
    # 9. Database checks
    print("\n9. Database checks...")
    print(f"   - Total Tenants: {Tenant.objects.count()}")
    print(f"   - Total Users: {User.objects.count()}")
    print(f"   - Total TenantUsers: {TenantUser.objects.count()}")
    print(f"   - Total Invitations: {TenantInvitation.objects.count()}")
    
    print("\n" + "=" * 60)
    print("✓ INVITATION SYSTEM TEST COMPLETE")
    print("=" * 60)
    print(f"\nTest invitation token: {invitation.token}")
    print("\nTo test API endpoints:")
    print(f"1. Validate: GET /api/tenants/api/invitations/validate/?token={invitation.token}")
    print(f"2. Signup: POST /api/tenants/api/auth/signup-with-invitation/")
    print("   Body: {")
    print(f'     "invitation_token": "{invitation.token}",')
    print('     "username": "newuser",')
    print('     "password": "SecurePass123!",')
    print('     "first_name": "New",')
    print('     "last_name": "User"')
    print("   }")
    print("\n")


if __name__ == '__main__':
    test_invitation_system()
