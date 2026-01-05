# Invitation Token Troubleshooting - Quick Reference

## 🔍 Symptom: "Invalid invitation token" Error

**User sees**: `400 Bad Request` with message "Invalid invitation token"

---

## ⚡ Quick Diagnosis

### 1. Run the Diagnostic Script
```bash
cd backend
python scripts/diagnose_invitation_token.py <TOKEN_FROM_URL>
```

Example:
```bash
python scripts/diagnose_invitation_token.py AYwY-DvIXBlEBgsryDUsnxkAVv0L4KKTxLUM2qeuhy0Xg5w3DVDenC5doXmiyxng
```

### 2. Check Which Environment You're Testing
- If token created on **dev** → Must test on **dev.meatscentral.com**
- If token created on **UAT** → Must test on **uat.meatscentral.com**
- If token created on **prod** → Must test on **meatscentral.com**

---

## 🔧 Common Issues & Fixes

### Issue 1: Cross-Environment Token Usage ⚠️ MOST COMMON

**Symptom**: Token not found in database

**Cause**: Token created in one environment (e.g., Dev), but link points to another (e.g., Prod)

**Fix**: 
1. Check where invitation was created
2. Use the matching environment URL
3. Verify `FRONTEND_URL` setting in Django settings

**How to Check**:
```bash
# Check current FRONTEND_URL setting
cd backend
python manage.py shell
>>> from django.conf import settings
>>> print(settings.FRONTEND_URL)
```

---

### Issue 2: Expired Token

**Symptom**: Diagnostic shows "Is Expired: ❌ YES"

**Cause**: Token created more than 7 days ago (default expiration)

**Fix**: Create new invitation

**Check Expiration**:
```python
# In Django shell
from apps.tenants.models import TenantInvitation
inv = TenantInvitation.objects.get(token='your-token')
print(f"Expires: {inv.expires_at}")
print(f"Is Expired: {inv.is_expired}")
```

---

### Issue 3: Token Already Used

**Symptom**: Diagnostic shows "Status: accepted"

**Cause**: Token already used by someone else (single-use invitations)

**Fix**: Create new invitation

**Check Status**:
```python
# In Django shell
from apps.tenants.models import TenantInvitation
inv = TenantInvitation.objects.get(token='your-token')
print(f"Status: {inv.status}")
print(f"Is Reusable: {inv.is_reusable}")
print(f"Usage Count: {inv.usage_count}/{inv.max_uses}")
```

---

### Issue 4: Missing FRONTEND_URL Setting (FIXED)

**Symptom**: Email contains wrong domain (e.g., production URL in dev)

**Cause**: `FRONTEND_URL` not set in Django settings (fixed as of Jan 5, 2026)

**Fix**: Already fixed in latest code

**Verify Fix**:
```bash
cd backend
grep "FRONTEND_URL" projectmeats/settings/development.py
# Should show: FRONTEND_URL = config("FRONTEND_URL", default="https://dev.meatscentral.com")
```

---

## 🛠️ Manual Token Validation

### Via Django Shell
```python
cd backend
python manage.py shell

from apps.tenants.models import TenantInvitation
token = "your-token-here"

# Check if exists
inv = TenantInvitation.objects.filter(token=token).first()
if inv:
    print(f"Found: {inv}")
    print(f"Valid: {inv.is_valid}")
    print(f"Status: {inv.status}")
    print(f"Expires: {inv.expires_at}")
else:
    print("Token not found")
```

### Via API (if endpoint exists)
```bash
curl -X GET "https://dev.meatscentral.com/api/v1/tenants/invitations/validate/?token=YOUR_TOKEN"
```

---

## 📊 Check Recent Invitations

### Django Shell
```python
from apps.tenants.models import TenantInvitation
from django.utils import timezone

# Last 10 invitations
recent = TenantInvitation.objects.select_related('tenant').order_by('-created_at')[:10]

for inv in recent:
    status_icon = "✅" if inv.is_valid else "❌"
    print(f"{status_icon} {inv.tenant.name}: {inv.email or '(reusable)'}")
    print(f"   Token: {inv.token[:20]}...")
    print(f"   Status: {inv.status}, Expires: {inv.expires_at}")
    print()
```

### Django Admin
1. Go to: `https://dev.meatscentral.com/admin/tenants/tenantinvitation/`
2. Filter by Status = "Pending"
3. Check expiration dates
4. Verify token values

---

## 🔄 Create New Invitation

### Via Django Admin
1. Go to: `https://dev.meatscentral.com/admin/tenants/tenant/`
2. Select tenant
3. Click "Onboard new tenant" action
4. Fill in email and click "Send Invitation"
5. Check console/email for new link

### Via Django Shell
```python
from apps.tenants.models import Tenant
from apps.tenants.utils.invitation_utils import generate_invitation_link

# Get tenant
tenant = Tenant.objects.get(slug='your-tenant-slug')

# Generate invitation
invitation, url = generate_invitation_link(
    tenant=tenant,
    role='user',
    days_valid=7,
    email='user@example.com',
    message='Welcome to the team!'
)

print(f"Invitation URL: {url}")
print(f"Token: {invitation.token}")
```

---

## 🚨 Emergency Actions

### Reset Expired Token (Extend Expiration)
```python
from apps.tenants.models import TenantInvitation
from django.utils import timezone
from datetime import timedelta

token = "your-expired-token"
inv = TenantInvitation.objects.get(token=token)

# Extend expiration by 7 days
inv.expires_at = timezone.now() + timedelta(days=7)
inv.save()

print(f"New expiration: {inv.expires_at}")
```

### Revoke Invitation
```python
from apps.tenants.models import TenantInvitation

token = "your-token"
inv = TenantInvitation.objects.get(token=token)
inv.revoke()

print(f"Status: {inv.status}")  # Should be 'revoked'
```

---

## 📋 Verification Checklist

After fixing any issues, verify:

- [ ] Token exists in database (diagnostic script shows "✅ TOKEN FOUND")
- [ ] Status is "pending" (not "accepted", "expired", or "revoked")
- [ ] Not expired (expires_at > current time)
- [ ] Testing on correct environment (dev token on dev site)
- [ ] FRONTEND_URL matches environment in Django settings
- [ ] Email contains correct domain for environment

---

## 📞 Still Having Issues?

1. **Check Django Logs**:
   ```bash
   docker logs pm-backend --tail 100
   ```

2. **Check Database Connection**:
   ```bash
   python manage.py dbshell
   SELECT * FROM tenants_invitation WHERE token LIKE 'AYwY%';
   ```

3. **Verify Settings**:
   ```bash
   python manage.py diffsettings | grep FRONTEND_URL
   ```

4. **Contact Team**: Share diagnostic script output with team

---

## 🔗 Related Documentation

- **Full Analysis**: `docs/INVITATION_TOKEN_FIX.md`
- **Diagnostic Script**: `backend/scripts/diagnose_invitation_token.py`
- **Invitation Utils**: `backend/apps/tenants/utils/invitation_utils.py`
- **Settings Files**: `backend/projectmeats/settings/*.py`
