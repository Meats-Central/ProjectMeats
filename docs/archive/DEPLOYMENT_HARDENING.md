# Deployment Pipeline Hardening Guide

## Overview
This document describes the hardened deployment pipeline with multiple safety layers and rollback capabilities.

## Safety Layers

### 1. Pre-Deployment Checks (`pre-deployment-check.sh`)
Validates deployment readiness before proceeding:
- ✅ Environment variables verification
- ✅ Docker daemon health check
- ✅ Registry connectivity test
- ✅ Disk space verification
- ✅ Active deployment detection
- ✅ Deployment artifacts validation

**Usage:**
```bash
.github/scripts/pre-deployment-check.sh dev
```

### 2. Database Backup (`pre-deploy-backup.sh`)
Creates automatic backup before deployment:
- ✅ Full database dump
- ✅ Compressed storage
- ✅ Retention policy (10 backups)
- ✅ Timestamp-based naming

**Usage:**
```bash
.github/scripts/pre-deploy-backup.sh prod $DB_HOST $DB_NAME $DB_USER $DB_PASSWORD
```

### 3. Deployment Lock System
Prevents concurrent deployments:
- ✅ Lock file creation
- ✅ Stale lock detection (10 min timeout)
- ✅ Automatic cleanup
- ✅ Per-environment isolation

### 4. Health Checks & Smoke Tests (`smoke-tests.sh`)
Post-deployment validation:
- ✅ Frontend availability
- ✅ Backend health endpoint
- ✅ API connectivity
- ✅ Response time checks
- ✅ Database connectivity
- ✅ SSL/TLS validation
- ✅ CORS configuration
- ✅ Container health status

**Usage:**
```bash
.github/scripts/smoke-tests.sh https://uat.meatscentral.com 10 5
```

### 5. Rollback Capability (`deployment-rollback.sh`)
Quick recovery from failed deployments:
- ✅ Automatic previous version detection
- ✅ Component-specific rollback (frontend/backend/all)
- ✅ State snapshot creation
- ✅ Rollback verification

**Usage:**
```bash
# Rollback all components
.github/scripts/deployment-rollback.sh prod all

# Rollback only backend
.github/scripts/deployment-rollback.sh prod backend
```

### 6. Deployment Notifications (`deployment-notifications.sh`)
Real-time deployment status updates:
- ✅ GitHub Actions annotations
- ✅ Slack webhook integration (optional)
- ✅ File-based logging
- ✅ Status tracking (started/success/failed/rollback)

**Usage:**
```bash
.github/scripts/deployment-notifications.sh prod started all "Deployment initiated"
.github/scripts/deployment-notifications.sh prod success backend "Backend updated"
.github/scripts/deployment-notifications.sh prod failed frontend "Health check failed"
```

### 7. Blue-Green Deployment Support
Zero-downtime deployment capability:
- ✅ Multiple container versions
- ✅ Traffic switching
- ✅ Quick rollback via tag switch
- ✅ Version history tracking

## Workflow Integration

### Updated Deployment Flow

```yaml
jobs:
  pre-flight:
    - Run pre-deployment checks
    - Create database backup
    - Acquire deployment lock
    - Send "started" notification
  
  build-and-test:
    - Build images
    - Run tests
    - Push to registry
  
  deploy:
    - Pull images
    - Run migrations
    - Deploy containers
    - Wait for stabilization
  
  post-deploy:
    - Run smoke tests
    - Verify health endpoints
    - Release deployment lock
    - Send "success" notification
  
  on-failure:
    - Execute rollback
    - Restore from backup (if needed)
    - Send "failed" notification
    - Create incident report
```

## Environment-Specific Configuration

### Development
- Pre-checks: Basic
- Backup: Optional
- Smoke tests: Essential only
- Notifications: GitHub only

### UAT/Staging
- Pre-checks: Standard
- Backup: Always
- Smoke tests: Full suite
- Notifications: GitHub + Slack

### Production
- Pre-checks: Strict
- Backup: Always + verification
- Smoke tests: Full suite + extended
- Notifications: All channels
- Approval: Required

## Rollback Procedures

### Automatic Rollback Triggers
1. Health check failures (3+ consecutive)
2. Smoke test failures
3. Container crash loops
4. Critical error rate spike

