# GitHub Actions Workflows

This directory contains all GitHub Actions workflows for the ProjectMeats repository.

## Deployment Workflows (1x series)

These workflows handle building, testing, and deploying the application to different environments:

### 11-dev-deployment.yml
- **Trigger**: Push to `development` branch
- **Environment**: Development
- **Purpose**: Deploys to dev environment after building and testing
- **Gates**:
  - Frontend build & tests
  - Backend build & tests
  - Docker image builds

### 12-uat-deployment.yml
- **Trigger**: Push to `uat` branch
- **Environment**: UAT (User Acceptance Testing) - uat.meatscentral.com
- **Purpose**: Deploys to UAT environment for stakeholder testing
- **Note**: UAT is the active middle environment per pipeline. staging.meatscentral.com is DEPRECATED.
- **Gates**:
  - Frontend build & tests
  - Backend build & tests
  - Docker image builds

### 13-prod-deployment.yml
- **Trigger**: Push to `main` branch
- **Environment**: Production
- **Purpose**: Deploys to production environment
- **Gates**:
  - Frontend build & tests
  - Backend build & tests
  - Docker image builds
  - Environment protection rules (manual approval)

## Database Workflows (2x series)

### 21-db-backup-restore-do.yml
- **Trigger**: Scheduled or manual
- **Purpose**: Manages database backups and restoration on DigitalOcean

## Planner Workflows (3x series)

These workflows help with project management and automation:

### 31-planner-auto-add-issue.yml
- **Purpose**: Automatically adds new issues to project boards

### 32-planner-Auto-Assign-to-Copilot.yml
- **Purpose**: Auto-assigns certain issues to Copilot for automated handling

### 33-planner-review-and-test
- **Purpose**: Automated review and test planning

### 34-planner-sprint-gen.yml
- **Purpose**: Sprint generation and planning automation

## Auto-Promotion Workflows (4x series)

These workflows automate PR creation between environments while enforcing CI/CD gates:

### 41-auto-promote-dev-to-uat.yml
- **Trigger**: After successful `11-dev-deployment.yml` completion
- **Purpose**: Creates PR from `development` → `uat`
- **Process**:
  1. Triggered when dev deployment succeeds
  2. Checks if PR already exists
  3. Creates PR with comprehensive checklist
  4. PR must pass all UAT deployment gates before merge
- **Gates Enforced**:
  - All checks from `12-uat-deployment.yml` must pass
  - Manual review required
  - CI/CD tests must pass

### 42-auto-promote-uat-to-main.yml
- **Trigger**: After successful `12-uat-deployment.yml` completion
- **Purpose**: Creates PR from `uat` → `main`
- **Process**:
  1. Triggered when UAT deployment succeeds
  2. Checks if PR already exists
  3. Creates PR with comprehensive checklist
  4. PR must pass all production deployment gates before merge
- **Gates Enforced**:
  - All checks from `13-prod-deployment.yml` must pass
  - Manual review required
  - Environment protection (production approval)
  - CI/CD tests must pass

**Important**: Auto-promotion workflows create PRs but do NOT bypass any gates. All deployment workflows run when PRs are created, and all tests must pass before merge is allowed.

## Cleanup Workflows (5x series)

### 51-cleanup-branches-tags.yml
- **Trigger**: Weekly (Sundays at 2 AM UTC) or manual
- **Purpose**: Maintains repository hygiene by cleaning up stale branches and tags
- **Features**:
  - Deletes merged branches
  - Removes stale feature branches (90+ days old)
  - Cleans up old Copilot branches (30+ days, no open PRs)
  - Keeps only last 10 pre-release tags per type
  - Protects main/uat/development branches
  - Never deletes branches with open PRs

## Validation Workflows (6x series)

These workflows enforce naming conventions and best practices:

