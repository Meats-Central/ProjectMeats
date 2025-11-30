# Django Staff Permissions Explained

## Overview

In Django, there are three main permission levels at the **user level** (not tenant level):

1. **Regular User** (`is_staff=False`, `is_superuser=False`)
2. **Staff User** (`is_staff=True`, `is_superuser=False`)
3. **Superuser** (`is_staff=True`, `is_superuser=True`)

---

## What `is_staff` Controls

### ✅ Staff Users CAN:

1. **Access Django Admin Interface** (`/admin/`)
   - Can log in at `http://localhost:8000/admin/`
   - See the Django admin dashboard
   - Navigate admin sections

2. **View/Edit Models (with proper permissions)**
   - If given specific model permissions, can CRUD those models in admin
   - Permissions are granular (add, change, delete, view)
   - Example: Can be given permission to edit Customers but not Suppliers

3. **Use Django Admin Tools**
   - Search functionality
   - Filters and sorting
   - Bulk actions
   - Export features

### ❌ Staff Users CANNOT (unless also superuser):

1. **Manage Users and Groups**
   - Cannot create/edit other users (unless given permission)
   - Cannot assign permissions to other users
   
2. **Access ALL Models**
   - Can only access models they have explicit permissions for
   - Example: Staff user without Customer permissions cannot see Customer admin

3. **System-Level Operations**
   - Cannot run Django shell with admin privileges
   - Cannot access system settings without specific permissions
   - Cannot override security restrictions

---

## Comparison Table

| Feature | Regular User | Staff User | Superuser |
|---------|--------------|------------|-----------|
| **Django Admin Login** | ❌ No | ✅ Yes | ✅ Yes |
| **Django Admin Dashboard** | ❌ No | ✅ Yes | ✅ Yes |
| **View All Models in Admin** | ❌ No | ⚠️ Only with permissions | ✅ Yes (automatic) |
| **Create Users** | ❌ No | ⚠️ Only with permission | ✅ Yes (automatic) |
| **Assign Permissions** | ❌ No | ❌ No | ✅ Yes |
| **System Settings** | ❌ No | ⚠️ Only with permission | ✅ Yes |
| **Bypass All Permissions** | ❌ No | ❌ No | ✅ Yes |

---

## In ProjectMeats Context

### Regular User (Guest User)
```python
User(
    username='guest',
    is_staff=False,      # ← Cannot access Django admin
    is_superuser=False   # ← No superuser powers
)
```

**Can do**:
- ✅ Log in to ProjectMeats web/mobile app
- ✅ Access API endpoints (with proper authentication)
- ✅ CRUD operations within their tenant (via API)
- ✅ Use frontend application fully

**Cannot do**:
- ❌ Access Django admin (`/admin/`)
- ❌ View/edit models in admin interface
- ❌ Manage users via admin
- ❌ Access system settings

### Staff User (Hypothetical)
```python
User(
    username='support',
    is_staff=True,       # ← CAN access Django admin
    is_superuser=False   # ← NOT superuser
)
```

**Can do**:
- ✅ Everything a regular user can do
- ✅ Log in to Django admin (`/admin/`)
- ✅ View models they have permissions for
- ✅ Edit data via admin interface (if given permissions)

**Cannot do**:
- ❌ See all models automatically
- ❌ Manage users/permissions
- ❌ Bypass security checks

### Superuser (Admin)
```python
User(
    username='admin',
    is_staff=True,       # ← Automatically True for superusers
    is_superuser=True    # ← Full system access
)
```

**Can do**:
- ✅ Everything (no restrictions)
- ✅ Access all Django admin features
- ✅ Manage all models
- ✅ Create/edit/delete users
- ✅ Assign permissions
- ✅ Access system settings
- ✅ Bypass all permission checks

---

## Django Admin Permissions System

### How Permissions Work

Django uses a **granular permission system**:

```python
# Each model gets 4 automatic permissions:
- app_label.add_modelname      # Can create new records
- app_label.change_modelname    # Can edit existing records
- app_label.delete_modelname    # Can delete records
- app_label.view_modelname      # Can view records

# Example for Customer model:
- customers.add_customer
- customers.change_customer
- customers.delete_customer
- customers.view_customer
```

### Staff User with Specific Permissions

```python
# Create staff user
staff_user = User.objects.create_user(
    username='support',
    is_staff=True,  # Can access admin
    is_superuser=False
)

# Give them specific permissions
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

# Allow viewing customers only
customer_ct = ContentType.objects.get_for_model(Customer)
view_perm = Permission.objects.get(
    codename='view_customer',
    content_type=customer_ct
)
staff_user.user_permissions.add(view_perm)

# Result: Staff user can:
# ✅ Log in to admin
# ✅ See Customer section in admin
# ✅ View customer list
# ❌ Add/edit/delete customers (no permissions)
# ❌ See other models (no permissions)
```

---

## Real-World Example

### Scenario: Customer Support Team

**Use Case**: Give customer support team access to view customer data in admin, but not modify it.

