#!/bin/bash
# Fix duplicate tenant_id migrations by faking the 0002 migrations
# This script should be run inside the backend container

set -e

echo "🔧 Fixing duplicate tenant migrations..."
echo "This will mark the 0002 migrations as applied without executing them."
echo ""

# List of apps with 0002 tenant migrations
APPS=(
    "accounts_receivables"
    "ai_assistant"
    "bug_reports"
    "carriers"
    "contacts"
    "customers"
    "invoices"
    "plants"
    "products"
    "purchase_orders"
    "sales_orders"
    "suppliers"
)

echo "📋 Apps to fake migrate:"
for app in "${APPS[@]}"; do
    echo "  - $app"
done
echo ""

# Fake each migration
for app in "${APPS[@]}"; do
    echo "⏩ Faking migration for: $app"
    python manage.py migrate $app 0002 --fake || {
        echo "⚠️  Warning: Could not fake $app (migration might not exist or already applied)"
    }
done

echo ""
echo "✅ Migration fix complete!"
echo ""
echo "Next steps:"
echo "1. Run 'python manage.py showmigrations' to verify"
echo "2. If any new migrations exist, run 'python manage.py migrate' normally"
