# Documentation Cleanup Plan - Development Pipeline Standardization

**Date:** 2025-12-09  
**Status:** Ready for Execution  
**Impact:** Major cleanup - ~95 obsolete files

---

## Executive Summary

The repository has transitioned to **Shared-Schema Multi-Tenancy**, making most django-tenants documentation obsolete. This plan consolidates ~150 documents into:
1. **One Source of Truth**: `docs/DEVELOPMENT_WORKFLOW.md` (✅ Created)
2. **Archive Legacy Docs**: `docs/archive/legacy_2025/` (✅ Created)

---

## What Was Created

### ✅ New Source of Truth Document
**Location:** `docs/DEVELOPMENT_WORKFLOW.md` (29KB)

**Contents:**
- Architecture (Shared-Schema Multi-Tenancy explained)
- Pipeline Stages (Build → Test → Migrate → Deploy)
- Environment Variables & Secrets (Complete reference)
- Operational Commands (Deploy, rollback, logs)
- Troubleshooting (Common issues + solutions)
- Future Enhancements (Migration runner, secret management, orchestration)

**Why Important:**
- Single authoritative reference
- Eliminates conflicting documentation
- Comprehensive operational procedures
- Future-proofing with enhancement roadmap

### ✅ Archive Structure
**Location:** `docs/archive/legacy_2025/`

**Contents:**
- `README.md` - Archive guide explaining what changed
- Space for 95 obsolete documents

---

## Files to Archive (95 Total)

### Category 1: Multi-Tenancy Implementation Docs (16 files)
Files describing the old django-tenants architecture:

```
BUSINESS_SCHEMA_IMPLEMENTATION.md
CICD_ORCHESTRATION_COMPLETE.md
COCKPIT_IMPLEMENTATION_SUMMARY.md
COCKPIT_QUICK_REFERENCE.md
COMPLETE_E2E_SUCCESS.md
DEPLOYMENT_MULTI_TENANCY_FIX.md
MULTI_TENANCY_IMPLEMENTATION.md
PHASE1_ARCHITECTURAL_PURGE_COMPLETE.md
PHASE2_COMPLIANCE_COMPLETE.md
PHASE2_IMPLEMENTATION_CHECKLIST.md
PHASE2_MULTI_TENANCY_ISOLATION_IMPLEMENTATION.md
PHASE2_QUICKSTART.md
PHASE2_QUICK_REFERENCE.md
PHASE3_CONTEXT_CLEANUP_COMPLETE.md
SCHEMA_ISOLATION_MIGRATION_COMPLETE.md
SCHEMA_TENANCY_TEST_FIX_SUMMARY.md
```

### Category 2: Redundant Deployment Docs (26 files)
Now consolidated into `DEVELOPMENT_WORKFLOW.md`:

```
DEPLOYMENT_COMPARISON_SUMMARY.md
DEPLOYMENT_ENHANCEMENTS.md
DEPLOYMENT_FIX_NEXT_STEPS.md
DEPLOYMENT_FIX_SUMMARY.md
DEPLOYMENT_FIX_SUMMARY_OLD.md
DEPLOYMENT_HARDENING_SUMMARY.md
DEPLOYMENT_PIPELINE_HARDENING.md
DEPLOYMENT_QUICK_REF.md
DEPLOYMENT_REFERENCE_INDEX.md
DEPLOYMENT_SETUP_COMPLETE.md
DEPLOYMENT_WORKFLOW_ENHANCEMENTS.md
DEPLOYMENT_WORKFLOW_OPTIMIZATION.md
DEPLOYMENT_WORKFLOW_OPTIMIZATION_PHASE2.md
DEPLOYMENT_WORKING_SOLUTION.md
DEPLOYMENT_YAML_FIX_SUMMARY.md
DEV_ENVIRONMENT_HARDENING_SUMMARY.md
E2E_DEPLOYMENT_SUCCESS_SUMMARY.md
E2E_DEPLOYMENT_TEST.md
E2E_FINAL_TEST.md
E2E_TESTING_SUMMARY.md
E2E_TEST_DEPLOYMENT.md
FINAL_DEPLOYMENT_STATUS.md
GOLDEN_PIPELINE_REFERENCE.md
HARDENING_COMPLETE.md
```

