# DigitalOcean Registry Authentication Fix

## 🚨 Problem

The frontend deployment failed with:
- **Docker login to registry.digitalocean.com/meatscentral failed**
- **Invalid, expired, or missing DO_ACCESS_TOKEN secret**

## 🔍 Root Cause

The workflow requires:
1. **Secret**: `DO_ACCESS_TOKEN` - DigitalOcean API token with registry access
2. **Variables**: `DOCR_REGISTRY`, `DOCR_REPO_FRONTEND`, `DOCR_REPO_BACKEND`

One or more of these is missing, invalid, or expired.

## ✅ Solution

### Step 1: Generate New DigitalOcean API Token

1. **Go to DigitalOcean Dashboard**:
   ```
   https://cloud.digitalocean.com/account/api/tokens
   ```

2. **Click "Generate New Token"**

3. **Configure Token**:
   - **Name**: `GitHub Actions Deploy`
   - **Expiration**: Choose (90 days, 1 year, or no expiration)
   - **Scopes**: 
     - ✅ Read (checked)
     - ✅ Write (checked)

4. **Copy the token** (you'll only see it once!)
   - Format: `dop_v1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### Step 2: Set GitHub Secret

1. **Go to GitHub Secrets**:
   ```
   https://github.com/Meats-Central/ProjectMeats/settings/secrets/actions
   ```

2. **Update or Create `DO_ACCESS_TOKEN`**:
   - If it exists, click the pencil icon to edit
   - If not, click "New repository secret"
   - **Name**: `DO_ACCESS_TOKEN`
   - **Value**: Paste the token from Step 1
   - Click "Add secret" or "Update secret"

### Step 3: Verify Repository Variables

1. **Go to GitHub Variables**:
   ```
   https://github.com/Meats-Central/ProjectMeats/settings/variables/actions
   ```

2. **Verify these exist with correct values**:

   | Variable Name | Expected Value | Description |
   |--------------|----------------|-------------|
   | `DOCR_REGISTRY` | `registry.digitalocean.com/meatscentral` | Registry URL |
   | `DOCR_REPO_FRONTEND` | `projectmeats-frontend` | Frontend image name |
   | `DOCR_REPO_BACKEND` | `projectmeats-backend` | Backend image name |

3. **If any are missing, create them**:
   - Click "New repository variable"
   - Enter name and value
   - Click "Add variable"

### Step 4: Verify DigitalOcean Registry Exists

1. **Go to DigitalOcean Container Registry**:
   ```
   https://cloud.digitalocean.com/registry
   ```

2. **Verify registry exists**:
   - Should see: `registry.digitalocean.com/meatscentral`
   - If not, create one named `meatscentral`

3. **Check repositories**:
   - Should see: `projectmeats-frontend` and `projectmeats-backend`
   - These get created automatically on first push

### Step 5: Re-run Workflow

1. **Trigger deployment**:
   ```bash
   # Option A: Push a commit
   git commit --allow-empty -m "chore: trigger deployment after DO token fix"
   git push origin development
   
   # Option B: Manual workflow dispatch
   gh workflow run "Deploy Dev (Frontend + Backend via DOCR and GHCR)"
   ```

2. **Monitor the run**:
   ```
   https://github.com/Meats-Central/ProjectMeats/actions
   ```

## 🔍 Troubleshooting

### Error: "unauthorized: authentication required"

**Cause**: Token doesn't have registry access or is invalid

**Fix**:
1. Generate new token with Read + Write scopes
2. Update `DO_ACCESS_TOKEN` secret
3. Wait 30 seconds and retry

### Error: "repository does not exist"

**Cause**: Image hasn't been built yet or wrong repository name

**Fix**:
1. Check `DOCR_REPO_FRONTEND` matches actual repository name
2. Verify registry exists in DigitalOcean
3. Build step should run before deploy (check workflow logs)

### Error: "registry.digitalocean.com: Name or service not known"

**Cause**: Wrong registry URL or network issue

**Fix**:
1. Verify `DOCR_REGISTRY` is `registry.digitalocean.com/meatscentral`
2. Check if DigitalOcean has any service disruptions
3. Verify deployment server can reach DigitalOcean

### Token Works Locally But Not in GitHub Actions

**Cause**: Token might be missing required scopes

**Fix**:
1. Delete old token in DigitalOcean
2. Create new token with **both** Read + Write scopes
3. Update GitHub secret immediately
4. Retry workflow

## 📊 Current Workflow Configuration

### Secrets Required
```yaml
secrets:
  DO_ACCESS_TOKEN: "dop_v1_..." # DigitalOcean API token
  DEV_FRONTEND_HOST: "104.131.186.75"
  DEV_FRONTEND_USER: "root"
  DEV_FRONTEND_SSH_KEY: "-----BEGIN OPENSSH PRIVATE KEY-----..."
```

### Variables Required
```yaml
vars:
  DOCR_REGISTRY: "registry.digitalocean.com/meatscentral"
  DOCR_REPO_FRONTEND: "projectmeats-frontend"
  DOCR_REPO_BACKEND: "projectmeats-backend"
```

## 🔐 Security Best Practices

1. **Token Expiration**: Use 90-day tokens and rotate regularly
2. **Minimal Scopes**: Only grant necessary permissions (Read + Write for registry)
3. **Token Naming**: Use descriptive names like "GitHub Actions Deploy"
4. **Audit Log**: Review DigitalOcean audit logs periodically
5. **Revoke Old Tokens**: Delete tokens after updating in GitHub

## 📝 Quick Commands

```bash
# Test DO token locally (replace TOKEN)
echo "YOUR_TOKEN" | docker login registry.digitalocean.com/meatscentral -u doctl --password-stdin

# List images in registry
doctl registry repository list-tags meatscentral/projectmeats-frontend

# Verify registry access
doctl registry get

# Check workflow status
gh run list --workflow="Deploy Dev (Frontend + Backend via DOCR and GHCR)" --limit 5

# Re-run failed workflow
gh run rerun <run-id>
```

## 📞 Getting Help

If issues persist:

1. **Check DigitalOcean Status**: https://status.digitalocean.com/
2. **Review Workflow Logs**: Look for specific error messages
3. **Test Token Locally**: Use commands above to verify token works
4. **Contact Support**: Include workflow run ID and error messages

## ✅ Verification Checklist

Before re-running workflow, verify:

- [ ] `DO_ACCESS_TOKEN` secret is set in GitHub
- [ ] Token is valid and hasn't expired
- [ ] Token has Read + Write scopes
- [ ] `DOCR_REGISTRY` variable is set correctly
- [ ] `DOCR_REPO_FRONTEND` variable is set correctly
- [ ] `DOCR_REPO_BACKEND` variable is set correctly
- [ ] Registry `meatscentral` exists in DigitalOcean
- [ ] SSH key secrets are set (from previous step)
- [ ] Deployment server can reach DigitalOcean

## 🎯 Expected Behavior After Fix

1. **Build-and-push job**: 
   - Logs into DOCR successfully
   - Builds frontend and backend images
   - Pushes images with SHA tags

2. **Deploy-frontend job**:
   - SSH connects to droplet
   - Logs into DOCR on remote server
   - Pulls latest image
   - Starts container successfully

3. **Health check**:
   - Frontend responds at deployment URL
   - No errors in container logs

---

**Last Updated**: 2025-12-09
**Related**: FRONTEND_SSH_KEY_SETUP_GUIDE.md
**Workflow**: `.github/workflows/11-dev-deployment.yml`
