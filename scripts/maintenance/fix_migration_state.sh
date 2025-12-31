#!/bin/bash
#
# Fix Migration State - Mark existing migrations as applied
#
# This script marks migrations as applied without running them,
# since the tenant_id columns already exist in the database from
# previous migration attempts.

set -e

echo "========================================="
echo "Fixing Migration State"
echo "========================================="

# List of apps with tenant migrations that need to be faked
APPS=(
    "carriers"
    "accounts_receivables"
    "ai_assistant"
    "bug_reports"
    "contacts"
    "customers"
    "invoices"
    "plants"
    "products"
    "purchase_orders"
    "sales_orders"
    "suppliers"
)

echo ""
echo "Step 1: Faking tenant migrations for apps with existing columns..."
for app in "${APPS[@]}"; do
    echo "  - Faking: tenant_apps.$app.0002"
    python manage.py migrate tenant_apps.$app 0002 --fake || echo "    (Already applied or doesn't exist)"
done

echo ""
echo "Step 2: Running any remaining migrations normally..."
python manage.py migrate --noinput

echo ""
echo "✓ Migration state fixed successfully"
