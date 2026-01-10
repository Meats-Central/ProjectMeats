# Tenant Update 500 Error - Bugfix Documentation

## Issue Summary

**Problem**: Tenant PATCH requests for logo uploads and color updates were failing with 500 errors, and color changes were not persisting after page refresh.

**Root Causes Identified**:
1. Missing detailed error logging in backend views
2. No validation for logo uploads (file type, size, format)
3. Missing permission checks for tenant admin/owner operations
4. Cache not being cleared after tenant updates
5. Poor error handling and user feedback in frontend

## Solutions Implemented

### 🔧 Step 1: Enhanced Backend Logging (`apps/tenants/views.py`)

**Changes**:
- Added `logging` and `traceback` imports
- Implemented `perform_update()` override in `TenantViewSet`
- Logs all PATCH/PUT requests with full context:
  - User information
  - Tenant ID
  - Request data
  - File uploads (name, size, content type)
  - Full traceback on errors
- Cache clearing after successful updates

**Benefits**:
- Detailed error diagnostics in server logs
- Easy identification of Pillow/validation issues
- Production-ready error tracking

**Testing**:
```bash
# Trigger a PATCH request and check logs
tail -f /path/to/django.log

# Expected output on success:
# ✅ Tenant update successful - Cache cleared: tenant_branding_<uuid>

# Expected output on failure:
# ❌ Tenant update failed for tenant <uuid>
# Full Traceback: ...
```

---

### 🛡️ Step 2: Custom Permission Class (`apps/tenants/permissions.py`)

**New File Created**: `backend/apps/tenants/permissions.py`

**Classes**:
1. `IsTenantAdminOrOwner`:
   - Allows superusers full access
   - Allows tenant owners/admins to update their tenant
   - Denies regular users from PATCH/PUT/DELETE
   - Safe methods (GET) allowed for all tenant members

2. `IsTenantMember`:
   - Read-only access for any tenant member
   - Used for views that require tenant membership

**Integration**:
```python
# In TenantViewSet
permission_classes = [permissions.IsAuthenticated, IsTenantAdminOrOwner]
```

**Testing**:
```bash
# As regular user (should fail)
curl -X PATCH https://api.meatscentral.com/tenants/<id>/ \
  -H "Authorization: Token <user_token>" \
  -d '{"name": "New Name"}'
# Expected: 403 Forbidden

# As admin/owner (should succeed)
curl -X PATCH https://api.meatscentral.com/tenants/<id>/ \
  -H "Authorization: Token <admin_token>" \
  -d '{"name": "New Name"}'
# Expected: 200 OK
```

---

### 📝 Step 3: Logo Upload Validation (`apps/tenants/serializers.py`)

**Enhanced `TenantSerializer`**:

1. **`validate_logo()` method**:
   - File size check (max 5MB)
   - File type validation (JPEG, PNG, WebP only)
   - Pillow image verification
   - Dimension check (max 4000x4000px)
   - Proper error messages

