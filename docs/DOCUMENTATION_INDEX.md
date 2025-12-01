# ProjectMeats Documentation Index

**Last Updated**: 2025-11-29

## 📚 Purpose

This document serves as the central navigation hub for all ProjectMeats documentation. Use this index to quickly find the information you need.

---

## 🚀 Getting Started

**New to ProjectMeats? Start here:**

1. [README.md](../README.md) - Project overview and quick start
2. [QUICK_START.md](../QUICK_START.md) - 5-minute setup guide
3. [PROJECT_SPECIFIC_CONVENTIONS.md](./PROJECT_SPECIFIC_CONVENTIONS.md) - **⭐ ESSENTIAL** - Unique patterns that differ from standard Django/React
4. [CONTRIBUTING.md](../CONTRIBUTING.md) - How to contribute
5. [.github/copilot-instructions.md](../.github/copilot-instructions.md) - **Essential** - Coding standards and best practices

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

**Root-level implementation summaries** (should be reviewed for archival):
- [../IMPLEMENTATION_SUMMARY.md](../IMPLEMENTATION_SUMMARY.md)
- [../IMPLEMENTATION_SUMMARY_AUTH_FIX.md](../IMPLEMENTATION_SUMMARY_AUTH_FIX.md)
- [../IMPLEMENTATION_SUMMARY_GUEST_MODE.md](../IMPLEMENTATION_SUMMARY_GUEST_MODE.md)
- [../IMPLEMENTATION_SUMMARY_INVITE_SYSTEM.md](../IMPLEMENTATION_SUMMARY_INVITE_SYSTEM.md)
- [../IMPLEMENTATION_SUMMARY_MIGRATION_FIX.md](../IMPLEMENTATION_SUMMARY_MIGRATION_FIX.md)
- [../IMPLEMENTATION_SUMMARY_NAMING_STANDARDS.md](../IMPLEMENTATION_SUMMARY_NAMING_STANDARDS.md)
- [../IMPLEMENTATION_SUMMARY_PO_VERSION_HISTORY.md](../IMPLEMENTATION_SUMMARY_PO_VERSION_HISTORY.md)
- [../IMPLEMENTATION_SUMMARY_STAGING_FIX.md](../IMPLEMENTATION_SUMMARY_STAGING_FIX.md)
- [../IMPLEMENTATION_VERIFICATION.md](../IMPLEMENTATION_VERIFICATION.md)

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

## 🗃️ Issue-Specific Fix Documentation

**Note**: These documents capture specific bug fixes and should eventually be archived after the fixes are stable.

### Migration & Database Fixes

- [../CICD_DJANGO_TENANTS_FIX.md](../CICD_DJANGO_TENANTS_FIX.md)
- [../DB_CONFIG_MIGRATION_IDEMPOTENCY_FIX.md](../DB_CONFIG_MIGRATION_IDEMPOTENCY_FIX.md)
- [../DEV_WORKFLOW_MIGRATION_DOCKER_FIX.md](../DEV_WORKFLOW_MIGRATION_DOCKER_FIX.md)
- [../DJANGO_TENANTS_ALIGNMENT.md](../DJANGO_TENANTS_ALIGNMENT.md)
- [../DJANGO_TENANTS_CI_FIX_COMPREHENSIVE.md](../DJANGO_TENANTS_CI_FIX_COMPREHENSIVE.md)
- [../GITHUB_ISSUE_DEV_DB_ENGINE_FIX.md](../GITHUB_ISSUE_DEV_DB_ENGINE_FIX.md)
- [../GITHUB_ISSUE_MIGRATION_HISTORY_FIX.md](../GITHUB_ISSUE_MIGRATION_HISTORY_FIX.md)
- [../GITHUB_ISSUE_MISSING_TABLES_FIX.md](../GITHUB_ISSUE_MISSING_TABLES_FIX.md)
- [../MIGRATION_FIX_DUPLICATE_DOMAIN_TABLE.md](../MIGRATION_FIX_DUPLICATE_DOMAIN_TABLE.md)
- [../MIGRATION_FIX_PR135_CORRECTION.md](../MIGRATION_FIX_PR135_CORRECTION.md)
- [../MIGRATION_FIX_SUMMARY_QUICK.md](../MIGRATION_FIX_SUMMARY_QUICK.md)
- [../MIGRATION_HISTORY_FIX.md](../MIGRATION_HISTORY_FIX.md)
- [../MIGRATION_DEPENDENCY_FIX_2025-10-13.md](../MIGRATION_DEPENDENCY_FIX_2025-10-13.md)
- [../MODEL_DEFAULTS_AUDIT_SUMMARY.md](../MODEL_DEFAULTS_AUDIT_SUMMARY.md)
- [../MODEL_DEFAULTS_MIGRATION_GUIDE.md](../MODEL_DEFAULTS_MIGRATION_GUIDE.md)

### Deployment & Configuration Fixes

- [../DEPLOYMENT_FIX_SUMMARY.md](../DEPLOYMENT_FIX_SUMMARY.md)
- [../GITHUB_ISSUE_STAGING_SECRETS.md](../GITHUB_ISSUE_STAGING_SECRETS.md)
- [../STAGING_LOAD_FAILURE_FIX.md](../STAGING_LOAD_FAILURE_FIX.md)
- [../README_STAGING_FIX.md](../README_STAGING_FIX.md)
- [../SECURITY_SUMMARY_STAGING_FIX.md](../SECURITY_SUMMARY_STAGING_FIX.md)
- [../UAT_SUPERUSER_FIX_SUMMARY.md](../UAT_SUPERUSER_FIX_SUMMARY.md)

### Authentication & Permissions Fixes

