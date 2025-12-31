# Deployment Fix - Next Steps & Monitoring Guide

**Date:** 2025-12-01  
**PR:** #808 - https://github.com/Meats-Central/ProjectMeats/pull/808  
**Status:** ✅ PR Created & Checks Passing

---

## Current Status

### ✅ Completed
- [x] Root cause analysis (django-tenants command mismatch)
- [x] Fixed production workflow (13-prod-deployment.yml)
- [x] Fixed UAT workflow (12-uat-deployment.yml)
- [x] Created comprehensive documentation
- [x] Committed and pushed changes (branch: uat-merge-fix)
- [x] Created PR #808 to development
- [x] All CI checks passing

### 🔄 In Progress
- [ ] PR review and approval
- [ ] Merge to development
- [ ] Automated PR to UAT
- [ ] UAT deployment validation
- [ ] Automated PR to main
- [ ] Production deployment validation

---

## Next Steps

### Step 1: PR Review (CURRENT)
**Action:** Wait for PR review and approval  
**Who:** Repository maintainers/reviewers  
**Expected Time:** 1-24 hours  

**What Reviewers Should Check:**
- Migration command changes are correct
- No breaking changes to workflow logic
- Documentation is clear and accurate

**PR Link:** https://github.com/Meats-Central/ProjectMeats/pull/808

### Step 2: Merge to Development
**Action:** Merge PR #808 after approval  
**Trigger:** Manual merge by reviewer  

