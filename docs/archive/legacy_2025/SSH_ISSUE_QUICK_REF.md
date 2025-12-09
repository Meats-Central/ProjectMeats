# SSH Issues - Quick Reference

## Two Separate Issues

### 1️⃣ ssh-keyscan Timeout ✅ RESOLVED
- **Fixed**: PR #1230 (Dec 7, 2025)
- **Symptom**: Workflow hangs at "Setup SSH" step
- **Solution**: Added `-T 10` timeout + fallback handling
- **No action needed** - Already merged to `development`

### 2️⃣ SSH Connection Timeout ⚠️ ACTION REQUIRED
- **Error**: `ssh: connect to host *** port 22: Connection timed out`
- **Cause**: Firewall/network issue
- **Action**: Follow troubleshooting guide below

---

## Immediate Actions for Connection Timeout

### Step 1: Verify Secrets (2 minutes)
Go to: **Repository Settings → Secrets and variables → Actions**

Check these are set correctly:
- `DEV_HOST` - Server IP/hostname
- `DEV_USER` - SSH username
- `DEV_SSH_PASSWORD` - SSH password

### Step 2: Test Server (5 minutes)
```bash
# From your local machine
ping <server-ip>                    # Is server online?
nc -zv <server-ip> 22               # Is SSH port open?
ssh <user>@<server-ip>              # Can you connect?
```

### Step 3: Check Firewall (10 minutes)

**Get GitHub Actions IP ranges**:
```bash
curl https://api.github.com/meta | jq -r '.actions[]'
```

**Allow in firewall**:
```bash
# UFW (Ubuntu)
sudo ufw allow from 13.64.0.0/16 to any port 22
sudo ufw allow from 13.65.0.0/16 to any port 22
# ... repeat for all GitHub IP ranges

# OR allow from anywhere (less secure)
sudo ufw allow 22/tcp
```

**Cloud provider**: Update security group to allow port 22 from GitHub IPs

### Step 4: Restart SSH Service (if needed)
```bash
sudo systemctl restart ssh
sudo systemctl status ssh
```

---

## Documentation Files

| File | Purpose |
|------|---------|
| `SSH_CONNECTION_TROUBLESHOOTING.md` | 📖 Comprehensive troubleshooting guide |
| `SSH_DEPLOYMENT_ISSUES_SUMMARY.md` | 📋 Complete issue history & solutions |
| `SSH_ISSUE_QUICK_REF.md` | ⚡ This file - quick actions |

---

## Related Links

- **PR #1230**: https://github.com/Meats-Central/ProjectMeats/pull/1230
- **Commit d94d4aa**: https://github.com/Meats-Central/ProjectMeats/commit/d94d4aac4256b01335c22fc00ea32f20f607a867
- **GitHub Actions IPs**: https://api.github.com/meta

---

**TL;DR**: ssh-keyscan timeout is fixed. If you still see connection timeouts, check your server's firewall allows GitHub Actions IP ranges.