- [../DELETE_BUTTON_FIX_SUMMARY.md](../DELETE_BUTTON_FIX_SUMMARY.md)
- [../DJANGO_ADMIN_PERMISSIONS_FIX_SUMMARY.md](../DJANGO_ADMIN_PERMISSIONS_FIX_SUMMARY.md)
- [../DJANGO_STAFF_PERMISSIONS_EXPLAINED.md](../DJANGO_STAFF_PERMISSIONS_EXPLAINED.md)
- [../GUEST_MODE_QUICK_REF.md](../GUEST_MODE_QUICK_REF.md)
- [../GUEST_USER_PERMISSIONS_GUIDE.md](../GUEST_USER_PERMISSIONS_GUIDE.md)
- [../MULTI_TENANCY_ENHANCEMENT_SUMMARY.md](../MULTI_TENANCY_ENHANCEMENT_SUMMARY.md)
- [../TENANT_VALIDATION_FIX_SUMMARY.md](../TENANT_VALIDATION_FIX_SUMMARY.md)

### Superuser & Environment Fixes

- [../GITHUB_ISSUE_SUPERUSER_ENV_LOADING.md](../GITHUB_ISSUE_SUPERUSER_ENV_LOADING.md)
- [../PR_SUMMARY_SUPERUSER_FIX.md](../PR_SUMMARY_SUPERUSER_FIX.md)
- [../SUPERUSER_DUPLICATE_FIX_SUMMARY.md](../SUPERUSER_DUPLICATE_FIX_SUMMARY.md)
- [../SUPERUSER_ENVIRONMENT_VARIABLES_FIX.md](../SUPERUSER_ENVIRONMENT_VARIABLES_FIX.md)
- [../SUPERUSER_INTEGRATION_SUMMARY.md](../SUPERUSER_INTEGRATION_SUMMARY.md)
- [../SUPERUSER_PASSWORD_SYNC_FIX.md](../SUPERUSER_PASSWORD_SYNC_FIX.md)
- [../SUPERUSER_PASSWORD_SYNC_SUMMARY.md](../SUPERUSER_PASSWORD_SYNC_SUMMARY.md)
- [../SUPER_TENANT_FIX_SUMMARY.md](../SUPER_TENANT_FIX_SUMMARY.md)

### Supplier & Customer Fixes

- [../SUPPLIER_ADMIN_UPDATE_VERIFICATION.md](../SUPPLIER_ADMIN_UPDATE_VERIFICATION.md)
- [../SUPPLIER_CUSTOMER_500_ERROR_FIX.md](../SUPPLIER_CUSTOMER_500_ERROR_FIX.md)
- [../SUPPLIER_CUSTOMER_TENANT_FALLBACK_FIX.md](../SUPPLIER_CUSTOMER_TENANT_FALLBACK_FIX.md)
- [../SUPPLIER_FIX_VERIFICATION.md](../SUPPLIER_FIX_VERIFICATION.md)
- [../SUPPLIER_NETWORK_ERROR_FIX_SUMMARY.md](../SUPPLIER_NETWORK_ERROR_FIX_SUMMARY.md)
- [../NETWORK_ERROR_TROUBLESHOOTING.md](../NETWORK_ERROR_TROUBLESHOOTING.md)

### Workflow & CI/CD Fixes

- [../PR_SUMMARY_BASH_HEREDOC_FIX.md](../PR_SUMMARY_BASH_HEREDOC_FIX.md)
- [../PSYCOPG_FIX.md](../PSYCOPG_FIX.md)
- [../WORKFLOW_MIGRATIONS_FIX_SUMMARY.md](../WORKFLOW_MIGRATIONS_FIX_SUMMARY.md)
- [../WORKFLOW_TRIGGER_FIX.md](../WORKFLOW_TRIGGER_FIX.md)

### Pull Request Descriptions

- [../PR_DESCRIPTION_INVITE_GUEST_MODE.md](../PR_DESCRIPTION_INVITE_GUEST_MODE.md)

---

## 📝 Internal Logs & Tracking

- [../copilot-log.md](../copilot-log.md) - Copilot task history and lessons learned
- [TODO_LOG.md](./TODO_LOG.md) - Future work and improvements
- [CLEANUP_CHECKLIST.md](./CLEANUP_CHECKLIST.md) - Repository cleanup tasks
- [REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md) - Refactoring documentation
- [REPO_AUDIT_PLATFORM_CORE.md](./REPO_AUDIT_PLATFORM_CORE.md) - Repository audit notes
- [DEPLOYMENT_EFFICIENCY_REVIEW_SUMMARY.md](./DEPLOYMENT_EFFICIENCY_REVIEW_SUMMARY.md) - Deployment efficiency analysis

---

## 🗂️ Archive Candidates

**These documents are valuable historical records but may not be actively needed:**

### Suggested for Archival

The following documents capture point-in-time fixes and may be candidates for moving to `archived/docs/fixes/` once the fixes are verified stable in production:

1. All `*_FIX_SUMMARY.md` files (capture specific bug fixes)
2. All `GITHUB_ISSUE_*.md` files (GitHub-specific issue resolutions)
3. All `PR_SUMMARY_*.md` and `PR_DESCRIPTION_*.md` files (PR-specific documentation)
4. Duplicate/overlapping implementation summaries in root vs docs/implementation-summaries/

**Archival Benefits:**
- Cleaner root directory
- Easier navigation for active development
- Historical record preserved for future reference
- Reduced documentation maintenance burden

**Archival Process:**
1. Move to `archived/docs/fixes/<year>-<month>/`
2. Update any cross-references
3. Add entry to `archived/docs/INDEX.md`

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

**Documentation Version**: 1.0.0  
**Last Reviewed**: 2025-11-29  
**Next Review Due**: 2026-02-28

