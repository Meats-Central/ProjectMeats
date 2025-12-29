# Environment Variable Migration Plan
**Status**: 🚧 Draft | **Date**: 2025-12-29 | **Manifest Version**: v3.3

---

## Executive Summary

This document provides a comprehensive plan to standardize environment variables across all ProjectMeats environments. The current audit shows **48 missing secrets** across 6 environments, with legacy naming inconsistencies that must be resolved.

**Authority**: All secret names are defined in [`config/env.manifest.json`](../config/env.manifest.json) (v3.3)

---

## Current State Analysis

### Audit Results (2025-12-29)

Running `python config/manage_env.py audit` shows:

```
❌ AUDIT FAILED
Total Missing Secrets: 48
```

**Environment Status:**
- ✅ **dev-backend**: 10 missing secrets
- ✅ **dev-frontend**: 6 missing secrets
- ⚠️ **uat2-backend**: 10 missing secrets
- ⚠️ **uat2** (frontend): 6 missing secrets
- ❌ **prod2-backend**: 10 missing secrets
- ❌ **prod2-frontend**: 6 missing secrets

### Key Issues Identified

1. **Legacy Naming Inconsistencies**
   - UAT frontend uses `STAGING_*` prefix (legacy) instead of `UAT_*`
   - Production uses `prod2-*` environment names instead of `production-*`
   - SSH_PASSWORD shared globally instead of per-environment for UAT/prod

2. **Missing GitHub Environment Secrets**
   - All environments missing infrastructure secrets (HOST, USER, SSH_PASSWORD)
   - All backend environments missing database credentials
   - All frontend environments missing React runtime variables

3. **Workflow References**
   - Workflows still reference `STAGING_HOST`, `STAGING_USER` (legacy)
   - Environment names use `uat2`, `prod2` instead of `uat`, `production`

---

## Migration Strategy

### Phase 1: Create Missing Secrets (UAT & Production)

**Priority**: HIGH | **Risk**: Medium | **Effort**: 2-3 hours

Create all missing secrets in GitHub to match the development standard.

#### 1.1 UAT Backend Secrets (`uat2-backend` environment)

Navigate to: `https://github.com/Meats-Central/ProjectMeats/settings/environments`

**Infrastructure (SSH Access):**
```bash
# Create environment: uat2-backend
UAT_HOST=<droplet-ip>
UAT_USER=<ssh-username>
SSH_PASSWORD=<shared-ssh-password>  # Legacy exception - shared across UAT/prod
```

**Database (PostgreSQL):**
```bash
UAT_DB_HOST=<private-db-host>
UAT_DB_PORT=5432
UAT_DB_USER=<db-username>
UAT_DB_PASSWORD=<db-password>
UAT_DB_NAME=<db-name>
UAT_DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/<db>
```

**Application:**
```bash
UAT_SECRET_KEY=<django-secret-key>
# DJANGO_SETTINGS_MODULE derived from manifest: projectmeats.settings.staging
```

#### 1.2 UAT Frontend Secrets (`uat2` environment)

**Infrastructure (SSH Access):**
```bash
# Create environment: uat2
STAGING_HOST=<droplet-ip>  # Legacy name - DO NOT CHANGE YET
STAGING_USER=<ssh-username>  # Legacy name - DO NOT CHANGE YET
SSH_PASSWORD=<shared-ssh-password>  # Legacy exception
```

**Frontend Runtime:**
```bash
REACT_APP_API_BASE_URL=https://api-uat.meatscentral.com
REACT_APP_ENVIRONMENT=uat
REACT_APP_AI_ASSISTANT_ENABLED=true
```

#### 1.3 Production Backend Secrets (`prod2-backend` environment)

**Infrastructure (SSH Access):**
```bash
# Create environment: prod2-backend
PROD_HOST=<droplet-ip>
PROD_USER=<ssh-username>
SSH_PASSWORD=<shared-ssh-password>  # Legacy exception - shared across UAT/prod
```

**Database (PostgreSQL):**
```bash
PROD_DB_HOST=<private-db-host>
PROD_DB_PORT=5432
PROD_DB_USER=<db-username>
PROD_DB_PASSWORD=<db-password>
PROD_DB_NAME=<db-name>
PROD_DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/<db>
```

