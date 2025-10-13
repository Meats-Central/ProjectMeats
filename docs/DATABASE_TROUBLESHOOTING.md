# Database Permissions and Read-Only Error Troubleshooting

This document provides guidance for troubleshooting and resolving "attempt to write a readonly database" errors in ProjectMeats.

## Overview

The "OperationalError: attempt to write a readonly database" error typically occurs when:

1. **File Permission Issues**: The database file or its directory lacks write permissions for the application user
2. **Database Engine Mismatch**: Using SQLite in environments that should use PostgreSQL
3. **Session Management Issues**: Django admin sessions cannot be written due to readonly database

## Environment-Specific Guidance

### Development Environment (dev.meatscentral.com)

**Recommended Configuration**: PostgreSQL for environment parity with staging/production

**Issue**: If using SQLite, readonly errors may occur due to file permissions.

**Solutions**:

#### Option 1: Migrate to PostgreSQL (Recommended)

1. **Update `backend/projectmeats/settings/development.py`**:
   ```python
   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.postgresql",
           "NAME": config("DB_NAME"),
           "USER": config("DB_USER"),
           "PASSWORD": config("DB_PASSWORD"),
           "HOST": config("DB_HOST"),
           "PORT": config("DB_PORT", default="5432"),
       }
   }
   ```

2. **Configure environment variables** in `.env`:
   ```bash
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=projectmeats_dev
   DB_USER=projectmeats_dev
   DB_PASSWORD=your_secure_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

3. **Install PostgreSQL adapter** (if not already installed):
   ```bash
   pip install psycopg[binary]
   ```

4. **Create PostgreSQL database and user**:
   ```sql
   CREATE DATABASE projectmeats_dev;
   CREATE USER projectmeats_dev WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE projectmeats_dev TO projectmeats_dev;
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

#### Option 2: Fix SQLite Permissions (Temporary)

If using SQLite temporarily, ensure proper permissions:

1. **SSH to development server**:
   ```bash
   ssh user@dev.meatscentral.com
   ```

2. **Check file permissions**:
   ```bash
   ls -l /home/django/ProjectMeats/backend/db.sqlite3
   ls -ld /home/django/ProjectMeats/backend/
   ```

3. **Fix permissions**:
   ```bash
   # Fix database file ownership
   sudo chown django:django /home/django/ProjectMeats/backend/db.sqlite3
   
   # Fix database file permissions (read+write for owner and group)
   sudo chmod 664 /home/django/ProjectMeats/backend/db.sqlite3
   
   # Fix directory permissions (must be writable for SQLite journal files)
   sudo chmod 775 /home/django/ProjectMeats/backend/
   ```

4. **Restart application server**:
   ```bash
   sudo systemctl restart gunicorn
   # or
   sudo systemctl restart projectmeats
   ```

### Production Environment

**Required Configuration**: PostgreSQL with proper SSL/TLS

**Never use SQLite in production** - it doesn't support concurrent writes and lacks the robustness needed for production environments.

## Django Admin Session Issues

### Symptoms
- "View as Admin" button redirects to login page repeatedly
- Session-related errors in logs during authentication
- Unable to maintain admin login state

### Root Cause
Django admin requires database write access to:
- Create and update session records
- Track user authentication state
- Store CSRF tokens

### Solutions

1. **Verify database write permissions** (see solutions above)

2. **Check session backend configuration** in settings:
   ```python
   # Default: database-backed sessions (requires write access)
   SESSION_ENGINE = 'django.contrib.sessions.backends.db'
   
   # Alternative: cache-backed sessions (no database writes)
   SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
   ```

3. **Clear stale sessions**:
   ```bash
   python manage.py clearsessions
   ```

## Error Detection in Application

The application now includes enhanced error handling for readonly database errors:

### Custom Exception Handler

Located in `apps/core/exceptions.py`, the custom exception handler:

1. **Detects readonly database errors** by checking error messages
2. **Logs detailed context**:
   - User (authenticated or anonymous)
   - Request path and method
   - View name
   - Full exception traceback
3. **Returns user-friendly error messages**:
   ```json
   {
     "error": "Database write failure",
     "details": "Database is in read-only mode. Please check permissions or contact administrator.",
     "hint": "This may be caused by file permission issues. Server administrators should verify database file ownership and permissions."
   }
   ```

### Middleware Error Handling

The `TenantMiddleware` includes error handling for database errors during:
- User authentication
- Session operations
- Tenant resolution

Errors are logged with full context for troubleshooting.

## Logging and Monitoring

### Log Locations

**Development**:
- Console output (DEBUG level)
- Application logs: `/var/log/projectmeats/`

**Production**:
- Syslog integration
- Centralized logging (if configured)

### Key Log Messages

Look for these log messages when troubleshooting:

```
Read-Only Database Error: attempt to write a readonly database
Database error when fetching TenantUser: user=username, tenant=tenant_slug, error=OperationalError
Readonly database error detected: user=username, path=/admin/
```

## Testing

Run database tests to verify write permissions:

```bash
# Run all database tests
python manage.py test apps.core.tests.test_database

# Run specific test for readonly errors
python manage.py test apps.core.tests.test_database.ReadOnlyDatabaseErrorTest
```

## Security Best Practices

### PostgreSQL Configuration

1. **Use SSL/TLS for connections**:
   ```python
   DATABASES = {
       "default": {
           "OPTIONS": {
               "sslmode": "require",
           }
       }
   }
   ```

2. **Configure pg_hba.conf** for secure access:
   ```
   # TYPE  DATABASE        USER            ADDRESS                 METHOD
   host    projectmeats    projectmeats    127.0.0.1/32           md5
   hostssl projectmeats    projectmeats    0.0.0.0/0              md5
   ```

3. **Use minimal privileges**:
   ```sql
   GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO projectmeats_dev;
   GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO projectmeats_dev;
   ```

### OWASP Compliance

- **Database credentials**: Store in environment variables, never commit to git
- **Connection strings**: Use encrypted connections (SSL/TLS) for remote databases
- **Audit logging**: Monitor database access and permission errors
- **Least privilege**: Grant only necessary database permissions

### GDPR Considerations

- **Data encryption**: Use PostgreSQL encryption for sensitive data at rest
- **Access logging**: Maintain audit trail of database access
- **Backup procedures**: Ensure encrypted backups with retention policies

## Preventive Measures

### Development Best Practices

1. **Use PostgreSQL in all environments** for environment parity
2. **Automate database setup** with Docker Compose or setup scripts
3. **Document database configuration** in environment variable files
4. **Regular testing** of database permissions in CI/CD pipeline

### Monitoring

1. **Health checks** for database connectivity and write access
2. **Alerts** for database permission errors
3. **Metrics** for database operation latency and failures

### Makefile Integration

The project Makefile includes database validation:

```bash
# Validate database configuration
make validate-db-config

# Run database tests
make test-backend
```

## References

- [Django Database Settings](https://docs.djangoproject.com/en/stable/ref/settings/#databases)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [OWASP Database Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html)
- [12-Factor App: Config](https://12factor.net/config)
- [Django Security Best Practices](https://docs.djangoproject.com/en/stable/topics/security/)

## Support

For additional help:

1. Check application logs for detailed error messages
2. Review this troubleshooting guide
3. Consult `docs/BACKEND_ARCHITECTURE.md` for database configuration
4. Contact system administrators for server-level access issues
