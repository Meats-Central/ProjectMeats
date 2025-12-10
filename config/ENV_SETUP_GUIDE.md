# Environment Setup Guide

## Single Source of Truth: env.manifest.json

All environment variables for **both backend and frontend** are defined in `config/env.manifest.json`. This eliminates drift between environments and provides a unified management interface.

## Quick Start

### Generate Backend .env
```bash
# Development
python config/manage_env.py setup dev-backend

# UAT
python config/manage_env.py setup uat2-backend

# Production
python config/manage_env.py setup prod2-backend
```

### Generate Frontend .env
```bash
# Development
python config/manage_env.py setup dev-frontend

# UAT
python config/manage_env.py setup uat2-frontend

# Production
python config/manage_env.py setup prod2-frontend
```

### Auto-detect Target
```bash
# Automatically detects backend vs frontend from environment name
python config/manage_env.py setup dev-backend   # Generates backend/.env
python config/manage_env.py setup dev-frontend  # Generates frontend/.env
```

### Custom Output Path
```bash
python config/manage_env.py setup dev-backend --output=/tmp/custom.env
```

## Audit GitHub Secrets

Verify all required secrets are defined in GitHub:

```bash
python config/manage_env.py audit
```

This will:
- ✅ Check all required secrets exist
- 🧟 Identify zombie secrets (defined but not in manifest)
- 📋 Report missing secrets per environment

## Manifest Structure

### Environments
Each environment is typed as either `backend` or `frontend`:

```json
{
  "environments": {
    "dev-backend": {
      "type": "backend",
      "prefix": "DEV",
      "django_settings": "projectmeats.settings.development"
    },
    "dev-frontend": {
      "type": "frontend",
      "prefix": "DEV",
      "url": "https://dev.meatscentral.com"
    }
  }
}
```

### Variables

#### Backend Variables
- **infrastructure**: BASTION_HOST, DB_HOST, DB_USER, DB_PASSWORD, etc.
- **application**: DATABASE_URL, SECRET_KEY, DJANGO_SETTINGS_MODULE

#### Frontend Variables
- **frontend_runtime**: REACT_APP_API_BASE_URL, REACT_APP_ENVIRONMENT, feature flags

### Secret Mapping Strategies

#### 1. Explicit Mapping
For secrets with non-standard names:

```json
"BASTION_SSH_PASSWORD": {
  "ci_secret_mapping": {
    "dev-backend": "DEV_SSH_PASSWORD",
    "uat2-backend": "SSH_PASSWORD",  // Shared UAT/Prod secret
    "prod2-backend": "SSH_PASSWORD"
  }
}
```

#### 2. Pattern Mapping
For predictable naming patterns:

```json
"DB_HOST": {
  "ci_secret_pattern": "{PREFIX}_DB_HOST"
}
// Resolves to: DEV_DB_HOST, UAT_DB_HOST, PROD_DB_HOST
```

#### 3. Direct Values
For frontend config that doesn't need GitHub secrets:

```json
"REACT_APP_API_BASE_URL": {
  "values": {
    "dev-frontend": "https://dev.meatscentral.com/api/v1",
    "uat2-frontend": "https://uat.meatscentral.com/api/v1",
    "prod2-frontend": "https://meatscentral.com/api/v1"
  }
}
```

#### 4. Default Values
For feature flags and non-sensitive config:

```json
"REACT_APP_AI_ASSISTANT_ENABLED": {
  "default": "true"
}
```

## Workflow Integration

GitHub Actions workflows automatically use secrets defined in the manifest:

```yaml
secrets:
  DATABASE_URL: ${{ secrets.DEV_DATABASE_URL }}
  DB_HOST: ${{ secrets.DEV_DB_HOST }}
  DB_USER: ${{ secrets.DEV_DB_USER }}
  DB_PASSWORD: ${{ secrets.DEV_DB_PASSWORD }}
  DB_NAME: ${{ secrets.DEV_DB_NAME }}
  SECRET_KEY: ${{ secrets.DEV_SECRET_KEY }}
```

The manifest ensures these secret names are consistent and auditable.

## Benefits

### 1. No More Drift
- Frontend and backend configs defined in one place
- API URLs, environments, and feature flags are synchronized
- Impossible to point UAT frontend to Prod backend by mistake

### 2. Self-Documenting
- Every variable has a description
- Secret mapping is explicit and auditable
- New team members can understand the full picture

### 3. Automated Validation
- `audit` command catches missing secrets before deployment
- CI/CD workflows fail fast if secrets are misconfigured
- No more "works on my machine" issues

### 4. Easy Onboarding
- Run `setup` command to generate correct .env files
- No need to track down example files or ask teammates
- Secrets are templated with clear placeholders

## Migration Notes

### Deprecated Files
The following files can now be **deleted**:
- ❌ `frontend/.env.example`
- ❌ `frontend/.env.production.example`
- ❌ `backend/.env.example`

These are replaced by:
- ✅ `config/env.manifest.json` (source of truth)
- ✅ `python config/manage_env.py setup <env>` (generator)

### For Developers
Instead of copying `.env.example`, run:

```bash
python config/manage_env.py setup dev-backend
python config/manage_env.py setup dev-frontend
```

Then replace `<SECRET_NAME>` placeholders with actual values from 1Password/team lead.

### For DevOps
Instead of manually updating GitHub secrets, use:

```bash
python config/manage_env.py audit
```

To verify all secrets are correctly configured.

## Troubleshooting

### "Environment not found"
- Check `config/env.manifest.json` for available environments
- Ensure you're using the correct environment name (e.g., `dev-backend` not `development`)

### "Secret not defined"
- Run `python config/manage_env.py audit` to see missing secrets
- Use `gh secret set <NAME> --body "<VALUE>"` to add missing secrets

### "Type mismatch"
- Backend environments must have `"type": "backend"`
- Frontend environments must have `"type": "frontend"`
- The `setup` command validates this automatically

## Advanced Usage

### Adding a New Secret
1. Add to `config/env.manifest.json`:
   ```json
   "NEW_SECRET": {
     "ci_secret_pattern": "{PREFIX}_NEW_SECRET",
     "description": "What this secret does"
   }
   ```

2. Set in GitHub:
   ```bash
   gh secret set DEV_NEW_SECRET --body "dev-value"
   gh secret set UAT_NEW_SECRET --body "uat-value"
   gh secret set PROD_NEW_SECRET --body "prod-value"
   ```

3. Verify:
   ```bash
   python config/manage_env.py audit
   ```

### Adding a Frontend Variable
1. Add to `frontend_runtime` category:
   ```json
   "REACT_APP_NEW_FEATURE": {
     "values": {
       "dev-frontend": "true",
       "uat2-frontend": "true",
       "prod2-frontend": "false"
     }
   }
   ```

2. Regenerate frontend .env:
   ```bash
   python config/manage_env.py setup dev-frontend
   ```

No GitHub secret needed if using direct values!

## Help

```bash
# Show available commands
python config/manage_env.py --help

# Show available environments
cat config/env.manifest.json | jq '.environments | keys'
```
