# ProjectMeats Unified Deployment Workflow Documentation

## Overview
ProjectMeats uses a unified GitHub Actions workflow that automates testing and deployment across three environments: Development, UAT2 (Staging), and Production. The workflow is built with intelligent change detection, automated testing, and robust health checks. It deploys a Django backend and React frontend to DigitalOcean droplets using SSH-based deployment with supervisor and nginx.

This documentation covers:
- Workflow architecture and triggers
- Environment configuration
- Deployment process and flow
- Rollback procedures
- Troubleshooting guide

## 1. Workflow Architecture

### Infrastructure Overview
The deployment infrastructure consists of:
- **Three Environment Tiers**:
  - **Development (DEV)**: Rapid iteration and testing environment, deployed from `development` branch
  - **UAT2 (Staging)**: Pre-production validation environment, deployed from `development` branch
  - **Production (PROD)**: Live production environment, deployed from `main` branch

- **Technology Stack**:
  - **Backend**: Django with Gunicorn, managed by Supervisor
  - **Frontend**: React SPA (Single Page Application)
  - **Web Server**: Nginx for reverse proxy and static file serving
  - **Process Manager**: Supervisor for backend process management
  - **Deployment Method**: SSH-based deployment with sshpass

- **Branch Strategy**:
  - `development` branch → Deploys to **Development** AND **UAT2 Staging**
  - `main` branch → Deploys to **Production**

### Architecture Diagram
```
GitHub Repository (Push Trigger)
    |
    ├─── development branch
    |    ├─── Deploy to Development
    |    └─── Deploy to UAT2 Staging
    |
    └─── main branch
         └─── Deploy to Production

Each Environment:
┌─────────────────────────────────┐
│  DigitalOcean Droplet           │
│  ┌───────────────────────────┐  │
│  │  Nginx (Reverse Proxy)    │  │
│  └───────────┬───────────────┘  │
│              │                   │
│     ┌────────┴────────┐         │
│     │                 │         │
│  ┌──▼────┐      ┌────▼──────┐  │
│  │Backend│      │ Frontend  │  │
│  │Django │      │  React    │  │
│  │+Gunic.│      │   SPA     │  │
│  │Super. │      │  (build)  │  │
│  └───────┘      └───────────┘  │
│     │                           │
│  ┌──▼────┐                      │
│  │PostgreSQL                    │
│  │Database│                     │
│  └────────┘                     │
└─────────────────────────────────┘
```

## 2. Workflow Triggers and Jobs

### Triggers
The workflow (`unified-deployment.yml`) is triggered by:
- **Push Events**: Automatically triggers on push to `main` or `development` branches
- **Manual Dispatch**: Can be manually triggered via GitHub Actions UI with options:
  - `deploy`: Normal deployment
  - `rollback`: Emergency rollback to previous version

### Job Flow
```
┌─────────────────────────┐
│  detect-changes         │ ← Detects backend/frontend changes
└───────────┬─────────────┘
            │
     ┌──────┴──────┐
     │             │
┌────▼────┐   ┌───▼─────┐
│test-    │   │test-    │ ← Run tests in parallel
│backend  │   │frontend │
└────┬────┘   └───┬─────┘
     │            │
     └──────┬─────┘
            │
  ┌─────────┴──────────┐
  │                    │
  │  If development branch:
  │  ┌─────────────────────────┐
  │  │ deploy-backend-dev      │
  │  │ deploy-frontend-dev     │
  │  │ deploy-backend-staging  │
  │  │ deploy-frontend-staging │
  │  └─────────────────────────┘
  │
  │  If main branch:
  │  ┌──────────────────────┐
  │  │ deploy-backend-prod  │
  │  │ deploy-frontend-prod │
  │  └──────────────────────┘
  │
  └────────────────────────┘
```

### Jobs Overview

1. **detect-changes**:
   - Compares HEAD with previous commit to identify changed files
   - Outputs `backend: true/false` and `frontend: true/false`
   - Manual triggers deploy both backend and frontend

