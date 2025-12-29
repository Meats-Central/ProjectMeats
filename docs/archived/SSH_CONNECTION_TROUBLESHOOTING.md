# SSH Connection Timeout Troubleshooting Guide

## Issue Summary
GitHub Actions deployment workflows fail with SSH-related timeouts. There are **two distinct issues**:

### Issue 1: ssh-keyscan Timeout ✅ FIXED in PR #1230
```
Setup SSH
ssh-keyscan hangs/times out
Process exits with code 1
```
**Status**: Fixed by PR #1230 - Added `-T 10` timeout flag and fallback handling  
**Reference**: https://github.com/Meats-Central/ProjectMeats/pull/1230

### Issue 2: SSH Connection Timeout (This Guide)
```
ssh: connect to host *** port 22: Connection timed out
Process completed with exit code 255.
```
**Status**: Infrastructure/network issue requiring manual intervention  
**Reference Workflow**: `11-dev-deployment.yml` (and similar for UAT/Production)

---

## Recent Fixes (PR #1230)

**Merged**: December 7, 2025  
**Commit**: [d94d4aa](https://github.com/Meats-Central/ProjectMeats/commit/d94d4aac4256b01335c22fc00ea32f20f607a867)

### What Was Fixed
The `ssh-keyscan` step was hanging indefinitely during SSH setup:

```bash
# ❌ BEFORE (could hang forever)
ssh-keyscan -H "$HOST" >> ~/.ssh/known_hosts

# ✅ AFTER (10s timeout + graceful fallback)
chmod 700 ~/.ssh
ssh-keyscan -T 10 -H "$HOST" >> ~/.ssh/known_hosts 2>&1 || echo "Warning: ssh-keyscan failed, will try connection anyway"
chmod 600 ~/.ssh/known_hosts || true
```

### Changes Applied
1. **Added `-T 10` timeout** - Prevents hanging beyond 10 seconds
2. **Added `|| echo` fallback** - Continues even if keyscan fails
3. **Proper permissions** - `chmod 700` for `.ssh`, `chmod 600` for `known_hosts`
4. **Stderr redirect** - `2>&1` captures timeout errors

### Safety
- ✅ `StrictHostKeyChecking=yes` still validates the actual SSH connection
- ✅ Fallback only bypasses keyscan, not the security check
- ✅ Invalid host keys will still fail at SSH connection time

---

## Root Cause Analysis (Connection Timeout)

The GitHub Actions runner cannot establish an SSH connection to the deployment server. Possible causes:

1. **Server is offline or unreachable**
2. **Firewall blocking GitHub Actions IP ranges**
3. **SSH service not running or listening on port 22**
4. **Incorrect secrets configuration**
5. **Network routing issues**
6. **Cloud provider security group restrictions**

---

## Diagnostic Steps

### 1. Verify GitHub Secrets Configuration

Navigate to: **Repository Settings → Secrets and variables → Actions**

Verify the following secrets are correctly set:

#### Development Environment
- `DEV_HOST` - Server IP address or hostname
- `DEV_USER` - SSH username (typically `django` or `ubuntu`)
- `DEV_SSH_PASSWORD` - SSH password for authentication

#### UAT Environment
- `STAGING_HOST` - UAT server IP/hostname
- `STAGING_USER` - SSH username
- `STAGING_SSH_PASSWORD` - SSH password

#### Production Environment
- `PRODUCTION_HOST` - Production server IP/hostname
- `PRODUCTION_USER` - SSH username
- `PRODUCTION_SSH_PASSWORD` - SSH password

**Action**: Update any missing or incorrect secrets.

---

### 2. Check Server Status

#### From Local Machine
```bash
# Test basic connectivity
ping <server-ip>

# Test SSH connection
ssh <user>@<server-ip>

# Test SSH with verbose output
ssh -v <user>@<server-ip>
```

#### On the Server (if accessible)
```bash
# Check if SSH service is running
sudo systemctl status ssh
# OR for older systems
sudo service ssh status

# Check SSH is listening on port 22
sudo ss -tlnp | grep :22
# OR
sudo netstat -tlnp | grep :22

# Check SSH configuration
sudo cat /etc/ssh/sshd_config | grep -E "^Port|^PermitRootLogin|^PasswordAuthentication"
```

**Expected Output**:
```
Port 22
PasswordAuthentication yes
```

**Action**: If SSH is not running, start it:
```bash
sudo systemctl start ssh
sudo systemctl enable ssh
```

---

### 3. Firewall & Security Group Configuration

#### GitHub Actions IP Ranges

GitHub Actions runners use dynamic IP addresses from Microsoft Azure datacenters. You have two options:

##### Option A: Allow GitHub's IP Ranges (Recommended)
```bash
# Fetch current GitHub IP ranges
curl https://api.github.com/meta | jq -r '.actions[]'

# Example output:
# 13.64.0.0/16
# 13.65.0.0/16
# ...
```

##### Option B: Use Self-Hosted Runners
- Set up a self-hosted runner within your network
- Eliminates need to whitelist external IPs
- See: https://docs.github.com/en/actions/hosting-your-own-runners

#### Cloud Provider Firewall Settings

**DigitalOcean**:
```bash
# List current firewall rules
doctl compute firewall list

# Add GitHub Actions IP range to firewall
doctl compute firewall add-rules <firewall-id> \
  --inbound-rules "protocol:tcp,ports:22,sources:addresses:<github-ip-range>"
```

**AWS EC2 Security Groups**:
1. Go to EC2 Console → Security Groups
2. Select your instance's security group
3. Edit Inbound Rules
4. Add Rule: Type=SSH, Port=22, Source=Custom (GitHub IP ranges)

**Azure Network Security Groups**:
1. Go to Virtual Machines → Networking
2. Add inbound port rule
3. Source: IP Addresses, Source IP: GitHub ranges
4. Destination port: 22

**Google Cloud Firewall Rules**:
```bash
gcloud compute firewall-rules create allow-github-ssh \
  --direction=INGRESS \
  --priority=1000 \
  --network=default \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=<github-ip-range>
```

#### Server-Level Firewall (UFW/iptables)

**UFW (Ubuntu/Debian)**:
```bash
# Check status
sudo ufw status verbose

# Allow SSH from GitHub IP range
sudo ufw allow from <github-ip-range> to any port 22

# Or allow SSH from anywhere (less secure)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

**iptables**:
```bash
# Check current rules
sudo iptables -L -n -v

# Allow SSH from GitHub IP range
sudo iptables -A INPUT -p tcp -s <github-ip-range> --dport 22 -j ACCEPT

# Save rules
sudo netfilter-persistent save
# OR for older systems
sudo iptables-save > /etc/iptables/rules.v4
```

---

### 4. Test Connection from GitHub Actions

Add a diagnostic step to your workflow **before** the actual deployment:

```yaml
- name: Test SSH connectivity
  env:
    SSHPASS: ${{ secrets.DEV_SSH_PASSWORD }}
  run: |
    sudo apt-get update
    sudo apt-get install -y sshpass netcat-openbsd
    
    echo "=== Testing connectivity to ${{ secrets.DEV_HOST }} ==="
    
    # Test if host is reachable
    if ! ping -c 3 ${{ secrets.DEV_HOST }}; then
      echo "❌ Host is not reachable via ping"
      exit 1
    fi
    
    # Test if port 22 is open
    if ! nc -zv ${{ secrets.DEV_HOST }} 22 -w 10; then
      echo "❌ Port 22 is not accessible"
      exit 1
    fi
    
    echo "✅ Host and port are reachable"
    
    # Setup SSH with proper permissions (from PR #1230)
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    ssh-keyscan -T 10 -H "${{ secrets.DEV_HOST }}" >> ~/.ssh/known_hosts 2>&1 || echo "Warning: ssh-keyscan failed"
    chmod 600 ~/.ssh/known_hosts || true
    
    # Test SSH authentication
    sshpass -e ssh -o StrictHostKeyChecking=yes \
      -o ConnectTimeout=30 \
      ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} \
      "echo '✅ SSH authentication successful'"
