#!/usr/bin/env python
"""
Fix Dev Domain Mapping
======================
Maps dev-backend.meatscentral.com to the root tenant to resolve 403 Forbidden errors.

Usage:
    # Inside container:
    python /app/scripts/fix_dev_domain.py

    # Or via docker exec:
    docker exec pm-backend python /app/scripts/fix_dev_domain.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/app/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projectmeats.settings.development')

try:
    django.setup()
except Exception as e:
    print(f"❌ Failed to setup Django: {e}")
    sys.exit(1)

from apps.tenants.models import Tenant, TenantDomain


def fix_domain():
    """
    Map dev-backend.meatscentral.com to root tenant.
    
    This fixes 403 Forbidden errors caused by TenantMiddleware
    not being able to resolve a tenant from the subdomain.
    """
    print("=" * 60)
    print("Fixing Dev Domain Mapping")
    print("=" * 60)
    print()
    
    try:
        # 1. Get the Root Tenant
        print("Step 1: Looking for root tenant...")
        root_tenant = Tenant.objects.get(slug='root')
        print(f"✅ Found Root Tenant:")
        print(f"   ID: {root_tenant.id}")
        print(f"   Name: {root_tenant.name}")
        print(f"   Slug: {root_tenant.slug}")
        print()

        # 2. Create/Update Domain Mapping
        print("Step 2: Creating domain mapping...")
        domain = "dev-backend.meatscentral.com"
        
        obj, created = TenantDomain.objects.update_or_create(
            domain=domain,
            defaults={
                'tenant': root_tenant,
                'is_primary': True
            }
        )
        
        if created:
            print(f"✅ Created new domain mapping:")
        else:
            print(f"✅ Updated existing domain mapping:")
        
        print(f"   Domain: {obj.domain}")
        print(f"   Tenant: {obj.tenant.name} (slug: {obj.tenant.slug})")
        print(f"   Primary: {obj.is_primary}")
        print()

        # 3. Verify mapping
        print("Step 3: Verifying mapping...")
        verification = TenantDomain.objects.get(domain=domain)
        if verification.tenant == root_tenant:
            print("✅ Mapping verified successfully!")
            print()
            print("=" * 60)
            print("Domain mapping complete!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Restart the backend container")
            print("2. Try accessing dev-backend.meatscentral.com")
            print("3. 403 errors should be resolved")
            return 0
        else:
            print("❌ Verification failed: Mapping doesn't match")
            return 1

    except Tenant.DoesNotExist:
        print("❌ Error: Root tenant not found!")
        print()
        print("The 'root' tenant must exist before domain mapping.")
        print()
        print("To create the root tenant, run:")
        print("  python manage.py create_super_tenant")
        print()
        return 1
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def show_current_mappings():
    """Display all current domain mappings for debugging."""
    print()
    print("=" * 60)
    print("Current Domain Mappings")
    print("=" * 60)
    
    try:
        mappings = TenantDomain.objects.select_related('tenant').all()
        
        if not mappings:
            print("No domain mappings found.")
        else:
            for mapping in mappings:
                print(f"  {mapping.domain} → {mapping.tenant.name} "
                      f"(slug: {mapping.tenant.slug}, primary: {mapping.is_primary})")
        
        print("=" * 60)
        print()
    except Exception as e:
        print(f"Could not fetch mappings: {e}")


if __name__ == "__main__":
    # Show current state
    show_current_mappings()
    
    # Apply fix
    exit_code = fix_domain()
    
    # Show new state
    if exit_code == 0:
        show_current_mappings()
    
    sys.exit(exit_code)
