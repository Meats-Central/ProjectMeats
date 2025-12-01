# ProjectMeats Documentation Index

**Last Updated**: 2025-11-29

## 📚 Purpose

This document serves as the central navigation hub for all ProjectMeats documentation. Use this index to quickly find the information you need.

---

## 🚀 Getting Started

**New to ProjectMeats? Start here:**

1. [README.md](../README.md) - Project overview and quick start
2. [QUICK_START.md](../QUICK_START.md) - 5-minute setup guide
3. [CONTRIBUTING.md](../CONTRIBUTING.md) - How to contribute
4. [.github/copilot-instructions.md](../.github/copilot-instructions.md) - **Essential** - Coding standards and best practices

---

## 📖 Core Documentation

### Architecture & Design

- [BACKEND_ARCHITECTURE.md](./BACKEND_ARCHITECTURE.md) - Django backend structure and patterns
- [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) - React frontend structure and patterns  
- [MULTI_TENANCY_GUIDE.md](./MULTI_TENANCY_GUIDE.md) - Multi-tenant architecture and implementation
- [../MULTI_TENANCY_IMPLEMENTATION.md](../MULTI_TENANCY_IMPLEMENTATION.md) - Detailed multi-tenancy setup

### Development Workflows

- [../branch-workflow-checklist.md](../branch-workflow-checklist.md) - Git workflow and branch management
- [REPOSITORY_BEST_PRACTICES.md](./REPOSITORY_BEST_PRACTICES.md) - Repository maintenance and standards
- [../CHANGELOG.md](../CHANGELOG.md) - Project changelog
- [../.github/copilot-instructions.md](../.github/copilot-instructions.md) - **Must read** - Complete development guidelines

### Testing

- [TESTING_STRATEGY.md](./TESTING_STRATEGY.md) - Comprehensive testing guide
- [../TESTING_GUIDE_WORKFLOW_FIX.md](../TESTING_GUIDE_WORKFLOW_FIX.md) - Testing workflow improvements

### Deployment

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [DEPLOYMENT_TROUBLESHOOTING.md](./DEPLOYMENT_TROUBLESHOOTING.md) - Troubleshooting common deployment issues
- [ENVIRONMENT_GUIDE.md](./ENVIRONMENT_GUIDE.md) - Environment configuration guide
- [../DEPLOYMENT_ENHANCEMENTS.md](../DEPLOYMENT_ENHANCEMENTS.md) - Recent deployment improvements

### Database & Migrations

- [MIGRATION_BEST_PRACTICES.md](./MIGRATION_BEST_PRACTICES.md) - **Critical** - Migration guidelines and troubleshooting
- [../MIGRATION_DEPENDENCIES_FIX_FINAL.md](../MIGRATION_DEPENDENCIES_FIX_FINAL.md) - Migration dependency best practices
- [../MIGRATION_FIX_SUMMARY.md](../MIGRATION_FIX_SUMMARY.md) - Common migration issues and solutions
- [../POSTGRESQL_MIGRATION_GUIDE.md](../POSTGRESQL_MIGRATION_GUIDE.md) - PostgreSQL-specific guidance

### Security & Permissions

- [../TENANT_ACCESS_CONTROL.md](../TENANT_ACCESS_CONTROL.md) - Tenant-based access control
- [../AUTHENTICATION_EXPLANATION.md](../AUTHENTICATION_EXPLANATION.md) - Authentication system overview
- [../GUEST_MODE_IMPLEMENTATION.md](../GUEST_MODE_IMPLEMENTATION.md) - Guest mode and permissions
- [../INVITE_ONLY_SYSTEM.md](../INVITE_ONLY_SYSTEM.md) - Invitation system documentation

### Data & Models

- [DATA_GUIDE.md](./DATA_GUIDE.md) - Data model overview
- [DATA_MODEL_ENHANCEMENTS.md](./DATA_MODEL_ENHANCEMENTS.md) - Recent model enhancements
- [environment-variables.md](./environment-variables.md) - Environment variable reference

### UI/UX