2. **test-backend**:
   - Sets up PostgreSQL test database
   - Installs Python dependencies
   - Runs Django tests and migrations
   - Performs code quality checks (flake8, black)

3. **test-frontend**:
   - Sets up Node.js environment
   - Installs npm dependencies
   - Runs Jest/React tests
   - Performs TypeScript type checking

4. **deploy-backend-{environment}**:
   - Deploys Django backend to target environment
   - Runs database migrations
   - Collects static files
   - Restarts supervisor services

5. **deploy-frontend-{environment}**:
   - Builds React production bundle
   - Deploys to web server
   - Reloads nginx configuration

## 3. Environment Configuration

### Required GitHub Secrets

#### Repository-Level Secrets (Shared)
- `GIT_TOKEN`: GitHub Personal Access Token for repository access
- `SSH_PASSWORD`: SSH password for staging server
- `DEV_SSH_PASSWORD`: SSH password for development server

#### Development Environment (`dev-backend` and `dev-frontend`)

**Server Access:**
- `DEV_HOST`: Development server IP/hostname
- `DEV_USER`: SSH username (typically `django`)
- `DEV_SSH_PASSWORD`: SSH password for development server

**Backend Secrets:**
- `DEV_API_URL`: Backend API URL (e.g., `https://dev-api.yourdomain.com`)

**Frontend Secrets:**
- `DEV_URL`: Frontend URL (e.g., `https://dev.yourdomain.com`)
- `REACT_APP_API_BASE_URL`: Backend API URL for frontend
- `REACT_APP_AI_ASSISTANT_ENABLED`: Enable AI features (true/false)
- `REACT_APP_ENABLE_DOCUMENT_UPLOAD`: Enable document uploads (true/false)
- `REACT_APP_ENABLE_CHAT_EXPORT`: Enable chat exports (true/false)
- `REACT_APP_MAX_FILE_SIZE`: Max upload size in bytes
- `REACT_APP_SUPPORTED_FILE_TYPES`: Allowed file extensions
- `REACT_APP_ENABLE_DEBUG`: Debug mode (true for dev)
- `REACT_APP_ENABLE_DEVTOOLS`: DevTools enabled (true for dev)

#### Staging Environment (`uat2-backend` and `uat2`)

**Server Access:**
- `STAGING_HOST`: Staging server IP/hostname
- `STAGING_USER`: SSH username
- `SSH_PASSWORD`: SSH password for staging server

**Backend Secrets:**
- `STAGING_API_URL`: Staging backend API URL

**Frontend Secrets:**
- `STAGING_URL`: Staging frontend URL
- `REACT_APP_API_BASE_URL`: Staging backend API URL
- (Same REACT_APP_* variables as development)

#### Production Environment (`prod2-backend` and `prod2-frontend`)

**Server Access:**
- `PRODUCTION_HOST`: Production server IP/hostname
- `PRODUCTION_USER`: SSH username
- `SSH_PASSWORD`: SSH password for production server

**Backend Secrets:**
- `PRODUCTION_API_URL`: Production backend API URL

**Frontend Secrets:**
- `PRODUCTION_URL`: Production frontend URL
- `REACT_APP_API_BASE_URL`: Production backend API URL
- (Same REACT_APP_* variables, but with debug/devtools set to false)

### Server Configuration Requirements

Each server must have:
1. **Directory Structure**:
   ```
   /home/django/ProjectMeats/
   ├── backend/
   │   ├── venv/              # Python virtual environment
   │   ├── manage.py
   │   └── requirements.txt
   └── /var/www/ProjectMeats/frontend/build/  # Frontend build directory
   ```

2. **Supervisor Configuration**:
   - Service names: `projectmeats-development`, `projectmeats-staging`, `projectmeats-production`
   - Must have sudo access for `supervisorctl` commands

3. **Nginx Configuration**:
   - Configured to serve frontend static files from `/var/www/ProjectMeats/frontend/build/`
   - Proxy backend API requests appropriately

4. **Permissions**:
   - Deployment user must have sudo access for supervisor and nginx commands
   - Frontend directory owned by `www-data:www-data` with `755` permissions

