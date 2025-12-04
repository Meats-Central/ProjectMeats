# PR Review Guide - Phase 2 Environment Remediation

**PR Branch**: `feature/phase2-environment-remediation` → `development`  
**PR URL**: https://github.com/Meats-Central/ProjectMeats/compare/development...feature/phase2-environment-remediation?expand=1  
**Reviewer**: Lead Developer  
**Date**: 2025-12-04

## Quick Summary

This PR implements comprehensive environment standardization to eliminate manual interventions and ensure proper multi-tenant migration patterns across all environments.

## Critical Review Focus Areas

### 1. ⚠️ Environment Name Scoping

**Files to Review**:
- `.github/workflows/11-dev-deployment.yml` (line ~236+)
- `.github/workflows/12-uat-deployment.yml` (line ~279+)
- `.github/workflows/13-prod-deployment.yml` (line ~273+)

**What to Check**:
```yaml
# Development workflow
environment: dev-backend  # ✅ Correct
env:
  DATABASE_URL: ${{ secrets.DEV_DATABASE_URL }}    # ✅ Verify this secret exists
  SECRET_KEY: ${{ secrets.DEV_SECRET_KEY }}        # ✅ Verify this secret exists
  DJANGO_SETTINGS_MODULE: ${{ secrets.DEV_DJANGO_SETTINGS_MODULE }}  # ✅ Verify

# UAT workflow
environment: uat2-backend  # ✅ Correct (matches existing)
env:
  DATABASE_URL: ${{ secrets.UAT_DATABASE_URL }}    # ✅ Verify this secret exists
  SECRET_KEY: ${{ secrets.UAT_SECRET_KEY }}        # ✅ Verify this secret exists
  DJANGO_SETTINGS_MODULE: ${{ secrets.UAT_DJANGO_SETTINGS_MODULE }}  # ✅ Verify

# Production workflow
environment: production  # ⚠️ CHANGED from prod2-backend - VERIFY THIS IS CORRECT
env:
  DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}   # ✅ Verify this secret exists
  SECRET_KEY: ${{ secrets.PROD_SECRET_KEY }}       # ✅ Verify this secret exists
  DJANGO_SETTINGS_MODULE: ${{ secrets.PROD_DJANGO_SETTINGS_MODULE }}  # ✅ Verify
```

**Action Required**: Verify all GitHub environment names and secrets exist before merging.

### 2. ⚠️ Multi-Tenancy Migration Logic

**Files to Review**:
- All three deployment workflows (search for "run-migrations" job)

**What to Check**:

The migration pattern must follow this exact order:
```bash
# Step 1: Shared schema FIRST (creates Tenant, TenantUser tables in public schema)
python manage.py migrate_schemas --shared --noinput --fake-initial

# Step 2: Create super tenant (depends on Tenant table from step 1)
python manage.py create_super_tenant --no-input

# Step 3: Tenant schemas LAST (creates tables in each tenant's schema)
python manage.py migrate_schemas --tenant --noinput --fake-initial
```

**Critical Flags**:
- `--shared` = public schema only (Django core + Tenant model)
- `--tenant` = all tenant schemas (business entities)
- `--fake-initial` = idempotency (safe to re-run)
- `--noinput` = no prompts (CI-safe)

**Why This Matters**: Running `--tenant` before `--shared` will fail because Tenant table won't exist. Missing `--fake-initial` will cause duplicate table errors on re-runs.

### 3. ✅ Job Dependencies

**What to Check**:
```yaml
# In all deployment workflows:

deploy-frontend:
  needs: [run-migrations, test-frontend]  # ✅ Must wait for migrations

deploy-backend:
  needs: [run-migrations]  # ✅ Must wait for migrations (or also test-backend for prod)
```

**Verify**: Deployments are blocked if migrations fail.

### 4. ✅ Codespace Auto-Detection

**File**: `backend/projectmeats/settings/development.py`

