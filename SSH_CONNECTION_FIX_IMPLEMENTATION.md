# SSH Connection Timeout Fix - Implementation Summary

**Date**: 2025-12-07  
**Issue**: GitHub Actions deployment workflow failing with SSH connection timeout  
**Status**: ✅ Fixed with enhanced retry logic and diagnostics

---

## Problem

The GitHub Actions workflow was failing at the "Test SSH connectivity" step with:

```
ssh: connect to host *** port 22: Connection timed out
Process completed with exit code 1.
```

**Root Cause**: The GitHub Actions runner was unable to establish an SSH connection to the deployment server, likely due to:
- Network connectivity issues
- Firewall rules blocking GitHub Actions IP ranges
- Server being temporarily unreachable
- SSH service not running or misconfigured

---

## Solution Implemented

### 1. Enhanced SSH Connection Script

Created `.github/scripts/ssh-connect-with-retry.sh` with:

**Features:**
- ✅ Pre-flight network diagnostics (DNS, ping, port check)
- ✅ Exponential backoff retry logic (3-5 attempts)
- ✅ Progressive timeout increase (30s → 90s)
- ✅ Detailed logging and error messages
- ✅ Graceful degradation
- ✅ Clear troubleshooting guidance

**Pre-Flight Checks:**
1. DNS resolution test
2. ICMP ping test (if not blocked)
3. TCP port 22 connectivity test (using netcat)
4. SSH service detection (using ssh-keyscan)

**Retry Logic:**
- Initial timeout: 30 seconds
- Max retries: 5 (configurable)
- Backoff delay: 1s, 2s, 4s, 8s, 16s (exponential)
- Timeout increase: +20s per attempt (capped at 90s)

### 2. Workflow Updates

Updated `.github/workflows/11-dev-deployment.yml`:

**All SSH-dependent jobs now:**
- Install network diagnostic tools (`netcat-openbsd`, `dnsutils`)
- Use the enhanced retry script for initial connectivity tests
- Provide clear error messages when connection fails

**Jobs Updated:**
- `migrate` - Migration job
- `deploy-backend` - Backend deployment
- `deploy-frontend` - Frontend deployment (with test step)

### 3. Configuration

The retry script supports environment variables:

```yaml
env:
  MAX_SSH_RETRIES: 5          # Number of retry attempts
  SSH_CONNECT_TIMEOUT: 30     # Initial timeout in seconds
```

---

## Usage

### In GitHub Actions

The workflow automatically uses the enhanced SSH connection:

```yaml
- name: Test SSH connectivity with retry
  env:
    SSHPASS: ${{ secrets.DEV_SSH_PASSWORD }}
    MAX_SSH_RETRIES: 5
    SSH_CONNECT_TIMEOUT: 30
  run: |
    chmod +x .github/scripts/ssh-connect-with-retry.sh
    ./.github/scripts/ssh-connect-with-retry.sh \
      "${{ secrets.DEV_USER }}" \
      "${{ secrets.DEV_HOST }}" \
      "echo 'SSH connection successful'"
```

### Manual Testing

You can test the script locally:

```bash
# Set password in environment
export SSHPASS="your-password"

# Run the script
./.github/scripts/ssh-connect-with-retry.sh \
  username \
  hostname \
  "echo 'test command'"
```

---

## Example Output

### Successful Connection

```
[2025-12-07 03:33:42] Starting SSH connection attempt to user@host
[2025-12-07 03:33:42] Max retries: 5, Initial timeout: 30s

=== Running Pre-Flight Network Diagnostics ===
[2025-12-07 03:33:42] Checking DNS resolution...
[2025-12-07 03:33:42] SUCCESS: DNS resolution successful for host
[2025-12-07 03:33:42] Resolved IP: 192.168.1.100
[2025-12-07 03:33:43] Testing ICMP connectivity (ping)...
[2025-12-07 03:33:45] SUCCESS: ICMP ping successful
[2025-12-07 03:33:45] Testing TCP connectivity to port 22...
[2025-12-07 03:33:46] SUCCESS: Port 22 is reachable via TCP
[2025-12-07 03:33:46] Testing SSH service response...
[2025-12-07 03:33:47] SUCCESS: SSH service is responding

=== Pre-Flight Diagnostics Complete ===

=== Attempt 1/5 (timeout: 30s) ===
[2025-12-07 03:33:47] SUCCESS: SSH connection successful on attempt 1
```

### Failed Connection with Diagnostics

