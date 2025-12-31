#!/usr/bin/env python
"""
Tenant Data Backup Script for Master Convergence Migration

This script exports all tenant-related data to JSON format for safe backup
before the django-tenants to shared-schema migration.

Usage:
    python scripts/backup_tenants.py [--output PATH]

The script exports:
- Tenant model instances
- TenantDomain model instances  
- TenantUser model instances
- TenantInvitation model instances

GDPR Compliance:
- No PII is exported (passwords are hashed)
- Email addresses are included as necessary for tenant identification
- Backup files should be stored securely and deleted after verification
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "projectmeats.settings.development")

import django
django.setup()

from django.core import serializers
from apps.tenants.models import Tenant, TenantDomain, TenantUser, TenantInvitation


def backup_tenant_data(output_path=None):
    """
    Backup all tenant-related data to JSON format.
    
    Args:
        output_path: Optional custom output path for backup file
        
    Returns:
        Path to the created backup file
    """
    # Determine output path
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backups_dir = backend_dir.parent / "backups"
        backups_dir.mkdir(exist_ok=True)
        output_path = backups_dir / f"tenants_backup_{timestamp}.json"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Starting tenant data backup...")
    print(f"Output: {output_path}")
    print("-" * 70)
    
    # Collect all tenant-related objects
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "description": "Tenant data backup for Master Convergence migration",
        "models": {}
    }
    
    # Export Tenant model
    tenants = Tenant.objects.all()
    tenant_count = tenants.count()
    if tenant_count > 0:
        backup_data["models"]["tenants.Tenant"] = json.loads(
            serializers.serialize("json", tenants)
        )
        print(f"✓ Exported {tenant_count} Tenant records")
    else:
        print("⚠ No Tenant records found")
    
    # Export TenantDomain model
    domains = TenantDomain.objects.all()
    domain_count = domains.count()
    if domain_count > 0:
        backup_data["models"]["tenants.TenantDomain"] = json.loads(
            serializers.serialize("json", domains)
        )
        print(f"✓ Exported {domain_count} TenantDomain records")
    else:
        print("⚠ No TenantDomain records found")
    
    # Export TenantUser model
    tenant_users = TenantUser.objects.all()
    tenant_user_count = tenant_users.count()
    if tenant_user_count > 0:
        backup_data["models"]["tenants.TenantUser"] = json.loads(
            serializers.serialize("json", tenant_users)
        )
        print(f"✓ Exported {tenant_user_count} TenantUser records")
    else:
        print("⚠ No TenantUser records found")
    
    # Export TenantInvitation model
    invitations = TenantInvitation.objects.all()
    invitation_count = invitations.count()
    if invitation_count > 0:
        backup_data["models"]["tenants.TenantInvitation"] = json.loads(
            serializers.serialize("json", invitations)
        )
        print(f"✓ Exported {invitation_count} TenantInvitation records")
    else:
        print("⚠ No TenantInvitation records found")
    
    # Write backup to file
    with open(output_path, "w") as f:
        json.dump(backup_data, f, indent=2)
    
    print("-" * 70)
    print(f"✓ Backup completed successfully")
    print(f"✓ File: {output_path}")
    print(f"✓ Size: {output_path.stat().st_size:,} bytes")
    
    # Verify backup integrity
    with open(output_path, "r") as f:
        verify_data = json.load(f)
        total_records = sum(
            len(records) for records in verify_data["models"].values()
        )
        print(f"✓ Verified {total_records} total records in backup")
    
    return str(output_path)


def main():
    """Main entry point for backup script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Backup tenant data for Master Convergence migration"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output path for backup file (default: backups/tenants_backup_TIMESTAMP.json)"
    )
    
    args = parser.parse_args()
    
    try:
        backup_path = backup_tenant_data(args.output)
        print("\n" + "=" * 70)
        print("BACKUP SUCCESSFUL")
        print("=" * 70)
        print(f"\nBackup file: {backup_path}")
        print("\nNext steps:")
        print("1. Verify backup file exists and is not empty")
        print("2. Store backup in secure location (e.g., GitHub Releases)")
        print("3. Add backup file to .gitignore if not already excluded")
        print("4. Proceed with Phase 1: Backend Purge")
        return 0
    except Exception as e:
        print(f"\n❌ ERROR: Backup failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
