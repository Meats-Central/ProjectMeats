# Applying Phase 4 to UAT and Production Workflows

## Overview

This guide provides step-by-step instructions for applying Phase 4 enhancements (notifications, health checks, documentation) to UAT and Production deployment workflows.

## Prerequisites

✅ **Completed:**
- Phase 4 implemented in dev workflow (PR #872)
- Notification script created (`.github/scripts/notify-deployment.sh`)
- Health check script enhanced (`.github/scripts/health-check.sh`)
- ROADMAP.md and documentation complete

🔄 **Required:**
- PR #872 merged to `development`
- UAT and Production GitHub Environments configured
- Webhook URLs obtained (optional but recommended)

---

## Step 1: Configure Webhook URLs

### Slack Webhook Setup

1. Navigate to: https://api.slack.com/messaging/webhooks
2. Click "Create your Slack app" or use existing app
3. Enable "Incoming Webhooks"
4. Click "Add New Webhook to Workspace"
5. Select channel (e.g., `#deployments`, `#cicd-alerts`)
6. Copy webhook URL: `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX`

### Teams Webhook Setup

1. In Teams, navigate to desired channel
2. Click "..." → "Connectors" → "Incoming Webhook"
3. Click "Configure"
4. Name webhook: "ProjectMeats Deployments"
5. Upload icon (optional)
6. Click "Create"
7. Copy webhook URL: `https://outlook.office.com/webhook/...`

### Add to GitHub Secrets

1. Navigate to: https://github.com/Meats-Central/ProjectMeats/settings/secrets/actions
2. Add repository secrets (or environment-specific secrets):
   - `SLACK_WEBHOOK_URL`: Paste Slack webhook URL
   - `TEAMS_WEBHOOK_URL`: Paste Teams webhook URL (optional)

**Recommendation:** Use environment-scoped secrets for better isolation:
- `UAT_SLACK_WEBHOOK_URL` for UAT environment
- `PROD_SLACK_WEBHOOK_URL` for Production environment

---

## Step 2: Update UAT Workflow (12-uat-deployment.yml)

### Changes Required

1. **Add checkout step to deploy jobs** (for accessing scripts)
2. **Replace ad-hoc health checks** with standardized script
3. **Add notification steps** (success + failure)

### Example: deploy-frontend Job

```yaml
deploy-frontend:
  runs-on: ubuntu-latest
  needs: [test-frontend]
  environment: uat-frontend
  timeout-minutes: 20
  permissions:
    contents: read
  steps:
    # ADD: Checkout for scripts access
    - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      with:
        fetch-depth: 1

    - name: Setup SSH with password authentication
      run: |
        sudo apt-get update
        sudo apt-get install -y sshpass
        mkdir -p ~/.ssh
        ssh-keyscan -H "${{ secrets.UAT_HOST }}" >> ~/.ssh/known_hosts

    - name: Deploy frontend container
      env:
        SSHPASS: ${{ secrets.UAT_SSH_PASSWORD }}
      run: |
        # ... existing deployment steps ...

    # REPLACE: Old health check
    # - name: Health check (Frontend)
    #   run: |
    #     sleep 5
    #     curl -fsS "${{ secrets.UAT_URL }}" > /dev/null

    # NEW: Standardized health check
    - name: Health check (Frontend)
      run: |
        chmod +x .github/scripts/health-check.sh
        ./.github/scripts/health-check.sh "${{ secrets.UAT_URL }}" 20 5

    # ADD: Success notification
    - name: Notify deployment success
      if: success()
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.UAT_SLACK_WEBHOOK_URL }}
      run: |
        chmod +x .github/scripts/notify-deployment.sh
        ./.github/scripts/notify-deployment.sh "success" "uat" "frontend" "${{ github.sha }}"

    # ADD: Failure notification
    - name: Notify deployment failure
      if: failure()
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.UAT_SLACK_WEBHOOK_URL }}
      run: |
        chmod +x .github/scripts/notify-deployment.sh
        ./.github/scripts/notify-deployment.sh "failure" "uat" "frontend" "${{ github.sha }}" "Frontend deployment or health check failed"
```

### Example: deploy-backend Job

```yaml
deploy-backend:
  runs-on: ubuntu-latest
  needs: [test-backend]
  environment: uat-backend
  timeout-minutes: 30
  permissions:
    contents: read
  steps:
    # ADD: Checkout for scripts access
    - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
      with:
        fetch-depth: 1

    - name: Setup SSH with password authentication
      run: |
        sudo apt-get update
        sudo apt-get install -y sshpass
        mkdir -p ~/.ssh
        ssh-keyscan -H "${{ secrets.UAT_HOST }}" >> ~/.ssh/known_hosts

    - name: Deploy backend container
      env:
        SSHPASS: ${{ secrets.UAT_SSH_PASSWORD }}
      run: |
        # ... existing deployment steps with migrations ...
        # Backend health check is already structured (retain existing)

    # ADD: Success notification
    - name: Notify deployment success
      if: success()
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.UAT_SLACK_WEBHOOK_URL }}
      run: |
        chmod +x .github/scripts/notify-deployment.sh
        ./.github/scripts/notify-deployment.sh "success" "uat" "backend" "${{ github.sha }}"

    # ADD: Failure notification
    - name: Notify deployment failure
      if: failure()
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.UAT_SLACK_WEBHOOK_URL }}
      run: |
        chmod +x .github/scripts/notify-deployment.sh
        ./.github/scripts/notify-deployment.sh "failure" "uat" "backend" "${{ github.sha }}" "Backend deployment, migration, or health check failed"
```

---

## Step 3: Update Production Workflow (13-prod-deployment.yml)

### Changes Required

Same pattern as UAT, with production-specific considerations:

1. **Add checkout step** to all deploy jobs
2. **Standardize health checks** (if not already done)
3. **Add notifications** with production-specific secrets
4. **Consider additional approval step** before notifications (optional)

### Production-Specific Considerations

#### Critical Notifications

For production, consider adding a separate critical alert channel:

```yaml
- name: Notify deployment failure (Critical)
  if: failure()
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.PROD_CRITICAL_SLACK_WEBHOOK_URL }}  # Separate channel
    TEAMS_WEBHOOK_URL: ${{ secrets.PROD_TEAMS_WEBHOOK_URL }}
  run: |
    chmod +x .github/scripts/notify-deployment.sh
    ./.github/scripts/notify-deployment.sh "failure" "prod" "backend" "${{ github.sha }}" "CRITICAL: Production deployment failed"
```

#### Rollback Notifications

Add notification for rollback events:

```yaml
- name: Notify rollback
  if: steps.deployment.outcome == 'failure' && steps.rollback.outcome == 'success'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.PROD_SLACK_WEBHOOK_URL }}
  run: |
    ./.github/scripts/notify-deployment.sh "warning" "prod" "backend" "${{ github.sha }}" "Deployment failed, rolled back to previous version"
```

#### Success Notifications with Metrics

For production, include additional context:

```yaml
- name: Notify deployment success
  if: success()
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.PROD_SLACK_WEBHOOK_URL }}
  run: |
    # Calculate deployment duration
    DURATION=$((SECONDS / 60))
    ./.github/scripts/notify-deployment.sh "success" "prod" "backend" "${{ github.sha }}" "Deployment completed in ${DURATION}m"
```

---

## Step 4: Testing Notifications

### Test Plan

1. **Dev Environment (Already Configured)**
   ```bash
   # Merge PR #872 to trigger dev deployment
   gh pr merge 872 --squash
   
   # Monitor for notification in Slack/Teams
   # Expected: Success notification with green indicator
   ```

2. **UAT Environment**
   ```bash
   # After dev deployment succeeds, auto-PR to UAT will be created
   # Merge UAT PR to trigger deployment
   
   # Expected notifications:
   # - Frontend deployment success
   # - Backend deployment success
   # - Both with "UAT" environment label
   ```

3. **Production Environment**
   ```bash
   # After UAT verification, merge to main
   # Monitor critical notification channels
   
   # Expected:
   # - Production deployment notifications
   # - Sent to production-specific channels
   ```

### Validation Checklist

For each environment:
- [ ] Notification received in correct channel
- [ ] Environment label correct (DEV/UAT/PROD)
- [ ] Commit SHA matches deployed version
- [ ] GitHub Actions run URL is clickable and correct
- [ ] Error messages are actionable (for failure notifications)
- [ ] Notification arrives within 10 seconds of deployment completion

---

## Step 5: Monitoring and Iteration

### Week 1: Monitor Notification Delivery

Track metrics:
- **Delivery rate:** Should be >99%
- **Latency:** Notification within 10s of completion
- **False positives:** Health checks failing incorrectly
- **Actionability:** Team can diagnose issues from notification alone

### Week 2: Gather Feedback

Questions to ask team:
1. Are notifications arriving in the right channels?
2. Is the information sufficient for incident response?
3. Are there too many/too few notifications?
4. Should we add more context (e.g., deployment duration, affected services)?

### Week 3: Iterate

Based on feedback, consider:
- **Add metrics:** Deployment duration, number of migrations applied
- **Conditional notifications:** Only notify on failures, or only production
- **Digest mode:** Daily summary instead of per-deployment
- **Integration:** Link to monitoring dashboards (Datadog, New Relic, etc.)

---

## Step 6: Update UAT and Production Workflows

### Create PR for UAT Workflow

```bash
git checkout -b feat/phase4-uat-notifications
# Apply changes to .github/workflows/12-uat-deployment.yml
git add .github/workflows/12-uat-deployment.yml
git commit -m "feat: Add Phase 4 notifications to UAT workflow

Applies Phase 4 enhancements to UAT deployment:
- Add checkout step for script access
- Replace ad-hoc health checks with standardized script
- Add success/failure notifications
- Configure UAT-specific webhook URLs

Follows same pattern as dev workflow (PR #872)"

git push -u origin feat/phase4-uat-notifications
gh pr create --base development --head feat/phase4-uat-notifications \
  --title "feat: Add Phase 4 notifications to UAT workflow" \
  --body "Applies Phase 4 enhancements to UAT deployment..."
```

### Create PR for Production Workflow

```bash
git checkout -b feat/phase4-prod-notifications
# Apply changes to .github/workflows/13-prod-deployment.yml
# Include production-specific enhancements (critical alerts, rollback notifications)
git add .github/workflows/13-prod-deployment.yml
git commit -m "feat: Add Phase 4 notifications to Production workflow

Applies Phase 4 enhancements to Production deployment:
- Add checkout step for script access
- Standardize health checks across all deploy jobs
- Add success/failure notifications with critical channel
- Add rollback notifications
- Include deployment metrics in success messages

Follows same pattern as dev (PR #872) and UAT with
production-specific enhancements for critical alerting."

git push -u origin feat/phase4-prod-notifications
gh pr create --base development --head feat/phase4-prod-notifications \
  --title "feat: Add Phase 4 notifications to Production workflow" \
  --body "Applies Phase 4 enhancements to Production deployment..."
```

---

## Rollout Schedule

### Conservative Rollout (Recommended)

| Week | Environment | Action | Validation |
|------|-------------|--------|------------|
| Week 1 | Development | Merge PR #872 | Monitor notifications for 7 days |
| Week 2 | UAT | Merge UAT PR | Monitor notifications for 7 days |
| Week 3 | Production | Merge Prod PR | Monitor notifications for 14 days |
| Week 4 | All | Iterate based on feedback | Update scripts/workflows |

### Aggressive Rollout (Fast-Track)

| Day | Environment | Action | Validation |
|-----|-------------|--------|------------|
| Day 1 | Development | Merge PR #872 | Monitor for 24 hours |
| Day 2 | UAT | Merge UAT PR | Monitor for 24 hours |
| Day 3 | Production | Merge Prod PR | Monitor continuously |

**Recommendation:** Use conservative rollout for production systems.

---

## Troubleshooting

### Issue: Notifications Not Received

**Symptoms:**
- Workflow succeeds but no notification
- Logs show "Slack webhook URL not configured, skipping"

**Solution:**
1. Verify secret is configured: `gh secret list`
2. Check secret name matches workflow: `SLACK_WEBHOOK_URL` or `UAT_SLACK_WEBHOOK_URL`
3. Ensure secret is in correct environment (not repo-level)
4. Test webhook manually:
   ```bash
   curl -X POST -H 'Content-Type: application/json' \
     -d '{"text":"Test notification"}' \
     "$SLACK_WEBHOOK_URL"
   ```

### Issue: Health Check False Positives

**Symptoms:**
- Deployment succeeds but health check fails
- Application is actually running and healthy

**Solution:**
1. Increase max_attempts: `./.github/scripts/health-check.sh "$URL" 30 5`
2. Check if URL requires authentication
3. Verify URL is correct (not localhost)
4. Add delay before health check: `sleep 10` before script execution
5. Check firewall/security group rules

### Issue: Notification Spam

**Symptoms:**
- Too many notifications
- Team ignoring notifications

**Solution:**
1. **Option A:** Only notify on failures
   ```yaml
   - name: Notify deployment status
     if: failure()  # Remove success notification
   ```

2. **Option B:** Aggregate notifications (daily digest)
   - Create separate workflow that runs on schedule
   - Queries GitHub API for deployment history
   - Sends single summary notification

3. **Option C:** Use notification preferences
   - Add environment variable: `NOTIFY_LEVEL=critical`
   - Only send critical (production) notifications

---

## Best Practices

### Notification Channel Strategy

| Environment | Channel | Subscribers | Noise Level |
|-------------|---------|-------------|-------------|
| Development | `#dev-deployments` | Dev team | High (all deploys) |
| UAT | `#uat-deployments` | QA + Dev leads | Medium (merge events) |
| Production | `#prod-deployments` | All engineering | Low (failures only) |
| Critical | `#prod-critical` | On-call + management | Very low (prod failures) |

### Notification Content Guidelines

**DO:**
- Include commit SHA (first 7 chars)
- Include triggering user (accountability)
- Include direct link to workflow run
- Use color coding (green=success, red=failure, yellow=warning)
- Keep messages concise (<200 chars for title)

**DON'T:**
- Include sensitive data (passwords, API keys)
- Include full error traces (link to logs instead)
- Send notifications for non-actionable events
- Use `@channel` or `@here` (too disruptive)

### Health Check Best Practices

**DO:**
- Use application-specific health endpoints (`/api/v1/health/`)
- Check dependencies (database, cache, external services)
- Return structured JSON with status details
- Use HTTP 200 for healthy, 503 for unhealthy
- Implement timeout-aware health checks

**DON'T:**
- Check root URL (may redirect or be cached)
- Rely on container status alone (may be running but unhealthy)
- Skip database connection checks
- Use overly aggressive timeouts (<5s)

---

## Success Metrics

### Target Metrics (90 days post-rollout)

| Metric | Target | Current (Baseline) |
|--------|--------|--------------------|
| Notification delivery rate | >99% | N/A |
| Mean time to incident awareness | <2 min | ~15 min |
| False positive rate (health checks) | <5% | ~30% |
| Deployment confidence score | 9/10 | 7/10 |
| Team satisfaction with alerts | 8/10 | 5/10 |

### Measurement Plan

**Weekly:**
- Count notifications sent vs expected
- Track notification delivery latency
- Log health check false positives

**Monthly:**
- Survey team on notification quality
- Analyze incident response times (before/after)
- Review and adjust notification thresholds

**Quarterly:**
- Update ROADMAP with lessons learned
- Plan Phase 5 enhancements based on data
- Present metrics to stakeholders

---

## Appendix A: Webhook Payload Examples

### Slack Payload (Success)

```json
{
  "attachments": [
    {
      "color": "#28a745",
      "title": "✅ Deployment Successful",
      "fields": [
        {"title": "Environment", "value": "UAT", "short": true},
        {"title": "Component", "value": "backend", "short": true},
        {"title": "Commit", "value": "`9551c69`", "short": true},
        {"title": "Triggered By", "value": "Vacilator", "short": true},
        {"title": "Timestamp", "value": "2024-12-01 22:54:00 UTC", "short": false}
      ],
      "actions": [
        {
          "type": "button",
          "text": "View Workflow Run",
          "url": "https://github.com/Meats-Central/ProjectMeats/actions/runs/123456789"
        }
      ]
    }
  ]
}
```

### Slack Payload (Failure)

```json
{
  "attachments": [
    {
      "color": "#dc3545",
      "title": "❌ Deployment Failed",
      "fields": [
        {"title": "Environment", "value": "PROD", "short": true},
        {"title": "Component", "value": "backend", "short": true},
        {"title": "Commit", "value": "`9551c69`", "short": true},
        {"title": "Triggered By", "value": "Vacilator", "short": true},
        {"title": "Error Details", "value": "```Migration 0042 failed: relation 'users' already exists```", "short": false}
      ],
      "actions": [
        {
          "type": "button",
          "text": "View Workflow Run",
          "url": "https://github.com/Meats-Central/ProjectMeats/actions/runs/123456789"
        }
      ]
    }
  ]
}
```

---

## Appendix B: Quick Reference

### Notification Script Usage

```bash
# Success notification
./.github/scripts/notify-deployment.sh "success" "dev" "frontend" "$SHA"

# Failure notification with error
./.github/scripts/notify-deployment.sh "failure" "prod" "backend" "$SHA" "Migration failed"

# Warning notification
./.github/scripts/notify-deployment.sh "warning" "uat" "full-stack" "$SHA" "Deployment succeeded with warnings"
```

### Health Check Script Usage

```bash
# Basic usage
./.github/scripts/health-check.sh "https://api.example.com/health/" 20 5

# Custom parameters
./.github/scripts/health-check.sh "$URL" 30 10  # 30 attempts, 10s delay

# With environment variable
export HEALTH_URL="https://api.example.com/health/"
./.github/scripts/health-check.sh "$HEALTH_URL"
```

### Required Secrets by Environment

| Secret | Dev | UAT | Prod | Description |
|--------|-----|-----|------|-------------|
| `SLACK_WEBHOOK_URL` | ✓ | ✓ | ✓ | Slack incoming webhook URL |
| `TEAMS_WEBHOOK_URL` | ○ | ○ | ○ | Teams channel webhook URL |
| `{ENV}_SLACK_WEBHOOK_URL` | ○ | ✓ | ✓ | Environment-specific Slack URL |
| `PROD_CRITICAL_SLACK_WEBHOOK_URL` | ✗ | ✗ | ✓ | Production critical channel |

Legend: ✓ Required | ○ Optional | ✗ Not applicable

---

*Last Updated: 2024-12-01*  
*Version: 1.0*  
*Applies to: Phase 4 Implementation*  
*Related PRs: #869, #872*