### Category 3: Specific Fix Summaries (53 files)
Historical issue resolutions (reference only):

```
BRANCH_DIVERGENCE_RESOLUTION_SUMMARY.md
DELETE_BUTTON_FIX_SUMMARY.md
DEPLOYMENT_502_ERROR_ANALYSIS.md
DEPLOYMENT_HEALTH_CHECK_FIX.md
DJANGO_ADMIN_PERMISSIONS_FIX_SUMMARY.md
GITHUB_ISSUE_MIGRATION_HISTORY_FIX.md
GITHUB_ISSUE_MISSING_TABLES_FIX.md
GITHUB_ISSUE_STAGING_SECRETS.md
GITHUB_ISSUE_SUPERUSER_ENV_LOADING.md
IMPLEMENTATION_SUMMARY_AUTH_FIX.md
IMPLEMENTATION_SUMMARY_MIGRATION_FIX.md
IMPLEMENTATION_SUMMARY_NAMING_STANDARDS.md
IMPLEMENTATION_SUMMARY_PO_VERSION_HISTORY.md
IMPLEMENTATION_SUMMARY_STAGING_FIX.md
MIGRATION_DEPENDENCIES_FIX_FINAL.md
MIGRATION_DUPLICATE_COLUMN_FIX.md
MIGRATION_FIX_0006_IDEMPOTENCY.md
MIGRATION_FIX_DUPLICATE_DOMAIN_TABLE.md
MIGRATION_FIX_PR135_CORRECTION.md
MIGRATION_FIX_SUMMARY.md
MIGRATION_FIX_SUMMARY_QUICK.md
MIGRATION_SUCCESS_REPORT.md
NGINX_FIX_QUICK_REF.md
NGINX_HEREDOC_INDENTATION_FIX.md
NGINX_ROUTING_OPTIMIZATION_SUMMARY.md
OPERATION_FRESH_START_SUMMARY.md
PR_SUMMARY.md
PR_SUMMARY_BASH_HEREDOC_FIX.md
PR_SUMMARY_SUPERUSER_FIX.md
QUICK_DEPLOYMENT_FIX_SUMMARY.md
README_STAGING_FIX.md
SDLC_LOOP_DEPLOYMENT_FIX.md
SECURITY_SUMMARY_STAGING_FIX.md
SSH_CONNECTION_FIX_IMPLEMENTATION.md
SSH_CONNECTION_FIX_QUICK_REF.md
SSH_CONNECTION_FIX_READY_FOR_TESTING.md
SSH_DEPLOYMENT_ISSUES_SUMMARY.md
SSH_ISSUE_QUICK_REF.md
STAGING_LOAD_FAILURE_FIX.md
SUPERUSER_DUPLICATE_FIX_SUMMARY.md
SUPERUSER_ENVIRONMENT_VARIABLES_FIX.md
SUPERUSER_INTEGRATION_SUMMARY.md
SUPERUSER_PASSWORD_SYNC_FIX.md
SUPERUSER_PASSWORD_SYNC_SUMMARY.md
SUPER_TENANT_FIX_SUMMARY.md
SUPPLIER_ADMIN_UPDATE_VERIFICATION.md
SUPPLIER_CUSTOMER_500_ERROR_FIX.md
SUPPLIER_CUSTOMER_TENANT_FALLBACK_FIX.md
SUPPLIER_FIX_VERIFICATION.md
SUPPLIER_NETWORK_ERROR_FIX_SUMMARY.md
TENANT_VALIDATION_FIX_SUMMARY.md
UAT_SUPERUSER_FIX_SUMMARY.md
WORKFLOW_MIGRATIONS_FIX_SUMMARY.md
WORKFLOW_REVERT_SUMMARY.md
```

---

## Files to KEEP (Still Relevant)

### Core Documentation
```
README.md - Main project readme
CONTRIBUTING.md - Contribution guidelines
CHANGELOG.md - Project changelog
ROADMAP.md - Future plans
```

