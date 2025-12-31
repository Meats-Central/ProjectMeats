# GitHub Secrets Migration Guide

## Overview
This guide documents the standardization of secret names for environment-agnostic workflow design.

## Changes Made

### 1. Reusable Workflow (`reusable-deploy.yml`)
**Updated `secrets:` section to accept standardized names:**

```yaml
secrets:
  DO_ACCESS_TOKEN          # DigitalOcean registry access
  SSH_HOST                 # Deployment target host
  SSH_USER                 # SSH username
  SSH_PASSWORD             # Backend deployment (password auth)
  SSH_KEY                  # Frontend deployment (key auth)
  DB_HOST                  # Database host for SSH tunnel
  DB_PORT                  # Database port (optional, defaults to 5432)
  DB_NAME                  # Database name
  DB_USER                  # Database username
  DB_PASSWORD              # Database password
  DJANGO_SECRET_KEY        # Django secret key
  DJANGO_SETTINGS_MODULE   # Django settings module
  REACT_APP_API_BASE_URL   # Frontend runtime config
  BACKEND_HOST             # Backend IP for nginx proxy
```

### 2. Main Pipeline (`main-pipeline.yml`)
**Updated Development deployment to map environment-specific secrets:**

```yaml
secrets:
  DO_ACCESS_TOKEN: ${{ secrets.DO_ACCESS_TOKEN }}
  SSH_HOST: ${{ secrets.DEV_HOST }}
  SSH_USER: ${{ secrets.DEV_USER }}
  SSH_PASSWORD: ${{ secrets.DEV_SSH_PASSWORD }}
  SSH_KEY: ${{ secrets.DEV_FRONTEND_SSH_KEY }}
  DB_HOST: ${{ secrets.DEV_DB_HOST }}
  DB_PORT: ${{ secrets.DEV_DB_PORT }}
  DB_NAME: ${{ secrets.DEV_DB_NAME }}
  DB_USER: ${{ secrets.DEV_DB_USER }}
  DB_PASSWORD: ${{ secrets.DEV_DB_PASSWORD }}
  DJANGO_SECRET_KEY: ${{ secrets.DEV_SECRET_KEY }}
  DJANGO_SETTINGS_MODULE: ${{ secrets.DEV_DJANGO_SETTINGS_MODULE }}
  REACT_APP_API_BASE_URL: ${{ secrets.DEV_API_BASE_URL }}
  BACKEND_HOST: ${{ secrets.DEV_BACKEND_IP }}
```

## Required Actions for UAT and Production

Since UAT and Production use `secrets: inherit`, you must configure **environment-scoped secrets** in GitHub with the **standardized names** (not environment-prefixed).

### Configure GitHub Environments

#### For `uat-backend` Environment:
```bash
gh secret set SSH_HOST --env uat-backend --body "$UAT_HOST"
gh secret set SSH_USER --env uat-backend --body "$UAT_USER"
gh secret set SSH_PASSWORD --env uat-backend --body "$UAT_SSH_PASSWORD"
gh secret set DB_HOST --env uat-backend --body "$UAT_DB_HOST"
gh secret set DB_PORT --env uat-backend --body "5432"
gh secret set DB_NAME --env uat-backend --body "$UAT_DB_NAME"
gh secret set DB_USER --env uat-backend --body "$UAT_DB_USER"
gh secret set DB_PASSWORD --env uat-backend --body "$UAT_DB_PASSWORD"
gh secret set DJANGO_SECRET_KEY --env uat-backend --body "$UAT_SECRET_KEY"
gh secret set DJANGO_SETTINGS_MODULE --env uat-backend --body "projectmeats.settings.production"
gh secret set BACKEND_HOST --env uat-backend --body "$UAT_BACKEND_IP"
```

#### For `uat-frontend` Environment:
```bash
gh secret set SSH_HOST --env uat-frontend --body "$UAT_HOST"
gh secret set SSH_USER --env uat-frontend --body "$UAT_USER"
gh secret set SSH_KEY --env uat-frontend --body "$UAT_FRONTEND_SSH_KEY"
gh secret set REACT_APP_API_BASE_URL --env uat-frontend --body "https://uat.meatscentral.com"
gh secret set BACKEND_HOST --env uat-frontend --body "$UAT_BACKEND_IP"
```

