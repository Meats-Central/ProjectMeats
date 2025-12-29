# Archived Workflows

This directory contains deprecated GitHub Actions workflows that are no longer part of the **Golden Pipeline** architecture.

## Archive Date
December 29, 2025

## Reason for Archival
These workflows were superseded by the Golden Pipeline implementation, which consolidates deployment logic into:
- `main-pipeline.yml` - Master deployment pipeline
- `reusable-deploy.yml` - Reusable deployment worker
- `99-ops-management-command.yml` - Operations management commands

## Archived Workflows

### Deprecated Deployment Workflows

| Workflow | Reason for Archival |
|----------|---------------------|
| `pipeline-orchestrator.yml` | Superseded by `main-pipeline.yml` |
| `build-dev-image.yml` | Not part of Golden Pipeline deployment flow |

### Utility Workflows

| Workflow | Reason for Archival |
|----------|---------------------|
| `copilot-setup-steps.yml` | Setup utility, not part of deployment pipeline |
| `docs-lint.yml` | Can be integrated into PR checks if needed |
| `validate-immutable-tags.yml` | Validation should be in main pipeline |
| `21-db-backup-restore-do.yml` | Manual operation, not automated deployment |

## Active Workflows (Not Archived)

The following workflows remain active:

### Golden Pipeline
- **main-pipeline.yml** - Master deployment orchestrator
- **reusable-deploy.yml** - Reusable deployment worker
- **99-ops-management-command.yml** - Operations command runner

### Maintenance & Utilities
- **51-cleanup-branches-tags.yml** - Automated branch cleanup
- **workflow-retention-policy.yml** - Artifact retention management
- **automated-workflow-deletion.yml** - Workflow run cleanup
- **workflow-health-monitor.yml** - Repository health monitoring

## Restoration

If you need to restore any of these workflows:

1. **Review the workflow** - Ensure it's still needed and compatible
2. **Update to current standards** - Follow Golden Pipeline patterns
3. **Test thoroughly** - Verify against current architecture
4. **Document changes** - Update this README and relevant docs

## Related Documentation

- [GOLDEN_PIPELINE.md](../../../docs/GOLDEN_PIPELINE.md) - Current deployment architecture
- [CONTRIBUTING.md](../../../docs/CONTRIBUTING.md) - Contribution guidelines
- [Branch Workflow](../../../docs/branch-workflow-checklist.md) - Branch management

## Notes

- These workflows are **NOT automatically run** when in the archived/ directory
- Git history is preserved for all workflows
- Contact DevOps team if restoration is needed
- Consider if functionality can be integrated into existing Golden Pipeline workflows

---

**Last Updated**: December 29, 2025  
**Archive Policy**: Keep archived workflows for 90 days, then consider permanent deletion  
**Review Cycle**: Quarterly review of archived workflows
