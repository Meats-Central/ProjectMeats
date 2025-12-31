# ProjectMeats Environment Configuration

## ⚠️ CRITICAL: Read This First

**🎯 Single Source of Truth**: [`config/env.manifest.json`](env.manifest.json) (v3.3)

**📖 Complete Documentation**: [`docs/CONFIGURATION_AND_SECRETS.md`](../docs/CONFIGURATION_AND_SECRETS.md)

---

## Quick Command Reference

```bash
# Check for missing secrets (RUN THIS FIRST)
python config/manage_env.py audit

# Expected output:
# ✓ Fetched N Global Repository Secrets
# Scanning Environment: dev-backend...
#   ✅ All Clear (X env-specific secrets found)

# List secrets in GitHub
gh secret list --env dev-backend    # Environment-specific
gh secret list                       # Global repository secrets

# View current manifest
cat config/env.manifest.json | jq
```

---

## What This Directory Contains

```
config/
├── env.manifest.json          # ⭐ SINGLE SOURCE OF TRUTH (v3.3)
├── manage_env.py              # 🔍 Audit tool
└── README.md                  # This file
```

### The Manifest (`env.manifest.json`)
**Authority**: Defines ALL environment variables and GitHub Secret mappings for all 6 environments:
- `dev-backend`, `dev-frontend`
- `uat2-backend`, `uat2` (frontend)
- `prod2-backend`, `prod2-frontend`

### The Audit Tool (`manage_env.py`)
**Purpose**: Validates that required secrets exist in GitHub before deployment

**Usage**:
```bash
python config/manage_env.py audit
```

**What it checks**:
1. Fetches global repository secrets
2. For each environment:
   - Fetches environment-specific secrets
   - Combines with global secrets
   - Compares against manifest requirements
   - Reports missing secrets

---

## How to Use

### Before Making Changes
```bash
# Always audit first
python config/manage_env.py audit
```

### Adding a New Environment Variable

1. **Update manifest**:
   ```json
   "variables": {
     "application": {
       "NEW_VAR": {
         "ci_secret_pattern": "{PREFIX}_NEW_VAR",
         "description": "What this does"
       }
     }
   }
   ```

2. **Run audit** (will show missing):
   ```bash
   python config/manage_env.py audit
   ```

3. **Add secrets to GitHub**:
   ```bash
   gh secret set DEV_NEW_VAR --env dev-backend
   gh secret set UAT_NEW_VAR --env uat2-backend
   gh secret set PROD_NEW_VAR --env prod2-backend
   ```

4. **Verify**:
   ```bash
   python config/manage_env.py audit
   # Should show ✅ All Clear
   ```

### Setting Up Secrets for New Environment

1. **Create GitHub Environment** (repo Settings → Environments)
2. **Run audit to see requirements**:
   ```bash
   python config/manage_env.py audit
   ```
3. **Add missing secrets** shown in audit output
4. **Re-run audit** to verify

---

## Important Rules

### ✅ DO
- **Read the manifest first** before touching secrets
- **Run audit before deployments**
- **Use manifest-defined secret names** (no guessing)
- **Check both environment AND global secrets**
- **Consult `docs/CONFIGURATION_AND_SECRETS.md`** for details

### ❌ DON'T
- **Never guess secret names** ("it's probably DEV_*")
- **Never hardcode secrets** in code or docs
- **Never create `.env.example`** files with values
- **Never reference archived docs** for secret info
- **Never skip the audit** before deployment

---

## Legacy Exceptions (Documented in Manifest)

### UAT Frontend (`uat2`)
- Uses `STAGING_*` prefix (not `UAT_*`)
- GitHub Environment named `uat2` (not `uat2-frontend`)
- Reason: Legacy naming from pre-standardization

### Shared SSH Password
- UAT and Prod share `SSH_PASSWORD` (global secret)
- Dev uses separate `DEV_SSH_PASSWORD`
- Reason: Legacy infrastructure

**See manifest v3.3 for complete legacy mappings**

---

## Complete Documentation

**📖 START HERE**: [`docs/CONFIGURATION_AND_SECRETS.md`](../docs/CONFIGURATION_AND_SECRETS.md)

**Topics covered**:
- Complete environment list
- Secret management architecture
- Using the audit tool
- Legacy exceptions explained
- Developer workflows
- Troubleshooting guide

---

## Archived/Deprecated Files

**❌ DO NOT USE** (superseded by manifest system):
- `environments/` directory → Use manifest
- `shared/` directory → Use manifest  
- `.env.example` files → Use manifest
- `docs/GITHUB_SECRETS_CONFIGURATION.md` → Use `CONFIGURATION_AND_SECRETS.md`

**If documentation conflicts with the manifest, the manifest is always correct.**

---

**Last Updated**: December 10, 2025  
**Manifest Version**: 3.3  
**Authority**: `config/env.manifest.json`

---

## Directory Structure

