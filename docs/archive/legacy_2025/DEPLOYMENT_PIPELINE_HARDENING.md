# Deployment Pipeline Hardening Guide

**Status**: Production-Ready  
**Last Updated**: 2024-12-01  
**Maintainer**: DevOps Team

## Overview

This document describes the hardening measures implemented to ensure deployment pipeline reliability, security, and resilience.

---

## 🛡️ Hardening Measures Implemented

### 1. Pre-commit Hooks

**Purpose**: Catch issues before they reach CI/CD

**Configuration**: `.pre-commit-config-deployment.yaml`

**Checks**:
- ✅ YAML syntax validation
- ✅ Shell script linting (shellcheck)
- ✅ Python formatting (black, flake8)
- ✅ Secret detection
- ✅ Django migrations check
- ✅ Workflow validation
- ✅ Dockerfile linting

**Setup**:
```bash
pip install pre-commit
pre-commit install --config .pre-commit-config-deployment.yaml
```

---

### 2. Workflow Health Monitoring

**Workflow**: `.github/workflows/workflow-health-monitor.yml`

**Features**:
- Runs every 6 hours automatically
- Checks for recent workflow failures
- Monitors deployment durations
- Validates workflow configurations
- Generates health reports

**Alerts**:
- High failure rate (>5 failures in 24h)
- Slow deployments (>15 minutes)
- Configuration issues

---

### 3. Deployment Health Checks

**Script**: `.github/scripts/deployment-health-check.sh`

**Pre-Deployment Checks**:
- Environment variables validation
- Database connectivity
- Migration status
- Disk space availability

**Post-Deployment Checks**:
- Container health
- HTTP health endpoint
- Static files presence
- Log error analysis

**Usage**:
```bash
# Before deployment
./deployment-health-check.sh pre

# After deployment
./deployment-health-check.sh post

# Health check only
HEALTH_CHECK_URL=http://localhost:8000/api/v1/health/ \
  ./deployment-health-check.sh health
```

---

### 4. Workflow Validation

**Script**: `.github/scripts/validate-workflows.sh`

**Validations**:
- YAML syntax
- Required secrets presence
- Cache configuration
- Health check steps
- fetch-depth settings
- Error handling
- Timeout configurations
- Retry logic
- Migration safety
- Concurrency control
- Environment separation

**Usage**:
```bash
./validate-workflows.sh
```

---

### 5. Timeout Configurations

All jobs now have appropriate timeouts:

| Job | Timeout | Reason |
|-----|---------|--------|
| build-and-push | 45min | Docker builds can be slow on cold cache |
| test-frontend | 15min | Tests should complete quickly |
| test-backend | 20min | Database setup + tests |
| deploy-frontend | 20min | Image pull + container start |
| deploy-backend | 30min | Migrations + health checks |

**Benefits**:
- Prevents hung workflows
- Faster failure detection
- Resource conservation

---

### 6. Fail-Fast Strategy

**Configuration**:
```yaml
strategy:
  matrix:
    app: [ frontend, backend ]
  fail-fast: false  # Continue other jobs even if one fails
```

**Benefits**:
- See all failures, not just first
- Parallel job completion
- Better debugging information

---

### 7. Retry Logic

**Health Checks**:
```bash
MAX_RETRIES=30
RETRY_DELAY=10

for i in {1..30}; do
  if health_check; then
    echo "Success"
    exit 0
  fi
  sleep 10
done
```

**Benefits**:
- Handles transient failures
- Network blips don't fail deployments
- Configurable retry behavior

---

### 8. Rollback Capability

**Implementation**: `deployment-health-check.sh rollback`

**Process**:
1. Detects deployment failure
2. Stops new container
3. Restores previous container from backup
4. Validates rollback success

**Usage**:
```bash
# Automatic rollback on failure
if ! post_deployment_checks; then
  rollback
  exit 1
fi
```

---

### 9. Environment Variable Validation

**Checks**:
- Required variables present
- No empty values
- Correct formats (URLs, etc.)

**Critical Variables**:
- `DJANGO_SETTINGS_MODULE`
- `SECRET_KEY`
- `DATABASE_URL`
- `ALLOWED_HOSTS`

---

### 10. Docker Cache Management

**Features**:
- Automatic cache cleanup (>7 days old)
- Dangling image removal
- Cache size monitoring

**Script**: Built into `deployment-health-check.sh cleanup`

**Scheduling**:
```yaml
# Run weekly
- cron: '0 2 * * 0'
```

---

## 🔒 Security Hardening

### Secret Management

1. **Never commit secrets** ✅
   - Pre-commit hook detects secrets
   - `.secrets.baseline` for false positives

2. **Environment-specific secrets** ✅
   - DEV_*, UAT_*, PROD_* prefixes
   - No shared secrets between environments

3. **Minimal secret scope** ✅
   - Secrets only where needed
   - Environment protection rules

### Access Control

1. **Branch Protection** ✅
   - No direct pushes to main/uat/development
   - Required reviews
   - Status checks must pass

2. **Environment Protection** ✅
   - Required reviewers for production
   - Deployment branches restricted

3. **Least Privilege** ✅
   - Minimal GitHub token permissions
   - SSH with limited sudo access

---

## 📊 Monitoring & Alerting

### Metrics Tracked