- [UI_ENHANCEMENTS.md](./UI_ENHANCEMENTS.md) - UI enhancement details
- [UI_UX_ENHANCEMENTS.md](./UI_UX_ENHANCEMENTS.md) - UX improvements
- [../FRONTEND_MULTI_TENANCY_SUMMARY.md](../FRONTEND_MULTI_TENANCY_SUMMARY.md) - Frontend multi-tenancy

---

##  🔧 Implementation Summaries

Detailed implementation notes for specific features and fixes:

- [implementation-summaries/allowed-hosts-fix.md](./implementation-summaries/allowed-hosts-fix.md)
- [implementation-summaries/backend-audit-cleanup.md](./implementation-summaries/backend-audit-cleanup.md)
- [implementation-summaries/dashboard-enhancement.md](./implementation-summaries/dashboard-enhancement.md)
- [implementation-summaries/deployment-optimization.md](./implementation-summaries/deployment-optimization.md)
- [implementation-summaries/dev-auth-bypass-fix.md](./implementation-summaries/dev-auth-bypass-fix.md)
- [implementation-summaries/repository-refactoring-phase-1.md](./implementation-summaries/repository-refactoring-phase-1.md)

**Root-level implementation summaries** (archived as of December 2025):
- See `archived/docs/2025-fixes/implementation-summaries/` for historical implementation summaries including:
  - IMPLEMENTATION_SUMMARY.md
  - IMPLEMENTATION_SUMMARY_AUTH_FIX.md  
  - IMPLEMENTATION_SUMMARY_GUEST_MODE.md
  - IMPLEMENTATION_SUMMARY_INVITE_SYSTEM.md
  - IMPLEMENTATION_SUMMARY_MIGRATION_FIX.md
  - IMPLEMENTATION_SUMMARY_NAMING_STANDARDS.md
  - IMPLEMENTATION_SUMMARY_PO_VERSION_HISTORY.md
  - IMPLEMENTATION_SUMMARY_STAGING_FIX.md (now in deployments category)
  - IMPLEMENTATION_VERIFICATION.md

---

## 🔍 Reference Documentation

### Workflows & CI/CD

- [workflows/CICD-workflow.md](./workflows/CICD-workflow.md) - CI/CD pipeline documentation
- [workflows/cicd-infrastructure.md](./workflows/cicd-infrastructure.md) - Infrastructure as code
- [workflows/database-backup.md](./workflows/database-backup.md) - Backup procedures

### Technical References

- [reference/deployment-technical-reference.md](./reference/deployment-technical-reference.md) - Deployment technical details
- [TODO_LOG.md](./TODO_LOG.md) - Tracked TODOs and future work

### Research & Best Practices

- [research/platform-core/monorepo-best-practices.md](./research/platform-core/monorepo-best-practices.md)

---

## 🗃️ Archived Fix Documentation (December 2025)

**Note**: These documents have been archived to `archived/docs/2025-fixes/` to keep the root directory clean. All content is preserved for historical reference.

For the most current troubleshooting guidance, see:
- [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) - Database migration best practices
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues and solutions
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Deployment procedures

### Archived Categories

All fix documentation has been organized into 12 categories in `archived/docs/2025-fixes/`:

1. **Migrations** (17 files) - Database migration fixes and django-tenants issues
2. **Deployments** (14 files) - Deployment configuration and staging environment fixes
3. **Authentication** (20 files) - Superuser, guest mode, and permissions fixes
4. **Suppliers/Customers** (6 files) - Supplier and customer management fixes
5. **Workflows** (3 files) - CI/CD workflow and testing fixes
6. **Branch Protection** (3 files) - Branch protection and divergence resolution
7. **GitHub Issues** (2 files) - Specific GitHub issue resolutions
8. **PR Docs** (1 file) - Pull request documentation
9. **Multi-Tenancy** (3 files) - Multi-tenant architecture enhancements
10. **Fixes** (2 files) - UI and tenant-specific fixes
11. **Implementation Summaries** (6 files) - Feature implementation details
12. **Reorganization** (1 file) - Previous reorganization documentation

See [../archived/docs/2025-fixes/README.md](../archived/docs/2025-fixes/README.md) for complete archive index and file listings.

---

