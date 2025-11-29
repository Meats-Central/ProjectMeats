# Guest Mode Implementation

## Overview

Guest mode allows users to try ProjectMeats without creating an account. Guest users are automatically assigned to a dedicated "Guest Demo Organization" tenant with admin-level permissions, but they do NOT have superuser privileges.

---

## Architecture

### Components

1. **Guest User**: A standard Django user with username `guest`
   - Username: `guest`
   - Password: `guest123` (configurable)
   - Permissions: Regular user (NOT staff, NOT superuser)
   - Email: `guest@guest.projectmeats.local`

2. **Guest Tenant**: A dedicated tenant for guest users
   - Name: `Guest Demo Organization` (configurable)
   - Slug: `guest-demo` (configurable)
   - Marked as trial: `is_trial=True`
   - Special settings:
     ```json
     {
       "is_guest_tenant": true,
       "allow_data_reset": true,
       "max_records": 100,
       "description": "Demo organization for guest users to explore ProjectMeats features"
     }
     ```

3. **TenantUser Association**: Links guest user to guest tenant
   - Role: `admin` (NOT `owner` to prevent tenant deletion)
   - Permissions: Full CRUD within tenant, cannot delete tenant

---

## Setup

### Automatic Setup (Recommended)

Run the management command to create guest tenant and user:

```bash
# Default setup (guest/guest123)
python manage.py create_guest_tenant

# Custom credentials
python manage.py create_guest_tenant \
  --username demo \
  --password demo456 \
  --tenant-name "Demo Company" \
  --tenant-slug demo-company
```

**Command Options:**
- `--username`: Guest username (default: `guest`)
- `--password`: Guest password (default: `guest123`)
- `--tenant-name`: Tenant display name (default: `Guest Demo Organization`)
- `--tenant-slug`: Tenant slug (default: `guest-demo`)

**Output:**
```
✓ Created guest user: guest
✓ Created guest tenant: Guest Demo Organization (guest-demo)
✓ Associated guest with Guest Demo Organization (role: admin)

============================================================
GUEST MODE SETUP COMPLETE
============================================================

Guest Username: guest
Guest Password: guest123
Tenant Name: Guest Demo Organization
Tenant Slug: guest-demo
Role: admin (tenant-level)
Superuser: No

Users can now log in with these credentials to try ProjectMeats!
```

### Manual Setup

If you prefer manual setup:

```python
from django.contrib.auth.models import User
from apps.tenants.models import Tenant, TenantUser

# 1. Create guest user
guest = User.objects.create_user(
    username='guest',
    email='guest@guest.projectmeats.local',
    password='guest123',
    first_name='Guest',
    last_name='User',
    is_staff=True,  # Can access Django admin for testing
    is_superuser=False  # NO system-wide permissions
)

# 2. Create guest tenant
tenant = Tenant.objects.create(
    name='Guest Demo Organization',
    slug='guest-demo',
    contact_email='admin@guest-demo.projectmeats.local',
    is_trial=True,
    created_by=guest,
    settings={
        'is_guest_tenant': True,
        'allow_data_reset': True,
        'max_records': 100
    }
)

# 3. Associate guest with tenant as admin
TenantUser.objects.create(
    tenant=tenant,
    user=guest,
    role='admin',
    is_active=True
)
```

---

## API Usage

### Guest Login Endpoint

**Endpoint**: `POST /api/v1/core/auth/guest-login/`

**Permission**: AllowAny (Public)

**Request**: No parameters required

```bash
curl -X POST http://localhost:8000/api/v1/core/auth/guest-login/
```

**Response**:
```json
{
  "token": "auth-token-here",
  "user": {
    "id": 2,
    "username": "guest",
    "email": "guest@guest.projectmeats.local",
    "first_name": "Guest",
    "last_name": "User",
    "is_staff": true,
    "is_superuser": false,
    "is_active": true
  },
  "tenant": {
    "id": "uuid-here",
    "name": "Guest Demo Organization",
    "slug": "guest-demo",
    "role": "admin",
    "is_guest": true
  },
  "message": "Welcome to ProjectMeats! You are logged in as a guest user."
}
```

**Error Responses**:

```json
// Guest user not found
{
  "error": "Guest account not found. Please run: python manage.py create_guest_tenant",
  "setup_command": "python manage.py create_guest_tenant"
}

// Guest account disabled
{
  "error": "Guest account is currently disabled"
}

// Guest tenant not configured
{
  "error": "Guest tenant not configured. Please run: python manage.py create_guest_tenant"
}
```

### Regular Login (with Guest)

