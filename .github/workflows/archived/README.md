# Archived Workflows

This directory contains deprecated GitHub Actions workflows that are no longer part of the **Golden Pipeline** architecture.

## Archive Date
- December 29, 2025 (initial archival)
- December 29, 2025 (workflow consolidation)

## Reason for Archival
These workflows were superseded by the Golden Pipeline implementation, which consolidates deployment logic into:
- `main-pipeline.yml` - Master deployment pipeline (with integrated validation)
- `reusable-deploy.yml` - Reusable deployment worker
- `99-ops-management-command.yml` - Operations management commands
- `auto-pr.yml` - Automated PR creation for release promotion

## Archived Workflows

### Deleted (Consolidated into main-pipeline.yml)

| Workflow | Reason for Deletion | Integrated Into |
|----------|---------------------|-----------------|
| `copilot-setup-steps.yml` | Cruft - dummy setup validation | Deleted (no longer needed) |
| `docs-lint.yml` | Markdown linting for PRs | `main-pipeline.yml` (lint-docs job) |
| `validate-immutable-tags.yml` | Docker tag validation | `main-pipeline.yml` (check-docker-tags job) |

### Deprecated Deployment Workflows

| Workflow | Reason for Archival |
|----------|---------------------|
| `pipeline-orchestrator.yml` | Superseded by `main-pipeline.yml` |
| `build-dev-image.yml` | Not part of Golden Pipeline deployment flow |

### Maintenance Workflows (Optional - Archived for Simplicity)

| Workflow | Reason for Archival | Restoration Notes |
|----------|---------------------|-------------------|
| `51-cleanup-branches-tags.yml` | Optional maintenance | Can restore if automatic cleanup needed |
| `automated-workflow-deletion.yml` | Optional maintenance | Can restore for workflow run cleanup |
| `workflow-health-monitor.yml` | Optional monitoring | Can restore for health checks |
| `workflow-retention-policy.yml` | Optional cleanup | Can restore for artifact retention |

### Utility Workflows

| Workflow | Reason for Archival |
|----------|---------------------|
| `21-db-backup-restore-do.yml` | Manual operation, not automated deployment |

## Active Workflows (Not Archived)

The following 4 workflows remain active:

### Golden Pipeline (3)
- **main-pipeline.yml** - Master deployment orchestrator with integrated validation
  - Includes `lint-docs` job (from docs-lint.yml)
  - Includes `check-docker-tags` job (from validate-immutable-tags.yml)
  - Routes deployments to dev/uat/prod
- **reusable-deploy.yml** - Reusable deployment worker
- **99-ops-management-command.yml** - Operations command runner

### Automation (1)
- **auto-pr.yml** - Automated PR creation from development → uat

## Consolidation Benefits

### Before Consolidation (8 workflows)
- main-pipeline.yml
- reusable-deploy.yml
- 99-ops-management-command.yml
- auto-pr.yml
- docs-lint.yml
- validate-immutable-tags.yml
- 51-cleanup-branches-tags.yml
- automated-workflow-deletion.yml
- workflow-health-monitor.yml
- workflow-retention-policy.yml

### After Consolidation (4 workflows)
- main-pipeline.yml (with integrated validation)
- reusable-deploy.yml
- 99-ops-management-command.yml
- auto-pr.yml

**Result**: 60% reduction in workflow files (10 → 4)

### Benefits
- ✅ Cleaner GitHub Actions UI
- ✅ Fewer workflow runs to monitor
- ✅ Centralized validation in main pipeline
- ✅ Reduced maintenance overhead
- ✅ Faster CI/CD execution (parallel validation)

## Restoration

If you need to restore any of these workflows:

1. **Review the workflow** - Ensure it's still needed and compatible
2. **Update to current standards** - Follow Golden Pipeline patterns
3. **Test thoroughly** - Verify against current architecture
4. **Document changes** - Update this README and relevant docs

### Restoring Maintenance Workflows

If automatic cleanup is needed:
```bash
# Restore branch cleanup
cp archived/51-cleanup-branches-tags.yml ./

# Restore workflow retention
cp archived/workflow-retention-policy.yml ./
```

### Restoring Consolidated Jobs

The jobs from deleted workflows are now in `main-pipeline.yml`:
- **docs-lint.yml** → `lint-docs` job in main-pipeline.yml
- **validate-immutable-tags.yml** → `check-docker-tags` job in main-pipeline.yml

To disable these jobs without restoring the original workflows, modify `main-pipeline.yml` to skip the jobs.

## Related Documentation

- [GOLDEN_PIPELINE.md](../../../docs/GOLDEN_PIPELINE.md) - Current deployment architecture
- [CONTRIBUTING.md](../../../docs/CONTRIBUTING.md) - Contribution guidelines
- [Branch Workflow](../../../docs/branch-workflow-checklist.md) - Branch management
- [REPOSITORY_CLEANUP_SUMMARY.md](../../../docs/REPOSITORY_CLEANUP_SUMMARY.md) - Cleanup history

## Notes

- These workflows are **NOT automatically run** when in the archived/ directory
- Git history is preserved for all workflows
- Contact DevOps team if restoration is needed
- Consider if functionality can be integrated into existing Golden Pipeline workflows

---

**Last Updated**: December 29, 2025  
**Archive Policy**: Keep archived workflows for 90 days, then consider permanent deletion  
**Review Cycle**: Quarterly review of archived workflows  
**Active Workflows**: 4 (main-pipeline, reusable-deploy, ops-command, auto-pr)
