# Deployment Runbook

**Quick Reference for Deployment Operations**

## 🚀 Standard Deployment

### Pre-Deployment

```bash
# 1. Ensure you're on the correct branch
git checkout development
git pull origin development

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes and commit
git add .
git commit -m "feat: description"

# 4. Run pre-commit checks (if configured)
pre-commit run --all-files

# 5. Push to remote
git push origin feature/my-feature
```

### Creating Pull Request

```bash
# Using GitHub CLI
gh pr create \
  --base development \
  --head feature/my-feature \
  --title "feat: description" \
  --body "Description of changes"
```

### Monitoring Deployment

```bash
# Watch workflow status
gh run watch

# View logs in real-time
gh run view --log

# List recent runs
gh run list --limit 5
```

---

## ⚠️ Emergency Procedures

### Production Down

```bash
# 1. Check status
gh run list --workflow="Deploy Prod" --limit 3

# 2. View failed run
gh run view <run-id> --log-failed

# 3. Quick rollback (if deployment-related)
gh workflow run "Deploy Prod" \
  --ref main \
  --field rollback=true

# 4. Or manual rollback
ssh user@prod-host << 'EOF'
  docker stop pm-backend
  docker rename pm-backend pm-backend-failed
  docker rename pm-backend-backup pm-backend
  docker start pm-backend
EOF
```

### Health Check Failures

```bash
# 1. Check container logs
ssh user@host 'docker logs pm-backend --tail 100'

# 2. Check container status
ssh user@host 'docker ps -a | grep pm-'

# 3. Restart if needed
ssh user@host 'docker restart pm-backend'

# 4. Verify health
curl https://api.example.com/api/v1/health/
```

### Database Issues

```bash
# 1. Check database connection
ssh user@host 'docker exec pm-backend python manage.py check --database default'

# 2. Check migration status
ssh user@host 'docker exec pm-backend python manage.py showmigrations'

# 3. Manual migration (if safe)
ssh user@host 'docker exec pm-backend python manage.py migrate'
```

---

## 🔧 Troubleshooting

### Build Failures

**Symptom**: Docker build fails

```bash
# 1. Check build logs
gh run view --log | grep "Build & Push"

# 2. Test build locally
docker build -f frontend/dockerfile -t test .

# 3. Check cache
gh cache list
gh cache delete --all  # If cache corrupted
```

### Test Failures

**Symptom**: Tests fail in CI but pass locally

```bash
# 1. Run tests with same environment
docker-compose -f docker-compose.test.yml up

# 2. Check for environment-specific issues
# - Database version
# - Python version
# - Node version

# 3. Review test logs
gh run view --log | grep "test"
```

### Deployment Hangs

**Symptom**: Deployment stuck, no progress

```bash
# 1. Check runner status
gh run view <run-id>

# 2. Cancel if needed
gh run cancel <run-id>

# 3. Check remote host
ssh user@host 'top'  # CPU usage
ssh user@host 'df -h'  # Disk space
ssh user@host 'docker ps -a'  # Container status
```

---

## 📊 Health Checks

### Manual Health Checks

```bash
# Backend
curl -f https://api.example.com/api/v1/health/ | jq

# Frontend
curl -f https://app.example.com/ | head

# Database
ssh user@host 'docker exec pm-backend python manage.py check --database default'

# Cache
ssh user@host 'docker exec pm-backend python manage.py shell -c "from django.core.cache import cache; print(cache.get(\"test\"))"'
```

### Automated Health Monitoring

```bash
# Run health check script
./github/scripts/deployment-health-check.sh health

# View health report
gh run list --workflow="Workflow Health Monitor"
gh run view <run-id>
```

---

## 🔄 Rollback Procedures

### Automatic Rollback

**Trigger**: Post-deployment health check fails

```yaml
# Already configured in workflows
- name: Health check
  run: |
    if ! health_check; then
      rollback
      exit 1
    fi
```

### Manual Rollback

**When to use**: Discovered issues after deployment