2. **`validate_settings()` method**:
   - Hex color format validation (#RRGGBB)
   - Validates `primary_color`, `primary_color_light`, `primary_color_dark`

3. **`update()` method override**:
   - Handles partial updates correctly
   - Clears tenant branding cache
   - Returns updated instance

**Validation Rules**:
- **File Size**: Max 5MB (5,242,880 bytes)
- **File Types**: `image/jpeg`, `image/jpg`, `image/png`, `image/webp`
- **Dimensions**: Max 4000x4000 pixels
- **Color Format**: `#RRGGBB` (e.g., `#3498db`)

**Testing**:
```python
# Test oversized file
file = File(open('large_logo.jpg', 'rb'))  # 6MB
serializer = TenantSerializer(instance=tenant, data={'logo': file}, partial=True)
assert not serializer.is_valid()
assert 'Logo file size must be less than 5MB' in str(serializer.errors)

# Test invalid file type
file = File(open('document.pdf', 'rb'))
serializer = TenantSerializer(instance=tenant, data={'logo': file}, partial=True)
assert not serializer.is_valid()
assert 'Invalid file type' in str(serializer.errors)

# Test invalid color
data = {'settings': {'theme': {'primary_color': 'blue'}}}
serializer = TenantSerializer(instance=tenant, data=data, partial=True)
assert not serializer.is_valid()
assert 'Invalid hex color format' in str(serializer.errors)
```

---

### 🎨 Step 4: Cache Clearing Signal (`apps/tenants/signals.py`)

**New Signal Added**: `clear_tenant_branding_cache()`

**Functionality**:
- Listens to `post_save` signal on `Tenant` model
- Only triggers on updates (not creation)
- Clears two cache keys:
  1. `tenant_branding_{tenant_id}` - Main branding cache
  2. `tenant_by_domain_{domain}` - Domain-based lookup cache

**Benefits**:
- Automatic cache invalidation
- No manual cache management needed
- Ensures color/logo changes persist immediately

**Testing**:
```python
from django.core.cache import cache
from apps.tenants.models import Tenant

# Set cache
tenant = Tenant.objects.get(slug='test-tenant')
cache.set(f'tenant_branding_{tenant.id}', {'old': 'data'}, 3600)

# Update tenant
tenant.name = 'Updated Name'
tenant.save()

# Cache should be cleared
assert cache.get(f'tenant_branding_{tenant.id}') is None
```

**Log Output**:
```
🎨 Cleared branding cache for tenant: test-tenant (key: tenant_branding_<uuid>)
🌐 Cleared domain cache for tenant: test.meatscentral.com
```

---

### 💻 Step 5: Frontend Error Handling (`frontend/src/`)

**Enhanced `tenantService.ts`**:

1. **`uploadLogo()` method**:
   - Try-catch wrapper with detailed error parsing
   - Extracts validation errors from API response
   - Maps HTTP status codes to user-friendly messages:
     - `400` → Validation error details
     - `413` → File too large
     - `500` → Server error with suggestion
   - Network error handling

2. **`updateThemeColors()` method**:
   - Similar error enhancement
   - Permission denied (403) detection
   - Validation error extraction

**Enhanced `Settings.tsx`**:

1. **`handleLogoUpload()`**:
   - Shows actual error message from service
   - Auto-reload page on success (after 1.5s delay)
   - Updates logo preview from response
   - Loading states during upload

2. **`handleApplyThemeColors()`**:
   - Shows actual error message from service
   - Auto-reload page on success (applies theme globally)
   - Immediate CSS variable injection for preview

**Error Message Examples**:
```typescript
// Good error messages
"Logo validation failed: Image dimensions too large. Max: 4000x4000px, Actual: 5000x5000px"
"Upload failed: Invalid file type: application/pdf. Allowed types: JPEG, PNG, WebP"
"Permission denied: Only tenant owners and admins can update theme colors."
"Server error while uploading logo. Please check server logs or try again later."

// Bad error messages (before fix)
"Failed to upload logo. Please try again."
"Failed to save theme colors. Please try again."
```

**Testing**:
```bash
# Test logo upload with oversized file
# Expected: "Logo file is too large. Please use a file smaller than 5MB."

# Test logo upload with invalid type
# Expected: "Logo validation failed: Invalid file type: application/pdf. Allowed types: JPEG, PNG, WebP"

# Test as non-admin user
# Expected: "Permission denied: Only tenant owners and admins can update theme colors."

# Test with network disconnected
# Expected: "Network error: Unable to reach server. Please check your connection."
```

---

## Verification Checklist

### Backend Tests

```bash
cd backend

# 1. Test logo upload validation
python manage.py shell
>>> from apps.tenants.models import Tenant
>>> from apps.tenants.serializers import TenantSerializer
>>> tenant = Tenant.objects.first()
>>> # Test oversized file, invalid type, invalid dimensions

# 2. Test permissions
python manage.py shell
>>> from apps.tenants.permissions import IsTenantAdminOrOwner
>>> from apps.tenants.models import TenantUser
>>> # Test with different user roles

# 3. Test cache clearing
python manage.py shell
>>> from django.core.cache import cache
>>> from apps.tenants.models import Tenant
>>> tenant = Tenant.objects.first()
>>> cache.set(f'tenant_branding_{tenant.id}', 'test', 3600)
>>> tenant.save()
>>> cache.get(f'tenant_branding_{tenant.id}')  # Should be None

# 4. Check logs during PATCH request
tail -f /var/log/django.log
# Then make a PATCH request from frontend
```

### Frontend Tests

```bash
cd frontend

# 1. Test logo upload UI
npm run dev
# Navigate to /settings
# Click "Upload Logo" and select various files:
# - Valid: small PNG/JPEG (should succeed)
# - Invalid: PDF, oversized image (should show error)
# - Check console for detailed error logs

# 2. Test theme color updates
# Click "Apply Theme Colors" with new colors
# Should see success message and page reload
# Check that colors persist after refresh

# 3. Test as non-admin user
# Login as regular user
# Try to upload logo or change colors
# Should see "Permission denied" error
```

### Integration Tests

```bash
# 1. Full workflow as admin
1. Login as admin_test_development_2
2. Navigate to /settings
3. Upload valid logo (PNG, < 5MB)
4. Extract colors from logo
5. Apply theme colors
6. Refresh page → verify colors/logo persist
7. Check backend logs for successful operation

# 2. Error scenarios
1. Try uploading 6MB image → see size error
2. Try uploading PDF → see type error
3. Try as regular user → see permission error
4. Disconnect network → see network error

# 3. Cache verification
1. Update logo in settings
2. Navigate to another page (e.g., /dashboard)
3. Check that new logo appears in sidebar
4. Check backend logs for cache clearing
```

---

## Media Configuration Verification

**File**: `backend/projectmeats/settings/base.py`

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))
```

**File**: `backend/projectmeats/settings/development.py`

```python
MEDIA_ROOT = BASE_DIR / "media"
```

**File**: `backend/projectmeats/urls.py`

```python
# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