```

**Note**: This includes the PR #1230 fix for ssh-keyscan timeout handling.

---

### 5. Alternative: SSH Key-Based Authentication

**More secure than password authentication**. Set up SSH keys:

#### On GitHub Actions Runner (Workflow)
```yaml
- name: Setup SSH with key
  run: |
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    echo "${{ secrets.DEV_SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    ssh-keyscan -H "${{ secrets.DEV_HOST }}" >> ~/.ssh/known_hosts

- name: Deploy via SSH
  run: |
    ssh ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} << 'SSH_END'
      # Your deployment commands
    SSH_END
```

#### Generate SSH Key Pair
```bash
# On your local machine
ssh-keygen -t rsa -b 4096 -C "github-actions@projectmeats"

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_rsa.pub <user>@<server>

# Add private key as GitHub secret
cat ~/.ssh/id_rsa
# Copy output and add as DEV_SSH_PRIVATE_KEY secret
```

---

## Quick Fixes Checklist

- [ ] **Verify secrets are set** in GitHub repository settings
- [ ] **Confirm server is online** (`ping <server-ip>`)
- [ ] **Check SSH service is running** (`sudo systemctl status ssh`)
- [ ] **Verify SSH listens on port 22** (`sudo ss -tlnp | grep :22`)
- [ ] **Check server firewall allows SSH** (`sudo ufw status`)
- [ ] **Check cloud provider security groups** allow port 22
- [ ] **Whitelist GitHub Actions IP ranges** in firewall
- [ ] **Test SSH manually** from local machine
- [ ] **Consider switching to SSH keys** instead of passwords

---

## Workflow Modifications (If Needed)

### Add Connection Timeout
```yaml
- name: Deploy with timeout handling
  timeout-minutes: 5  # Fail fast if connection hangs
  env:
    SSHPASS: ${{ secrets.DEV_SSH_PASSWORD }}
  run: |
    sshpass -e ssh -o ConnectTimeout=30 \
      -o StrictHostKeyChecking=yes \
      ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} << 'SSH_END'
      # Deployment commands
    SSH_END
