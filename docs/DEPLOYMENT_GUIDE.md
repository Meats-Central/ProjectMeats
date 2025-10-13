# ProjectMeats Deployment Guide

## Overview

ProjectMeats supports deployment across three environments using a centralized configuration system:

- **Development** - Local development with PostgreSQL (recommended) or SQLite (fallback)
- **Staging** - Pre-production testing with PostgreSQL and monitoring
- **Production** - Full production deployment with high availability and monitoring

## Prerequisites

### General Requirements
- Python 3.8+
- Node.js 16+
- Docker and Docker Compose (for containerized deployments)
- Git

### Environment-Specific Requirements

#### Development
- **PostgreSQL 12+** (recommended for environment parity)
  - macOS: `brew install postgresql`
  - Ubuntu: `sudo apt-get install postgresql postgresql-contrib`
  - Windows: Download from [PostgreSQL.org](https://www.postgresql.org/download/windows/)
  - Docker: `docker run --name projectmeats-postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:15`
- **SQLite** (fallback option, built-in with Python)
- Local development tools

#### Staging/Production
- PostgreSQL database server (managed instance recommended)
- Redis server (optional, for caching)
- HTTPS certificates
- Monitoring infrastructure (recommended)

## Environment Configuration

### 1. Set Up Environment Variables

#### Development

**Option A: PostgreSQL (Recommended)**
```bash
# 1. Set up PostgreSQL database
# Create database and user
createdb projectmeats_dev
createuser -P projectmeats_dev  # Set password when prompted

# Grant privileges
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;"

# 2. Configure environment
python config/manage_env.py setup development

# 3. Edit config/environments/development.env
# DB_ENGINE=django.db.backends.postgresql
# DB_NAME=projectmeats_dev
# DB_USER=projectmeats_dev
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=5432
```

**Option B: SQLite (Fallback)**
```bash
# 1. Configure environment
python config/manage_env.py setup development

# 2. Edit config/environments/development.env
# DB_ENGINE=django.db.backends.sqlite3
# (No other DB variables needed)
```

#### Staging
```bash
# Set staging environment variables in your deployment system
export STAGING_SECRET_KEY="your-staging-secret-key"
export STAGING_DB_HOST="staging-db.example.com"
export STAGING_DB_NAME="projectmeats_staging"
export STAGING_DB_USER="projectmeats_staging"
export STAGING_DB_PASSWORD="staging-password"
export STAGING_DOMAIN="staging.projectmeats.com"
export STAGING_FRONTEND_DOMAIN="staging.projectmeats.com"
export STAGING_API_DOMAIN="api-staging.projectmeats.com"

# Apply staging configuration
python config/manage_env.py setup staging
```

#### Production
```bash
# Set production environment variables securely
export PRODUCTION_SECRET_KEY="your-production-secret-key"
export PRODUCTION_DB_HOST="prod-db.example.com"
export PRODUCTION_DB_NAME="projectmeats"
export PRODUCTION_DB_USER="projectmeats"
export PRODUCTION_DB_PASSWORD="production-password"
export PRODUCTION_DOMAIN="projectmeats.com"
export PRODUCTION_FRONTEND_DOMAIN="app.projectmeats.com"
export PRODUCTION_API_DOMAIN="api.projectmeats.com"

# Apply production configuration
python config/manage_env.py setup production
```

### 2. Validate Configuration
```bash
python config/manage_env.py validate
```

## Deployment Methods

### Method 1: Direct Deployment

#### Development

**Using PostgreSQL (Recommended):**
```bash
# 1. Set up PostgreSQL database (if not already done)
createdb projectmeats_dev
createuser -P projectmeats_dev
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;"

# 2. Install Python dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 3. Set up database migrations
cd backend && python manage.py migrate && cd ..

# 4. Create superuser and root tenant (uses environment variables)
cd backend && python manage.py create_super_tenant && cd ..

# 5. Start development servers
make dev
```

**Using SQLite (Fallback):**
```bash
# 1. Install Python dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 2. Set up database migrations
cd backend && python manage.py migrate && cd ..

# 3. Create superuser and root tenant (uses environment variables)
cd backend && python manage.py create_super_tenant && cd ..

# 4. Start development servers
make dev
```

#### Staging/Production
```bash
# Backend deployment
cd backend
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py create_super_tenant  # Creates/updates superuser from env vars
python -m gunicorn projectmeats.wsgi:application --bind 0.0.0.0:8000

# Frontend deployment
cd frontend
npm install
npm run build
# Serve build files with nginx or similar
```

## Superuser Management

### Environment Variables

All environments use environment variables for superuser credentials to ensure security and avoid hardcoded credentials in code.

**Required Environment Variables:**
- `SUPERUSER_USERNAME` - Username for the superuser (default: admin)
- `SUPERUSER_EMAIL` - Email address for the superuser
- `SUPERUSER_PASSWORD` - Password for the superuser

**Development:**
Set in `config/environments/development.env`:
```bash
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@meatscentral.com
SUPERUSER_PASSWORD=DevAdmin123!SecurePass
```

**Staging:**
Set as GitHub Secrets or deployment platform environment variables:
```bash
STAGING_SUPERUSER_USERNAME=admin
STAGING_SUPERUSER_EMAIL=admin@staging.projectmeats.com
STAGING_SUPERUSER_PASSWORD=<secure-staging-password>
```

**Production:**
Set as GitHub Secrets or deployment platform environment variables:
```bash
PRODUCTION_SUPERUSER_USERNAME=admin
PRODUCTION_SUPERUSER_EMAIL=admin@meatscentral.com
PRODUCTION_SUPERUSER_PASSWORD=<secure-production-password>
```

### Creating/Updating Superuser

The `create_super_tenant` management command is idempotent and can be run safely multiple times:

```bash
# Development
make superuser

# Staging/Production (run after migrations)
python manage.py create_super_tenant

# With custom verbosity for debugging
python manage.py create_super_tenant --verbosity 2
```

**What the command does:**
1. Reads credentials from environment variables
2. Creates a superuser if one doesn't exist (or updates if exists)
3. Creates a root tenant for multi-tenancy support
4. Links the superuser to the root tenant with owner role

**Automatic Execution:**
The command runs automatically during:
- Initial setup via `python setup_env.py`
- Deployment workflows (after migrations)
- Can be manually triggered with `make superuser`

### Method 2: Docker Deployment (Archived)

> **Note:** Docker deployment files have been archived to `archived/docker/`. See `archived/README.md` for details.

#### Development
```bash
# Using docker-compose for development (archived)
docker-compose -f archived/docker/docker-compose.dev.yml up
```

#### Staging
```bash
# Build and push images (archived)
docker build -f archived/docker/Dockerfile.backend -t projectmeats/backend:staging backend/
docker build -f archived/docker/Dockerfile.frontend -t projectmeats/frontend:staging frontend/

# Deploy with docker-compose (archived)
docker-compose -f archived/docker/docker-compose.staging.config.yml up -d
```

#### Production
```bash
# Build and push images (archived)
docker build -f archived/docker/Dockerfile.backend -t projectmeats/backend:latest backend/
docker build -f archived/docker/Dockerfile.frontend -t projectmeats/frontend:latest frontend/

# Deploy with docker swarm (archived)
docker stack deploy -c archived/docker/docker-compose.prod.yml projectmeats
```

## Platform-Specific Deployments

### Digital Ocean App Platform

#### 1. Create App Spec
```yaml
name: projectmeats
services:
- name: backend
  source_dir: /backend
  github:
    repo: Meats-Central/ProjectMeats3
    branch: main
  run_command: python -m gunicorn projectmeats.wsgi:application --bind 0.0.0.0:8000
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: SECRET_KEY
    value: ${SECRET_KEY}
    type: SECRET
  - key: DATABASE_URL
    value: ${DATABASE_URL}
    type: SECRET
  - key: DEBUG
    value: "False"

- name: frontend
  source_dir: /frontend
  github:
    repo: Meats-Central/ProjectMeats3
    branch: main
  run_command: serve -s build
  environment_slug: node-js
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: REACT_APP_API_BASE_URL
    value: ${BACKEND_URL}/api/v1

databases:
- name: projectmeats-db
  engine: PG
  num_nodes: 1
  size: basic-xs
```

#### 2. Deploy
```bash
# Using doctl (Digital Ocean CLI)
doctl apps create --spec .do/app.yaml

# Or use the web interface
```

### AWS Deployment

#### Using Elastic Beanstalk
```bash
# Create application
eb init projectmeats --platform python-3.8

# Set environment variables
eb setenv SECRET_KEY=your-secret-key DATABASE_URL=your-db-url

# Deploy
eb deploy
```

#### Using ECS/Fargate
```yaml
# task-definition.json
{
  "family": "projectmeats",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [...]
}
```

### Heroku Deployment

#### 1. Create Heroku Apps
```bash
# Create backend app
heroku create projectmeats-backend

# Create frontend app (if needed)
heroku create projectmeats-frontend
```

#### 2. Set Environment Variables
```bash
# Backend configuration
heroku config:set SECRET_KEY=your-secret-key -a projectmeats-backend
heroku config:set DEBUG=False -a projectmeats-backend
heroku config:set DATABASE_URL=postgres://... -a projectmeats-backend

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev -a projectmeats-backend
```

#### 3. Deploy
```bash
# Deploy backend
git subtree push --prefix backend heroku main

# Or use GitHub integration
```

## Environment-Specific Configurations

### Development Configuration
- **Database**: PostgreSQL (for environment parity with staging/production)
- **Debug**: Enabled
- **Security**: Minimal (for development ease)
- **CORS**: Localhost origins allowed
- **Logging**: Console output

### Staging Configuration
- **Database**: Shared PostgreSQL instance
- **Debug**: Disabled
- **Security**: HTTPS enforced
- **CORS**: Staging domain only
- **Logging**: File and console output
- **Monitoring**: Basic monitoring

### Production Configuration
- **Database**: Production PostgreSQL with backups
- **Debug**: Disabled
- **Security**: Full security features enabled
- **CORS**: Production domain only
- **Logging**: Structured logging with retention
- **Monitoring**: Full monitoring and alerting
- **Performance**: Optimized settings and caching

## Security Checklist

### Development
- [ ] Local secrets only
- [ ] No production data access
- [ ] Basic error handling

### Staging
- [ ] HTTPS certificates installed
- [ ] Staging-specific secrets
- [ ] Database access restricted
- [ ] CORS configured for staging domain
- [ ] Basic monitoring enabled

### Production
- [ ] Strong secret keys generated
- [ ] Database backups configured
- [ ] HTTPS with HSTS enabled
- [ ] CORS restricted to production domains
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Error logging configured
- [ ] Monitoring and alerting active
- [ ] Access logs enabled
- [ ] Regular security updates scheduled

## Monitoring and Maintenance

### Health Checks
```bash
# Backend health check
curl https://api.projectmeats.com/api/v1/health/

# Frontend health check  
curl https://app.projectmeats.com/health.json
```

### Log Management
```bash
# View application logs
tail -f backend/debug.log

# For Docker deployments
docker logs projectmeats_backend
```

### Database Maintenance
```bash
# Backup database
pg_dump projectmeats > backup.sql

# Restore database
psql projectmeats < backup.sql

# Run migrations
python manage.py migrate
```

### Performance Monitoring
- **Backend**: Monitor API response times and database queries
- **Frontend**: Monitor page load times and user interactions
- **Infrastructure**: Monitor server resources and uptime

## Troubleshooting

### Common Issues

#### Environment Variable Errors
```bash
# Validate configuration
python config/manage_env.py validate

# Check environment variables are loaded
cd backend && python manage.py shell
>>> import os
>>> os.environ['SECRET_KEY']
```

#### Database Connection Issues
```bash
# Test database connection
cd backend && python manage.py dbshell

# Run migrations
python manage.py migrate --verbosity=2
```

#### CORS Issues
```bash
# Check CORS settings
cd backend && python manage.py shell
>>> from django.conf import settings
>>> settings.CORS_ALLOWED_ORIGINS
```

#### Static Files Issues
```bash
# Collect static files
cd backend && python manage.py collectstatic --verbosity=2

# Check static files configuration
python manage.py findstatic admin/css/base.css
```

### Debug Commands
```bash
# Django configuration check
cd backend && python manage.py check

# Django system check
cd backend && python manage.py check --deploy

# Test frontend build
cd frontend && npm run build

# Validate environment
python config/manage_env.py validate
```

## Rollback Procedures

### Application Rollback
```bash
# For Docker deployments
docker service update --rollback projectmeats_backend

# For direct deployments
git checkout previous-stable-tag
# Redeploy using standard deployment process
```

### Database Rollback
```bash
# Restore from backup
psql projectmeats < backup-before-migration.sql

# Reverse migrations (if applicable)
cd backend && python manage.py migrate app_name previous_migration_number
```

This deployment guide ensures consistent, secure, and maintainable deployments across all environments.