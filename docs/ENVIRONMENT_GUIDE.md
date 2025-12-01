# ProjectMeats Environment Configuration Guide

**Last Updated**: December 2025

## Overview

ProjectMeats uses a centralized environment configuration system that provides:
- **Centralized management** of all environment variables
- **Environment-specific configurations** (development, staging, production)
- **Validation and error checking** for required variables
- **Security best practices** for each deployment environment
- **Easy deployment** with standardized configurations

---

## 🔐 Security Best Practices for Environment Variables

### Using GitHub Secrets (Recommended for CI/CD)

All sensitive environment variables should be stored as GitHub Secrets:

1. Navigate to: **Repository Settings → Secrets and variables → Actions**
2. Create environment-specific secrets under **Environments** (e.g., `uat2-backend`, `prod2-backend`)
3. Reference secrets in workflows: `${{ secrets.SECRET_NAME }}`

### Secret Naming Convention

| Environment | Prefix | Example |
|-------------|--------|---------|
| Development | `DEVELOPMENT_` | `DEVELOPMENT_DB_PASSWORD` |
| Staging/UAT | `STAGING_` | `STAGING_SECRET_KEY` |
| Production | `PRODUCTION_` | `PRODUCTION_DB_PASSWORD` |

### Security Rules

1. **Never commit secrets** to version control
2. **Never log sensitive values** in application logs
3. **Rotate secrets** every 90 days (production)
4. **Use strong, unique secrets** for each environment
5. **Encrypt backups** containing environment data

### Generate Secure Secrets

```bash
# Generate Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate random password
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using OpenSSL
openssl rand -base64 32
```

---

## Quick Start

### 1. Set Up Development Environment
```bash
# Option 1: Using the configuration manager (recommended)
python config/manage_env.py setup development

# Option 2: Using Make
make env-dev

# Option 3: Manual setup
cp config/environments/development.env backend/.env
cp config/shared/frontend.env.template frontend/.env.local
```

### 2. Validate Configuration
```bash
python config/manage_env.py validate
# or
make env-validate
```

### 3. Start Development Servers
```bash
# Start both backend and frontend
make dev

# Or start individually
make backend    # Django server on :8000
make frontend   # React server on :3000
```

## Environment Configuration Files

### Directory Structure
```
config/
├── README.md                    # Environment configuration documentation
├── environments/               # Environment-specific configurations
│   ├── development.env        # Development environment
│   ├── staging.env           # Staging environment
│   └── production.env        # Production environment
├── shared/                    # Shared configuration templates
│   ├── backend.env.template  # Backend environment template
│   └── frontend.env.template # Frontend environment template
└── deployment/               # Deployment configurations
    └── manage_env.py         # Environment management script
```

### Environment Files

#### Development (config/environments/development.env)
- **Database**: SQLite for local development (temporary - see note below)
- **Debug**: Enabled for development
- **CORS**: Allows localhost origins
- **Security**: Disabled for development ease
- **AI Services**: Optional API keys

**Note**: Development temporarily uses SQLite instead of PostgreSQL due to Postgres server setup issues. This will be reverted to PostgreSQL for environment parity once resolved.

#### Staging (config/environments/staging.env)  
**IMPORTANT:** This configuration is for UAT environment (uat.meatscentral.com).  
**DEPRECATED:** staging.meatscentral.com is deprecated. UAT is the active middle environment per pipeline configuration.

- **Database**: PostgreSQL with environment variables
- **Debug**: Disabled  
- **CORS**: Restricted to staging domains
- **Security**: Enabled with HTTPS
- **AI Services**: Staging API keys
- **Monitoring**: Basic monitoring setup

#### Production (config/environments/production.env)
- **Database**: PostgreSQL with connection pooling
- **Debug**: Disabled
- **CORS**: Restricted to production domains only
- **Security**: Full security features enabled
- **AI Services**: Production API keys
- **Monitoring**: Full monitoring and alerting
- **Performance**: Optimized settings

## Environment Variables

### Backend Variables

