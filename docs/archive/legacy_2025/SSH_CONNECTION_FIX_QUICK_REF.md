# SSH Connection Timeout - Quick Fix Reference

**Status**: ✅ Enhanced with retry logic and diagnostics  
**Date**: 2025-12-07  
**Workflow**: `.github/workflows/11-dev-deployment.yml`

---

## What Was Fixed

SSH connection timeouts in GitHub Actions deployment workflows now have:

✅ **5 retry attempts** with exponential backoff  
✅ **Pre-flight diagnostics** (DNS, ping, port check)  
✅ **Progressive timeouts** (30s → 90s)  
✅ **Clear error messages** with troubleshooting steps

---

## How It Works

### Enhanced SSH Script
`.github/scripts/ssh-connect-with-retry.sh`

**Pre-Flight Checks:**
1. DNS resolution
2. ICMP ping (if not blocked)
3. TCP port 22 connectivity
4. SSH service detection

**Retry Logic:**
- Attempt 1: 30s timeout, immediate
- Attempt 2: 50s timeout, 2s delay
- Attempt 3: 70s timeout, 4s delay
- Attempt 4: 90s timeout, 8s delay
- Attempt 5: 90s timeout, 16s delay

**Total max time**: ~5 minutes (if all attempts fail)

---

## When to Use

This fix helps with:
- ✅ Transient network issues
- ✅ Brief server maintenance
- ✅ Temporary firewall hiccups
- ✅ Network congestion
- ✅ SSH service restarts

**Won't fix** (requires manual intervention):
- ❌ Server permanently offline
- ❌ Firewall blocking GitHub Actions IPs
- ❌ SSH service not running
- ❌ Incorrect credentials

---

## If Deployment Still Fails

The issue is **infrastructure-related**. Check:

### 1. Server Status
```bash
ping <server-ip>
ssh <user>@<server-ip>
```

### 2. SSH Service
```bash
sudo systemctl status ssh
sudo ss -tlnp | grep :22
```

### 3. Firewall Rules
```bash
# Get GitHub Actions IP ranges
curl https://api.github.com/meta | jq -r '.actions[]'

# Allow SSH from GitHub Actions
sudo ufw allow from <github-ip-range> to any port 22
```

### 4. Cloud Provider Security Groups
- AWS: EC2 → Security Groups → Inbound Rules
- DigitalOcean: Networking → Firewalls
- Azure: Virtual Machines → Networking

### 5. GitHub Secrets
Verify in Repository Settings → Secrets:
- `DEV_HOST`
- `DEV_USER`
- `DEV_SSH_PASSWORD`

---

## Configuration

Customize retry behavior via environment variables:

```yaml
env:
  MAX_SSH_RETRIES: 5          # Number of attempts
  SSH_CONNECT_TIMEOUT: 30     # Initial timeout (seconds)
```

---

## Testing Locally

```bash
export SSHPASS="your-password"
export MAX_SSH_RETRIES=3

./.github/scripts/ssh-connect-with-retry.sh \
  username \
  hostname \
  "uptime"
```

---

## Related Documentation

- **Detailed Guide**: `SSH_CONNECTION_FIX_IMPLEMENTATION.md`
- **Troubleshooting**: `SSH_CONNECTION_TROUBLESHOOTING.md`
- **Issue History**: `SSH_DEPLOYMENT_ISSUES_SUMMARY.md`

---

## Future Improvements

1. **Switch to SSH keys** (more secure than passwords)
2. **Self-hosted runners** (eliminate firewall issues)
3. **Health monitoring** (pre-deployment checks)
4. **Circuit breaker pattern** (fail fast after detecting patterns)

---

**Last Updated**: 2025-12-07  
**PR**: #XXXX (pending)