#### For `production-backend` Environment:
```bash
gh secret set SSH_HOST --env production-backend --body "$PROD_HOST"
gh secret set SSH_USER --env production-backend --body "$PROD_USER"
gh secret set SSH_PASSWORD --env production-backend --body "$PROD_SSH_PASSWORD"
gh secret set DB_HOST --env production-backend --body "$PROD_DB_HOST"
gh secret set DB_PORT --env production-backend --body "5432"
gh secret set DB_NAME --env production-backend --body "$PROD_DB_NAME"
gh secret set DB_USER --env production-backend --body "$PROD_DB_USER"
gh secret set DB_PASSWORD --env production-backend --body "$PROD_DB_PASSWORD"
gh secret set DJANGO_SECRET_KEY --env production-backend --body "$PROD_SECRET_KEY"
gh secret set DJANGO_SETTINGS_MODULE --env production-backend --body "projectmeats.settings.production"
gh secret set BACKEND_HOST --env production-backend --body "$PROD_BACKEND_IP"
```

#### For `production-frontend` Environment:
```bash
gh secret set SSH_HOST --env production-frontend --body "$PROD_HOST"
gh secret set SSH_USER --env production-frontend --body "$PROD_USER"
gh secret set SSH_KEY --env production-frontend --body "$PROD_FRONTEND_SSH_KEY"
gh secret set REACT_APP_API_BASE_URL --env production-frontend --body "https://meatscentral.com"
gh secret set BACKEND_HOST --env production-frontend --body "$PROD_BACKEND_IP"
```

## Verification

### Check Environment Secrets:
```bash
gh secret list --env uat-backend
gh secret list --env uat-frontend
gh secret list --env production-backend
gh secret list --env production-frontend
```

### Expected Output (Example for uat-backend):
```
SSH_HOST                 Updated 2024-12-30
SSH_USER                 Updated 2024-12-30
SSH_PASSWORD             Updated 2024-12-30
DB_HOST                  Updated 2024-12-30
DB_PORT                  Updated 2024-12-30
DB_NAME                  Updated 2024-12-30
DB_USER                  Updated 2024-12-30
DB_PASSWORD              Updated 2024-12-30
DJANGO_SECRET_KEY        Updated 2024-12-30
DJANGO_SETTINGS_MODULE   Updated 2024-12-30
BACKEND_HOST             Updated 2024-12-30
```

## Benefits of Standardization

1. **Environment Agnostic**: Reusable workflow doesn't need to know environment prefixes
2. **Consistency**: Same secret names across all environments
3. **Maintainability**: Easier to understand and update
4. **Scalability**: Easy to add new environments without workflow changes
5. **Security**: Environment-scoped secrets prevent cross-environment access

## Removed Secrets (No Longer Needed)

The following environment-prefixed secrets from `main-pipeline.yml` were removed:
- `FRONTEND_SSH_KEY` → Now `SSH_KEY`
- `BACKEND_SSH_PASSWORD` → Now `SSH_PASSWORD`
- `FRONTEND_HOST` → Removed (not used in reusable workflow)
- `FRONTEND_USER` → Removed (SSH_USER is shared)
- `BACKEND_HOST` → Now `SSH_HOST` (for deployment) and `BACKEND_HOST` (for nginx)
- `BACKEND_USER` → Removed (SSH_USER is shared)
- `BACKEND_IP` → Now `BACKEND_HOST`
- `DATABASE_URL` → Removed (constructed from DB_* secrets)
- `SECRET_KEY` → Now `DJANGO_SECRET_KEY`

## Testing

After configuring secrets, test with:
```bash
# Trigger manual deployment to UAT
gh workflow run main-pipeline.yml --ref uat -f environment=uat

# Monitor workflow
gh run watch
```

## Troubleshooting

### "Secret not found" error:
- Verify secret name matches standardized list
- Check environment name (e.g., `uat-backend` vs `uat`)
- Confirm secret is set in correct environment scope

### SSH authentication failures:
- Backend uses `SSH_PASSWORD` (password auth)
- Frontend uses `SSH_KEY` (key auth)
- Ensure correct auth method for each component

### Database connection issues:
- Verify all DB_* secrets are set
- Check DB_PORT defaults to 5432 if not specified
- Confirm SSH tunnel can reach DB_HOST
