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
# Staging deployment uses GitHub Actions workflow which automatically pulls from 
# the development branch and deploys to the UAT2 staging environment.
#
# IMPORTANT: All environment variables must be configured as GitHub Secrets before deployment.
# See the "Required GitHub Secrets for Staging" section below for the complete list.
#
# On the staging server, environment variables should be set in the server's environment:
export STAGING_SECRET_KEY="your-staging-secret-key"
export STAGING_DB_HOST="staging-db.example.com"
export STAGING_DB_NAME="projectmeats_staging"
export STAGING_DB_USER="projectmeats_staging"
export STAGING_DB_PASSWORD="staging-password"
export STAGING_DOMAIN="uat.meatscentral.com"
export STAGING_FRONTEND_DOMAIN="uat.meatscentral.com"
export STAGING_API_DOMAIN="uat-api.meatscentral.com"
export STAGING_SUPERUSER_USERNAME="admin"
export STAGING_SUPERUSER_EMAIL="admin@meatscentral.com"
export STAGING_SUPERUSER_PASSWORD="secure-staging-password"

# Apply staging configuration
python config/manage_env.py setup staging
```

**Required GitHub Secrets for Staging:**

To enable automated deployment to staging, configure these secrets in your GitHub repository:

**Repository-Level Secrets** (Settings → Secrets → Actions → Repository secrets):
- `STAGING_HOST` - Staging server IP or hostname
- `STAGING_USER` - SSH username for staging server
- `SSH_PASSWORD` - SSH password for staging server
- `GIT_TOKEN` - GitHub Personal Access Token for repository access

**Environment Secrets for `uat2-backend`** (Settings → Environments → uat2-backend):
- `STAGING_SUPERUSER_USERNAME` - Admin username
- `STAGING_SUPERUSER_EMAIL` - Admin email
- `STAGING_SUPERUSER_PASSWORD` - Admin password (use strong password)
- `STAGING_SECRET_KEY` - Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `STAGING_DB_USER` - Database username
- `STAGING_DB_PASSWORD` - Database password
- `STAGING_DB_HOST` - Database host
- `STAGING_DB_PORT` - Database port (default: `5432`)
- `STAGING_DB_NAME` - Database name
- `STAGING_DOMAIN` - Main domain (e.g., `uat.meatscentral.com`)
- `STAGING_API_DOMAIN` - API domain (e.g., `uat-api.meatscentral.com`)
- `STAGING_FRONTEND_DOMAIN` - Frontend domain (same as STAGING_DOMAIN)
- `STAGING_API_URL` - Backend API URL (e.g., `https://uat-api.meatscentral.com`)

**Optional Secrets** (if features are enabled):
- `STAGING_OPENAI_API_KEY`, `STAGING_ANTHROPIC_API_KEY` - AI service keys
- `STAGING_EMAIL_HOST`, `STAGING_EMAIL_USER`, `STAGING_EMAIL_PASSWORD` - Email configuration
- `STAGING_REDIS_HOST`, `STAGING_REDIS_PORT` - Redis cache configuration
- `STAGING_SENTRY_DSN` - Sentry error tracking

**Note**: The GitHub Actions workflow (`.github/workflows/unified-deployment.yml`) currently only passes superuser credentials to the deployment script. To pass database and other credentials, the workflow needs to be updated to export these environment variables during deployment.

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

## Secret Validation in CI/CD and Tests

### Overview

The `setup_superuser` management command is designed to work reliably across all environments including CI/CD pipelines and test execution contexts. This section explains how to properly configure secrets for testing and CI/CD.

### Test Context Detection

The command automatically detects test contexts and applies appropriate behavior:

1. **Test Environment Detection:**
   - Checks if `DJANGO_ENV` contains 'test'
   - Checks if `DJANGO_SETTINGS_MODULE` ends with 'test'
   
2. **Test-Friendly Behavior:**
   - Uses safe defaults when environment variables are missing
   - Logs warnings instead of raising errors
   - Prevents test failures due to missing production secrets

### GitHub Actions Configuration

The unified deployment workflow (`unified-deployment.yml`) includes test-specific environment variables to prevent failures during test execution:

