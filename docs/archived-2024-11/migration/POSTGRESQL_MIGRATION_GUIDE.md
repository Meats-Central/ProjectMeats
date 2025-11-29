# PostgreSQL Migration - Post-Merge Setup Guide

This document provides step-by-step instructions for setting up PostgreSQL for the development environment after merging this PR.

## Overview

This PR migrates the development environment from SQLite to PostgreSQL for environment parity with staging and production. The implementation includes:

- ✅ PostgreSQL-first database configuration with SQLite fallback
- ✅ Environment variable-based configuration (12-Factor App)
- ✅ Enhanced error logging for database permission issues
- ✅ Comprehensive database connectivity tests
- ✅ Detailed troubleshooting documentation
- ✅ Deployment workflow updates with secret injection

## Required Actions After Merge

### 1. Set Up PostgreSQL Database Instance

Choose one of the following options:

#### Option A: DigitalOcean Managed Database (Recommended for Production-like Setup)

1. Log in to DigitalOcean
2. Navigate to Databases
3. Click "Create Database"
4. Select:
   - Database Engine: PostgreSQL 15
   - Plan: Dev Database (smallest plan for development)
   - Data Center: Same as dev-backend server
5. Create database named `projectmeats_dev`
6. Note the connection details provided

#### Option B: Self-Hosted PostgreSQL

```bash
# SSH into dev-backend.meatscentral.com
ssh django@dev-backend.meatscentral.com

# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE projectmeats_dev;
CREATE USER projectmeats_dev WITH PASSWORD 'CHANGE_THIS_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;
\q
EOF

# Configure PostgreSQL to allow password authentication
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add or modify line:
# local   projectmeats_dev    projectmeats_dev                            md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### Option C: Docker PostgreSQL (Local Development Only)

```bash
# Run PostgreSQL container
docker run --name projectmeats-postgres \
  -e POSTGRES_DB=projectmeats_dev \
  -e POSTGRES_USER=projectmeats_dev \
  -e POSTGRES_PASSWORD=dev_password \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Configure GitHub Secrets

Navigate to: Repository Settings → Environments → `dev-backend`

Add the following secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `DEVELOPMENT_DB_ENGINE` | `django.db.backends.postgresql` | (exact value) |
| `DEVELOPMENT_DB_NAME` | Database name | `projectmeats_dev` |
| `DEVELOPMENT_DB_USER` | Database user | `projectmeats_dev` |
| `DEVELOPMENT_DB_PASSWORD` | Database password | (secure password) |
| `DEVELOPMENT_DB_HOST` | Database host | `localhost` or `db-host.digitalocean.com` |
| `DEVELOPMENT_DB_PORT` | Database port | `5432` |

**Security Note:** Use a strong password (minimum 16 characters) for `DEVELOPMENT_DB_PASSWORD`.

Generate a secure password:
```bash
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

### 3. Update Local Development Environment (Optional)

If you want to use PostgreSQL for local development:

```bash
# Edit config/environments/development.env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=projectmeats_dev
DB_USER=projectmeats_dev
DB_PASSWORD=your_local_password
DB_HOST=localhost
DB_PORT=5432

# Run migrations
cd backend
python manage.py migrate

# Create superuser
python manage.py create_super_tenant
```

To continue using SQLite locally:
```bash
# Edit config/environments/development.env
DB_ENGINE=django.db.backends.sqlite3
```

### 4. Deploy and Verify

After configuring secrets, trigger a deployment:

1. Push a commit to the `development` branch
2. Monitor the deployment workflow
3. Verify deployment steps:
   - ✅ Database connection check passes
   - ✅ Migrations apply successfully
   - ✅ Superuser creation completes
   - ✅ Application starts without errors

### 5. Verification Checklist

After deployment, verify the following:

```bash
# SSH into dev-backend
ssh django@dev-backend.meatscentral.com

# Check Django can connect to database
cd /home/django/ProjectMeats/backend
source venv/bin/activate
python manage.py check --database default

# Verify migrations are applied
python manage.py showmigrations

# Test database write operations
python manage.py shell
>>> from apps.core.models import Protein
>>> Protein.objects.create(name="Test Write Operation")
>>> Protein.objects.filter(name="Test Write Operation").delete()
>>> # Should complete without errors
>>> exit()

# Check logs for any database errors
tail -f /home/django/ProjectMeats/backend/logs/django.log
```

Access the development site and verify:
- ✅ Application loads successfully
- ✅ Login/logout works (tests session handling)
- ✅ No "readonly database" errors in logs
- ✅ Can create/edit/delete records

### 6. Troubleshooting

If you encounter issues, refer to:

- **Database Configuration**: [docs/environment-variables.md](docs/environment-variables.md)
- **Troubleshooting Guide**: [docs/multi-tenancy.md](docs/multi-tenancy.md#troubleshooting-database-issues)
- **Test Suite**: Run `python manage.py test apps.core.tests.test_database`

Common issues:

#### Connection Refused
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check PostgreSQL is listening
sudo netstat -plnt | grep 5432

# Verify firewall allows connection
sudo ufw status
```

#### Authentication Failed
```bash
# Verify user exists
sudo -u postgres psql -c "\du"

# Reset password if needed
sudo -u postgres psql << EOF
ALTER USER projectmeats_dev WITH PASSWORD 'new_password';
EOF
```

#### Permission Denied
```bash
# Grant necessary permissions
sudo -u postgres psql << EOF
GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;
GRANT ALL PRIVILEGES ON SCHEMA public TO projectmeats_dev;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO projectmeats_dev;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO projectmeats_dev;
EOF
```

## Rollback Plan

If PostgreSQL setup fails and you need to rollback to SQLite:

1. Update GitHub Secret: `DEVELOPMENT_DB_ENGINE=django.db.backends.sqlite3`
2. Deployment will automatically use SQLite fallback
3. Note: The SQLite permission fix is included in the deployment script

## Benefits of This Migration

1. **Environment Parity**: Development matches staging/production
2. **Better Testing**: Database-specific features tested properly
3. **Production-like Data**: Can use production dumps for testing
4. **Advanced Features**: Support for PostgreSQL-specific features
5. **Better Performance**: PostgreSQL handles concurrent connections better
6. **Reliability**: No more "readonly database" errors

## Support

For questions or issues:
1. Check documentation in `docs/` directory
2. Review deployment logs in GitHub Actions
3. Check application logs on server
4. Create an issue in the repository

## Security Reminders

- ✅ Never commit database credentials to git
- ✅ Use strong passwords (minimum 16 characters)
- ✅ Store secrets in GitHub Secrets only
- ✅ Rotate credentials every 90 days
- ✅ Restrict database access to application servers only
- ✅ Enable SSL/TLS for production database connections
