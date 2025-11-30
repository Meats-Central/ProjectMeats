# Guest Mode Quick Reference

## Setup (One Command)

```bash
python manage.py create_guest_tenant
```

**Output**: Creates guest user + guest tenant + admin association

---

## API Endpoints

### Guest Login (Recommended for Frontend)
```bash
POST /api/v1/core/auth/guest-login/

# No body required
# Returns: { token, user, tenant, message }
```

### Regular Login (Also Works)
```bash
POST /api/v1/core/auth/login/
{
  "username": "guest",
  "password": "guest123"
}

# Returns: { token, user, tenants: [...] }
```

---

## Frontend Integration (3 Steps)

### 1. Add Guest Login Button
```typescript
const handleGuestLogin = async () => {
  const response = await axios.post('/api/v1/core/auth/guest-login/');
  const { token, user, tenant } = response.data;
  
  localStorage.setItem('authToken', token);
  localStorage.setItem('user', JSON.stringify(user));
  localStorage.setItem('currentTenant', JSON.stringify(tenant));
  
  navigate('/dashboard');
};

<Button onClick={handleGuestLogin}>Try as Guest</Button>
```

### 2. Show Guest Indicator
```typescript
const isGuest = user?.username === 'guest';
const isGuestTenant = tenant?.settings?.is_guest_tenant === true;

{isGuest && (
  <Alert severity="info">
    Guest Mode - <Link href="/signup">Sign up</Link> for full access
  </Alert>
)}
```

### 3. Optional: Limit Features
```typescript
if (isGuestTenant && recordCount >= 100) {
  toast.warning('Guest mode limited to 100 records');
  return;
}
```

---

## Security Properties

| Property | Guest User |
|----------|-----------|
| Superuser | ❌ No |
| Staff | ❌ No |
| Django Admin Access | ❌ No |
| System Settings | ❌ No |
| Tenant Admin (CRUD in guest tenant) | ✅ Yes |
| Can Delete Guest Tenant | ❌ No |
| Access Other Tenants | ❌ No |

**Summary**: Admin-level permissions WITHIN guest tenant only, NOT system-wide.

---

## Default Credentials

```
Username: guest
Password: guest123
Tenant: Guest Demo Organization (slug: guest-demo)
Role: admin
```

---

## Testing

```bash
# Test setup
python test_guest_mode.py

# Test API
curl -X POST http://localhost:8000/api/v1/core/auth/guest-login/

# Verify security
✓ Guest is NOT superuser (no system-wide access)
✓ Guest IS staff (can access Django admin for testing)
✓ Guest has admin role in tenant
✓ Guest cannot access other tenants
```

---

## Customization

```bash
# Custom guest credentials
python manage.py create_guest_tenant \
  --username demo \
  --password demo456 \
  --tenant-name "Demo Company" \
  --tenant-slug demo-company
```

---

## Troubleshooting

**"Guest account not found"**  
→ Run: `python manage.py create_guest_tenant`

**"Guest tenant not configured"**  
→ Delete guest user and re-run command

**Guest can see other tenants**  
→ Check TenantUser association exists

---

## Production Checklist

- [ ] Run `create_guest_tenant` command
- [ ] Test guest login API
- [ ] Add "Try as Guest" button to frontend
- [ ] Set up rate limiting (10/hour per IP)
- [ ] Configure periodic data cleanup (weekly)
- [ ] Monitor guest login analytics

---

## Documentation

- **Full Guide**: `GUEST_MODE_IMPLEMENTATION.md`
- **Implementation Details**: `IMPLEMENTATION_SUMMARY_GUEST_MODE.md`
- **Management Command**: `backend/apps/core/management/commands/create_guest_tenant.py`
- **API Views**: `backend/apps/core/views.py`
