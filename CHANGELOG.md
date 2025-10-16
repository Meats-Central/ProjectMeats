# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Fixed migration dependency issue causing `InconsistentMigrationHistory` error in deployment pipeline
  - Changed `purchase_orders.0004` dependency from `sales_orders.0002` to `sales_orders.0001`
  - Resolved error: "Migration purchase_orders.0004 is applied before its dependency sales_orders.0002"
  - GitHub Actions run: https://github.com/Meats-Central/ProjectMeats/actions/runs/18547306185/job/52867765684
- Fixed inconsistent migration history blocking Dev and UAT deployments (migration `purchase_orders.0004` applied before dependency `suppliers.0006`)
- Added migration consistency checks to CI/CD pipeline to prevent future migration ordering issues
- Fixed SyntaxError in PurchaseOrder model due to duplicate keyword arguments in `total_amount` field definition (refs commit 4ed9474c280c95370953800838533462aed67a4b)
- Fixed corrupted migration file `0004_alter_purchaseorder_carrier_release_format_and_more.py` with duplicate model definitions
- Fixed syntax error in `tests.py` with unclosed docstring

### Added
- Migration history fix documentation in `docs/MIGRATION_HISTORY_FIX.md` with step-by-step manual fix procedures
- CI/CD migration consistency validation using `makemigrations --check` and `migrate --plan`

## [Previous Versions]
See git history for changes prior to this changelog.
