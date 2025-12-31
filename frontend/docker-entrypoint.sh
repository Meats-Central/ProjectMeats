#!/bin/bash
set -e

echo "=== Frontend Container Entrypoint ==="
echo "Environment: ${ENVIRONMENT:-development}"

# Check if SSL certificates exist
SSL_CERT="/etc/nginx/ssl/fullchain.pem"
SSL_KEY="/etc/nginx/ssl/privkey.pem"
HAS_SSL=false

if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
    echo "✓ SSL certificates found"
    HAS_SSL=true
else
    echo "ℹ SSL certificates not found (dev environment)"
    HAS_SSL=false
fi

# Clear any existing configs in conf.d to ensure a clean slate
echo "→ Cleaning existing nginx configs"
rm -f /etc/nginx/conf.d/*.conf

# Choose nginx config based on SSL availability
if [ "$HAS_SSL" = true ] && [ -f "/etc/nginx/templates/frontend-ssl.conf" ]; then
    echo "→ Using SSL-enabled configuration"
    cp /etc/nginx/templates/frontend-ssl.conf /etc/nginx/conf.d/default.conf
elif [ -f "/etc/nginx/templates/frontend-http.conf" ]; then
    echo "→ Using HTTP-only configuration"
    cp /etc/nginx/templates/frontend-http.conf /etc/nginx/conf.d/default.conf
else
    echo "✗ No valid configuration template found!"
    exit 1
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
    echo "Configuration files:"
    echo "===================="
    echo "Main config: /etc/nginx/nginx.conf"
    echo "Default config: /etc/nginx/conf.d/default.conf"
    echo ""
    echo "Content of /etc/nginx/conf.d/default.conf:"
    cat /etc/nginx/conf.d/default.conf
    exit 1
fi

echo "=== Starting nginx ==="
echo "Nginx will listen on ports 80 and 443"
exec nginx -g 'daemon off;'
