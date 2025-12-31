#!/usr/bin/env python
"""
Verification script for staging.meatscentral.com configuration.

This script checks that all necessary configuration is in place for
staging.meatscentral.com to work correctly.

Usage:
    python verify_staging_config.py
"""

import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmeats.settings.staging')

import django
django.setup()

from django.conf import settings
from apps.tenants.models import Tenant, TenantDomain


def check_allowed_hosts():
    """Check if staging.meatscentral.com is in ALLOWED_HOSTS."""
    print("=" * 70)
    print("1. Checking ALLOWED_HOSTS configuration...")
    print("=" * 70)
    
    domain = "staging.meatscentral.com"
    allowed_hosts = settings.ALLOWED_HOSTS
    
    print(f"ALLOWED_HOSTS: {allowed_hosts}")
    
    if domain in allowed_hosts or '*' in allowed_hosts:
        print(f"✓ {domain} is allowed")
        return True
    else:
        print(f"✗ {domain} is NOT in ALLOWED_HOSTS")
        print(f"  Add it to STAGING_HOSTS in backend/projectmeats/settings/staging.py")
        return False


def check_tenant_domain():
    """Check if TenantDomain entry exists for staging.meatscentral.com."""
    print("\n" + "=" * 70)
    print("2. Checking TenantDomain entry...")
    print("=" * 70)
    
    domain = "staging.meatscentral.com"
    
    try:
        tenant_domain = TenantDomain.objects.get(domain=domain)
        print(f"✓ TenantDomain entry exists")
        print(f"  Domain: {tenant_domain.domain}")
        print(f"  Tenant: {tenant_domain.tenant.slug} (ID: {tenant_domain.tenant.id})")
        print(f"  Tenant Name: {tenant_domain.tenant.name}")
        print(f"  Tenant Active: {tenant_domain.tenant.is_active}")
        print(f"  Is Primary: {tenant_domain.is_primary}")
        
        if not tenant_domain.tenant.is_active:
            print(f"✗ WARNING: Tenant '{tenant_domain.tenant.slug}' is INACTIVE")
            return False
        
        return True
    except TenantDomain.DoesNotExist:
        print(f"✗ No TenantDomain entry for {domain}")
        print(f"\nTo fix this, run:")
        print(f"  python manage.py add_tenant_domain --domain={domain} --tenant-slug=<TENANT_SLUG>")
        print(f"\nAvailable tenants:")
        
        tenants = Tenant.objects.filter(is_active=True).values_list('slug', 'name')
        for slug, name in tenants:
            print(f"  - {slug}: {name}")
        
        return False


def check_tenant_exists():
    """Check if any active tenants exist."""
    print("\n" + "=" * 70)
    print("3. Checking active tenants...")
    print("=" * 70)
    
    active_tenants = Tenant.objects.filter(is_active=True)
    count = active_tenants.count()
    
    print(f"Active tenants found: {count}")
    
    if count == 0:
        print("✗ No active tenants found")
        print("  You need to create a tenant first using:")
        print("  python manage.py create_tenant --schema-name=... --name=...")
        return False
    
    print("✓ Active tenants:")
    for tenant in active_tenants:
        print(f"  - {tenant.slug}: {tenant.name} (ID: {tenant.id})")
    
    return True


def check_logging_config():
    """Check if logging is configured to capture debug messages."""
    print("\n" + "=" * 70)
    print("4. Checking logging configuration...")
    print("=" * 70)
    
    import logging
    
    # Get the logger used by the middleware
    logger = logging.getLogger('apps.tenants.middleware')
    
    print(f"Logger level: {logging.getLevelName(logger.level)}")
    print(f"Effective level: {logging.getLevelName(logger.getEffectiveLevel())}")
    
    if logger.isEnabledFor(logging.INFO):
        print("✓ INFO logging is enabled (debug logs will be visible)")
        return True
    else:
        print("✗ INFO logging is disabled (debug logs will NOT be visible)")
        print("  Update LOGGING configuration in settings to enable INFO level")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("STAGING.MEATSCENTRAL.COM CONFIGURATION VERIFICATION")
    print("=" * 70)
    print()
    
    results = {
        'ALLOWED_HOSTS': check_allowed_hosts(),
        'Active Tenants': check_tenant_exists(),
        'TenantDomain': check_tenant_domain(),
        'Logging': check_logging_config(),
    }
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n✓ All checks passed! staging.meatscentral.com should work correctly.")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ Error running verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
