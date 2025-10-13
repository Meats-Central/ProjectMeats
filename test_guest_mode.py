"""
Test script for guest mode functionality.
Run with: python test_guest_mode.py
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
from apps.tenants.models import Tenant, TenantUser
from rest_framework.authtoken.models import Token


def test_guest_mode():
    """Test the guest mode setup."""
    
    print("=" * 60)
    print("TESTING GUEST MODE")
    print("=" * 60)
    
    # 1. Check guest user exists
    print("\n1. Checking guest user...")
    try:
        guest_user = User.objects.get(username='guest')
        print(f"   ✓ Guest user found: {guest_user.username}")
        print(f"     - Email: {guest_user.email}")
        print(f"     - First name: {guest_user.first_name}")
        print(f"     - Last name: {guest_user.last_name}")
        print(f"     - Is staff: {guest_user.is_staff}")
        print(f"     - Is superuser: {guest_user.is_superuser}")
        print(f"     - Is active: {guest_user.is_active}")
        
        # Verify NOT superuser
        if guest_user.is_superuser:
            print("   ✗ ERROR: Guest user should NOT be superuser!")
        else:
            print("   ✓ Confirmed: Guest is NOT superuser")
        
        # Verify IS staff (for testing/demo purposes)
        if guest_user.is_staff:
            print("   ✓ Confirmed: Guest IS staff (can access Django admin for testing)")
        else:
            print("   ⚠ Warning: Guest is NOT staff (cannot access Django admin)")
            
    except User.DoesNotExist:
        print("   ✗ Guest user not found!")
        print("   Run: python manage.py create_guest_tenant")
        return
    
    # 2. Check guest token
    print("\n2. Checking guest auth token...")
    token, created = Token.objects.get_or_create(user=guest_user)
    print(f"   ✓ Token: {token.key[:20]}...")
    if created:
        print("   ✓ Created new token")
    else:
        print("   ✓ Using existing token")
    
    # 3. Check guest tenant
    print("\n3. Checking guest tenant...")
    try:
        guest_tenant = Tenant.objects.get(slug='guest-demo')
        print(f"   ✓ Guest tenant found: {guest_tenant.name}")
        print(f"     - Slug: {guest_tenant.slug}")
        print(f"     - Contact email: {guest_tenant.contact_email}")
        print(f"     - Is active: {guest_tenant.is_active}")
        print(f"     - Is trial: {guest_tenant.is_trial}")
        print(f"     - Settings: {guest_tenant.settings}")
        
        # Check if marked as guest tenant
        if guest_tenant.settings.get('is_guest_tenant'):
            print("   ✓ Confirmed: Marked as guest tenant")
        else:
            print("   ⚠ Warning: Not marked as guest tenant in settings")
            
    except Tenant.DoesNotExist:
        print("   ✗ Guest tenant not found!")
        print("   Run: python manage.py create_guest_tenant")
        return
    
    # 4. Check TenantUser association
    print("\n4. Checking guest-tenant association...")
    try:
        tenant_user = TenantUser.objects.get(
            tenant=guest_tenant,
            user=guest_user
        )
        print(f"   ✓ Association found")
        print(f"     - Role: {tenant_user.role}")
        print(f"     - Is active: {tenant_user.is_active}")
        
        # Verify role is admin (NOT owner)
        if tenant_user.role == 'admin':
            print("   ✓ Confirmed: Guest has 'admin' role (correct)")
        elif tenant_user.role == 'owner':
            print("   ⚠ Warning: Guest has 'owner' role (should be 'admin')")
        else:
            print(f"   ⚠ Warning: Guest has '{tenant_user.role}' role (expected 'admin')")
            
    except TenantUser.DoesNotExist:
        print("   ✗ Guest-tenant association not found!")
        return
    
    # 5. Verify guest can't access other tenants
    print("\n5. Checking tenant isolation...")
    guest_tenants = TenantUser.objects.filter(
        user=guest_user,
        is_active=True
    ).count()
    print(f"   - Guest has access to {guest_tenants} tenant(s)")
    
    if guest_tenants == 1:
        print("   ✓ Confirmed: Guest only has access to guest tenant")
    else:
        print(f"   ⚠ Warning: Guest has access to {guest_tenants} tenants")
    
    # 6. Test guest permissions
    print("\n6. Testing guest permissions...")
    
    # Check Django permissions
    all_tenants = Tenant.objects.all().count()
    print(f"   - Total tenants in system: {all_tenants}")
    
    # Guest should only see their tenant via API
    guest_accessible_tenants = Tenant.objects.filter(
        users__user=guest_user,
        users__is_active=True
    ).count()
    print(f"   - Tenants accessible to guest: {guest_accessible_tenants}")
    
    # 7. Summary
    print("\n" + "=" * 60)
    print("✓ GUEST MODE TEST COMPLETE")
    print("=" * 60)
    
    print("\nGuest Login Credentials:")
    print(f"  Username: {guest_user.username}")
    print(f"  Password: guest123")
    print(f"  Token: {token.key}")
    
    print("\nTenant Information:")
    print(f"  Name: {guest_tenant.name}")
    print(f"  Slug: {guest_tenant.slug}")
    print(f"  Role: {tenant_user.role}")
    
    print("\nSecurity Verification:")
    print(f"  ✓ NOT Superuser: {not guest_user.is_superuser}")
    print(f"  ✓ IS Staff (Testing): {guest_user.is_staff}")
    print(f"     - Can access Django admin for testing/demo")
    print(f"     - NO system-wide permissions (not superuser)")
    print(f"  ✓ Admin Role: {tenant_user.role == 'admin'}")
    print(f"  ✓ Tenant Isolated: {guest_tenants == 1}")
    
    print("\nAPI Testing:")
    print("  Test guest login:")
    print("    POST http://localhost:8000/api/v1/core/auth/guest-login/")
    print("\n  Test regular login:")
    print("    POST http://localhost:8000/api/v1/core/auth/login/")
    print("    Body: {\"username\": \"guest\", \"password\": \"guest123\"}")
    print("\n  Test tenant access:")
    print(f"    GET http://localhost:8000/api/v1/tenants/api/tenants/")
    print(f"    Header: Authorization: Token {token.key}")
    
    print("\n")


if __name__ == '__main__':
    test_guest_mode()