**Application:**
```bash
PROD_SECRET_KEY=<django-secret-key>
# DJANGO_SETTINGS_MODULE derived from manifest: projectmeats.settings.production
```

#### 1.4 Production Frontend Secrets (`prod2-frontend` environment)

**Infrastructure (SSH Access):**
```bash
# Create environment: prod2-frontend
PRODUCTION_HOST=<droplet-ip>
PRODUCTION_USER=<ssh-username>
SSH_PASSWORD=<shared-ssh-password>  # Legacy exception
```

**Frontend Runtime:**
```bash
REACT_APP_API_BASE_URL=https://api.meatscentral.com
REACT_APP_ENVIRONMENT=production
REACT_APP_AI_ASSISTANT_ENABLED=true
```

#### 1.5 Development Secrets (Complete the Set)

**Dev Backend (`dev-backend` environment):**
```bash
# Infrastructure
DEV_HOST=<droplet-ip>
DEV_USER=<ssh-username>
DEV_SSH_PASSWORD=<ssh-password>

# Database
DEV_DB_HOST=<private-db-host>
DEV_DB_PORT=5432
DEV_DB_USER=<db-username>
DEV_DB_PASSWORD=<db-password>
DEV_DB_NAME=<db-name>
DEV_DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/<db>

# Application
DEV_SECRET_KEY=<django-secret-key>
# DJANGO_SETTINGS_MODULE derived from manifest: projectmeats.settings.development
```

**Dev Frontend (`dev-frontend` environment):**
```bash
# Infrastructure (same as backend)
DEV_HOST=<droplet-ip>
DEV_USER=<ssh-username>
DEV_SSH_PASSWORD=<ssh-password>

# Frontend Runtime
REACT_APP_API_BASE_URL=https://dev.meatscentral.com
REACT_APP_ENVIRONMENT=development
REACT_APP_AI_ASSISTANT_ENABLED=true
```

---

### Phase 2: Legacy Cleanup (Future - DO NOT DO NOW)

**Priority**: LOW | **Risk**: HIGH | **Effort**: 4-6 hours

⚠️ **WARNING**: This phase requires careful coordination and should be done AFTER Phase 1 is stable.

#### 2.1 Rename Environment Names

**Current → Target:**
- `uat2-backend` → `uat-backend`
- `uat2` (frontend) → `uat-frontend`
- `prod2-backend` → `production-backend`
- `prod2-frontend` → `production-frontend`

**Impact:**
- All workflows must be updated (`.github/workflows/*.yml`)
- Manifest must be updated (`config/env.manifest.json`)
- Documentation must be updated

#### 2.2 Standardize UAT Frontend Prefix

**Current:** `STAGING_HOST`, `STAGING_USER`  
**Target:** `UAT_HOST`, `UAT_USER`

**Files to Update:**
- `.github/workflows/99-ops-management-command.yml` (lines 46-47)
- `config/env.manifest.json` (uat2 frontend mapping)
- Any deployment scripts referencing STAGING_*

**Migration Steps:**
1. Create new secrets with UAT_* names
2. Update workflows to reference UAT_* names
3. Test UAT deployments
4. Delete old STAGING_* secrets

#### 2.3 Per-Environment SSH Passwords (Optional)

**Current:** `SSH_PASSWORD` shared globally  
**Target:** `DEV_SSH_PASSWORD`, `UAT_SSH_PASSWORD`, `PROD_SSH_PASSWORD`

**Reason for Current Design**: Simplifies management when all environments use same droplet password.  
**Recommendation**: Keep shared password unless security requirements change.

---

## Standard Variable Checklist

### Backend Environment Requirements

Every backend environment (`dev-backend`, `uat2-backend`, `prod2-backend`) **MUST** have:

#### Infrastructure Secrets
- [ ] `{PREFIX}_HOST` - Droplet IP address
- [ ] `{PREFIX}_USER` - SSH username
- [ ] `SSH_PASSWORD` or `{PREFIX}_SSH_PASSWORD` - SSH authentication