Guest users can also log in via the regular login endpoint:

**Endpoint**: `POST /api/v1/core/auth/login/`

```json
{
  "username": "guest",
  "password": "guest123"
}
```

**Response** (now includes tenants):
```json
{
  "token": "auth-token-here",
  "user": {
    "id": 2,
    "username": "guest",
    "email": "guest@guest.projectmeats.local",
    "first_name": "Guest",
    "last_name": "User",
    "is_staff": true,
    "is_superuser": false,
    "is_active": true
  },
  "tenants": [
    {
      "tenant__id": "uuid-here",
      "tenant__name": "Guest Demo Organization",
      "tenant__slug": "guest-demo",
      "role": "admin"
    }
  ]
}
```

---

## Frontend Integration

### Guest Login Button

Add a "Try as Guest" button to your login page:

```typescript
// LoginPage.tsx
const handleGuestLogin = async () => {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/v1/core/auth/guest-login/'
    );
    
    const { token, user, tenant } = response.data;
    
    // Store auth data
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));
    localStorage.setItem('currentTenant', JSON.stringify(tenant));
    
    // Redirect to dashboard
    navigate('/dashboard');
    
    // Show welcome message
    toast.success(response.data.message);
  } catch (error) {
    console.error('Guest login failed:', error);
    toast.error('Guest mode is currently unavailable');
  }
};

// JSX
<Button 
  variant="outlined" 
  onClick={handleGuestLogin}
  fullWidth
>
  Try as Guest
</Button>
```

### UI Indicators

Show visual indicators when user is in guest mode:

```typescript
// Check if user is guest
const isGuest = user?.username === 'guest';

// Or check tenant settings
const isGuestTenant = currentTenant?.settings?.is_guest_tenant === true;

// Show banner
{isGuest && (
  <Alert severity="info" sx={{ mb: 2 }}>
    You are using ProjectMeats in guest mode. 
    <Link href="/signup">Create an account</Link> for full access.
  </Alert>
)}
```

### Feature Limitations

Optionally limit features in guest mode:

```typescript
// Disable tenant deletion for guest
const canDeleteTenant = !isGuestTenant && userRole === 'owner';

// Limit record creation
const maxRecords = isGuestTenant ? 100 : Infinity;

if (isGuestTenant && recordCount >= maxRecords) {
  toast.warning('Guest mode limited to 100 records. Sign up for unlimited access.');
  return;
}
```

---

## Security Considerations

### ✅ Security Features

1. **Not Superuser**: Guest user CANNOT access system-level settings or bypass permissions
2. **Is Staff (Testing Only)**: Guest user CAN access Django admin for testing/demo purposes
   - Can view and manage tenant-scoped data via admin interface
   - Cannot manage users, permissions, or system settings (requires superuser)
   - All data still restricted to guest tenant only
3. **Tenant-Scoped**: Guest can only access data within guest tenant
4. **Admin Role**: Guest has admin permissions within tenant, NOT owner (prevents tenant deletion)
5. **Trial Status**: Guest tenant marked as trial for easy identification
6. **Isolated Data**: Guest tenant data is completely separate from other tenants

### ⚠️ Considerations

1. **Shared Account**: All guest users share the same account
   - Data visible to all guest users
   - Changes made by one guest affect all others
   - Consider periodic data cleanup

2. **No Password Reset**: Guest account password is public
   - Don't allow sensitive data in guest mode
   - Encourage users to sign up for private accounts

3. **Rate Limiting**: Consider rate limiting guest login endpoint to prevent abuse

4. **Data Cleanup**: Implement periodic cleanup of guest tenant data:
   ```python
   # Scheduled task (e.g., daily at midnight)
   from apps.tenants.models import Tenant
   from apps.customers.models import Customer
   
   guest_tenant = Tenant.objects.get(slug='guest-demo')
   
   # Delete old guest data (older than 7 days)
   Customer.objects.filter(
       tenant=guest_tenant,
       created_on__lt=timezone.now() - timedelta(days=7)
   ).delete()
   ```

---

## Permissions Summary

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

**Note**: Guest user has `is_staff=True` to access Django admin for testing/demo purposes, but `is_superuser=False` prevents system-wide permissions. Guest can only manage data within their assigned guest tenant.

---

## Testing

### Manual Test

```bash
# 1. Create guest setup
python manage.py create_guest_tenant

# 2. Test guest login API
curl -X POST http://localhost:8000/api/v1/core/auth/guest-login/

# 3. Test regular login with guest credentials
curl -X POST http://localhost:8000/api/v1/core/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "guest", "password": "guest123"}'

# 4. Verify tenant association
curl -H "Authorization: Token <guest-token>" \
  http://localhost:8000/api/v1/tenants/api/tenants/my_tenants/

# 5. Test CRUD operations
curl -H "Authorization: Token <guest-token>" \
  http://localhost:8000/api/v1/customers/
```

