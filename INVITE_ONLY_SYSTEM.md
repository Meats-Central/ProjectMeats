# Tenant Invite-Only User Creation System

## 🎯 Overview

This document explains how ProjectMeats implements an **invite-only user creation system** that ensures:

1. ✅ **All users are tied to a tenant** - No orphan users
2. ✅ **Invite-only registration** - No open signups
3. ✅ **Role-based access** - Users invited with specific roles
4. ✅ **Tenant isolation** - Users can only access their tenant's data

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   Invitation Flow                           │
└─────────────────────────────────────────────────────────────┘

1. Tenant Admin Creates Invitation
   ↓
2. Invitation Record Created with Token
   ↓
3. Email Sent to Invitee (with token link)
   ↓
4. Invitee Clicks Link & Signs Up
   ↓
5. User Created & Automatically Linked to Tenant
   ↓
6. Invitation Marked as "Accepted"
```

### Database Models

#### 1. **Tenant** (Existing)
```python
- id (UUID)
- name
- slug
- contact_email
- is_active
- created_at
```

#### 2. **TenantUser** (Existing)
```python
- tenant (FK to Tenant)
- user (FK to User)
- role (owner/admin/manager/user/readonly)
- is_active
- created_at
```

#### 3. **TenantInvitation** (NEW)
```python
- id (UUID)
- token (unique 64-char string)
- tenant (FK to Tenant)
- email (email being invited)
- role (role user will have)
- invited_by (FK to User who sent invite)
- status (pending/accepted/expired/revoked)
- expires_at (default: 7 days)
- accepted_at
- accepted_by (FK to User created)
- message (optional personal message)
```

---

## 🔐 Security Model

### Who Can Invite Users?

Only **Tenant Admins** and **Tenant Owners** can create invitations.

```python
# Permission check in view
tenant_user = TenantUser.objects.filter(
    tenant=tenant,
    user=request.user,
    role__in=['admin', 'owner'],  # ← Only admin/owner
    is_active=True
).first()
```

### Invitation Security Features

1. **Unique Tokens**: Each invitation has a cryptographically secure token
2. **Expiration**: Invitations expire after 7 days (configurable)
3. **One-Time Use**: Token invalid after acceptance
4. **Email Verification**: User must sign up with invited email
5. **Revocable**: Admins can revoke pending invitations

---

## 📋 API Endpoints

### 1. Create Invitation

**Endpoint**: `POST /api/v1/tenants/invitations/`

**Permission**: Tenant Admin/Owner only

**Request**:
```json
{
  "email": "newuser@example.com",
  "role": "user",
  "message": "Welcome to our team!",
  "expires_at": "2025-10-19T00:00:00Z"  // Optional
}
```

**Response**:
```json
{
  "id": "uuid",
  "email": "newuser@example.com",
  "role": "user",
  "status": "pending",
  "token": "secure-token-here",
  "tenant_name": "Acme Corp",
  "invited_by_username": "admin",
  "created_at": "2025-10-12T10:00:00Z",
  "expires_at": "2025-10-19T10:00:00Z"
}
```

**Validation**:
- ✅ Email not already a member of tenant
- ✅ No pending invitation exists for same email
- ✅ User is admin/owner of the tenant

---

### 2. List Invitations

**Endpoint**: `GET /api/v1/tenants/invitations/`

**Permission**: Authenticated (sees own tenant's invitations)

**Response**:
```json
[
  {
    "id": "uuid",
    "email": "user@example.com",
    "role": "manager",
    "status": "pending",
    "tenant_name": "Acme Corp",
    "invited_by_username": "admin",
    "is_expired_status": false,
    "is_valid_status": true,
    "created_at": "2025-10-12T10:00:00Z",
    "expires_at": "2025-10-19T10:00:00Z"
  }
]
```

---

### 3. Validate Invitation (Public)

**Endpoint**: `GET /api/v1/tenants/invitations/validate/?token=<token>`

**Permission**: Public (AllowAny)

**Purpose**: Check if invitation is valid before signup

**Response** (Valid):
```json
{
  "valid": true,
  "email": "newuser@example.com",
  "role": "user",
  "tenant": {
    "name": "Acme Corp",
    "slug": "acme-corp"
  },
  "message": "Welcome to our team!",
  "expires_at": "2025-10-19T10:00:00Z"
}
```

**Response** (Invalid):
```json
{
  "error": "This invitation has expired"
}
```

---

### 4. Sign Up with Invitation

**Endpoint**: `POST /api/v1/auth/signup-with-invitation/`

**Permission**: Public (AllowAny) - Replaces open signup

**Request**:
```json
{
  "invitation_token": "secure-token-from-email",
  "username": "johndoe",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response**:
```json
{
  "token": "auth-token-for-login",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "newuser@example.com",
    "first_name": "John",
    "last_name": "Doe"
  },
  "tenant": {
    "id": "tenant-uuid",
    "name": "Acme Corp",
    "slug": "acme-corp"
  },
  "role": "user"
}
```

**What Happens**:
1. Invitation validated (exists, pending, not expired)
2. User created with email from invitation
3. TenantUser record created with role from invitation
4. Invitation marked as "accepted"
5. Auth token generated for immediate login

---

### 5. Resend Invitation

**Endpoint**: `POST /api/v1/tenants/invitations/{id}/resend/`

**Permission**: Tenant Admin/Owner

**Purpose**: Extend expiration and resend email

**Response**:
```json
{
  "id": "uuid",
  "status": "pending",
  "expires_at": "2025-10-26T10:00:00Z"  // Extended by 7 days
}
```

---

### 6. Revoke Invitation

**Endpoint**: `POST /api/v1/tenants/invitations/{id}/revoke/`

**Permission**: Tenant Admin/Owner

**Response**:
```json
{
  "status": "Invitation revoked"
}
```

---

## 🚀 Implementation Steps

### Phase 1: Database Migration

```bash
# 1. Add TenantInvitation model to tenants/models.py
python manage.py makemigrations tenants

# 2. Review migration
python manage.py sqlmigrate tenants 0XXX

# 3. Apply migration
python manage.py migrate
```

### Phase 2: Update URLs

**Add to `backend/apps/tenants/urls.py`**:
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tenants.invitation_views import (
    TenantInvitationViewSet,
    signup_with_invitation,
    validate_invitation
)

router = DefaultRouter()
router.register(r'invitations', TenantInvitationViewSet, basename='tenant-invitation')

urlpatterns = [
    path('', include(router.urls)),
    path('invitations/validate/', validate_invitation, name='validate-invitation'),
]
```

**Add to `backend/apps/core/urls.py`**:
```python
from apps.tenants.invitation_views import signup_with_invitation

urlpatterns = [
    path("auth/login/", views.login, name="login"),
    path("auth/signup-with-invitation/", signup_with_invitation, name="signup-invitation"),  # NEW
    # path("auth/signup/", views.signup, name="signup"),  # DISABLE open signup
    path("auth/logout/", views.logout, name="logout"),
]
```

### Phase 3: Disable Open Signup (CRITICAL)

**Option A: Comment out** (for gradual migration):
```python
# @api_view(["POST"])
# @permission_classes([AllowAny])
# def signup(request):
#     """DEPRECATED: Use signup_with_invitation instead"""
#     return Response(
#         {"error": "Open signup is disabled. Please use an invitation link."},
#         status=status.HTTP_403_FORBIDDEN
#     )
```

**Option B: Return error** (immediate enforcement):
```python
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """Open signup disabled - invitation required."""
    return Response(
        {
            "error": "Registration is invite-only. Please contact your administrator for an invitation."
        },
        status=status.HTTP_403_FORBIDDEN
    )
```

### Phase 4: Frontend Updates

**Update signup form**:
```typescript
// OLD: /signup
// NEW: /signup?token=<invitation-token>

// 1. Extract token from URL query params
const searchParams = new URLSearchParams(window.location.search);
const invitationToken = searchParams.get('token');

// 2. Validate invitation first
const validateInvitation = async (token: string) => {
  const response = await axios.get(
    `/api/v1/tenants/invitations/validate/?token=${token}`
  );
  return response.data;
};

// 3. Include token in signup request
const signup = async (userData: SignupData) => {
  const response = await axios.post('/api/v1/auth/signup-with-invitation/', {
    invitation_token: invitationToken,
    username: userData.username,
    password: userData.password,
    first_name: userData.firstName,
    last_name: userData.lastName,
  });
  return response.data;
};
```

---

## 🎨 User Experience Flow

### 1. Admin Invites User

```
Admin Dashboard
  → "Invite User" Button
  → Form: Email, Role, Optional Message
  → Click "Send Invitation"
  → Backend creates TenantInvitation
  → Email sent to invitee
```

### 2. User Receives Email

```
Subject: You're invited to join Acme Corp on ProjectMeats!

Hi there,

John Doe has invited you to join Acme Corp as a Manager.

Message: "Welcome to our team!"

Click here to accept:
https://app.meatscentral.com/signup?token=abc123xyz...

This invitation expires on October 19, 2025.
```

### 3. User Signs Up

```
User clicks link
  → Redirects to /signup?token=abc123xyz
  → Frontend validates token (shows tenant name, role)
  → User fills in: Username, Password, Name
  → Submits signup form with token
  → Backend:
      - Validates invitation
      - Creates user account
      - Links to tenant with role
      - Marks invitation as accepted
  → User automatically logged in
  → Redirected to dashboard
```

---

## 🔄 Existing Users

### What About Current Users?

Users created before invitation system can be:

1. **Left as-is**: They continue working
2. **Manually associated**: Admin creates TenantUser records
3. **Migration script**: Auto-associate based on existing data

**Migration Script Example**:
```python
# Create TenantUser for users without tenants
from django.contrib.auth.models import User
from apps.tenants.models import Tenant, TenantUser

# Assuming you have a "default" tenant or can determine tenant from user data
default_tenant = Tenant.objects.get(slug='main-company')

users_without_tenant = User.objects.exclude(
    tenants__isnull=False
)

for user in users_without_tenant:
    TenantUser.objects.create(
        tenant=default_tenant,
        user=user,
        role='user',  # or determine from user.is_staff, etc.
        is_active=True
    )
```

---

## 🛡️ Security Best Practices

### 1. Token Security
- ✅ Tokens are 48-byte URL-safe strings (384 bits of entropy)
- ✅ Stored hashed in database (optional enhancement)
- ✅ Single-use only
- ✅ Time-limited (7 days default)

### 2. Email Verification
- ✅ User must use email from invitation
- ✅ Prevents email spoofing
- ✅ Ensures invitee owns the email

### 3. Rate Limiting
Consider adding:
```python
# In invitation creation view
from django.core.cache import cache

def create(self, request, *args, **kwargs):
    # Rate limit: max 10 invitations per hour per user
    cache_key = f'invite_limit:{request.user.id}'
    count = cache.get(cache_key, 0)
    
    if count >= 10:
        return Response(
            {'error': 'Invitation limit reached. Try again later.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    cache.set(cache_key, count + 1, 3600)  # 1 hour
    return super().create(request, *args, **kwargs)
```

### 4. Audit Logging
```python
logger.info(
    f"User {user.username} invited {email} to {tenant.name} "
    f"with role {role}"
)
```

---

## 📊 Database Constraints

### Unique Constraints

1. **Unique Token**: Each invitation has unique token
```python
token = models.CharField(max_length=64, unique=True)
```

2. **One Pending Invitation Per Email Per Tenant**:
```python
constraints = [
    models.UniqueConstraint(
        fields=['tenant', 'email'],
        condition=models.Q(status='pending'),
        name='unique_pending_invitation_per_tenant_email'
    )
]
```

3. **Unique User Per Tenant**:
```python
# In TenantUser
unique_together = ["tenant", "user"]
```

---

## 🧪 Testing Scenarios

### Test Case 1: Happy Path
```python
# 1. Admin creates invitation
# 2. User signs up with token
# 3. User automatically linked to tenant
# 4. User can access tenant data
# 5. Invitation marked as "accepted"
```

### Test Case 2: Expired Invitation
```python
# 1. Create invitation with expires_at in past
# 2. Attempt signup with token
# 3. Should return "invitation has expired"
# 4. Invitation status changed to "expired"
```

### Test Case 3: Already Accepted
```python
# 1. User signs up with token
# 2. Another user tries same token
# 3. Should return "invitation already accepted"
```

### Test Case 4: Duplicate Email
```python
# 1. User exists in tenant
# 2. Admin tries to invite same email
# 3. Should return "user already a member"
```

---

## 🎓 Key Takeaways

### ✅ Benefits

1. **No Orphan Users**: Every user must have a tenant
2. **Controlled Growth**: Only admins can add users
3. **Role Assignment**: Users invited with specific permissions
4. **Security**: No open registration = lower spam/abuse
5. **Audit Trail**: Track who invited whom and when

### ⚠️ Trade-offs

1. **Less Convenient**: Users can't self-register
2. **Admin Overhead**: Requires manual invitation process
3. **Email Dependency**: Must have working email system

### 🔄 Alternatives Considered

1. **Open Signup + Manual Approval**: Users sign up, admin approves
   - ❌ Creates orphan users waiting for approval
   
2. **Domain-Based Auto-Join**: Anyone with @company.com joins automatically
   - ❌ Less control, potential security risk
   
3. **Invitation Codes** (Simple): One reusable code per tenant
   - ❌ Code can be shared/leaked

4. **Invite-Only** (Chosen): One-time tokens per email
   - ✅ Best security and control

---

## 📝 Summary

The invite-only system ensures **all users are tied to tenants** by:

1. **Requiring invitation tokens** for signup
2. **Automatically creating TenantUser** on acceptance
3. **Validating email matches** invitation email
4. **Assigning role** from invitation
5. **Preventing open signups** entirely

This guarantees proper multi-tenant isolation and prevents orphan users in the system.

---

## 🚀 Next Steps

1. ✅ Create migration for TenantInvitation model
2. ✅ Add URL routes for invitation endpoints
3. ✅ Disable/modify open signup endpoint
4. ✅ Update frontend signup flow
5. ✅ Implement email sending (optional for MVP)
6. ✅ Add admin UI for managing invitations
7. ✅ Test thoroughly in development
8. ✅ Deploy to staging/UAT
9. ✅ Migrate existing users (if any)
10. ✅ Deploy to production

---

**Implementation Status**: 🟡 Code Ready (Migration Needed)  
**Documentation**: 📚 Complete  
**Testing**: 🧪 Required  
