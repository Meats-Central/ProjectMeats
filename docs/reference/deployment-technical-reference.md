# ProjectMeats Deployment Documentation

## Project Overview

ProjectMeats is a comprehensive business management system for meat sales brokers, built with:
- **Backend**: Django REST Framework (Python 3.12)
- **Frontend**: React TypeScript with Vite
- **Database**: PostgreSQL (Managed Database)
- **Deployment**: Digital Ocean Droplets
- **CI/CD**: GitHub Actions
- **Web Server**: Nginx with SSL certificates
- **Process Management**: systemd/systemctl

## Infrastructure Architecture

### Environment Setup

We have implemented two separate environments:

1. **Staging Environment (UAT2)**
   - Backend Droplet Name: meatscentral-uat2-backend
   - Backend Droplet: Runs Django REST API
   - Frontend Droplet Name: meatscentral-uat2-frontend
   - Frontend Droplet: Serves React application via Nginx
   - Deploys from `development` branch
   - SSL certificates configured

2. **Production Environment (PROD2)**
   - Backend Droplet Name: meatscentral-prod2-backend
   - Backend Droplet: Runs Django REST API
   - Frontend Droplet Name: meatscentral-prod2-frontend
   - Frontend Droplet: Serves React application via Nginx
   - Deploys from `main` branch
   - SSL certificates configured

### Server Configuration

#### Backend Servers
- **Python Version**: 3.12
- **Virtual Environment**: Located at `/home/django/ProjectMeats/backend/venv/`
- **Project Directory**: `/home/django/ProjectMeats/`
- **Process Management**: systemd/systemctl
- **Web Server**: Nginx (reverse proxy)
- **Database**: PostgreSQL managed database
- **SSL**: SSL certificates configured

#### Frontend Servers
- **Node.js Version**: 18
- **Build Directory**: `/var/www/ProjectMeats/frontend/build/`
- **Web Server**: Nginx (serves static files)
- **SSL**: SSL certificates configured

## Deployment Process

### Automated CI/CD Pipeline

We have implemented GitHub Actions workflows for automated deployment:

#### Staging Deployment
- **Trigger**: Push to `development` branch
- **Backend Workflow**: `.github/workflows/deploy-backend-staging.yml`
- **Frontend Workflow**: `.github/workflows/deploy-frontend-staging.yml`

#### Production Deployment  
- **Trigger**: Push to `main` branch
- **Backend Workflow**: `.github/workflows/deploy-backend-production.yml`
- **Frontend Workflow**: `.github/workflows/deploy-frontend-production.yml`

### Deployment Steps

#### Backend Deployment Process
1. **Testing Phase**
   - Runs Django tests on PostgreSQL test database
   - Performs code quality checks (flake8, black) - non-blocking
   - Validates Django configuration

2. **Deployment Phase**
   - Connects to server via SSH (password authentication)
   - Creates backup of current deployment
   - Pulls latest code from GitHub using token authentication
   - Activates virtual environment at `backend/venv/`
   - Installs/updates Python dependencies
   - Runs database migrations
   - Creates/updates superuser and root tenant (using environment variables)
   - Collects static files
   - Validates Django configuration

3. **Service Management**
   - Restarts backend service using systemctl:
     - **Staging**: `sudo systemctl restart gunicorn`
     - **Production**: `sudo systemctl restart gunicorn`
   - Reloads Nginx configuration
     - **Staging**: `sudo systemctl restart nginx`
     - **Production**: `sudo systemctl restart nginx`

4. **Health Verification**
   - Performs health checks against `/api/v1/health/` endpoint
   - Multiple retry attempts with exponential backoff
   - Fails deployment if health checks don't pass

#### Frontend Deployment Process
1. **Testing Phase**
   - Installs Node.js dependencies
   - Runs React tests in CI mode
   - Performs TypeScript type checking

2. **Build Phase**
   - Creates environment-specific `.env` file from GitHub secrets
   - Builds React application for production
   - Creates compressed deployment archive

3. **Deployment Phase**
   - Uploads build archive to server
   - Creates backup of current build
   - Extracts new build to `/var/www/ProjectMeats/frontend/build/`
   - Sets proper file permissions (`www-data:www-data`)
   - Tests and reloads Nginx configuration

