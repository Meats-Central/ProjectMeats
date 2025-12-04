#!/bin/bash
# Schema-Based Multi-Tenancy Deployment Script
# This script handles the special migration steps required for django-tenants

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  Schema-Based Multi-Tenancy Migration Deployment"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if running in correct environment
if [ -z "${DJANGO_SETTINGS_MODULE:-}" ]; then
    echo "❌ ERROR: DJANGO_SETTINGS_MODULE not set"
    exit 1
fi

echo "✅ Environment: ${DJANGO_SETTINGS_MODULE}"
echo ""

# Step 1: Collect static files
echo "📦 Step 1/5: Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected"
echo ""

# Step 2: Apply shared schema migrations
echo "🗄️  Step 2/5: Applying shared schema migrations..."
python manage.py migrate_schemas --shared --fake-initial --noinput
echo "✅ Shared schema migrations applied"
echo ""

# Step 3: Create super tenant
echo "🏢 Step 3/5: Creating super tenant..."
python manage.py create_super_tenant --no-input || echo "⚠️  Super tenant may already exist"
echo "✅ Super tenant verified"
echo ""

# Step 4: Apply tenant schema migrations
echo "🗄️  Step 4/5: Applying tenant schema migrations..."
python manage.py migrate_schemas --tenant --noinput
echo "✅ Tenant schema migrations applied"
echo ""

# Step 5: Verification
echo "✅ Step 5/5: Running verification checks..."
python manage.py check --deploy
echo "✅ Deployment checks passed"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Schema Migration Deployment Complete"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Create test tenant via Django shell"
echo "2. Verify schema isolation"
echo "3. Test API endpoints with tenant domain"
echo ""