```
config/
├── README.md                      # This file
├── env.manifest.json             # ⭐ SINGLE SOURCE OF TRUTH
├── manage_env.py                 # Environment generator & auditor
├── ENV_SETUP_GUIDE.md           # Complete usage guide
├── ENV_MANIFEST_README.md       # Manifest documentation
├── environments/                 # Legacy: Use manage_env.py instead
│   ├── development.env          # DEPRECATED - Use manifest
│   ├── staging.env             # DEPRECATED - Use manifest
│   └── production.env          # DEPRECATED - Use manifest
└── shared/                       # Legacy: Use manage_env.py instead
    ├── backend.env.template    # DEPRECATED - Use manifest
    └── frontend.env.template   # DEPRECATED - Use manifest
```

**⚠️ Deprecation Notice**: `environments/` and `shared/` directories are superseded by the unified manifest system. Use `manage_env.py` for all environment management.

---

## Why Unified Manifest?

### Problems Solved
✅ **No Configuration Drift**: Frontend and backend configs are guaranteed to be in sync  
✅ **Automated Validation**: `audit` command catches missing secrets before deployment  
✅ **Self-Documenting**: Every variable has a description and mapping  
✅ **Easy Onboarding**: One command generates correct .env files  
✅ **CI/CD Ready**: GitHub Actions workflows reference the same source  

### Old Way (Deprecated)
```bash
# ❌ Manual, error-prone, drift risk
cp config/environments/development.env backend/.env
cp config/shared/frontend.env.template frontend/.env.local
# Manually edit both files, hope you didn't make mistakes
```

### New Way (Recommended)
```bash
# ✅ Automated, validated, drift-free
python config/manage_env.py setup dev-backend
python config/manage_env.py setup dev-frontend
# Replace <SECRET_NAME> placeholders with actual values
```

### Environment Variables (Defined in Manifest)

#### Backend Variables (Category: infrastructure, application)
- **Infrastructure**: `BASTION_HOST`, `BASTION_USER`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- **Application**: `DATABASE_URL`, `SECRET_KEY`, `DJANGO_SETTINGS_MODULE`

#### Frontend Variables (Category: frontend_runtime)
- **Runtime**: `REACT_APP_API_BASE_URL`, `REACT_APP_ENVIRONMENT`, `REACT_APP_AI_ASSISTANT_ENABLED`

**Note**: All variables are documented in `env.manifest.json` with descriptions and secret mappings.

### Deployment Environments (Defined in Manifest)

#### Development (dev-backend, dev-frontend)
- **Backend**: `projectmeats.settings.development`
- **Frontend**: `https://dev.meatscentral.com/api/v1`
- **Secrets Prefix**: `DEV_*`

#### UAT/Staging (uat2-backend, uat2-frontend)
- **Backend**: `projectmeats.settings.staging`
- **Frontend**: `https://uat.meatscentral.com/api/v1`
- **Secrets Prefix**: `UAT_*`

#### Production (prod2-backend, prod2-frontend)
- **Backend**: `projectmeats.settings.production`
- **Frontend**: `https://meatscentral.com/api/v1`
- **Secrets Prefix**: `PROD_*`

**Note**: Environment definitions guarantee frontend API URLs match backend deployments.

### Best Practices

1. **Use the manifest system** - Run `manage_env.py` instead of manual .env editing
2. **Audit secrets regularly** - Run `python config/manage_env.py audit` before deployments
3. **Update manifest, not .env** - Edit `env.manifest.json`, then regenerate .env files
4. **Document changes** - Add descriptions to new variables in manifest
5. **Test generations** - Verify generated .env files match expectations
6. **Never commit secrets** - Generated .env files contain `<SECRET_NAME>` placeholders

### Security Guidelines

- Use different secrets for each environment
- Enable HTTPS and HSTS in production
- Restrict CORS origins to specific domains
- Use environment-specific database credentials
- Enable logging and monitoring in production
- Regular security audits and updates

### Troubleshooting

Common issues and solutions:
- **"Environment not found"**: Check `env.manifest.json` for available environments
- **"Secret not defined"**: Run `python config/manage_env.py audit` to see missing secrets
- **"Type mismatch"**: Ensure environment type matches target (backend vs frontend)
- **GitHub CLI errors**: Run `export GITHUB_TOKEN=...` if in Codespaces

## Migration from Old System

### Files to Delete (After Migration)
- ❌ `frontend/.env.example`
- ❌ `frontend/.env.production.example`
- ❌ `backend/.env.example`

### Replacement Commands
```bash
# Old: cp frontend/.env.example frontend/.env
# New:
python config/manage_env.py setup dev-frontend

# Old: cp backend/.env.example backend/.env
# New:
python config/manage_env.py setup dev-backend
```

## Additional Documentation

📚 **Primary Documentation**:
- **[ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md)** - Complete usage guide (START HERE)
- **[ENV_MANIFEST_README.md](ENV_MANIFEST_README.md)** - Manifest structure documentation
- **[ENVIRONMENT_UNIFICATION_COMPLETE.md](../ENVIRONMENT_UNIFICATION_COMPLETE.md)** - Implementation summary

📚 **Legacy Documentation** (deprecated):
- **[Environment Guide](../docs/ENVIRONMENT_GUIDE.md)** - Old environment configuration guide
- **[Documentation Hub](../docs/README.md)** - Central documentation navigation
- **[User Deployment Guide](../USER_DEPLOYMENT_GUIDE.md)** - Deployment instructions