#### Database Secrets
- [ ] `{PREFIX}_DB_ENGINE` - Database engine (typically `django.db.backends.postgresql`)
- [ ] `{PREFIX}_DB_NAME` - Database name
- [ ] `{PREFIX}_DB_USER` - Database username
- [ ] `{PREFIX}_DB_PASSWORD` - Database password
- [ ] `{PREFIX}_DB_HOST` - Database host (private IP)
- [ ] `{PREFIX}_DB_PORT` - Database port (default: 5432)
- [ ] `{PREFIX}_DATABASE_URL` - Full connection string (for production settings)

#### Application Secrets
- [ ] `{PREFIX}_SECRET_KEY` - Django secret key (50+ characters)
- [ ] `DJANGO_SETTINGS_MODULE` - Derived from manifest (e.g., `projectmeats.settings.production`)

#### Optional/Derived
- [ ] `DJANGO_ALLOWED_HOSTS` - Comma-separated list (typically set in settings file)
- [ ] `DB_ENGINE` - Often defaults to `django.db.backends.postgresql`

**Prefix Mapping:**
- Development: `DEV_*`
- UAT: `UAT_*`
- Production: `PROD_*`

---

### Frontend Environment Requirements

Every frontend environment (`dev-frontend`, `uat2`, `prod2-frontend`) **MUST** have:

#### Infrastructure Secrets (Same as Backend)
- [ ] `{PREFIX}_HOST` - Droplet IP address
- [ ] `{PREFIX}_USER` - SSH username
- [ ] `SSH_PASSWORD` or `{PREFIX}_SSH_PASSWORD` - SSH authentication

#### Frontend Runtime Variables
- [ ] `REACT_APP_API_BASE_URL` - Backend API endpoint URL
- [ ] `REACT_APP_ENVIRONMENT` - Environment name (development, uat, production)
- [ ] `REACT_APP_AI_ASSISTANT_ENABLED` - Feature flag (true/false)

**Note**: Frontend secrets are used at **build time** and injected into the Docker image.

---

## Verification Steps

### Step 1: Run Audit After Creating Secrets

```bash
cd /workspaces/ProjectMeats
python config/manage_env.py audit
```

Expected output:
```
✅ AUDIT PASSED
All required secrets are configured correctly.
```

### Step 2: Test Each Environment

**Development:**
```bash
# Trigger dev deployment
git push origin development
```

**UAT:**
```bash
# After dev passes, merge to UAT
gh pr create --base uat --head development
```

**Production:**
```bash
# After UAT passes, merge to main
gh pr create --base main --head uat
```

### Step 3: Validate Deployments

Check each deployment:
1. ✅ Workflow completes successfully
2. ✅ Migrations run without errors
3. ✅ Backend health check passes (HTTP 200)
4. ✅ Frontend loads correctly
5. ✅ API connectivity works

---

## Legacy Variables to DELETE (Future Phase)

⚠️ **DO NOT DELETE THESE YET** - They are still referenced in workflows.

### After Phase 2.2 Completion:
- [ ] `STAGING_HOST` (replace with `UAT_HOST`)
- [ ] `STAGING_USER` (replace with `UAT_USER`)
- [ ] `STAGING_DB_URL` (archived workflow reference only)

### Archived References (Safe to Ignore):
These appear in `/archived` workflows and should NOT be deleted:
- `STAGING_DB_URL` (in `21-db-backup-restore-do.yml`)

---

## Migration Timeline

### Week 1: Immediate Actions (Phase 1)
- [ ] Day 1-2: Create all missing dev-backend secrets
- [ ] Day 2-3: Create all missing dev-frontend secrets
- [ ] Day 3-4: Create all missing uat2-backend secrets
- [ ] Day 4-5: Create all missing uat2 frontend secrets
- [ ] Day 5-6: Create all missing prod2-backend secrets
- [ ] Day 6-7: Create all missing prod2-frontend secrets

### Week 2: Validation
- [ ] Day 8-9: Run audit, verify all environments pass
- [ ] Day 9-10: Test development deployment end-to-end
- [ ] Day 10-11: Test UAT deployment end-to-end
- [ ] Day 11-12: Test production deployment end-to-end
- [ ] Day 12-14: Monitor production, fix any issues

