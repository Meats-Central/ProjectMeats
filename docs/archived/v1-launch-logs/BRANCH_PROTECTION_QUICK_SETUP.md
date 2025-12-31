# Quick Branch Protection Setup

**⏱️ Time Required:** 10 minutes  
**🎯 Goal:** Prevent future branch divergence  
**📅 Date:** 2025-11-29

---

## ✅ Prerequisites Complete

- ✅ PR #620 merged - Production deployment fixed
- ✅ PR #621 merged - Branches synced (main ← development)
- ✅ Current state: Main only 1 commit ahead (acceptable)

---

## 🚀 Quick Setup (3 Rules)

### Step 1: Navigate to Settings

**URL:** https://github.com/Meats-Central/ProjectMeats/settings/branches

Or: `Settings` → `Branches` → `Add branch protection rule`

---

### Rule 1: Protect `main` Branch

**Branch name pattern:** `main`

**Check these boxes:**

```
☑️ Require a pull request before merging
   ☑️ Require approvals: 1
   ☑️ Dismiss stale pull request approvals when new commits are pushed

☑️ Require status checks to pass before merging
   ☑️ Require branches to be up to date before merging
   Search for: build-and-push ➕ test-frontend ➕ test-backend

☑️ Require conversation resolution before merging

☑️ Do not allow bypassing the above settings
   (Enforces rules even for admins)
```

**Click:** `Create` or `Save changes`

---

### Rule 2: Protect `uat` Branch

**Branch name pattern:** `uat`

**Check these boxes:**

```
☑️ Require a pull request before merging
   ☑️ Require approvals: 1

☑️ Require status checks to pass before merging
   Search for: build-and-push ➕ test-frontend ➕ test-backend

☑️ Require conversation resolution before merging
```

**Click:** `Create` or `Save changes`

---

### Rule 3: Protect `development` Branch

**Branch name pattern:** `development`

**Check these boxes:**

```
☑️ Require a pull request before merging
   ☑️ Require approvals: 1

☑️ Require status checks to pass before merging
   Search for: build-and-push ➕ test-frontend ➕ test-backend
```

**Click:** `Create` or `Save changes`

---

## ✅ Verification

After setting up, verify protection is active:

```bash
# Try to push directly to main (should fail)
git push origin main
# Expected: "refusing to allow a Personal Access Token to push to a protected branch"

# Check protection status
gh api repos/Meats-Central/ProjectMeats/branches/main/protection \
  --jq '.required_status_checks.contexts[]'
# Expected: build-and-push, test-frontend, test-backend
```

---

## 📊 Before vs After

### Before (Current State)
```
❌ Direct pushes to main allowed
❌ Hotfixes bypassed development
❌ Main 25+ commits ahead of development
```

### After (Protected State)
```
✅ All changes require PRs
✅ Status checks must pass
✅ Flow enforced: development → uat → main
```

---

## 🔄 Proper Workflow After Protection

### Normal Feature Development
```bash
1. git checkout development
2. git checkout -b feature/my-feature
3. # Make changes, commit
4. gh pr create --base development
5. # After merge, auto-promote to uat
6. # After UAT testing, promote to main
```

### Emergency Hotfix
```bash
1. git checkout main
2. git checkout -b hotfix/critical-fix
3. # Make minimal fix, commit
4. gh pr create --base main  # Emergency merge
5. # IMMEDIATELY backport:
   git checkout development
   git checkout -b sync/hotfix-backport
   git cherry-pick <commit-sha>
   gh pr create --base development
```

---

## 🆘 Troubleshooting

### "I can't push to main anymore!"
✅ **This is correct!** Create a PR instead:
```bash
gh pr create --base main --head your-branch
```

### "Status checks are failing"
❌ **Don't bypass** - Fix the tests first:
```bash
# Run tests locally
cd frontend && npm test
cd backend && python manage.py test
```

### "Emergency change needed NOW!"
1. Create hotfix branch from `main`
2. Create PR with `[URGENT]` in title
3. Request immediate review
4. After merge, **backport to development immediately**

---

## 📈 Monitoring Branch Health

**Daily Check:**
```bash
git fetch origin
git log development..origin/main --oneline | wc -l
# Expected: 0 (or ≤3 during active hotfix window)
```

**If divergence detected:**
```bash
# Create sync PR
git checkout development
git checkout -b sync/main-to-dev-$(date +%Y%m%d)
git merge origin/main --no-edit
git push origin sync/main-to-dev-$(date +%Y%m%d)
gh pr create --base development --title "sync: merge main hotfixes to development"
```

---

## 🎯 Success Criteria

After setup, you should see:

1. **GitHub UI shows:**
   - 🔒 Protected branch badges on `main`, `uat`, `development`
   - ⚙️ Required checks listed under branch settings

2. **Workflow enforced:**
   - All changes go through PRs
   - Tests must pass before merge
   - Admins can't bypass rules (main branch only)

3. **Branch health:**
   - `development` ≥ `uat` ≥ `main` (commit count)
   - No divergence (all commits flow in one direction)

---

## 📚 Additional Resources

- **Full Guide:** `BRANCH_PROTECTION_SETUP.md`
- **Workflow Checklist:** `branch-workflow-checklist.md`
- **GitHub Docs:** https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches

---

**Status:** Ready to implement  
**Priority:** High - Prevents future divergence  
**Owner:** Repository administrators  
**Next Review:** After first week of enforcement
