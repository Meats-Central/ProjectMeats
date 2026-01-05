# Email Branding & Owner Permissions Fix

**Date:** January 5, 2026  
**Author:** GitHub Copilot  
**Related PRs:** #1698 (Invitation Tokens), #1713 (Duplicate Emails), TBD (This PR)

---

## Summary

This fix improves the user experience by:
1. **Updating email branding** from "Project Meats" to "Meats Central"
2. **Improving email messaging** with more professional and concise copy
3. **Automatically granting Django admin access** to tenant owners
4. **Customizing Django admin UI** with dynamic tenant branding and Meats Central theme

---

## Changes Made

### 1. Email Branding Updates

**File:** `backend/apps/tenants/signals.py`

**Changes:**
- Subject line: `"You've been invited to join {tenant.name} on Project Meats"` → `"You've been invited to join {tenant.name} on Meats Central"`
- Email body improvements:
  - Removed "the workspace" (redundant wording)
  - Changed `"Message from sender: {message}"` → `"{message}"` (cleaner presentation)
  - Updated sign-off: `"Welcome aboard,\nThe Project Meats Team"` → `"Welcome to easy meat management,\nThe Meats Central Team"`

**Before:**
```
Subject: You've been invited to join Acme Corp on Project Meats

Hello,

You have been invited to join the workspace 'Acme Corp' as a owner.

Message from sender: Welcome John Doe, your new workspace 'Acme Corp' is ready!

Click the link below to accept the invitation...

Welcome aboard,
The Project Meats Team
```

**After:**
```
Subject: You've been invited to join Acme Corp on Meats Central

Hello,

You have been invited to join 'Acme Corp' as a owner.

Welcome John Doe, your new workspace 'Acme Corp' is ready!

Click the link below to accept the invitation...

Welcome to easy meat management,
The Meats Central Team
```

### 2. Owner Permissions Signal

**File:** `backend/apps/tenants/signals.py`

**New Signal:** `ensure_owner_has_staff_access`

**Purpose:** Automatically grants `is_staff=True` to users when they are assigned the 'owner' role in a tenant.

**Behavior:**
- Listens to `post_save` signal on `TenantUser` model
- When `role='owner'` and `user.is_staff=False`, it:
  - Sets `user.is_staff = True`
  - Saves the user with `update_fields=['is_staff']`
  - Logs the permission grant

**Why This Matters:**
- Tenant owners need access to Django admin to manage their workspace
- Previously, owners had to be manually granted staff status
- Now it happens automatically when they accept their invitation

**Code:**
```python
@receiver(post_save, sender=TenantUser, dispatch_uid="ensure_owner_has_staff_access")
def ensure_owner_has_staff_access(sender, instance, created, **kwargs):
    """
    Automatically grant Django admin access to users with 'owner' role.
    """
    if instance.role == 'owner' and not instance.user.is_staff:
        logger.info(f"🔑 Granting admin access to owner: {instance.user.username} @ {instance.tenant.slug}")
        instance.user.is_staff = True
        instance.user.save(update_fields=['is_staff'])
        logger.info(f"✅ Admin access granted to {instance.user.username}")
```

**Security Notes:**
- Only grants `is_staff` (Django admin access), not `is_superuser`
- Owners can only see/manage data within their tenant (enforced by ViewSet querysets)
- Does not bypass tenant isolation
- Uses `dispatch_uid` to prevent duplicate signal connections during Django reload

### 3. Custom Django Admin Template

**File:** `backend/templates/admin/base_site.html`

**Purpose:** Customize Django admin interface with:
- Dynamic branding (shows tenant name when `request.tenant` is available)
- Meats Central red/dark color theme
- Professional appearance matching frontend branding

**Features:**

**Dynamic Branding:**
```django
{% block title %}
  {% if request.tenant %}
    {{ request.tenant.name }} Admin
  {% else %}
    Meats Central Admin
  {% endif %}
{% endblock %}

{% block branding %}
<h1 id="site-name">
  <a href="{% url 'admin:index' %}">
    {% if request.tenant %}
      {{ request.tenant.name }} Administration
    {% else %}
      Meats Central Administration
    {% endif %}
  </a>
</h1>
{% endblock %}
```

