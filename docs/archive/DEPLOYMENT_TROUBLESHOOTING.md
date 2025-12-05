# Deployment Troubleshooting Guide

## Overview
Comprehensive guide for diagnosing and resolving deployment issues across dev, UAT, and production environments.

## Table of Contents
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Common Deployment Issues](#common-deployment-issues)
- [Environment-Specific Issues](#environment-specific-issues)
- [Migration Issues](#migration-issues)
- [Static Files Issues](#static-files-issues)
- [Container Issues](#container-issues)
- [Network & Security Issues](#network--security-issues)
- [Rollback Procedures](#rollback-procedures)

## Pre-Deployment Checklist

### Before Triggering Deployment

- [ ] All CI/CD checks passed
- [ ] Code reviewed and approved
- [ ] Migrations validated locally
- [ ] Environment variables verified
- [ ] Database backup plan confirmed
- [ ] Rollback procedure documented
- [ ] Team notified of deployment

### Verify Environment Configuration

```bash
# Check environment variables are set
.github/scripts/validate-environment.sh

# Verify database connectivity
python manage.py check --database default

# Test migrations (dry-run)
python manage.py migrate --plan
```

## Common Deployment Issues

### Issue 1: CI/CD Workflow Fails

**Symptom:** GitHub Actions workflow fails before deployment

**Common Causes:**
1. Test failures
2. Migration validation errors
3. Build failures
4. Linting errors

**Diagnosis:**
```bash
# Check workflow run logs
gh run view <run-id>

# Get failed job logs
gh run view <run-id> --log-failed

# Check specific test failures
cd backend && python manage.py test apps/ --verbose
```

**Solution:**
1. Review error logs from failed step
2. Reproduce issue locally
3. Fix and push changes
4. Re-run workflow

### Issue 2: Container Fails to Start

**Symptom:** Container exits immediately after starting

**Diagnosis:**
```bash
# SSH into server
ssh user@host

# Check container logs
sudo docker logs pm-backend

# Check container status
sudo docker ps -a | grep pm-backend

# Inspect container
sudo docker inspect pm-backend
```

**Common Causes:**
- Missing environment variables
- Database connection failure
- Port already in use
- Invalid .env file

**Solution:**
```bash
# Verify .env file exists and is readable
sudo ls -la /home/django/ProjectMeats/backend/.env

# Test database connection manually
DATABASE_URL=<value> python manage.py check --database default

# Check port availability
sudo netstat -tuln | grep 8000

# Review environment variables
sudo docker run --rm --env-file /path/to/.env <image> env
```

### Issue 3: Health Check Fails

**Symptom:** Deployment workflow fails at health check step

**Diagnosis:**
```bash
# Test health endpoint manually
curl -v http://server:8000/health/

# Check backend logs
sudo docker logs pm-backend --tail 100

# Verify container is running
sudo docker ps | grep pm-backend
```

**Solution:**
1. Ensure container started successfully
2. Check application logs for errors
3. Verify health endpoint implementation
4. Check firewall rules/security groups

## Environment-Specific Issues

### Development Environment

**Issue:** Dev deployment succeeds but app doesn't work

**Common Causes:**
- CORS configuration missing dev URLs
- CSRF trusted origins not configured
- Static files not collected

**Solution:**
```python
# In development.py, verify:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://dev.meatscentral.com",
    "https://dev-backend.meatscentral.com",
]

CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

ALLOWED_HOSTS = [
    "localhost",
    "dev-backend.meatscentral.com",
]
```

### UAT Environment

**Issue:** Works in dev but breaks in UAT

**Diagnosis:**
```bash
# Compare environment variables
# Dev:
ssh dev-server "sudo cat /home/django/ProjectMeats/backend/.env"

# UAT:
ssh uat-server "sudo cat /home/django/ProjectMeats/backend/.env"

# Compare database migrations
# Dev:
ssh dev-server "sudo docker exec pm-backend python manage.py showmigrations"

# UAT:
ssh uat-server "sudo docker exec pm-backend python manage.py showmigrations"
```

**Solution:**
1. Sync environment variables
2. Ensure migrations are applied
3. Clear cache if applicable
4. Verify media/static file permissions

### Production Environment

**Issue:** Critical error in production

**Immediate Actions:**
1. **Don't panic** - you have backups
2. **Assess impact** - how many users affected?
3. **Check monitoring** - error rates, response times
4. **Decide:** Quick fix or rollback?

**Rollback Procedure:**
```bash
# SSH to production server
ssh prod-server

# Stop current container
sudo docker stop pm-backend

# Pull previous working image
sudo docker pull registry/image:prod-<previous-sha>

# Start with previous image
sudo docker run -d --name pm-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file /home/django/ProjectMeats/backend/.env \
  -v /home/django/ProjectMeats/media:/app/media \
  -v /home/django/ProjectMeats/staticfiles:/app/staticfiles \
  registry/image:prod-<previous-sha>

# Verify health
curl http://localhost:8000/health/
```

## Migration Issues

### Issue: InconsistentMigrationHistory

**Error:**
```
django.db.migrations.exceptions.InconsistentMigrationHistory: 
Migration X is applied before its dependency Y on database 'default'.
```

**Solution:**
See [Migration Best Practices - Troubleshooting](MIGRATION_BEST_PRACTICES.md#inconsistentmigrationhistory-error) for detailed fix procedure.

### Issue: Unapplied Migrations Detected in CI/CD

**Error:**
```
CommandError: Conflicting migrations detected; multiple leaf nodes in the migration graph.
Or: You have unapplied migrations. Run 'python manage.py migrate' to apply them.
```

**Cause:** Model changes were made but migration files were not created/committed, or migrations were created locally but not committed to the repository.

**Prevention:** 
- The pre-commit hook (`validate-django-migrations`) now runs on **every commit** to catch this before pushing
- Always run `pre-commit install` after cloning the repository

**Solution:**
1. **Pull latest changes** to ensure you have the current codebase:
   ```bash
   git pull origin <branch-name>
   ```

2. **Generate missing migration files**:
   ```bash
   cd backend
   python manage.py makemigrations
   ```

3. **Review the generated migrations** to ensure they're correct:
   ```bash
   # Check what migrations were created
   git status
   
   # Review migration content
   cat backend/apps/<app>/migrations/<new_migration>.py
   ```

4. **Commit the new migration file(s)**:
   ```bash
   # Add all new migration files
   git add backend/
   
   # Review what's being committed
   git status
   
   # Commit the changes
   git commit -m "Add missing migration files for model changes"
   ```

5. **Push to re-trigger the CI pipeline**:
   ```bash
   git push
   ```

**Note:** This error is now caught by the pre-commit hook if you have run `pre-commit install`. The hook runs `python manage.py makemigrations --check --dry-run` on every commit to ensure no unapplied migrations exist.

### Issue: Migration Hangs

**Symptom:** Migration process runs for > 5 minutes without completing

**Diagnosis:**
```bash
# Check database locks
docker exec pm-backend python manage.py shell <<EOF
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM pg_stat_activity WHERE state = 'active';")
    print(cursor.fetchall())
EOF
```

**Solution:**
1. Cancel hung migration (Ctrl+C)
2. Check for long-running queries
3. Run migration with `--verbosity 3` for details
4. Consider breaking large migrations into smaller ones

## Static Files Issues

### Issue: Admin CSS/JS Not Loading (404 Errors)

**Symptom:** Django admin loads without styling

**Diagnosis:**
```bash
# Check if static files exist
ssh server "sudo ls -la /home/django/ProjectMeats/staticfiles/admin/"

# Check volume mount
ssh server "sudo docker inspect pm-backend" | grep -A 5 "Mounts"

# Test collectstatic manually
ssh server "sudo docker run --rm --env-file /path/.env <image> python manage.py collectstatic --noinput"
```

**Solution:**
```bash
# Ensure STATIC_DIR exists and has correct permissions
sudo mkdir -p /home/django/ProjectMeats/staticfiles
sudo chown -R 1000:1000 /home/django/ProjectMeats/staticfiles

# Run collectstatic with volume mount
sudo docker run --rm \
  --env-file /home/django/ProjectMeats/backend/.env \
  -v /home/django/ProjectMeats/staticfiles:/app/staticfiles \
  <image> python manage.py collectstatic --noinput

# Verify files collected
sudo ls -la /home/django/ProjectMeats/staticfiles/

# Restart backend container with volume mounted
# (See deployment workflow for full command)
```

## Container Issues

### Issue: Container Exits with Code 137

**Meaning:** Container was killed (usually OOM - Out of Memory)

**Diagnosis:**
```bash
# Check container memory usage before crash
sudo docker stats --no-stream

# Check system memory
free -h

# Review Docker logs for OOM
sudo dmesg | grep -i 'out of memory'
```

**Solution:**
1. Increase container memory limit
2. Optimize application memory usage
3. Review for memory leaks
4. Add swap space if needed

### Issue: Port Already in Use

**Error:** `bind: address already in use`

**Solution:**
```bash
# Find process using port
sudo lsof -i :8000
sudo netstat -tuln | grep 8000

# Stop conflicting container
sudo docker ps | grep 8000
sudo docker stop <container-name>

# Or kill process
sudo kill <pid>
```

## Network & Security Issues

### Issue: CORS Errors in Browser

**Symptom:** Frontend can't make API requests, browser console shows CORS errors

**Solution:**
```python
# Verify CORS configuration in settings
CORS_ALLOWED_ORIGINS = [
    "https://app.meatscentral.com",
    "https://www.meatscentral.com",
]

# Or for development (NOT production!)
CORS_ALLOW_ALL_ORIGINS = True  # DEV ONLY!
```

**Test:**
```bash
# Test CORS headers
curl -H "Origin: https://app.meatscentral.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://api.meatscentral.com/api/v1/customers/ -v
```

### Issue: CSRF Verification Failed (403)

**Symptom:** Admin login fails with 403 error

**Solution:**
```python
# Add to settings
CSRF_TRUSTED_ORIGINS = [
    "https://app.meatscentral.com",
    "https://backend.meatscentral.com",
]

# Ensure it matches CORS_ALLOWED_ORIGINS
# They should generally be the same
```

### Issue: Database Connection Refused

**Error:** `could not connect to server: Connection refused`

**Diagnosis:**
```bash
# Test database connectivity from container
sudo docker run --rm --env-file /path/.env <image> python manage.py check --database default

# Test from host
psql -h <db-host> -U <db-user> -d <db-name>

# Check firewall rules
sudo ufw status
```

**Solution:**
1. Verify DATABASE_URL is correct
2. Check database server is running
3. Verify network connectivity
4. Check firewall/security group rules
5. Verify database credentials

## Rollback Procedures

### Application Rollback (Code-Only)

```bash
# 1. Identify last working commit/image
git log --oneline -10
# Or check Docker registry for previous image

# 2. SSH to server
ssh server

# 3. Stop current container
sudo docker stop pm-backend
sudo docker rm pm-backend

# 4. Pull previous image
sudo docker pull registry/image:env-<previous-sha>

# 5. Start with previous image (same .env)
sudo docker run -d --name pm-backend --restart unless-stopped \
  -p 8000:8000 \
  --env-file /home/django/ProjectMeats/backend/.env \
  -v /home/django/ProjectMeats/media:/app/media \
  -v /home/django/ProjectMeats/staticfiles:/app/staticfiles \
  registry/image:env-<previous-sha>

# 6. Verify health
curl http://localhost:8000/health/
```

### Database Rollback (With Migrations)

```bash
# 1. Check available backups
ls -lh /home/django/ProjectMeats/backups/

# 2. Identify backup to restore (before failed migration)
# Format: db_backup_YYYYMMDD_HHMMSS.sql.gz

# 3. Stop application
sudo docker stop pm-backend

# 4. Restore database
gunzip -c /path/to/backup.sql.gz | \
  PGPASSWORD=<pass> psql -h <host> -U <user> <dbname>

# 5. Verify restoration
PGPASSWORD=<pass> psql -h <host> -U <user> <dbname> -c "SELECT COUNT(*) FROM django_migrations;"

# 6. Start application with previous code version
# (See application rollback steps above)

# 7. Verify migration state
sudo docker exec pm-backend python manage.py showmigrations
```

### Full Environment Rollback

For catastrophic failures:

1. **Restore database** from backup
2. **Deploy previous code** version
3. **Restore media files** if needed (from backup)
4. **Clear cache** (Redis/Memcached)
5. **Verify all services** are healthy
6. **Monitor** for 30 minutes
7. **Document** what went wrong
8. **Plan fix** for next deployment

## Monitoring & Alerts

### Key Metrics to Watch Post-Deployment

- **Error Rate:** Should be < 1% within 15 minutes
- **Response Time:** Should be < 500ms p95
- **Database Connections:** Should stabilize within 5 minutes
- **Memory Usage:** Should be < 80% container limit
- **CPU Usage:** Should be < 70% average

### Setting Up Alerts

```bash
# Example: Alert on high error rate
# Add to monitoring system (Datadog, New Relic, etc.)
error_rate > 5% for 5 minutes → page oncall
response_time_p95 > 2s for 10 minutes → notify team
container_restart → immediate alert
database_connection_failed → critical alert
```

## Getting Help

### Escalation Path

1. **Check this guide** first
2. **Review [copilot-log.md](../copilot-log.md)** for similar issues
3. **Check GitHub Actions** logs
4. **Review [Migration Best Practices](MIGRATION_BEST_PRACTICES.md)**
5. **Contact team lead** if issue persists
6. **Create incident** for production issues

### Useful Commands Reference

```bash
# View logs
sudo docker logs pm-backend --tail 100 -f

# Execute commands in container
sudo docker exec -it pm-backend bash
sudo docker exec pm-backend python manage.py shell

# Check migrations
sudo docker exec pm-backend python manage.py showmigrations

# Run management command
sudo docker exec pm-backend python manage.py <command>

# Check container health
sudo docker inspect pm-backend | grep Health

# View container resources
sudo docker stats pm-backend --no-stream

# Restart container
sudo docker restart pm-backend
```

## Post-Incident Review

After resolving an issue:

1. **Document** the problem and solution
2. **Update** this guide if needed
3. **Add to** copilot-log.md lessons learned
4. **Create ticket** to prevent recurrence
5. **Update monitoring** if gap identified
6. **Share learnings** with team

---

**Last Updated:** 2025-12-04  
**Version:** 1.1  
**Maintained By:** DevOps Team
