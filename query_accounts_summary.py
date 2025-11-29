#!/usr/bin/env python3
"""
Quick script to query UAT or Production accounts via GitHub Actions API
This uses the GitHub CLI to trigger a workflow and get results
"""

import argparse
import subprocess
import sys

QUERY_SCRIPT = """
from django.contrib.auth.models import User
from apps.tenants.models import Tenant, TenantUser

print("\\n=== SUMMARY ===")
print(f"Superusers: {User.objects.filter(is_superuser=True).count()}")
print(f"Total Users: {User.objects.count()}")
print(f"Tenants: {Tenant.objects.count()}")
print(f"Tenant-User Links: {TenantUser.objects.count()}")

print("\\n=== SUPERUSERS ===")
for user in User.objects.filter(is_superuser=True):
    print(f"- {user.username} ({user.email}) - Active: {user.is_active}")

print("\\n=== TENANTS ===")
for tenant in Tenant.objects.all():
    print(f"- {tenant.slug}: {tenant.name} - Active: {tenant.is_active}")

print("\\n=== LINKS ===")
for tu in TenantUser.objects.select_related('tenant', 'user').all():
    print(f"- {tu.user.username} -> {tu.tenant.slug} ({tu.role})")
"""

def main():
    parser = argparse.ArgumentParser(description='Query remote database accounts')
    parser.add_argument('environment', choices=['uat', 'production', 'dev'],
                       help='Environment to query')
    args = parser.parse_args()
    
    if args.environment == 'dev':
        # Query local development database
        print("Querying local development database...")
        print("="*70)
        
        # Use manage.py shell
        import subprocess
        result = subprocess.run(
            ['python', 'manage.py', 'shell', '-c', QUERY_SCRIPT],
            cwd='backend',
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr, file=sys.stderr)
        
    else:
        print(f"To query {args.environment}, you need to:")
        print(f"1. SSH into the {args.environment} server")
        print(f"2. Run: sudo docker exec pm-backend python manage.py shell -c '<query>'")
        print(f"\nOr use the query_remote_accounts.sh script:")
        print(f"   ./query_remote_accounts.sh {args.environment}")
        print(f"\nMake sure to set these environment variables first:")
        if args.environment == 'uat':
            print("   export STAGING_HOST='your-uat-host'")
            print("   export STAGING_USER='django'")
            print("   export SSH_PASSWORD='your-password'")
        else:
            print("   export PRODUCTION_HOST='your-prod-host'")
            print("   export PRODUCTION_USER='django'")
            print("   export SSH_PASSWORD='your-password'")

if __name__ == '__main__':
    main()
