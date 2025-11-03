#!/bin/bash
# Environment validation script for deployments
# Validates required environment variables and configuration

set -euo pipefail

echo "=== Environment Validation Script ==="

# Function to check if a variable is set
check_var() {
    local var_name="$1"
    local var_value="${!var_name:-}"
    
    if [ -z "$var_value" ]; then
        echo "❌ ERROR: Required environment variable $var_name is not set"
        return 1
    else
        echo "✅ $var_name is set"
        return 0
    fi
}

# Function to validate URL format
validate_url() {
    local var_name="$1"
    local var_value="${!var_name:-}"
    
    if [[ "$var_value" =~ ^https?:// ]]; then
        echo "✅ $var_name has valid URL format"
        return 0
    else
        echo "❌ ERROR: $var_name does not have valid URL format (must start with http:// or https://)"
        return 1
    fi
}

ERRORS=0

# Required environment variables for Django
echo ""
echo "Checking required Django environment variables..."

check_var "SECRET_KEY" || ERRORS=$((ERRORS + 1))
check_var "DATABASE_URL" || ERRORS=$((ERRORS + 1))
check_var "ALLOWED_HOSTS" || ERRORS=$((ERRORS + 1))

# Check CORS configuration
echo ""
echo "Checking CORS configuration..."
if check_var "CORS_ALLOWED_ORIGINS"; then
    # Validate CORS URLs
    IFS=',' read -ra ORIGINS <<< "$CORS_ALLOWED_ORIGINS"
    for origin in "${ORIGINS[@]}"; do
        origin=$(echo "$origin" | xargs) # trim whitespace
        if [[ ! "$origin" =~ ^https?:// ]]; then
            echo "❌ ERROR: Invalid CORS origin format: $origin"
            ERRORS=$((ERRORS + 1))
        fi
    done
fi

# Check CSRF configuration (should match CORS for consistency)
echo ""
echo "Checking CSRF configuration..."
if check_var "CSRF_TRUSTED_ORIGINS"; then
    # Validate CSRF URLs
    IFS=',' read -ra CSRF_ORIGINS <<< "$CSRF_TRUSTED_ORIGINS"
    for origin in "${CSRF_ORIGINS[@]}"; do
        origin=$(echo "$origin" | xargs) # trim whitespace
        if [[ ! "$origin" =~ ^https?:// ]]; then
            echo "❌ ERROR: Invalid CSRF origin format: $origin"
            ERRORS=$((ERRORS + 1))
        fi
    done
    
    # Warn if CORS and CSRF don't match
    if [ "${CORS_ALLOWED_ORIGINS:-}" != "${CSRF_TRUSTED_ORIGINS:-}" ]; then
        echo "⚠️  WARNING: CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS don't match"
        echo "   CORS: $CORS_ALLOWED_ORIGINS"
        echo "   CSRF: $CSRF_TRUSTED_ORIGINS"
        echo "   This may cause issues with cross-origin requests"
    fi
else
    echo "⚠️  WARNING: CSRF_TRUSTED_ORIGINS not set (may cause 403 errors)"
fi

# Check database configuration
echo ""
echo "Checking database configuration..."
if [ -n "${DATABASE_URL:-}" ]; then
    if [[ "$DATABASE_URL" =~ ^postgresql:// ]]; then
        echo "✅ DATABASE_URL uses PostgreSQL (recommended for production)"
    elif [[ "$DATABASE_URL" =~ ^sqlite:// ]]; then
        echo "⚠️  WARNING: DATABASE_URL uses SQLite (not recommended for production)"
    else
        echo "❌ ERROR: DATABASE_URL has unexpected format"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Check security settings for production
echo ""
echo "Checking security settings..."

if [ "${DEBUG:-False}" = "True" ]; then
    echo "⚠️  WARNING: DEBUG is enabled (should be False in production)"
fi

if [ "${SESSION_COOKIE_SECURE:-False}" = "False" ]; then
    echo "⚠️  WARNING: SESSION_COOKIE_SECURE is False (should be True in production with HTTPS)"
fi

if [ "${CSRF_COOKIE_SECURE:-False}" = "False" ]; then
    echo "⚠️  WARNING: CSRF_COOKIE_SECURE is False (should be True in production with HTTPS)"
fi

# Summary
echo ""
echo "=== Validation Summary ==="
if [ $ERRORS -eq 0 ]; then
    echo "✅ All required environment variables are set and valid"
    exit 0
else
    echo "❌ Found $ERRORS error(s) in environment configuration"
    exit 1
fi
