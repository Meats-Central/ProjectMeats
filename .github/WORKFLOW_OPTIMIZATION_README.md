# Workflow Optimization & Cleanup Tools

This directory contains automation tools for managing GitHub Actions workflows, reducing clutter, and enforcing retention policies.

## 📋 Table of Contents

1. [Scripts](#scripts)
2. [Workflows](#workflows)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## 🛠️ Scripts

### `bulk-delete-workflow-runs.sh`

**Purpose**: Manually delete workflow runs older than a specified age with flexible filtering.

**Features**:
- Delete runs by age, status (failed/success/cancelled), and actor (e.g., Dependabot)
- Dry-run mode for safe previewing
- Comprehensive logging with timestamps
- Rate limiting to respect GitHub API limits
- Confirmation prompts for safety
- Retry logic for failed deletions

**Prerequisites**:
```bash
# Install GitHub CLI
# macOS
brew install gh

# Linux (Debian/Ubuntu)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate
gh auth login
```

**Basic Usage**:
```bash
# Dry run (preview only)
./.github/scripts/bulk-delete-workflow-runs.sh --dry-run

# Delete failed runs older than 30 days
./.github/scripts/bulk-delete-workflow-runs.sh --status failed --days 30

# Delete Dependabot runs older than 60 days
./.github/scripts/bulk-delete-workflow-runs.sh --actor "dependabot[bot]" --days 60

# Auto-confirm (no prompts) for automation
./.github/scripts/bulk-delete-workflow-runs.sh --status failed --days 30 --auto-confirm
```

**Advanced Options**:
```bash
--dry-run           # Preview mode (no deletions)
--auto-confirm      # Skip confirmation prompts
--days N            # Age threshold in days (default: 30)
--status STATUS     # Filter: failed, success, cancelled, all (default: all)
--actor ACTOR       # Filter by actor (e.g., dependabot[bot])
--help              # Show help message
```

**Output**:
- Console output with color-coded status
- Log file: `workflow-deletion-YYYYMMDD-HHMMSS.log`
- Summary of deleted runs with IDs

---

## ⚙️ Workflows

### 1. `workflow-retention-policy.yml`

**Purpose**: Automated enforcement of artifact and workflow run retention policies.

**Schedule**: Weekly (Sundays at 3 AM UTC)

**Features**:
- Deletes artifacts older than 30 days
- Deletes failed/cancelled workflow runs older than 30 days
- Configurable retention period via workflow_dispatch
- Dry-run mode for testing
- Generates detailed retention reports
- Tracks storage savings

**Configuration**:
```yaml
# Default settings (can be overridden via workflow_dispatch)
RETENTION_DAYS: 30
DRY_RUN: false
```

**Manual Trigger**:
```bash
# Via GitHub CLI
gh workflow run workflow-retention-policy.yml

# With custom parameters
gh workflow run workflow-retention-policy.yml \
  -f retention_days=60 \
  -f dry_run=true
```

**Outputs**:
- Retention report (uploaded as artifact)
- Summary of deleted artifacts and runs
- Storage space saved (in MB)

**Slack Notifications** (Optional):
To enable Slack notifications, uncomment the notification step and configure:
```yaml
secrets:
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

---

### 2. `automated-workflow-deletion.yml`

**Purpose**: Reusable workflow for automated deletion of old workflow runs.

**Schedule**: Monthly (1st day at 4 AM UTC)

**Features**:
- Flexible filtering by status, age, and actor
- Safety limit to prevent accidental mass deletion
- Dry-run mode for testing
- Comprehensive audit logging
- Retry logic with exponential backoff
- Future-ready for Celery integration (Phase 6)

**Configuration**:
```yaml
# Default settings
STATUS_FILTER: failed      # failed, cancelled, success, all
AGE_DAYS: 90              # Delete runs older than 90 days
ACTOR_FILTER: ''          # Optional: filter by actor
DRY_RUN: false
MAX_DELETIONS: 1000       # Safety limit
```

**Manual Trigger**:
```bash
# Delete failed runs older than 90 days
gh workflow run automated-workflow-deletion.yml \
  -f status_filter=failed \
  -f age_days=90

# Delete Dependabot runs older than 60 days (dry run)
gh workflow run automated-workflow-deletion.yml \
  -f status_filter=all \
  -f age_days=60 \
  -f actor_filter="dependabot[bot]" \
  -f dry_run=true

# Delete all runs older than 120 days
gh workflow run automated-workflow-deletion.yml \
  -f status_filter=all \
  -f age_days=120 \
  -f max_deletions=2000
```

**Outputs**:
- Audit log with complete deletion history (retained for 365 days)
- Job summary with deletion statistics
- List of failed deletions for manual review

**Security**:
- Uses minimal `actions:write` permission
- Complete audit trail
- Rate limiting to respect API limits
- Safety limits to prevent accidents

---

## 📝 Configuration

### Dependabot Configuration

The enhanced `dependabot.yml` includes:

**Grouped Updates**:
- All GitHub Actions updates → Single weekly PR
- Django/DRF packages → Single PR
- React/TypeScript packages → Single PR
- Build tools (Vite, esbuild) → Single PR

**Open PR Limit**: 5 (increased from 3)

**Patch Version Handling**:
- Critical dependencies: Update on minor + patch
- Non-critical dependencies: Update on minor only (ignore patch)
- Dev dependencies: Update on minor only

**OWASP Vulnerability Management**:
```yaml
ignore:
  - dependency-name: "package-name"
    versions: ["< x.y.z"]
    # Always document why a vulnerability is ignored
    # Example reasons:
    # - Not applicable to our use case
    # - Mitigated by other controls
    # - False positive
```

**Auto-merge Support**:
- PRs labeled with `automerge` can be auto-merged after CI passes
- Requires branch protection rules

---

## 💡 Usage Examples

### Example 1: Clean up old Dependabot runs

```bash
# Step 1: Preview what would be deleted
./.github/scripts/bulk-delete-workflow-runs.sh \
  --actor "dependabot[bot]" \
  --days 30 \
  --dry-run

# Step 2: Execute deletion
./.github/scripts/bulk-delete-workflow-runs.sh \
  --actor "dependabot[bot]" \
  --days 30
```

### Example 2: Clean up failed workflow runs

```bash
# Delete failed runs older than 60 days
./.github/scripts/bulk-delete-workflow-runs.sh \
  --status failed \
  --days 60
```

### Example 3: Enforce custom retention policy

```bash
# Via workflow (dry run first)
gh workflow run workflow-retention-policy.yml \
  -f retention_days=45 \
  -f dry_run=true

# Execute after reviewing dry run results
gh workflow run workflow-retention-policy.yml \
  -f retention_days=45
```

### Example 4: Emergency cleanup

```bash
# Quick cleanup of very old runs
gh workflow run automated-workflow-deletion.yml \
  -f status_filter=all \
  -f age_days=180 \
  -f max_deletions=5000
```

---

## 🎯 Best Practices

### 1. **Always test with dry-run first**
```bash
# Test before executing
./.github/scripts/bulk-delete-workflow-runs.sh --dry-run --status failed
```

### 2. **Use safety limits**
- Default `max_deletions=1000` prevents accidents
- Increase only when necessary
- Monitor deletion logs

### 3. **Regular maintenance schedule**
- Weekly: Artifact cleanup (automated)
- Monthly: Workflow run cleanup (automated)
- Quarterly: Manual review of retention policies

### 4. **Monitor storage usage**
```bash
# Check repository storage via API
gh api /repos/Meats-Central/ProjectMeats --jq '.size'
```

### 5. **Document ignored vulnerabilities**
- Always add reason when ignoring Dependabot alerts
- Review ignored vulnerabilities quarterly
- Remove ignore rules when fixed

### 6. **Review audit logs**
```bash
# Download latest audit log
gh run download $(gh run list --workflow=automated-workflow-deletion.yml --limit 1 --json databaseId --jq '.[0].databaseId')
```

---

## 🐛 Troubleshooting

### Issue: Script fails with "gh: command not found"

**Solution**:
```bash
# Install GitHub CLI
# See Prerequisites section above
```

### Issue: "API rate limit exceeded"

**Solution**:
```bash
# Check rate limit status
gh api rate_limit

# Wait for rate limit reset or reduce batch size
./.github/scripts/bulk-delete-workflow-runs.sh --days 30 --max-deletions=100
```

### Issue: Workflow run deletion fails with 403

**Solution**:
- Ensure `GITHUB_TOKEN` has `actions:write` permission
- Check if workflow is protected (cannot delete runs from protected branches)
- Verify repository permissions

### Issue: Dependabot PRs not auto-merging

**Solution**:
1. Enable auto-merge in repository settings
2. Configure branch protection rules
3. Add `automerge` label to PRs
4. Ensure status checks pass

### Issue: Too many open Dependabot PRs

**Solution**:
```yaml
# Adjust open-pull-requests-limit in dependabot.yml
open-pull-requests-limit: 3  # Lower value

# Or close stale PRs manually
gh pr list --label dependencies --state open | while read pr; do
  gh pr close $(echo $pr | awk '{print $1}')
done
```

---

## 🔮 Future Enhancements (Phase 6)

### Planned Features:

1. **Celery Integration**
   - Async task processing for large-scale deletions
   - Background job queue for cleanup operations
   - Progress tracking and status updates

2. **Advanced Filtering**
   - Workflow-specific retention policies
   - Branch-based retention rules
   - Tag-based deletion policies

3. **Enhanced Notifications**
   - Slack integration (webhook ready)
   - Email alerts for cleanup reports
   - Discord/Teams notifications

4. **Storage Analytics**
   - Track storage usage over time
   - Identify storage-heavy workflows
   - Cost optimization recommendations

5. **Smart Retention**
   - ML-based retention policy suggestions
   - Automatic adjustment based on patterns
   - Predictive cleanup scheduling

---

## 📚 Additional Resources

- [GitHub Actions API Documentation](https://docs.github.com/en/rest/actions)
- [GitHub CLI Manual](https://cli.github.com/manual/)
- [Dependabot Configuration Reference](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [Workflow Concurrency Documentation](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#concurrency)

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review audit logs and error messages
3. Consult GitHub Actions documentation
4. Create an issue in the repository

---

**Last Updated**: 2024-12-09
**Maintained By**: ProjectMeats DevOps Team
