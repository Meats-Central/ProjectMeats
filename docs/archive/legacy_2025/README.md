# Legacy Documentation Archive

**Archive Date:** 2025-12-09  
**Reason:** Transition to Shared-Schema Multi-Tenancy Architecture

---

## About This Archive

This directory contains documentation from the project's transition period when migrating from django-tenants schema-based multi-tenancy to shared-schema row-level security architecture.

**These documents are kept for historical reference only and should NOT be used for current development.**

---

## Current Documentation

For up-to-date development workflows and architecture, see:
- **[DEVELOPMENT_WORKFLOW.md](../DEVELOPMENT_WORKFLOW.md)** - Single source of truth for pipelines
- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Current system architecture
- **[DEPLOYMENT_RUNBOOK.md](../DEPLOYMENT_RUNBOOK.md)** - Operational procedures

---

## What Changed?

### Old Architecture (Archived)
- ❌ django-tenants with separate PostgreSQL schemas per tenant
- ❌ `migrate_schemas` command for migrations
- ❌ `TenantMixin`, `DomainMixin` models
- ❌ `schema_context()` for tenant isolation
- ❌ Separate public/tenant schemas

### New Architecture (Current)
- ✅ Shared-schema multi-tenancy with `tenant_id` ForeignKey
- ✅ Standard Django `migrate` command
- ✅ Standard Django models with tenant field
- ✅ QuerySet filtering: `filter(tenant=request.tenant)`
- ✅ Single PostgreSQL `public` schema

---

## Archived Categories

### Multi-Tenancy Implementation Docs
Files describing the old django-tenants architecture:
- `MULTI_TENANCY_IMPLEMENTATION.md`
- `PHASE1_ARCHITECTURAL_PURGE_COMPLETE.md`
- `PHASE2_MULTI_TENANCY_ISOLATION_IMPLEMENTATION.md`
- `SCHEMA_ISOLATION_MIGRATION_COMPLETE.md`

### Deployment Evolution Docs
Incremental fixes and improvements (now consolidated):
- `DEPLOYMENT_FIX_SUMMARY.md`
- `DEPLOYMENT_WORKFLOW_OPTIMIZATION.md`
- `GOLDEN_PIPELINE_REFERENCE.md`
- E2E testing summaries

### Specific Bug Fixes
Historical issue resolutions (for reference only):
- Django admin permissions fixes
- Migration dependency fixes
- SSH connection fixes
- Superuser integration fixes

---

## Using Archived Documentation

⚠️ **Warning:** Commands and procedures in these documents may be **outdated or incorrect** for the current architecture.

**Before using any archived information:**
1. Check if an equivalent exists in current documentation
2. Verify compatibility with shared-schema architecture
3. Test in development environment first
4. Consult with team lead if unsure

---

## Questions?

If you need information not covered in current documentation:
1. Check this archive for historical context
2. Review Git history for implementation details
3. Ask in #projectmeats-dev Slack channel
4. Open a documentation improvement issue

---

*Last Updated: 2025-12-09*
