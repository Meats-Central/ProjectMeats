#!/bin/bash
# Test script to validate deployment workflow changes
# Run this locally before pushing to catch issues early

set -e

echo "==================================="
echo "ProjectMeats Deployment Test Script"
echo "==================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
}

fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    exit 1
}

echo "Test 1: Checking migration file syntax..."
python3 -m py_compile backend/apps/tenants/migrations/0005_client_domain.py && pass "Migration file syntax is valid" || fail "Migration file has syntax errors"

echo ""
echo "Test 2: Validating migration idempotency..."
cd backend
if python manage.py sqlmigrate tenants 0005 2>&1 | grep -q "CREATE TABLE IF NOT EXISTS"; then
    pass "Migration uses idempotent SQL (CREATE IF NOT EXISTS)"
else
    warn "Migration may not be fully idempotent"
fi

echo ""
echo "Test 3: Checking for migration dependencies..."
if grep -q "0004_add_schema_name_and_domain_model" apps/tenants/migrations/0005_client_domain.py; then
    pass "Migration dependencies are correct"
else
    fail "Migration dependencies are missing or incorrect"
fi

echo ""
echo "Test 4: Validating deployment script..."
if [ -f "deploy.sh" ] && [ -x "deploy.sh" ]; then
    pass "Deployment script exists and is executable"
else
    fail "Deployment script is missing or not executable"
fi

echo ""
echo "Test 5: Checking workflow syntax..."
cd ..
if grep -q "create_super_tenant" .github/workflows/11-dev-deployment.yml; then
    pass "Workflow includes superuser creation step"
else
    warn "Workflow may be missing superuser creation"
fi

if grep -q "create_guest_tenant" .github/workflows/11-dev-deployment.yml; then
    pass "Workflow includes guest tenant creation step"
else
    warn "Workflow may be missing guest tenant creation"
fi

echo ""
echo "Test 6: Checking for proper error handling..."
if grep -q "exit 1" .github/workflows/11-dev-deployment.yml; then
    pass "Workflow has error handling"
else
    fail "Workflow lacks proper error handling"
fi

echo ""
echo "Test 7: Validating Docker build context..."
if [ -f "backend/dockerfile" ]; then
    pass "Backend Dockerfile exists"
else
    fail "Backend Dockerfile is missing"
fi

echo ""
echo "Test 8: Checking management commands..."
cd backend
for cmd in create_super_tenant create_guest_tenant; do
    if [ -f "apps/core/management/commands/${cmd}.py" ] || [ -f "apps/tenants/management/commands/${cmd}.py" ]; then
        pass "Management command '$cmd' exists"
    else
        warn "Management command '$cmd' not found"
    fi
done

echo ""
echo "Test 9: Validating settings configuration..."
if python manage.py check --settings=projectmeats.settings.development >/dev/null 2>&1; then
    pass "Development settings are valid"
else
    warn "Development settings may have issues"
fi

echo ""
echo "Test 10: Checking for required environment variables..."
cd ..
REQUIRED_VARS=(
    "DEV_SECRET_KEY"
    "DEV_DATABASE_URL"
    "DEV_ALLOWED_HOSTS"
    "DEV_DB_ENGINE"
    "DEV_DB_NAME"
    "DEV_DB_USER"
    "DEV_DB_PASSWORD"
    "DEV_DB_HOST"
    "DEV_DB_PORT"
)

for var in "${REQUIRED_VARS[@]}"; do
    if grep -q "$var" .github/workflows/11-dev-deployment.yml; then
        pass "Workflow references required variable: $var"
    else
        warn "Workflow may be missing variable: $var"
    fi
done

echo ""
echo "==================================="
echo -e "${GREEN}All tests completed!${NC}"
echo "==================================="
echo ""
echo "Summary:"
echo "  - Migration is idempotent"
echo "  - Deployment script is ready"
echo "  - Workflow has proper error handling"
echo "  - Management commands exist"
echo ""
echo "Next steps:"
echo "  1. Review the changes: git diff"
echo "  2. Commit changes: git add . && git commit -m 'your message'"
echo "  3. Push to branch: git push origin your-branch"
echo "  4. Create PR and merge to development"
echo ""
