# Phase 2 Compliance - Post-Merge Testing Plan

**Date Created:** 2025-12-04  
**PR:** #891  
**Branch:** fix/update-upload-artifact-action  
**Target:** development

---

## Overview

This document provides a comprehensive testing plan to validate Phase 2 compliance changes after merge to development branch.

---

## 🎯 Testing Objectives

1. Verify React 19 functionality in development environment
2. Validate TypeScript 5.9 compilation and type safety
3. Confirm multi-tenancy migrations work idempotently
4. Test docker-compose local development setup
5. Monitor deployment workflow execution

---

## ✅ Pre-Merge Checklist

### Code Review
- [ ] All commits reviewed and approved
- [ ] No merge conflicts with development branch
- [ ] CI/CD checks all passing
- [ ] Documentation reviewed and approved

### Automated Tests
- [x] Frontend TypeScript type-check: PASSED
- [x] Frontend unit tests: PASSED (33/33)
- [x] Frontend production build: PASSED
- [x] Docker Compose syntax: VALID
- [x] Workflow YAML syntax: VALID

---

## 🧪 Post-Merge Testing

### Phase 1: Local Development Environment (Day 1)

#### Test 1.1: Docker Compose Validation
```bash
# Pull latest development branch
git checkout development
git pull origin development

# Test docker-compose startup
docker-compose up -d

# Expected: All services start with health checks passing
docker-compose ps
# ✅ db: healthy
# ✅ backend: running
# ✅ frontend: running

# Test database connection
docker-compose exec backend python manage.py dbshell
# ✅ Successfully connects to PostgreSQL

# Cleanup
docker-compose down -v
```

**Success Criteria:**
- All services start without errors
- PostgreSQL health check passes within 30 seconds
- Backend connects to database successfully
- Frontend accessible at http://localhost:3000

#### Test 1.2: Frontend React 19 Validation
```bash
cd frontend

# Test type checking
npm run type-check
# ✅ Expected: 0 errors

# Run unit tests
npm run test:ci
# ✅ Expected: All 33 tests pass

# Test development server
npm start
# ✅ Expected: Dev server starts on port 3000

# Test production build
npm run build
# ✅ Expected: Build succeeds, bundle size ~273 kB
```

**Success Criteria:**
- TypeScript compilation succeeds with 0 errors
- All unit tests pass
- Development server runs without errors
- Production build completes successfully
- No React 19 breaking changes impact functionality

#### Test 1.3: Backend Multi-Tenancy Migrations
```bash
cd backend

# Test shared schema migrations (idempotent)
python manage.py migrate_schemas --shared --fake-initial --noinput
# ✅ Expected: Succeeds, can be run multiple times safely

# Test super tenant creation (idempotent)
python manage.py create_super_tenant --no-input
# ✅ Expected: Succeeds, no duplicates created

# Test tenant schema migrations (idempotent)
python manage.py migrate_schemas --tenant --fake-initial --noinput
# ✅ Expected: Succeeds, applies to all tenant schemas

# Re-run to verify idempotency
python manage.py migrate_schemas --shared --fake-initial --noinput
python manage.py migrate_schemas --tenant --fake-initial --noinput
# ✅ Expected: No errors, "no migrations to apply" or safe skips
```

**Success Criteria:**
- Shared schema migrations succeed
- Super tenant created without duplicates
- Tenant migrations apply to all schemas
- All migration commands are idempotent (safe to re-run)
- No SQLite fallback errors

---

### Phase 2: CI/CD Pipeline Validation (Day 1-2)

#### Test 2.1: Dev Deployment Workflow
```bash
# Trigger dev deployment by pushing to development
git checkout development
git push origin development

# Monitor workflow execution
gh run list --branch development --limit 5
gh run watch <run-id>
```

**Expected Workflow Steps:**
1. ✅ lint-yaml job passes
2. ✅ build-and-push creates SHA-tagged images
3. ✅ test-frontend passes with React 19
4. ✅ test-backend passes with PostgreSQL service
5. ✅ migrate job runs migrate_schemas with --fake-initial
6. ✅ deploy-frontend succeeds
7. ✅ deploy-backend succeeds
8. ✅ Health checks pass

