# Testing Guide: Auto-Promotion Workflow Fix

## Overview
This guide explains how to test and verify that the auto-promotion workflows are working correctly after this PR is merged to `main`.

## Pre-Merge State
- ❌ Auto-promotion workflows exist only in `development` branch
- ❌ GitHub Actions cannot find them in `main` (the default branch)
- ❌ Workflows never trigger after deployments

## Post-Merge State
- ✅ Auto-promotion workflows exist in `main` branch
- ✅ GitHub Actions can find and execute them
- ✅ Workflows trigger automatically after successful deployments

## Test Plan

### Test 1: Verify Workflows Exist in Main
**After PR is merged to main:**
```bash
# Check that workflows are in main branch
git checkout main
git pull origin main
ls -la .github/workflows/ | grep "41-auto-promote-dev-to-uat.yml"
ls -la .github/workflows/ | grep "42-auto-promote-uat-to-main.yml"
```
**Expected**: Both files should be present in main branch

### Test 2: Manual Workflow Trigger
**Test the workflows manually to ensure they work:**
```bash
# Manually trigger dev→uat promotion workflow
gh workflow run "Auto-Promote Dev to UAT"

# Check workflow run status
gh run list --workflow="Auto-Promote Dev to UAT" --limit 1

# Manually trigger uat→main promotion workflow
gh workflow run "Auto-Promote UAT to Main"

# Check workflow run status
gh run list --workflow="Auto-Promote UAT to Main" --limit 1
```
**Expected**: Workflows should run successfully and create PRs (if none exist)

### Test 3: Automatic Trigger - Dev to UAT
**Test that the workflow triggers automatically after dev deployment:**
1. Make a small change to development branch (e.g., update README)
2. Push to development:
   ```bash
   git checkout development
   git pull origin development
   echo "<!-- Test auto-promotion: $(date) -->" >> README.md
   git add README.md
   git commit -m "Test auto-promotion workflow trigger"
   git push origin development
   ```
3. Monitor the deployment workflow:
   ```bash
   gh run list --workflow=11-dev-deployment.yml --limit 1 --watch
   ```
4. After deployment succeeds, check if auto-promotion workflow runs:
   ```bash
   gh run list --workflow="Auto-Promote Dev to UAT" --limit 1
   ```
5. Check if PR was created:
   ```bash
   gh pr list --base uat --head development
   ```

**Expected**: 
- ✅ Dev deployment workflow completes successfully
- ✅ Auto-promotion workflow triggers automatically
- ✅ PR is created from development → uat (if one doesn't already exist)

### Test 4: Automatic Trigger - UAT to Main
**Test that the workflow triggers automatically after UAT deployment:**
1. Merge an existing PR to uat (or push directly to uat)
2. Monitor the UAT deployment workflow:
   ```bash
   gh run list --workflow=12-uat-deployment.yml --limit 1 --watch
   ```
3. After deployment succeeds, check if auto-promotion workflow runs:
   ```bash
   gh run list --workflow="Auto-Promote UAT to Main" --limit 1
   ```
4. Check if PR was created:
   ```bash
   gh pr list --base main --head uat
   ```

**Expected**:
- ✅ UAT deployment workflow completes successfully
- ✅ Auto-promotion workflow triggers automatically
- ✅ PR is created from uat → main (if one doesn't already exist)

## Troubleshooting

### If Workflows Don't Trigger Automatically

1. **Verify workflow files exist in main:**
   ```bash
   git checkout main
   git pull origin main
   ls -la .github/workflows/41-auto-promote-dev-to-uat.yml
   ls -la .github/workflows/42-auto-promote-uat-to-main.yml
   ```

2. **Check workflow syntax:**
   ```bash
   cat .github/workflows/41-auto-promote-dev-to-uat.yml | grep -A 5 "workflow_run:"
   ```
   Should show:
   ```yaml
   workflow_run:
     workflows: ["Deploy Dev (Frontend + Backend via DOCR)"]
     types:
       - completed
     branches:
       - development
   ```

3. **Verify deployment workflow names match:**
   ```bash
   grep '^name:' .github/workflows/11-dev-deployment.yml
   # Should output: name: Deploy Dev (Frontend + Backend via DOCR)
   
   grep '^name:' .github/workflows/12-uat-deployment.yml
   # Should output: name: Deploy UAT (Frontend + Backend via DOCR)
   ```

4. **Check GitHub Actions logs:**
   - Go to Actions tab in GitHub
   - Look for the auto-promotion workflow runs
   - Check if they're being triggered but failing

5. **Check workflow permissions:**
   - Ensure `GITHUB_TOKEN` has `contents: write` and `pull-requests: write` permissions
   - These are set in the workflow files

## Success Criteria
✅ Workflow files exist in `main` branch  
✅ Manual workflow triggers work correctly  
✅ Auto-promotion workflow triggers after successful dev deployment  
✅ Auto-promotion workflow triggers after successful UAT deployment  
✅ PRs are created automatically (when none exist)  
✅ PRs include comprehensive descriptions and checklists  
✅ Duplicate PR prevention works (no duplicate PRs created)

## Additional Notes
- Workflows will NOT trigger if deployment fails
- Workflows check for existing PRs to avoid duplicates
- PRs require manual approval before merge
- Each PR includes comprehensive checklists for review
