# Deployment Pipeline - Quick Reference

## 🚀 Quick Commands

### Monitoring
```bash
# View deployment status
python3 .github/scripts/deployment-monitor.py

# Continuous monitoring
python3 .github/scripts/deployment-monitor.py --watch

# JSON output for scripting
python3 .github/scripts/deployment-monitor.py --json
```

### Health Checks
```bash
# Run smoke tests
.github/scripts/smoke-tests.sh https://uat.meatscentral.com

# Run with custom retries
.github/scripts/smoke-tests.sh https://meatscentral.com 20 5
```

### Rollback
```bash
# Rollback all components
.github/scripts/deployment-rollback.sh prod all

# Rollback specific component
.github/scripts/deployment-rollback.sh prod backend
```

### Pre-deployment
```bash
# Run pre-deployment checks
.github/scripts/pre-deployment-check.sh prod

# Create manual backup
.github/scripts/pre-deploy-backup.sh prod $DB_HOST $DB_NAME $DB_USER $DB_PASSWORD
```

## 🔒 Safety Features

### Enabled by Default
✅ Pre-deployment validation  
✅ Automatic database backups  
✅ Deployment locks (prevents concurrent deployments)  
✅ Health checks with retries  
✅ Post-deployment smoke tests  
✅ Deployment notifications  
✅ Rollback capability  

### Concurrency Protection
- Development: No restrictions
- UAT: Single deployment at a time
- Production: Single deployment at a time (enforced via `concurrency.group`)

### Automatic Rollback Triggers
- Health check failures (3+ consecutive)
- Container crash loops
- Smoke test failures

## 📊 Monitoring

### Real-time Dashboard
```bash
# Local server monitoring
ssh user@server
python3 /path/to/deployment-monitor.py --watch
```

### Key Metrics
- Container status (running/stopped)
- Health check status (healthy/unhealthy)
- Disk space usage
- Recent deployments
- Active deployment locks
- Recent error logs

## 🔄 Deployment Flow

### Development → UAT
1. Push to `development` branch
2. Automated PR created to `uat`
3. Review and approve PR
4. Merge triggers UAT deployment
5. Smoke tests run automatically

### UAT → Production
1. Push to `uat` branch (via merge)
2. Automated PR created to `main`
3. **Required approval**
4. Merge triggers production deployment
5. Full validation suite runs
6. Success notification sent

## ⚠️ Emergency Procedures

### Quick Rollback
```bash
# SSH to production server
ssh django@production-server

# Run rollback
sudo /home/django/ProjectMeats/.github/scripts/deployment-rollback.sh prod all

# Verify rollback
docker ps
curl https://meatscentral.com/api/v1/health/
```

### Database Restore
```bash
# List backups
ls -lh /tmp/pm-backups/

# Find latest backup
LATEST=$(ls -t /tmp/pm-backups/pm_prod_*.sql.gz | head -1)

# Restore
gunzip < $LATEST | psql -h $DB_HOST -U $DB_USER -d $DB_NAME
```

### Force Container Restart
```bash
# Restart backend
docker restart pm-backend

# Restart frontend
docker restart pm-frontend

# Check logs
docker logs pm-backend --tail 100
```

## 📝 Troubleshooting

### Deployment Stuck
```bash
# Check for locks
ls -l /tmp/pm-deploy-*.lock

# Remove stale lock (if > 10 min old)
rm -f /tmp/pm-deploy-prod.lock

# Retry deployment
```

### Health Check Failing
```bash
# Check container status
docker ps -a | grep pm-

# View logs
docker logs pm-backend --tail 100

# Check network
curl -v http://localhost:8000/api/v1/health/

# Restart if needed
docker restart pm-backend
```

### Disk Space Full
```bash
# Check disk usage
df -h

# Clean old Docker images
docker image prune -a --filter "until=72h"

# Clean old backups
find /tmp/pm-backups -name "*.sql.gz" -mtime +7 -delete
```

## 🔐 Security Checklist

### Pre-Deployment
- [ ] All secrets configured in GitHub
- [ ] Environment variables validated
- [ ] Database backup created
- [ ] No sensitive data in logs
- [ ] SSL certificates valid

### Post-Deployment
- [ ] Health checks passing
- [ ] Smoke tests completed
- [ ] No error spikes in logs
- [ ] Response times normal
- [ ] Database migrations applied
- [ ] Static files served correctly

## 📞 Support

### Documentation
- Full guide: `docs/DEPLOYMENT_HARDENING.md`
- Scripts README: `.github/scripts/README.md`
- Workflow docs: `.github/workflows/README.md`

### Logs
- Deployment logs: GitHub Actions
- Container logs: `docker logs pm-backend`
- Notification log: `/tmp/pm-deployment-notifications.log`
- Backup logs: `/tmp/pm-backups/`

### Key Files
- Health check: `health_check.py`
- Smoke tests: `.github/scripts/smoke-tests.sh`
- Rollback: `.github/scripts/deployment-rollback.sh`
- Monitor: `.github/scripts/deployment-monitor.py`
