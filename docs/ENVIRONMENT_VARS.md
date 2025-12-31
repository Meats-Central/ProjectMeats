# Environment Variables Reference

**Source of Truth**: `config/env.manifest.json` (v3.3)

This document lists all environment variables required by ProjectMeats across different environments and deployment contexts.

## Table of Contents
- [Infrastructure Variables](#infrastructure-variables)
- [Application Variables (Backend)](#application-variables-backend)
- [Frontend Runtime Variables](#frontend-runtime-variables)
- [Environment Mapping](#environment-mapping)
- [Secret Naming Conventions](#secret-naming-conventions)
- [Usage Examples](#usage-examples)
- [Credential Drift Prevention](#credential-drift-prevention)

---

## Infrastructure Variables

These variables are required for deployment infrastructure (SSH access, server configuration).

| Variable | Description | Required By | Dev Secret | UAT Secret | Prod Secret |
|----------|-------------|-------------|------------|------------|-------------|
| `BASTION_HOST` | Droplet IP address | All environments | `DEV_HOST` | `STAGING_HOST` | `PRODUCTION_HOST` |
| `BASTION_USER` | SSH Username | All environments | `DEV_USER` | `STAGING_USER` | `PRODUCTION_USER` |
| `BASTION_SSH_PASSWORD` | SSH Password (Legacy Shared) | All environments | `DEV_SSH_PASSWORD` | `SSH_PASSWORD` | `SSH_PASSWORD` |

### Infrastructure Notes

- **Legacy SSH Password Sharing**: UAT and Production share `SSH_PASSWORD` for backward compatibility
- **Security Recommendation**: Migrate to SSH key-based authentication to eliminate password sharing

---

## Application Variables (Backend)

These variables configure the Django application and database connections.

| Variable | Description | Required By | Pattern/Mapping | Default | Required |
|----------|-------------|-------------|-----------------|---------|----------|
| `DB_HOST` | Private DB Host | Backend environments | `{PREFIX}_DB_HOST` | N/A | ✅ Yes |
| `DB_PORT` | Database Port | Backend environments | `{PREFIX}_DB_PORT` | `5432` | ⚠️ Optional |
| `DB_USER` | DB Username | Backend environments | `{PREFIX}_DB_USER` | N/A | ✅ Yes |
| `DB_PASSWORD` | DB Password | Backend environments | `{PREFIX}_DB_PASSWORD` | N/A | ✅ Yes |
| `DB_NAME` | Database Name | Backend environments | `{PREFIX}_DB_NAME` | N/A | ✅ Yes |
| `DATABASE_URL` | PostgreSQL Connection String | Backend environments | See mapping below | N/A | ⚠️ Optional |
| `SECRET_KEY` | Django Secret Key | Backend environments | `{PREFIX}_SECRET_KEY` | N/A | ✅ Yes |
| `DJANGO_SETTINGS_MODULE` | Django Settings Module | Backend environments | Source: environment_config | N/A | ✅ Yes |

### Database Configuration Details

**Option 1: DATABASE_URL (Recommended for Production)**
- Single connection string format: `postgresql://user:password@host:port/dbname`
- Environment-specific mappings:
  - Dev: `DEV_DATABASE_URL`
  - UAT: `UAT_DATABASE_URL`
  - Prod: `PROD_DATABASE_URL`

**Option 2: Individual DB_* Variables**
- Use when DATABASE_URL is not provided
- Requires: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- Pattern: `{PREFIX}_DB_*` (e.g., `DEV_DB_HOST`, `PROD_DB_PASSWORD`)

**Settings Resolution**: Django production settings parse `DATABASE_URL` first, then fall back to individual `DB_*` variables.

### Django Superuser Variables (Management Commands)

These variables are used by management commands like `init_tenant`, `createsuperuser`, etc.:

| Variable | Description | Used By | Required |
|----------|-------------|---------|----------|
| `DJANGO_SUPERUSER_USERNAME` | Initial superuser username | `init_tenant`, `createsuperuser` | ⚠️ Optional |
| `DJANGO_SUPERUSER_EMAIL` | Initial superuser email | `init_tenant`, `createsuperuser` | ⚠️ Optional |
| `DJANGO_SUPERUSER_PASSWORD` | Initial superuser password | `init_tenant`, `createsuperuser` | ⚠️ Optional |

**Note**: These are automatically injected into management commands via the Ops workflow (`99-ops-management-command.yml`).

---

## Frontend Runtime Variables

These variables are injected into the React application at runtime.

| Variable | Description | Required By | Pattern | Example Value |
|----------|-------------|-------------|---------|---------------|
| `REACT_APP_API_BASE_URL` | Backend API base URL | Frontend environments | `REACT_APP_API_BASE_URL` | `https://dev-backend.meatscentral.com` |
| `REACT_APP_ENVIRONMENT` | Current environment name | Frontend environments | `REACT_APP_ENVIRONMENT` | `development` |
| `REACT_APP_AI_ASSISTANT_ENABLED` | Enable/disable AI assistant | Frontend environments | `REACT_APP_AI_ASSISTANT_ENABLED` | `true` or `false` |

### Frontend Variable Injection

Frontend variables are:
1. Set in GitHub Secrets (no prefix needed, use exact variable name)
2. Injected via `env-config.js` at container runtime
3. Accessed via `window.ENV` object in React code

**Example Access Pattern**:
```javascript
const API_URL = window.ENV?.API_BASE_URL || 'http://localhost:8000';
```

---

## Environment Mapping

ProjectMeats uses 6 GitHub environment contexts for secret scoping:

| Environment | Type | Prefix | Django Settings | URL |
|-------------|------|--------|-----------------|-----|
| `dev-backend` | backend | `DEV` | `projectmeats.settings.development` | N/A |
| `dev-frontend` | frontend | `DEV` | N/A | `https://dev.meatscentral.com` |
| `uat2-backend` | backend | `UAT` | `projectmeats.settings.staging` | N/A |
| `uat2` | frontend | `STAGING` | N/A | `https://uat.meatscentral.com` |
| `prod2-backend` | backend | `PROD` | `projectmeats.settings.production` | N/A |
| `prod2-frontend` | frontend | `PROD` | N/A | `https://meatscentral.com` |

### Environment-Aware Secret Resolution

Secrets are resolved using this priority:

1. **Environment-Scoped Secrets** (highest priority)
   - Set at: `Settings > Environments > {env-name} > Add secret`
   - Accessible only to workflows using that environment

2. **Global Repository Secrets** (fallback)
   - Set at: `Settings > Secrets and variables > Actions > New repository secret`
   - Accessible to all workflows

3. **Explicit Mapping** (overrides pattern)
   - Defined in `ci_secret_mapping` in manifest
   - Used for legacy secret names

4. **Pattern-Based** (default)
   - Uses `ci_secret_pattern` with `{PREFIX}` substitution
   - Example: `{PREFIX}_DB_HOST` → `DEV_DB_HOST` for dev

---

## Secret Naming Conventions

### Standard Patterns

```
{PREFIX}_{VARIABLE_NAME}
```

Examples:
- Development: `DEV_DB_HOST`, `DEV_SECRET_KEY`
- UAT/Staging: `UAT_DB_HOST`, `UAT_SECRET_KEY`
- Production: `PROD_DB_HOST`, `PROD_SECRET_KEY`

### Legacy Exceptions

Some secrets use non-standard names for backward compatibility:

| Standard Pattern | Actual Secret | Reason |
|------------------|---------------|--------|
| `UAT_HOST` | `STAGING_HOST` | Legacy naming |
| `UAT_USER` | `STAGING_USER` | Legacy naming |
| `UAT_SSH_PASSWORD` | `SSH_PASSWORD` | Shared across UAT/Prod |
| `PROD_SSH_PASSWORD` | `SSH_PASSWORD` | Shared across UAT/Prod |

---

## Usage Examples

### Auditing Secrets

Check if all required secrets are configured:

```bash
python config/manage_env.py audit
```

**Sample Output**:
```
Starting Environment-Aware Audit (Manifest v3.3)...

✓ Fetched 0 Global Repository Secrets

Environment: dev-backend
  Type: backend
  Prefix: DEV
  Checking categories: infrastructure, application

  ❌ MISSING SECRETS (10):
     • BASTION_HOST → DEV_HOST
       Category: infrastructure
     • DB_HOST → DEV_DB_HOST
       Category: application
```

### Setting Secrets via GitHub CLI

```bash
# Environment-scoped secret (recommended)
gh secret set DEV_DB_HOST --env dev-backend --body "10.x.x.x"

# Global repository secret (use sparingly)
gh secret set SSH_PASSWORD --body "your_password"

# List secrets in an environment
gh secret list --env dev-backend

# List global secrets
gh secret list
```

---

## Credential Drift Prevention

### Best Practices

1. **Single Source of Truth**
   - All variable definitions live in `config/env.manifest.json`
   - Never hardcode secret names in workflows or code
   - Update manifest FIRST, then add secrets

2. **Audit Before Deploy**
   - Run `python config/manage_env.py audit` before deployment
   - Gate deployments on audit success (CI fails if secrets missing)

3. **Environment Scoping**
   - Prefer environment-scoped secrets over global
   - Reduces blast radius of credential leaks

### Common Pitfalls

❌ **DON'T**: Hardcode secret names in workflows
```yaml
env:
  DB_HOST: ${{ secrets.PROD_DB_HOST }}  # Hardcoded!
```

✅ **DO**: Reference manifest and use environment scoping
```yaml
environment: prod2-backend
env:
  DB_HOST: ${{ secrets.PROD_DB_HOST }}  # Scoped to environment
```

---

## Troubleshooting

### Audit Failures

If `python config/manage_env.py audit` fails:

1. Check the error output for missing secret names
2. Verify environment scope (global vs. environment-specific)
3. Add missing secrets via GitHub UI or CLI
4. Re-run audit to confirm

### Workflow Failures

If deployment workflows fail with "secret not found":

1. Check if secret exists: `gh secret list --env {env-name}`
2. Verify secret name matches manifest mapping
3. Ensure workflow uses correct environment context
4. Check for typos in secret references

---

**Last Updated**: 2025-12-29  
**Manifest Version**: `config/env.manifest.json` v3.3  
**Audit Command**: `python config/manage_env.py audit`  
**GitHub Secrets**: https://github.com/Meats-Central/ProjectMeats/settings/secrets/actions
