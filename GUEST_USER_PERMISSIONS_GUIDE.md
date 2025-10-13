# Guest User Permissions Guide

## Overview

The guest user is designed to provide **tenant-scoped administrative access** for testing and demo purposes without granting system-wide superuser privileges. This document explains the two-layer permission model and what the guest user can and cannot access.

---

## Permission Architecture

### Two-Layer Security Model

ProjectMeats uses a **two-layer permission system**:

1. **Django Level** (System Access)
   - `is_staff=True` - Grants access to Django admin interface
   - `is_superuser=False` - Prevents system-wide administrative access

2. **Application Level** (Tenant Scope)
   - `TenantUser.role='admin'` - Grants admin privileges within the guest tenant
   - All queries automatically filtered by tenant context

---

## What Guest User CAN Access

### ✅ Django Admin Interface

The guest user has **full CRUD access** to the following tenant-scoped models:

| Model | Permissions | Description |
|-------|-------------|-------------|
| **Customers** | view, add, change, delete | Customer management within guest tenant |
| **Suppliers** | view, add, change, delete | Supplier management within guest tenant |
| **Contacts** | view, add, change, delete | Contact management within guest tenant |
| **Products** | view, add, change, delete | Product catalog within guest tenant |
| **Purchase Orders** | view, add, change, delete | Purchase order management |
| **Sales Orders** | view, add, change, delete | Sales order management |
| **Invoices** | view, add, change, delete | Invoice management |
| **Accounts Receivables** | view, add, change, delete | AR management |
| **Carriers** | view, add, change, delete | Carrier management |
| **Plants** | view, add, change, delete | Plant/facility management |

**Total: 40 Permissions** (4 per model × 10 models)

### ✅ Frontend Access

- **Full CRUD via API/Frontend** - All endpoints work normally
- **Profile Dropdown** - "View as Admin" button visible and functional
- **Tenant Context** - Automatically set to "Guest Demo Organization"

### ✅ Tenant-Scoped Data

All data is **automatically filtered** by tenant:
- Only sees data belonging to "Guest Demo Organization"
- Cannot access other tenants' data (enforced by `TenantManager.for_tenant()`)
- Queries use `Customer.objects.for_tenant(request.tenant)`

---

## What Guest User CANNOT Access

### ❌ System Administration

The guest user is **NOT a superuser** and cannot:

| Restricted Area | Reason |
|----------------|---------|
| **User Management** | Cannot create/edit/delete users |
| **Group Management** | Cannot manage Django groups/permissions |
| **Tenant Management** | Cannot create/edit/delete tenants |
| **TenantUser Management** | Cannot modify tenant memberships |
| **System Settings** | Cannot access Django sites, sessions, etc. |
| **Other Tenants' Data** | Strict tenant isolation enforced |

### ❌ Superuser-Only Functions

- Cannot access raw SQL console
- Cannot manage Django's internal tables
- Cannot override tenant filtering
- Cannot impersonate other users
- Cannot modify system-wide configurations

---

## How Tenant Isolation Works

### Backend Enforcement

#### 1. QuerySet Filtering (`get_queryset`)

```python
def get_queryset(self):
    """Filter by tenant automatically."""
    if hasattr(self.request, 'tenant') and self.request.tenant:
        return Customer.objects.for_tenant(self.request.tenant)
    
    # Development: Return all (DEBUG=True)
    if settings.DEBUG:
        return Customer.objects.all()
    
    # Production: No tenant = no data (security)
    return Customer.objects.none()
```

#### 2. Manager Method (`for_tenant`)

```python
def for_tenant(self, tenant):
    """Filter queryset for specific tenant."""
    if tenant:
        return self.filter(tenant=tenant)
    return self.none()
```

#### 3. Middleware (`TenantMiddleware`)

- Sets `request.tenant` from user's `TenantUser` relationship
- All API calls automatically scoped to guest tenant
- No manual tenant selection needed

### Django Admin Filtering

**Important:** Current Django admin implementation does NOT enforce tenant filtering in list views. This is a known limitation.

