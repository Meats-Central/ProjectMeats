# Pipeline Changes Quick Reference

**PR #871** | **Status:** Ready for Review | **Date:** 2025-12-01

---

## 🎯 What Changed?

### Dev Workflow Only
- **New:** Decoupled `migrate` job runs before deployment
- **Changed:** Deploy jobs now wait for migrations to complete
- **Why:** Prevents SSH-based migration failures, enables rollback

### All Workflows
- **Fixed:** Duplicate SHA tags (prod, uat)
- **Added:** `-latest` tags alongside SHA tags
- **Why:** Immutable deployments with cache support

---

## 🔑 Key Changes at a Glance

| Environment | Before | After |
|-------------|--------|-------|
| **Dev** | Migrations in deploy step (SSH) | Separate migrate job (CI) |
| **UAT** | Already correct ✅ | Fixed duplicate tags only |
| **Prod** | Already correct ✅ | Fixed duplicate tags only |

---

## 🚀 Migration Pattern (All Envs)

```bash
# Step 1: Shared schema
migrate_schemas --shared --fake-initial --noinput

# Step 2: Super tenant  
create_super_tenant --no-input

# Step 3: Tenant schemas
migrate_schemas --tenant --noinput
```

**Key:** `--fake-initial` makes re-runs safe (idempotent)

---

## 🏷️ Image Tagging Pattern

### Build Step (pushes both)
```yaml
tags:
  - registry/image:dev-abc123def  # For deployment
  - registry/image:dev-latest     # For cache
```

### Deploy Step (uses SHA only)
```bash
docker pull registry/image:dev-abc123def  # NOT -latest
```

---

## ✅ What to Verify After Merge

### 1. First Dev Deployment
```bash
# Watch the workflow run
gh run watch

# Check migrate job succeeded
gh run view <run_id> --log --job="migrate"
```

### 2. Verify Idempotency
```bash
# Deploy twice to same environment
# Second run should NOT error with "already exists"
```

### 3. Check Image Tags
```bash
# On dev server
ssh dev@dev.meatscentral.com "docker ps --format '{{.Image}}'"

# Should see: registry.../image:dev-abc123def (SHA, not -latest)
```

---

## 🔄 Workflow Dependency Chain

### Before (Dev)
```
build → test-backend → deploy-backend (runs migrations)
```

### After (Dev)
```
build + test-backend → migrate → deploy-backend
                    ↘        ↗
                     deploy-frontend
```

**Result:** Migrations run once in CI, deployments just pull and run

---

## 📊 Expected Improvements

| Metric | Impact |
|--------|--------|
| **Migration Reliability** | ↑ (CI environment > SSH) |
| **Deployment Safety** | ↑ (blocked if migrations fail) |
| **Rollback Capability** | ↑ (SHA tags = specific versions) |
| **Developer Onboarding** | ↑ (Codespace auto-migrates) |

---

## 🚨 If Something Goes Wrong

### Dev Deployment Fails
1. Check migrate job logs: `gh run view <id> --log --job=migrate`
2. Common issues:
   - Database connection: Check `DEV_DB_URL` secret
   - Permission denied: Check database user permissions
   - Already exists: Verify `--fake-initial` flag present

### Wrong Image Deployed
1. Check deployment logs: `grep "docker pull" workflow.log`
2. Should see SHA tag, not `-latest`
3. If wrong: Check workflow file line ~255 (dev), ~330 (uat), ~320 (prod)

### Rollback Needed
```bash
# Find previous good SHA
git log --oneline -10

# Manually trigger workflow with that SHA
# Or: Revert merge commit, push to development
```

---

## 📖 Documentation

- **Full Guide:** `docs/PIPELINE_DECOUPLING_IMPLEMENTATION.md`
- **Validation:** `docs/PIPELINE_IMPLEMENTATION_VALIDATION.md`
- **PR:** https://github.com/Meats-Central/ProjectMeats/pull/871

---

## 💡 Key Concepts

### Idempotency
**What:** Running same command multiple times = same result  
**How:** `--fake-initial` flag skips already-applied migrations  
**Why:** Safe to re-deploy without errors

### Immutable Tagging
**What:** Each commit = unique image tag (SHA)  
**How:** `image:env-abc123def` instead of `image:env-latest`  
**Why:** Exact version control, precise rollback

### Decoupled Migrations
**What:** Migrations run separately from deployment  
**How:** Dedicated `migrate` job in workflow  
**Why:** Clear separation, better error handling

---

## ✅ Approval Checklist

Before merging PR #871:

- [ ] Review PR description and changes
- [ ] Understand rollout plan (dev → uat → prod)
- [ ] Know rollback procedure (revert or previous SHA)
- [ ] Team informed of migration job change
- [ ] Monitoring plan agreed upon

After merge:

- [ ] Watch first dev deployment
- [ ] Verify migrate job runs successfully
- [ ] Check images tagged correctly
- [ ] Document any issues encountered

---

**Questions?** See full documentation or ask in PR comments.

**Ready to merge?** All checks passed, documentation complete!