#### Django Core
| Variable | Description | Development | Staging | Production |
|----------|-------------|-------------|---------|-----------|
| `SECRET_KEY` | Django secret key | Generated | ${STAGING_SECRET_KEY} | ${PRODUCTION_SECRET_KEY} |
| `DEBUG` | Debug mode | `True` | `False` | `False` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` | Staging domains | Production domains |

#### Database
| Variable | Description | Development | Staging | Production |
|----------|-------------|-------------|---------|-----------|
| `DATABASE_URL` | Database connection | `sqlite:///db.sqlite3` (temporary) | PostgreSQL URL | PostgreSQL URL with pooling |

#### Security & CORS
| Variable | Description | Development | Staging | Production |
|----------|-------------|-------------|---------|-----------|
| `CORS_ALLOWED_ORIGINS` | CORS origins | `localhost:3000` | Staging frontend | Production frontend only |
| `SECURE_SSL_REDIRECT` | Force HTTPS | `False` | `True` | `True` |
| `SECURE_HSTS_SECONDS` | HSTS max age | `0` | `31536000` | `31536000` |

#### AI Services
| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |

#### Superuser Configuration
| Variable | Description | Development | Staging | Production |
|----------|-------------|-------------|---------|-----------|
| `SUPERUSER_USERNAME` | Admin username | `admin` | `${STAGING_SUPERUSER_USERNAME}` | `${PRODUCTION_SUPERUSER_USERNAME}` |
| `SUPERUSER_EMAIL` | Admin email | `admin@meatscentral.com` | `${STAGING_SUPERUSER_EMAIL}` | `${PRODUCTION_SUPERUSER_EMAIL}` |
| `SUPERUSER_PASSWORD` | Admin password | Dev password | `${STAGING_SUPERUSER_PASSWORD}` | `${PRODUCTION_SUPERUSER_PASSWORD}` |

### Frontend Variables

#### API Configuration
| Variable | Description | Example |
|----------|-------------|---------|
| `REACT_APP_API_BASE_URL` | Backend API URL | `http://localhost:8000/api/v1` |
| `REACT_APP_ENVIRONMENT` | Environment name | `development` |

#### Feature Flags
| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_AI_ASSISTANT_ENABLED` | Enable AI chat | `true` |
| `REACT_APP_ENABLE_DOCUMENT_UPLOAD` | Enable file uploads | `true` |
| `REACT_APP_ENABLE_CHAT_EXPORT` | Enable chat export | `true` |

## Deployment Guide

### Development Deployment
1. **PostgreSQL Setup**: 
   - Install PostgreSQL locally (see docs/DEPLOYMENT_GUIDE.md for OS-specific instructions)
   - Create database: `createdb projectmeats_dev`
   - Create user: `createuser -P projectmeats_dev` (password: devpassword)
   - Grant privileges: `psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;"`
2. **Setup**: `python config/manage_env.py setup development`
3. **Install**: `pip install -r backend/requirements.txt && cd frontend && npm install`
4. **Migrate**: `cd backend && python manage.py migrate`
5. **Superuser**: `make superuser` (creates admin user from environment variables)
6. **Run**: `make dev`

### Staging Deployment
**IMPORTANT NOTE:** "Staging" refers to the UAT environment (uat.meatscentral.com).  
**DEPRECATED:** staging.meatscentral.com is no longer used. UAT is the active middle environment per our pipeline configuration.

1. **Configure GitHub Secrets**: Before deployment, ensure all required secrets are configured in GitHub repository settings (see "Required GitHub Secrets for Staging" section below)
2. **Environment Variables**: Set staging environment variables on the staging server's environment configuration
3. **Setup**: `python config/manage_env.py setup staging`
4. **Validate**: `python config/manage_env.py validate`
5. **Deploy**: Follow your staging deployment process (GitHub Actions workflow handles this automatically)
6. **Superuser**: Automatically created during deployment via `python manage.py create_super_tenant`

#### Required GitHub Secrets for Staging

