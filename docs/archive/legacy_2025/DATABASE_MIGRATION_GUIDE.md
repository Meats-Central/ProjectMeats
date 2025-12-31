# Database Migration Setup - Current Implementation

**Last Updated:** 2025-12-04  
**Status:** ✅ Production Ready  
**Approach:** SSH Tunnel from GitHub Actions to Deployment Servers

---

## Overview

Database migrations in our deployment pipeline run on deployment servers via SSH tunnel. This approach provides secure, reliable migrations without exposing the database to GitHub Actions IP ranges.

---

## How It Works

### Architecture

```
GitHub Actions Workflow
  ↓
  SSH Connection (via sshpass)
  ↓
Deployment Server (dev/UAT/prod)
  ↓
  Execute: python manage.py migrate
  ↓
DigitalOcean Managed PostgreSQL Database
```

### Key Benefits

- ✅ **No firewall changes** - Database remains restricted to deployment servers
- ✅ **Secure** - No need to expose database to 5,462 GitHub Actions IP ranges
- ✅ **Reliable** - Uses server's existing configuration (.env, venv)
- ✅ **Maintainable** - No ongoing IP range updates needed

---

## Implementation Details

### Workflows Updated

All three deployment workflows use SSH tunnel for migrations:
- `.github/workflows/11-dev-deployment.yml` (Development)
- `.github/workflows/12-uat-deployment.yml` (UAT)
- `.github/workflows/13-prod-deployment.yml` (Production)

### Migration Job Structure

```yaml
migrate:
  runs-on: ubuntu-latest
  needs: [build-and-push, test-backend]
  environment: dev-backend
  
  steps:
    - name: Setup SSH
      run: |
        sudo apt-get update
        sudo apt-get install -y sshpass
        mkdir -p ~/.ssh
        ssh-keyscan -H "${{ secrets.DEV_HOST }}" >> ~/.ssh/known_hosts
    
    - name: Run migrations via SSH on deployment server
      env:
        SSHPASS: ${{ secrets.DEV_SSH_PASSWORD }}
      run: |
        sshpass -e ssh -o StrictHostKeyChecking=yes \
          ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }} << 'SSH_END'
        set -euo pipefail
        
        cd /home/django/ProjectMeats/backend
        source ../venv/bin/activate
        python manage.py migrate --fake-initial --noinput
        SSH_END
```

---

## Required Secrets

Each environment requires three secrets:

### Development Environment (`dev-backend`)
```
DEV_HOST            # Deployment server hostname/IP
DEV_USER            # SSH username (typically 'django')
DEV_SSH_PASSWORD    # SSH password
```

### UAT Environment (`uat2-backend`)
```
UAT_HOST
UAT_USER
UAT_SSH_PASSWORD
```

### Production Environment (`prod2-backend`)
```
PROD_HOST
PROD_USER
PROD_SSH_PASSWORD
```

### Additional Secrets (Already Configured)
```
DEV_DATABASE_URL    # PostgreSQL connection string
DEV_SECRET_KEY      # Django secret key
DEV_DJANGO_SETTINGS_MODULE  # Settings module path
```

---

## Migration Process

### 1. Trigger
Deployments are triggered by:
- Push to `development` branch → Dev deployment
- Merge to `uat` branch → UAT deployment
- Merge to `main` branch → Production deployment

### 2. Workflow Steps
1. **Lint YAML** - Validate workflow files
2. **Build & Push** - Build Docker images, push to registries
3. **Test** - Run frontend and backend tests
4. **Migrate** ⭐ - SSH to server, run migrations
5. **Deploy** - Deploy new containers
6. **Health Check** - Verify deployment

### 3. Migration Execution

On the deployment server:
```bash
cd /home/django/ProjectMeats/backend
source ../venv/bin/activate
python manage.py migrate --fake-initial --noinput
```

**Flags:**
- `--fake-initial` - Makes migrations idempotent (safe to rerun)
- `--noinput` - Non-interactive mode for CI/CD

---

## Troubleshooting

### Migration Job Fails: "Permission denied"

**Cause:** SSH credentials incorrect or user lacks permissions

**Solution:**
1. Verify SSH secrets are correct:
   ```bash
   ssh $DEV_USER@$DEV_HOST
   ```
2. Ensure user has access to project directory:
   ```bash
   ls -la /home/django/ProjectMeats/backend
   ```

---

### Migration Job Fails: "Project directory not found"

**Cause:** Project path on server is different

**Solution:**
Update the `cd` command in workflow to match your server's path:
```yaml
cd /your/actual/path/to/ProjectMeats/backend
```

---

### Migration Job Fails: "No such file or directory: venv"

**Cause:** Virtual environment not set up on server