## 4. Deployment Process

### Deployment Flow Diagram
```
Code Push to GitHub
    ↓
Change Detection (backend/frontend)
    ↓
Run Tests (parallel)
    ↓
Tests Pass?
    ↓ Yes
Environment Selection (based on branch)
    ↓
┌───────────────────────────────────┐
│ Backend Deployment:               │
│ 1. SSH to server                  │
│ 2. Create backup (backend_backup) │
│ 3. Pull latest code from branch   │
│ 4. Activate virtual environment   │
│ 5. Install dependencies            │
│ 6. Run migrations                  │
│ 7. Collect static files            │
│ 8. Run Django checks               │
│ 9. Restart supervisor service     │
│ 10. Health check API endpoint     │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│ Frontend Deployment:              │
│ 1. Build React app locally        │
│ 2. Create deployment tarball      │
│ 3. Upload to server via SCP       │
│ 4. SSH to server                  │
│ 5. Create backup (build.backup.*)  │
│ 6. Extract new build              │
│ 7. Update permissions             │
│ 8. Reload nginx                   │
│ 9. Health check frontend URL      │
└───────────────────────────────────┘
    ↓
Deployment Success Notification
```

### Step-by-Step Backend Deployment

1. **Pre-Deployment**:
   - Workflow detects backend changes in `backend/` directory
   - Tests run and pass successfully
   - Creates deployment script dynamically

2. **Server Preparation**:
   - SSH connection established using sshpass
   - Navigate to `/home/django/ProjectMeats`
   - Backup current backend: `cp -r backend backend_backup`

3. **Code Update**:
   - Configure git authentication with `GIT_TOKEN`
   - Stash any local changes
   - Fetch and checkout target branch (`development` or `main`)
   - Hard reset to latest commit: `git reset --hard origin/{branch}`

4. **Dependency Installation**:
   - Activate Python virtual environment
   - Install/update packages: `pip install -r requirements.txt`

5. **Database & Static Files**:
   - Run migrations: `python manage.py migrate`
   - Collect static files: `python manage.py collectstatic --noinput`
   - Django configuration check: `python manage.py check` (production uses `--deploy` flag)

6. **Service Restart**:
   - Restart supervisor service: `supervisorctl restart projectmeats-{environment}`
   - Wait for service to stabilize (5-10 seconds)
   - Reload nginx: `systemctl reload nginx`

7. **Health Verification**:
   - Poll `/api/v1/health/` endpoint
   - 5 attempts with 10-second intervals for dev/staging
   - 10 attempts with 15-second intervals for production
   - Fail deployment if health check doesn't pass

### Step-by-Step Frontend Deployment

1. **Local Build**:
   - Checkout code from GitHub
   - Setup Node.js environment (v18)
   - Install dependencies: `npm ci`
   - Create environment-specific `.env.production` file
   - Build production bundle: `npm run build`
   - Create tarball: `tar -czf frontend-build.tar.gz`

2. **File Transfer**:
   - Upload tarball to server: `scp frontend-build.tar.gz user@host:/tmp/`

3. **Server Deployment**:
   - SSH to server
   - Backup existing build: `cp -r build build.backup.$(date +%Y%m%d_%H%M%S)`
   - Extract new build to temporary directory
   - Replace old build with new: `cp -r frontend-build-new/* /var/www/ProjectMeats/frontend/build/`

4. **Permission & Service Update**:
   - Set ownership: `chown -R www-data:www-data build`
   - Set permissions: `chmod -R 755 build`
   - Test nginx config: `nginx -t`
   - Reload nginx: `systemctl reload nginx`

5. **Health Verification**:
   - Wait 10 seconds for service stabilization
   - Curl frontend URL to verify it's serving
   - Production performs 8 attempts with 10-second intervals

6. **Cleanup**:
   - Remove temporary files from `/tmp/`
   - Remove local tarball

## 5. Rollback Procedures