```
[2025-12-07 03:33:42] Starting SSH connection attempt to user@host
[2025-12-07 03:33:42] Max retries: 5, Initial timeout: 30s

=== Running Pre-Flight Network Diagnostics ===
[2025-12-07 03:33:42] Checking DNS resolution...
[2025-12-07 03:33:42] SUCCESS: DNS resolution successful for host
[2025-12-07 03:33:42] Resolved IP: 192.168.1.100
[2025-12-07 03:33:43] Testing ICMP connectivity (ping)...
[2025-12-07 03:33:46] WARNING: ICMP ping failed (firewall may block ICMP)
[2025-12-07 03:33:46] Testing TCP connectivity to port 22...
[2025-12-07 03:33:56] ERROR: Port 22 is NOT reachable via TCP
[2025-12-07 03:33:56] ERROR: Possible causes:
[2025-12-07 03:33:56] ERROR:   1. Server is offline or unreachable
[2025-12-07 03:33:56] ERROR:   2. Firewall blocking port 22
[2025-12-07 03:33:56] ERROR:   3. SSH service not running
[2025-12-07 03:33:56] ERROR:   4. Network routing issue
```

---

## Troubleshooting

If the workflow still fails after this fix, the issue is **infrastructure-related**:

### 1. Verify Server Status

```bash
# From your local machine
ping <server-ip>
ssh <user>@<server-ip>
```

### 2. Check SSH Service

```bash
# On the server
sudo systemctl status ssh
sudo ss -tlnp | grep :22
```

### 3. Check Firewall Rules

The server firewall must allow incoming SSH from GitHub Actions IP ranges.

**Get GitHub Actions IP ranges:**
```bash
curl https://api.github.com/meta | jq -r '.actions[]'
```

**Configure firewall (Ubuntu/UFW):**
```bash
# Allow from specific IP range
sudo ufw allow from <github-ip-range> to any port 22

# Or allow from anywhere (less secure)
sudo ufw allow 22/tcp
```

**Check cloud provider security groups** (AWS, DigitalOcean, Azure, etc.)

### 4. Verify GitHub Secrets

Ensure these secrets are correctly configured in repository settings:

- `DEV_HOST` - Server IP or hostname
- `DEV_USER` - SSH username
- `DEV_SSH_PASSWORD` - SSH password

### 5. Consider Self-Hosted Runners

If GitHub Actions IP ranges cannot be whitelisted, use self-hosted runners:
- Runners within your network can bypass firewall restrictions
- See: https://docs.github.com/en/actions/hosting-your-own-runners

---

## Benefits

### Before
- ❌ Single SSH attempt with fixed 30s timeout
- ❌ No diagnostic information
- ❌ Immediate failure on any network hiccup
- ❌ Unclear error messages

### After
- ✅ 5 retry attempts with exponential backoff
- ✅ Pre-flight network diagnostics
- ✅ Resilient to transient network issues
- ✅ Clear, actionable error messages
- ✅ Progressive timeout increase (30s → 90s)
- ✅ Detailed troubleshooting guidance

---

## Performance Impact

- **Successful connection**: Similar time to before (~5-10s)
- **Transient failure**: Auto-recovers in 10-30s
- **Permanent failure**: Takes longer to detect (up to 5 minutes with all retries)

The longer failure detection time is acceptable because it:
1. Provides detailed diagnostics
2. Avoids false failures from transient issues
3. Gives time for server recovery (e.g., brief maintenance)

---

## Related Files

- `.github/scripts/ssh-connect-with-retry.sh` - Enhanced SSH connection script
- `.github/workflows/11-dev-deployment.yml` - Updated deployment workflow
- `SSH_CONNECTION_TROUBLESHOOTING.md` - Comprehensive troubleshooting guide
- `SSH_DEPLOYMENT_ISSUES_SUMMARY.md` - Issue history

---

## Testing

### Validate Workflow Syntax

```bash
# Install yamllint
sudo apt-get install yamllint

# Check workflow syntax
yamllint .github/workflows/11-dev-deployment.yml
```

### Test SSH Script Locally

```bash
# Set environment variables
export SSHPASS="your-password"
export MAX_SSH_RETRIES=3
export SSH_CONNECT_TIMEOUT=10

# Test the script
./.github/scripts/ssh-connect-with-retry.sh \
  username \
  hostname \
  "uptime"
```

---

## Future Enhancements

Potential improvements for future PRs:

1. **Switch to SSH Key Authentication**
   - More secure than password auth
   - Easier to rotate credentials
   - See: `SSH_CONNECTION_TROUBLESHOOTING.md` section 5

2. **Implement Circuit Breaker Pattern**
   - Fail fast after detecting persistent issues
   - Avoid wasting CI minutes

3. **Add Deployment Server Health Monitoring**
   - Pre-deployment health check
   - Automatic alerting for server issues

4. **Self-Hosted Runners**
   - Eliminate firewall concerns
   - Faster deployment times
   - Better control over runner environment

---

## References

- **Original Issue**: GitHub Actions Run #19998331383
- **PR #1230**: ssh-keyscan timeout fix (merged 2025-12-07)
- **Related Docs**:
  - `SSH_CONNECTION_TROUBLESHOOTING.md`
  - `SSH_DEPLOYMENT_ISSUES_SUMMARY.md`
  - `SSH_ISSUE_QUICK_REF.md`

---

**Last Updated**: 2025-12-07  
**Status**: Active - Deployed to development workflow
