# Email Troubleshooting Guide - Server Side

## 🚨 Quick Diagnosis

Run this diagnostic script on your server:

```bash
# On the server (SSH into your droplet)
cd /opt/projectmeats  # or wherever your deployment is
curl -O https://raw.githubusercontent.com/Meats-Central/ProjectMeats/development/scripts/diagnose_email.sh
chmod +x diagnose_email.sh
./diagnose_email.sh
```

Or manually:

```bash
# SSH into server
ssh user@your-server

# Check if EMAIL_HOST_PASSWORD is set in container
docker exec pm-backend printenv | grep EMAIL_HOST_PASSWORD

# Check Django settings
docker exec pm-backend python manage.py shell -c "
from django.conf import settings
print('EMAIL_HOST_PASSWORD:', 'SET' if settings.EMAIL_HOST_PASSWORD else 'NOT SET')
print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)
print('DJANGO_SETTINGS_MODULE:', settings.DJANGO_SETTINGS_MODULE)
"

# Check signal registration
docker exec pm-backend python manage.py shell -c "
from django.db.models import signals
from apps.tenants.models import TenantInvitation
receivers = list(signals.post_save._live_receivers(TenantInvitation))
print('Signal handlers:', len(receivers))
"

# Test SMTP connection
docker exec pm-backend python manage.py test_email --check-only

# Check recent logs
docker logs pm-backend --tail 100 | grep -A10 "📧"
```

## Common Issues & Fixes

### Issue 1: EMAIL_HOST_PASSWORD Not Set in Container

**Symptom**: `EMAIL_HOST_PASSWORD: NOT SET` when checking environment

**Cause**: Secret not passed to container OR .env file not mounted

**Fix Option A - Environment Variable**:
```bash
# Check if secret is set in GitHub
gh secret list --env production-backend

# If not set:
gh secret set EMAIL_HOST_PASSWORD \
  --env production-backend \
  --body "SG.your-sendgrid-api-key"

# Redeploy
git push origin main
```

**Fix Option B - .env File on Server**:
```bash
# SSH into server
ssh user@server

# Check if .env exists
ls -la /root/projectmeats/backend/.env

# If not exists, create it:
cat > /root/projectmeats/backend/.env << 'EOF'
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key-here
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
DEFAULT_FROM_EMAIL=noreply@meatscentral.com
EOF

# Restart container to reload environment
docker restart pm-backend

# Verify it loaded
docker exec pm-backend python manage.py test_email --check-only
```

### Issue 2: Wrong DJANGO_SETTINGS_MODULE

**Symptom**: Using development settings instead of production

**Cause**: Container started without `DJANGO_SETTINGS_MODULE` env var

**Fix**:
```bash
# Check current setting
docker exec pm-backend printenv DJANGO_SETTINGS_MODULE

# Should be: projectmeats.settings.production
# If wrong, update docker run command or .env file:

# Stop container
docker stop pm-backend

# Start with correct settings
docker run -d --name pm-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file /root/projectmeats/backend/.env \
  -e DJANGO_SETTINGS_MODULE=projectmeats.settings.production \
  -v /root/projectmeats/media:/app/media \
  -v /root/projectmeats/staticfiles:/app/staticfiles \
  registry.digitalocean.com/meatscentral/projectmeats-backend:prod-latest
```

### Issue 3: Development Email Backend Active

**Symptom**: `EMAIL_BACKEND: django.core.mail.backends.console.EmailBackend`

**Cause**: Development settings being used OR production override missing

**Fix**:
```bash
# Add to .env file
echo "EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend" >> /root/projectmeats/backend/.env

# Restart container
docker restart pm-backend
```

### Issue 4: Firewall Blocking Port 587

**Symptom**: `Connection timeout` or `Connection refused`

**Cause**: Server firewall or DigitalOcean firewall blocking outbound SMTP

**Fix**:
```bash
# Test connection from server
nc -zv smtp.sendgrid.net 587

# If blocked, try alternative ports:
# Port 2525 (alternative SMTP)
# Port 465 (SMTP over SSL)

# Update .env:
EMAIL_PORT=2525
# OR
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True

# Restart
docker restart pm-backend
```

### Issue 5: Signal Handler Not Firing

**Symptom**: No email-related logs when invitation created

**Cause**: `apps.tenants.signals` not imported

**Fix**:
```bash
# SSH into server
docker exec -it pm-backend bash

# Check if signals module loads
python manage.py shell -c "
import apps.tenants.signals
print('Signal module loaded:', apps.tenants.signals.__file__)
"

# If error, check apps.py has ready() method
# Should contain: import apps.tenants.signals  # noqa: F401

# Restart application
exit
docker restart pm-backend
```

### Issue 6: SendGrid API Key Invalid

**Symptom**: `SMTPAuthenticationError: (535, Authentication failed)`

**Cause**: Wrong API key or key lacks permissions

