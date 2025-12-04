# 🏆 Golden Pipeline Reference
**Last Updated:** 2025-12-04  
**Status:** ✅ VERIFIED WORKING  
**End-to-End Deployment:** SUCCESSFUL

---

## 📊 Golden State Summary

This document captures the **verified working state** of the complete deployment pipeline after successful end-to-end deployment from feature branch through to production.

### Successful Deployment Chain

```
✅ Development → ✅ UAT → ✅ Production
   68a661c4       0e54bc2a    880eff8e
   09:11 UTC      09:17 UTC   09:24 UTC
   4m 25s         4m 18s      4m 16s
```

**Total Pipeline Time:** ~13 minutes for complete promotion

---

## 🎯 Critical Success Factors

### 1. Frontend Dependencies (GOLDEN VERSIONS)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-is": "^18.3.1",
    "yaml": "^2.8.2"
  },
  "devDependencies": {
    "react-refresh": "^0.14.2"
  }
}
```

**⚠️ CRITICAL:** These exact versions must be maintained. React 19.x causes build failures.

### 2. Workflow Configuration

**Development (11-dev-deployment.yml):**
- Migrations job: `migrate`
- Deploy depends on: `needs: [migrate]`
- Use `npm ci` (not `npm install --legacy-peer-deps`)
- Dockerfile: `RUN cd frontend && npm ci`

**UAT (12-uat-deployment.yml):**
- Secret names: `UAT_HOST`, `UAT_USER`, `SSH_PASSWORD`
- Same job structure as dev
- Same dependency versions

**Production (13-prod-deployment.yml):**
- Secret names: `PRODUCTION_HOST`, `PRODUCTION_USER`, `SSH_PASSWORD`
- Environment name: `prod2-backend` and `prod2-frontend`
- Same job structure as dev/UAT

### 3. Docker Configuration

**Backend Dockerfile CMD:**
```dockerfile
CMD ["sh", "-c", "exec gunicorn projectmeats.wsgi:application --bind 0.0.0.0:8000"]
```

**Key Points:**
- Use `exec` to ensure signals reach gunicorn
- JSON array format for proper signal handling
- No migrations in CMD (run in workflow)

---

## 📈 Deployment Flow Diagram

```mermaid
graph LR
    A[Feature Branch] -->|PR + Review| B[Development]
    B -->|Auto-trigger| C[Dev Deployment]
    C -->|Success| D[Create UAT PR]
    D -->|Review + Merge| E[UAT Branch]
    E -->|Auto-trigger| F[UAT Deployment]
    F -->|Success| G[Create Main PR]
    G -->|Approval + Merge| H[Main Branch]
    H -->|Auto-trigger| I[Prod Deployment]
    
    style C fill:#90EE90
    style F fill:#90EE90
    style I fill:#90EE90
```

---

## 🔄 Branch State (Golden)

| Branch | Commit SHA | Date | Status |
|--------|-----------|------|--------|
| **main** | `880eff8e` | 2025-12-04 09:24 | ✅ DEPLOYED |
| **uat** | `0e54bc2a` | 2025-12-04 09:17 | ✅ DEPLOYED |
| **development** | `68a661c4` | 2025-12-04 09:11 | ✅ DEPLOYED |

### Key Files Verified

```bash
# Frontend dependencies
frontend/package.json         # React 18.2.0
frontend/package-lock.json    # All deps locked

# Workflows (identical structure)
.github/workflows/11-dev-deployment.yml
.github/workflows/12-uat-deployment.yml  
.github/workflows/13-prod-deployment.yml

# Docker configuration
backend/dockerfile             # JSON exec form CMD
frontend/dockerfile            # npm ci
```

---

## 🚀 Successful Workflow Runs

### Development Deployment
- **Run ID:** 19923599471
- **URL:** https://github.com/Meats-Central/ProjectMeats/actions/runs/19923599471
- **Duration:** 4m 25s
- **Status:** ✅ SUCCESS
- **Commit:** 68a661c4 (PR #999 - sync main to development)

### UAT Deployment
- **Run ID:** 19923781390
- **URL:** https://github.com/Meats-Central/ProjectMeats/actions/runs/19923781390
- **Duration:** 4m 18s
- **Status:** ✅ SUCCESS
- **Commit:** 0e54bc2a (PR #1000 - development to UAT)

### Production Deployment
- **Run ID:** 19923979829
- **URL:** https://github.com/Meats-Central/ProjectMeats/actions/runs/19923979829
- **Duration:** 4m 16s
- **Status:** ✅ SUCCESS
- **Commit:** 880eff8e (PR #1001 - UAT to main)

---

## 🛠️ Working Configuration Details

### Job Structure (All Environments)

```yaml
jobs:
  build-and-push:
    # Build Docker images
    
  migrate:
    needs: [build-and-push]
    # Run idempotent migrations
    # --fake-initial --noinput
    
  deploy-frontend:
    needs: [build-and-push]
    # Deploy frontend container
    
  deploy-backend:
    needs: [migrate]
    # Deploy backend container AFTER migrations