```python
# Create support user
support = User.objects.create_user(
    username='support',
    email='support@projectmeats.com',
    password='secure_password',
    is_staff=True,        # Can access admin
    is_superuser=False,   # Not superuser
    first_name='Support',
    last_name='Team'
)

# Grant read-only permissions
from django.contrib.auth.models import Permission

permissions = Permission.objects.filter(
    codename__in=[
        'view_customer',
        'view_supplier',
        'view_contact',
        'view_salesorder',
    ]
)
support.user_permissions.set(permissions)
```

**Result**:
- ✅ Support team can log in to admin
- ✅ Can view customer, supplier, contact, sales order data
- ✅ Can search and filter records
- ❌ **Cannot** add/edit/delete any records
- ❌ **Cannot** see other models (products, plants, etc.)
- ❌ **Cannot** manage users or permissions

---

## ProjectMeats Architecture: Two Permission Layers

### Layer 1: Django User Permissions (System-Level)

```python
is_staff       → Access to Django Admin
is_superuser   → Full system access
```

**Controls**: System-level features (admin interface, user management)

### Layer 2: Tenant Permissions (Application-Level)

```python
TenantUser.role → owner | admin | manager | user | readonly
```

**Controls**: Application-level features (CRUD within tenant, invite users, etc.)

### How They Work Together

```python
# Example 1: Regular User with Tenant Admin
user = User(is_staff=False, is_superuser=False)
TenantUser(user=user, tenant=tenant, role='admin')

# Result:
# ❌ Cannot access Django admin (/admin/)
# ✅ Full CRUD access within tenant (via API/frontend)
# ✅ Can invite users to tenant
# ✅ Can manage tenant settings

# Example 2: Staff User with Tenant User Role
user = User(is_staff=True, is_superuser=False)
TenantUser(user=user, tenant=tenant, role='user')

# Result:
# ✅ Can access Django admin (/admin/)
# ✅ Can view models (if given permissions)
# ✅ Basic access within tenant (via API/frontend)
# ❌ Cannot invite users to tenant (role='user')

# Example 3: Guest User
user = User(username='guest', is_staff=False, is_superuser=False)
TenantUser(user=user, tenant=guest_tenant, role='admin')

# Result:
# ❌ Cannot access Django admin (/admin/)  ← KEY!
# ✅ Full CRUD access within GUEST TENANT ONLY
# ❌ Cannot access other tenants
# ❌ No system-level access
```

---

## Why Guest User Has `is_staff=False`

The guest user is intentionally set to `is_staff=False` to:

1. **Prevent Django Admin Access**
   - Guest should not see backend admin interface
   - Admin interface shows system-level data
   - Not appropriate for demo/trial users

2. **Limit to Frontend Only**
   - Guest uses frontend application only
   - API endpoints for CRUD operations
   - Clean, user-friendly interface

3. **Security**
   - Admin interface can expose sensitive system info
   - Even with limited permissions, admin access is powerful
   - Better to keep guests isolated to application layer

4. **Separation of Concerns**
   - **Django Admin** = System administration (staff)
   - **ProjectMeats App** = Business operations (all users including guests)

---

## When to Use Each Permission Level

### Regular User (`is_staff=False`)
**Use for**: 
- ✅ All normal application users
- ✅ Guest/demo users
- ✅ Customers accessing the app
- ✅ Mobile app users

**They interact via**: Frontend UI and API only

### Staff User (`is_staff=True`, `is_superuser=False`)
**Use for**:
- ✅ Customer support team (read-only access to help customers)
- ✅ Data entry team (specific model permissions)
- ✅ Auditors (read-only access to specific models)
- ✅ Junior admins (limited admin access)

**They interact via**: Django Admin (with limited permissions)

### Superuser (`is_staff=True`, `is_superuser=True`)
**Use for**:
- ✅ System administrators
- ✅ Developers (in dev/staging)
- ✅ Senior IT staff

**They interact via**: Django Admin (full access), shell, system settings

---

## Summary

| Permission | What It Controls | Guest User | Staff User | Superuser |
|------------|-----------------|------------|------------|-----------|
| `is_staff` | Django Admin Access | ❌ No | ✅ Yes | ✅ Yes |
| `is_superuser` | Bypass All Permissions | ❌ No | ❌ No | ✅ Yes |
| TenantUser.role | In-App Permissions | ✅ admin | ✅ (varies) | ✅ (varies) |
| Frontend Access | Web/Mobile App | ✅ Yes | ✅ Yes | ✅ Yes |
| API Access | REST API | ✅ Yes | ✅ Yes | ✅ Yes |
| Django Admin | Backend Admin | ❌ No | ✅ Yes | ✅ Yes |

---

## Key Takeaway

**`is_staff`** is specifically about **Django Admin access**, not application features.

- **Guest users** (`is_staff=False`) get full application access via frontend/API but **cannot access Django admin**
- **Staff users** (`is_staff=True`) get Django admin access **plus** application access
- **Superusers** get **everything** with no restrictions

In ProjectMeats, we use:
- **`is_staff` / `is_superuser`** for system-level access (admin interface)
- **`TenantUser.role`** for application-level access (business features)

This separation keeps the system secure and flexible! 🔐
