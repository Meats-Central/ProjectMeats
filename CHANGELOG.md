# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **[MAJOR]** Comprehensive documentation consolidation (November 2024)
  - Created 4 new comprehensive guides consolidating 67 scattered documentation files:
    - `docs/MIGRATION_GUIDE.md` - Complete database migration guide (consolidates 12 docs)
    - `docs/AUTHENTICATION_GUIDE.md` - Authentication & permissions guide (consolidates 13 docs)
    - `docs/TROUBLESHOOTING.md` - Common issues and solutions (consolidates 14 docs)
    - `docs/lessons-learned/3-MONTH-RETROSPECTIVE.md` - 3-month development retrospective (consolidates 10 docs)
  - Archived all redundant documentation to `docs/archived-2024-11/` with complete cross-references
  - Updated `docs/README.md` with new structure and navigation
  - Cleaned root directory from 67 to 6 essential markdown files
  - **Impact:** Improved documentation discoverability, reduced duplication, single source of truth per topic
  - **For developers:** All old documentation references updated; use new consolidated guides
- Comprehensive final fix documentation in `MIGRATION_DEPENDENCIES_FIX_FINAL.md` (2025-10-16)
- Migration history fix documentation in `docs/MIGRATION_HISTORY_FIX.md` with step-by-step manual fix procedures
- CI/CD migration consistency validation using `makemigrations --check` and `migrate --plan`
- Comprehensive migration fix documentation in `MIGRATION_FIX_PR135_CORRECTION.md`

### Fixed
- **[CRITICAL]** Fixed RecursionError in deployment pipeline caused by psycopg3 incompatibility with django-tenants
  - Downgraded from `psycopg[binary]==3.2.9` (psycopg3) to `psycopg2-binary==2.9.9`
  - Fixes deployment failures in PRs #235, #240, #237 related to django-tenants integration
  - Root cause: django-tenants 3.5.0 has infinite recursion bug with psycopg3's cursor API
  - See `docs/archived-2024-11/troubleshooting/PSYCOPG_FIX.md` for detailed technical analysis
  - **Impact:** Enables successful database migrations in CI/CD with django-tenants
  - **Compatibility:** psycopg2-binary 2.9.9 is stable with Django 4.2.7, Python 3.12, PostgreSQL 15
  - **Future upgrade path:** django-tenants 3.7.0+ supports psycopg3 when we upgrade django-tenants
- **[DEFINITIVE FIX]** Resolved root cause of migration dependency issues from PR #126 (2025-10-16)
  - Simplified `purchase_orders.0004` dependencies to only structurally required migrations
  - Changed dependencies from latest migrations (0002/0004/0005/0006) to initial migrations (0001)
  - Eliminates all `InconsistentMigrationHistory` errors from deployment pipeline
  - Works for both fresh and existing database deployments
  - See `docs/archived-2024-11/migration/MIGRATION_DEPENDENCIES_FIX_FINAL.md` for comprehensive analysis
  - **Key insight:** Django auto-generates dependencies on latest migrations, but only structural dependencies should be declared
  - **Impact:** Prevents future migration ordering conflicts; safe for all environments
- **[CRITICAL]** Corrected migration dependency issue that was incorrectly "fixed" in PR #135
  - Reverted PR #135's incorrect change that caused deployment failures
  - Restored `purchase_orders.0004` dependency to `sales_orders.0002` (was incorrectly changed to 0001)
  - Fixes both errors:
    * "Migration purchase_orders.0004 is applied before its dependency carriers.0004"
    * "Migration purchase_orders.0004 is applied before its dependency sales_orders.0002"
  - Migration dependencies now match database history, eliminating `InconsistentMigrationHistory` errors
  - **Lesson learned:** Migration files are historical records - once deployed, dependencies cannot be changed
- ~~Fixed migration dependency issue~~ (PR #135 - THIS WAS INCORRECT, see above correction)
- Fixed inconsistent migration history blocking Dev and UAT deployments (migration `purchase_orders.0004` applied before dependency `suppliers.0006`)
- Added migration consistency checks to CI/CD pipeline to prevent future migration ordering issues
- Fixed SyntaxError in PurchaseOrder model due to duplicate keyword arguments in `total_amount` field definition (refs commit 4ed9474c280c95370953800838533462aed67a4b)
- Fixed corrupted migration file `0004_alter_purchaseorder_carrier_release_format_and_more.py` with duplicate model definitions
- Fixed syntax error in `tests.py` with unclosed docstring

### Changed
- **[DOCUMENTATION]** Reorganized documentation structure (November 2024)
  - Moved 67 scattered root-level markdown files to organized archive
  - Consolidated redundant documentation into comprehensive guides
  - Updated all internal documentation references to new locations
  - **Migration Path:** See `docs/archived-2024-11/README.md` for file mapping

## [Previous Versions]
See git history for changes prior to this changelog.
