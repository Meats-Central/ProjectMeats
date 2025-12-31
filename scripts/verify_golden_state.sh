#!/bin/bash
# scripts/verify_golden_state.sh
# Verifies the Golden Pipeline implementation

echo "🔍 Verifying Golden Pipeline State..."
echo ""

ERRORS=0

# 1. Check manifest exists
if [ -f "config/env.manifest.json" ]; then
    echo "✅ config/env.manifest.json exists"
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

# 3. Check workflow has bastion tunnel (in reusable-deploy.yml)
if grep -q "ssh.*5433" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ reusable-deploy.yml uses SSH tunnel (port 5433)"
else
    echo "❌ reusable-deploy.yml missing SSH tunnel"
    ERRORS=$((ERRORS + 1))
fi

# 4. Check workflow uses --network host
if grep -q "\\-\\-network host" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ reusable-deploy.yml uses Docker host networking"
else
    echo "❌ reusable-deploy.yml missing --network host"
    ERRORS=$((ERRORS + 1))
fi

# 5. Check frontend health check
if grep -q "8080" .github/workflows/reusable-deploy.yml 2>/dev/null; then
    echo "✅ reusable-deploy.yml checks frontend container directly"
else
    echo "❌ reusable-deploy.yml frontend check incorrect"
    ERRORS=$((ERRORS + 1))
fi

# 6. Check for prohibited patterns
if grep -q "django-tenants" backend/requirements.txt 2>/dev/null; then
    echo "❌ CRITICAL: django-tenants found in requirements.txt"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No django-tenants in requirements.txt"
fi

# 7. Check documentation exists
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

# 8. Check for archived documentation references
if grep -rq "docs/archive/" .github/workflows/*.yml 2>/dev/null; then
    echo "⚠️  WARNING: Workflows reference archived documentation"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ No references to archived docs in workflows"
fi

# 9. Check workflow naming conventions
if grep -q "run-name:" .github/workflows/main-pipeline.yml 2>/dev/null; then
    echo "✅ main-pipeline.yml has dynamic run-name"
else
    echo "❌ main-pipeline.yml missing dynamic run-name"
    ERRORS=$((ERRORS + 1))
fi

echo ""
echo "────────────────────────────────────"
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! Golden Pipeline verified."
    exit 0
else
    echo "❌ $ERRORS check(s) failed. Review errors above."
    exit 1
fi