```

### Add Retry Logic
```yaml
- name: Deploy with retries
  uses: nick-fields/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    retry_wait_seconds: 30
    command: |
      sshpass -e ssh -o ConnectTimeout=30 \
        ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} << 'SSH_END'
        # Deployment commands
      SSH_END
```

---

## Common Errors & Solutions

### Error: `ssh-keyscan: Connection timed out` ✅ FIXED
**Cause**: ssh-keyscan hanging indefinitely  
**Solution**: Fixed in PR #1230 with `-T 10` timeout flag and fallback  
**Status**: No action needed if on commit d94d4aa or later

### Error: `Connection timed out` (SSH connection)
**Cause**: Firewall blocking connection or server offline  
**Solution**: Check firewall rules and server status (see sections 2 & 3)

### Error: `Permission denied (publickey,password)`
**Cause**: Incorrect credentials or SSH key mismatch  
**Solution**: Verify `DEV_USER` and `DEV_SSH_PASSWORD` secrets

### Error: `Host key verification failed`
**Cause**: SSH host key not in known_hosts  
**Solution**: ssh-keyscan step handles this automatically (PR #1230 fix)

### Error: `No route to host`
**Cause**: Network routing issue or incorrect IP  
**Solution**: Verify `DEV_HOST` secret contains correct IP/hostname

---

## Security Best Practices

1. **Use SSH keys instead of passwords** - More secure and easier to rotate
2. **Restrict IP ranges** - Only allow GitHub Actions IP ranges
3. **Use environment protection rules** - Require manual approval for production
4. **Rotate credentials regularly** - Update SSH keys/passwords quarterly
5. **Monitor SSH logs** - Review `/var/log/auth.log` for unauthorized access
6. **Disable root login** - Use non-root user with sudo privileges
7. **Enable fail2ban** - Automatically ban IPs with failed login attempts

---

## Monitoring & Alerts

### Enable SSH Logging
```bash
# On server
sudo vim /etc/ssh/sshd_config

# Set log level
LogLevel VERBOSE

# Restart SSH
sudo systemctl restart ssh

# Monitor logs
sudo tail -f /var/log/auth.log
```

### GitHub Actions Notifications
Add Slack/Discord notifications for deployment failures:

```yaml
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'SSH connection failed to ${{ secrets.DEV_HOST }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Related Documentation

- **PR #1230**: ssh-keyscan timeout fix - https://github.com/Meats-Central/ProjectMeats/pull/1230
- **Commit d94d4aa**: Merged fix for ssh-keyscan hanging
- **Deployment Workflows**: `.github/workflows/11-dev-deployment.yml`
- **Deployment Runbook**: `DEPLOYMENT_RUNBOOK.md`
- **Network Troubleshooting**: `NETWORK_ERROR_TROUBLESHOOTING.md`
- **GitHub Actions Logs**: Repository → Actions → Failed workflow run

---

## Support & Escalation

If issue persists after following this guide:

1. **Capture diagnostics**:
   ```bash
   # On server
   sudo systemctl status ssh
   sudo ss -tlnp | grep :22
   sudo tail -50 /var/log/auth.log
   
   # From local machine
   ssh -vvv <user>@<server> 2>&1 | tee ssh-debug.log
   ```

2. **Check cloud provider status** - Look for service outages
3. **Review GitHub Actions logs** - Check for additional error details
4. **Contact infrastructure team** - Share diagnostics and error messages

---

**Last Updated**: 2025-12-07  
**Status**: Active troubleshooting guide for SSH connection issues