### validate-branch-name.yml
- **Trigger**: On PR open, edit, or sync
- **Purpose**: Validates branch naming conventions
- **Validates**:
  - Branch follows `<type>/<description>` format
  - Type is from approved list (feature, fix, chore, refactor, hotfix, etc.)
  - Description uses lowercase and hyphens only
  - Protected branches (main, uat, development) are exempt
- **On Failure**: Posts helpful comment on PR with examples and guidance

### validate-pr-title.yml
- **Trigger**: On PR open, edit, or sync
- **Purpose**: Validates PR titles follow Conventional Commits
- **Validates**:
  - Title follows `<type>(<scope>): <description>` format
  - Type is from approved list (feat, fix, docs, chore, etc.)
  - Description is lowercase and properly formatted
  - Auto-promotion PRs are exempt
- **On Failure**: Posts helpful comment with format requirements and examples

### validate-tag-name.yml
- **Trigger**: On tag push
- **Purpose**: Validates tag naming and automates release creation
- **Validates**:
  - Production releases follow semantic versioning (v1.0.0)
  - Pre-release tags are properly formatted (v1.0.0-alpha.1)
  - Environment tags are valid (v1.0.0-dev, v1.0.0-uat)
- **On Success**: 
  - Auto-creates GitHub Release for production tags
  - Auto-creates Pre-Release for alpha/beta/rc tags
- **On Failure**: Provides guidance on proper tag formats

## Workflow Naming Convention

Workflows are numbered in series:
- **1x**: Deployment workflows
- **2x**: Database workflows
- **3x**: Planner/automation workflows
- **4x**: Auto-promotion workflows
- **5x**: Cleanup/maintenance workflows
- **6x**: Validation workflows (naming conventions, standards)
- **Standalone**: Promotion workflows (promote-dev-to-uat.yml, promote-uat-to-main.yml)

## CI/CD Flow

```
development branch
      ↓
[11-dev-deployment.yml] ← Builds, tests, deploys to dev
      ↓ (on success)
[41-auto-promote-dev-to-uat.yml] ← Creates PR to uat
      ↓ (manual merge)
uat branch
      ↓
[12-uat-deployment.yml] ← Builds, tests, deploys to UAT
      ↓ (on success)
[42-auto-promote-uat-to-main.yml] ← Creates PR to main
      ↓ (manual approval + merge)
main branch
      ↓
[13-prod-deployment.yml] ← Builds, tests, deploys to production
```

## Key Principles

1. **No Gate Bypassing**: Auto-promotion workflows create PRs that must pass all CI/CD gates
2. **Manual Review**: All promotions require human review and approval
3. **Environment Protection**: Production deployments require explicit approval
4. **Test Enforcement**: All tests must pass before any deployment
5. **Rollback Safety**: All deployments include health checks and can be rolled back

## CODEOWNERS Integration

The `.github/CODEOWNERS` file defines ownership for different parts of the codebase:
- Auto-promotion workflows require senior team approval
- Deployment workflows require DevOps team review
- Security-sensitive files require security team review

## Pull Request Template

The enhanced PR template (`.github/PULL_REQUEST_TEMPLATE.md`) provides:
- Comprehensive checklist for all PR types
- Security considerations
- Testing requirements
- Deployment notes
- Rollback procedures

## Troubleshooting

### PR Not Created
- Check if PR already exists (workflows skip if PR is open)
- Verify deployment workflow succeeded
- Check workflow run logs

### Deployment Failed
- Review job logs in GitHub Actions
- Check environment secrets are configured
- Verify Docker image builds succeeded

### Branch Not Deleted
- Check if branch has open PR (protected from deletion)
- Verify branch is not in protected list
- Check branch age meets cleanup criteria

## Manual Triggers

All workflows can be manually triggered via GitHub Actions UI using `workflow_dispatch`.

## Security

- All workflows use GitHub Actions permissions scoping
- Secrets are managed through GitHub Secrets
- CODEOWNERS enforces review requirements
- Production deployments require environment approval
