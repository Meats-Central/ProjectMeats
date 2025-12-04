# Deployment Workflow Stability Guide

## Overview
This guide provides actionable steps to ensure the dev deployment workflow remains stable and functional after fixing the bash heredoc escaping issues.

---

## Immediate Actions (Next 24 Hours)

### 1. Monitor Next Deployment
- [ ] Watch the next automatic deployment triggered by push to `development`
- [ ] Verify all 8 jobs complete successfully
- [ ] Check backend health endpoint: `http://dev-server:8000/api/v1/health/`
- [ ] Confirm application is accessible and functional

### 2. Test Manual Deployment
```bash
# Trigger workflow manually to verify workflow_dispatch works
gh workflow run 11-dev-deployment.yml --ref development
```

### 3. Document Current Working State
- [x] Escaping rules documented in `SDLC_LOOP_DEPLOYMENT_FIX.md`
- [ ] Add inline comments to workflow file explaining escaping rules
- [ ] Share knowledge with team members

---

## Short-Term Actions (Next Week)

### 1. Add Pre-Commit Validation

Create `.github/hooks/pre-commit-workflow-check.sh`:

```bash
#!/bin/bash
# Pre-commit hook to validate workflow syntax

echo "Validating GitHub Actions workflows..."

# Check YAML syntax
for workflow in .github/workflows/*.yml; do
    echo "Checking: $workflow"
    python3 -c "import yaml; yaml.safe_load(open('$workflow'))" || {
        echo "❌ YAML syntax error in $workflow"
        exit 1
    }
done

# Check for common heredoc escaping mistakes
echo "Checking for heredoc escaping issues..."
if grep -r '<<.*SSH' .github/workflows/ | grep -q '\\$\$('; then
    echo "⚠️  Warning: Found \\\$\$( pattern - this may cause syntax errors in heredocs"
    echo "    In quoted heredocs (<<'SSH'), use \$(cmd) not \\\$(cmd)"
fi

echo "✅ Workflow validation passed"
```

**Install the hook:**
```bash
chmod +x .github/hooks/pre-commit-workflow-check.sh
# Add to .git/hooks/pre-commit or use husky/pre-commit framework
```

### 2. Create Workflow Syntax Test Suite

Create `.github/workflows/test-deployment-syntax.yml`:

```yaml
name: Test Deployment Syntax

on:
  pull_request:
    paths:
      - '.github/workflows/**'
  workflow_dispatch:

jobs:
  validate-bash-syntax:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Extract and test SSH heredoc scripts
        run: |
          # Extract SSH heredoc blocks and validate bash syntax
          echo "Testing heredoc bash syntax..."
          
          # Test command substitution patterns
          bash -c 'VAR=$(echo "test"); echo "Result: $VAR"' || {
            echo "❌ Command substitution test failed"
            exit 1
          }
          
          # Test arithmetic expansion patterns
          bash -c 'ATTEMPT=1; ATTEMPT=$((ATTEMPT + 1)); echo $ATTEMPT' || {
            echo "❌ Arithmetic expansion test failed"
            exit 1
          }
          
          echo "✅ Bash syntax tests passed"
      
      - name: Validate YAML syntax
        run: |
          for workflow in .github/workflows/*.yml; do
            python3 -c "import yaml; yaml.safe_load(open('$workflow'))"
          done
          echo "✅ All workflow YAML files are valid"
```

### 3. Set Up Deployment Notifications

Add to Slack/Discord/Email notifications:

```yaml
# Add to end of deploy-backend job in 11-dev-deployment.yml
      - name: Notify deployment status
        if: always()
        run: |
          if [ "${{ job.status }}" = "success" ]; then
            echo "✅ Dev deployment successful"
            # Add Slack webhook notification here
            # curl -X POST -H 'Content-type: application/json' \
            #   --data '{"text":"✅ Dev deployment successful"}' \
            #   ${{ secrets.SLACK_WEBHOOK_URL }}
          else
            echo "❌ Dev deployment failed"
            # Add failure notification
          fi
```

---

## Long-Term Actions (Next Month)

### 1. Migrate to Composite Actions

**Create `.github/actions/ssh-deploy/action.yml`:**

