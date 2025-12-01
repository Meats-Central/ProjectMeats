# GitHub Issue: Align staging.env placeholders with existing GitHub secrets for consistent deployment

## Issue Title
Align staging.env placeholders with existing GitHub secrets for consistent deployment

## Description

### Problem Statement

There is a mismatch between the placeholder variable names in `config/environments/staging.env` and the GitHub secrets currently documented and used in the deployment workflow (`.github/workflows/unified-deployment.yml`).

### Current Issues

1. **Incomplete Secret Documentation**: The `staging.env` file references many environment variables (e.g., `STAGING_DB_USER`, `STAGING_SECRET_KEY`, `STAGING_DOMAIN`, etc.) that are not documented in the existing GitHub secrets documentation.

2. **Workflow Limitation**: The GitHub Actions workflow currently only passes `STAGING_SUPERUSER_*` credentials to the staging deployment script, unlike the development deployment which passes all `DEVELOPMENT_DB_*` and other environment variables.

3. **Inconsistent Placeholder Values**: The superuser configuration in `staging.env` previously used hardcoded `change_me_in_secrets` placeholders instead of environment variable syntax like `${STAGING_SUPERUSER_USERNAME}`.

### Changes Implemented in PR #[NUMBER]

#### 1. Updated `config/environments/staging.env`
- Added clear documentation comments indicating which variables must be set in GitHub Secrets
- Categorized secrets as **required** vs. **optional**:
  - **Required**: Database credentials, Django settings, domains, superuser credentials
  - **Optional**: AI services (OpenAI, Anthropic), email (SMTP), cache (Redis), monitoring (Sentry)
- Changed superuser placeholders from `change_me_in_secrets` to `${STAGING_SUPERUSER_*}` for consistency
- Added inline documentation explaining how secrets are used during deployment

#### 2. Updated Documentation Files
Updated three key documentation files with comprehensive GitHub secrets requirements:

**`docs/ENVIRONMENT_GUIDE.md`:**
- Added "Required GitHub Secrets for Staging" section
- Listed all repository-level and environment-specific secrets
- Provided example values and generation commands (e.g., for SECRET_KEY)

**`docs/DEPLOYMENT_GUIDE.md`:**
- Expanded staging deployment section
- Listed all required and optional secrets
- Added important note about current workflow limitations
- Provided server-side environment configuration guidance

**`docs/workflows/unified-workflow.md`:**
- Expanded uat2-backend environment secrets table
- Added Required/Optional indicators
- Updated Quick Reference checklist with complete staging secret list
- Added important notes about workflow implementation gaps

### Required GitHub Secrets for Staging

The following secrets must be configured in the GitHub repository for complete staging deployment support:

#### Repository-Level Secrets
(Settings → Secrets and variables → Actions → Repository secrets)

- `STAGING_HOST` - Staging server IP/hostname (e.g., `192.168.1.101` or `uat.yourdomain.com`)
- `STAGING_USER` - SSH username for staging server (e.g., `django`)
- `SSH_PASSWORD` - SSH password for staging server
- `GIT_TOKEN` - GitHub Personal Access Token (already configured)

#### Environment Secrets for `uat2-backend`
(Settings → Environments → uat2-backend → Environment secrets)

**Currently Configured:**
- ✅ `STAGING_API_URL` - Staging backend API URL
- ✅ `STAGING_SUPERUSER_USERNAME` - Admin username
- ✅ `STAGING_SUPERUSER_EMAIL` - Admin email
- ✅ `STAGING_SUPERUSER_PASSWORD` - Admin password

**MISSING - Need to Add:**

*Core Django Settings:*
- ❌ `STAGING_SECRET_KEY` - Django secret key
  - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  
*Database Configuration:*
- ❌ `STAGING_DB_USER` - PostgreSQL database username
- ❌ `STAGING_DB_PASSWORD` - PostgreSQL database password
- ❌ `STAGING_DB_HOST` - PostgreSQL database host (e.g., `localhost` or DB server IP)
- ❌ `STAGING_DB_PORT` - PostgreSQL database port (typically `5432`)
- ❌ `STAGING_DB_NAME` - PostgreSQL database name (e.g., `projectmeats_staging`)

*Domain Configuration:*
- ❌ `STAGING_DOMAIN` - Main staging domain (e.g., `uat.meatscentral.com`)
- ❌ `STAGING_API_DOMAIN` - API staging domain (e.g., `uat-api.meatscentral.com`)
- ❌ `STAGING_FRONTEND_DOMAIN` - Frontend staging domain (e.g., `uat.meatscentral.com`)

