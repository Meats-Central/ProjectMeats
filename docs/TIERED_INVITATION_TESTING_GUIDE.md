# Tiered Tenant Invitation System - Testing Guide

## 🎯 Overview

PR #1532 now includes a comprehensive three-tier invitation system for managing tenant access.

## 📋 Changes Included in This PR

### 1. Login UX Enhancement
- ✅ Added "Note: Username is case-sensitive" hint below username field
- ✅ Styled as subtle gray italic text

### 2. Django Admin Static Files Fix
- ✅ Added `collectstatic --noinput --clear` to container startup CMD
- ✅ Fixes 404 errors for Django admin CSS/JS files

### 3. **NEW: Tiered Invitation System**
- ✅ Three distinct invitation actions based on user role
- ✅ Intermediate form wizard using Django admin patterns
- ✅ Smart environment detection for invite links
- ✅ Permission-based access control

---

## 🔐 Three-Tier Invitation Actions

### Action 1: Generate Team Invite (Superuser Only)
**Access**: Superusers only  
**Icon**: ⚡  
**Purpose**: Create reusable "Golden Ticket" links for team onboarding

**Features:**
- No email required (reusable link)
- Max 50 uses per link
- Default role: `user`
- Usage tracking included

**How to Use:**
1. Django Admin → Tenants
2. Select ONE tenant
3. Actions dropdown → "⚡ Generate Team Invite Link (Superuser Only)"
4. Click "Go"
5. Copy the generated link from the success message
6. Share link with team members

**Expected Result:**
```
✅ Golden Ticket Created!
[Text input with link - click to select and copy]
```

---

### Action 2: Onboard Tenant Owner (Superuser Only)
**Access**: Superusers only  
**Icon**: 🚀  
**Purpose**: Create personalized admin invitation for new tenant owners

**Features:**
- Captures first name, last name, email
- Forces `admin` role
- Personalized welcome message
- Validates existing users
- Single-use invitation

**How to Use:**
1. Django Admin → Tenants
2. Select ONE tenant
3. Actions dropdown → "🚀 Onboard New Tenant Owner (Superuser Only)"
4. Click "Go"
5. Fill out form:
   - Owner First Name
   - Owner Last Name
   - Owner Email
6. Click "Send Invite"
7. Copy the generated link

**Form Fields:**
- **Owner First Name**: Required (e.g., "John")
- **Owner Last Name**: Required (e.g., "Doe")
- **Owner Email**: Required (e.g., "john.doe@example.com")

**Expected Result:**
```
✅ Owner Onboarded! Invitation created for John Doe (john.doe@example.com)
Send them this link:
[Text input with link - click to select and copy]
```

**Error Cases:**
- If email already exists: "User john.doe@example.com already exists!" (Warning)
- If multiple tenants selected: "Please select exactly one tenant to onboard." (Error)
- If non-superuser tries: "⛔ Permission Denied: Only Superusers can onboard owners." (Error)

---

### Action 3: Send Individual Invite (All Admins)
**Access**: All tenant admins (including superusers)  
**Icon**: 📧  
**Purpose**: Send email-specific single-use invitations

**Features:**
- Specify email, role, and message
- Single-use invitation
- Available to all tenant admins
- Custom welcome message

**How to Use:**
1. Django Admin → Tenants
2. Select ONE tenant
3. Actions dropdown → "📧 Send Individual Invite"
4. Click "Go"
5. Fill out form:
   - User Email
   - Role (dropdown)
   - Message (optional custom text)
6. Click "Send Invite"
7. Copy the generated link

**Form Fields:**
- **User Email**: Required (e.g., "newuser@example.com")
- **Role**: Dropdown with choices:
  - `user` (default)
  - `admin`
  - `owner`
  - `viewer`
- **Message**: Optional textarea (default: "Join us on Project Meats!")

**Expected Result:**
```
✅ Invite Created! Link for newuser@example.com:
[Text input with link - click to select and copy]
```

---

## 🧪 Testing Checklist

### Prerequisites
- [ ] Deploy PR #1532 to development
- [ ] SSH into dev server and run `docker exec pm-backend python manage.py collectstatic --noinput --clear`
- [ ] Restart backend container: `docker restart pm-backend`
- [ ] Access Django admin: https://dev.meatscentral.com/admin/

### Test 1: Login UX
- [ ] Navigate to https://dev.meatscentral.com/login
- [ ] Verify "Note: Username is case-sensitive" appears below username field
- [ ] Verify hint is styled as gray italic text