## 📝 Internal Logs & Tracking

- [../copilot-log.md](../copilot-log.md) - Copilot task history and lessons learned
- [TODO_LOG.md](./TODO_LOG.md) - Future work and improvements
- [CLEANUP_CHECKLIST.md](./CLEANUP_CHECKLIST.md) - Repository cleanup tasks
- [REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md) - Refactoring documentation
- [REPO_AUDIT_PLATFORM_CORE.md](./REPO_AUDIT_PLATFORM_CORE.md) - Repository audit notes
- [DEPLOYMENT_EFFICIENCY_REVIEW_SUMMARY.md](./DEPLOYMENT_EFFICIENCY_REVIEW_SUMMARY.md) - Deployment efficiency analysis

---

## 🗂️ Archival Status (Updated December 2025)

**✅ Major documentation archival completed!**

### What Was Archived

On December 1, 2025, **78 historical documentation files** were moved from the root directory to organized categories in `archived/docs/2025-fixes/`:

1. ✅ All `*_FIX_SUMMARY.md` files (specific bug fixes)
2. ✅ All `GITHUB_ISSUE_*.md` files (GitHub-specific issue resolutions)
3. ✅ All `PR_SUMMARY_*.md` and `PR_DESCRIPTION_*.md` files (PR-specific documentation)
4. ✅ All implementation summaries from root directory
5. ✅ Migration, deployment, authentication, and other fix documentation

**Results:**
- Root directory reduced from **85 to 7 essential markdown files**
- All content organized into **12 categories**
- Complete archive index created at `archived/docs/2025-fixes/README.md`
- All cross-references updated

### Current Status

**Root directory now contains only essential files:**
- README.md - Project overview
- CONTRIBUTING.md - Contribution guidelines  
- CHANGELOG.md - Version history
- QUICK_START.md - Quick setup guide
- LOCAL_DEVELOPMENT.md - Development setup
- branch-workflow-checklist.md - Git workflow
- copilot-log.md - Copilot task history

**For historical documentation, see:**
- [archived/docs/2025-fixes/README.md](../archived/docs/2025-fixes/README.md) - Complete archive index

### Future Archival

Going forward, any new fix or issue-specific documentation should:
1. Be created in appropriate docs/ subdirectories
2. Be archived after 3-6 months of stability
3. Follow the established categorization pattern

---

## 🔄 Documentation Maintenance

### Ownership

- **Core Documentation**: Maintained by core team
- **Implementation Summaries**: Created by feature developers, reviewed by core team
- **Fix Documentation**: Created by fix authors, archived after 3+ months of stability

### Update Guidelines

1. **Always update** `.github/copilot-instructions.md` for coding standard changes
2. **Keep current** DEPLOYMENT_GUIDE.md and TESTING_STRATEGY.md
3. **Archive old** fix documentation after verification
4. **Cross-reference** related documents
5. **Date updates** with "Last Updated" sections

### Review Schedule

- **Weekly**: Check for new root-level docs that should be organized
- **Monthly**: Review implementation summaries for archival
- **Quarterly**: Audit all documentation for accuracy and relevance
- **Annually**: Major documentation reorganization if needed

---

## 📞 Getting Help

- **Development Questions**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Deployment Issues**: See [DEPLOYMENT_TROUBLESHOOTING.md](./DEPLOYMENT_TROUBLESHOOTING.md)
- **Migration Problems**: See [MIGRATION_BEST_PRACTICES.md](./MIGRATION_BEST_PRACTICES.md)
- **Testing Help**: See [TESTING_STRATEGY.md](./TESTING_STRATEGY.md)
- **General Questions**: Check [copilot-log.md](../copilot-log.md) for similar issues

---

## 🔗 Quick Links

- **GitHub Repository**: https://github.com/Meats-Central/ProjectMeats (verified current repository)
- **Deployment Environments**:
  - Development: dev.meatscentral.com
  - UAT: uat.meatscentral.com
  - Production: (TBD)

---

**Documentation Version**: 2.0.0 (Major reorganization)  
**Last Reviewed**: 2025-12-01  
**Next Review Due**: 2026-03-01

