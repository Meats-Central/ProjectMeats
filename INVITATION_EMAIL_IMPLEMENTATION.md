# Tenant Invitation Email Notification Implementation

## Overview
This implementation adds automatic email notifications when tenant invitations are created or resent, both via the API and Django admin interface.

## Date Implemented
November 2, 2025

## Files Changed/Added

### New Files
1. **backend/apps/tenants/email_utils.py** - Email sending utility functions
2. **backend/apps/tenants/templates/tenants/email/invitation_email.html** - HTML email template
3. **backend/apps/tenants/templates/tenants/email/invitation_email.txt** - Plain text email template
4. **backend/apps/tenants/tests_invitation_email.py** - Comprehensive test suite for email functionality
5. **test_invitation_email_manual.py** - Manual testing script

### Modified Files
1. **backend/apps/tenants/invitation_views.py**
   - Added `perform_create()` method to send email after invitation creation
   - Updated `resend()` action to send email when resending
   - Fixed security issue (stack trace exposure)

2. **backend/apps/tenants/admin.py**
   - Added `save_model()` override to send email when invitations are created via admin
   - Added `resend_invitation_emails` admin action for batch resending
   - Added user feedback messages for email send status

3. **backend/apps/tenants/invitation_serializers.py**
   - Updated `TenantInvitationCreateSerializer` to include additional fields in response
   - Fixed `TenantInvitationDetailSerializer` read-only fields issue

4. **backend/projectmeats/settings/base.py**
   - Added `DEFAULT_FROM_EMAIL` setting
   - Added `FRONTEND_URL` setting for email links

## Features Implemented

### 1. Email Sending on Invitation Creation
- **API**: When a new invitation is created via POST to `/api/tenants/api/invitations/`, an email is automatically sent
- **Admin**: When an admin creates an invitation in Django admin, an email is automatically sent
- **Content includes**:
  - Tenant name
  - Role being invited to
  - Inviter's name (if available)
  - Personal message (optional)
  - Signup URL with invitation token
  - Expiration date

### 2. Email Sending on Invitation Resend
- **API**: When resending via POST to `/api/tenants/api/invitations/{id}/resend/`, updates expiration and sends email
- **Admin**: Added bulk action "Resend invitation emails" that extends expiration and resends emails

### 3. Email Templates
- **HTML Template**: Professionally styled responsive email with:
  - Clean, modern design
  - Clear call-to-action button
  - Highlighted invitation details
  - Personal message box (if provided)
  - Expiration warning
- **Plain Text Template**: Fallback for email clients that don't support HTML