**IMPORTANT:** Staging refers to UAT environment (uat.meatscentral.com).  
**DEPRECATED:** staging.meatscentral.com is no longer used. Use uat.meatscentral.com as the primary middle environment.

The following secrets must be configured in GitHub for staging deployment:

**Repository-Level Secrets** (Settings → Secrets and variables → Actions → Repository secrets):
- `STAGING_HOST` - Staging server IP/hostname (e.g., `192.168.1.101` or `uat.yourdomain.com`)
- `STAGING_USER` - SSH username for staging server (e.g., `django`)
- `SSH_PASSWORD` - SSH password for staging server

**Environment Secrets for `uat2-backend`** (Settings → Environments → uat2-backend → Environment secrets):

*Required Secrets:*
- `STAGING_SUPERUSER_USERNAME` - Admin username for staging
- `STAGING_SUPERUSER_EMAIL` - Admin email for staging  
- `STAGING_SUPERUSER_PASSWORD` - Admin password for staging
- `STAGING_SECRET_KEY` - Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `STAGING_DB_USER` - PostgreSQL database username
- `STAGING_DB_PASSWORD` - PostgreSQL database password
- `STAGING_DB_HOST` - PostgreSQL database host (e.g., `localhost` or DB server IP)
- `STAGING_DB_PORT` - PostgreSQL database port (default: `5432`)
- `STAGING_DB_NAME` - PostgreSQL database name (e.g., `projectmeats_staging`)
- `STAGING_DOMAIN` - Main staging domain (e.g., `uat.meatscentral.com`)
- `STAGING_API_DOMAIN` - API staging domain (e.g., `uat-api.meatscentral.com`)
- `STAGING_FRONTEND_DOMAIN` - Frontend staging domain (e.g., `uat.meatscentral.com`)
- `STAGING_API_URL` - Staging backend API URL (e.g., `https://uat-api.meatscentral.com`)

*Optional Secrets (if features are enabled):*
- `STAGING_OPENAI_API_KEY` - OpenAI API key for AI features
- `STAGING_ANTHROPIC_API_KEY` - Anthropic API key for AI features
- `STAGING_EMAIL_HOST` - SMTP server hostname
- `STAGING_EMAIL_USER` - SMTP username
- `STAGING_EMAIL_PASSWORD` - SMTP password
- `STAGING_REDIS_HOST` - Redis server host (if using Redis cache)
- `STAGING_REDIS_PORT` - Redis server port (default: `6379`)
- `STAGING_SENTRY_DSN` - Sentry DSN for error tracking

**Note**: These secrets are referenced in `config/environments/staging.env` using placeholder syntax like `${STAGING_DB_USER}`. The actual values must be set as environment variables on the staging server.

### Production Deployment
1. **Environment Variables**: Set production environment variables securely (including `PRODUCTION_SUPERUSER_*` variables)
2. **Setup**: `python config/manage_env.py setup production`
3. **Validate**: `python config/manage_env.py validate`
4. **Security Check**: Verify all security settings are enabled
5. **Deploy**: Follow your production deployment process
6. **Superuser**: Automatically created during deployment via `python manage.py create_super_tenant`

## Security Best Practices

### Superuser Management

**Overview:**
ProjectMeats uses environment variables for all superuser credentials to ensure security and prevent hardcoded credentials in the codebase. The `create_super_tenant` management command automatically handles superuser creation and updates.

**Environment Variables:**
- `SUPERUSER_USERNAME` - Admin username (default: admin)
- `SUPERUSER_EMAIL` - Admin email address
- `SUPERUSER_PASSWORD` - Admin password (must be secure for production)

**Development Environment:**
```bash
# Set in config/environments/development.env
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@meatscentral.com
SUPERUSER_PASSWORD=DevAdmin123!SecurePass
```

