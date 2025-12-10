#!/bin/bash
# scripts/verify_golden_state.sh
# Verifies the Golden Pipeline implementation

set -e

echo "🔍 Verifying Golden Pipeline State..."
echo ""

ERRORS=0

# 1. Check manifest exists
if [ -f "config/env.manifest.json" ]; then
    VERSION=$(jq -r '.version' config/env.manifest.json 2>/dev/null || echo "unknown")
    echo "✅ config/env.manifest.json exists (version: $VERSION)"
else
    echo "❌ config/env.manifest.json NOT FOUND"
    ERRORS=$((ERRORS + 1))
fi

# 2. Check manage_env.py supports audit
if grep -q "def audit_secrets" config/manage_env.py 2>/dev/null; then
    echo "✅ manage_env.py has audit_secrets method"
else
    echo "❌ manage_env.py missing audit_secrets"
    ERRORS=$((ERRORS + 1))
fi

# 3. Check workflow has bastion tunnel
if grep -q -- "-L 5433" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ reusable-deploy.yml uses SSH tunnel (port 5433)"
else
    echo "❌ reusable-deploy.yml missing SSH tunnel"
    ERRORS=$((ERRORS + 1))
fi

# 4. Check workflow uses --network host
if grep -q -- "--network host" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ reusable-deploy.yml uses Docker host networking"
else
    echo "❌ reusable-deploy.yml missing --network host"
    ERRORS=$((ERRORS + 1))
fi

# 5. Check frontend health check
if grep -q "127.0.0.1:8080" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ reusable-deploy.yml checks frontend container directly"
else
    echo "❌ reusable-deploy.yml frontend check incorrect"
    ERRORS=$((ERRORS + 1))
fi

# 6. Check for prohibited patterns
if grep "^django-tenants" backend/requirements.txt 2>/dev/null | grep -v "^#" >/dev/null; then
    echo "❌ CRITICAL: django-tenants found in requirements.txt"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No django-tenants in requirements.txt"
fi

# 7. Check retry count is 5
if grep -q "MAX_ATTEMPTS=5" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ Health check retries set to 5"
else
    echo "⚠️  Warning: MAX_ATTEMPTS may not be set to 5"
fi

# 8. Check documentation exists
if [ -f "docs/GOLDEN_PIPELINE.md" ]; then
    echo "✅ docs/GOLDEN_PIPELINE.md exists"
else
    echo "❌ docs/GOLDEN_PIPELINE.md NOT FOUND"
    ERRORS=$((ERRORS + 1))
fi

if [ -f "docs/CONFIGURATION_AND_SECRETS.md" ]; then
    echo "✅ docs/CONFIGURATION_AND_SECRETS.md exists"
else
    echo "❌ docs/CONFIGURATION_AND_SECRETS.md NOT FOUND"
    ERRORS=$((ERRORS + 1))
fi

# 9. Check for migrate --fake-initial
if grep -q "migrate --fake-initial" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ Migrations use --fake-initial flag"
else
    echo "❌ Migrations missing --fake-initial flag"
    ERRORS=$((ERRORS + 1))
fi

# 10. Check DATABASE_URL points to tunnel
if grep -q "127.0.0.1:5433" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ DATABASE_URL configured for tunnel"
else
    echo "❌ DATABASE_URL not pointing to tunnel port"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "────────────────────────────────────"
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! Golden Pipeline verified."
    exit 0
else
    echo "❌ $ERRORS check(s) failed. Review errors above."
    echo ""
    echo "For details, see:"
    echo "  docs/GOLDEN_PIPELINE.md"
    echo "  docs/CONFIGURATION_AND_SECRETS.md"
    exit 1
fi
