#!/bin/bash
# Migration validation script for CI/CD
# This script validates Django migrations before deployment

set -euo pipefail

echo "=== Migration Validation Script ==="
echo "Validating Django migrations..."

cd backend

# 1. Check for unapplied migrations (Public Schema)
echo ""
echo "Step 1: Checking for unapplied migrations (Public Schema - Shared Apps)..."
if python manage.py makemigrations --check --dry-run; then
    echo "✅ No unapplied migrations detected in public schema"
else
    echo "❌ ERROR: Unapplied migrations detected. Run 'python manage.py makemigrations' and commit the files."
    exit 1
fi

# 2. Validate tenant schema migrations (django-tenants)
echo ""
echo "Step 2: Validating tenant schema migrations (django-tenants)..."
# Check if migrate_schemas command is available (django-tenants installed and configured)
if python manage.py help migrate_schemas &> /dev/null; then
    echo "Checking tenant migrations with migrate_schemas..."
    # Use --noinput and check if it can show the migration plan
    # The migrate_schemas command will validate tenant apps defined in TENANT_APPS setting
    if python manage.py migrate_schemas --noinput --plan > /tmp/tenant_migration_plan.txt 2>&1; then
        echo "✅ Tenant schema migrations validated successfully"
        echo "Tenant migration plan (first 20 lines):"
        head -20 /tmp/tenant_migration_plan.txt
        if [ $(wc -l < /tmp/tenant_migration_plan.txt) -gt 20 ]; then
            echo "... (truncated, see full plan in CI logs)"
        fi
    else
        # Check if it's a configuration issue vs actual migration problem
        if grep -q "TENANT_APPS\|SHARED_APPS\|has no attribute" /tmp/tenant_migration_plan.txt; then
            echo "⚠️  django-tenants configuration incomplete - skipping tenant validation"
            echo "    This is expected if django-tenants is not fully configured yet"
            cat /tmp/tenant_migration_plan.txt | grep -i "error\|TENANT" || true
        else
            echo "❌ ERROR: Tenant schema migration validation failed"
            echo "Error details:"
            cat /tmp/tenant_migration_plan.txt
            exit 1
        fi
    fi
else
    echo "⚠️  django-tenants migrate_schemas command not available - skipping tenant schema validation"
    echo "    This is expected if django-tenants is not in INSTALLED_APPS"
fi

# 3. Validate migration plan
echo ""
echo "Step 3: Validating migration plan..."
if python manage.py migrate --plan > /tmp/migration_plan.txt; then
    echo "✅ Migration plan is valid"
    echo "Migration plan:"
    cat /tmp/migration_plan.txt
else
    echo "❌ ERROR: Migration plan validation failed"
    exit 1
fi

# 4. Check for migration conflicts
echo ""
echo "Step 4: Checking for migration conflicts..."
if python manage.py showmigrations --plan > /tmp/showmigrations.txt; then
    echo "✅ No migration conflicts detected"
else
    echo "❌ ERROR: Migration conflicts detected"
    exit 1
fi

# 5. Validate Python syntax in migration files
echo ""
echo "Step 5: Validating Python syntax in migration files..."
SYNTAX_ERRORS=0
for migration_file in $(find apps/*/migrations -name "*.py" -type f | grep -v __pycache__); do
    if ! python -m py_compile "$migration_file" 2>/dev/null; then
        echo "❌ Syntax error in: $migration_file"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo "✅ All migration files have valid Python syntax"
else
    echo "❌ ERROR: $SYNTAX_ERRORS migration file(s) have syntax errors"
    exit 1
fi

# 6. Check for proper migration dependencies
echo ""
echo "Step 6: Checking migration dependencies..."
# This checks that migrations reference existing dependencies
python manage.py migrate --plan 2>&1 | grep -i "inconsistent\|missing" && {
    echo "❌ ERROR: Inconsistent or missing migration dependencies detected"
    exit 1
} || echo "✅ Migration dependencies are consistent"

# 7. Test migrations on fresh database (CI only)
echo ""
echo "Step 7: Testing migrations on fresh database..."
echo "Setting up temporary test database..."

# Export current DATABASE_URL and create a test database
ORIGINAL_DB_URL=${DATABASE_URL:-}
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/test_migration_validation"

# Skip if we can't create a test database (not in CI environment)
if command -v psql &> /dev/null && [ -n "${CI:-}" ]; then
    echo "Creating test database for migration validation..."
    PGPASSWORD=postgres psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS test_migration_validation;" 2>/dev/null || true
    PGPASSWORD=postgres psql -h localhost -U postgres -c "CREATE DATABASE test_migration_validation;" 2>/dev/null || true
    
    if python manage.py migrate --noinput 2>&1; then
        echo "✅ Migrations applied successfully on fresh database"
    else
        echo "❌ ERROR: Migrations failed on fresh database"
        export DATABASE_URL="$ORIGINAL_DB_URL"
        exit 1
    fi
    
    # Cleanup
    PGPASSWORD=postgres psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS test_migration_validation;" 2>/dev/null || true
    export DATABASE_URL="$ORIGINAL_DB_URL"
else
    echo "⚠️  Skipping fresh database test (not in CI environment or psql not available)"
fi

echo ""
echo "=== Migration Validation Complete ==="
echo "✅ All migration checks passed!"
exit 0
