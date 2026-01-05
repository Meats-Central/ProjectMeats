# Invitation System Verification Guide

## Quick Status Check

**Signal Handler**: ✅ Connected (`apps/tenants/signals.py::send_invitation_email`)  
**Email Config**: ⚠️ Requires `EMAIL_HOST_PASSWORD` secret in GitHub

## Test Invitation Flow

### 1. Verify Configuration
```bash
# Check email settings
python manage.py test_email --check-only

# Expected output:
# ✅ Configuration looks good!
#   EMAIL_HOST_USER: apikey
#   EMAIL_HOST_PASSWORD: ✅ SET (69 characters)
#   DEFAULT_FROM_EMAIL: noreply@meatscentral.com
```

### 2. Test Invitation Creation
```bash
# Create test invitation (will trigger email)
python manage.py test_invitation --email=your-email@example.com

# Dry run (no email sent)
python manage.py test_invitation --email=test@example.com --dry-run
```

### 3. Manual Test via Django Admin

1. Navigate to: https://dev.meatscentral.com/admin/tenants/tenantinvitation/
2. Click "Add Tenant Invitation"
3. Fill in:
   - **Tenant**: Select a test tenant
   - **Email**: Your email address
   - **Role**: User
   - **Status**: Pending
   - **Expires at**: 7 days from now
   - **Message**: "Test invitation"
4. Click "Save"
5. **Signal fires automatically** → Email sent via SendGrid

### 4. Check Logs for Email Delivery

**Development (Console Backend)**:
```bash
docker logs pm-backend --tail 50 | grep -A10 "📧"
```

**Production (SMTP Backend)**:
```bash
# SSH into server
ssh user@host

# Check logs
docker logs pm-backend --tail 100 | grep -A20 "📧 Preparing to send"

# Look for:
# ✅ Email sent successfully! (result=1)
# OR
# ❌ Failed to send email
```

## Signal Handler Flow

When `TenantInvitation` is saved with `status='pending'` and `email` set:

1. **Django saves model** → `TenantInvitation.objects.create()`
2. **`post_save` signal fires** → `send_invitation_email()` called
3. **Signal handler logs configuration**:
   ```
   📧 Preparing to send invitation email
   Recipient: user@example.com
   Tenant: Test Company
   Role: user
   EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST: smtp.sendgrid.net
   EMAIL_HOST_PASSWORD: ✅ SET
   ```
4. **Email constructed**:
   - Subject: "You've been invited to join {tenant} on Project Meats"
   - Body: Welcome message + invitation link + expiration
   - From: `DEFAULT_FROM_EMAIL` (noreply@meatscentral.com)
   - To: `invitation.email`
5. **`send_mail()` called** via Django's SMTP backend
6. **SendGrid processes**:
   - Authenticates with API key
   - Verifies sender email
   - Delivers to recipient
7. **Result logged**: `✅ Email sent successfully! (result=1)`

## Common Issues

### Issue: "EMAIL_HOST_PASSWORD: NOT SET"

**Symptom**: Configuration check shows password not set  
**Cause**: GitHub secret not configured for environment  
**Solution**:
```bash
gh secret set EMAIL_HOST_PASSWORD \
  --env production-backend \
  --body "SG.xxxxxxxxxxxxx"
```

### Issue: "SMTPAuthenticationError: (535, Authentication failed)"

**Symptom**: Email sending fails with auth error  
**Cause**: Invalid SendGrid API key  
**Solution**:
1. Generate new API key at https://app.sendgrid.com/settings/api_keys
2. Ensure "Mail Send" permission enabled
3. Update GitHub secret with new key

### Issue: "SMTPSenderRefused: (550, Sender verify failed)"

**Symptom**: SendGrid rejects sender email  
**Cause**: `DEFAULT_FROM_EMAIL` not verified in SendGrid  
**Solution**:
1. Go to SendGrid → Settings → Sender Authentication
2. Verify `noreply@meatscentral.com`
3. Click verification link in email
4. OR use domain authentication for all @meatscentral.com

### Issue: Email goes to spam

**Symptom**: Email delivered but lands in spam folder  
**Cause**: Domain not authenticated  
**Solution**:
1. Set up Domain Authentication in SendGrid
2. Add SPF, DKIM, DMARC records to DNS
3. Use verified domain sender

## Environment-Specific Behavior

### Development (`dev-backend`)
- Uses `console.EmailBackend` by default
- Emails print to Docker logs (not sent)
- Override with `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` to test real sending

### UAT (`uat-backend`)
- Can use console or SMTP (configurable)
- Recommended: Use real SMTP for UAT testing
- Use separate SendGrid API key from production

### Production (`production-backend`)
- Always uses `smtp.EmailBackend`
- **Requires** `EMAIL_HOST_PASSWORD` secret
- Fails fast if not configured

## Verification Checklist

Before deploying to production:

- [ ] `EMAIL_HOST_PASSWORD` secret set in GitHub (`production-backend` environment)
- [ ] `DEFAULT_FROM_EMAIL` verified in SendGrid dashboard
- [ ] SendGrid API key has "Mail Send" permission
- [ ] Test invitation sent successfully: `python manage.py test_invitation --email=admin@meatscentral.com`
- [ ] Email received in inbox (check spam folder)
- [ ] Invitation link works: Click link → Signup page loads
- [ ] Signal handler logs show: `✅ Email sent successfully!`

## Monitoring

### Check Invitation Status
```python
from apps.tenants.models import TenantInvitation

# Recent invitations
recent = TenantInvitation.objects.order_by('-created_at')[:10]
for inv in recent:
    print(f"{inv.email} - {inv.status} - {inv.created_at}")
```

### Check SendGrid Activity
1. Login to SendGrid dashboard
2. Navigate to **Activity**
3. Filter by recipient email or date
4. Check delivery status: Delivered, Bounced, Blocked, etc.

### Check Django Logs
```bash
# Development
docker logs pm-backend --tail 100 | grep "invitation"

# Production
ssh user@host "docker logs pm-backend --tail 100 | grep invitation"
```

## Reference Files

- **Signal Handler**: `backend/apps/tenants/signals.py`
- **Model**: `backend/apps/tenants/models.py::TenantInvitation`
- **Email Settings**: `backend/projectmeats/settings/production.py` (lines 229-239)
- **Test Command**: `backend/apps/tenants/management/commands/test_invitation.py`
- **Email Test**: `backend/apps/tenants/management/commands/test_email.py`
- **Full Guide**: `docs/SENDGRID_EMAIL_CONFIGURATION.md`
