# Branch Protection Setup Guide

## Purpose
Prevent future branch divergence by enforcing GitFlow: `development` → `UAT` → `main`

## Problem Resolved
Main was 25+ commits ahead of development due to hotfixes bypassing the proper flow.

**Related PRs:**
- #620 - Production env-config.js fix
- #621 - Sync main → development

---

## Branch Protection Rules

### 1. Protect `main` Branch

**Settings → Branches → Add branch protection rule**

**Branch name pattern:** `main`

**Required settings:**
- ✅ Require a pull request before merging
  - Required approvals: 1
  - Dismiss stale PR approvals when new commits are pushed
- ✅ Require status checks to pass before merging
  - Require branches to be up to date before merging
  - Status checks: 
    - `build-and-push`
    - `test-frontend`
    - `test-backend`
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings
- ✅ Restrict who can push to matching branches
  - Allow: Only from `UAT` branch via PR

**Why:** Ensures only UAT-tested code reaches production

---

### 2. Protect `UAT` Branch

**Branch name pattern:** `UAT`

**Required settings:**
- ✅ Require a pull request before merging
  - Required approvals: 1
- ✅ Require status checks to pass before merging
  - Status checks:
    - `build-and-push`
    - `test-frontend`
    - `test-backend`
- ✅ Restrict who can push to matching branches
  - Allow: Only from `development` branch via PR

**Why:** Ensures only dev-tested code reaches UAT

---

### 3. Protect `development` Branch

**Branch name pattern:** `development`

**Required settings:**
- ✅ Require a pull request before merging
  - Required approvals: 1 (can be lower for dev)
- ✅ Require status checks to pass before merging
  - Status checks:
    - `build-and-push`
    - `test-frontend`
    - `test-backend`
- ✅ Allow force pushes (for cleanup only)
  - Only for admins

**Why:** Maintains quality while allowing flexibility for active development

---

## Hotfix Exception Process

**For critical production bugs:**

### Option 1: Proper Flow (Recommended)
1. Create hotfix branch from `main`: `hotfix/description`
2. Fix and test
3. PR to `main` (emergency)
4. **Immediately** create PR from `main` → `development` (sync)
5. Let sync flow through: `development` → `UAT` → `main`

### Option 2: Cherry-Pick (If Option 1 Not Feasible)
1. Merge hotfix to `main`
2. Cherry-pick commit to `development`
3. Let it flow: `development` → `UAT` → `main`

### ⚠️ Never Skip Backporting
**Always** bring hotfixes back to development to prevent divergence.

---

## Automation Workflows

Existing workflows that support this flow:

### Promotion Workflows
- `.github/workflows/promote-dev-to-uat.yml` - Auto-create PR: dev → UAT
- `.github/workflows/promote-uat-to-main.yml` - Auto-create PR: UAT → main

### Deployment Workflows
- `.github/workflows/11-dev-deployment.yml` - Deploy on push to `development`
- `.github/workflows/12-uat-deployment.yml` - Deploy on push to `UAT`
- `.github/workflows/13-prod-deployment.yml` - Deploy on push to `main`

**Note:** Promotion workflows create PRs automatically but require manual approval/merge.

---

## Monitoring Branch Health

### Regular Checks
```bash
# Check if main is ahead of development (should be 0)
git fetch origin
git log development..main --oneline | wc -l

# Check if UAT is ahead of development (should be 0 or very small)
git log development..UAT --oneline | wc -l

# Check if main is ahead of UAT (should be 0 or very small)
git log UAT..main --oneline | wc -l
```

### Expected State
- `development` is always ahead or equal to `UAT`
- `UAT` is always ahead or equal to `main`
- Divergence = 0 commits or very small window during active PR

---

## Setup Instructions

1. **Navigate to Repository Settings**
   - Go to: https://github.com/Meats-Central/ProjectMeats/settings/branches

2. **Add Protection Rules** (follow sections 1-3 above)

3. **Test the Protection**
   ```bash
   # This should fail (protected)
   git push origin main
   
   # This should require PR
   git push origin development
   ```

4. **Document Exceptions**
   - Add admin bypass reasons to audit log
   - Document all direct pushes in CHANGELOG.md

---

## Benefits

✅ **Prevents Divergence** - Enforces single flow direction  
✅ **Quality Gates** - Tests must pass at each stage  
✅ **Audit Trail** - All changes tracked through PRs  
✅ **Team Alignment** - Clear promotion path for all contributors  
✅ **Rollback Safety** - Each environment has tested state

---

## Troubleshooting

### "Cannot push to protected branch"
✅ **Expected behavior** - Create a PR instead

### "Status checks failed"
Fix tests before merging. Don't bypass.

### "Main is ahead of development again"
1. Check audit log for direct pushes
2. Create sync PR: `main` → `development`
3. Review branch protection settings

### "Emergency hotfix needed NOW"
Use Option 1 from Hotfix Exception Process above.

---

**Last Updated:** 2025-11-29  
**Related Issues:** #620, #621  
**Maintainer:** @Vacilator
