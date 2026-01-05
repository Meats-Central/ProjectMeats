# SendGrid Configuration for Server Deployment
# =================================================
# 
# GitHub's security scanning prevents committing API keys to source code.
# This is the CORRECT approach - secrets should be managed separately.
#
# Your API key is provided separately - see SENDGRID_API_KEY.txt (do NOT commit this file)

## Method 1: GitHub Secrets (Recommended for CI/CD)
Run these commands to set secrets in GitHub:

```bash
# Production Backend
gh secret set EMAIL_HOST_PASSWORD \
  --env production-backend \
  --body "YOUR_SENDGRID_API_KEY_HERE"

# UAT Backend  
gh secret set EMAIL_HOST_PASSWORD \
  --env uat-backend \
  --body "YOUR_SENDGRID_API_KEY_HERE"

# Dev Backend (optional - uses console by default)
gh secret set EMAIL_BACKEND \
  --env dev-backend \
  --body "django.core.mail.backends.smtp.EmailBackend"
  
gh secret set EMAIL_HOST_PASSWORD \
  --env dev-backend \
  --body "YOUR_SENDGRID_API_KEY_HERE"
```

Then redeploy your application (push to main/development/uat branches).

## Method 2: Server .env File (Quick Manual Fix)
SSH into your server and create/update the .env file:

```bash
# SSH into server
ssh user@your-server

# Create backend .env file
cat > /root/projectmeats/backend/.env << 'EOF'
# Django Settings
DJANGO_SETTINGS_MODULE=projectmeats.settings.production
DEBUG=False
SECRET_KEY=your-django-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# SendGrid Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=YOUR_SENDGRID_API_KEY_HERE
DEFAULT_FROM_EMAIL=noreply@meatscentral.com

# Allowed Hosts
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com,yourdomain.com
EOF

# Restart the backend container
docker restart pm-backend

# Verify it loaded
docker exec pm-backend python manage.py test_email --check-only
```

## Method 3: Docker Environment Variable
If starting container manually:

```bash
docker run -d --name pm-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DJANGO_SETTINGS_MODULE=projectmeats.settings.production \
  -e EMAIL_HOST_PASSWORD="YOUR_SENDGRID_API_KEY_HERE" \
  -e EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
  --env-file /root/projectmeats/backend/.env \
  -v /root/projectmeats/media:/app/media \
  -v /root/projectmeats/staticfiles:/app/staticfiles \
  registry.digitalocean.com/meatscentral/projectmeats-backend:prod-latest
```

## Verification
After applying configuration, test the connection:

```bash
# Check configuration
docker exec pm-backend python manage.py test_email --check-only

# Expected output:
# ✅ Configuration looks good!
#   EMAIL_HOST_PASSWORD: ✅ SET (69 characters)

# Send test email
docker exec pm-backend python manage.py test_email --to=your-email@example.com

# Create test invitation
docker exec pm-backend python manage.py test_invitation --email=your-email@example.com

# Check logs
docker logs pm-backend --tail 100 | grep "📧"
```

## Security Notes

1. **Never commit secrets to Git** - GitHub will block pushes containing secrets
2. **Rotate API keys regularly** - Generate new keys in SendGrid dashboard quarterly
3. **Use environment-specific keys** - Different keys for dev/staging/production
4. **Verify sender email** - Ensure noreply@meatscentral.com is verified in SendGrid
5. **Monitor usage** - Check SendGrid dashboard for quota and deliverability

## Troubleshooting

If emails still don't send after configuration:

1. Run diagnostics:
   ```bash
   ./scripts/diagnose_email.sh
   ```

2. Check SendGrid activity log:
   https://app.sendgrid.com/activity

3. Verify sender email:
   https://app.sendgrid.com/settings/sender_auth

4. Review complete guide:
   `docs/EMAIL_TROUBLESHOOTING_SERVER_SIDE.md`

## SendGrid API Key Details

**Format**: Starts with `SG.` followed by two dot-separated segments
- **Length**: 69 characters
- **Required Permissions**: Mail Send
- **Sender**: noreply@meatscentral.com (must be verified in SendGrid)

To generate a new API key:
1. Login to SendGrid: https://app.sendgrid.com
2. Navigate to Settings → API Keys
3. Click "Create API Key"
4. Name it (e.g., "ProjectMeats-Production")
5. Select "Full Access" or minimum "Mail Send"
6. Copy the key immediately (can't view again)
7. Update your deployment configuration

## What Settings Are Configured

All environment settings files now include:

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "apikey"  # This is the literal string "apikey" for SendGrid
EMAIL_HOST_PASSWORD = # Read from environment variable
DEFAULT_FROM_EMAIL = "noreply@meatscentral.com"
```

These settings are in:
- `backend/projectmeats/settings/production.py`
- `backend/projectmeats/settings/staging.py`
- `backend/projectmeats/settings/development.py`

## Signal Handler Verification

The invitation email signal is properly configured:
- File: `backend/apps/tenants/signals.py`
- Function: `send_invitation_email`
- Decorator: `@receiver(post_save, sender=TenantInvitation)`
- Triggers: When TenantInvitation created with status='pending' and email set

The signal will automatically send emails once EMAIL_HOST_PASSWORD is configured.
