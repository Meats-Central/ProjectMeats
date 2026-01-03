#!/bin/bash
set -e

echo "=== Frontend Container Entrypoint ==="
echo "Environment: ${ENVIRONMENT:-development}"
echo "Domain: ${DOMAIN_NAME:-localhost}"
echo "Backend Host: ${BACKEND_HOST:-backend}"

# Set defaults if not provided
export BACKEND_HOST="${BACKEND_HOST:-backend}"
export DOMAIN_NAME="${DOMAIN_NAME:-localhost}"

# Check if SSL certificates exist for this domain
SSL_CERT="/etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem"
SSL_KEY="/etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem"

echo "→ Checking for SSL certificates at:"
echo "   Certificate: $SSL_CERT"
echo "   Key: $SSL_KEY"

if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
    echo "✓ SSL certificates found for ${DOMAIN_NAME}"
    USE_SSL=true
else
    echo "ℹ SSL certificates not found (using HTTP-only configuration)"
    USE_SSL=false
fi

# Clear any existing configs in conf.d to ensure a clean slate
echo "→ Cleaning existing nginx configs"
rm -f /etc/nginx/conf.d/*.conf

echo "→ Using backend host: $BACKEND_HOST"
echo "→ Using domain: $DOMAIN_NAME"

# Choose nginx config based on SSL availability and substitute variables
if [ "$USE_SSL" = true ]; then
    if [ ! -f "/etc/nginx/templates/frontend-ssl.conf" ]; then
        echo "✗ SSL template not found at /etc/nginx/templates/frontend-ssl.conf"
        exit 1
    fi
    
    echo "→ Using SSL-enabled configuration (frontend-ssl.conf)"
    echo "→ Substituting environment variables: \${BACKEND_HOST} and \${DOMAIN_NAME}"
    envsubst '${BACKEND_HOST} ${DOMAIN_NAME}' < /etc/nginx/templates/frontend-ssl.conf > /etc/nginx/conf.d/default.conf
else
    if [ ! -f "/etc/nginx/templates/frontend-http.conf" ]; then
        echo "✗ HTTP template not found at /etc/nginx/templates/frontend-http.conf"
        exit 1
    fi
    
    echo "→ Using HTTP-only configuration (frontend-http.conf)"
    echo "→ Substituting environment variables: \${BACKEND_HOST}"
    envsubst '${BACKEND_HOST}' < /etc/nginx/templates/frontend-http.conf > /etc/nginx/conf.d/default.conf
fi

echo "=== Validating nginx configuration ==="
# Test nginx configuration before starting
if nginx -t 2>&1; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration validation failed!"
    echo ""
    echo "Nginx test output:"
    nginx -t 2>&1 || true
    echo ""
    echo "Configuration details:"
    echo "===================="
    echo "Main config: /etc/nginx/nginx.conf"
    echo "Active config: /etc/nginx/conf.d/default.conf"
    echo ""
    echo "Content of /etc/nginx/conf.d/default.conf:"
    cat /etc/nginx/conf.d/default.conf
    exit 1
fi

echo "=== Starting nginx ==="
if [ "$USE_SSL" = true ]; then
    echo "Nginx listening on ports 80 (redirect) and 443 (SSL)"
    echo "Domain: ${DOMAIN_NAME}"
else
    echo "Nginx listening on port 80 (HTTP only)"
fi
echo "Backend proxied to: ${BACKEND_HOST}:8000"

exec nginx -g 'daemon off;'