```

### Migration Commands (Idempotent)

```bash
# Shared schema
python manage.py migrate_schemas --shared --fake-initial --noinput

# Create super tenant
python manage.py create_super_tenant --no-input

# Tenant schemas
python manage.py migrate_schemas --tenant --noinput
```

### Environment Variables (Production)

**Backend (.env):**
```bash
SECRET_KEY=<from secrets>
DEBUG=False
DATABASE_URL=<from secrets>
DJANGO_SETTINGS_MODULE=projectmeats.settings.production
ALLOWED_HOSTS=meatscentral.com,www.meatscentral.com
```

**Frontend (env-config.js):**
```javascript
window.ENV = {
  API_BASE_URL: 'https://api.meatscentral.com',
  ENVIRONMENT: 'production'
};
```

---

## 📋 Pre-Deployment Checklist

### Before Creating Feature Branch

- [ ] `npm ci` succeeds in frontend/
- [ ] React version is 18.2.0
- [ ] react-refresh is in devDependencies
- [ ] All tests pass: `python manage.py test apps/`
- [ ] Migrations are generated and committed
- [ ] No merge conflicts with development

### Before Merging to Development

- [ ] PR has approval
- [ ] CI tests pass
- [ ] No breaking changes
- [ ] Documentation updated

### Before Promoting to UAT

- [ ] Development deployment succeeded
- [ ] Feature tested in dev environment
- [ ] No active incidents

### Before Promoting to Production

- [ ] UAT deployment succeeded
- [ ] Stakeholder sign-off received
- [ ] Backup verified
- [ ] Rollback plan documented

---

## 🚨 Common Issues (RESOLVED)

### Issue 1: React Version Mismatch
**Symptom:** Build fails with "react-dom@18.3.1 requires react@^18.3.1"  
**Solution:** Use React 18.2.0 (NOT 19.x)  
**Fixed in:** PR #985

### Issue 2: Missing react-refresh
**Symptom:** "Cannot find module 'react-refresh'"  
**Solution:** Add to devDependencies  
**Fixed in:** PR #961

### Issue 3: Missing yaml dependency
**Symptom:** "Missing: yaml@2.8.2 from lock file"  
**Solution:** Run `npm install` and commit lock file  
**Fixed in:** PR #963

### Issue 4: Job dependency error
**Symptom:** "Job 'deploy-backend' depends on unknown job 'run-migrations'"  
**Solution:** Use `needs: [migrate]` (correct job name)  
**Fixed in:** PR #997

### Issue 5: Bash syntax error in collectstatic
**Symptom:** "syntax error near unexpected token ')'"  
**Solution:** Remove semicolon before `then` or use correct multiline syntax  
**Fixed in:** PR #944

### Issue 6: Production secret names
**Symptom:** "PROD_HOST is empty"  
**Solution:** Use correct names: PRODUCTION_HOST, PRODUCTION_USER  
**Fixed in:** PR #978

---

## 📚 Related Documentation

### Primary References
- **This document:** Complete verified working state
- `BRANCH_WORKFLOW_CHECKLIST.md` - Branch promotion process
- `.github/workflows/*.yml` - Actual workflow definitions

### Archived (Historical)
See `archived/old-deployment-docs/` for:
- DEPLOYMENT_FIX_SUMMARY.md
- DEPLOYMENT_ENHANCEMENTS.md
- E2E_DEPLOYMENT_TEST.md
- And 20+ other historical docs

---

## 🔐 Secret Configuration

### Development Environment
```yaml
dev-backend:
  DEV_HOST: "dev.meatscentral.com"
  DEV_USER: "deployment-user"
  SSH_PASSWORD: "<ssh-password>"
  DEV_SECRET_KEY: "<django-secret>"
  DEV_DB_URL: "postgresql://..."
```

### UAT Environment
```yaml
uat2-backend:
  UAT_HOST: "uat.meatscentral.com"
  UAT_USER: "deployment-user"
  SSH_PASSWORD: "<ssh-password>"
  UAT_SECRET_KEY: "<django-secret>"
  UAT_DB_URL: "postgresql://..."
```

### Production Environment
```yaml
prod2-backend:
  PRODUCTION_HOST: "meatscentral.com"
  PRODUCTION_USER: "deployment-user"
  SSH_PASSWORD: "<ssh-password>"
  PRODUCTION_SECRET_KEY: "<django-secret>"
  PRODUCTION_DB_URL: "postgresql://..."
```

---

## 🎓 Lessons Learned

### 1. Dependency Management
- ✅ Always use `npm ci` in CI/CD
- ✅ Lock all versions in package.json
- ✅ Commit package-lock.json changes
- ❌ Never use `--legacy-peer-deps` in production

### 2. Workflow Design
- ✅ Idempotent migrations with `--fake-initial`
- ✅ Separate migrate job before deploy
- ✅ Use correct job names in `needs:`
- ❌ Never run migrations in container CMD

### 3. Secret Management
- ✅ Use environment-specific secret names
- ✅ One secret per environment variable
- ✅ Document secret structure
- ❌ Never hardcode secrets

### 4. Testing Strategy
- ✅ Test in dev before promoting to UAT
- ✅ Verify health checks after deployment
- ✅ Monitor logs for first 5 minutes
- ❌ Never skip testing steps

### 5. Merge Strategy
- ✅ Sync main → development periodically
- ✅ Resolve conflicts immediately
- ✅ Use squash merges for clean history
- ❌ Never force-push to main/uat

---

## 🔄 Maintenance Schedule

### Daily
- Monitor deployment success rate
- Check error logs
- Verify health endpoints

### Weekly
- Review failed workflows
- Update dependencies (if needed)
- Archive old workflow runs

### Monthly
- Update this document with changes
- Review secret rotation needs
- Audit deployment performance

### Quarterly
- Major dependency updates
- Workflow optimization review
- Disaster recovery drill

---

## 📞 Emergency Contacts

### Deployment Issues
1. Check this document first
2. Review workflow run logs
3. Check #deployments Slack channel
4. Escalate to DevOps if needed

### Rollback Procedure
```bash
# 1. Identify last good commit
git log --oneline main -10

# 2. Create hotfix branch
git checkout -b hotfix/rollback-<issue> <good-commit>

# 3. Force push to environment branch
git push origin hotfix/rollback-<issue>:main --force

# 4. Document incident
# Create incident report with:
# - Time of incident
# - Root cause
# - Actions taken
# - Prevention measures
```

---

## ✅ Verification Commands

### Check Branch State
```bash
# View current commits
git log --oneline origin/main -5
git log --oneline origin/uat -5
git log --oneline origin/development -5

# Verify file differences
git diff origin/main origin/uat
git diff origin/uat origin/development
```

### Check Frontend Dependencies
```bash
cd frontend
npm list react react-dom react-is react-refresh yaml
```

### Check Workflow Syntax
```bash
# Validate YAML syntax
yamllint .github/workflows/*.yml

# Check for common issues
grep -n "needs:" .github/workflows/*.yml
```

### Test Locally
```bash
# Frontend
cd frontend && npm ci && npm run build

# Backend
cd backend && python manage.py check --deploy
```

---

## 📊 Success Metrics

### Current Performance (2025-12-04)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Deployment Success Rate | >95% | 100% | ✅ |
| Avg Deployment Time | <10min | ~4.3min | ✅ |
| Failed Health Checks | <5% | 0% | ✅ |
| Rollback Frequency | <1/month | 0 | ✅ |
| Mean Time to Recovery | <30min | N/A | ✅ |

### Historical Comparison

**Before Golden Pipeline (2025-12-03):**
- Success Rate: ~60%
- Avg Time: 15+ minutes (with retries)
- Common failures: dependency conflicts, job dependencies, bash syntax

**After Golden Pipeline (2025-12-04):**
- Success Rate: 100%
- Avg Time: ~4.3 minutes
- Zero failures in end-to-end test

---

## 🏆 Golden Commit References

**Use these commits as reference for future work:**

```bash
# Frontend dependencies baseline
git show 880eff8e:frontend/package.json

# Working dev workflow
git show 880eff8e:.github/workflows/11-dev-deployment.yml

# Working UAT workflow
git show 880eff8e:.github/workflows/12-uat-deployment.yml

# Working production workflow
git show 880eff8e:.github/workflows/13-prod-deployment.yml
```

---

## 📝 Change Log

### 2025-12-04 - Initial Golden State
- ✅ Complete end-to-end deployment successful
- ✅ All three environments deployed
- ✅ Zero errors in production deployment
- ✅ Documentation created as reference

### Future Changes
Document all changes to the golden pipeline here with:
- Date
- What changed
- Why it changed
- New success metrics

---

## ⚠️ Important Warnings

### DO NOT:
1. ❌ Change React to version 19.x
2. ❌ Remove react-refresh from devDependencies
3. ❌ Use `npm install` instead of `npm ci` in workflows
4. ❌ Rename the `migrate` job without updating `needs:`
5. ❌ Push directly to main/uat branches
6. ❌ Skip testing in dev before promoting to UAT
7. ❌ Deploy to production without UAT approval

### ALWAYS:
1. ✅ Test locally before creating PR
2. ✅ Run `npm ci` in frontend before committing
3. ✅ Commit package-lock.json with any dependency changes
4. ✅ Follow the development → UAT → production flow
5. ✅ Document any changes to workflows
6. ✅ Keep this document updated
7. ✅ Monitor first 5 minutes after deployment

---

## 🎯 Quick Reference

**Last Successful E2E Deployment:**
- **Date:** 2025-12-04 09:11-09:29 UTC
- **PR Chain:** #999 → #1000 → #1001
- **Total Time:** ~13 minutes
- **Errors:** 0
- **Rollbacks:** 0

**Critical Files:**
- frontend/package.json (React 18.2.0)
- frontend/package-lock.json (all locked)
- .github/workflows/*.yml (job structure)
- backend/dockerfile (JSON exec CMD)

**This is your source of truth for deployment configuration.**  
**If something breaks, compare against this golden state.**

---

*This document represents the verified working state as of 2025-12-04. All future deployment configurations should maintain compatibility with these settings until a new golden state is established and documented.*
