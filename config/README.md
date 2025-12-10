# ProjectMeats Environment Configuration

## 🎯 Single Source of Truth: env.manifest.json

**All environment variables for backend and frontend are defined in `env.manifest.json`.**

### Quick Start (New Unified System)

```bash
# Generate backend .env
python config/manage_env.py setup dev-backend
python config/manage_env.py setup uat2-backend
python config/manage_env.py setup prod2-backend

# Generate frontend .env
python config/manage_env.py setup dev-frontend
python config/manage_env.py setup uat2-frontend
python config/manage_env.py setup prod2-frontend

# Audit GitHub secrets
python config/manage_env.py audit
```

📖 **See [ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md) for complete documentation.**

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