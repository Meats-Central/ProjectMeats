# Repository Cleanup Checklist
**Generated from**: REPO_AUDIT_PLATFORM_CORE.md  
**Date**: 2025-10-07

This checklist provides actionable items from the Platform Core Components audit.

---

## 🚨 CRITICAL - Security Issues (Do Immediately)

- [ ] **Remove secrets directory** 
  ```bash
  rm -rf "secrets and environment backups - sajid/"
  ```
  - ⚠️ **HIGH SECURITY RISK**: May contain sensitive credentials
  - After removal: Review screenshots to check for exposed secrets
  - If secrets found: Rotate all credentials immediately

- [x] **Remove backup files** - **PARTIALLY COMPLETED**
  ```bash
  rm backend/.env.env.backup
  rm frontend/.env.env.local.backup
  rm backend/projectmeats/settings_original_backup.py
  # ✅ Archived: .github/workflows/ci-cd.yml.sajid-workflow-backup → archived/code/
  ```

- [ ] **Update .gitignore**
  ```
  # Add these patterns:
  *.backup
  secrets*/
  *secrets*/
  *.env.backup
  *.env.*.backup
  ```

---

## 📁 HIGH Priority - File Organization

### Docker Configuration Consolidation

- [ ] Move docker-compose files to config/deployment/
  ```bash
  mv docker-compose.dev.yml config/deployment/
  mv docker-compose.prod.yml config/deployment/
  mv docker-compose.uat.yml config/deployment/docker-compose.staging.yml
  ```

- [ ] Update references in documentation
  - [ ] Update README.md
  - [ ] Update USER_DEPLOYMENT_GUIDE.md
  - [ ] Update docs/DEPLOYMENT_GUIDE.md
  - [ ] Update Makefile if needed

- [ ] (Optional) Create symlinks for backward compatibility
  ```bash
  ln -s config/deployment/docker-compose.dev.yml docker-compose.dev.yml
  ln -s config/deployment/docker-compose.prod.yml docker-compose.prod.yml
  ln -s config/deployment/docker-compose.staging.yml docker-compose.staging.yml
  ```

### Environment Configuration Consolidation

- [ ] Remove duplicate environment templates
  ```bash
  rm backend/.env.production.example
  rm frontend/.env.production.example
  ```

- [ ] Update config/README.md to document:
  - [ ] `config/environments/` as source of truth
  - [ ] How to use environment files
  - [ ] Migration path from old structure

- [ ] Update config/shared/ templates to reference config/environments/

### Root Directory Organization

- [ ] Create scripts directory
  ```bash
  mkdir -p scripts
  ```

- [ ] Move utility scripts
  ```bash
  mv health_check.py scripts/
  mv setup_env.py scripts/
  mv simulate_deployment.py scripts/
  mv test_deployment.py scripts/
  ```

- [ ] Update script references
  - [ ] Update GitHub workflows
  - [ ] Update Makefile
  - [ ] Update documentation
  - [ ] Update any deployment scripts

- [x] Move copilot files - **COMPLETED**
  ```bash
  # Moved to .github/ per GitHub best practices
  # copilot-instructions.md → .github/copilot-instructions.md
  # copilot-log.md → .github/copilot-log.md
  ```

---

## 🔧 MEDIUM Priority - Code Quality

### Incomplete Apps

- [ ] **bug_reports app** - Choose one:
  - [ ] Option A: Complete implementation
    - [ ] Add models.py
    - [ ] Add serializers.py
    - [ ] Add views.py
    - [ ] Add admin.py
    - [ ] Add tests.py
  - [ ] Option B: Remove if not needed
    - [ ] Remove app directory
    - [ ] Remove from INSTALLED_APPS
    - [ ] Remove URL imports

### Test Coverage

- [ ] Add test files for apps without tests:
  - [ ] backend/apps/accounts_receivables/tests.py
  - [ ] backend/apps/ai_assistant/tests.py
  - [ ] backend/apps/carriers/tests.py
  - [ ] backend/apps/contacts/tests.py
  - [ ] backend/apps/core/tests.py
  - [ ] backend/apps/customers/tests.py
  - [ ] backend/apps/plants/tests.py
  - [ ] backend/apps/suppliers/tests.py

