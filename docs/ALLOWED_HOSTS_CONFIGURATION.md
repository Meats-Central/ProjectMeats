# ALLOWED_HOSTS Configuration Guide

**Last Updated**: 2025-12-07  
**Status**: Development settings updated to read from environment variables

---

## Overview

Django's `ALLOWED_HOSTS` setting controls which hostnames/IPs are allowed to serve the application. This guide explains how to configure it across different environments.

---

## Format in GitHub Secrets / Environment Variables

### ✅ CORRECT Format (Comma-Separated String)

```bash
# In GitHub Secrets or .env files
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com,157.245.114.182
```

**No spaces, no brackets, no quotes around individual items.**

### ❌ INCORRECT Formats

```bash
# Python list syntax (wrong for env vars)
ALLOWED_HOSTS=['meatscentral.com', 'www.meatscentral.com']

# Spaces between items (will include spaces in hostnames)
ALLOWED_HOSTS=meatscentral.com, www.meatscentral.com

# Missing items
ALLOWED_HOSTS=meatscentral.com
```

---

## Configuration by Environment

### Development (`development.py`)

**File**: `backend/projectmeats/settings/development.py`

```python
# Hardcoded defaults for local development
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "testserver",
    "0.0.0.0",
    ".meatscentral.com",  # Wildcard for all subdomains
    "dev.meatscentral.com",
    "157.245.114.182",
]

# PLUS any additional hosts from environment variable
_env_hosts = config("ALLOWED_HOSTS", default="", cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])
ALLOWED_HOSTS = ALLOWED_HOSTS + _env_hosts
```

**Behavior**:
- ✅ Uses hardcoded defaults (always includes localhost, etc.)
- ✅ Reads `ALLOWED_HOSTS` environment variable and appends to list
- ✅ If `ALLOWED_HOSTS` is not set, uses only defaults

**GitHub Secret Setup**:
```yaml
Environment: dev-backend
ALLOWED_HOSTS=dev-backend.meatscentral.com,157.245.114.182
```

---

### Staging/UAT (`staging.py`)

**File**: `backend/projectmeats/settings/staging.py`

```python
# Reads from environment variable
env_allowed_hosts = config("ALLOWED_HOSTS", default="localhost,127.0.0.1")
ALLOWED_HOSTS = [host.strip() for host in env_allowed_hosts.split(",") if host.strip()]

# Adds UAT-specific hosts
STAGING_HOSTS = [
    "uat.meatscentral.com",
    "staging-projectmeats.ondigitalocean.app",
]

# Merges with environment hosts
for host in STAGING_HOSTS:
    if host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)
```

**Behavior**:
- ✅ Reads `ALLOWED_HOSTS` from environment (defaults to localhost if not set)
- ✅ Always includes UAT-specific hosts
- ✅ Removes duplicates

**GitHub Secret Setup**:
```yaml
Environment: uat-backend
ALLOWED_HOSTS=uat.meatscentral.com,uat-backend.meatscentral.com,165.227.XXX.XXX
```

---

### Production (`production.py`)

**File**: `backend/projectmeats/settings/production.py`

```python
# Helper function to split comma-separated values
def _split_list(val: str | None) -> list[str]:
    if not val:
        return []
    return [item.strip() for item in val.split(",") if item.strip()]

# Read from two environment variables
_ext_hosts = _split_list(os.environ.get("ALLOWED_HOSTS", ""))
_int_hosts = _split_list(os.environ.get("INTERNAL_ALLOWED_HOSTS", ""))

# Common internal hosts (always included)
_COMMON_INTERNAL_HOSTS = [
    "localhost",
    "127.0.0.1",
    ".meatscentral.com",
    "10.244.45.4",  # Container IPs
    "172.17.0.1",
]

# Merge all hosts (removes duplicates)
ALLOWED_HOSTS = list(set(_ext_hosts + _int_hosts + _COMMON_INTERNAL_HOSTS))
```

**Behavior**:
- ✅ Reads `ALLOWED_HOSTS` for external/public domains
- ✅ Reads `INTERNAL_ALLOWED_HOSTS` for container/internal IPs
- ✅ Always includes common internal hosts
- ✅ Removes duplicates

**GitHub Secret Setup**:
```yaml
Environment: prod-backend
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com,api.meatscentral.com
INTERNAL_ALLOWED_HOSTS=10.244.45.4,172.17.0.1
```

---

## Setting Up GitHub Environment Secrets

### Step 1: Navigate to Environments
https://github.com/Meats-Central/ProjectMeats/settings/environments

### Step 2: Configure Each Environment

#### Development Backend (`dev-backend`)
```yaml
ALLOWED_HOSTS=dev.meatscentral.com,dev-backend.meatscentral.com,157.245.114.182
DEV_HOST=157.245.114.182
DEV_USER=django
DEV_SSH_PASSWORD=<password>
```

#### Development Frontend (`dev-frontend`)
```yaml
ALLOWED_HOSTS=dev.meatscentral.com,165.227.XXX.XXX
DEV_HOST=165.227.XXX.XXX
DEV_USER=root
DEV_SSH_PASSWORD=<password>
```