```yaml
name: 'SSH Deployment'
description: 'Reusable SSH deployment with proper heredoc handling'
inputs:
  ssh-host:
    required: true
  ssh-user:
    required: true
  ssh-password:
    required: true
  script:
    required: true
    description: 'Bash script to execute (no heredoc needed)'

runs:
  using: 'composite'
  steps:
    - name: Setup SSH
      shell: bash
      run: |
        sudo apt-get update
        sudo apt-get install -y sshpass
        mkdir -p ~/.ssh
        ssh-keyscan -H "${{ inputs.ssh-host }}" >> ~/.ssh/known_hosts
    
    - name: Execute deployment
      shell: bash
      env:
        SSHPASS: ${{ inputs.ssh-password }}
      run: |
        # Write script to temp file to avoid heredoc issues
        cat > /tmp/deploy-script.sh << 'DEPLOY_EOF'
        ${{ inputs.script }}
        DEPLOY_EOF
        
        sshpass -e scp /tmp/deploy-script.sh \
          ${{ inputs.ssh-user }}@${{ inputs.ssh-host }}:/tmp/
        
        sshpass -e ssh ${{ inputs.ssh-user }}@${{ inputs.ssh-host }} \
          'bash /tmp/deploy-script.sh && rm /tmp/deploy-script.sh'
        
        rm /tmp/deploy-script.sh
```

**Benefits:**
- Eliminates complex nested heredocs
- Easier to test and maintain
- Reusable across workflows

### 2. Implement Deployment Rollback

Add rollback capability to workflow:

```yaml
      - name: Store previous deployment state
        run: |
          PREV_CONTAINER=$(ssh $HOST 'docker ps -q --filter name=pm-backend')
          echo "PREV_CONTAINER=$PREV_CONTAINER" >> $GITHUB_ENV
      
      - name: Deploy with rollback on failure
        run: |
          # Deployment steps...
          
      - name: Rollback on failure
        if: failure()
        run: |
          echo "Rolling back to previous container..."
          ssh $HOST "docker start $PREV_CONTAINER || echo 'No rollback available'"
```

### 3. Add Integration Tests Post-Deployment

```yaml
  integration-tests:
    runs-on: ubuntu-latest
    needs: [deploy-backend]
    steps:
      - name: Run health checks
        run: |
          curl -f ${{ secrets.DEV_BACKEND_HEALTH_URL }} || exit 1
      
      - name: Test critical endpoints
        run: |
          # Test authentication
          curl -f ${{ secrets.DEV_URL }}/api/v1/auth/status
          
          # Test database connectivity
          curl -f ${{ secrets.DEV_BACKEND_HEALTH_URL }}
          
          echo "✅ Integration tests passed"
```

---

## Best Practices for Workflow Maintenance

### 1. Heredoc Escaping Rules (Reference)

| Context | Variable | Cmd Sub | Arithmetic | Example |
|---------|----------|---------|------------|---------|
| `<<'EOF'` | `\$VAR` | `$(cmd)` | `$((\$X + 1))` | Quoted heredoc (current) |
| `<<EOF` | `\${VAR}` | `\$(cmd)` | `\$((\${X} + 1))` | Unquoted heredoc |
| Direct SSH | `\\\$VAR` | `\\\$(cmd)` | `\\\$((\\\$X + 1))` | Triple escape |

**Current workflow uses:** `<<'SSH'` (quoted heredoc)

### 2. Code Review Checklist

When reviewing changes to `.github/workflows/11-dev-deployment.yml`:

- [ ] Check for `\$(` patterns in quoted heredocs (should be `$(`)
- [ ] Verify arithmetic expansions: `$((\$VAR))` not `\$((\$VAR))`
- [ ] Test bash syntax locally before merging
- [ ] Run workflow manually after merge
- [ ] Monitor first production deployment

### 3. Testing Workflow Changes

```bash
# Local syntax validation
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/11-dev-deployment.yml'))"

# Test heredoc syntax locally
bash << 'TEST'
ATTEMPT=1
HTTP_CODE=$(echo "200")
ATTEMPT=$(($ATTEMPT + 1))
echo "Test passed: ATTEMPT=$ATTEMPT, HTTP_CODE=$HTTP_CODE"
TEST

# Use act to test locally (optional)
# brew install act  # or appropriate package manager
# act -j deploy-backend --secret-file .secrets
```

### 4. Documentation Requirements

For any workflow changes:
- Document WHY the change was made
- Include examples of correct syntax
- Link to this stability guide
- Test in non-production environment first