4. **Health Verification**
   - Performs HTTP health checks against frontend URL
   - Validates that the application is serving correctly

## Environment Variables and Secrets

### Backend Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ip-address

# Additional settings as needed
```

### Frontend Environment Variables
```bash
# API Configuration
REACT_APP_API_BASE_URL=https://your-api-domain.com
REACT_APP_ENVIRONMENT=staging|production

# Feature Flags
REACT_APP_AI_ASSISTANT_ENABLED=true
REACT_APP_ENABLE_DOCUMENT_UPLOAD=true
REACT_APP_ENABLE_CHAT_EXPORT=true

# File Upload Settings
REACT_APP_MAX_FILE_SIZE=10485760
REACT_APP_SUPPORTED_FILE_TYPES=.pdf,.doc,.docx,.txt

# Debug Settings
REACT_APP_ENABLE_DEBUG=false
REACT_APP_ENABLE_DEVTOOLS=false
```

### GitHub Secrets Configuration

#### Staging Environment (uat2-backend, uat2)
- `STAGING_HOST`: Server IP address
- `STAGING_USER`: SSH username  
- `SSH_PASSWORD`: SSH password
- `GIT_TOKEN`: GitHub personal access token
- `STAGING_API_URL`: Backend API URL
- `STAGING_URL`: Frontend URL
- `STAGING_SUPERUSER_USERNAME`: Superuser username for staging
- `STAGING_SUPERUSER_EMAIL`: Superuser email for staging
- `STAGING_SUPERUSER_PASSWORD`: Secure superuser password for staging
- Frontend-specific environment variables

#### Production Environment (prod2-backend, prod2-frontend)  
- `PRODUCTION_HOST`: Server IP address
- `PRODUCTION_USER`: SSH username
- `SSH_PASSWORD`: SSH password
- `GIT_TOKEN`: GitHub personal access token
- `PRODUCTION_API_URL`: Backend API URL
- `PRODUCTION_URL`: Frontend URL
- `PRODUCTION_SUPERUSER_USERNAME`: Superuser username for production
- `PRODUCTION_SUPERUSER_EMAIL`: Superuser email for production
- `PRODUCTION_SUPERUSER_PASSWORD`: Secure superuser password for production
- Frontend-specific environment variables

## Service Management

### Backend Services

#### Staging Service Management
```bash
# Check service status
sudo systemctl status gunicorn

# Start service
sudo systemctl start gunicorn

# Stop service  
sudo systemctl stop gunicorn

# Restart service
sudo systemctl restart gunicorn

# View logs
sudo journalctl -u gunicorn -f
```

#### Production Service Management
```bash
# Check service status
sudo systemctl status gunicorn

# Start service
sudo systemctl start gunicorn

# Stop service
sudo systemctl stop gunicorn

# Restart service  
sudo systemctl restart gunicorn

# View logs
sudo journalctl -u gunicorn -f
```

### Nginx Management
```bash
# Test nginx configuration
sudo nginx -t

# Reload nginx (without downtime)
sudo systemctl reload nginx

# Restart nginx
sudo systemctl restart nginx