**Success Criteria:**
- All workflow jobs complete successfully
- Migration job uses correct migrate_schemas commands
- No SQLite fallback errors in logs
- Frontend deploys with React 19 build
- Backend deploys with updated migrations
- Health checks return 200 OK

#### Test 2.2: Migration Idempotency in CI
```bash
# Re-run deployment to same environment
gh workflow run "Deploy Dev (Frontend + Backend via DOCR and GHCR)"

# Monitor migrate job specifically
gh run view <run-id> --job <migrate-job-id> --log
```

**Success Criteria:**
- Migration job completes without errors
- Logs show "no migrations to apply" or safe skips
- No duplicate table/column errors
- --fake-initial flag prevents conflicts

---

### Phase 3: Functional Testing (Day 2-3)

#### Test 3.1: Frontend React 19 Features
Test in deployed dev environment:

1. **Component Rendering**
   - [ ] Dashboard loads without errors
   - [ ] All navigation links work
   - [ ] Data fetching components work
   - [ ] Forms submit successfully

2. **State Management**
   - [ ] Context providers work correctly
   - [ ] useState/useEffect hooks function normally
   - [ ] No React 19 breaking changes detected

3. **TypeScript Type Safety**
   - [ ] No runtime type errors in console
   - [ ] Prop types validated correctly
   - [ ] API responses typed properly

**Browser Testing:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (if available)

#### Test 3.2: Multi-Tenancy Functionality
Test tenant isolation:

1. **Tenant Creation**
   ```bash
   # SSH to dev server
   ssh <dev-server>
   docker exec -it pm-backend bash
   
   # Create test tenant
   python manage.py shell
   >>> from apps.tenants.models import Client, Domain
   >>> tenant = Client.objects.create(
   ...     schema_name='test_tenant',
   ...     name='Test Tenant',
   ...     description='Testing Phase 2 compliance'
   ... )
   >>> Domain.objects.create(
   ...     domain='test.dev.meatscentral.com',
   ...     tenant=tenant,
   ...     is_primary=True
   ... )
   ```

2. **Tenant Isolation**
   - [ ] New tenant schema created
   - [ ] Migrations applied to tenant schema
   - [ ] Data isolated between tenants
   - [ ] No cross-tenant data leaks

3. **Schema Migrations**
   - [ ] Run migrate_schemas --tenant
   - [ ] Verify all tenant schemas updated
   - [ ] Check migration history per tenant

#### Test 3.3: Docker Compose Local Dev
For new developers:

1. **Clean Setup**
   ```bash
   # Fresh checkout
   git clone <repo-url>
   cd ProjectMeats
   git checkout development
   
   # Create .env files (copy from .env.example)
   cp backend/.env.example backend/.env
   
   # Start services
   docker-compose up -d
   
   # Wait for health checks
   sleep 30
   docker-compose ps
   ```

2. **Development Workflow**
   - [ ] Services start on first run
   - [ ] Hot reload works for frontend
   - [ ] Database persists data across restarts
   - [ ] Logs accessible via docker-compose logs

3. **Cleanup and Restart**
   ```bash
   docker-compose down
   docker-compose up -d
   # ✅ Expected: Services restart without errors
   ```

---

### Phase 4: Performance & Monitoring (Day 3-4)

#### Test 4.1: Build Performance
Compare before/after metrics:

| Metric | Before (React 18, TS 4.9) | After (React 19, TS 5.9) |
|--------|---------------------------|--------------------------|
| Frontend build time | ~X min | ~Y min |
| Frontend bundle size | ~X kB | 273.38 kB |
| Type check time | ~X sec | ~Y sec |
| Test execution time | ~X sec | 5.978 sec |

**Success Criteria:**
- Build time change within ±20%
- Bundle size change within ±10%
- No significant performance regressions

#### Test 4.2: Deployment Time
Monitor workflow execution times:

| Workflow Step | Before | After | Delta |
|---------------|--------|-------|-------|
| lint-yaml | X sec | Y sec | ±Z sec |
| build-and-push | X min | Y min | ±Z min |
| test-frontend | X min | Y min | ±Z min |
| test-backend | X min | Y min | ±Z min |
| migrate | X min | Y min | ±Z min |
| deploy-frontend | X min | Y min | ±Z min |
| deploy-backend | X min | Y min | ±Z min |
| **Total** | X min | Y min | ±Z min |

**Success Criteria:**
- Total deployment time within ±15%
- No single step takes >2x previous time

