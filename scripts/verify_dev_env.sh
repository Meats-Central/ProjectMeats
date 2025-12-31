#!/bin/bash
# Verification script for Dev environment configuration

set -e

echo "=========================================="
echo "Dev Environment Verification"
echo "=========================================="
echo ""

# Check env-config.js
echo "1. Checking runtime config..."
RUNTIME_CONFIG=$(curl -s https://dev.meatscentral.com/env-config.js)
echo "$RUNTIME_CONFIG"

API_URL=$(echo "$RUNTIME_CONFIG" | grep -o 'API_BASE_URL: "[^"]*"' | cut -d'"' -f2)
echo ""
echo "   API_BASE_URL: $API_URL"

if [[ "$API_URL" == "https://dev.meatscentral.com/api/v1" ]]; then
    echo "   ✅ CORRECT: Using unified proxy architecture"
elif [[ "$API_URL" == "https://development.meatscentral.com" ]]; then
    echo "   ❌ WRONG: Still using old hardcoded URL"
    echo "   👉 Deployment hasn't run yet, or secret is not set"
    exit 1
else
    echo "   ⚠️  UNEXPECTED: $API_URL"
    exit 1
fi

echo ""
echo "2. Checking API health..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" https://dev.meatscentral.com/api/v1/health/ || echo "failed")

if echo "$HEALTH_RESPONSE" | tail -1 | grep -q "200"; then
    echo "   ✅ API is reachable and healthy"
else
    echo "   ❌ API health check failed"
    echo "   Response: $HEALTH_RESPONSE"
    exit 1
fi

echo ""
echo "3. Checking CORS headers..."
CORS_TEST=$(curl -s -I -X OPTIONS \
    -H "Origin: https://dev.meatscentral.com" \
    -H "Access-Control-Request-Method: GET" \
    https://dev.meatscentral.com/api/v1/health/ | grep -i "access-control")

if [ -n "$CORS_TEST" ]; then
    echo "   ℹ️  CORS headers present (not needed for same-origin):"
    echo "$CORS_TEST" | sed 's/^/      /'
else
    echo "   ✅ No CORS headers needed (same-origin requests)"
fi

echo ""
echo "=========================================="
echo "✅ All checks passed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test in Incognito mode: https://dev.meatscentral.com"
echo "2. Open DevTools Console (F12)"
echo "3. Try login and supplier creation"
echo "4. Verify NO CORS errors appear"