*Optional - Add if Features Enabled:*
- ❌ `STAGING_OPENAI_API_KEY` - OpenAI API key for AI features
- ❌ `STAGING_ANTHROPIC_API_KEY` - Anthropic API key for AI features
- ❌ `STAGING_EMAIL_HOST` - SMTP server hostname (e.g., `smtp.gmail.com`)
- ❌ `STAGING_EMAIL_USER` - SMTP username
- ❌ `STAGING_EMAIL_PASSWORD` - SMTP password
- ❌ `STAGING_REDIS_HOST` - Redis server host (e.g., `localhost`)
- ❌ `STAGING_REDIS_PORT` - Redis server port (typically `6379`)
- ❌ `STAGING_SENTRY_DSN` - Sentry error tracking DSN

### Workflow Update Required

⚠️ **IMPORTANT**: The GitHub Actions workflow (`.github/workflows/unified-deployment.yml`) needs to be updated to pass these new environment variables during staging deployment.

**Current Behavior:**
```yaml
# Lines 422-427 in unified-deployment.yml
env:
  SSHPASS: ${{ secrets.SSH_PASSWORD }}
  GIT_TOKEN: ${{ secrets.GIT_TOKEN }}
  STAGING_SUPERUSER_USERNAME: ${{ secrets.STAGING_SUPERUSER_USERNAME }}
  STAGING_SUPERUSER_EMAIL: ${{ secrets.STAGING_SUPERUSER_EMAIL }}
  STAGING_SUPERUSER_PASSWORD: ${{ secrets.STAGING_SUPERUSER_PASSWORD }}
```

**Required Addition:**
The workflow should be updated to include database and other secrets, similar to how the development deployment works (lines 226-234):
```yaml
env:
  # ... existing env vars ...
  STAGING_SECRET_KEY: ${{ secrets.STAGING_SECRET_KEY }}
  STAGING_DB_USER: ${{ secrets.STAGING_DB_USER }}
  STAGING_DB_PASSWORD: ${{ secrets.STAGING_DB_PASSWORD }}
  STAGING_DB_HOST: ${{ secrets.STAGING_DB_HOST }}
  STAGING_DB_PORT: ${{ secrets.STAGING_DB_PORT }}
  STAGING_DB_NAME: ${{ secrets.STAGING_DB_NAME }}
  STAGING_DOMAIN: ${{ secrets.STAGING_DOMAIN }}
  STAGING_API_DOMAIN: ${{ secrets.STAGING_API_DOMAIN }}
  STAGING_FRONTEND_DOMAIN: ${{ secrets.STAGING_FRONTEND_DOMAIN }}
  # Optional secrets (if configured)
  STAGING_OPENAI_API_KEY: ${{ secrets.STAGING_OPENAI_API_KEY }}
  STAGING_ANTHROPIC_API_KEY: ${{ secrets.STAGING_ANTHROPIC_API_KEY }}
  # ... etc
```

And these should be exported in the deployment script (lines 494-507).

### Action Items

- [ ] **Add missing GitHub secrets** to the `uat2-backend` environment in repository settings
  - Add all required secrets listed above
  - Optionally add optional secrets if features are enabled
  
- [ ] **Update GitHub Actions workflow** (`.github/workflows/unified-deployment.yml`)
  - Add new environment variables to the `deploy-backend-staging` job
  - Export these variables in the SSH deployment script
  - Test deployment to ensure all secrets are properly passed
  
- [ ] **Configure staging server environment**
  - Ensure all environment variables are properly set on the staging server
  - Variables can be set in `/etc/environment`, systemd service files, or shell profiles
  - Verify Django can read these variables using `python-decouple`

- [ ] **Test deployment**
  - Run `make env-staging` locally to verify configuration loads
  - Trigger a staging deployment via GitHub Actions
  - Verify all environment variables are correctly passed and used
  - Check that Django application starts without environment variable errors

### Benefits

1. **Consistency**: Aligns placeholder naming in `staging.env` with GitHub secret names
2. **Documentation**: Clear documentation of all required and optional secrets
3. **Maintainability**: Easier to understand which secrets need to be configured
4. **Deployment Reliability**: Reduces deployment failures due to missing environment variables
5. **Security**: Better separation of secrets from code with proper GitHub Secrets integration

### References

- Updated files in PR: `config/environments/staging.env`, `docs/ENVIRONMENT_GUIDE.md`, `docs/DEPLOYMENT_GUIDE.md`, `docs/workflows/unified-workflow.md`
- Related workflow: `.github/workflows/unified-deployment.yml` (lines 399-556)
- Development deployment pattern: Lines 200-394 (shows proper environment variable passing)

### Related Documentation

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Environment Variables in GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/variables)
- ProjectMeats ENVIRONMENT_GUIDE.md
- ProjectMeats DEPLOYMENT_GUIDE.md

---

**Labels**: `deployment`, `configuration`, `staging`, `github-actions`, `documentation`
**Priority**: High
**Type**: Enhancement
