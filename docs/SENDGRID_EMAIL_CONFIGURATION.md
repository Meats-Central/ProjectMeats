# SendGrid Email Configuration Guide

## Overview

ProjectMeats uses SendGrid for transactional emails (invitations, password resets, notifications). This guide covers setup, troubleshooting, and testing.

## Required Environment Variables

All backend environments (dev, uat, production) need these variables:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<your-sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@meatscentral.com
```

## GitHub Secrets Setup

Add these secrets to each backend environment in GitHub:

### Production Backend (`production-backend` environment)
```bash
gh secret set EMAIL_HOST_PASSWORD --env production-backend --body "SG.xxxxxxxxxxxxx"
gh secret set DEFAULT_FROM_EMAIL --env production-backend --body "noreply@meatscentral.com"
```

### UAT Backend (`uat-backend` environment)
```bash
gh secret set EMAIL_HOST_PASSWORD --env uat-backend --body "SG.xxxxxxxxxxxxx"
gh secret set DEFAULT_FROM_EMAIL --env uat-backend --body "noreply@meatscentral.com"
```

### Dev Backend (`dev-backend` environment)
**Note**: Development uses console backend by default (emails print to logs). To test real emails in dev:

```bash
gh secret set EMAIL_BACKEND --env dev-backend --body "django.core.mail.backends.smtp.EmailBackend"
gh secret set EMAIL_HOST_PASSWORD --env dev-backend --body "SG.xxxxxxxxxxxxx"
```

## SendGrid Configuration

### 1. Create SendGrid Account
- Sign up at https://sendgrid.com
- Verify your account and domain

### 2. Create API Key
1. Navigate to Settings → API Keys
2. Click "Create API Key"
3. Name: `ProjectMeats-Production` (or environment-specific)
4. Permissions: Select "Full Access" or at minimum "Mail Send"
5. Copy the API key (starts with `SG.`)
6. **Important**: Save this key immediately - you can't view it again

### 3. Verify Sender Email
1. Navigate to Settings → Sender Authentication
2. Choose "Single Sender Verification" (quick) or "Domain Authentication" (recommended for production)
3. Add `noreply@meatscentral.com` and verify via email link
4. **Critical**: Sender email MUST match `DEFAULT_FROM_EMAIL` setting

## Testing Email Configuration

### Option 1: Management Command (Recommended)
```bash
# Check configuration only
python manage.py test_email --check-only

# Send test email
python manage.py test_email --to=your-email@example.com
```

### Option 2: Django Shell
```python
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

# Check configuration
print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}")
print(f"Password set: {'Yes' if settings.EMAIL_HOST_PASSWORD else 'No'}")

# Send test email
send_mail(
    subject="Test from Django",
    message="This is a test email",
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=["your-email@example.com"],
    fail_silently=False,
)
```

### Option 3: Test Script
```bash
cd backend
export EMAIL_HOST_PASSWORD="SG.xxxxxxxxxxxxx"
python test_email.py
```

## Invitation Email Flow

When a tenant onboarding happens:

1. **Admin creates invitation** via Django admin or management command
2. **Signal handler triggers** (`apps/tenants/signals.py::send_invitation_email`)
3. **Email content generated**:
   - Subject: "You've been invited to join {tenant} on Project Meats"
   - Body: Welcome message + invitation link + expiration date
4. **Email sent via SendGrid**
5. **User receives email** and clicks link to signup

## Troubleshooting

### Email Not Sending

**Check 1: Configuration**
```bash
python manage.py test_email --check-only
```

Expected output:
```
✅ Configuration looks good!
  EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
  EMAIL_HOST: smtp.sendgrid.net
  EMAIL_HOST_PASSWORD: ✅ SET (69 characters)
  DEFAULT_FROM_EMAIL: noreply@meatscentral.com
```

**Check 2: Logs**
```bash
# Local development
docker logs pm-backend --tail 100

# Production
ssh user@host "docker logs pm-backend --tail 100"
```

Look for:
- `📧 Preparing to send invitation email`
- `✅ Email sent successfully!`
- `❌ Failed to send email` (with error details)

**Check 3: SendGrid Activity Log**
1. Login to SendGrid dashboard
2. Navigate to Activity
3. Filter by recipient email or date
4. Check status: Delivered, Bounced, Blocked, etc.

### Common Errors

#### `SMTPAuthenticationError: (535, b'Authentication failed')`
**Cause**: Invalid API key
**Solution**: 
- Verify API key is correct (starts with `SG.`)
- Check key has "Mail Send" permissions
- Generate new API key if needed

#### `SMTPSenderRefused: (550, b'Sender verify failed')`
**Cause**: Sender email not verified in SendGrid
**Solution**:
- Verify `noreply@meatscentral.com` in SendGrid
- Or use a verified sender email in `DEFAULT_FROM_EMAIL`

#### `ConnectionRefusedError: [Errno 111] Connection refused`
**Cause**: Firewall blocking SMTP port 587
**Solution**:
- Check network/firewall rules
- Try port 2525 or 465 (SSL) as alternative

#### Emails going to spam
**Solution**:
- Set up Domain Authentication (SPF, DKIM, DMARC)
- Use verified domain sender
- Avoid spam trigger words
- Check SendGrid reputation score

## Environment-Specific Behavior

### Development (`projectmeats.settings.development`)
- Default: `EMAIL_BACKEND = console.EmailBackend`
- Emails print to console/logs (not sent)
- Override with environment variable to test real emails

### Staging/UAT (`projectmeats.settings.staging`)
- Default: `EMAIL_BACKEND = console.EmailBackend`
- Can be configured to use SMTP for UAT testing
- Recommended: Use separate SendGrid subuser for UAT

### Production (`projectmeats.settings.production`)
- Always uses `smtp.EmailBackend`
- **Requires** `EMAIL_HOST_PASSWORD` to be set
- Fails fast if configuration missing

## Monitoring

### Success Metrics
- Invitation emails sent: Check Django logs
- Delivery rate: SendGrid dashboard → Statistics
- Open rate: SendGrid dashboard → Email Activity

### Alerts
Set up SendGrid webhooks to receive alerts for:
- Bounced emails
- Spam reports
- Unsubscribes
- Failed deliveries

## Best Practices

1. **Separate API Keys**: Use different keys for dev/uat/production
2. **Rotate Keys**: Regenerate API keys quarterly
3. **Monitor Usage**: Check SendGrid quota usage monthly
4. **Test Regularly**: Run `test_email` command after deployments
5. **Domain Authentication**: Use full domain auth (not single sender) for production
6. **Backup Sender**: Configure `SERVER_EMAIL` for server error notifications

## Reference

- SendGrid Docs: https://docs.sendgrid.com/
- Django Email Docs: https://docs.djangoproject.com/en/stable/topics/email/
- Manifest: `config/env.manifest.json` (EMAIL_* variables)
- Signal Handler: `backend/apps/tenants/signals.py`
- Settings: `backend/projectmeats/settings/production.py`

## Support

If emails still fail after following this guide:
1. Check SendGrid status page: https://status.sendgrid.com/
2. Review SendGrid activity log for rejected messages
3. Contact SendGrid support with activity ID
4. Check ProjectMeats deployment logs for detailed error traces
