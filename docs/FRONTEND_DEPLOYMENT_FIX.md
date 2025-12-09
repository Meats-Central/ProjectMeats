# Fix Frontend Deployment SSH Connection - Action Required

> **⚠️ DEPRECATION NOTICE (2025-12-09)**  
> This document references deprecated workflow files (`11-dev-deployment.yml`, `12-uat-deployment.yml`, `13-prod-deployment.yml`) that have been replaced by the reusable workflow architecture (`main-pipeline.yml` + `reusable-deploy.yml`).  
>   
> **Current Documentation:** See [DEVELOPMENT_WORKFLOW.md](./DEVELOPMENT_WORKFLOW.md) for the active deployment architecture.  
>   
> This file is retained for historical reference only.

---

## Summary

The GitHub Actions deployment workflow has been updated to fix the SSH connection timeout issue for the dev frontend deployment. The workflow now correctly uses separate server configurations for frontend and backend deployments.

## What Changed

### Workflow Updates
File: `.github/workflows/11-dev-deployment.yml`

The `deploy-frontend` job now uses separate secrets for connecting to the frontend server:
- `DEV_FRONTEND_HOST` - Frontend server IP/hostname (should be 104.131.186.75)
- `DEV_FRONTEND_USER` - SSH username for frontend server
- `DEV_FRONTEND_PASSWORD` - SSH password for frontend server

Backend deployment continues to use existing secrets:
- `DEV_HOST` - Backend server IP (142.93.73.23)
- `DEV_USER` - SSH username for backend server
- `DEV_SSH_PASSWORD` - SSH password for backend server

## Action Required: Configure GitHub Secrets

**⚠️ IMPORTANT: You must configure these new secrets before the workflow will work.**

### Steps to Configure Secrets

1. Navigate to repository settings:
   - Go to **GitHub repository** → **Settings** → **Secrets and variables** → **Actions**

2. Click **"New repository secret"** and add each of the following:

   | Secret Name | Value | Notes |
   |------------|-------|-------|
   | `DEV_FRONTEND_HOST` | `104.131.186.75` | Or hostname that resolves to this IP |
   | `DEV_FRONTEND_USER` | `<username>` | SSH username for frontend server (e.g., `ubuntu`, `django`) |
   | `DEV_FRONTEND_PASSWORD` | `<password>` | SSH password for frontend server |

3. Verify existing backend secrets are still configured:
   - `DEV_HOST` (should be `142.93.73.23`)
   - `DEV_USER`
   - `DEV_SSH_PASSWORD`

### Server Requirements

Ensure the frontend server at `104.131.186.75` meets these requirements:

1. **SSH Access**
   - SSH service is running: `sudo systemctl status ssh`
   - Port 22 is open: `sudo ss -tlnp | grep :22`
   - Firewall allows connections from GitHub Actions IP ranges

2. **User Permissions**
   - User has sudo privileges
   - User can run Docker commands (member of docker group or via sudo)

3. **Software Installed**
   - Docker
   - nginx (for reverse proxy configuration)

## Testing the Fix

After configuring the secrets:

1. Push a change to the `development` branch
2. Monitor the workflow run at: https://github.com/Meats-Central/ProjectMeats/actions
3. The `deploy-frontend` job should now:
   - Successfully connect to `104.131.186.75`
   - Pass the SSH connectivity test
   - Complete the frontend deployment

## Troubleshooting

If the deployment still fails:

1. **Verify Secret Configuration**
   ```bash
   # On your local machine with GitHub CLI:
   gh secret list
   ```

2. **Test SSH Connection Manually**
   ```bash
   # Test connection to frontend server
   ssh <DEV_FRONTEND_USER>@104.131.186.75
   
   # Test connection to backend server
   ssh <DEV_USER>@142.93.73.23
   ```

3. **Check Server Firewall**
   ```bash
   # On the frontend server
   sudo ufw status
   sudo ufw allow 22/tcp
   ```

4. **Check SSH Service**
   ```bash
   # On the frontend server
   sudo systemctl status ssh
   sudo systemctl restart ssh
   ```

5. **Review Workflow Logs**
   - Go to the failed workflow run in GitHub Actions
   - Check the `deploy-frontend` job logs
   - Look for specific error messages in the "Test SSH connectivity with retry" step

## Related Documentation

- [GitHub Secrets Configuration Guide](./GITHUB_SECRETS_CONFIGURATION.md) - Complete guide for all secrets
- [GitHub Actions Workflows](../.github/workflows/README.md) - Workflow documentation
- [SSH Connection Script](../.github/scripts/ssh-connect-with-retry.sh) - SSH retry logic

## Security Notes

- Use strong, unique passwords for SSH authentication
- Consider migrating to SSH key-based authentication for improved security
- Regularly rotate credentials
- Restrict SSH access to only necessary IP ranges
- Monitor authentication logs for suspicious activity

## Questions?

If you encounter issues:
1. Check the [GitHub Secrets Configuration Guide](./GITHUB_SECRETS_CONFIGURATION.md)
2. Review workflow logs in GitHub Actions
3. Verify server connectivity and configuration
4. Check firewall rules and SSH service status

---

**Last Updated**: 2025-12-09
**Related PR**: #1240
**Related Workflow Run**: https://github.com/Meats-Central/ProjectMeats/actions/runs/20047585483
