# Automated Tests - Quick Reference

## 🚀 Quick Start

### For Developers

**Your PR gets tested automatically!** No action needed.

When you:
1. Open a PR to `development`, `uat`, or `main`
2. Push new commits to an open PR
3. Mark a draft PR as "Ready for review"

Then:
- ✅ Frontend tests run (Jest + TypeScript)
- ✅ Backend tests run (Django + PostgreSQL)
- 💬 Results posted as PR comments
- 📊 Coverage report generated

## 📋 What Gets Tested

| Component | Tests | Duration |
|-----------|-------|----------|
| Frontend | 33 tests (Jest) | ~5-10s |
| Backend | 17 test files (Django) | ~30-60s |
| TypeScript | Type checking | ~5s |
| Migrations | Validation | ~10s |

## 🎯 Manual Testing

Need to run tests manually?

1. Go to **Actions** → **Automated Tests**
2. Click **"Run workflow"**
3. Select your branch
4. Optional: Check boxes to skip frontend or backend
5. Click **"Run workflow"**

## 📊 Reading Results

### In PR Comments

You'll see 3 comments:
1. **Frontend Tests** - With coverage percentages
2. **Backend Tests** - With migration status
3. **Test Results Summary** - Overall status table

### Status Indicators
- ✅ = Passed
- ❌ = Failed
- ⏭️ = Skipped
- ⚠️ = Cancelled/Error

## 🔧 Common Issues

### Tests failing?
```bash
# Run locally first
cd frontend && npm run test:ci
cd backend && python manage.py test apps/
```

### Workflow not triggering?
- Check PR is not in draft mode
- Verify targeting correct branch (dev/uat/main)
- Ensure Actions are enabled

### Need help?
- See: [docs/automated-testing.md](automated-testing.md)
- Tag: `@devops-vst` in PR comments

## 💡 Pro Tips

1. **Fix tests locally** before pushing to save CI time
2. **Keep PRs small** for faster test runs
3. **Check coverage** - aim to maintain or improve
4. **Don't skip tests** unless absolutely necessary
5. **Review logs** if tests fail - they're detailed!

## 🔗 Links

- [Full Documentation](automated-testing.md)
- [Workflow File](.github/workflows/40-automated-tests.yml)
- [GitHub Actions](https://github.com/Meats-Central/ProjectMeats/actions/workflows/40-automated-tests.yml)

---

**Last Updated**: 2025-11-20  
**Workflow Version**: 1.0.0
