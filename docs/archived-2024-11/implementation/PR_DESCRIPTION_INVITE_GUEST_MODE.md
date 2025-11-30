# PR: Invite-Only Registration and Guest Mode with Staff Testing Permissions

## 📋 Overview

This PR implements two major authentication enhancements for ProjectMeats:

1. **Invite-Only User Registration System** - Secure, token-based invitation system that ensures all users are tied to a tenant
2. **Guest Mode** - One-click demo access with comprehensive testing capabilities

## 🎯 Objectives Achieved

### Primary Requirements
- ✅ Ensure all users are tied to a tenant (no orphaned users)
- ✅ Restrict user creation to invite-only from tenant admins/owners
- ✅ Provide guest mode for easy platform exploration
- ✅ Maintain strict security boundaries (tenant isolation)
- ✅ Enable comprehensive testing via Django admin access for guests

## 🔐 Security Model

### Guest User Permissions
- **is_staff = True**: Can access Django admin for comprehensive testing/demo
- **is_superuser = False**: NO system-wide permissions
- **TenantUser.role = 'admin'**: Full permissions within guest tenant only
- **Tenant Isolation**: Cannot access or view other tenants' data

### Why Staff Permissions for Guest?
Guest users have `is_staff=True` to enable:
- Testing Django admin interface with real tenant-scoped data
- Comprehensive demonstration of platform capabilities
- No system-wide access (prevented by `is_superuser=False`)
- Cannot manage users, permissions, or system settings
- All operations restricted to guest tenant only

## 🏗️ Implementation Details

### 1. Invitation System

#### Database Changes
- **Migration 0002**: Added `TenantInvitation` model
  - Unique 64-character tokens
  - Time-limited expiration (default 7 days)
  - Single-use with status tracking
  - Role assignment capability
  - Unique constraint: (tenant, email, status='pending')

#### New Files
- `backend/apps/tenants/invitation_models.py` - TenantInvitation model
- `backend/apps/tenants/invitation_serializers.py` - Invitation CRUD serializers
- `backend/apps/tenants/invitation_views.py` - Invitation API endpoints
- `test_invitations.py` - Automated testing script

#### Modified Files
- `backend/apps/tenants/models.py` - Imported TenantInvitation
- `backend/apps/tenants/urls.py` - Added invitation routes
- `backend/apps/tenants/admin.py` - Added invitation inline
- `backend/apps/core/views.py` - Disabled direct signup

#### API Endpoints
```
POST   /api/v1/tenants/api/invitations/                    # Create invitation (admin/owner only)
GET    /api/v1/tenants/api/invitations/                    # List invitations
GET    /api/v1/tenants/api/invitations/{id}/               # Get invitation details
DELETE /api/v1/tenants/api/invitations/{id}/               # Delete invitation
POST   /api/v1/tenants/auth/signup-with-invitation/        # Accept invitation & sign up
POST   /api/v1/tenants/auth/validate-invitation/           # Validate invitation token
POST   /api/v1/core/auth/signup/                           # Now returns 403 (invite required)
```

### 2. Guest Mode

#### New Files
- `backend/apps/core/management/commands/create_guest_tenant.py` - Management command
- `test_guest_mode.py` - Automated security verification script

#### Modified Files
- `backend/apps/core/views.py` - Added `guest_login()` endpoint, updated `login()`
- `backend/apps/core/urls.py` - Added guest login route

#### Management Command
```bash
# Default usage
python manage.py create_guest_tenant

# Custom configuration
python manage.py create_guest_tenant \
  --username demo \
  --password demo456 \
  --tenant-name "Demo Company" \
  --tenant-slug demo-company
```

#### What It Creates
1. **Guest User**
   - Username: `guest` (default)
   - Password: `guest123` (default)
   - is_staff: True (Django admin access)
   - is_superuser: False (no system-wide access)

2. **Guest Tenant**
   - Name: "Guest Demo Organization" (default)
   - Slug: `guest-demo` (default)
   - is_trial: True
   - Settings: `{'is_guest_tenant': True, 'allow_data_reset': True, 'max_records': 100}`

3. **TenantUser Association**
   - Role: `admin`
   - Links guest user to guest tenant

#### API Endpoint
```
POST /api/v1/core/auth/guest-login/   # One-click guest access
```

**Response**:
```json
{
  "token": "auth-token-here",
  "user": {
    "id": 2,
    "username": "guest",
    "email": "guest@guest.projectmeats.local",
    "is_staff": true,
    "is_superuser": false
  },
  "tenant": {
    "id": "uuid-here",
    "name": "Guest Demo Organization",
    "slug": "guest-demo",
    "role": "admin",
    "is_guest": true
  }
}
```

## 📚 Documentation

### New Documentation Files
- `INVITE_ONLY_SYSTEM.md` - Complete invitation system guide
- `IMPLEMENTATION_SUMMARY_INVITE_SYSTEM.md` - Implementation details
- `GUEST_MODE_IMPLEMENTATION.md` - Complete guest mode guide
- `IMPLEMENTATION_SUMMARY_GUEST_MODE.md` - Implementation details
- `GUEST_MODE_QUICK_REF.md` - Quick reference for guest mode
- `AUTHENTICATION_EXPLANATION.md` - Authentication flow overview
- `DJANGO_STAFF_PERMISSIONS_EXPLAINED.md` - Detailed permission model explanation