**Staging/Production Environments:**
```bash
# Set as deployment secrets in GitHub or your platform
# NOTE: "Staging" refers to UAT (uat.meatscentral.com)
# DEPRECATED: staging.meatscentral.com - use uat.meatscentral.com instead

STAGING_SUPERUSER_USERNAME=admin
STAGING_SUPERUSER_EMAIL=admin@uat.meatscentral.com
STAGING_SUPERUSER_PASSWORD=<secure-password>

PRODUCTION_SUPERUSER_USERNAME=admin
PRODUCTION_SUPERUSER_EMAIL=admin@meatscentral.com
PRODUCTION_SUPERUSER_PASSWORD=<secure-password>
```

**Creating/Updating Superuser:**
```bash
# Via Make command (recommended)
make superuser

# Direct command
python manage.py create_super_tenant

# With verbose output
python manage.py create_super_tenant --verbosity 2
```

**Automatic Execution:**
The superuser creation command runs automatically:
- During initial setup (`python setup_env.py`)
- After migrations in development setup
- In deployment workflows (after migrations)

**Command Features:**
- **Idempotent**: Safe to run multiple times
- **Updates existing users**: Updates password if user already exists
- **Multi-tenancy support**: Creates root tenant and links superuser
- **Secure**: Uses Django's password hashing
- **Configurable**: All settings from environment variables

### Secret Management
- **Generate unique secrets** for each environment
- **Store secrets securely** using your deployment platform's secret management
- **Never commit secrets** to version control
- **Rotate secrets regularly** especially for production

### Environment Separation  
- **Use different databases** for each environment
- **Separate API keys** for AI services per environment
- **Restrict CORS origins** to specific domains
- **Enable security features** in staging and production

### Access Control
- **Limit staging access** to development team only
- **Secure production access** with proper authentication
- **Monitor access logs** for suspicious activity
- **Regular security audits** of environment configurations

## Troubleshooting

### Common Issues

#### CORS Errors
**Symptom**: Frontend can't connect to backend
**Solution**: 
1. Check `CORS_ALLOWED_ORIGINS` in backend `.env`
2. Ensure frontend domain is included
3. Restart backend server after changes

#### Database Connection Errors
**Symptom**: Django can't connect to database
**Solution**:
1. Verify `DATABASE_URL` format
2. Check database credentials
3. Ensure database server is running
4. Test connection manually

#### Environment Variable Not Found
**Symptom**: `KeyError` for environment variable
**Solution**:
1. Run validation: `python config/manage_env.py validate`
2. Check variable exists in `.env` file
3. Ensure no typos in variable names
4. Restart application after changes

### Validation Commands
```bash
# Validate current environment
python config/manage_env.py validate

# Generate new secrets
python config/manage_env.py generate-secrets

# Check Django configuration
cd backend && python manage.py check

# Test frontend build
cd frontend && npm run build
```

## Migration from Legacy Configuration

### Automatic Migration
The new configuration system is backward compatible. Existing `.env` and `.env.local` files will continue to work.

### Manual Migration Steps
1. **Backup existing files**: `cp backend/.env backend/.env.backup`
2. **Set up new configuration**: `python config/manage_env.py setup development`
3. **Copy custom values**: Transfer any custom configurations from backup files
4. **Validate setup**: `python config/manage_env.py validate`
5. **Test application**: `make dev`

### Legacy File Support
- `backend/.env.example` - Now points to centralized system
- `frontend/.env.example` - Now points to centralized system
- Existing `.env` files will be backed up automatically

## Environment Management Commands

### Configuration Manager
```bash
# Set up environments
python config/manage_env.py setup development
python config/manage_env.py setup staging
python config/manage_env.py setup production

# Validation and utilities
python config/manage_env.py validate
python config/manage_env.py generate-secrets
```

### Make Commands
```bash
# Environment setup
make env-dev        # Set up development
make env-staging    # Set up staging  
make env-prod       # Set up production
make env-validate   # Validate configuration
make env-secrets    # Generate secrets

# Development
make dev           # Start development servers
make backend       # Start backend only
make frontend      # Start frontend only
```

### Project Setup
```bash
# Complete project setup (recommended)
python setup.py

# Component setup
python setup.py --backend
python setup.py --frontend
```

This centralized system ensures consistent, secure, and easily manageable environment configurations across all deployment environments.