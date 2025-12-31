# Configuration and Secrets Management
**Single Source of Truth for ProjectMeats Environments**

> **Authority**: This document describes the authoritative configuration system for ProjectMeats.  
> **Version**: Manifest v3.3 (December 2025)  
> **Status**: ✅ Active | All other environment/secret docs are archived

---

## Table of Contents
1. [Overview](#overview)
2. [The Authority: env.manifest.json](#the-authority-envmanifestjson)
3. [Supported Environments](#supported-environments)
4. [Secret Management](#secret-management)
5. [Using the Audit Tool](#using-the-audit-tool)
6. [Legacy Exceptions](#legacy-exceptions)
7. [Developer Workflow](#developer-workflow)
8. [Troubleshooting](#troubleshooting)

---

## Overview

ProjectMeats uses a **manifest-based configuration system** to eliminate secret drift and ensure consistency across all environments.

### Core Principles
1. **Single Source of Truth**: `config/env.manifest.json` defines ALL environment variables and their GitHub Secret mappings
2. **Environment-Aware**: Secrets can be scoped globally (repository-level) or per-environment (e.g., `dev-backend`, `uat2`)
3. **Audit-First**: Run `python config/manage_env.py audit` before any deployment or secret changes
4. **No Guessing**: Never assume secret names - always reference the manifest

### The Problem This Solves
**Before (❌ Secret Drift):**
- Secrets defined in multiple places (README, wiki, `.env.example`, CI/CD)
- Inconsistent naming between environments
- Deployment failures from missing/misnamed secrets
- No visibility into which secrets are required

**After (✅ Manifest System):**
- All secrets defined in one JSON file
- Automated validation via audit script
- Clear environment-specific mappings
- Self-documenting system

---

## The Authority: env.manifest.json

**Location**: [`config/env.manifest.json`](../config/env.manifest.json)

This file defines:
- **Environments**: All 6 deployment targets (dev, uat, prod × backend, frontend)
- **Variables**: Every required environment variable, grouped by category
- **Mappings**: How variables map to GitHub Secret names per environment
- **Patterns**: Reusable naming patterns (e.g., `{PREFIX}_DB_HOST`)

### File Structure
```json
{
  "project": "ProjectMeats",
  "version": "3.3",
  "environments": {
    "dev-backend": { "type": "backend", "prefix": "DEV" },
    "uat2": { "type": "frontend", "prefix": "STAGING" }
  },
  "variables": {
    "infrastructure": { /* SSH, host configs */ },
    "application": { /* DB, Django settings */ },
    "frontend_runtime": { /* React env vars */ }
  }
}
```

### Variable Categories

#### 1. Infrastructure Secrets
Used by **both** backend and frontend deployments for SSH access:
- `BASTION_HOST` - Droplet IP address
- `BASTION_USER` - SSH username
- `BASTION_SSH_PASSWORD` - SSH password (see [Legacy Exceptions](#legacy-exceptions))

#### 2. Application Secrets (Backend Only)
Used by Django/Python backend:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` - Database connection
- `DATABASE_URL` - Full PostgreSQL connection string
- `SECRET_KEY` - Django secret key
- `DJANGO_SETTINGS_MODULE` - Settings file path (derived from manifest)

#### 3. Frontend Runtime (Frontend Only)
Used by React at build time:
- `REACT_APP_API_BASE_URL` - Backend API endpoint
- `REACT_APP_ENVIRONMENT` - Environment name (dev, uat, production)
- `REACT_APP_AI_ASSISTANT_ENABLED` - Feature flag

---

## Supported Environments

The manifest defines **6 environments** matching our deployment architecture:

| Environment | Type | Prefix | GitHub Environment | Purpose |
|-------------|------|--------|-------------------|---------|
| `dev-backend` | backend | `DEV` | `dev-backend` | Development Django API |
| `dev-frontend` | frontend | `DEV` | `dev-frontend` | Development React UI |
| `uat2-backend` | backend | `UAT` | `uat2-backend` | Staging Django API |
| `uat2` | frontend | `STAGING` | `uat2` | Staging React UI ⚠️ |
| `prod2-backend` | backend | `PROD` | `prod2-backend` | Production Django API |
| `prod2-frontend` | frontend | `PROD` | `prod2-frontend` | Production React UI |

⚠️ **Note**: `uat2` uses `STAGING` prefix due to legacy naming (see [Legacy Exceptions](#legacy-exceptions))

---

## Secret Management

### GitHub Secrets Architecture

Secrets exist at **two levels**:

#### 1. Global Repository Secrets
- Available to **all** workflows and environments
- Use for: DO registry tokens, shared credentials
- Example: `DO_ACCESS_TOKEN`, `GITHUB_TOKEN`

#### 2. Environment Secrets
- Scoped to specific GitHub Environments (e.g., `dev-backend`, `uat2`)
- Use for: Environment-specific configs (DB credentials, SSH passwords)
- Example: `DEV_DB_HOST` in `dev-backend` environment

### Effective Secret Resolution
**The audit tool uses this logic:**
```
Available Secrets = Environment Secrets ∪ Global Repository Secrets
```

When a workflow runs in the `dev-backend` environment, it can access:
- All secrets defined in `dev-backend` environment
- All global repository secrets

### Secret Naming Patterns

#### Pattern Mapping
Most secrets follow a pattern defined in the manifest:
```json
"DB_HOST": {
  "ci_secret_pattern": "{PREFIX}_DB_HOST"
}
```

For `dev-backend` (prefix=DEV): → `DEV_DB_HOST`  
For `uat2-backend` (prefix=UAT): → `UAT_DB_HOST`

#### Explicit Mapping
Some secrets have explicit overrides:
```json
"BASTION_HOST": {
  "ci_secret_mapping": {
    "dev-backend": "DEV_HOST",
    "uat2": "STAGING_HOST"
  }
}
```

This handles legacy naming and exceptions.

---

## Using the Audit Tool

**Location**: [`config/manage_env.py`](../config/manage_env.py)

### Quick Reference
```bash
# Check all environments for missing secrets
python config/manage_env.py audit

# Expected output:
# ✓ Fetched N Global Repository Secrets
# Scanning Environment: dev-backend...
#   ✅ All Clear (X env-specific secrets found)
```

### What the Audit Checks
1. **Fetches Global Secrets**: Queries GitHub for repository-level secrets
2. **Per-Environment Validation**: For each environment:
   - Fetches environment-specific secrets
   - Combines with global secrets
   - Compares against manifest requirements
   - Reports missing secrets

### Interpreting Results

#### ✅ Success
```
Scanning Environment: dev-backend...
  ✅ All Clear (5 env-specific secrets found)
```
**Meaning**: All required secrets are present (either in environment or globally)

#### ❌ Missing Secrets
```
Scanning Environment: uat2...
  ❌ MISSING:
     - BASTION_HOST -> STAGING_HOST
     - BASTION_USER -> STAGING_USER
```
**Action Required**: Add the missing secrets to the `uat2` GitHub Environment

### Running Before Deployment
**ALWAYS** run the audit before:
- Deploying to a new environment
- Modifying secret names
- Adding new environment variables
- Troubleshooting deployment failures

---

## Legacy Exceptions

### UAT Frontend Naming (`uat2` vs `uat2-frontend`)

**Why it's different:**
- GitHub Environment is named `uat2` (not `uat2-frontend`)
- Uses `STAGING_*` prefix instead of `UAT_*`
- Predates our standardization effort

**Manifest Configuration:**
```json
"uat2": {
  "type": "frontend",
  "prefix": "STAGING",
  "url": "https://uat.meatscentral.com"
}
```

**Secret Mappings:**
- `BASTION_HOST` → `STAGING_HOST` (not `UAT_HOST`)
- `BASTION_USER` → `STAGING_USER` (not `UAT_USER`)

**Why We Keep It:**
- Avoids password resets on production infrastructure
- Maintains backward compatibility
- No operational impact

### Shared SSH Password (`SSH_PASSWORD`)

**Scope**: UAT and Production environments

**Configuration:**
```json
"BASTION_SSH_PASSWORD": {
  "ci_secret_mapping": {
    "uat2-backend": "SSH_PASSWORD",
    "uat2": "SSH_PASSWORD",
    "prod2-backend": "SSH_PASSWORD",
    "prod2-frontend": "SSH_PASSWORD"
  }
}
```

**Why it's shared:**
- Legacy infrastructure uses single SSH password for UAT/Prod droplets
- Stored as global repository secret
- Accessible to all UAT/Prod deployments

**Security Note**: Dev environments use separate `DEV_SSH_PASSWORD` for isolation.

### Production Frontend Naming

**Secret Prefix**: `PRODUCTION_*` (not `PROD_*`)

**Why:**
- Matches existing secrets in production environment
- Example: `PRODUCTION_HOST` instead of `PROD_HOST`

---

## Developer Workflow

### Adding a New Environment Variable

1. **Update the Manifest** (`config/env.manifest.json`)
   ```json
   "variables": {
     "application": {
       "NEW_VARIABLE": {
         "ci_secret_pattern": "{PREFIX}_NEW_VARIABLE",
         "description": "What this variable does",
         "required": true
       }
     }
   }
   ```

2. **Run Audit** (will show missing secrets)
   ```bash
   python config/manage_env.py audit
   ```

3. **Add Secrets to GitHub**
   ```bash
   # For each environment showing missing secrets:
   gh secret set DEV_NEW_VARIABLE --env dev-backend
   gh secret set UAT_NEW_VARIABLE --env uat2-backend
   gh secret set PROD_NEW_VARIABLE --env prod2-backend
   ```

4. **Verify**
   ```bash
   python config/manage_env.py audit
   # Should show ✅ All Clear
   ```

### Modifying an Existing Variable

1. **Check Current Mapping** in manifest
2. **Update Secret Values** in GitHub (don't rename unless necessary)
3. **Run Audit** to verify
4. **Update Manifest** if changing the mapping pattern

### Setting Up a New Environment

1. **Define in Manifest**
   ```json
   "environments": {
     "staging-backend": {
       "type": "backend",
       "prefix": "STAGING",
       "django_settings": "projectmeats.settings.staging"
     }
   }
   ```

2. **Create GitHub Environment**
   - Go to repo Settings → Environments
   - Create environment matching manifest name

3. **Add Required Secrets**
   - Run audit to see what's needed
   - Add secrets to the new environment

4. **Update Workflows**
   - Add environment to deployment workflows
   - Reference manifest for secret names

---

## Troubleshooting

### "Secret Not Found" in Workflow

**Symptom**: Workflow fails with "secret not found" or undefined variable

**Debug Steps:**
1. **Check the Manifest**: What secret name should it be?
   ```bash
   grep -A5 "VARIABLE_NAME" config/env.manifest.json
   ```

2. **Run Audit**: Is it actually missing?
   ```bash
   python config/manage_env.py audit
   ```

3. **Check GitHub**: Does the secret exist in the right place?
   ```bash
   # Check environment secrets
   gh secret list --env dev-backend
   
   # Check global secrets
   gh secret list
   ```

4. **Verify Mapping**: Does the workflow reference the correct name?
   - Check workflow file for `secrets.SECRET_NAME`
   - Compare against manifest's `ci_secret_mapping`

### Audit Shows Missing Secrets (But They Exist!)

**Possible Causes:**

1. **Wrong Environment Name**
   - Manifest: `uat2`
   - GitHub: `uat2-frontend`
   - **Fix**: Rename GitHub Environment or update manifest

2. **Wrong Secret Name**
   - Manifest expects: `STAGING_HOST`
   - GitHub has: `UAT_HOST`
   - **Fix**: Rename secret in GitHub or update manifest mapping

3. **Secret in Wrong Scope**
   - Secret is global (repo-level)
   - Manifest expects environment-specific
   - **Usually OK**: Audit should still pass (checks both)

### Deployment Works Locally but Fails in CI

**Check:**
1. **Environment Variables vs Secrets**
   - Locally: `.env` file with `KEY=value`
   - CI: GitHub Secrets with workflow mapping
   - **Ensure**: Secret names match manifest

2. **Environment Context**
   - Locally: May use dev settings
   - CI: Uses environment-specific settings
   - **Verify**: `DJANGO_SETTINGS_MODULE` is correct in manifest

### HTTP 400 Errors in Health Checks

**Symptom**: Frontend deployment fails at health check with HTTP 400

**Fix Applied**: Ensure curl uses HTTP/1.1:
```bash
curl --http1.1 -H "Host: localhost" http://localhost:80/
```

**If still failing**: Check nginx configuration in deployment script

---

## Related Documentation

- [Development Pipeline](DEVELOPMENT_PIPELINE.md) - CI/CD workflow overview
- [Environment Manifest README](../config/ENV_MANIFEST_README.md) - Technical details
- [Best Practices](../config/BEST_PRACTICES.md) - Configuration guidelines

## Archived Documentation

**These documents are NO LONGER AUTHORITATIVE:**
- `docs/GITHUB_SECRETS_CONFIGURATION.md` → Superseded by this doc
- `docs/archive/legacy_2025/environment-variables.md` → Superseded by manifest
- `archived/DEPLOYMENT_DB_SECRETS_SETUP.md` → Superseded by manifest

**Always consult the manifest first. If documentation conflicts with the manifest, the manifest is correct.**

---

## Quick Command Reference

```bash
# Audit all environments
python config/manage_env.py audit

# List secrets in an environment
gh secret list --env dev-backend

# List global secrets
gh secret list

# Set a secret (environment-scoped)
gh secret set SECRET_NAME --env dev-backend

# Set a secret (global)
gh secret set SECRET_NAME

# View manifest
cat config/env.manifest.json | jq

# Check manifest version
jq '.version' config/env.manifest.json
```

---

**Last Updated**: December 10, 2025  
**Manifest Version**: 3.3  
**Maintainer**: DevOps Team
