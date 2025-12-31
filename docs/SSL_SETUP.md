# SSL Setup for Production

## Quick Setup (One-time)

SSH into the production frontend droplet (161.35.189.183) and run:

```bash
# Download and run SSL setup script
curl -o setup-ssl.sh https://raw.githubusercontent.com/Meats-Central/ProjectMeats/main/scripts/setup-ssl.sh
chmod +x setup-ssl.sh
sudo ./setup-ssl.sh meatscentral.com admin@meatscentral.com
```

This will:
1. Install certbot
2. Obtain Let's Encrypt SSL certificate for meatscentral.com
3. Configure auto-renewal
4. Place certificates in /etc/nginx/ssl/

## After Running SSL Setup

1. Ensure DigitalOcean firewall allows port 443
2. Redeploy frontend to pick up SSL configuration:
   - The workflow now mounts SSL certificates
   - Container exposes both ports 80 and 443
   - HTTP automatically redirects to HTTPS

## Testing

```bash
# Test HTTP (should redirect)
curl -I http://meatscentral.com

# Test HTTPS
curl -I https://meatscentral.com
```

## Cert Renewal

Certificates auto-renew via cron job (runs daily at 3 AM).
Manual renewal: `sudo certbot renew`

## Switching to SSL Config

To use the SSL-enabled nginx config, update the dockerfile to copy:
```dockerfile
COPY deploy/nginx/frontend-ssl.conf /etc/nginx/conf.d/default.conf
```

Instead of:
```dockerfile
COPY deploy/nginx/frontend.conf /etc/nginx/conf.d/default.conf
```