### Manual Rollback
```bash
# Connect to deployment server
ssh user@server

# Run rollback script
sudo /path/to/deployment-rollback.sh prod backend

# Verify rollback
docker ps
curl https://api.example.com/health/
```

### Database Rollback
```bash
# List available backups
ls -lh /tmp/pm-backups/

# Restore specific backup
gunzip < /tmp/pm-backups/pm_prod_20231201_120000.sql.gz | \
  psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

## Monitoring & Alerts

### Key Metrics
- Deployment duration
- Health check response times
- Container restart counts
- Error rates post-deployment
- Database migration times

### Alert Thresholds
- Health check failures: 3 consecutive
- Response time: >2s
- Container restarts: >2 in 5 min
- Error rate: >5% increase

## Security Hardening

### Secrets Management
- ✅ No secrets in code
- ✅ GitHub Secrets for CI/CD
- ✅ Environment-specific secrets
- ✅ Secret rotation tracking

### Access Control
- ✅ Deployment locks
- ✅ Environment protection rules
- ✅ Required approvals (UAT/Prod)
- ✅ Audit logging

### Network Security
- ✅ Registry authentication
- ✅ SSH key-based access
- ✅ HTTPS enforcement
- ✅ CORS configuration

## Disaster Recovery

### Recovery Time Objectives (RTO)
- Development: 30 minutes
- UAT: 15 minutes
- Production: 5 minutes

### Recovery Point Objectives (RPO)
- Development: 24 hours
- UAT: 1 hour
- Production: 15 minutes

### Backup Strategy
1. **Pre-deployment**: Automatic backup before each deployment
2. **Scheduled**: Daily backups at 2 AM UTC
3. **On-demand**: Manual backups before major changes
4. **Retention**: 10 rolling backups per environment

## Testing the Hardened Pipeline

### Pre-Production Testing
```bash
# 1. Test pre-deployment checks
.github/scripts/pre-deployment-check.sh dev

# 2. Test backup creation
.github/scripts/pre-deploy-backup.sh dev localhost test_db postgres password

# 3. Test smoke tests
.github/scripts/smoke-tests.sh http://localhost:8000

# 4. Test rollback (dry run)
.github/scripts/deployment-rollback.sh dev all

# 5. Test notifications
.github/scripts/deployment-notifications.sh dev started all "Test deployment"
```

### Production Validation Checklist
- [ ] All scripts executable and tested
- [ ] Environment variables configured
- [ ] GitHub secrets validated
- [ ] Backup storage configured
- [ ] Notification channels tested
- [ ] Rollback procedure documented
- [ ] Team trained on procedures
- [ ] Incident response plan ready

## Troubleshooting

### Common Issues

#### Pre-deployment Check Failures
```bash
# Check environment variables
env | grep -E "(REGISTRY|IMAGE|TOKEN)"

# Verify Docker
docker info

# Test registry connectivity
ping registry.digitalocean.com
```

#### Smoke Test Failures
```bash
# Check container logs
docker logs pm-backend --tail 100
docker logs pm-frontend --tail 100

# Verify ports
netstat -tulpn | grep -E "(8000|8080)"

# Test endpoints manually
curl -v http://localhost:8000/api/v1/health/
```

#### Rollback Issues
```bash
# List available images
docker images | grep projectmeats

# Check container status
docker ps -a

# View deployment logs
tail -f /tmp/pm-deployment-notifications.log
```

## Maintenance

### Regular Tasks
- **Weekly**: Review deployment logs
- **Monthly**: Test rollback procedures
- **Quarterly**: Update scripts and documentation
- **Annually**: Disaster recovery drill

### Script Updates
All scripts in `.github/scripts/` are version controlled. Update procedures:
1. Test changes in development
2. Create PR with test results
3. Review and approve
4. Deploy to UAT first
5. Monitor and deploy to production

## Contact & Support

- **Deployment Issues**: Check GitHub Actions logs
- **Rollback Assistance**: Refer to rollback section
- **Script Bugs**: Create GitHub issue with label `deployment`

## Version History

- **v1.0**: Initial hardened pipeline (2024-12-01)
  - Pre-deployment checks
  - Automated backups
  - Smoke tests
  - Rollback capability
  - Deployment notifications
