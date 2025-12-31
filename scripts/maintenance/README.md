# Maintenance Scripts

This directory contains utility scripts for maintenance, debugging, and one-off fixes.

## Purpose

These scripts are used for:
- Database maintenance and migrations
- Configuration fixes
- System verification and health checks
- Deployment troubleshooting
- Repository maintenance

## Scripts

### Database & Migration
- `fix_duplicate_tenant_migrations.sh` - Fix duplicate tenant migration issues
- `fix_migration_state.sh` - Repair migration state inconsistencies
- `setup-db-secrets.sh` - Configure database secrets

### Configuration & Setup
- `fix_dev_domain.py` - Fix development domain configuration
- `setup-ssl.sh` - SSL certificate setup
- `setup-db-secrets.sh` - Database secret configuration

### Deployment & Infrastructure
- `apply_deployment_fixes.sh` - Apply deployment fixes
- `query_remote_accounts.sh` - Query remote account information
- `get-github-actions-ips.sh` - Get GitHub Actions IP ranges

### Monitoring & Verification
- `monitor_branch_health.sh` - Monitor branch health status
- `monitor_phase2_health.sh` - Phase 2 health monitoring
- `verify_dev_env.sh` - Verify development environment
- `verify_golden_state.sh` - Verify golden state configuration
- `verify_staging_config.py` - Verify staging configuration

### Code Quality & Analysis
- `remove_debug_logging.py` - Remove debug logging statements
- `lint-docker-ports.sh` - Lint Docker port configurations
- `query_accounts_summary.py` - Query and summarize account data

### Repository Management
- `close_old_prs.sh` - Close old/stale pull requests
- `simplify_workflows.sh` - Simplify GitHub workflow files

## Usage

Most scripts are designed for one-time or occasional use during maintenance windows or troubleshooting sessions. Review each script's internal documentation before use.

**Warning**: Some scripts modify production state. Always test in development first.
