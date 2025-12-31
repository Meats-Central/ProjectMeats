#!/usr/bin/env python3
"""
Seed Script Stub for ProjectMeats Development Data

This is a NON-EXECUTING stub that documents the expected seed data structure.
Actual seed implementation should be done via Django fixtures or management commands.

Usage (when implemented):
    python manage.py seed_data --environment=development
    python manage.py seed_data --environment=test

WARNING: This script is intentionally a stub and does not execute any database operations.
"""

import sys


def main():
    """
    Seed data stub - does not execute any database operations.
    
    Expected seed data structure:
    
    1. Tenants:
       - Default tenant for development
       - Test tenant for automated testing
    
    2. Users:
       - Admin user (superuser)
       - Regular user per tenant
       - Guest user for demo access
    
    3. Business Data (per tenant):
       - Sample suppliers (3-5)
       - Sample customers (5-10)
       - Sample contacts linked to suppliers/customers
       - Sample purchase orders (10-20)
       - Sample products (10-15)
    
    Implementation Notes:
    - Use Django management commands for actual seeding
    - See: backend/apps/tenants/management/commands/
    - Fixtures should be in: backend/fixtures/
    """
    print("=" * 60)
    print("SEED SCRIPT STUB - NO DATABASE OPERATIONS PERFORMED")
    print("=" * 60)
    print()
    print("This is a documentation stub for development seed data.")
    print("To implement actual seeding, create Django management commands:")
    print()
    print("  python manage.py seed_development_data")
    print("  python manage.py seed_test_data")
    print()
    print("Or use Django fixtures:")
    print()
    print("  python manage.py loaddata backend/fixtures/development.json")
    print()
    print("See scripts/seed_data.py for expected data structure.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
