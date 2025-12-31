# Fix Dev Frontend API Routing

The deployed frontend on dev.meatscentral.com is calling the wrong API URL.

## Problem

Browser console shows:
```
Access to XMLHttpRequest at 'https://development.meatscentral.com/suppliers/' 
from origin 'https://dev.meatscentral.com' has been blocked by CORS
```

**Wrong URL:** `development.meatscentral.com`  
**Correct URL:** `dev-backend.meatscentral.com`

## Root Cause

The deployed frontend has old code that hasn't been rebuilt after PR #1328.

## Immediate Fix (No Rebuild Required)

### Option 1: Update env-config.js on Server

SSH into dev frontend server and update the runtime config:

```bash
# SSH to dev frontend server
ssh user@dev-frontend-server

# Update env-config.js
sudo cat > /usr/share/nginx/html/env-config.js << 'EOF'
// Runtime Environment Configuration
window.ENV = {
  API_BASE_URL: "https://dev-backend.meatscentral.com/api/v1",
  ENVIRONMENT: "development",
  AI_ASSISTANT_ENABLED: "true"
};
EOF

# Restart nginx to clear any cache
sudo systemctl reload nginx
```

### Option 2: Update via Docker

If frontend runs in Docker:

```bash
# Create env-config.js
cat > /tmp/env-config.js << 'EOF'
window.ENV = {
  API_BASE_URL: "https://dev-backend.meatscentral.com/api/v1",
  ENVIRONMENT: "development"
};
EOF

# Copy into container
docker cp /tmp/env-config.js pm-frontend:/usr/share/nginx/html/env-config.js

# Restart container
docker restart pm-frontend
```

## Permanent Fix (Requires Rebuild)

Trigger CI/CD to rebuild frontend with latest code (includes PR #1328 fix):

```bash
# Push to development branch to trigger deployment
git push origin development
```

Or manually trigger workflow in GitHub Actions.

## Verification

After applying fix, check browser console:

```javascript
// Should log correct URL
console.log(window.ENV.API_BASE_URL);
// Expected: "https://dev-backend.meatscentral.com/api/v1"

// Test API call
fetch(window.ENV.API_BASE_URL + '/health/')
  .then(r => r.json())
  .then(console.log);
// Expected: {status: "healthy"}
```

## CORS Issue

There's also a bizarre CORS error showing:
```
Access-Control-Allow-Origin: https://bitdefender.com
```

This suggests either:
1. **Proxy misconfiguration** - nginx is not proxying correctly
2. **Wrong backend response** - backend is returning wrong CORS headers
3. **DNS hijacking** - bitdefender antivirus is intercepting requests

### Fix CORS on Backend

Check Django CORS settings in `backend/projectmeats/settings/development.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "https://dev.meatscentral.com",
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True
```

If using `CORS_ORIGIN_WHITELIST`, update it similarly.

### Verify DNS

```bash
# Check DNS resolution
nslookup dev-backend.meatscentral.com

# Check if request reaches correct server
curl -I https://dev-backend.meatscentral.com/api/v1/health/
```

## Related

- PR #1328 - Fixed API routing in tenantContext.ts
- docs/FRONTEND_ENVIRONMENT_VARIABLES.md - Environment config guide
- docs/DEV_DOMAIN_FIX.md - Backend domain mapping

---

**TL;DR:** Update `env-config.js` to use `dev-backend.meatscentral.com` and rebuild frontend.