```yaml
- name: 🧪 Run tests
  working-directory: ./backend
  env:
    DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
    SECRET_KEY: test-secret-key-for-testing-only
    DEBUG: True
    DJANGO_ENV: test
    DJANGO_SETTINGS_MODULE: projectmeats.settings.test
    # Test-specific superuser credentials (mocked in tests)
    STAGING_SUPERUSER_USERNAME: testadmin
    STAGING_SUPERUSER_EMAIL: testadmin@example.com
    STAGING_SUPERUSER_PASSWORD: testpass123
    PRODUCTION_SUPERUSER_USERNAME: testadmin
    PRODUCTION_SUPERUSER_EMAIL: testadmin@example.com
    PRODUCTION_SUPERUSER_PASSWORD: testpass123
  run: |
    python manage.py test apps/
```

### Mocking Secrets in Tests

When writing tests that use the `setup_superuser` command, use `@patch` to mock environment variables:

```python
from unittest import mock
from django.core.management import call_command
from django.test import TestCase

class SetupSuperuserTests(TestCase):
    def test_command_with_missing_vars(self):
        """Test that command handles missing vars in test context."""
        # Mock environment to simulate missing vars
        with mock.patch.dict('os.environ', {
            'DJANGO_ENV': 'test',
            'DJANGO_SETTINGS_MODULE': 'projectmeats.settings.test'
        }, clear=True):
            # Should not raise error in test context
            call_command('setup_superuser')
        
        # Verify user was created with defaults
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.assertTrue(User.objects.exists())
```

### Environment-Specific Behavior

| Environment | Missing Vars Behavior | Logging Level |
|-------------|----------------------|---------------|
| `development` | Uses defaults (`admin@meatscentral.com`) | WARNING |
| `test` | Uses test defaults (`testadmin@example.com`) | WARNING |
| `staging`/`uat` | Raises `ValueError` (strict validation) | ERROR |
| `production` | Raises `ValueError` (strict validation) | ERROR |

### Verbose Logging

Use `--verbosity 2` or higher to see detailed information about which environment variables are loaded:

```bash
python manage.py setup_superuser --verbosity 2
```

Output example:
```
Running setup_superuser for environment: staging (test_context=False)
Staging/UAT mode: loaded STAGING_SUPERUSER_USERNAME: set
Staging/UAT mode: loaded STAGING_SUPERUSER_EMAIL: set
Staging/UAT mode: loaded STAGING_SUPERUSER_PASSWORD: set
✅ Superuser password synced/updated for: admin@staging.example.com
✅ Password verified - user can login successfully
```

### Troubleshooting

#### Issue: Tests fail with "required in staging environment!" error

**Cause:** Test environment is not properly detected, or GitHub Actions workflow doesn't export test-specific env vars.

**Solution:**
1. Ensure `DJANGO_ENV=test` is set in test configuration
2. Update `.github/workflows/unified-deployment.yml` to include test-specific superuser variables
3. Use `@patch.dict('os.environ', ...)` in test setup to provide required vars

#### Issue: CI/CD deployment fails with missing secrets

**Cause:** GitHub Secrets not configured for the deployment environment.

**Solution:**
1. Go to repository Settings → Secrets and variables → Actions
2. Select the appropriate environment (dev-backend, uat2-backend, prod2-backend)
3. Add required secrets:
   - `STAGING_SUPERUSER_USERNAME`
   - `STAGING_SUPERUSER_EMAIL`
   - `STAGING_SUPERUSER_PASSWORD` (or equivalent for your environment)

#### Issue: Local development fails to create superuser

**Cause:** Development environment variables not set.

**Solution:**
```bash
# Option 1: Set in config/environments/development.env
DEVELOPMENT_SUPERUSER_USERNAME=admin
DEVELOPMENT_SUPERUSER_EMAIL=admin@meatscentral.com
DEVELOPMENT_SUPERUSER_PASSWORD=your_dev_password

# Option 2: Run with inline env vars
DEVELOPMENT_SUPERUSER_PASSWORD=mypass python manage.py setup_superuser
```

### Best Practices

1. **Never commit real credentials:** Always use placeholders in version control
2. **Use environment-specific prefixes:** `DEVELOPMENT_*`, `STAGING_*`, `PRODUCTION_*`
3. **Validate in CI:** Test workflows should verify secrets are properly loaded
4. **Document secret requirements:** Keep documentation updated with all required secrets
5. **Monitor logs:** Use verbose logging in deployment workflows for troubleshooting

### References

