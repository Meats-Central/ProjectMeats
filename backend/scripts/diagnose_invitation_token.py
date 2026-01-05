#!/usr/bin/env python
"""
Diagnostic script to troubleshoot invitation token issues.

Usage:
    python scripts/diagnose_invitation_token.py <token>
    
Example:
    python scripts/diagnose_invitation_token.py AYwY-DvIXBlEBgsryDUsnxkAVv0L4KKTxLUM2qeuhy0Xg5w3DVDenC5doXmiyxng
"""
import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Detect which settings to use from environment or default to development
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'projectmeats.settings.development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

django.setup()

from django.conf import settings
from django.utils import timezone
from apps.tenants.models import TenantInvitation


def diagnose_token(token_str):
    """Diagnose invitation token issues."""
    
    print("=" * 80)
    print("INVITATION TOKEN DIAGNOSTIC REPORT")
    print("=" * 80)
    print()
    
    # Environment info
    print("🔧 ENVIRONMENT CONFIGURATION:")
    print(f"   Django Settings: {settings_module}")
    print(f"   Database: {settings.DATABASES['default']['NAME']}")
    print(f"   Database Host: {settings.DATABASES['default']['HOST']}")
    print(f"   FRONTEND_URL: {getattr(settings, 'FRONTEND_URL', '❌ NOT SET (defaults to production!)')}")
    print()
    
    # Token search
    print(f"🔍 SEARCHING FOR TOKEN: {token_str[:20]}...")
    print()
    
    try:
        # Try exact match
        invitation = TenantInvitation.objects.select_related('tenant').filter(token=token_str).first()
        
        if invitation:
            print("✅ TOKEN FOUND!")
            print()
            print("📋 INVITATION DETAILS:")
            print(f"   ID: {invitation.id}")
            print(f"   Email: {invitation.email or '(Reusable link - no email)'}")
            print(f"   Tenant: {invitation.tenant.name} (slug: {invitation.tenant.slug})")
            print(f"   Status: {invitation.status}")
            print(f"   Role: {invitation.role}")
            print(f"   Created: {invitation.created_at}")
            print(f"   Expires: {invitation.expires_at}")
            print(f"   Is Expired: {'❌ YES' if invitation.is_expired else '✅ NO'}")
            print(f"   Is Valid: {'✅ YES' if invitation.is_valid else '❌ NO'}")
            print()
            
            if invitation.is_reusable:
                print("♻️  REUSABILITY:")
                print(f"   Reusable: Yes")
                print(f"   Usage Count: {invitation.usage_count}/{invitation.max_uses}")
                print()
            
            # Test the URL that would be generated
            frontend_url = getattr(settings, 'FRONTEND_URL', 'https://meatscentral.com')
            expected_link = f"{frontend_url}/signup?token={invitation.token}"
            print("🔗 EXPECTED INVITATION LINK:")
            print(f"   {expected_link}")
            print()
            
            # Validation warnings
            if invitation.is_expired:
                print("⚠️  WARNING: Invitation has expired!")
                print(f"   Expired on: {invitation.expires_at}")
                print(f"   Current time: {timezone.now()}")
                print()
            
            if not invitation.is_valid:
                print("⚠️  WARNING: Invitation is not valid!")
                if invitation.status != 'pending':
                    print(f"   Reason: Status is '{invitation.status}' (must be 'pending')")
                if invitation.is_reusable and invitation.usage_count >= invitation.max_uses:
                    print(f"   Reason: Maximum uses reached ({invitation.usage_count}/{invitation.max_uses})")
                print()
            
        else:
            print("❌ TOKEN NOT FOUND in this database")
            print()
            print("🔍 POSSIBLE CAUSES:")
            print("   1. Cross-environment issue: Token created in different environment")
            print("      - Check if you're testing on the correct environment")
            print("      - Dev tokens only work on dev.meatscentral.com")
            print("      - Prod tokens only work on meatscentral.com")
            print()
            print("   2. Token has been deleted or never created")
            print()
            print("   3. Database connection issue")
            print()
            
            # Show recent invitations for comparison
            print("📊 RECENT INVITATIONS (Last 5):")
            recent = TenantInvitation.objects.select_related('tenant').order_by('-created_at')[:5]
            
            if recent.exists():
                for inv in recent:
                    status_icon = "✅" if inv.is_valid else "❌"
                    print(f"   {status_icon} {inv.tenant.name}: {inv.email or '(reusable)'}")
                    print(f"      Token: {inv.token[:20]}...")
                    print(f"      Status: {inv.status}, Created: {inv.created_at}")
                print()
            else:
                print("   No invitations found in database")
                print()
        
    except Exception as e:
        print(f"❌ ERROR QUERYING DATABASE: {e}")
        print()
        import traceback
        traceback.print_exc()
    
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/diagnose_invitation_token.py <token>")
        print()
        print("Example:")
        print("  python scripts/diagnose_invitation_token.py AYwY-DvIXBlEBgsryDUsnxkAVv0L4KKTxLUM2qeuhy0Xg5w3DVDenC5doXmiyxng")
        sys.exit(1)
    
    token = sys.argv[1]
    diagnose_token(token)
