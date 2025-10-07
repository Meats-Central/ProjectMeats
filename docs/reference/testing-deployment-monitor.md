# Testing the Deployment Failure Monitoring

## Overview
This document explains how to test the automatic issue creation for deployment failures.

## Test Workflow Created
A test workflow (`test-deployment-failure.yml`) has been created to simulate deployment failures safely.

## How to Test

### Step 1: Temporarily Modify the Monitor
To test without waiting for real failures, temporarily modify `.github/workflows/deployment-failure-monitor.yml`:

```yaml
# Change this section:
on:
  workflow_run:
    workflows: 
      - "Deploy Frontend to UAT2 Staging"
      - "Deploy Backend to UAT2 Staging"
    types:
      - completed

# To this (add the test workflow):
on:
  workflow_run:
    workflows: 
      - "Deploy Frontend to UAT2 Staging"
      - "Deploy Backend to UAT2 Staging"
      - "Test Deployment Failure Monitor"  # Add this line
    types:
      - completed
```

### Step 2: Run the Test
1. Go to GitHub Actions tab
2. Select "Test Deployment Failure Monitor" workflow  
3. Click "Run workflow"
4. Choose either "frontend" or "backend" to simulate failure
5. Click "Run workflow" button

### Step 3: Verify Issue Creation
After the test workflow fails (takes 1-2 minutes):
1. Check the "Issues" tab for a new issue
2. Verify it has:
   - Title starting with "Fix"
   - Link to the failed workflow run
   - Error logs from the simulated failure
   - Assignment to @copilot
   - Proper labels (bug, deployment, staging, urgent)
   - Instructions about using development branch

### Step 4: Clean Up
1. **Restore** the original monitoring workflow (remove the test workflow from the list)
2. **Delete** the test issue that was created
3. **Optional:** Delete the test workflow file if no longer needed

## Expected Results

### Frontend Test
Should create issue like:
```
Title: Fix Frontend UAT2 Staging Deployment Failure - 2024-09-13

Content includes:
- Link to test workflow run
- Error logs showing "Failed to build React app"
- Instructions about development branch PRs
- Assignment to @copilot
```

### Backend Test  
Should create issue like:
```
Title: Fix Backend UAT2 Staging Deployment Failure - 2024-09-13

Content includes:
- Link to test workflow run  
- Error logs showing "Database connection failed"
- Instructions about development branch PRs
- Assignment to @copilot
```

## Production Readiness
Once testing is complete and results are verified:
1. Remove the test workflow from monitoring
2. The system is ready to automatically handle real deployment failures
3. No further configuration needed

## Troubleshooting
If issues aren't created:
1. Check that the monitor workflow has proper permissions
2. Verify the workflow names match exactly
3. Ensure the test workflow actually failed (not cancelled)
4. Check GitHub Actions logs for the monitor workflow