#### UAT Backend (`uat-backend`)
```yaml
ALLOWED_HOSTS=uat.meatscentral.com,uat-backend.meatscentral.com,<uat-ip>
STAGING_HOST=<uat-backend-ip>
STAGING_USER=django
STAGING_SSH_PASSWORD=<password>
```

#### Production Backend (`prod-backend`)
```yaml
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com,api.meatscentral.com
INTERNAL_ALLOWED_HOSTS=10.244.45.4,172.17.0.1
PRODUCTION_HOST=<prod-backend-ip>
PRODUCTION_USER=django
PRODUCTION_SSH_PASSWORD=<password>
```

---

## Common Issues & Solutions

### Issue 1: "400 Bad Request" Error

**Symptom**: Browser shows "Bad Request (400)" with no details

**Cause**: The request hostname is not in `ALLOWED_HOSTS`

**Solution**: Add the hostname to the appropriate environment secret:
```bash
# If accessing via IP
ALLOWED_HOSTS=157.245.114.182,dev.meatscentral.com

# If accessing via domain
ALLOWED_HOSTS=dev.meatscentral.com,www.dev.meatscentral.com
```

---

### Issue 2: Changes Not Taking Effect

**Symptom**: Updated `ALLOWED_HOSTS` secret but still getting 400 error

**Cause**: Application needs restart to reload environment variables

**Solution**: Restart the backend container:
```bash
# SSH to server
ssh user@server

# Restart backend container
sudo docker restart pm-backend

# Check logs
sudo docker logs pm-backend --tail 50
```

---

### Issue 3: Wildcard Not Working

**Symptom**: `.meatscentral.com` wildcard not matching `dev.meatscentral.com`

**Cause**: Wildcard must start with a dot (`.`)

**Solution**:
```bash
# ✅ CORRECT - matches all subdomains
ALLOWED_HOSTS=.meatscentral.com

# ❌ WRONG - only matches exact "meatscentral.com"
ALLOWED_HOSTS=meatscentral.com
```

---

### Issue 4: Development Settings Not Reading Secret

**Symptom**: `DEV_ALLOWED_HOSTS` secret set but not being used

**Status**: ✅ FIXED - Development settings now read from `ALLOWED_HOSTS` environment variable

**Previous Behavior** (before fix):
- Development settings used only hardcoded list
- Environment variable was ignored

**Current Behavior** (after fix):
- Development settings read from `ALLOWED_HOSTS` environment variable
- Appends environment hosts to hardcoded defaults
- Both local development and deployed dev environment work correctly

---

## Testing ALLOWED_HOSTS Configuration

### Test 1: Check Current Setting

SSH to server and run:
```bash
# Access Django shell
sudo docker exec -it pm-backend python manage.py shell

# Check ALLOWED_HOSTS
from django.conf import settings
print(settings.ALLOWED_HOSTS)
```

### Test 2: Verify from Browser

Access the application via different hostnames:
```bash
# Should work (if in ALLOWED_HOSTS)
curl -I http://dev.meatscentral.com
curl -I http://157.245.114.182

# Should fail with 400 (if not in ALLOWED_HOSTS)
curl -I http://unknown-domain.com
```

### Test 3: Check Logs

```bash
# View Django logs
sudo docker logs pm-backend --tail 100 | grep -i "allowed"
```

---

## Best Practices

### 1. Always Include Server IP
```bash
# Include both domain and IP
ALLOWED_HOSTS=dev.meatscentral.com,157.245.114.182
```

### 2. Use Wildcards for Subdomains
```bash
# Allows dev.meatscentral.com, api.meatscentral.com, etc.
ALLOWED_HOSTS=.meatscentral.com
```

### 3. Keep Development and Production Separate
```bash
# Development - more permissive
ALLOWED_HOSTS=localhost,127.0.0.1,.meatscentral.com

# Production - restrictive
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com,api.meatscentral.com
```

### 4. Document Changes
When updating `ALLOWED_HOSTS`, document:
- Why the hostname was added
- Which environment needs it
- Expected deployment/app behavior

---

## Related Documentation

- **SSH Connection Troubleshooting**: `SSH_CONNECTION_TROUBLESHOOTING.md`
- **Environment Secrets Guide**: This file
- **Deployment Runbook**: `DEPLOYMENT_RUNBOOK.md`
- **Django ALLOWED_HOSTS Docs**: https://docs.djangoproject.com/en/stable/ref/settings/#allowed-hosts

---

## Change History

| Date | Change | Reason |
|------|--------|--------|
| 2025-12-07 | Updated `development.py` to read from env | Fix: Dev settings ignored `ALLOWED_HOSTS` secret |
| 2025-12-07 | Documented comma-separated format | Clarity: Users were unsure of correct format |
| 2025-12-07 | Added environment-specific examples | Fix: SSH timeout due to wrong server IPs |

---

**Last Updated**: 2025-12-07  
**Maintainer**: DevOps Team  
**Status**: Active configuration guide
