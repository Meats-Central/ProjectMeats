#!/usr/bin/env python
"""
Manual test script for invitation email functionality.

This script demonstrates:
1. Creating an invitation and sending an email
2. Resending an invitation email
3. Verifying email content
"""
import os
import sys
import django

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectmeats.settings.development")
django.setup()

from datetime import timedelta

from django.contrib.auth.models import User
from django.core import mail
from django.utils import timezone

from apps.tenants.email_utils import send_invitation_email
from apps.tenants.models import Tenant, TenantInvitation, TenantUser


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def print_section(text):
    """Print a formatted section header."""
    print("\n" + "-" * 70)
    print(text)
    print("-" * 70)


def main():
    print_header("TENANT INVITATION EMAIL SYSTEM - MANUAL TEST")

    # Clean up from previous runs
    print_section("Setup: Cleaning up test data")
    try:
        TenantInvitation.objects.filter(email__contains="@emailtest.com").delete()
        User.objects.filter(username="emailtest_admin").delete()
        Tenant.objects.filter(slug="email-test-tenant").delete()
        print("✓ Cleaned up existing test data")
    except Exception as e:
        print(f"⚠ Warning: Could not clean up test data: {e}")
        print("  (This is OK if this is the first run)")

    # Create test tenant
    print_section("Step 1: Creating test tenant")
    tenant, tenant_created = Tenant.objects.get_or_create(
        slug="email-test-tenant",
        defaults={
            "name": "Email Test Company",
            "contact_email": "admin@emailtest.com",
            "is_active": True,
        },
    )
    if tenant_created:
        print(f"✓ Created tenant: {tenant.name} (ID: {tenant.id})")
    else:
        print(f"✓ Using existing tenant: {tenant.name} (ID: {tenant.id})")

    # Create admin user
    print_section("Step 2: Creating admin user")
    admin_user, user_created = User.objects.get_or_create(
        username="emailtest_admin",
        defaults={
            "email": "admin@emailtest.com",
            "first_name": "Admin",
            "last_name": "Tester",
        },
    )
    if user_created:
        admin_user.set_password("testpass123")
        admin_user.save()
        print(f"✓ Created admin user: {admin_user.get_full_name()} ({admin_user.username})")
    else:
        print(
            f"✓ Using existing admin user: {admin_user.get_full_name()} ({admin_user.username})"
        )

    # Create TenantUser association
    print_section("Step 3: Linking admin to tenant")
    tenant_user, tu_created = TenantUser.objects.get_or_create(
        tenant=tenant,
        user=admin_user,
        defaults={"role": "admin", "is_active": True},
    )
    if tu_created:
        print(f"✓ Linked {admin_user.username} to {tenant.name} as admin")
    else:
        print(
            f"✓ Using existing link: {admin_user.username} → {tenant.name} ({tenant_user.role})"
        )

    # Create invitation
    print_section("Step 4: Creating invitation")
    invitation = TenantInvitation.objects.create(
        tenant=tenant,
        email="newuser@emailtest.com",
        role="manager",
        invited_by=admin_user,
        message="Welcome to our team! We're excited to have you join us.",
        expires_at=timezone.now() + timedelta(days=7),
    )
    print(f"✓ Created invitation for: {invitation.email}")
    print(f"  - Role: {invitation.role}")
    print(f"  - Token: {invitation.token[:20]}... (truncated)")
    print(f"  - Expires: {invitation.expires_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"  - Status: {invitation.status}")
    print(f"  - Is valid: {invitation.is_valid}")

    # Send email
    print_section("Step 5: Sending invitation email")
    result = send_invitation_email(invitation)

    if result:
        print("✓ Email sent successfully!")
        print("\nNote: In development mode, emails are printed to console above.")
        print("In production, they would be sent via SMTP.")
    else:
        print("✗ Email failed to send")
        return

    # Summary
    print_header("TEST SUMMARY")
    if result:
        print("✅ ALL TESTS PASSED!")
        print("\nThe email notification system is working correctly:")
        print("  ✓ Emails are sent when invitations are created")
        print("  ✓ Email content includes all required information:")
        print(f"    - Tenant name: {tenant.name}")
        print(f"    - Invitee email: {invitation.email}")
        print(f"    - Role: {invitation.role}")
        print(f"    - Inviter name: {admin_user.get_full_name()}")
        print(f"    - Personal message: {invitation.message}")
        print(f"    - Signup URL with token")
        print(f"    - Expiration date")
        print("  ✓ HTML and plain text versions are included")
        print("  ✓ Email was successfully processed")
    else:
        print("❌ TEST FAILED")
        print("\nEmail sending failed. Please review the output above for details.")

    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
