#!/bin/bash
# Setup Let's Encrypt SSL certificate for production frontend

set -euo pipefail

DOMAIN="${1:-meatscentral.com}"
EMAIL="${2:-admin@meatscentral.com}"

echo "=================================="
echo "Setting up SSL for $DOMAIN"
echo "=================================="

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt-get update -qq
    sudo apt-get install -y certbot
fi

# Create SSL directory
sudo mkdir -p /etc/nginx/ssl
sudo mkdir -p /var/www/certbot

# Stop any process using port 80 temporarily
echo "Freeing port 80 for certificate validation..."
docker stop pm-frontend 2>/dev/null || true
sudo fuser -k 80/tcp 2>/dev/null || true
sleep 2

# Get certificate using standalone mode
echo "Obtaining SSL certificate from Let's Encrypt..."
sudo certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --domains "$DOMAIN" \
    --domains "www.$DOMAIN" \
    --keep-until-expiring

# Copy certificates to nginx SSL directory
echo "Copying certificates..."
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem /etc/nginx/ssl/
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem /etc/nginx/ssl/
sudo chmod 644 /etc/nginx/ssl/fullchain.pem
sudo chmod 600 /etc/nginx/ssl/privkey.pem

echo "✓ SSL certificates installed successfully"
echo ""
echo "Certificate locations:"
echo "  Fullchain: /etc/nginx/ssl/fullchain.pem"
echo "  Private key: /etc/nginx/ssl/privkey.pem"
echo ""
echo "Next steps:"
echo "1. Update docker run command to mount SSL certificates"
echo "2. Use frontend-ssl.conf nginx configuration"
echo "3. Expose port 443"

# Setup auto-renewal cron job
if ! sudo crontab -l 2>/dev/null | grep -q certbot; then
    echo "Setting up auto-renewal..."
    (sudo crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --deploy-hook 'docker restart pm-frontend'") | sudo crontab -
    echo "✓ Auto-renewal configured (runs daily at 3 AM)"
fi
