#!/bin/bash
# Host Infrastructure Setup Script
# 
# Purpose: Install and configure host-level reverse proxy for ProjectMeats
# This script should be run ONCE per environment (dev/uat/prod) on the host server
#
# Usage: 
#   sudo ./setup-host-infrastructure.sh dev dev.meatscentral.com 127.0.0.1
#   sudo ./setup-host-infrastructure.sh uat uat.meatscentral.com 127.0.0.1
#   sudo ./setup-host-infrastructure.sh production meatscentral.com 127.0.0.1

set -euo pipefail

# Configuration
ENVIRONMENT="${1:-}"
DOMAIN_NAME="${2:-}"
BACKEND_HOST="${3:-127.0.0.1}"
CERTBOT_EMAIL="${4:-admin@meatscentral.com}"

# Validation
if [ -z "$ENVIRONMENT" ] || [ -z "$DOMAIN_NAME" ]; then
    echo "❌ Usage: $0 <environment> <domain> [backend_host] [certbot_email]"
    echo ""
    echo "Examples:"
    echo "  $0 dev dev.meatscentral.com 127.0.0.1"
    echo "  $0 uat uat.meatscentral.com 127.0.0.1"
    echo "  $0 production meatscentral.com 127.0.0.1"
    exit 1
fi

if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "========================================="
echo "ProjectMeats Host Infrastructure Setup"
echo "========================================="
echo "Environment: $ENVIRONMENT"
echo "Domain: $DOMAIN_NAME"
echo "Backend Host: $BACKEND_HOST"
echo "Certbot Email: $CERTBOT_EMAIL"
echo ""

# Step 1: Install required packages
echo "→ Installing required packages..."
apt-get update -qq
apt-get install -y nginx certbot python3-certbot-nginx curl

# Step 2: Create webroot for certbot
echo "→ Creating certbot webroot..."
mkdir -p /var/www/certbot
chown -R www-data:www-data /var/www/certbot

# Step 3: Create temporary HTTP-only config for initial SSL certificate
echo "→ Creating temporary HTTP-only nginx config..."
cat > /etc/nginx/sites-available/projectmeats-$ENVIRONMENT << EOF
# Temporary HTTP-only config for initial SSL certificate acquisition
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN_NAME;
    
    # Allow Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        allow all;
    }
    
    # Temporary: Allow all traffic during setup
    location / {
        return 200 "ProjectMeats infrastructure setup in progress...\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Step 4: Enable site and test nginx config
echo "→ Enabling site..."
ln -sf /etc/nginx/sites-available/projectmeats-$ENVIRONMENT /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default config to avoid conflicts

echo "→ Testing nginx configuration..."
nginx -t

echo "→ Restarting nginx..."
systemctl restart nginx

# Step 5: Obtain SSL certificate
echo "→ Obtaining SSL certificate from Let's Encrypt..."
echo "   This may take a few minutes..."

if [ -d "/etc/letsencrypt/live/$DOMAIN_NAME" ]; then
    echo "✓ SSL certificate already exists for $DOMAIN_NAME"
    echo "   Skipping certificate acquisition"
else
    certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$CERTBOT_EMAIL" \
        --agree-tos \
        --no-eff-email \
        --non-interactive \
        -d "$DOMAIN_NAME"
    
    if [ $? -eq 0 ]; then
        echo "✓ SSL certificate obtained successfully"
    else
        echo "❌ Failed to obtain SSL certificate"
        echo "   Check that:"
        echo "   1. DNS is properly configured ($DOMAIN_NAME → this server's IP)"
        echo "   2. Port 80 is accessible from the internet"
        echo "   3. No firewall is blocking Let's Encrypt servers"
        exit 1
    fi
fi

# Step 6: Deploy production reverse proxy config
echo "→ Deploying production reverse proxy configuration..."

# Find script directory to locate template
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_PATH="$SCRIPT_DIR/../../deploy/nginx/host-reverse-proxy.conf.template"

if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "❌ Template not found at: $TEMPLATE_PATH"
    exit 1
fi

# Substitute variables in template
sed -e "s/\${DOMAIN_NAME}/$DOMAIN_NAME/g" \
    -e "s/\${BACKEND_HOST}/$BACKEND_HOST/g" \
    "$TEMPLATE_PATH" \
    > /etc/nginx/sites-available/projectmeats-$ENVIRONMENT

# Step 7: Test and reload nginx
echo "→ Testing nginx configuration..."
nginx -t

echo "→ Reloading nginx with production config..."
systemctl reload nginx

# Step 8: Setup auto-renewal
echo "→ Setting up SSL certificate auto-renewal..."
(crontab -l 2>/dev/null | grep -v certbot; echo "0 3 * * * certbot renew --quiet --deploy-hook 'systemctl reload nginx'") | crontab -

# Step 9: Verify setup
echo ""
echo "========================================="
echo "✓ Host infrastructure setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Verify DNS is pointing to this server:"
echo "   dig +short $DOMAIN_NAME"
echo ""
echo "2. Ensure Docker containers are running:"
echo "   docker ps | grep -E 'pm-backend|pm-frontend'"
echo ""
echo "3. Update GitHub workflow to use correct ports:"
echo "   - Backend: -p 8000:8000 (NO CHANGE)"
echo "   - Frontend: -p 8080:80 (CHANGED FROM -p 80:80)"
echo ""
echo "4. Test the setup:"
echo "   curl -I https://$DOMAIN_NAME/health"
echo "   curl -I https://$DOMAIN_NAME/api/v1/health/"
echo ""
echo "Configuration files:"
echo "  - Nginx config: /etc/nginx/sites-available/projectmeats-$ENVIRONMENT"
echo "  - SSL cert: /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
echo "  - SSL key: /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem"
echo ""
echo "Useful commands:"
echo "  - Check nginx status: systemctl status nginx"
echo "  - Test nginx config: nginx -t"
echo "  - Reload nginx: systemctl reload nginx"
echo "  - View nginx logs: tail -f /var/log/nginx/access.log"
echo "  - Renew SSL cert: certbot renew --dry-run"
echo ""
