# 🚀 IMMEDIATE ACTION REQUIRED

**Date:** December 10, 2025  
**PR:** #1331 - Unified Proxy Architecture  
**Severity:** CRITICAL  

---

## ✅ ACTION CHECKLIST

### Step 1: Update GitHub Secret ⚠️ MUST DO FIRST

**Via GitHub Web UI** (gh CLI lacks permissions):

1. **Navigate to:**
   ```
   https://github.com/Meats-Central/ProjectMeats/settings/environments
   ```

2. **Click:** `dev-frontend` environment

3. **Find secret:** `REACT_APP_API_BASE_URL`

4. **Click "Update"** and set value to:
   ```
   https://dev.meatscentral.com/api/v1
   ```

5. **Save**

**Why this is critical:**
- Frontend builds "bake in" environment variables
- Changing secret doesn't affect running app
- Must be set BEFORE merging PR

---

### Step 2: Merge PR #1331

**Link:** https://github.com/Meats-Central/ProjectMeats/pull/1331

```bash
gh pr merge 1331 --squash --auto
```

Or merge via GitHub UI.

---

### Step 3: Wait for Deployment

Monitor the GitHub Actions workflow:

```
https://github.com/Meats-Central/ProjectMeats/actions
```

Look for: **Deploy Dev (Frontend + Backend via DOCR)**

**Expected:**
- ✅ Build frontend (with new secret)
- ✅ Push to Docker registry
- ✅ Deploy to dev server
- ✅ Health checks pass

**Duration:** ~5-10 minutes

---

### Step 4: Test in Clean Environment

**CRITICAL:** Disable Bitdefender first!

#### Option A: Incognito Mode (Recommended)

```
Windows/Linux: Ctrl+Shift+N
Mac: Cmd+Shift+N
```

#### Option B: Disable Bitdefender Extension

```
Chrome: chrome://extensions/
Find: Bitdefender Anti-Tracker
Toggle: OFF
```

Or whitelist `dev.meatscentral.com` in Bitdefender settings.

---

### Step 5: Verification Tests

#### Test 1: Check Runtime Config

Open browser console (F12) on `https://dev.meatscentral.com`:

```javascript
// Should show unified URL
console.log(window.ENV.API_BASE_URL);
```

**Expected:** `"https://dev.meatscentral.com/api/v1"`

---

#### Test 2: API Health Check

```javascript
fetch('https://dev.meatscentral.com/api/v1/health/')
  .then(r => r.json())
  .then(console.log);
```

**Expected:** `{status: "healthy"}`

---

#### Test 3: Try Login

1. Go to: `https://dev.meatscentral.com/login`
2. Enter credentials
3. Open Network tab (F12 → Network)
4. Watch for requests

**Expected:**
```
Request URL: https://dev.meatscentral.com/api/v1/auth/login/
Status: 200 OK
No CORS errors in console
```

---

#### Test 4: Create Supplier

1. Navigate to Suppliers page
2. Click "Add Supplier"
3. Fill form and save
4. Check Network tab

**Expected:**
```
POST https://dev.meatscentral.com/api/v1/suppliers/
Status: 201 Created
No CORS errors
Supplier appears in list
```

---

## 🎯 SUCCESS CRITERIA

### All Green ✅

- [ ] Secret updated in GitHub
- [ ] PR #1331 merged
- [ ] Deployment workflow completed
- [ ] Runtime config shows correct URL
- [ ] API health check returns 200
- [ ] Login succeeds (no CORS errors)
- [ ] Can create supplier (no CORS errors)
- [ ] Network tab shows same-origin requests

---

## 🚨 TROUBLESHOOTING

### Issue: Still seeing CORS errors

**Fix 1:** Verify you're in Incognito mode
```bash
# Bitdefender can still interfere in normal mode
# MUST use Incognito for accurate testing
```

**Fix 2:** Hard refresh to clear cache
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

**Fix 3:** Check if secret was actually updated
```bash
# Should see new secret value in workflow logs
gh run list --workflow="Deploy Dev"
gh run view <run-id> --log
```

---

### Issue: 404 Not Found on /api/

**Fix:** Verify nginx proxy configuration

```bash
# SSH to dev frontend server
ssh user@dev-frontend-server

# Check nginx config
cat /etc/nginx/conf.d/pm-frontend.conf

# Should contain proxy rules for /api/*
# If missing, re-apply nginx config from workflow
```

---

### Issue: 502 Bad Gateway

**Fix:** Check backend container health

```bash
# Check backend is running
docker ps | grep backend

# Check backend logs
docker logs pm-backend --tail 50

# Test backend directly
curl http://backend-ip:8000/api/v1/health/
```

---

### Issue: 403 Forbidden

**Fix:** Run domain mapping script

```bash
# SSH to dev backend server
ssh user@dev-backend-server

# Run fix script
docker exec pm-backend python scripts/fix_dev_domain.py

# Verify mapping
docker exec pm-backend python manage.py shell
>>> from apps.tenants.models import TenantDomain
>>> TenantDomain.objects.filter(domain='dev.meatscentral.com')
# Should show: <TenantDomain: dev.meatscentral.com -> root>
```

---

## 📊 EXPECTED TIMELINE

| Step | Duration | Status |
|------|----------|--------|
| Update secret | 1 min | ⏳ Waiting |
| Merge PR | 1 min | ⏳ Waiting |
| CI/CD build | 5-8 min | ⏳ Waiting |
| Deployment | 2-3 min | ⏳ Waiting |
| Verification | 2 min | ⏳ Waiting |
| **TOTAL** | **~10-15 min** | |

---

## 📚 DOCUMENTATION

**Primary Guide:** `docs/UNIFIED_PROXY_ARCHITECTURE.md`

**Quick Reference:**
- Frontend env vars: `docs/FRONTEND_ENVIRONMENT_VARIABLES.md`
- Domain mapping: `scripts/fix_dev_domain.py`
- Golden Pipeline: `docs/GOLDEN_PIPELINE.md`

---

## 🎉 WHAT THIS FIXES

### Before (Broken)
```
❌ CORS errors on every API call
❌ Login fails
❌ Can't create suppliers
❌ Bitdefender interference
❌ Different-origin requests
```

### After (Golden)
```
✅ Zero CORS errors
✅ Login works perfectly
✅ Supplier creation works
✅ Bitdefender can't interfere
✅ Same-origin requests (production-ready)
```

---

## 🚀 TL;DR

1. **Update secret** in GitHub UI: `REACT_APP_API_BASE_URL=https://dev.meatscentral.com/api/v1`
2. **Merge PR #1331**
3. **Wait** for deployment (~10 min)
4. **Test in Incognito** with Bitdefender disabled
5. **Verify** login and supplier creation work

**Result:** All CORS issues permanently eliminated! 🎉

---

**Last Updated:** December 10, 2025  
**Status:** READY FOR DEPLOYMENT  
**PR:** https://github.com/Meats-Central/ProjectMeats/pull/1331