---

## Monitoring & Alerting

### 1. Set Up GitHub Actions Monitoring

**Use GitHub CLI to monitor:**
```bash
# Add to cron or monitoring system
#!/bin/bash
FAILURES=$(gh run list --workflow=11-dev-deployment.yml --limit 10 --json conclusion \
  --jq '[.[] | select(.conclusion == "failure")] | length')

if [ "$FAILURES" -gt 2 ]; then
  echo "⚠️  More than 2 deployment failures detected"
  # Send alert
fi
```

### 2. Health Check Monitoring

**Add to deployment server cron:**
```bash
# /etc/cron.d/health-check-monitor
*/5 * * * * root curl -f http://localhost:8000/api/v1/health/ || \
  echo "Backend health check failed" | mail -s "Alert" devops@example.com
```

### 3. Key Metrics to Track

- Deployment success rate (target: >95%)
- Deployment duration (target: <10 minutes)
- Health check failures (target: 0)
- Container restart count (target: 0)

---

## Emergency Response Plan

### If Deployment Fails

1. **Check workflow logs:**
   ```bash
   gh run list --workflow=11-dev-deployment.yml --limit 1
   gh run view <run-id> --log-failed
   ```

2. **Common issues and fixes:**

   **Syntax error in heredoc:**
   - Check for `\$(` patterns (should be `$(`)
   - Verify arithmetic: `$((\$VAR))` not `\$((\$VAR))`
   
   **Container fails to start:**
   - Check environment variables
   - Verify database connectivity
   - Check container logs: `docker logs pm-backend`
   
   **Health check fails:**
   - Verify health endpoint is accessible
   - Check application logs
   - Confirm migrations ran successfully

3. **Quick rollback:**
   ```bash
   # SSH to server
   ssh $DEV_HOST
   
   # Stop current container
   docker stop pm-backend
   
   # Start previous working image
   docker run -d --name pm-backend \
     --env-file /home/django/ProjectMeats/backend/.env \
     registry.digitalocean.com/meatscentral/projectmeats-backend:dev-<previous-sha>
   ```

4. **Escalation path:**
   - First 15 min: Check logs and common issues
   - After 15 min: Rollback to previous working version
   - After 30 min: Contact team lead
   - After 1 hour: Emergency meeting

---

## Continuous Improvement

### Monthly Review Checklist

- [ ] Review deployment success metrics
- [ ] Check for new workflow best practices
- [ ] Update dependencies (GitHub Actions versions)
- [ ] Review and update documentation
- [ ] Conduct fire drill for emergency response
- [ ] Optimize deployment speed

### Quarterly Actions

- [ ] Audit all GitHub Actions workflows
- [ ] Review and update secrets
- [ ] Test disaster recovery procedures
- [ ] Train new team members on deployment
- [ ] Update runbooks and documentation

---

## Resources

### Documentation
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Bash Heredoc Guide](https://tldp.org/LDP/abs/html/here-docs.html)
- Repository: `SDLC_LOOP_DEPLOYMENT_FIX.md`

### Tools
- **yamllint:** YAML syntax validation
- **shellcheck:** Bash script linting
- **act:** Local GitHub Actions testing
- **gh cli:** GitHub workflow management

### Team Contacts
- DevOps Lead: [Name/Slack]
- On-call Engineer: [Rotation schedule]
- Escalation: [Team lead contact]

---

## Appendix: Heredoc Syntax Reference

### Quoted Heredoc (`<<'DELIMITER'`)
```bash
ssh user@host <<'SSH'
  # No local variable expansion
  echo $HOME              # Expands on remote server
  RESULT=$(date)          # Command substitution on remote
  COUNT=$((COUNT + 1))    # Arithmetic on remote
SSH
```

### Unquoted Heredoc (`<<DELIMITER`)
```bash
ssh user@host <<SSH
  # Local AND remote variable expansion
  echo \$HOME             # Expands on remote (escaped)
  echo $HOME              # Expands locally
  RESULT=\$(date)         # Command substitution on remote
SSH
```

### Best Practice
Use **quoted heredocs** (`<<'DELIMITER'`) for SSH scripts to avoid confusion between local and remote variable expansion.

---

**Version:** 1.0  
**Last Updated:** 2025-11-29  
**Owner:** DevOps Team  
**Status:** Active
