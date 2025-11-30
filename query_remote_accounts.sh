#!/bin/bash
# Query UAT or Production accounts remotely
# Usage: ./query_remote_accounts.sh [uat|production]

set -e

ENVIRONMENT="${1:-uat}"

if [ "$ENVIRONMENT" != "uat" ] && [ "$ENVIRONMENT" != "production" ]; then
    echo "Usage: $0 [uat|production]"
    exit 1
fi

echo "=========================================="
echo "Querying $ENVIRONMENT database accounts"
echo "=========================================="
echo ""

# Note: You need to set these environment variables first:
# export STAGING_HOST="your-uat-host"
# export STAGING_USER="your-ssh-user"
# export SSH_PASSWORD="your-ssh-password"
# OR
# export PRODUCTION_HOST="your-prod-host"
# export PRODUCTION_USER="your-ssh-user"
# export SSH_PASSWORD="your-ssh-password"

if [ "$ENVIRONMENT" = "uat" ]; then
    if [ -z "$STAGING_HOST" ] || [ -z "$STAGING_USER" ]; then
        echo "ERROR: Please set STAGING_HOST and STAGING_USER environment variables"
        echo "Example:"
        echo "  export STAGING_HOST='your-uat-host.com'"
        echo "  export STAGING_USER='django'"
        echo "  export SSH_PASSWORD='your-password'"
        exit 1
    fi
    
    SSH_HOST="$STAGING_HOST"
    SSH_USER="$STAGING_USER"
else
    if [ -z "$PRODUCTION_HOST" ] || [ -z "$PRODUCTION_USER" ]; then
        echo "ERROR: Please set PRODUCTION_HOST and PRODUCTION_USER environment variables"
        echo "Example:"
        echo "  export PRODUCTION_HOST='your-prod-host.com'"
        echo "  export PRODUCTION_USER='django'"
        echo "  export SSH_PASSWORD='your-password'"
        exit 1
    fi
    
    SSH_HOST="$PRODUCTION_HOST"
    SSH_USER="$PRODUCTION_USER"
fi

echo "Connecting to $SSH_HOST as $SSH_USER..."
echo ""

# The query to run on the remote server
QUERY_SCRIPT='
from django.contrib.auth.models import User
from apps.tenants.models import Tenant, TenantUser

print("\n" + "="*70)
print("SUPERUSERS / ADMIN ACCOUNTS")
print("="*70)
superusers = User.objects.filter(is_superuser=True)
for user in superusers:
    print(f"\n👤 User ID: {user.id}")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Is Superuser: {user.is_superuser}")
    print(f"   Is Staff: {user.is_staff}")
    print(f"   Is Active: {user.is_active}")
    print(f"   Date Joined: {user.date_joined}")

print(f"\n📊 Total Superusers: {superusers.count()}")

print("\n" + "="*70)
print("TENANTS (SUPER TENANT)")
print("="*70)
tenants = Tenant.objects.all()
for tenant in tenants:
    print(f"\n🏢 Tenant ID: {tenant.id}")
    print(f"   Name: {tenant.name}")
    print(f"   Slug: {tenant.slug}")
    print(f"   Is Active: {tenant.is_active}")
    print(f"   Is Trial: {tenant.is_trial}")
    print(f"   Contact Email: {tenant.contact_email}")
    print(f"   Created By: {tenant.created_by.username if tenant.created_by else \"N/A\"}")
    print(f"   Created At: {tenant.created_at}")

print(f"\n📊 Total Tenants: {tenants.count()}")

print("\n" + "="*70)
print("TENANT-USER RELATIONSHIPS")
print("="*70)
tenant_users = TenantUser.objects.all().select_related("tenant", "user")
for tu in tenant_users:
    print(f"\n🔗 Link ID: {tu.id}")
    print(f"   Tenant: {tu.tenant.slug} ({tu.tenant.name})")
    print(f"   User: {tu.user.username} ({tu.user.email})")
    print(f"   Role: {tu.role}")
    print(f"   Is Active: {tu.is_active}")
    print(f"   Created At: {tu.created_at}")

print(f"\n📊 Total Links: {tenant_users.count()}")
print("\n" + "="*70)
'

# Execute the query on remote server
if [ -n "$SSH_PASSWORD" ]; then
    echo "Using password authentication..."
    sshpass -e ssh -o StrictHostKeyChecking=yes "$SSH_USER@$SSH_HOST" \
        "sudo docker exec pm-backend python manage.py shell -c '$QUERY_SCRIPT'"
else
    echo "Using SSH key authentication..."
    ssh -o StrictHostKeyChecking=yes "$SSH_USER@$SSH_HOST" \
        "sudo docker exec pm-backend python manage.py shell -c '$QUERY_SCRIPT'"
fi

echo ""
echo "Query completed successfully!"