### Updated Documentation
- `.github/copilot-log.md` - Added lessons learned from implementation

## 🧪 Testing

### Automated Tests
```bash
# Test invitation system
python test_invitations.py

# Test guest mode with security verification
python test_guest_mode.py
```

### Test Results
✅ All tests passing with updated security expectations
✅ Guest mode verified with tenant isolation
✅ Invitation system validated with proper constraints
✅ Security boundaries confirmed (staff but not superuser)

### Security Verification Checklist
- ✅ Guest is NOT superuser (no system-wide access)
- ✅ Guest IS staff (can access Django admin for testing)
- ✅ Guest has admin role in tenant (can manage tenant data)
- ✅ Guest cannot access other tenants (isolation verified)
- ✅ Invitation tokens are unique and time-limited
- ✅ No direct signup (all users must be invited)

## 🚀 Deployment Checklist

### Development (✅ Completed)
- [x] Create invitation model and apply migration
- [x] Implement invitation serializers and views
- [x] Create guest mode management command
- [x] Implement guest login endpoint
- [x] Update regular login to return tenants
- [x] Disable direct signup
- [x] Create comprehensive documentation
- [x] Test all functionality locally
- [x] Verify security boundaries
- [x] Update test scripts

### UAT/Staging (📋 Pending)
- [ ] Apply migration 0002 to UAT database
- [ ] Run `python manage.py create_guest_tenant` on UAT
- [ ] Test invitation creation and signup flow
- [ ] Test guest login endpoint
- [ ] Verify guest user has Django admin access
- [ ] Verify guest cannot access system-wide settings
- [ ] Test tenant isolation (guest can't see other tenants)
- [ ] Test CRUD operations as guest
- [ ] Verify frontend "Try as Guest" button integration

### Production (📋 Pending - Requires Approval)
- [ ] CI/CD workflow approvals completed
- [ ] Backup production database before migration
- [ ] Apply migration 0002 to production database
- [ ] Run `python manage.py create_guest_tenant` on production
- [ ] Monitor for any migration issues
- [ ] Verify guest mode works in production
- [ ] Test invitation flow in production
- [ ] Monitor error logs for any issues

## 🔄 Migration Details

**Migration 0002**: `backend/apps/tenants/migrations/0002_alter_tenant_contact_phone_tenantinvitation_and_more.py`

**What it does**:
1. Alters `Tenant.contact_phone` field type (to TextField)
2. Creates `TenantInvitation` model with all fields and constraints
3. Adds indexes for performance (email, status, created_at, expires_at)

**Rollback**: Safe to rollback - no data loss (new table only)

**Data Preservation**: Existing tenant and user data unaffected

## 📊 Permissions Comparison

| Permission | Guest User | Regular User | Superuser |
|------------|------------|--------------|-----------|
| Access Django Admin | ✅ (Testing) | ❌ | ✅ |
| System Settings | ❌ | ❌ | ✅ |
| Manage Users (system) | ❌ | ❌ | ✅ |
| Create Tenant | ❌ | ✅ | ✅ |
| Delete Tenant | ❌ | ✅ (owner) | ✅ |
| Manage Users (in tenant) | ✅ | ✅ (admin/owner) | ✅ |
| CRUD Records (in tenant) | ✅ | ✅ | ✅ |
| View Other Tenants | ❌ | ✅ (if member) | ✅ |

## 🎓 Lessons Learned

### What Worked Well
- Separating invitation logic into dedicated files (invitation_*.py)
- Creating automated test scripts for verification
- Comprehensive documentation with multiple quick references
- Staff permissions provide valuable testing capability without compromising security

### Challenges & Solutions
- **Challenge**: Initial design had `is_staff=False`, limiting testing capability
- **Solution**: Updated to `is_staff=True` for Django admin access while maintaining `is_superuser=False` for security

### Future Improvements
1. Implement periodic cleanup of guest tenant data
2. Add rate limiting for guest login endpoint
3. Consider session-based guest accounts for better isolation
4. Add progressive feature unlock for guest users
5. Implement invitation resend functionality

## 🔗 Related Documentation

- See `AUTHENTICATION_EXPLANATION.md` for auth flow overview
- See `DJANGO_STAFF_PERMISSIONS_EXPLAINED.md` for permission model details
- See `INVITE_ONLY_SYSTEM.md` for invitation system usage
- See `GUEST_MODE_IMPLEMENTATION.md` for guest mode setup

## ✅ Acceptance Criteria

- [x] All users must be tied to a tenant (no orphaned users)
- [x] User creation restricted to invite-only
- [x] Guest mode provides one-click demo access
- [x] Guest user has staff permissions for testing
- [x] Guest user is NOT superuser (no system-wide access)
- [x] Tenant isolation enforced for all users
- [x] Invitation tokens are unique, time-limited, single-use
- [x] No direct signup endpoint (disabled)
- [x] Comprehensive documentation created
- [x] Automated tests verify security boundaries
- [x] Migration applied successfully in development
- [x] All tests passing

## 👥 Reviewers

Please verify:
1. Migration safety and rollback procedure
2. Security boundaries (staff vs superuser permissions)
3. Tenant isolation enforcement
4. Invitation system validation logic
5. Guest mode test script results
6. Documentation completeness

---

**Status**: Ready for UAT deployment
**Branch**: `development`
**Commit**: `b425da2`
