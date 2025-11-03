# Auto-Promotion Workflow Trigger Fix

## Issue Summary
The auto-promotion workflows (`41-auto-promote-dev-to-uat.yml` and `42-auto-promote-uat-to-main.yml`) were not triggering after deployments to development and UAT environments.

## Root Cause
The workflows use GitHub Actions' `workflow_run` event, which has a critical requirement:
> **The workflow file must exist in the default branch (main) for the trigger to work.**

These workflow files were added to the `development` branch in PR #171 but were never promoted to the `main` branch. As a result:
- When "Deploy Dev (Frontend + Backend via DOCR)" workflow completed on the `development` branch, GitHub Actions looked in the `main` branch for workflows with a `workflow_run` trigger
- Since `41-auto-promote-dev-to-uat.yml` didn't exist in `main`, it never triggered
- Similarly, `42-auto-promote-uat-to-main.yml` didn't exist in `main`, so it never triggered when UAT deployments completed

## Solution
This PR adds both auto-promotion workflow files to the `main` branch:
- `.github/workflows/41-auto-promote-dev-to-uat.yml` - Triggers when dev deployment completes
- `.github/workflows/42-auto-promote-uat-to-main.yml` - Triggers when UAT deployment completes

## How It Works

### Auto-Promote Dev to UAT
```yaml
on:
  workflow_run:
    workflows: ["Deploy Dev (Frontend + Backend via DOCR)"]
    types:
      - completed
    branches:
      - development
```
- Listens for the "Deploy Dev (Frontend + Backend via DOCR)" workflow
- Only triggers when it completes on the `development` branch
- Creates a PR from `development` to `uat` after successful deployment

### Auto-Promote UAT to Main
```yaml
on:
  workflow_run:
    workflows: ["Deploy UAT (Frontend + Backend via DOCR)"]
    types:
      - completed
    branches:
      - uat
```
- Listens for the "Deploy UAT (Frontend + Backend via DOCR)" workflow
- Only triggers when it completes on the `uat` branch
- Creates a PR from `uat` to `main` after successful deployment

## Expected Behavior After Fix
Once this PR is merged to `main`:

1. **Development Deployment Flow:**
   - Push to `development` → "Deploy Dev (Frontend + Backend via DOCR)" runs
   - Upon successful deployment → `41-auto-promote-dev-to-uat.yml` triggers
   - Auto-creates PR: `development` → `uat`

2. **UAT Deployment Flow:**
   - Merge to `uat` → "Deploy UAT (Frontend + Backend via DOCR)" runs
   - Upon successful deployment → `42-auto-promote-uat-to-main.yml` triggers
   - Auto-creates PR: `uat` → `main`

## Testing
The workflows can be manually tested using the `workflow_dispatch` trigger:
```bash
# Manually trigger auto-promote dev to UAT
gh workflow run 41-auto-promote-dev-to-uat.yml

# Manually trigger auto-promote UAT to main
gh workflow run 42-auto-promote-uat-to-main.yml
```

## References
- [GitHub Actions workflow_run documentation](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_run)
- PR #171: Original PR that added these workflows to the development branch, along with CODEOWNERS, workflow improvements, invitation email features, UI enhancements, and model improvements
- Related workflows:
  - `11-dev-deployment.yml` - Deploy Dev (Frontend + Backend via DOCR)
  - `12-uat-deployment.yml` - Deploy UAT (Frontend + Backend via DOCR)