**Expected Behavior:**
- No deployment workflows triggered (development branch doesn't auto-deploy)
- Code merged into development branch
- Branch `uat-merge-fix` can be deleted

### Step 3: Automatic PR to UAT
**Action:** Monitor for automatic PR creation  
**Workflow:** `.github/workflows/promote-dev-to-uat.yml`  
**Expected Time:** ~1-2 minutes after merge to development  

**What to Check:**
```bash
# Monitor for new PR to UAT
gh pr list --base uat --state open
```

### Step 4: UAT Deployment Validation
**Action:** Review and merge UAT PR  
**Workflow:** `.github/workflows/12-uat-deployment.yml`  

**Validation Checklist:**
```bash
# 1. Check workflow status
gh run list --workflow=12-uat-deployment.yml --limit 1

# 2. Monitor deployment logs
gh run view <run-id> --log

# 3. Verify health check (from deployment logs)
# Look for: "✓ Backend health check passed (HTTP 200)"
```

**Key Validation Points:**
- ✅ Migration step completes: `python manage.py migrate --noinput`
- ✅ No "command not found" errors
- ✅ Health check returns HTTP 200 (not 500)
- ✅ All 20 health check attempts not needed (succeeds on first)

### Step 5: Automatic PR to Production
**Action:** After UAT validation, monitor for PR to main  
**Workflow:** `.github/workflows/promote-uat-to-main.yml`  

**What to Check:**
```bash
# Monitor for new PR to main
gh pr list --base main --state open
```

### Step 6: Production Deployment Validation
**Action:** Review and merge Production PR  
**Workflow:** `.github/workflows/13-prod-deployment.yml`  

**Validation Checklist:**
- ✅ Same validation as UAT
- ✅ Monitor production health endpoint
- ✅ Verify no service disruption

---

## Monitoring Commands

### Check PR Status
```bash
# View PR details
gh pr view 808

# Check PR checks
gh pr checks 808

# View PR diff
gh pr diff 808
```

### Monitor Workflow Runs
```bash
# List recent workflow runs
gh run list --limit 10

# View specific workflow
gh run view <run-id>

# View workflow logs
gh run view <run-id> --log

# Watch workflow in real-time
gh run watch <run-id>
```

### Check Deployment Status
```bash
# UAT workflow runs
gh run list --workflow=12-uat-deployment.yml --limit 5

# Production workflow runs
gh run list --workflow=13-prod-deployment.yml --limit 5

# Promotion workflows
gh run list --workflow=promote-dev-to-uat.yml --limit 5
gh run list --workflow=promote-uat-to-main.yml --limit 5
```

---

## Rollback Plan

### If UAT Deployment Fails
```bash
# 1. Identify the issue from logs
gh run view <failed-run-id> --log

# 2. Revert the UAT merge
gh pr create --base uat --head main --title "Revert: deployment fix"

# 3. Or cherry-pick previous working commit
git checkout uat
git revert <commit-hash>
git push origin uat
```

### If Production Deployment Fails
```bash
# 1. Immediately revert main branch
gh pr create --base main --head <previous-working-commit> \
  --title "Revert: deployment fix"

# 2. Monitor rollback deployment
gh run watch

# 3. Investigate and fix in new PR
```

---

## Success Indicators

### UAT Deployment Success
```
✅ Workflow status: completed with success
✅ Migration logs show: "python manage.py migrate --noinput"
✅ Health check logs show: "✓ Backend health check passed (HTTP 200)"
✅ No error messages in deployment logs
✅ UAT environment accessible
```

### Production Deployment Success
```
✅ Same as UAT success indicators
✅ Production health endpoint returns 200
✅ No alerts or error notifications
✅ Application functions normally
```

---

## Troubleshooting

### Issue: Health Check Still Returns 500

**Possible Causes:**
1. Migrations didn't run properly
2. Database connection issues
3. Environment variables missing

**Debug Steps:**
```bash
# 1. Check migration logs
gh run view <run-id> --log | grep -A 20 "Running database migrations"

# 2. Check health check logs
gh run view <run-id> --log | grep -A 20 "Health check"

# 3. Check for database errors
gh run view <run-id> --log | grep -i "error\|failed\|exception"
```

### Issue: Migration Command Fails

**Possible Causes:**
1. Database not ready
2. Connection string incorrect
3. Migration conflicts

**Debug Steps:**
```bash
# Check database readiness logs
gh run view <run-id> --log | grep -A 10 "Waiting for PostgreSQL"

# Check migration execution
gh run view <run-id> --log | grep -A 30 "migrate --noinput"
```

### Issue: Tenant Setup Fails

**Possible Causes:**
1. create_super_tenant command not found
2. Database schema issues

**Note:** This fix only addresses migration commands. Tenant setup commands are still referenced but don't affect the primary issue (health check 500).

---

## Follow-Up Tasks (Optional)

### 1. Update Test Backend Steps
**Priority:** Low  
**Files:**
- `.github/workflows/13-prod-deployment.yml` (lines 162-240)
- `.github/workflows/12-uat-deployment.yml` (lines 167-245)

**Change:** Replace complex shell tenant setup with:
```yaml
- name: Setup test tenants
  run: |
    python manage.py create_super_tenant --verbosity=1
    python manage.py create_guest_tenant --verbosity=1
```

### 2. Create Architecture Documentation
**Priority:** Medium  
**File:** `MULTI_TENANCY_ARCHITECTURE.md`

**Content:**
- Comprehensive guide to custom shared-schema multi-tenancy
- Model relationships (Tenant, TenantUser, TenantDomain)
- Migration patterns
- Middleware behavior
- Common pitfalls

### 3. Update Copilot Instructions
**Priority:** Medium  
**File:** `.github/copilot-instructions.md`

**Add:**
- Multi-tenancy architecture critical section
- Command dos and don'ts
- Health check bypass explanation

---

## Timeline Expectations

| Phase | Expected Duration | Status |
|-------|------------------|--------|
| PR Review | 1-24 hours | ⏳ Waiting |
| Merge to Development | Immediate | ⏸️ Not started |
| Auto PR to UAT | 1-2 minutes | ⏸️ Not started |
| UAT Deployment | 5-10 minutes | ⏸️ Not started |
| UAT Validation | 1-2 hours | ⏸️ Not started |
| Auto PR to Production | 1-2 minutes | ⏸️ Not started |
| Production Deployment | 5-10 minutes | ⏸️ Not started |
| **Total Estimated Time** | **2-28 hours** | |

---

## Contact & Escalation

### If Issues Arise
1. **Check Logs:** Use monitoring commands above
2. **Review Documentation:** DEPLOYMENT_MULTI_TENANCY_FIX.md
3. **Revert if Needed:** Follow rollback plan
4. **Create Issue:** Document problem for future reference

### Success Confirmation
Once production deployment succeeds:
1. ✅ Update PR #808 with success confirmation
2. ✅ Close any related issues
3. ✅ Archive documentation in appropriate folder
4. ✅ Update CHANGELOG.md

---

**Last Updated:** 2025-12-01  
**Maintained By:** Development Team  
**PR:** https://github.com/Meats-Central/ProjectMeats/pull/808