**Solution:**
1. SSH to server
2. Create venv:
   ```bash
   cd /home/django/ProjectMeats
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

---

### Migrations Hang or Timeout

**Cause:** Database connection issue from server

**Solution:**
1. Verify `.env` file exists on server:
   ```bash
   cat /home/django/ProjectMeats/backend/.env
   ```
2. Test database connection:
   ```bash
   cd /home/django/ProjectMeats/backend
   source ../venv/bin/activate
   python manage.py check --database default
   ```

---

## Verification

### Check Migration Status

After deployment, verify migrations ran successfully:

```bash
# View workflow logs
gh run view --log | grep "Migrations completed successfully"

# SSH to server and check migration status
ssh django@your-server
cd /home/django/ProjectMeats/backend
source ../venv/bin/activate
python manage.py showmigrations
```

### Expected Output

Successful migration logs show:
```
=== Running migrations on deployment server ===
Activating virtual environment...
Running database migrations...
Operations to perform:
  Apply all migrations: [list of apps]
Running migrations:
  Applying app.0001_initial... OK
  [or "No migrations to apply." if up to date]
✓ Migrations completed successfully
```

---

## Database Configuration

### Server .env File

Each deployment server must have a `.env` file with:

```bash
# /home/django/ProjectMeats/backend/.env

DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key
DJANGO_SETTINGS_MODULE=projectmeats.settings.production
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

### DigitalOcean Database Settings

**Trusted Sources:**
- Add deployment server IP addresses
- **Do NOT add GitHub Actions IP ranges** (5,462 ranges, changes frequently)

**Connection Settings:**
- SSL Mode: Required
- Port: 25060 (default for DigitalOcean)
- Database: defaultdb

---

## Multi-Tenancy Considerations

### Current Implementation

The migrations use standard Django `migrate` command:
```bash
python manage.py migrate --fake-initial --noinput
```

### For django-tenants (Future)

If using `django-tenants`, update migration commands:

```bash
# Shared schema (public)
python manage.py migrate_schemas --shared --fake-initial --noinput

# Create super tenant
python manage.py create_super_tenant --no-input

# Tenant schemas
python manage.py migrate_schemas --tenant --noinput
```

**Note:** Currently not implemented as `django-tenants` is not installed in requirements.

---

## Security Best Practices

### SSH Credentials
- ✅ Use SSH keys instead of passwords (recommended upgrade)
- ✅ Rotate SSH passwords quarterly
- ✅ Use different credentials per environment
- ✅ Store secrets in GitHub environment secrets (not repository secrets)

### Database Access
- ✅ Database only accessible from deployment servers
- ✅ Use strong, unique passwords (32+ characters)
- ✅ Enable SSL/TLS for all connections
- ✅ Monitor connection logs for suspicious activity

### Migration Safety
- ✅ Always use `--fake-initial` for idempotency
- ✅ Test migrations in dev/UAT before production
- ✅ Keep database backups before major migrations
- ✅ Use migration squashing for performance

---

## Maintenance

### Regular Tasks

**Monthly:**
- Review and rotate SSH passwords
- Check migration execution times
- Review database connection logs

**Quarterly:**
- Update Django and dependencies
- Review and optimize slow migrations
- Audit database access patterns

**Annually:**
- Consider migration squashing
- Review database performance
- Update deployment documentation

---

## Related Documentation

- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **GitHub Actions DB Access:** `GITHUB_ACTIONS_DATABASE_ACCESS.md`
- **Historical Context:** `archived/2025-12-04-db-migration-fix/`

---

## Support

### Quick Links

- **Workflow Runs:** https://github.com/Meats-Central/ProjectMeats/actions
- **Database Console:** https://cloud.digitalocean.com/databases
- **Server SSH:** `ssh django@{server-host}`

### Common Commands

```bash
# View recent migrations
gh run list --workflow "Deploy Dev" --limit 5

# Watch current deployment
gh run watch

# Check migration logs
gh run view --log | grep migrate

# SSH to server
ssh django@your-server

# Run migrations manually
cd /home/django/ProjectMeats/backend
source ../venv/bin/activate
python manage.py migrate --fake-initial --noinput
```

---

## Changelog

### 2025-12-04 - Initial Implementation
- Implemented SSH tunnel approach
- Updated all three deployment workflows
- Documented setup and troubleshooting
- Verified successful migration execution

**PRs:**
- #892 - Add DB_NAME default value
- #894 - Parse DATABASE_URL credentials
- #900 - Fix secret naming
- #902 - Implement SSH tunnel approach ⭐

---

## Contact

For issues or questions:
1. Check workflow logs
2. Review this documentation
3. Check archived docs for historical context
4. Contact DevOps team or repository maintainers