### Operational Guides
```
docs/DEVELOPMENT_WORKFLOW.md - ✅ NEW SOURCE OF TRUTH
docs/DEPLOYMENT_RUNBOOK.md - Operational procedures
docs/ARCHITECTURE.md - System architecture
docs/DATABASE_MIGRATION_GUIDE.md - Migration procedures (verify current)
docs/DEPLOYMENT_GUIDE.md - High-level deployment guide (consolidate with RUNBOOK)
```

### Development Setup
```
LOCAL_DEVELOPMENT.md - Local setup guide
DEV_SETUP_REFERENCE.md - Development environment
QUICK_START.md - Quick start guide
```

### Feature Documentation
```
AUTHENTICATION_EXPLANATION.md - Auth system
GUEST_MODE_IMPLEMENTATION.md - Guest mode
GUEST_MODE_QUICK_REF.md - Guest mode quick ref
GUEST_USER_PERMISSIONS_GUIDE.md - Guest permissions
INVITE_ONLY_SYSTEM.md - Invitation system
IMPLEMENTATION_SUMMARY_INVITE_SYSTEM.md - Invitation details
IMPLEMENTATION_SUMMARY_GUEST_MODE.md - Guest mode details
TENANT_ACCESS_CONTROL.md - Tenant access
```

### Operational Procedures
```
BRANCH_PROTECTION_SETUP.md - Branch protection
BRANCH_PROTECTION_QUICK_SETUP.md - Quick setup
branch-workflow-checklist.md - Workflow checklist
MAKE_DEV_PUBLIC_GUIDE.md - Dev server public access
```

### Monitoring & Troubleshooting
```
NETWORK_ERROR_TROUBLESHOOTING.md - Network issues
SSH_CONNECTION_TROUBLESHOOTING.md - SSH issues
```

### Configuration Guides
```
ALLOWED_HOSTS_CONFIGURATION.md - Django ALLOWED_HOSTS
COPILOT_INSTRUCTIONS_SETUP.md - GitHub Copilot setup
docs/GITHUB_SECRETS_CONFIGURATION.md - Secrets setup
```

### Utilities
```
DJANGO_STAFF_PERMISSIONS_EXPLAINED.md - Permissions
MODEL_DEFAULTS_AUDIT_SUMMARY.md - Model defaults
MODEL_DEFAULTS_MIGRATION_GUIDE.md - Defaults migration
POSTGRESQL_MIGRATION_GUIDE.md - PostgreSQL specifics
```

---

## Execution Plan

### Step 1: Run Archival Script
```bash
# Execute the archival script
bash /tmp/archive_docs.sh

# Expected output:
# - Moves 95 files to docs/archive/legacy_2025/
# - Prints summary of moved files
```

### Step 2: Verify Archive
```bash
# Check archived files
ls -la docs/archive/legacy_2025/ | wc -l
# Should show ~97 files (95 + README.md + directory)

# Verify root is cleaner
ls -1 *.md | wc -l
# Should be ~40-50 files (down from ~140)
```

### Step 3: Update Key Documents
Update these to reference `DEVELOPMENT_WORKFLOW.md`:

1. **README.md**
   - Add link to `docs/DEVELOPMENT_WORKFLOW.md` in "Documentation" section
   
2. **CONTRIBUTING.md**
   - Update deployment section to point to `DEVELOPMENT_WORKFLOW.md`

3. **docs/DEPLOYMENT_RUNBOOK.md**
   - Add note at top: "For pipeline details, see DEVELOPMENT_WORKFLOW.md"

4. **docs/ARCHITECTURE.md**
   - Ensure it matches shared-schema description
   - Remove any django-tenants references

### Step 4: Consolidate Redundant Guides
**Merge or redirect:**
- `DEPLOYMENT_GUIDE.md` → Point to `DEVELOPMENT_WORKFLOW.md`
- `DEV_SETUP_REFERENCE.md` → Merge into `LOCAL_DEVELOPMENT.md`
- Multiple "QUICK_REF" docs → Create single quick reference

### Step 5: Create Index
Create `docs/INDEX.md` with categorized links to all current docs.

---

## Commit Strategy