- [ ] Follow test pattern from:
  - backend/apps/purchase_orders/test_api_endpoints.py
  - backend/apps/tenants/tests.py

---

## 📚 MEDIUM Priority - Documentation

### TODO_LOG.md Maintenance

- [ ] Archive completed Sprint 1 content
  - [ ] Create docs/archive/sprint-1-summary.md
  - [ ] Move completed items to archive
  - [ ] Keep only current sprint in TODO_LOG.md

- [ ] Trim to active items only
  - Current sprint focus
  - Next 2 sprint planning
  - Active risk items

### Documentation Updates

- [ ] Update docs/README.md
  - [ ] Add reference to REPO_AUDIT_PLATFORM_CORE.md
  - [ ] Update file locations after reorganization
  - [ ] Add CLEANUP_CHECKLIST.md to index

- [ ] Update CONTRIBUTING.md
  - [ ] Document new scripts/ directory
  - [x] Document copilot files location (.github/) - **COMPLETED**
  - [ ] Update configuration references

---

## 🔍 LOW Priority - Enhancements

### Dependency Management

- [ ] Backend: Create requirements-dev.txt
  - Move development-only dependencies
  - pytest, black, flake8, etc.

- [ ] Backend: Pin all dependency versions
  - Review requirements.txt
  - Replace >= with ==
  - Document version policy

- [ ] Frontend: Review and update dependencies
  - Check for security updates
  - Update package.json if needed

### CI/CD Improvements

- [ ] Consider consolidating planner workflows
  - planner-Auto-Assign-to-Copilot.yml
  - planner-auto-add-issue.yml
  - planner-review-and-test
  - planner-sprint-gen.yml

- [ ] Add workflow documentation
  - Create docs/workflows/README.md
  - Document each workflow purpose
  - Add troubleshooting guide

### Code Organization

- [ ] Review config/deployment/ structure
  - Ensure staging config exists and is correct
  - Document differences between environments
  - Create comparison matrix

---

## ✅ Verification Steps

After completing cleanup:

- [ ] **Test builds**
  ```bash
  docker-compose -f config/deployment/docker-compose.dev.yml build
  docker-compose -f config/deployment/docker-compose.staging.yml build
  docker-compose -f config/deployment/docker-compose.prod.yml build
  ```

- [ ] **Test deployments**
  ```bash
  # Development
  cd scripts && python test_deployment.py
  
  # Staging
  # (follow deployment process)
  ```

- [ ] **Run test suite**
  ```bash
  cd backend && python manage.py test
  cd frontend && npm test
  ```

- [ ] **Verify documentation**
  - All links work
  - File references are correct
  - Instructions are accurate

- [ ] **Check .gitignore**
  - No backup files tracked
  - No secrets tracked
  - Build artifacts ignored

---

## 📊 Progress Tracking

| Phase | Items | Completed | Status |
|-------|-------|-----------|--------|
| **Phase 1: Security** | 3 | 0 | ⏳ Not Started |
| **Phase 2: Organization** | 4 | 0 | ⏳ Not Started |
| **Phase 3: Configuration** | 3 | 0 | ⏳ Not Started |
| **Phase 4: Code Quality** | 2 | 0 | ⏳ Not Started |
| **Total** | 12 | 0 | **0%** |

---

## 🎯 Success Criteria

Cleanup is complete when:

1. ✅ No security issues (secrets, backups removed)
2. ✅ Single source of truth for configs (config/ directory)
3. ✅ Clean root directory (<15 files)
4. ✅ All tests passing
5. ✅ Documentation updated and accurate
6. ✅ CI/CD pipelines working

---

## 📝 Notes

- **Before starting**: Create a backup branch
  ```bash
  git checkout -b backup/pre-cleanup
  git push origin backup/pre-cleanup
  ```

- **Test incrementally**: Don't make all changes at once

- **Update this checklist**: Mark items as complete

- **Document decisions**: Add notes for future reference

---

## 🔗 Related Documents

- [Full Audit Report](REPO_AUDIT_PLATFORM_CORE.md)
- [Documentation Hub](README.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

---

*Last Updated: 2025-10-07*  
*Next Review: After Phase 1-2 completion*