1. **Performance**:
   - Build duration
   - Test duration
   - Deploy duration
   - Cache hit rate

2. **Reliability**:
   - Failure rate
   - Rollback frequency
   - Health check pass rate

3. **Resources**:
   - Disk usage
   - Cache size
   - Action minutes consumed

### Alert Conditions

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Failure rate | >5 in 24h | Investigate immediately |
| Deploy duration | >15min | Check cache, optimize |
| Disk usage | >90% | Clean up immediately |
| Cache miss rate | >30% | Review cache keys |

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Deployment Timeout

**Symptoms**:
- Job exceeds timeout limit
- Workflow cancelled mid-deployment

**Solutions**:
```bash
# Increase timeout in workflow
timeout-minutes: 45  # Adjust as needed

# Check for hung processes
docker ps -a
docker logs pm-backend --tail 100

# Manual intervention
ssh user@host 'docker restart pm-backend'
```

#### 2. Cache Miss

**Symptoms**:
- Builds taking full 8+ minutes
- No "cache hit" messages in logs

**Solutions**:
```bash
# Check cache keys
grep "buildx-cache" .github/workflows/*.yml

# Verify hash files exist
ls -la frontend/package-lock.json
ls -la backend/requirements.txt

# Manual cache cleanup
gh cache delete --all
```

#### 3. Health Check Failure

**Symptoms**:
- Deployment completes but health check fails
- Container running but not responsive

**Solutions**:
```bash
# Check container logs
docker logs pm-backend --tail 100

# Check container health
docker inspect pm-backend | jq '.[0].State'

# Manual health check
curl -v http://localhost:8000/api/v1/health/

# Check database connection
docker exec pm-backend python manage.py check --database default
```

#### 4. Migration Conflicts

**Symptoms**:
- "Migration XYZ is applied before its dependency"
- Database schema mismatch

**Solutions**:
```bash
# Check migration status
python manage.py showmigrations

# Generate missing migrations
python manage.py makemigrations

# Fake migrate if necessary (dangerous!)
python manage.py migrate --fake app_name migration_name

# Rollback and re-apply
python manage.py migrate app_name zero
python manage.py migrate app_name
```

---

## 📋 Maintenance Checklist

### Weekly

- [ ] Review workflow health report
- [ ] Check cache hit rates
- [ ] Monitor disk usage
- [ ] Review failed deployments

### Monthly

- [ ] Update dependencies
- [ ] Review and update timeouts
- [ ] Clean up old workflow runs
- [ ] Update documentation
- [ ] Security audit

### Quarterly

- [ ] Performance review
- [ ] Optimize cache strategies
- [ ] Review alert thresholds
- [ ] Team training updates

---

## 🚨 Incident Response

### Deployment Failure

1. **Immediate**:
   ```bash
   # Check status
   gh run list --limit 5
   
   # View logs
   gh run view <run-id> --log-failed
   
   # Rollback if necessary
   ./deployment-health-check.sh rollback
   ```

2. **Investigation**:
   - Check error logs
   - Review recent changes
   - Validate environment
   - Test locally

3. **Resolution**:
   - Fix root cause
   - Test fix
   - Re-deploy
   - Update documentation

### Production Outage

1. **Assess** (1-2 min):
   - Check health endpoints
   - Review monitoring dashboards
   - Identify affected services

2. **Mitigate** (5-10 min):
   - Rollback if deployment-related
   - Scale up if capacity issue
   - Redirect traffic if needed

3. **Resolve** (varies):
   - Fix root cause
   - Validate fix in staging
   - Deploy to production
   - Monitor closely

4. **Post-Mortem**:
   - Document incident
   - Identify improvements
   - Update runbooks
   - Share learnings

---

## 📖 Best Practices

### DO ✅

1. **Always test locally first**
2. **Use feature flags for risky changes**
3. **Deploy during business hours (for major changes)**
4. **Monitor deployments actively**
5. **Keep deployment windows short**
6. **Document all changes**
7. **Run pre-deployment checks**
8. **Have rollback plan ready**

### DON'T ❌

1. **Don't skip pre-commit hooks**
2. **Don't commit secrets**
3. **Don't deploy untested code**
4. **Don't ignore health check failures**
5. **Don't deploy on Fridays (major changes)**
6. **Don't rush deployments**
7. **Don't ignore warnings**
8. **Don't delete migration files**

---

## 🔄 Continuous Improvement

### Feedback Loop

1. **Collect** metrics and feedback
2. **Analyze** patterns and trends
3. **Plan** improvements
4. **Implement** changes
5. **Validate** effectiveness
6. **Repeat**

### Metrics for Improvement

- Deployment frequency
- Lead time for changes
- Mean time to recovery
- Change failure rate
- Developer satisfaction

---

## 📞 Support

**Documentation**:
- This guide
- DEPLOYMENT_WORKFLOW_OPTIMIZATION.md
- DEPLOYMENT_WORKFLOW_OPTIMIZATION_PHASE2.md

**Tools**:
- `deployment-health-check.sh`
- `validate-workflows.sh`
- Workflow Health Monitor

**Contacts**:
- DevOps Team: #devops
- On-call: Check PagerDuty
- Emergency: Escalation matrix

---

**Version**: 1.0.0  
**Status**: Production  
**Next Review**: 2025-01-01