- [Django Environment Variables Documentation](https://docs.djangoproject.com/en/4.2/topics/settings/#envvar-DJANGO_SETTINGS_MODULE)
- [12-Factor App: Config](https://12factor.net/config)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)

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

## Database Configuration and Verification

### Understanding DB_ENGINE

The `DB_ENGINE` environment variable determines which database backend Django uses. This is critical for environment parity and deployment success.

**Valid Values:**
- `django.db.backends.postgresql` - PostgreSQL (recommended for all environments)
- `django.db.backends.sqlite3` - SQLite (local development fallback only)

**Reference:** [Django Database Settings Documentation](https://docs.djangoproject.com/en/stable/ref/settings/#databases)

### Development Environment Database Configuration

#### GitHub Secrets Configuration (Required for Deployment)

To deploy to the dev-backend environment, configure these secrets:

1. Navigate to: **Repository Settings → Environments → dev-backend**
2. Add the following secrets:

| Secret Name | Required? | Description | Example Value |
|-------------|-----------|-------------|---------------|
| `DEVELOPMENT_DB_ENGINE` | ⚠️ Recommended | Database backend | `django.db.backends.postgresql` |
| `DEVELOPMENT_DB_NAME` | If using PostgreSQL | Database name | `projectmeats_dev` |
| `DEVELOPMENT_DB_USER` | If using PostgreSQL | Database user | `projectmeats_dev` |
| `DEVELOPMENT_DB_PASSWORD` | If using PostgreSQL | Database password | `your-secure-password` |
| `DEVELOPMENT_DB_HOST` | If using PostgreSQL | Database host | `localhost` or managed DB hostname |
| `DEVELOPMENT_DB_PORT` | Optional | Database port | `5432` (default for PostgreSQL) |

**Note:** If `DEVELOPMENT_DB_ENGINE` is not set or empty, the system will automatically fall back to SQLite. However, for environment parity with UAT/production, PostgreSQL is strongly recommended.

#### Verification Steps

After configuring secrets, verify your database configuration:

**Step 1: Check Django Configuration**
```bash
# SSH into dev server or run locally
cd /home/django/ProjectMeats/backend
source venv/bin/activate

# Verify settings are loaded correctly
python manage.py check --database default

# Should output: System check identified no issues (0 silenced).
```

**Step 2: Test Database Connectivity**
```bash
# Verify database connection
python manage.py shell

# In the shell:
from django.db import connection
connection.ensure_connection()
print(f"Connected to: {connection.settings_dict['ENGINE']}")
# Should print: Connected to: django.db.backends.postgresql
```

**Step 3: Check Migration Status**
```bash
# Verify migrations can run
python manage.py showmigrations

# All migrations should show [X] indicating they're applied
```

**Step 4: Review Deployment Logs**

In GitHub Actions workflow logs, look for:
- ✅ `DEVELOPMENT_DB_ENGINE is set to: django.db.backends.postgresql`
- ✅ `Development environment using database backend: django.db.backends.postgresql`
- ❌ `DEVELOPMENT_DB_ENGINE secret is empty, will use SQLite fallback` (indicates missing secret)

### Troubleshooting DB_ENGINE ValueError

If deployment fails with `ValueError: Unsupported DB_ENGINE`, follow these steps:

#### Symptom
```
ValueError: Unsupported DB_ENGINE: ''. 
Supported values are 'django.db.backends.postgresql' or 'django.db.backends.sqlite3'.
```

#### Root Cause
The `DB_ENGINE` environment variable is either:
1. Not set in GitHub Secrets
2. Set to an empty string
3. Set to an invalid value

#### Solution

**Option A: Use PostgreSQL (Recommended)**
1. Go to: Settings → Environments → dev-backend
2. Add secret `DEVELOPMENT_DB_ENGINE` = `django.db.backends.postgresql`
3. Add other required DB secrets (`DEVELOPMENT_DB_NAME`, `DEVELOPMENT_DB_USER`, etc.)
4. Redeploy from development branch

**Option B: Use SQLite Fallback**
1. Ensure `DEVELOPMENT_DB_ENGINE` secret is either:
   - Not created at all (system will use fallback)
   - Set to `django.db.backends.sqlite3`
2. Note: SQLite is not recommended for deployment environments due to:
   - Different behavior from staging/production
   - Limited concurrency
   - No network access
   - File permission issues

#### Prevention
- Always set `DB_ENGINE` to a valid value in all environments
- Use PostgreSQL for development to match staging/production
- Review deployment logs after configuration changes
- Add DB secrets when creating new environments

### UAT/Staging Database Configuration

UAT deployment currently uses server-side environment variables. Database credentials should be configured on the UAT server:

```bash
# On UAT server (/home/django/ProjectMeats/.env or server environment)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=projectmeats_uat
DB_USER=projectmeats_uat
DB_PASSWORD=<secure-password>
DB_HOST=<managed-db-hostname>
DB_PORT=5432
```

**Verification:** Follow the same verification steps as development (Step 1-3 above).

### Production Database Configuration

Production uses managed PostgreSQL with enhanced security and backup configuration. Refer to the production deployment guide for specific setup instructions.

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

### Handling User Duplicates

In rare cases, database corruption or migration issues can result in duplicate users with the same username or email. The `create_super_tenant` command handles this scenario gracefully:

#### Automatic Duplicate Cleanup

The command automatically detects and handles duplicate users:

1. **Detection**: Uses `.filter()` instead of `.get()` to avoid `MultipleObjectsReturned` errors
2. **Resolution**: Keeps the first user and deletes duplicates
3. **Logging**: Warns about duplicates found and cleaned up

```bash
# Run with increased verbosity to see duplicate handling
python manage.py create_super_tenant --verbosity 2
```

#### Manual Verification and Cleanup (Staging/Production)

If you suspect duplicate users exist in your database:

```bash
# Connect to database shell
python manage.py dbshell

# Check for duplicate usernames
SELECT username, COUNT(*) as count 
FROM auth_user 
GROUP BY username 
HAVING COUNT(*) > 1;

# Check for duplicate emails
SELECT email, COUNT(*) as count 
FROM auth_user 
GROUP BY email 
HAVING COUNT(*) > 1 AND email != '';

# Exit dbshell
\q
```

#### Prevention

Django's User model has a UNIQUE constraint on the `username` field, which prevents duplicate usernames under normal circumstances. Duplicates can only occur through:

- Direct SQL manipulation bypassing constraints
- Database corruption
- Improper data migration from external systems

#### Recovery Steps

If duplicates are detected during deployment:

1. **Review**: Check deployment logs for duplicate warning messages
2. **Verify**: Use the SQL queries above to identify affected users
3. **Automatic Cleanup**: Re-run `create_super_tenant` command - it will handle cleanup automatically
4. **Manual Cleanup** (if needed):
   ```bash
   # Backup first!
   pg_dump projectmeats_staging > backup_before_cleanup.sql
   
   # Delete duplicate users (keep lowest ID)
   DELETE FROM auth_user 
   WHERE username = 'duplicate_username' 
   AND id NOT IN (
     SELECT MIN(id) FROM auth_user WHERE username = 'duplicate_username'
   );
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

#### TypeScript Lint Errors in CI/CD

Frontend builds in CI/CD environments treat ESLint warnings as errors (due to `CI=true` environment variable). This is a best practice to maintain code quality but can cause deployment failures if lint warnings are present.

**Common Issue: `@typescript-eslint/no-explicit-any` Error**

The ESLint rule `@typescript-eslint/no-explicit-any` prevents the use of the `any` type, which bypasses TypeScript's type checking.

**Problem:**
```typescript
catch (error: any) {  // ❌ Causes lint error in CI
  const message = error?.response?.data?.detail || 'Error occurred';
}
```

**Solution - Use `unknown` with Type Assertion:**
```typescript
catch (error: unknown) {  // ✅ Type-safe approach
  // Assert the expected error structure for safe property access
  const err = error as { response?: { data?: { detail?: string; message?: string } }; message?: string };
  const message = err?.response?.data?.detail 
    || err?.response?.data?.message 
    || err?.message 
    || 'Error occurred';
}
```

**Best Practices:**
- Always use `unknown` instead of `any` for error types in catch blocks
- Add a comment explaining the type assertion for maintainability
- Use optional chaining (`?.`) and nullish coalescing (`||`) for safe property access
- Define a fallback error message for better user experience

**Testing:**
```bash
# Run lint check locally
cd frontend && npm run lint

# Run build to verify no CI errors
cd frontend && npm run build

# Fix auto-fixable lint errors
cd frontend && npm run lint:fix
```

**Note:** The `.eslintrc.json` configuration sets this rule to "warn" in development, but CI treats all warnings as errors to enforce code quality standards.

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