**Recommendation for Production:**
1. Create custom admin site for tenant admins
2. Override `get_queryset()` in all `ModelAdmin` classes
3. Add tenant context indicators in admin interface
4. Consider using [django-tenant-schemas](https://github.com/bernardopires/django-tenant-schemas) or similar

---

## Testing Guest User Permissions

### Test Scenario 1: Django Admin Access

1. Navigate to `http://localhost:8000/admin/`
2. Login with `guest` / `guest123`
3. **Expected Result:**
   - See 10 model sections (Customers, Suppliers, etc.)
   - Can view/add/change/delete within those sections
   - Cannot see "Users", "Groups", "Tenants" sections

### Test Scenario 2: Frontend Access

1. Navigate to `http://localhost:3000`
2. Login with `guest` / `guest123`
3. Click profile dropdown → "View as Admin"
4. **Expected Result:**
   - Redirects to Django admin
   - Shows login page (need to re-login)
   - After login, see admin interface

### Test Scenario 3: API Access

1. Obtain token: `POST /api/v1/auth/login/` with guest credentials
2. Use token to access: `GET /api/v1/customers/`
3. **Expected Result:**
   - Returns only customers belonging to guest tenant
   - Can create new customers (auto-assigned to guest tenant)
   - Cannot see other tenants' customers

### Test Scenario 4: Cross-Tenant Isolation

1. Login as guest user
2. Try to access another tenant's data (if exists)
3. **Expected Result:**
   - Empty queryset or 404 error
   - Tenant filtering prevents access
   - No error messages exposing other tenants' existence

---

## Environment Behavior

### Development Mode (`DEBUG=True`)

- **Authentication:** Bypassed for easier testing
- **Tenant Creation:** Auto-creates "Development Tenant" if none exists
- **Data Filtering:** Returns all data (no tenant filter)
- **Purpose:** Developer convenience

### Production Mode (`DEBUG=False`)

- **Authentication:** Strictly required (401 if missing token)
- **Tenant Creation:** No auto-creation
- **Data Filtering:** Strict tenant isolation
- **Purpose:** Security and data protection

---

## Permission Grant Implementation

### How Permissions Are Assigned

The `create_guest_tenant` management command automatically grants permissions:

```python
def _grant_permissions(self, user):
    """Grant Django admin permissions for tenant-scoped models."""
    tenant_models = [
        Customer, Supplier, Contact, Product,
        PurchaseOrder, SalesOrder, Invoice,
        AccountsReceivable, Carrier, Plant,
    ]
    
    for model in tenant_models:
        content_type = ContentType.objects.get_for_model(model)
        model_permissions = Permission.objects.filter(content_type=content_type)
        
        for perm in model_permissions:
            user.user_permissions.add(perm)
```

### Re-Running Permission Grant

If permissions need to be reset or updated:

```bash
python manage.py create_guest_tenant
```

**Note:** Command is idempotent - safe to run multiple times.

---

## Security Considerations

### ✅ Safe for Production

- **No Superuser Access:** Guest cannot access system internals
- **Tenant Isolation:** Cannot see other tenants' data
- **Limited Scope:** Only has access to business models
- **Audit Trail:** All actions logged with user context

### ⚠️ Recommendations

1. **Limit Guest Data:** Use `max_records: 100` setting to prevent data bloat
2. **Periodic Cleanup:** Reset guest tenant data regularly
3. **Admin Filtering:** Add tenant filtering to Django admin (see above)
4. **Monitor Activity:** Track guest user actions for abuse
5. **Rate Limiting:** Implement API rate limits for guest tenant

### 🔒 Production Hardening

For production deployments, consider:

1. **Custom Admin Site:**
   ```python
   from django.contrib.admin import AdminSite
   
   class TenantAdminSite(AdminSite):
       def has_permission(self, request):
           return request.user.is_active and request.user.is_staff
   ```

2. **Admin QuerySet Override:**
   ```python
   class CustomerAdmin(admin.ModelAdmin):
       def get_queryset(self, request):
           qs = super().get_queryset(request)
           if not request.user.is_superuser:
               return qs.filter(tenant=request.tenant)
           return qs
   ```

3. **Tenant Context Middleware:**
   ```python
   class TenantContextMiddleware:
       def __call__(self, request):
           if hasattr(request, 'user') and request.user.is_authenticated:
               request.tenant = get_user_tenant(request.user)
   ```

---

## Troubleshooting

### Issue: "You don't have permission to view or edit anything"

**Cause:** Permissions not assigned to guest user

**Solution:**
```bash
python manage.py create_guest_tenant
```

### Issue: Guest sees all tenants' data in admin

**Cause:** Admin doesn't enforce tenant filtering (by design)

**Solution:** Override `get_queryset()` in ModelAdmin classes (see above)

### Issue: "View as Admin" button doesn't appear

**Cause:** User doesn't have `is_staff=True`

**Solution:** Check user in Django admin or re-run `create_guest_tenant`

### Issue: Cannot login to Django admin

**Cause:** Frontend token auth ≠ Django session auth

**Solution:** Login separately at `/admin/` with guest credentials

---

## Summary

**Guest User Permission Model:**

```
┌─────────────────────────────────────────┐
│         Guest User (guest/guest123)     │
├─────────────────────────────────────────┤
│ Django Level:                           │
│   ✓ is_staff = True                     │
│   ✗ is_superuser = False                │
│                                         │
│ Application Level:                      │
│   ✓ TenantUser.role = 'admin'           │
│   ✓ Tenant = 'Guest Demo Organization'  │
│                                         │
│ Permissions (40 total):                 │
│   ✓ Customers (view/add/change/delete)  │
│   ✓ Suppliers (view/add/change/delete)  │
│   ✓ Contacts (view/add/change/delete)   │
│   ✓ Products (view/add/change/delete)   │
│   ✓ Purchase Orders (...)               │
│   ✓ Sales Orders (...)                  │
│   ✓ Invoices (...)                      │
│   ✓ Accounts Receivables (...)          │
│   ✓ Carriers (...)                      │
│   ✓ Plants (...)                        │
│                                         │
│ Restrictions:                           │
│   ✗ User Management                     │
│   ✗ Tenant Management                   │
│   ✗ System Settings                     │
│   ✗ Other Tenants' Data                 │
└─────────────────────────────────────────┘
```

**This provides a secure, tenant-scoped admin experience perfect for demos and testing!** 🎉