### 4. Configuration
- **DEFAULT_FROM_EMAIL**: Configurable via environment variable (default: noreply@meatscentral.com)
- **FRONTEND_URL**: Configurable via environment variable (default: https://app.meatscentral.com)
- Uses existing email backend configuration (console for dev, SMTP for production)

## Testing

### Automated Tests (9 tests, all passing)
Located in `backend/apps/tenants/tests_invitation_email.py`:

1. **InvitationEmailTests** (4 tests)
   - Email sent successfully with all content
   - Email sent without inviter
   - Email sent without message
   - Custom FRONTEND_URL respected

2. **InvitationEmailAPITests** (3 tests)
   - Email sent when creating invitation via API
   - Email sent when resending via API
   - Multiple invitations send multiple emails

3. **InvitationAdminEmailTests** (2 tests)
   - Email sent when creating via admin
   - Batch resend action works

### Manual Testing
Run `python test_invitation_email_manual.py` from project root to:
- Create a test invitation
- Send an email
- Verify email content
- Print email to console (in dev mode)

### Test Results
```bash
$ python manage.py test apps.tenants.tests_invitation_email --settings=projectmeats.settings.test
----------------------------------------------------------------------
Ran 9 tests in 0.075s

OK
```

## Security

### CodeQL Analysis
- ✅ All security checks passed
- Fixed stack trace exposure issue in error responses
- No sensitive data leaked in emails
- Token security maintained

### Email Security
- Tokens are URL-safe, 48-character strings (384 bits of entropy)
- Tokens are not logged in email content
- Email addresses validated before sending
- SMTP connections use TLS in production

## Usage

### For Developers
The email system works automatically. No code changes needed to use it.

### For Administrators

#### Via Django Admin:
1. Navigate to Tenants > Tenant Invitations
2. Click "Add Tenant Invitation"
3. Fill in the form (email, role, optional message)
4. Click "Save"
5. ✅ Email automatically sent

#### To Resend:
1. Select one or more pending invitations
2. Choose "Resend invitation emails" from Actions dropdown
3. Click "Go"
4. ✅ Emails resent with extended expiration

### For API Users

#### Create Invitation:
```bash
POST /api/tenants/api/invitations/
Authorization: Token <your-token>

{
  "email": "newuser@example.com",
  "role": "manager",
  "message": "Welcome to the team!"
}
```
✅ Email automatically sent

#### Resend Invitation:
```bash
POST /api/tenants/api/invitations/{id}/resend/
Authorization: Token <your-token>
```
✅ Expiration extended and email resent

## Configuration for Deployment

### Environment Variables
Add these to your `.env` file:

```bash
# Email From Address
DEFAULT_FROM_EMAIL=noreply@meatscentral.com

# Frontend URL (for signup links in emails)
FRONTEND_URL=https://app.meatscentral.com

# SMTP Settings (production only)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-username
EMAIL_HOST_PASSWORD=your-password
```

### Development
- Uses `django.core.mail.backends.console.EmailBackend`
- Emails printed to console
- Test with `mail.outbox` in unit tests

### Production
- Uses `django.core.mail.backends.smtp.EmailBackend`
- Emails sent via configured SMTP server
- Ensure SMTP credentials are set

## Error Handling

### Email Send Failures
- Failures are logged but don't prevent invitation creation
- Admin sees warning message if email fails
- API returns invitation data successfully even if email fails

### Graceful Degradation
- If email server is down, invitations still work
- Users can manually share invitation links
- Errors logged for monitoring

## Monitoring

### Logs to Watch
```python
# Successful sends
INFO: Invitation email sent successfully to user@example.com for tenant Company Name (invitation ID: uuid)

# Send failures
ERROR: Failed to send invitation email to user@example.com for tenant Company Name (invitation ID: uuid): error message
```

### Metrics to Track
- Email send success rate
- Average time to send
- Bounce/delivery failures (via SMTP provider)

## Future Enhancements

### Potential Improvements
1. **Email Tracking**: Track opens and clicks
2. **Custom Templates**: Allow tenants to customize email templates
3. **Reminder Emails**: Send reminders before invitation expires
4. **Email Preferences**: Let users choose email frequency
5. **Internationalization**: Multi-language email templates
6. **Email Queue**: Use Celery for asynchronous sending
7. **Delivery Webhooks**: Track delivery status from SMTP provider

### Not Implemented (Intentionally)
- Email tracking/analytics (privacy-focused approach)
- HTML-only emails (plain text always included)
- Embedded images (better deliverability without them)

## Troubleshooting

### Emails Not Sending

1. **Check email backend configuration**:
   ```python
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.EMAIL_BACKEND)
   ```

2. **Check logs**:
   ```bash
   grep "Invitation email" backend/logs/django.log
   ```

3. **Test SMTP connection**:
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
   ```

### Emails in Spam

1. Configure SPF, DKIM, and DMARC records
2. Use reputable SMTP provider
3. Avoid spam trigger words in templates
4. Include unsubscribe link (future enhancement)

### Token Links Not Working

1. Verify `FRONTEND_URL` is correct
2. Check frontend routes match expected pattern
3. Ensure frontend validates tokens properly

## Summary

✅ **Complete**: All requirements met
- Email sent on invitation creation (API + Admin)
- Email sent on invitation resend (API + Admin)
- Professional HTML and plain text templates
- Comprehensive test coverage
- Security validated
- Production-ready

🎯 **Impact**: Streamlines user onboarding process and ensures invitees receive timely notifications with all necessary information to join their tenant.