```bash
# Stage all changes
git add docs/

# Commit with detailed message
git commit -m "docs: Archive obsolete documentation and create source of truth

BREAKING CHANGE: Major documentation reorganization

What Changed:
- Created docs/DEVELOPMENT_WORKFLOW.md as single source of truth (29KB)
- Archived 95 obsolete documents to docs/archive/legacy_2025/
- Removed django-tenants references (old architecture)
- Consolidated redundant deployment documentation

Why:
- Repository transitioned to Shared-Schema Multi-Tenancy
- django-tenants documentation now obsolete and misleading
- ~150 documents causing confusion and contradictions
- Need single authoritative reference for pipeline

Files Created:
- docs/DEVELOPMENT_WORKFLOW.md (source of truth)
- docs/archive/legacy_2025/README.md (archive guide)

Files Archived:
- 16 multi-tenancy implementation docs
- 26 redundant deployment docs  
- 53 specific fix summaries

Files Kept:
- Core documentation (README, CONTRIBUTING, CHANGELOG)
- Operational guides (still current)
- Feature documentation (guest mode, invites, auth)
- Development setup guides

Migration Guide:
For developers/operators:
1. Start with docs/DEVELOPMENT_WORKFLOW.md
2. Reference docs/DEPLOYMENT_RUNBOOK.md for procedures
3. Check docs/archive/legacy_2025/ only for historical context

For questions: Open issue or ask in #projectmeats-dev

Resolves: Documentation cleanup initiative
See: DOCUMENTATION_CLEANUP_PLAN.md for full details"
```

---

## Post-Cleanup Actions

### Update CI/CD
- [ ] Verify no workflows reference archived docs
- [ ] Update any scripts that parse documentation
- [ ] Check copilot instructions don't reference old docs

### Update External References
- [ ] Check Slack pins/bookmarks
- [ ] Update wiki/Confluence if applicable
- [ ] Update onboarding materials

### Team Communication
- [ ] Announce in #projectmeats-dev
- [ ] Include link to `DEVELOPMENT_WORKFLOW.md`
- [ ] Explain archive location for historical reference

---

## Validation Checklist

After execution, verify:

- [ ] `docs/DEVELOPMENT_WORKFLOW.md` exists and is comprehensive
- [ ] `docs/archive/legacy_2025/README.md` explains the archive
- [ ] ~95 files moved to `docs/archive/legacy_2025/`
- [ ] Root directory has <50 .md files
- [ ] No broken internal links in remaining docs
- [ ] CI/CD workflows still pass
- [ ] Key docs (README, CONTRIBUTING) updated

---

## Rollback Plan

If issues arise:

```bash
# Restore archived files
git mv docs/archive/legacy_2025/*.md ./

# Remove new docs
rm docs/DEVELOPMENT_WORKFLOW.md
rm -rf docs/archive/legacy_2025/

# Reset to previous state
git reset --hard HEAD~1
```

---

## Success Metrics

| Metric | Before | After | Improvement |
|--------|---------|-------|-------------|
| Root .md files | ~140 | ~45 | 68% reduction |
| Obsolete docs | 95 | 0 | 100% cleaned |
| Source of truth docs | 0 | 1 | ✅ Created |
| django-tenants refs | 15+ | 0 | 100% removed |
| Developer confusion | High | Low | ✅ Clarified |

---

## Timeline

- **Preparation**: 2 hours (✅ Complete)
- **Execution**: 30 minutes
- **Validation**: 30 minutes
- **Team Communication**: 15 minutes
- **Total**: ~3.5 hours

---

## Next Steps

1. **Execute archival script**: `bash /tmp/archive_docs.sh`
2. **Verify results**: Check file counts and locations
3. **Update references**: Modify key documents to point to new source of truth
4. **Commit changes**: Use detailed commit message above
5. **Create PR**: For review before merging to development
6. **Announce**: Share with team once merged

---

## Questions & Answers

**Q: What if I need information from archived docs?**
A: Check `docs/archive/legacy_2025/README.md` for guidance. Most info is now in `DEVELOPMENT_WORKFLOW.md`.

**Q: Are archived docs deleted forever?**
A: No, they're in Git history and `docs/archive/legacy_2025/` for reference.

**Q: What if a workflow references an archived doc?**
A: The archival script doesn't modify workflows. We'll check and update references post-archive.

**Q: Can we delete archived docs completely?**
A: Not recommended. Keep for historical context (troubleshooting, understanding decisions).

---

**Ready to execute when approved.**
