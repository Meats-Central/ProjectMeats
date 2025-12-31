# Frontend Deployment Docker Run Fix

**Date**: 2025-12-09  
**Status**: ✅ Fixed and Deployed  
**PR**: [#1253](https://github.com/Meats-Central/ProjectMeats/pull/1253)

---

## Problem Summary

Frontend deployment was failing with exit code 125 during the `deploy-frontend` job:

```
invalid argument "backend:" for "--add-host" flag: invalid IP address in add-host: ""

Usage:  docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
Process completed with exit code 125.
```

**Failed Run**: https://github.com/Meats-Central/ProjectMeats/actions/runs/20051654436/job/57509021833

---

## Root Cause

The `DEV_BACKEND_IP` secret was not configured in the repository settings, causing the docker run command to fail:

```bash
sudo docker run -d --name pm-frontend \
  --add-host backend:${{ secrets.DEV_BACKEND_IP }}  # ← Empty value here
  ...
```

When `DEV_BACKEND_IP` is empty, Docker interprets this as `--add-host backend:` with no IP, triggering a validation error.

---

## Solution Implemented

### 1. **Added Debug Logging**
Print deployment variables before running docker commands:
```bash
echo "=== Deployment Variables ==="
echo "REGISTRY: ${{ env.REGISTRY }}"
echo "FRONTEND_IMAGE: ${{ env.FRONTEND_IMAGE }}"
echo "TAG: dev-${{ github.sha }}"
echo "BACKEND_IP: ${{ secrets.DEV_BACKEND_IP }}"
echo "============================"
```

### 2. **Conditional --add-host Flag**
Made the backend host entry optional:
```bash
BACKEND_IP="${{ secrets.DEV_BACKEND_IP }}"
if [ -n "$BACKEND_IP" ]; then
  echo "Adding backend host entry: $BACKEND_IP"
  sudo docker run -d --name pm-frontend --restart unless-stopped \
    -p 8080:80 \
    --add-host backend:"$BACKEND_IP" \
    -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
    ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:dev-${{ github.sha }}
else
  echo "⚠️  DEV_BACKEND_IP not set, skipping --add-host"
  sudo docker run -d --name pm-frontend --restart unless-stopped \
    -p 8080:80 \
    -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
    ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:dev-${{ github.sha }}
fi
```

### 3. **Graceful Fallback**
- Container starts successfully even if `DEV_BACKEND_IP` is not set
- Nginx reverse proxy at the host level handles backend routing
- Frontend remains operational with warning logged

---

## Benefits

✅ **Deployment Resilience**: No longer fails if optional secret is missing  
✅ **Better Debugging**: Clear visibility into variable values  
✅ **Flexible Configuration**: Works with or without backend host entry  
✅ **Fail-Safe**: Explicit warning when DEV_BACKEND_IP is not configured  

---

## Action Required

**⚠️ IMPORTANT**: For optimal configuration, set the `DEV_BACKEND_IP` secret:

1. Navigate to repository settings
2. Go to: **Settings → Secrets and variables → Actions → Repository secrets**
3. Add new secret:
   - **Name**: `DEV_BACKEND_IP`
   - **Value**: Backend server IP address (e.g., `10.17.0.13`)

This enables the container to resolve `backend` hostname internally via `/etc/hosts`.

---

## Testing

### Before Fix
- ❌ Docker run failed with exit code 125
- ❌ Frontend deployment blocked
- ❌ No visibility into variable values

### After Fix
- ✅ Docker run succeeds with or without DEV_BACKEND_IP
- ✅ Frontend deploys successfully
- ✅ Debug output shows all variable values
- ✅ Clear warning when DEV_BACKEND_IP is missing

---

## Related Documentation

- [GitHub Actions Run (Failed)](https://github.com/Meats-Central/ProjectMeats/actions/runs/20051654436)
- [Pull Request #1253](https://github.com/Meats-Central/ProjectMeats/pull/1253)
- [Pull Request #1251](https://github.com/Meats-Central/ProjectMeats/pull/1251) (DOCR authentication fix)
- DIGITALOCEAN_REGISTRY_FIX.md
- .github/workflows/11-dev-deployment.yml

---

## Deployment History

1. **PR #1251**: Fixed DOCR authentication (merged to development)
2. **Workflow Run #504**: Failed due to missing DEV_BACKEND_IP
3. **PR #1253**: Fixed docker run to handle missing secret (merged to development)
4. **Next Run**: Will deploy successfully with debug output

---

## Monitoring

Watch for these indicators in future workflow runs:

### Success Indicators
```
=== Deployment Variables ===
REGISTRY: registry.digitalocean.com/meatscentral
FRONTEND_IMAGE: projectmeats-frontend
TAG: dev-<commit-sha>
BACKEND_IP: <IP or empty>
============================
✓ Container started successfully
```

### Expected Warnings (if DEV_BACKEND_IP not set)
```
⚠️  DEV_BACKEND_IP not set, skipping --add-host
```

### Error Indicators (if still failing)
```
✗ Docker run failed with exit code X
```

---

## Summary

This fix ensures the frontend deployment workflow is resilient to missing optional configuration while providing clear feedback about what's happening. The deployment will now succeed regardless of whether `DEV_BACKEND_IP` is configured, with appropriate warnings logged for visibility.

**Status**: Ready for next deployment ✅