### Manual Rollback Trigger
Rollbacks are performed via GitHub Actions workflow dispatch:
1. Go to Actions → Deploy to Development, UAT2 & Production
2. Click "Run workflow"
3. Select branch
4. Choose `rollback` action
5. Click "Run workflow"

### Backend Rollback Process
```bash
# Executed on server via SSH
cd /home/django/ProjectMeats

# Verify backup exists
if [ ! -d "backend_backup" ]; then
  echo "❌ No backup found!"
  exit 1
fi

# Stop service
sudo supervisorctl stop projectmeats-{environment}

# Restore backup
rm -rf backend
mv backend_backup backend

# Restart service
sudo supervisorctl start projectmeats-{environment}
sudo systemctl reload nginx
```

### Frontend Rollback Process
```bash
# Executed on server via SSH

# Find most recent backup
BACKUP_DIR=$(ls -1t /var/www/ProjectMeats/frontend/build.backup.* | head -n1)

# Verify backup exists
if [ -z "$BACKUP_DIR" ]; then
  echo "❌ No backup found!"
  exit 1
fi

# Restore backup
sudo rm -rf /var/www/ProjectMeats/frontend/build
sudo cp -r "$BACKUP_DIR" /var/www/ProjectMeats/frontend/build
sudo chown -R www-data:www-data build
sudo chmod -R 755 build
sudo systemctl reload nginx
```

### Rollback Limitations
- **One Version Back**: Only rolls back to the last deployment
- **No Backup**: Rollback fails if no backup exists
- **Manual Trigger Only**: Cannot be automated
- **Database Migrations**: Migrations are NOT rolled back automatically

## 6. Change Detection Logic

The workflow uses smart change detection to avoid unnecessary deployments:

```yaml
# Detects changes in last commit
changed_files=$(git diff --name-only HEAD^ HEAD)

# Backend changes: Any file in backend/ directory
if echo "$changed_files" | grep -q "^backend/"; then
  backend=true
fi

# Frontend changes: Any file in frontend/ directory
if echo "$changed_files" | grep -q "^frontend/"; then
  frontend=true
fi

# Manual triggers: Deploy both
if workflow_dispatch; then
  backend=true
  frontend=true
fi
```

**Optimization Benefits**:
- Only deploys changed components
- Saves deployment time
- Reduces server load
- Minimizes risk of unnecessary service restarts

## 7. Health Checks

### Backend Health Endpoint
- **URL**: `/api/v1/health/`
- **Method**: GET
- **Expected Response**: 200 OK
- **Implementation**: Located in `backend/projectmeats/health.py`

**Health Check Configuration**:
- Development: 5 attempts, 10-second intervals (75 seconds total)
- Staging: 5 attempts, 10-second intervals (75 seconds total)
- Production: 10 attempts, 15-second intervals (165 seconds total)

### Frontend Health Check
- **URL**: Root domain (e.g., `https://dev.yourdomain.com`)
- **Method**: GET
- **Expected Response**: 200 OK (index.html served)

**Health Check Configuration**:
- Development: Single attempt after 10 seconds
- Staging: Single attempt after 10 seconds
- Production: 8 attempts, 10-second intervals (90 seconds total)

## 8. Troubleshooting Guide

### Deployment Failures

#### Health Check Failures
**Symptoms**: "❌ Backend/Frontend health check failed after X attempts"

**Possible Causes**:
1. DNS not configured or not propagating
2. Service didn't start properly
3. Nginx misconfiguration
4. Firewall blocking access
5. SSL certificate issues

**Solutions**:
```bash
# SSH to server
ssh user@server

# Check backend service status
sudo supervisorctl status projectmeats-{environment}

# Check backend logs
sudo supervisorctl tail -f projectmeats-{environment} stderr

# Test health endpoint locally
curl http://localhost:8000/api/v1/health/

# Check nginx status
sudo systemctl status nginx
sudo nginx -t

# Test external access
curl -I https://your-domain.com/api/v1/health/
```

#### Deployment Script Failures
**Symptoms**: Deployment fails during git pull, migrations, or collectstatic