```bash
# 1. Identify last good deployment
gh run list --workflow="Deploy Prod" --status success --limit 5

# 2. Get commit SHA
gh run view <run-id> --json headSha

# 3. Revert to that version
git revert <bad-commit-sha>
git push origin main

# Or redeploy previous version
git checkout <good-commit-sha>
git push origin temp-rollback
# Then create PR from temp-rollback to main
```

### Database Rollback

**⚠️ DANGEROUS - Use with extreme caution**

```bash
# 1. Backup first!
ssh user@host 'docker exec pm-backend python manage.py dumpdata > backup.json'

# 2. Rollback migration
ssh user@host 'docker exec pm-backend python manage.py migrate app_name migration_number'

# 3. Verify
ssh user@host 'docker exec pm-backend python manage.py showmigrations'
```

---

## 📈 Performance Optimization

### Cache Warming

```bash
# After deployment, warm up cache
curl https://api.example.com/api/v1/popular-endpoints/

# Or run warm-up script
ssh user@host 'docker exec pm-backend python manage.py warm_cache'
```

### Monitoring Performance

```bash
# Check deployment duration
gh run list --workflow="Deploy Prod" --json durationMs

# Check cache hit rate
# (View in workflow logs under "Cache Docker layers")

# Check resource usage
ssh user@host 'docker stats --no-stream'
```

---

## 🔒 Security Operations

### Rotating Secrets

```bash
# 1. Generate new secret
openssl rand -base64 32

# 2. Update in GitHub Secrets
gh secret set SECRET_KEY

# 3. Redeploy to apply
gh workflow run "Deploy Prod"

# 4. Verify
curl https://api.example.com/api/v1/health/
```

### Security Audit

```bash
# 1. Check for secrets in code
git grep -i "password\|secret\|key" | grep -v ".md"

# 2. Run security scan
bandit -r backend/

# 3. Check dependencies
pip-audit
npm audit

# 4. Review access logs
ssh user@host 'tail -n 100 /var/log/nginx/access.log'
```

---

## 📞 Escalation

### Level 1: Self-Service
- Check this runbook
- Review documentation
- Check workflow logs

### Level 2: Team Support
- Post in #devops Slack
- Tag @devops-team
- Include run ID and error logs

### Level 3: On-Call
- PagerDuty alert
- Production outage only
- Include incident details

### Level 4: Emergency
- Multiple systems down
- Data loss risk
- Security breach
- Page CTO/Engineering Manager

---

## 📝 Checklist Templates

### Pre-Deployment Checklist

- [ ] Feature branch created from development
- [ ] Code reviewed and approved
- [ ] Tests passing locally
- [ ] Pre-commit hooks run
- [ ] Migration files committed (if applicable)
- [ ] Documentation updated
- [ ] PR approved and merged

### Post-Deployment Checklist

- [ ] Deployment completed successfully
- [ ] Health checks passing
- [ ] No errors in logs
- [ ] Performance acceptable
- [ ] Monitoring dashboards green
- [ ] Stakeholders notified

### Rollback Checklist

- [ ] Issue identified and documented
- [ ] Rollback decision approved
- [ ] Backup created (if DB changes)
- [ ] Rollback executed
- [ ] Health checks passing
- [ ] Issue resolved or mitigated
- [ ] Post-mortem scheduled

---

## 🎯 Quick Commands

```bash
# Deploy to development
git push origin development

# Deploy to UAT (via PR)
gh pr create --base uat --head development

# Deploy to production (via PR)
gh pr create --base main --head uat

# Check deployment status
gh run list --limit 5

# View logs
gh run view --log-failed

# Cancel deployment
gh run cancel <run-id>

# Rollback
git revert <commit>
git push origin <branch>

# Health check
curl https://api.example.com/api/v1/health/

# Container logs
ssh user@host 'docker logs pm-backend --tail 100'

# Restart container
ssh user@host 'docker restart pm-backend'
```

---

**Last Updated**: 2024-12-01  
**Maintained By**: DevOps Team  
**Version**: 1.0.0