# Check nginx status
sudo systemctl status nginx
```

## Manual Deployment Process

If needed, deployments can be triggered manually:

### Backend Manual Deployment
1. SSH into the backend server
2. Navigate to project directory: `cd /home/django/ProjectMeats`
3. Create backup: `cp -r backend backend_backup`
4. Pull latest changes: `git pull origin development` (staging) or `git pull origin main` (production)
5. Activate virtual environment: `cd backend && source venv/bin/activate`
6. Install dependencies: `pip install -r requirements.txt`
7. Run migrations: `python manage.py migrate`
8. Collect static files: `python manage.py collectstatic --noinput`
9. Restart service: `sudo systemctl restart gunicorn`
10. Reload nginx: `sudo systemctl reload nginx`

### Frontend Manual Deployment
1. Build locally: `npm run build` in frontend directory
2. Create archive: `tar -czf frontend-build.tar.gz -C build .`
3. Upload to server: `scp frontend-build.tar.gz user@server:/tmp/`
4. SSH into frontend server
5. Create backup: `sudo cp -r /var/www/ProjectMeats/frontend/build /var/www/ProjectMeats/frontend/build.backup.$(date +%Y%m%d_%H%M%S)`
6. Extract new build: `cd /tmp && mkdir frontend-build-new && tar -xzf frontend-build.tar.gz -C frontend-build-new/`
7. Deploy: `sudo rm -rf /var/www/ProjectMeats/frontend/build && sudo mkdir -p /var/www/ProjectMeats/frontend/build && sudo cp -r frontend-build-new/* /var/www/ProjectMeats/frontend/build/`
8. Set permissions: `sudo chown -R www-data:www-data /var/www/ProjectMeats/frontend/build`
9. Reload nginx: `sudo systemctl reload nginx`

## Rollback Procedures

### Automated Rollback
Both staging and production workflows support rollback via GitHub Actions:
- Navigate to Actions tab in GitHub repository
- Select the appropriate workflow
- Click "Run workflow" 
- Choose "rollback" from the action dropdown

### Manual Rollback

#### Backend Rollback
```bash
cd /home/django/ProjectMeats
sudo systemctl stop gunicorn
rm -rf backend
mv backend_backup backend
sudo systemctl start gunicorn
sudo systemctl reload nginx
```

#### Frontend Rollback
```bash
# Find latest backup
ls -la /var/www/ProjectMeats/frontend/build.backup.*

# Restore backup (replace YYYYMMDD_HHMMSS with actual backup timestamp)
sudo rm -rf /var/www/ProjectMeats/frontend/build
sudo cp -r /var/www/ProjectMeats/frontend/build.backup.YYYYMMDD_HHMMSS /var/www/ProjectMeats/frontend/build
sudo chown -R www-data:www-data /var/www/ProjectMeats/frontend/build
sudo systemctl reload nginx
```

## Monitoring and Maintenance

### Health Check Endpoints
- **Backend Staging**: `https://your-staging-api-domain.com/api/v1/health/`
- **Backend Production**: `https://your-production-api-domain.com/api/v1/health/`
- **Frontend**: Standard HTTP 200 response from main application URLs

### Log Locations
- **Backend Services**: `sudo journalctl -u gunicorn`
- **Nginx Access Logs**: `/var/log/nginx/access.log`
- **Nginx Error Logs**: `/var/log/nginx/error.log`

### Regular Maintenance Tasks
1. **Database Backups**: Ensure PostgreSQL managed database backups are configured
2. **SSL Certificate Renewal**: Monitor SSL certificate expiration dates
3. **System Updates**: Keep droplets updated with security patches
4. **Log Rotation**: Ensure log files don't consume excessive disk space
5. **Performance Monitoring**: Monitor application performance and server resources

## Future Updates

The system is configured for automatic updates through the CI/CD pipeline:

1. **Staging Updates**: Commit changes to `development` branch
2. **Production Updates**: Merge `development` to `main` branch
3. **Emergency Rollbacks**: Use GitHub Actions rollback feature
4. **Manual Interventions**: Follow manual deployment procedures if automated deployment fails

## Security Considerations

1. **GitHub Tokens**: Personal access tokens used for git operations (rotate regularly)
2. **Environment Variables**: Sensitive data stored in GitHub Secrets
3. **SSL/TLS**: Certificates configured on both staging and production
4. **Database Security**: Managed PostgreSQL with restricted access
5. **Server Hardening**: Ensure droplets follow security best practices

## Support and Troubleshooting

### Common Issues
1. **Deployment Failures**: Check GitHub Actions logs for detailed error messages
2. **Service Not Starting**: Check systemctl status and journalctl logs
3. **Database Connection Issues**: Verify DATABASE_URL and network connectivity
4. **Nginx Configuration Errors**: Run `nginx -t` to validate configuration
5. **Permission Issues**: Ensure proper file ownership (www-data:www-data for frontend)

### Getting Help
- Check service logs: `sudo journalctl -u gunicorn`
- Verify nginx configuration: `sudo nginx -t`
- Test database connectivity from Django shell
- Review GitHub Actions workflow logs for deployment issues