**Common Issues**:
1. **Git Authentication Failed**: Check `GIT_TOKEN` secret is valid
2. **Migration Errors**: Database connectivity or migration conflicts
3. **Disk Space Full**: Check server disk space: `df -h`
4. **Permission Denied**: Check directory permissions and user privileges

**Solutions**:
```bash
# Check git status on server
cd /home/django/ProjectMeats
git status
git remote -v

# Test database connection
cd backend
source venv/bin/activate
python manage.py dbshell

# Check disk space
df -h

# Fix permissions
sudo chown -R django:django /home/django/ProjectMeats
sudo chown -R www-data:www-data /var/www/ProjectMeats/frontend/build
```

#### Build Failures
**Symptoms**: Frontend build fails in GitHub Actions

**Solutions**:
1. Check Node.js version compatibility
2. Verify all environment variables are set
3. Check for syntax errors in React code
4. Review TypeScript type errors
5. Check npm dependencies for conflicts

### Rollback Issues

**Problem**: "No backup found for rollback"

**Solutions**:
1. Verify at least one successful deployment has occurred
2. Check if backup directories exist on server
3. Manually create backup before next deployment
4. Consider implementing versioned backups

### Service Not Starting

**Symptoms**: Supervisor shows service in FATAL state

**Solutions**:
```bash
# Check supervisor logs
sudo supervisorctl tail -f projectmeats-{environment} stderr

# Check Python/Django errors
cd /home/django/ProjectMeats/backend
source venv/bin/activate
python manage.py check

# Test Gunicorn manually
gunicorn projectmeats.wsgi:application --bind 0.0.0.0:8000

# Restart supervisor
sudo supervisorctl restart projectmeats-{environment}
```

### Workflow Not Triggering

**Symptoms**: Push to branch doesn't trigger deployment

**Possible Causes**:
1. Workflow file syntax error
2. Branch name mismatch
3. GitHub Actions disabled
4. No changes detected (workflow optimized to skip)

**Solutions**:
1. Check workflow file syntax: `.github/workflows/unified-deployment.yml`
2. Verify branch names match trigger configuration
3. Enable GitHub Actions in repository settings
4. Force deployment via manual workflow dispatch

## 9. Best Practices

### Development Workflow
1. **Local Testing**: Always test changes locally before pushing
2. **Branch Strategy**: Use feature branches, merge to `development` for testing
3. **Incremental Changes**: Push small, incremental changes for easier debugging
4. **Monitor Deployments**: Watch GitHub Actions logs during deployment

### Deployment Safety
1. **Test in Dev First**: Always deploy to development before staging/production
2. **Review Migrations**: Review database migrations before deploying
3. **Backup Verification**: Ensure backups are created successfully
4. **Health Monitoring**: Monitor health endpoints after deployment
5. **Gradual Rollout**: Test in development → staging → production

### Emergency Procedures
1. **Quick Rollback**: Use workflow dispatch rollback for immediate issues
2. **Communication**: Notify team of production deployments
3. **Monitoring**: Watch error logs and metrics after production deployment
4. **Incident Response**: Document issues and resolution steps

## 10. Maintenance

### Regular Tasks
- **Monitor Disk Space**: Check server storage monthly
- **Review Backups**: Verify backup directories don't consume excessive space
- **Update Dependencies**: Keep Python/Node packages updated
- **Review Logs**: Check supervisor and nginx logs for warnings
- **Secret Rotation**: Rotate SSH passwords and tokens periodically

### Cleanup Commands
```bash
# Remove old frontend backups (keep last 5)
ls -1t /var/www/ProjectMeats/frontend/build.backup.* | tail -n +6 | xargs sudo rm -rf

# Clean old Python cache
find /home/django/ProjectMeats/backend -type d -name "__pycache__" -exec rm -rf {} +

# Check and clean disk space
df -h
sudo apt-get autoclean
sudo apt-get autoremove
```

---

**Last Updated**: 2025
**Maintained By**: Development Team
**Workflow Version**: Unified Deployment v1.0