### Automated Tests (Future)

```python
# test_guest_mode.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from apps.tenants.models import Tenant, TenantUser

class GuestModeTests(TestCase):
    
    def setUp(self):
        # Run create_guest_tenant command
        from django.core.management import call_command
        call_command('create_guest_tenant')
        
        self.client = APIClient()
    
    def test_guest_login_creates_token(self):
        response = self.client.post('/api/v1/core/auth/guest-login/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tenant', response.data)
    
    def test_guest_user_is_not_superuser(self):
        response = self.client.post('/api/v1/core/auth/guest-login/')
        user_data = response.data['user']
        self.assertFalse(user_data['is_superuser'])
        self.assertFalse(user_data['is_staff'])
    
    def test_guest_user_has_admin_role(self):
        response = self.client.post('/api/v1/core/auth/guest-login/')
        tenant_data = response.data['tenant']
        self.assertEqual(tenant_data['role'], 'admin')
    
    def test_guest_can_access_tenant_data(self):
        # Login as guest
        response = self.client.post('/api/v1/core/auth/guest-login/')
        token = response.data['token']
        
        # Access tenant data
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        response = self.client.get('/api/v1/customers/')
        self.assertEqual(response.status_code, 200)
```

---

## Deployment Checklist

### Development
- [x] Create guest tenant management command
- [x] Implement guest login endpoint
- [x] Update regular login to return tenants
- [x] Add URL route for guest login
- [x] Test guest login flow
- [x] Document guest mode

### UAT/Staging
- [ ] Run `python manage.py create_guest_tenant`
- [ ] Test guest login via API
- [ ] Verify guest user has admin role (not owner)
- [ ] Confirm guest is NOT superuser
- [ ] Test frontend "Try as Guest" button
- [ ] Verify tenant isolation (guest can't see other tenants)

### Production
- [ ] Run `python manage.py create_guest_tenant`
- [ ] Configure rate limiting for guest login
- [ ] Set up periodic data cleanup for guest tenant
- [ ] Add monitoring for guest tenant usage
- [ ] Update user documentation with guest mode instructions
- [ ] Add "Try as Guest" button to login page

---

## Troubleshooting

### Guest Login Returns 404

**Error**: `Guest account not found`

**Solution**:
```bash
python manage.py create_guest_tenant
```

### Guest Login Returns 500

**Error**: `Guest tenant not configured`

**Cause**: Guest user exists but not associated with tenant

**Solution**:
```bash
# Delete and recreate
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='guest').delete()
>>> exit()
python manage.py create_guest_tenant
```

### Guest Can't Access Data

**Error**: 403 Forbidden on API calls

**Check**:
1. Token is valid
2. TenantUser association exists
3. Middleware is setting `request.tenant`

**Solution**:
```python
# Check tenant association
python manage.py shell
>>> from apps.tenants.models import TenantUser
>>> TenantUser.objects.filter(user__username='guest')
```

---

## Future Enhancements

### 1. Multiple Guest Sessions
Track individual guest sessions to prevent data conflicts:
```python
# Create unique guest user per session
guest_user = User.objects.create_user(
    username=f'guest_{session_id}',
    email=f'guest_{session_id}@projectmeats.local'
)
```

### 2. Session-Based Data Isolation
Create separate tenant per guest session with auto-cleanup

### 3. Guest Mode Analytics
Track:
- Number of guest logins per day
- Features used in guest mode
- Conversion rate (guest → signup)

### 4. Guest Mode Limitations UI
Display limitations prominently:
- "100 records max in guest mode"
- "Data resets every 24 hours"
- "Upgrade for unlimited access"

### 5. Progressive Disclosure
Start with limited features, unlock more as guest explores

---

## Summary

Guest mode provides a **zero-friction way** for users to try ProjectMeats:

✅ **No signup required** - Instant access with one click  
✅ **Tenant-scoped** - Full multi-tenancy support  
✅ **Admin permissions** - Try all features within guest tenant  
✅ **Secure** - NOT superuser, isolated from other tenants  
✅ **Easy setup** - One management command  
✅ **Frontend-ready** - Simple API integration  

**Implementation Date**: October 12, 2025  
**Status**: ✅ Complete (Backend) | 📋 Pending (Frontend UI)  
**Developer**: GitHub Copilot  