#### Test 4.3: Error Monitoring
Monitor for 48 hours post-deployment:

```bash
# Backend error logs
ssh <dev-server>
docker logs pm-backend --since 48h | grep -i "error\|exception\|traceback"

# Frontend console errors
# Check browser console for React errors
# Monitor Sentry/error tracking (if configured)

# Database query performance
docker exec -it projectmeats-db psql -U user -d projectmeats
SELECT query, calls, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

**Success Criteria:**
- No new critical errors introduced
- No React 19 deprecation warnings
- No TypeScript compilation errors
- Database query performance stable

---

## 📊 Testing Results Template

### Test Execution Summary

**Date:** _________________  
**Tester:** _________________  
**Environment:** development  

#### Phase 1: Local Development
| Test | Status | Notes |
|------|--------|-------|
| Docker Compose | ⬜ PASS / ⬜ FAIL | |
| React 19 Frontend | ⬜ PASS / ⬜ FAIL | |
| Multi-Tenancy Migrations | ⬜ PASS / ⬜ FAIL | |

#### Phase 2: CI/CD Pipeline
| Test | Status | Notes |
|------|--------|-------|
| Dev Deployment | ⬜ PASS / ⬜ FAIL | |
| Migration Idempotency | ⬜ PASS / ⬜ FAIL | |

#### Phase 3: Functional Testing
| Test | Status | Notes |
|------|--------|-------|
| React 19 Features | ⬜ PASS / ⬜ FAIL | |
| Multi-Tenancy | ⬜ PASS / ⬜ FAIL | |
| Docker Compose Dev | ⬜ PASS / ⬜ FAIL | |

#### Phase 4: Performance
| Test | Status | Notes |
|------|--------|-------|
| Build Performance | ⬜ PASS / ⬜ FAIL | |
| Deployment Time | ⬜ PASS / ⬜ FAIL | |
| Error Monitoring | ⬜ PASS / ⬜ FAIL | |

---

## 🐛 Known Issues & Workarounds

### Issue 1: react-scripts Peer Dependency Warning
**Symptom:** npm install shows peer dependency warning for TypeScript 5.9  
**Impact:** Non-blocking, doesn't affect functionality  
**Workaround:** Safe to ignore, will be resolved with react-scripts v6 upgrade  
**Tracking:** Add to next sprint backlog

### Issue 2: [Add issues as discovered]
**Symptom:**  
**Impact:**  
**Workaround:**  
**Tracking:**

---

## 🔄 Rollback Plan

If critical issues are discovered:

### Option 1: Revert PR
```bash
# On development branch
git revert <merge-commit-sha> -m 1
git push origin development
```

### Option 2: Emergency Hotfix
```bash
# Create hotfix branch
git checkout -b hotfix/phase2-rollback development

# Cherry-pick specific fixes or revert changes
git revert <problematic-commit>

# Create emergency PR
gh pr create --base development --title "hotfix: Rollback Phase 2 changes"
```

### Option 3: Database Migration Rollback
If migration issues occur:
```bash
# SSH to affected server
ssh <server>
docker exec -it pm-backend bash

# Rollback migrations (if needed)
python manage.py migrate <app_name> <previous_migration>

# Or restore from backup
psql -U user -d projectmeats < backup.sql
```

---

## ✅ Sign-Off

**Pre-Merge Validation:**
- [ ] All automated tests passed
- [ ] Code review approved
- [ ] Documentation reviewed
- [ ] PR approved and ready to merge

**Post-Merge Validation:**
- [ ] Phase 1 testing complete
- [ ] Phase 2 testing complete
- [ ] Phase 3 testing complete
- [ ] Phase 4 monitoring complete
- [ ] No critical issues identified
- [ ] Ready for UAT promotion

**Approvals:**
- Tech Lead: _________________ Date: _________
- QA Lead: _________________ Date: _________
- DevOps: _________________ Date: _________

---

## 📚 References

- PR #891: https://github.com/Meats-Central/ProjectMeats/pull/891
- docs/UPGRADE.md - Migration guide
- PHASE2_COMPLIANCE_COMPLETE.md - Implementation report
- ROADMAP.md - Project roadmap

---

*This testing plan ensures Phase 2 compliance changes are thoroughly validated before UAT promotion.*