**Fix**:
1. Login to SendGrid: https://app.sendgrid.com/settings/api_keys
2. Create new API key with "Mail Send" permission
3. Copy the key (starts with `SG.`)
4. Update secret:
```bash
gh secret set EMAIL_HOST_PASSWORD \
  --env production-backend \
  --body "SG.your-new-api-key"
```
5. Redeploy

### Issue 7: Sender Email Not Verified

**Symptom**: `SMTPSenderRefused: (550, Sender verify failed)`

**Cause**: `DEFAULT_FROM_EMAIL` not verified in SendGrid

**Fix**:
1. Login to SendGrid: https://app.sendgrid.com/settings/sender_auth
2. Add Single Sender Verification for `noreply@meatscentral.com`
3. Check email and click verification link
4. Wait 5-10 minutes for verification to propagate
5. Test again:
```bash
docker exec pm-backend python manage.py test_invitation --email=your-email@example.com
```

## Step-by-Step Debugging Process

### Step 1: Verify Container Has Email Password
```bash
docker exec pm-backend printenv EMAIL_HOST_PASSWORD
```
Expected: `SG.xxxxxxxxxxxxx` (69 characters)

If empty → Set GitHub secret and redeploy OR create .env file

### Step 2: Verify Django Can See Settings
```bash
docker exec pm-backend python manage.py test_email --check-only
```
Expected:
```
✅ Configuration looks good!
  EMAIL_HOST_PASSWORD: ✅ SET (69 characters)
  DEFAULT_FROM_EMAIL: noreply@meatscentral.com
```

If NOT SET → Settings not loading correctly, check `DJANGO_SETTINGS_MODULE`

### Step 3: Test SMTP Connection
```bash
docker exec pm-backend python manage.py shell -c "
from django.core.mail import get_connection
conn = get_connection()
print('Connection result:', conn.open())
"
```
Expected: `Connection result: True`

If False or error → Check API key, firewall, or try different port

### Step 4: Verify Signal Connected
```bash
docker exec pm-backend python manage.py shell -c "
from django.db.models import signals
from apps.tenants.models import TenantInvitation
receivers = list(signals.post_save._live_receivers(TenantInvitation))
print('Signal handlers:', len(receivers))
"
```
Expected: `Signal handlers: 1` (or more)

If 0 → Signals not importing, restart container

### Step 5: Create Test Invitation
```bash
docker exec pm-backend python manage.py test_invitation --email=your-email@example.com
```

Watch logs in real-time:
```bash
docker logs pm-backend -f
```

Expected in logs:
```
📧 Preparing to send invitation email
Recipient: your-email@example.com
...
✅ Email sent successfully! (result=1)
```

### Step 6: Check SendGrid Activity
1. Login: https://app.sendgrid.com/activity
2. Search for recipient email
3. Check status: Delivered, Processed, Bounced, etc.

## Manual Test Sequence

If automation isn't working, try manual steps:

```bash
# 1. SSH into server
ssh user@server

# 2. Enter container
docker exec -it pm-backend bash

# 3. Check environment
printenv | grep EMAIL

# 4. Test Django settings
python manage.py shell
>>> from django.conf import settings
>>> settings.EMAIL_HOST_PASSWORD
>>> settings.EMAIL_BACKEND
>>> exit()

# 5. Test connection
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test',
...     'Test message',
...     'noreply@meatscentral.com',
...     ['your-email@example.com'],
...     fail_silently=False
... )
>>> exit()

# 6. Check logs
exit  # exit container
docker logs pm-backend --tail 50
```

## Quick Fix Checklist

Run through this checklist:

- [ ] `EMAIL_HOST_PASSWORD` secret set in GitHub for correct environment
- [ ] Application redeployed after setting secret
- [ ] Container has EMAIL_HOST_PASSWORD in environment (`docker exec pm-backend printenv`)
- [ ] Django settings show password as SET (`python manage.py test_email --check-only`)
- [ ] SMTP connection test passes (`python manage.py shell` → `get_connection().open()`)
- [ ] Signal handler registered (should show 1+ handlers)
- [ ] Sender email verified in SendGrid dashboard
- [ ] SendGrid API key has "Mail Send" permission
- [ ] Port 587 not blocked by firewall
- [ ] DJANGO_SETTINGS_MODULE set to `projectmeats.settings.production`

## Still Not Working?

If you've checked everything and emails still don't send:

1. **Capture full error**:
```bash
docker logs pm-backend --tail 200 > email_debug.log
```

2. **Check SendGrid status**: https://status.sendgrid.com/

3. **Try alternative configuration**:
```bash
# Use port 2525 instead
EMAIL_PORT=2525

# OR use API instead of SMTP (requires sendgrid library)
# pip install sendgrid
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=SG.xxxxx
```

4. **Share diagnostic output**:
```bash
./diagnose_email.sh > diagnostics.txt
```

Then review the diagnostics output to identify the exact failure point.
