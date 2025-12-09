# SSH Deployment Issues - Complete Summary

**Date**: December 7, 2025  
**Status**: Partially resolved - ssh-keyscan fixed, connection timeout requires infrastructure action

---

## Overview

The deployment pipeline has experienced two distinct SSH-related issues:

### ✅ Issue 1: ssh-keyscan Timeout (RESOLVED)
**PR**: [#1230](https://github.com/Meats-Central/ProjectMeats/pull/1230)  
**Commit**: [d94d4aa](https://github.com/Meats-Central/ProjectMeats/commit/d94d4aac4256b01335c22fc00ea32f20f607a867)  
**Merged**: December 7, 2025, 1:19 AM UTC

### ⚠️ Issue 2: SSH Connection Timeout (INFRASTRUCTURE)
**Error**: `ssh: connect to host *** port 22: Connection timed out`  
**Cause**: Firewall/network preventing GitHub Actions from reaching deployment server  
**Action Required**: Infrastructure configuration (see troubleshooting guide)

---

## Issue 1: ssh-keyscan Timeout ✅

### Problem Statement
During the SSH setup phase of deployment workflows, the `ssh-keyscan` command would hang indefinitely, causing the workflow to eventually fail with exit code 1.

**Affected Jobs**:
- `migrate` - Database migrations via SSH
- `deploy-frontend` - Frontend container deployment
- `deploy-backend` - Backend container deployment

### Root Cause
```bash
# Original code (no timeout)
ssh-keyscan -H "${{ secrets.DEV_HOST }}" >> ~/.ssh/known_hosts
```

The `ssh-keyscan` command had no timeout configured. If the host was temporarily unreachable, experiencing network issues, or had firewall rules blocking the scan, the command would hang indefinitely until GitHub Actions killed the job.

### Solution Implemented

**Changes in `.github/workflows/11-dev-deployment.yml`**:

```yaml
- name: Setup SSH
  run: |
    sudo apt-get update
    sudo apt-get install -y sshpass
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    # Use -T timeout to prevent hanging, continue on failure
    ssh-keyscan -T 10 -H "${{ secrets.DEV_HOST }}" >> ~/.ssh/known_hosts 2>&1 || echo "Warning: ssh-keyscan failed, will try connection anyway"
    chmod 600 ~/.ssh/known_hosts || true
```

**Key Improvements**:
1. ✅ **`-T 10` flag** - Limits ssh-keyscan to 10 seconds maximum
2. ✅ **`|| echo` fallback** - Continues workflow even if keyscan fails
3. ✅ **`chmod 700/600`** - Proper SSH directory and file permissions
4. ✅ **`2>&1` redirect** - Captures stderr for debugging

### Why This is Safe

The ssh-keyscan fallback does NOT compromise security:

- `StrictHostKeyChecking=yes` is still used in the actual SSH connection
- If the host key is invalid or missing, the SSH connection will fail (as expected)
- The fallback only skips the *pre-scan* step, not the actual host key verification

### Impact
- ⏱️ Deployments no longer hang on ssh-keyscan
- 🔄 Workflows can proceed even with transient network issues
- 📊 Better visibility with warning messages in logs

### Testing
Applied to all deployment workflows:
- `11-dev-deployment.yml` ✅
- `12-uat-deployment.yml` (needs verification)
- `13-prod-deployment.yml` (needs verification)

---

## Issue 2: SSH Connection Timeout ⚠️

### Problem Statement
After ssh-keyscan completes, the actual SSH connection fails:

```
ssh: connect to host *** port 22: Connection timed out
Process completed with exit code 255.
```

### Root Causes

This is a **distinct issue** from ssh-keyscan timeout. Possible causes:

1. **Firewall Blocking GitHub Actions**
   - GitHub Actions runners use dynamic IPs from Azure datacenters
   - Deployment server firewall may not whitelist these ranges
   - Solution: Allow GitHub Actions IP ranges in firewall rules

2. **Server Offline/Unreachable**
   - Deployment server is down or suspended
   - Solution: Verify server is running and accessible

3. **SSH Service Not Running**
   - SSH daemon (sshd) is stopped or crashed
   - Solution: Restart SSH service on server

4. **Incorrect Secrets**
   - `DEV_HOST` contains wrong IP/hostname
   - `DEV_USER` is incorrect
   - `DEV_SSH_PASSWORD` is incorrect
   - Solution: Verify all secrets in repository settings

5. **Cloud Provider Security Groups**
   - Security group rules blocking port 22
   - Solution: Update security group to allow SSH from GitHub Actions IPs

6. **Network Routing Issues**
   - DNS resolution failure
   - Network partition between GitHub and server
   - Solution: Test connectivity from different locations

### Diagnosis Steps

#### 1. Verify Secrets
Navigate to: **Repository Settings → Secrets and variables → Actions**

Check:
- ✅ `DEV_HOST` - Server IP or hostname
- ✅ `DEV_USER` - SSH username (e.g., `django`, `ubuntu`)
- ✅ `DEV_SSH_PASSWORD` - Correct password

#### 2. Test Server Accessibility

**From your local machine**:
```bash
# Test basic connectivity
ping <server-ip>

# Test SSH port
nc -zv <server-ip> 22

# Test SSH connection
ssh <user>@<server-ip>

# Verbose SSH for debugging
ssh -v <user>@<server-ip>
```

**On the server** (if accessible):
```bash
# Check SSH service
sudo systemctl status ssh

# Check if SSH is listening
sudo ss -tlnp | grep :22

# Check SSH configuration
sudo cat /etc/ssh/sshd_config | grep -E "^Port|^PasswordAuthentication"
```

#### 3. Check Firewall Configuration

**GitHub Actions IP Ranges**:
```bash
# Fetch current ranges
curl https://api.github.com/meta | jq -r '.actions[]'
```

**Server Firewall (UFW)**:
```bash
sudo ufw status verbose
sudo ufw allow from <github-ip-range> to any port 22
```

**Cloud Provider Firewall**:
- **DigitalOcean**: Firewall → Inbound Rules → Add SSH rule for GitHub IPs
- **AWS**: EC2 Security Groups → Inbound Rules → Add SSH (port 22) for GitHub IPs
- **Azure**: Network Security Groups → Add inbound rule for port 22
- **Google Cloud**: Firewall Rules → Add rule for TCP:22 from GitHub IPs

### Solutions

#### Option 1: Whitelist GitHub Actions IPs (Recommended)

Add GitHub's action runner IP ranges to your firewall:

```bash
# Example for DigitalOcean
doctl compute firewall add-rules <firewall-id> \
  --inbound-rules "protocol:tcp,ports:22,sources:addresses:13.64.0.0/16"
```

#### Option 2: Use Self-Hosted Runner

Set up a runner within your network:
- Eliminates need to whitelist external IPs
- Faster deployments (no Docker layer download)
- Better control over runner environment

See: https://docs.github.com/en/actions/hosting-your-own-runners

#### Option 3: Use SSH Key Authentication

More secure than passwords:

```yaml
- name: Setup SSH with key
  run: |
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    echo "${{ secrets.DEV_SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    ssh-keyscan -T 10 -H "${{ secrets.DEV_HOST }}" >> ~/.ssh/known_hosts 2>&1 || true

- name: Deploy
  run: |
    ssh ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} << 'SSH'
      # Deployment commands
    SSH
```

---

## Quick Action Checklist

### For ssh-keyscan Timeout (Already Fixed ✅)
- [x] PR #1230 merged to `development`
- [x] Fix applied to `11-dev-deployment.yml`
- [ ] Verify fix in `12-uat-deployment.yml`
- [ ] Verify fix in `13-prod-deployment.yml`

### For SSH Connection Timeout (Action Required ⚠️)
- [ ] Verify `DEV_HOST`, `DEV_USER`, `DEV_SSH_PASSWORD` secrets
- [ ] Confirm server is online (`ping <server-ip>`)
- [ ] Check SSH service is running (`sudo systemctl status ssh`)
- [ ] Verify port 22 is open (`nc -zv <server-ip> 22`)
- [ ] Check server firewall allows SSH (`sudo ufw status`)
- [ ] Check cloud provider security group rules
- [ ] Whitelist GitHub Actions IP ranges in firewall
- [ ] Test SSH manually from local machine
- [ ] Consider switching to SSH key authentication

---

## Monitoring & Prevention

### Add Diagnostic Step to Workflows

```yaml
- name: Pre-deployment connectivity test
  env:
    SSHPASS: ${{ secrets.DEV_SSH_PASSWORD }}
  run: |
    echo "=== Testing ${{ secrets.DEV_HOST }} ==="
    
    # Test network connectivity
    ping -c 3 ${{ secrets.DEV_HOST }} || echo "⚠️ Ping failed"
    
    # Test SSH port
    nc -zv ${{ secrets.DEV_HOST }} 22 -w 10 || echo "⚠️ Port 22 not accessible"
    
    # Test SSH with timeout from PR #1230
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    ssh-keyscan -T 10 -H "${{ secrets.DEV_HOST }}" >> ~/.ssh/known_hosts 2>&1 || echo "⚠️ ssh-keyscan failed"
    
    # Test authentication
    sshpass -e ssh -o ConnectTimeout=30 -o StrictHostKeyChecking=yes \
      ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} \
      "echo '✅ SSH connection successful'"
```

### Set Up Alerts

**Slack/Discord Notifications**:
```yaml
- name: Notify on SSH failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'SSH connection failed to ${{ secrets.DEV_HOST }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Regular Health Checks

Schedule a workflow to test SSH connectivity daily:

```yaml
name: SSH Health Check
on:
  schedule:
    - cron: '0 8 * * *'  # 8 AM daily
  workflow_dispatch:

jobs:
  test-ssh:
    runs-on: ubuntu-latest
    steps:
      - name: Test all deployment servers
        env:
          SSHPASS: ${{ secrets.DEV_SSH_PASSWORD }}
        run: |
          # Test DEV
          ssh-keyscan -T 10 ${{ secrets.DEV_HOST }} || echo "⚠️ DEV unreachable"
          
          # Test UAT
          ssh-keyscan -T 10 ${{ secrets.STAGING_HOST }} || echo "⚠️ UAT unreachable"
          
          # Test PROD
          ssh-keyscan -T 10 ${{ secrets.PRODUCTION_HOST }} || echo "⚠️ PROD unreachable"
```

---

## Related Documentation

- **SSH Connection Troubleshooting**: `SSH_CONNECTION_TROUBLESHOOTING.md` (comprehensive guide)
- **PR #1230**: https://github.com/Meats-Central/ProjectMeats/pull/1230
- **Commit d94d4aa**: https://github.com/Meats-Central/ProjectMeats/commit/d94d4aac4256b01335c22fc00ea32f20f607a867
- **Deployment Runbook**: `DEPLOYMENT_RUNBOOK.md`
- **Network Troubleshooting**: `NETWORK_ERROR_TROUBLESHOOTING.md`

---

## Change History

| Date | Issue | Action | Status |
|------|-------|--------|--------|
| 2025-12-07 | ssh-keyscan timeout | PR #1230 merged | ✅ Resolved |
| 2025-12-07 | SSH connection timeout | Documentation created | ⚠️ Infrastructure action required |

---

**Last Updated**: 2025-12-07  
**Maintainer**: DevOps Team  
**Status**: Active troubleshooting reference
