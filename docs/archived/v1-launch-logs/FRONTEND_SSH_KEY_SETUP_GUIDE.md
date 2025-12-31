# Frontend SSH Key Authentication Setup Guide

## ✅ What Was Done

### 1. Workflow Updated
- **Branch**: `fix/frontend-ssh-key-authentication`
- **PR**: https://github.com/Meats-Central/ProjectMeats/pull/1247
- **File Changed**: `.github/workflows/11-dev-deployment.yml`

### 2. SSH Key Added to Droplet
- **Server**: `104.131.186.75` (meatscentral-dev-frontend)
- **User**: `root`
- **Key Location**: `~/.ssh/authorized_keys`
- **Key Type**: `ssh-ed25519`

## 🔐 Required GitHub Secrets

You need to set these secrets in the **`dev-frontend` environment**:

### How to Set Secrets (Web UI - RECOMMENDED)

1. **Go to GitHub Settings**:
   ```
   https://github.com/Meats-Central/ProjectMeats/settings/environments
   ```

2. **Click on `dev-frontend` environment**

3. **Add Environment Secrets**:

   #### Secret 1: DEV_FRONTEND_HOST
   - **Name**: `DEV_FRONTEND_HOST`
   - **Value**: `104.131.186.75`

   #### Secret 2: DEV_FRONTEND_USER
   - **Name**: `DEV_FRONTEND_USER`
   - **Value**: `root`

   #### Secret 3: DEV_FRONTEND_SSH_KEY
   - **Name**: `DEV_FRONTEND_SSH_KEY`
   - **Value**: Your **private** SSH key content
   
   **On Windows PowerShell**:
   ```powershell
   Get-Content ~/.ssh/id_ed25519
   ```
   
   Copy the **entire output** including:
   ```
   -----BEGIN OPENSSH PRIVATE KEY-----
   ... (all the content)
   -----END OPENSSH PRIVATE KEY-----
   ```
   
   Paste this into the secret value field.

4. **Click "Add secret"** for each one

## 🧪 Testing

### Test SSH Connection Locally
```bash
ssh root@104.131.186.75
```
Should connect without asking for password.

### Test After PR Merge
Once the PR is merged to `development`:
1. Push any commit to `development` branch
2. Watch workflow: https://github.com/Meats-Central/ProjectMeats/actions
3. Check "deploy-frontend" job logs
4. Should see: "SSH connection successful"

## 🔄 Migration from Password to SSH Key

### Before (Old)
```yaml
secrets:
  DEV_FRONTEND_PASSWORD: "<password>"
```

### After (New)
```yaml
secrets:
  DEV_FRONTEND_SSH_KEY: "<private-key-content>"
```

## 📋 Checklist

- [x] SSH key added to droplet (`~/.ssh/authorized_keys`)
- [x] Local SSH connection tested
- [x] Workflow updated to use SSH key
- [x] Branch pushed: `fix/frontend-ssh-key-authentication`
- [x] PR created: #1247
- [ ] **Set `DEV_FRONTEND_HOST` secret**
- [ ] **Set `DEV_FRONTEND_USER` secret**
- [ ] **Set `DEV_FRONTEND_SSH_KEY` secret**
- [ ] Merge PR to development
- [ ] Test deployment workflow
- [ ] Verify deployment succeeds

## 🚨 Important Notes

1. **Private Key Security**:
   - Never commit private keys to git
   - Only store in GitHub Secrets
   - Rotate keys if compromised

2. **Secret Names**:
   - Must be exactly: `DEV_FRONTEND_HOST`, `DEV_FRONTEND_USER`, `DEV_FRONTEND_SSH_KEY`
   - Case-sensitive
   - Must be in `dev-frontend` **environment** (not repository secrets)

3. **SSH Key Format**:
   - Must include header and footer lines
   - Must be the **private** key (not public `.pub` file)
   - Should be OpenSSH format (starts with `-----BEGIN OPENSSH PRIVATE KEY-----`)

## 🔍 Troubleshooting

### Workflow Fails: "Permission denied (publickey)"
- Check that `DEV_FRONTEND_SSH_KEY` contains the **private** key
- Verify key format includes header/footer
- Confirm public key is in droplet's `~/.ssh/authorized_keys`

### Workflow Fails: "Could not resolve hostname"
- Verify `DEV_FRONTEND_HOST` is set to `104.131.186.75`
- Check environment is `dev-frontend` (not `dev-backend`)

### Workflow Fails: "Host key verification failed"
- The `ssh-keyscan` step should prevent this
- If it still fails, check firewall allows SSH from GitHub Actions IPs

## 📞 Need Help?

If you encounter issues:
1. Check workflow logs: https://github.com/Meats-Central/ProjectMeats/actions
2. Verify secrets are set: https://github.com/Meats-Central/ProjectMeats/settings/environments
3. Test SSH locally: `ssh root@104.131.186.75`
4. Review this guide: `/workspaces/ProjectMeats/FRONTEND_SSH_KEY_SETUP_GUIDE.md`

---

**Last Updated**: 2025-12-09
**Created By**: GitHub Copilot
**PR**: #1247