### Test 2: Django Admin Static Files
- [ ] Log into Django admin
- [ ] Click "View site" button
- [ ] Verify NO console errors for missing CSS/JS files
- [ ] Verify admin UI loads correctly with proper styling

### Test 3: Generate Team Invite (Superuser)
- [ ] Log in as superuser
- [ ] Navigate to Tenants admin
- [ ] Select one tenant (checkbox)
- [ ] Actions dropdown → "⚡ Generate Team Invite Link (Superuser Only)"
- [ ] Click "Go"
- [ ] Verify success message with copyable link
- [ ] Click link input to verify it selects text
- [ ] Copy link and verify format: `https://dev.meatscentral.com/signup?token=...`

### Test 4: Onboard Tenant Owner (Superuser)
- [ ] Log in as superuser
- [ ] Navigate to Tenants admin
- [ ] Select one tenant
- [ ] Actions dropdown → "🚀 Onboard New Tenant Owner (Superuser Only)"
- [ ] Click "Go"
- [ ] Verify intermediate form page loads
- [ ] Fill out form (use unique email)
- [ ] Click "Send Invite"
- [ ] Verify success message with name and email
- [ ] Copy link and verify format

**Test Error Cases:**
- [ ] Try submitting with existing email → should show warning
- [ ] Select multiple tenants → should show error
- [ ] Try as non-superuser → should show permission denied

### Test 5: Send Individual Invite (All Admins)
- [ ] Log in as tenant admin (or superuser)
- [ ] Navigate to Tenants admin
- [ ] Select one tenant
- [ ] Actions dropdown → "📧 Send Individual Invite"
- [ ] Click "Go"
- [ ] Verify intermediate form page loads
- [ ] Fill out form:
  - Email: test@example.com
  - Role: user
  - Message: "Welcome to the team!"
- [ ] Click "Send Invite"
- [ ] Verify success message with email
- [ ] Copy link and verify format

### Test 6: Permission Checks
- [ ] Log in as regular user (non-admin)
- [ ] Verify only "📧 Send Individual Invite" is visible in actions dropdown
- [ ] Verify "⚡ Generate Team Invite Link" is NOT visible
- [ ] Verify "🚀 Onboard New Tenant Owner" is NOT visible

### Test 7: Invitation Tracking
- [ ] Navigate to Tenant Invitations admin
- [ ] Find the invitations created in tests above
- [ ] Verify:
  - Golden Ticket shows "🔗 Reusable Link" in Email/Type column
  - Owner invitation shows admin email
  - Individual invitation shows specified email
  - Usage counts are displayed correctly
  - Expiration dates are set

---

## 🐛 Known Issues & Limitations

### Current Limitations
1. **No Email Sending**: Links must be manually copied and shared
   - Future: Integrate with email service (SendGrid/SES)
2. **No Invitation History**: No audit log of sent invitations
   - Available in Tenant Invitations admin, but not visible during action
3. **Fixed Max Uses**: Golden Ticket hardcoded to 50 uses
   - Future: Allow admin to specify max uses in form

### Browser Compatibility
- Tested on: Chrome, Firefox, Safari, Edge
- Copy-on-click works on modern browsers
- Fallback: Manual selection and Ctrl+C/Cmd+C

---

## 📝 Post-Deployment Tasks

### After Merging PR #1532
1. **Immediate** (on dev server):
   ```bash
   ssh django@157.245.114.182
   docker exec pm-backend python manage.py collectstatic --noinput --clear
   docker restart pm-backend
   ```

2. **Verify Deployment**:
   - Check login page for username hint
   - Check Django admin styling
   - Test all three invitation actions

3. **Monitor Logs**:
   ```bash
   docker logs pm-backend --tail 100 -f
   ```
   - Look for "Collecting static files..."
   - Look for "Setting up superuser..."
   - Look for "Superuser setup complete"

### Future Deployments
- Static files will auto-collect on every container restart
- No manual intervention needed

---

## 🔗 Related Links

- **PR**: https://github.com/Meats-Central/ProjectMeats/pull/1532
- **Django Admin**: https://dev.meatscentral.com/admin/
- **Signup Page**: https://dev.meatscentral.com/signup

---

## 📞 Support

If you encounter issues:
1. Check container logs: `docker logs pm-backend --tail 100`
2. Verify static files: `docker exec pm-backend ls -la /app/staticfiles/admin/css`
3. Check templates: `docker exec pm-backend ls -la /app/templates/admin`
4. Test database: Check `tenants_tenantinvitation` table in pgAdmin

---

**Last Updated**: 2026-01-03  
**PR Status**: Ready for Review  
**Deployment Target**: Development → UAT → Production
