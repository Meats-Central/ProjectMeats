# 🎯 UNIFIED PROXY ARCHITECTURE FIX

**Last Updated:** December 10, 2025  
**Severity:** CRITICAL - Blocks all API access on dev environment  
**Status:** READY TO DEPLOY

---

## 🚨 The Real Problem

### What You're Seeing

```
Access to XMLHttpRequest at 'https://development.meatscentral.com/suppliers/' 
from origin 'https://dev.meatscentral.com' has been blocked by CORS policy: 
The 'Access-Control-Allow-Origin' header has a value 'https://bitdefender.com'
```

### What's Actually Happening

**TWO separate issues are combining:**

1. **Bitdefender Anti-Tracker Extension** is intercepting requests and injecting fake headers
2. **Wrong API URL** (`development.meatscentral.com` doesn't exist)

### The Smoking Gun

The error says `Access-Control-Allow-Origin: https://bitdefender.com` - **your Django backend would NEVER send this header**. This proves your browser extension is interfering with network requests.

---

## ✅ THE SOLUTION: Unified Proxy Architecture

### Architecture Overview

```
Browser Request                    Nginx Proxy                    Backend
─────────────────                 ─────────────                  ────────

https://dev.meatscentral.com/     ┌──────────────┐              ┌──────────────┐
            │                     │   Frontend   │              │   Backend    │
            │                     │   Container  │              │   Container  │
            ├─────────────────────▶   (nginx)    ├──────────────▶  (Django)   │
            │  /api/v1/suppliers/ │              │  :8000       │              │
            │                     └──────────────┘              └──────────────┘
            │                          Proxy                        Internal
       Same Origin!                  /api/* → backend:8000         Network
       (No CORS check)
```

**Key Insight:** When frontend and API share the same domain (`dev.meatscentral.com`), the browser **never triggers CORS checks** because it thinks it's talking to the same server!

---

## 🔧 Implementation Steps

### Step 1: Update GitHub Secret

**Via GitHub Web Interface** (gh CLI has permission issues):

1. Go to: https://github.com/Meats-Central/ProjectMeats/settings/environments
2. Click: **dev-frontend**
3. Find secret: **REACT_APP_API_BASE_URL**
4. Click "Update" and set value to:
   ```
   https://dev.meatscentral.com/api/v1
   ```
5. Save

**Why this URL?**
- ✅ **Same domain as frontend** → No CORS
- ✅ **Nginx proxies `/api/*` to backend** → Transparent
- ✅ **Browser never knows backend exists** → Secure

### Step 2: Verify Nginx Proxy Config

The nginx reverse proxy should already be configured (from earlier fixes). Verify it's correct:

```bash
# SSH to dev frontend server
ssh user@dev-frontend-server

# Check nginx config
cat /etc/nginx/conf.d/pm-frontend.conf
```

**Required configuration:**

```nginx
server {
    listen 80 default_server;
    server_name dev.meatscentral.com localhost _;
    
    # Proxy API requests to backend
    location ~ ^/(api|admin|static)/ {
        proxy_pass http://dev-backend-ip:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Serve frontend
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**If missing or wrong:**

```bash
# Update config
sudo nano /etc/nginx/conf.d/pm-frontend.conf

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

### Step 3: Trigger Frontend Rebuild

The frontend needs to be rebuilt with the new secret and updated code.

**Option A: GitHub Actions UI**

1. Go to: https://github.com/Meats-Central/ProjectMeats/actions
2. Select: **Deploy Dev (Frontend + Backend via DOCR)**
3. Click: "Run workflow" → Run on `development` branch

**Option B: Push to development**

```bash
git checkout development
git pull origin development
git commit --allow-empty -m "chore: trigger dev frontend rebuild with unified proxy"
git push origin development
```

The workflow will automatically:
1. Build frontend with new `REACT_APP_API_BASE_URL`
2. Deploy to dev server
3. Run health checks

### Step 4: Clean Testing Environment

**CRITICAL:** Bitdefender is interfering. Test in clean environment:

1. **Open Incognito/Private Window** (Ctrl+Shift+N or Cmd+Shift+N)
2. **Or disable Bitdefender extension:**
   - Chrome: `chrome://extensions/`
   - Find "Bitdefender Anti-Tracker"
   - Toggle OFF or add `dev.meatscentral.com` to whitelist

**Why?** Your extension injects fake headers that hide the real server response.

---

## ✅ Verification Steps

### 1. Check Runtime Config

Open browser console (F12) on `dev.meatscentral.com`:

```javascript
// Should show unified URL
console.log(window.ENV?.API_BASE_URL);
// Expected: "https://dev.meatscentral.com/api/v1"

// If undefined, check if env-config.js exists
fetch('/env-config.js').then(r => r.text()).then(console.log);
```

### 2. Test API Health

```javascript
// Test backend via proxy
fetch('https://dev.meatscentral.com/api/v1/health/')
  .then(r => r.json())
  .then(console.log);
// Expected: {status: "healthy"}
```

### 3. Check Network Tab

1. Open DevTools → Network tab
2. Try to login or create supplier
3. Look for request to `/api/v1/auth/login/` or `/api/v1/suppliers/`

**Expected Result:**

```
Request URL: https://dev.meatscentral.com/api/v1/suppliers/
Status: 200 OK
No CORS errors!
```

**Possible Issues:**

| Status | Meaning | Fix |
|--------|---------|-----|
| **200** | ✅ SUCCESS! | Nothing needed |
| **403** | Backend permissions | Run `python scripts/fix_dev_domain.py` |
| **404** | Nginx proxy not routing | Check nginx config |
| **502/504** | Backend not reachable | Check backend container health |
| **CORS error** | Still hitting old URL | Clear cache, rebuild frontend |

---

## 🎓 Why This Architecture Is "Golden"

### Before (BROKEN): Direct Backend Access

```
Browser: https://dev.meatscentral.com
   │
   ├─ Frontend: https://dev.meatscentral.com
   │
   └─ API: https://dev-backend.meatscentral.com  ← DIFFERENT ORIGIN!
          ❌ CORS checks triggered
          ❌ Preflight OPTIONS requests
          ❌ Must configure CORS on backend
          ❌ More attack surface
```

### After (GOLDEN): Unified Proxy

```
Browser: https://dev.meatscentral.com
   │
   ├─ Frontend: https://dev.meatscentral.com
   │
   └─ API: https://dev.meatscentral.com/api/  ← SAME ORIGIN!
          ├─ Nginx proxies to backend internally
          └─ Backend: http://backend-ip:8000
          
          ✅ No CORS checks (same origin)
          ✅ No preflight requests
          ✅ Backend hidden from browser
          ✅ Simpler configuration
          ✅ Better security
```

### Benefits

1. **No CORS Issues** - Browser thinks it's same origin
2. **Simpler Config** - No CORS headers needed on backend
3. **Better Security** - Backend not exposed to internet
4. **Faster** - No preflight OPTIONS requests
5. **Production-Ready** - Same pattern used in UAT/Prod

---

## 📋 Quick Reference

### Current State (BROKEN)
```bash
REACT_APP_API_BASE_URL=https://dev-backend.meatscentral.com/api/v1  ❌
# Result: CORS errors, Bitdefender interference
```

### Fixed State (GOLDEN)
```bash
REACT_APP_API_BASE_URL=https://dev.meatscentral.com/api/v1  ✅
# Result: Same-origin requests, no CORS, works perfectly
```

### Nginx Proxy Routes
```nginx
/api/*     → http://backend:8000/api/*     (Backend API)
/admin/*   → http://backend:8000/admin/*   (Django Admin)
/static/*  → http://backend:8000/static/*  (Static files)
/*         → http://localhost:8080/*        (Frontend React app)
```

---

## 🔍 Troubleshooting

### Issue: Still seeing CORS errors

**Check 1:** Are you in Incognito/Private mode?
```bash
# Bitdefender can still interfere in normal mode
# ALWAYS test in Incognito first
```

**Check 2:** Was frontend rebuilt after secret change?
```bash
# Secrets are "baked in" at build time
# Changing secret doesn't affect running app
# Must trigger new deployment
```

**Check 3:** Is browser caching old code?
```bash
# Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
# Or: DevTools → Network → "Disable cache" checkbox
```

### Issue: 404 Not Found on /api/v1/

**Nginx isn't proxying correctly.**

```bash
# Check nginx config exists
ls -l /etc/nginx/conf.d/pm-frontend.conf

# Check nginx syntax
sudo nginx -t

# Check nginx is running
sudo systemctl status nginx

# Check nginx access log
sudo tail -f /var/log/nginx/access.log
```

### Issue: 502 Bad Gateway

**Backend is not reachable from nginx.**

```bash
# Check backend container is running
docker ps | grep backend

# Check backend health
curl http://backend-ip:8000/api/v1/health/

# Check backend logs
docker logs pm-backend --tail 50
```

### Issue: 403 Forbidden

**Tenant resolution failing.**

```bash
# Run domain fix script
docker exec pm-backend python scripts/fix_dev_domain.py

# Verify domain mapping
docker exec pm-backend python manage.py shell
>>> from apps.tenants.models import TenantDomain
>>> TenantDomain.objects.filter(domain='dev.meatscentral.com')
```

---

## 📚 Related Documentation

- **Workflow Config:** `.github/workflows/reusable-deploy.yml`
- **Tenant Context:** `frontend/src/config/tenantContext.ts`
- **Domain Fix:** `scripts/fix_dev_domain.py`
- **Environment Vars:** `docs/FRONTEND_ENVIRONMENT_VARIABLES.md`
- **Golden Pipeline:** `docs/GOLDEN_PIPELINE.md`

---

## 🎯 Summary

**The Fix:**
1. ✅ Update secret: `REACT_APP_API_BASE_URL=https://dev.meatscentral.com/api/v1`
2. ✅ Verify nginx proxy config
3. ✅ Rebuild frontend (trigger workflow)
4. ✅ Test in Incognito (disable Bitdefender)

**The Result:**
- ✅ No more CORS errors
- ✅ API requests work
- ✅ Login works
- ✅ Supplier creation works
- ✅ Production-ready architecture

**TL;DR:** Same-domain proxying eliminates CORS. Bitdefender extension was lying about CORS headers. Test in Incognito!

---

**Last Updated:** December 10, 2025  
**Architecture:** Unified Proxy (Golden Standard)  
**Status:** Ready for deployment