**Verification**:
```bash
# Check media directory exists
ls -la backend/media/tenant_logos/

# Check media URL serves files
curl http://localhost:8000/media/tenant_logos/test_logo.png
# Should return image file (200 OK)

# Production: Media served by nginx
# Check nginx config includes media location block
```

---

## Deployment Notes

### Environment Variables

No new environment variables required. Existing variables:
- `MEDIA_ROOT` - Path to media files directory (default: `{BASE_DIR}/media`)
- `MEDIA_URL` - URL prefix for media files (default: `/media/`)

### Database Migrations

No database migrations required. Changes are code-only (validation, logging, caching).

### Dependencies

All dependencies already in `requirements.txt`:
- `Pillow>=10.2.0` - For image validation

### Production Checklist

- [ ] Ensure `MEDIA_ROOT` directory has write permissions for Django user
- [ ] Configure nginx/Apache to serve `/media/` location
- [ ] Set up log rotation for Django logs (detailed logging added)
- [ ] Test media upload with production settings
- [ ] Verify cache backend is configured (Redis recommended)
- [ ] Test tenant branding cache clearing
- [ ] Verify permissions with production users (owner/admin/regular)

---

## Known Limitations

1. **File Cleanup**: Old logos are not automatically deleted when uploading a new one. Consider adding cleanup logic in the future.

2. **Image Optimization**: Uploaded logos are stored as-is. Consider adding automatic optimization/resizing in the future.

3. **Cache Backend**: Uses default cache backend. For production, use Redis for better performance.

4. **Concurrent Uploads**: Multiple simultaneous logo uploads to the same tenant may have race conditions. Consider adding file locks if this becomes an issue.

---

## Related Files

### Backend
- `backend/apps/tenants/views.py` - Added logging and perform_update override
- `backend/apps/tenants/permissions.py` - New file with custom permissions
- `backend/apps/tenants/serializers.py` - Enhanced validation for logo/colors
- `backend/apps/tenants/signals.py` - Added cache clearing signal
- `backend/projectmeats/settings/base.py` - Media configuration
- `backend/projectmeats/urls.py` - Media URL patterns

### Frontend
- `frontend/src/services/tenantService.ts` - Enhanced error handling
- `frontend/src/pages/Settings.tsx` - Improved UX with auto-reload

### Documentation
- `TENANT_UPDATE_BUGFIX.md` - This file
- `backend/apps/tenants/permissions.py` - Inline documentation

---

## Commit Message

```
fix: Add comprehensive tenant update error handling and validation

Fixes 500 errors on tenant PATCH requests for logo uploads and color updates.

**Backend Changes**:
- Add detailed logging to TenantViewSet.perform_update() with full traceback
- Create IsTenantAdminOrOwner permission class for tenant admin operations
- Add logo upload validation (file type, size, dimensions) using Pillow
- Add hex color format validation for theme settings
- Add cache clearing signal for tenant branding updates

**Frontend Changes**:
- Enhance tenantService error handling with detailed messages
- Add auto-reload after successful logo/color updates
- Show actual validation errors to users instead of generic messages
- Add loading states during upload operations

**Testing**:
- Validate with oversized files, invalid types, wrong dimensions
- Test permission enforcement (admin/owner vs regular users)
- Verify cache clearing on tenant updates
- Confirm color persistence after page refresh

Closes: #<issue_number>
```

---

## Next Steps

1. **Test in Development Environment**:
   - Deploy to dev.meatscentral.com
   - Test all scenarios as admin_test_development_2
   - Verify logs in backend container
   - Test with various file types and sizes

2. **Monitor Logs**:
   - Watch for detailed error logs during testing
   - Identify any Pillow-related issues
   - Check cache clearing operations

3. **User Testing**:
   - Have QA test logo upload workflow
   - Test theme color persistence
   - Test as different user roles

4. **Production Deployment**:
   - Merge to UAT branch first
   - Test on staging environment
   - Deploy to production after approval

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-10  
**Author**: GitHub Copilot CLI