### Future: Phase 2 (After Stable Operation)
- [ ] Month 2: Plan Phase 2 migration (rename environments)
- [ ] Month 2: Update all workflows to use new names
- [ ] Month 2: Rename GitHub environments
- [ ] Month 2: Update manifest and documentation
- [ ] Month 2: Delete legacy STAGING_* secrets

---

## Risk Assessment

### High Risk Items
1. **Production Database Secrets**: Incorrect `PROD_DATABASE_URL` can cause data loss
   - Mitigation: Test in dev/UAT first, verify connection strings
2. **SSH Password Sharing**: `SSH_PASSWORD` used across UAT/prod
   - Mitigation: Document in manifest as "Legacy Exception"
3. **Environment Renaming (Phase 2)**: Breaking change to all workflows
   - Mitigation: Defer to future, keep current names for now

### Medium Risk Items
1. **Missing Secrets Blocking Deployments**: No immediate impact if not deploying
   - Mitigation: Create secrets before next deployment cycle
2. **Secret Naming Inconsistencies**: STAGING_* vs UAT_*
   - Mitigation: Document as known issue, address in Phase 2

### Low Risk Items
1. **Documentation Updates**: Does not affect runtime
2. **Audit Failures**: Informational only, does not block local development

---

## Rollback Plan

If deployments fail after adding secrets:

### Immediate Rollback
1. Check GitHub Actions logs for specific error
2. Verify secret names match manifest exactly
3. Test secret values locally (non-sensitive test DB)

### Secret-Specific Issues
```bash
# Check if secret is set in environment
gh secret list --env dev-backend

# Update specific secret
gh secret set DEV_DB_PASSWORD --env dev-backend

# Re-run failed workflow
gh run rerun <run-id>
```

### Nuclear Option
If all else fails:
1. Revert to previous working commit
2. Review manifest vs GitHub secrets mismatch
3. Create missing secrets one-by-one with audit verification

---

## Success Criteria

✅ **Phase 1 Complete When:**
- [ ] Audit passes: `python config/manage_env.py audit` returns 0 missing secrets
- [ ] All 6 environments have complete secret sets
- [ ] Development deployment works end-to-end
- [ ] UAT deployment works end-to-end
- [ ] Production deployment works end-to-end

✅ **Phase 2 Complete When (Future):**
- [ ] Environment names standardized (no `uat2`, `prod2` suffixes)
- [ ] UAT frontend uses `UAT_*` prefix (no `STAGING_*`)
- [ ] All workflows updated and tested
- [ ] Documentation reflects new naming

---

## Appendix: Quick Reference Commands

### Audit Environment Secrets
```bash
# Full audit
python config/manage_env.py audit

# Check specific environment
gh secret list --env dev-backend
```

### Create Secrets via CLI
```bash
# Set environment secret
gh secret set DEV_DB_PASSWORD --env dev-backend

# Set from file (for multi-line secrets like SSH keys)
gh secret set DEV_SSH_PRIVATE_KEY --env dev-backend < ~/.ssh/id_rsa
```

### View Manifest
```bash
# Pretty-print manifest
cat config/env.manifest.json | jq

# List all environment names
cat config/env.manifest.json | jq -r '.environments | keys[]'

# Show secrets for specific environment
cat config/env.manifest.json | jq '.variables.infrastructure.BASTION_HOST.ci_secret_mapping'
```

### Test Database Connection
```bash
# Test connection string locally (replace with actual values)
psql "postgresql://user:pass@host:5432/dbname" -c "SELECT version();"
```

---

## Contact & Support

- **Manifest Authority**: `config/env.manifest.json` (v3.3)
- **Documentation**: `docs/CONFIGURATION_AND_SECRETS.md`
- **Audit Script**: `config/manage_env.py`
- **GitHub Secrets**: https://github.com/Meats-Central/ProjectMeats/settings/secrets/actions

**Last Updated**: 2025-12-29  
**Next Review**: After Phase 1 completion (estimated 2 weeks)