**What to Check**:
```python
import os  # ✅ Added at top

# In the DB configuration block:
if os.getenv('CODESPACES') == 'true':
    DB_ENGINE = 'django_tenants.postgresql_backend'  # ✅ Correct backend

if DB_ENGINE in ("django.db.backends.postgresql", "django_tenants.postgresql_backend"):
    DATABASES = {
        "default": {
            "ENGINE": DB_ENGINE,  # ✅ Uses auto-detected value
            ...
```

**Why This Matters**: Eliminates manual `settings.py` edits for Codespace users.

### 5. ✅ GHCR Integration

**File**: `.github/workflows/ci.yml` (NEW FILE)

**What to Check**:
```yaml
on:
  push:
    branches: [development]  # ✅ Only builds on development
    paths:
      - '.devcontainer/**'
      - 'backend/requirements.txt'
      - 'frontend/package*.json'
```

**Why This Matters**: Ensures consistent dev environment images across all developers.

## Testing Plan Before Merge

### Pre-Merge Verification

1. **Verify Secrets Exist**:
   - Go to: Settings → Environments → [env-name] → Secrets
   - Confirm all `*_DATABASE_URL`, `*_SECRET_KEY`, `*_DJANGO_SETTINGS_MODULE` exist
   - Production environment should have protection rules enabled

2. **Dry Run (Optional but Recommended)**:
   - Manually trigger dev deployment workflow
   - Watch `run-migrations` job logs
   - Verify 3-step execution: shared → super tenant → tenant

3. **Codespace Test (Optional)**:
   - Create new Codespace from this branch
   - Verify automatic tenant backend detection
   - Check that migrations run without errors

### Post-Merge Monitoring

1. **First Dev Deployment**:
   - Watch for `run-migrations` job execution
   - Verify idempotency (can re-run safely)
   - Check for proper schema isolation in logs

2. **UAT Promotion**:
   - After testing in dev, promote to UAT
   - Verify UAT migrations with `UAT_*` secrets

3. **Production Rollout**:
   - After UAT validation, promote to main
   - Verify production migrations with `PROD_*` secrets

## Approval Checklist

- [ ] All secret variable names verified (`DEV_*`, `UAT_*`, `PROD_*`)
- [ ] Environment names verified (`dev-backend`, `uat2-backend`, `production`)
- [ ] Migration order correct (shared → super tenant → tenant)
- [ ] `--fake-initial` flag present in all `migrate_schemas` calls
- [ ] Job dependencies correct (deployments wait for migrations)
- [ ] Codespace auto-detection logic reviewed
- [ ] GHCR workflow triggers reviewed
- [ ] Documentation updates reviewed

## Rollback Plan

If issues arise after merge:

```bash
# Revert all commits
git revert 877091c  # Documentation
git revert b5842cf  # Copilot setup
git revert 9575560  # DevContainer GHCR
git revert ef826f7  # Codespace auto-detection
git revert c83ed4f  # GHCR workflow
git revert e2cc18d  # Migrations + ROADMAP

# Or revert entire range
git revert HEAD~6..HEAD
```

## Questions for Reviewer

1. **Production Environment Name**: Changed from `prod2-backend` to `production` - is this the correct environment name in GitHub settings?

2. **Secret Naming Convention**: All secrets now use `ENV_` prefix (e.g., `DEV_DATABASE_URL`, `UAT_DATABASE_URL`, `PROD_DATABASE_URL`) - confirm these exist in respective environments.

3. **Migration Timing**: Migrations now run in CI before deployment. Is there any reason they should run on the deployment server instead?

## Benefits After Merge

✅ Developers can use Codespaces without manual configuration  
✅ All developers pull same prebuilt dev environment image  
✅ Migrations are idempotent and follow proper multi-tenant pattern  
✅ Migration failures block deployment (fail-fast)  
✅ Better visibility into migration execution via CI logs  

## Risk Assessment

**Overall Risk**: Low  
**Reason**: Changes are additive and backward compatible

**Highest Risk Area**: Production environment name and secret variables  
**Mitigation**: Verify before merging, test in dev/UAT first

---

**Prepared by**: GitHub Copilot CLI  
**Date**: 2025-12-04  
**Status**: Ready for Review