**Color Theme:**
- Primary: Red-800 (#991b1b)
- Secondary: Red-900 (#7f1d1d)
- Accent: Red-400 (#f87171)
- Header: Gray-800 (#1f2937)

**CSS Customizations:**
- Header background with red border
- Button styling with red colors
- Module headers with dark theme
- Link colors matching brand
- Breadcrumbs styling
- Selected items highlighting

**How It Works:**
- Django automatically loads `templates/admin/base_site.html` to override default admin template
- `TenantMiddleware` sets `request.tenant` based on domain/subdomain/header
- Template uses `{% if request.tenant %}` to conditionally show tenant name
- Fallback to "Meats Central" when no tenant context (superuser view, etc.)

---

## Testing

### Email Branding Test

1. **Create a test invitation:**
   ```bash
   cd backend
   python manage.py shell
   ```
   ```python
   from apps.tenants.models import Tenant, TenantInvitation
   from django.contrib.auth.models import User
   
   tenant = Tenant.objects.first()
   admin = User.objects.filter(is_superuser=True).first()
   
   invitation = TenantInvitation.objects.create(
       tenant=tenant,
       email='test@example.com',
       role='owner',
       invited_by=admin,
       message='Test invitation with new branding'
   )
   ```

2. **Check email logs** in console output - should see:
   - Subject: `"You've been invited to join {tenant} on Meats Central"`
   - Message contains: `"Welcome to easy meat management,\nThe Meats Central Team"`
   - No "Message from sender:" prefix

3. **Check SendGrid dashboard** for sent email with updated branding

### Owner Permissions Test

1. **Create a new tenant owner:**
   ```python
   from apps.tenants.models import Tenant, TenantUser
   from django.contrib.auth.models import User
   
   # Create a test user without staff access
   user = User.objects.create_user(
       username='testowner',
       email='owner@example.com',
       password='testpass123'
   )
   assert user.is_staff == False  # Verify not staff initially
   
   # Create TenantUser with owner role
   tenant = Tenant.objects.first()
   tenant_user = TenantUser.objects.create(
       tenant=tenant,
       user=user,
       role='owner'
   )
   
   # Check that is_staff was automatically granted
   user.refresh_from_db()
   assert user.is_staff == True  # Signal should have set this
   ```

2. **Check logs** - should see:
   ```
   🔑 Granting admin access to owner: testowner @ tenant-slug
   ✅ Admin access granted to testowner
   ```

3. **Test admin access:**
   - Navigate to `/admin/`
   - Log in as the test owner
   - Verify access granted (no "You don't have permission" error)
   - Verify they only see their tenant's data

### Admin Template Test

1. **Test with tenant context:**
   - Log in as tenant owner
   - Navigate to `/admin/`
   - Verify header shows: `"{Tenant Name} Administration"`
   - Verify title shows: `"{Tenant Name} Admin"`

2. **Test without tenant context:**
   - Log in as superuser
   - Navigate to `/admin/`
   - Verify header shows: `"Meats Central Administration"`
   - Verify title shows: `"Meats Central Admin"`

3. **Test theme:**
   - Verify header has dark gray background (#1f2937)
   - Verify red border below header (#991b1b)
   - Verify buttons use red color scheme
   - Verify module headers use dark theme

---

## Deployment

### Prerequisites

No new environment variables or secrets required. This is a code-only change.

### Deployment Steps

1. **Merge to development:**
   ```bash
   git push origin fix/email-branding-and-owner-permissions
   # Create PR and merge
   ```

2. **Automatic deployment:**
   - CI/CD pipeline will automatically deploy to dev environment
   - No migration required (code-only changes)
   - No downtime expected

3. **Validation:**
   - Create test invitation in dev environment
   - Verify email branding is correct
   - Test owner permissions with new signup
   - Check admin interface customization

4. **Promote to UAT and Production:**
   - Follow standard promotion workflow
   - No special considerations

### Rollback Plan

If issues occur:

1. **Revert the commit:**
   ```bash
   git revert a17350c
   ```

2. **Emergency fix:**
   - Email will fallback to previous branding (still functional)
   - Owner permissions signal can be disabled by commenting out in `signals.py`
   - Admin template can be removed (Django will use default)

---

## Impact Analysis

### User Experience Improvements

1. **Better Email Branding:**
   - Consistent brand name (Meats Central)
   - More professional messaging
   - Cleaner presentation of custom messages
   - Improved tagline ("Welcome to easy meat management")

2. **Automatic Admin Access:**
   - Owners no longer need manual staff permission grants
   - Immediate access to admin interface after signup
   - Reduces support requests for "I can't access admin"

3. **Branded Admin Interface:**
   - Professional appearance matching frontend
   - Clear tenant context in multi-tenant environment
   - Improved usability with color-coded interface

### Technical Benefits

1. **Signal-Based Automation:**
   - Eliminates manual permission grants
   - Consistent behavior across all invitation flows
   - Prevents permission-related bugs

2. **Template Customization:**
   - Uses Django's built-in template override system
   - Easy to extend with additional branding
   - No modifications to Django admin source code

3. **Maintainability:**
   - All changes in one place (signals.py for logic, base_site.html for UI)
   - Well-documented with code comments
   - Uses dispatch_uid to prevent duplicate signals

### Potential Issues

**None Expected:**
- Signal uses safe `update_fields` to avoid infinite loops
- Template extends Django's base, preserving all functionality
- Email changes are cosmetic only (no logic changes)
- Backward compatible (no breaking changes)

**Monitoring:**
- Watch for signal-related errors in logs
- Monitor invitation email delivery rates
- Check for admin access issues reported by users

---

## Related Documentation

- **Invitation Token Fix:** `/docs/INVITATION_TOKEN_FIX.md`
- **Invitation Troubleshooting:** `/docs/INVITATION_TROUBLESHOOTING.md`
- **Multi-Tenancy Architecture:** `/docs/ARCHITECTURE.md`
- **Configuration & Secrets:** `/docs/CONFIGURATION_AND_SECRETS.md`

---

## Future Enhancements

1. **HTML Email Templates:**
   - Replace plain text with styled HTML emails
   - Include company logo and branding
   - Better mobile rendering

2. **Admin Dashboard Customization:**
   - Add tenant-specific analytics widget
   - Show quick stats for tenant data
   - Custom welcome message per tenant

3. **Permission Granularity:**
   - Fine-tune owner vs admin vs manager permissions
   - Role-based access control in admin interface
   - Per-model permissions for different roles

4. **Email Localization:**
   - Support multiple languages
   - Detect user's preferred language
   - Tenant-specific language defaults

---

## Questions & Support

For questions about this fix:
- Check related documentation (links above)
- Review signal code in `backend/apps/tenants/signals.py`
- Check admin template in `backend/templates/admin/base_site.html`
- Contact: infrastructure team

For issues with:
- **Email delivery:** Check SendGrid dashboard and `EMAIL_BACKEND` settings
- **Owner permissions:** Check logs for signal execution and `is_staff` status
- **Admin customization:** Verify `TEMPLATES['DIRS']` includes `BASE_DIR / 'templates'`
