# Resolve DB_ENGINE ValueError in Dev Deployment Pipeline

## Problem Description

The development backend deployment pipeline is failing with a `ValueError` for an unsupported `DB_ENGINE` value. Analysis shows the error occurs in `backend/projectmeats/settings/development.py` at lines 33-64 when the `DB_ENGINE` environment variable is empty.

### Error Details

**Location:** `backend/projectmeats/settings/development.py` lines 60-64

**Error Message:**
```python
ValueError: Unsupported DB_ENGINE: ''. 
Supported values are 'django.db.backends.postgresql' or 'django.db.backends.sqlite3'
```

**Failed Workflow:** Actions run #18453607857

### Root Cause

The `DB_ENGINE` environment variable in the dev-backend GitHub environment is either:
1. Not set (secret doesn't exist)
2. Set to an empty string value

When using `python-decouple`'s `config()` function:
```python
DB_ENGINE = config("DB_ENGINE", default="django.db.backends.sqlite3")
```

Empty strings are treated as **valid values**, not as missing values, so the default is not applied. This causes the `ValueError` when the code checks if `DB_ENGINE` equals a valid backend.

### Contrast with UAT Success

UAT (staging) deployment succeeds because:
- UAT uses server-side environment variables (not GitHub Secrets)
- Variables are properly configured on the UAT server
- No empty string values passed to the Django settings

## Solution

### Changes Implemented

Pull Request #[PR_NUMBER] implements the following fixes:

#### 1. Enhanced `backend/projectmeats/settings/development.py`

**Before:**
```python
DB_ENGINE = config("DB_ENGINE", default="django.db.backends.sqlite3")
```

**After:**
```python
import logging
logger = logging.getLogger(__name__)

# Handle empty strings correctly
DB_ENGINE = os.environ.get("DB_ENGINE", "").strip() or "django.db.backends.sqlite3"

# ... (database configuration) ...

else:
    logger.error(
        f"Invalid DB_ENGINE value: '{DB_ENGINE}'. "
        f"Supported values are 'django.db.backends.postgresql' or 'django.db.backends.sqlite3'. "
        f"See Django database settings docs: https://docs.djangoproject.com/en/stable/ref/settings/#databases"
    )
    raise ValueError(
        f"Unsupported DB_ENGINE: '{DB_ENGINE}'. "
        f"Ensure DB_ENGINE is set in GitHub Secrets (Settings → Environments → dev-backend) "
        f"or configure it in config/environments/development.env. "
        f"See Django docs: https://docs.djangoproject.com/en/stable/ref/settings/#databases"
    )

logger.info(f"Development environment using database backend: {DB_ENGINE}")
```

**Benefits:**
- Handles empty strings correctly with `.strip() or` pattern
- Adds logging for invalid values using Python's `logging` module
- Enhanced error messages with Django docs references
- Provides clear instructions for GitHub Secrets configuration
- Logs which database backend is being used for debugging

#### 2. Updated `.github/workflows/unified-deployment.yml`

Added validation step before deployment:

```yaml
- name: 🔍 Validate DB Configuration
  run: |
    DB_ENGINE_VALUE="${{ secrets.DEVELOPMENT_DB_ENGINE }}"
    if [ -z "$DB_ENGINE_VALUE" ] || [ "$DB_ENGINE_VALUE" = "" ]; then
      echo "⚠️ DEVELOPMENT_DB_ENGINE secret is empty, will use SQLite fallback"
      echo "📝 To use PostgreSQL, set DEVELOPMENT_DB_ENGINE='django.db.backends.postgresql' in GitHub Secrets"
      echo "   Navigate to: Settings → Environments → dev-backend → Add secret"
      echo "DB_ENGINE_FALLBACK=django.db.backends.sqlite3" >> $GITHUB_ENV
    else
      echo "✅ DEVELOPMENT_DB_ENGINE is set to: $DB_ENGINE_VALUE"
      echo "DB_ENGINE_FALLBACK=$DB_ENGINE_VALUE" >> $GITHUB_ENV
    fi
```

**Benefits:**
- Validates DB_ENGINE before deployment starts
- Sets appropriate fallback if secret is missing/empty
- Provides helpful messages in workflow logs
- Prevents deployment failure due to empty secret

#### 3. Enhanced `config/environments/development.env`

Added comprehensive documentation:

```bash
# Database Engine Selection
# Valid options:
#   - django.db.backends.postgresql  (Recommended for environment parity)
#   - django.db.backends.sqlite3     (Fallback for local development)
# 
# For GitHub Actions deployment, configure this in:
#   Repository Settings → Environments → dev-backend → Add secret: DEVELOPMENT_DB_ENGINE
#
# If not set or empty, SQLite will be used as fallback
DB_ENGINE=django.db.backends.postgresql
```

#### 4. Enhanced `docs/DEPLOYMENT_GUIDE.md`

Added comprehensive "Database Configuration and Verification" section (150+ lines):

- GitHub Secrets configuration table for dev-backend
- 4-step verification process
- Troubleshooting guide for ValueError
- Prevention measures
- References to Django documentation

#### 5. Enhanced `Makefile`

Added database configuration validation:

```makefile
validate-db-config:
	# Validates DB_ENGINE and required PostgreSQL variables
	# Provides helpful error messages
	# Integrated into 'make dev' command
```

### Configuration Requirements

To enforce valid `DB_ENGINE` values, configure GitHub Secrets:

#### Required GitHub Secrets (dev-backend environment)

| Secret Name | Required? | Description | Example Value |
|-------------|-----------|-------------|---------------|
| `DEVELOPMENT_DB_ENGINE` | ⚠️ Recommended | Database backend | `django.db.backends.postgresql` |
| `DEVELOPMENT_DB_NAME` | If using PostgreSQL | Database name | `projectmeats_dev` |
| `DEVELOPMENT_DB_USER` | If using PostgreSQL | Database user | `projectmeats_dev` |
| `DEVELOPMENT_DB_PASSWORD` | If using PostgreSQL | Database password | `your-secure-password` |
| `DEVELOPMENT_DB_HOST` | If using PostgreSQL | Database host | Managed DB hostname |
| `DEVELOPMENT_DB_PORT` | Optional | Database port | `5432` (default) |

#### How to Add Secrets

1. Navigate to: **Repository Settings → Environments → dev-backend**
2. Click "Add secret"
3. For each secret:
   - Name: `DEVELOPMENT_DB_ENGINE`
   - Value: `django.db.backends.postgresql`
4. Save each secret

**Note:** If `DEVELOPMENT_DB_ENGINE` is not set or empty, the system will automatically fall back to SQLite. However, PostgreSQL is strongly recommended for environment parity with UAT/production.

### Verification Steps

After configuring secrets, verify the deployment:

**Step 1: Trigger Manual Deployment**
1. Go to Actions tab
2. Select "Deploy to Development, UAT & Production" workflow
3. Click "Run workflow" on `development` branch
4. Select "deploy" action
5. Run the workflow

**Step 2: Monitor Workflow Logs**

Look for these indicators in the "Validate DB Configuration" step:

✅ **Success (PostgreSQL):**
```
✅ DEVELOPMENT_DB_ENGINE is set to: django.db.backends.postgresql
Development environment using database backend: django.db.backends.postgresql
```

⚠️ **Fallback (SQLite - if secret not set):**
```
⚠️ DEVELOPMENT_DB_ENGINE secret is empty, will use SQLite fallback
📝 To use PostgreSQL, set DEVELOPMENT_DB_ENGINE='django.db.backends.postgresql' in GitHub Secrets
```

❌ **Failure (should not occur with fixes):**
```
ValueError: Unsupported DB_ENGINE: ''.
```

**Step 3: Verify on Dev Server**

SSH into dev server and check:

```bash
cd /home/django/ProjectMeats/backend
source venv/bin/activate

# Check Django configuration
python manage.py check --database default

# Verify database backend
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DATABASES['default']['ENGINE'])
django.db.backends.postgresql  # Should show PostgreSQL if secret is set
```

## References

- **Django Database Settings:** https://docs.djangoproject.com/en/stable/ref/settings/#databases
- **Django Database Engines:** https://docs.djangoproject.com/en/stable/ref/databases/
- **12-Factor App Config:** https://12factor.net/config
- **Python-decouple Documentation:** https://github.com/henriquebastos/python-decouple

## Related Issues

- Environment parity between dev/UAT/production
- Database configuration in GitHub Actions
- Secret management best practices

## Action Items

- [ ] Add `DEVELOPMENT_DB_ENGINE` secret to dev-backend environment
- [ ] Add other PostgreSQL secrets (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST)
- [ ] Test deployment with new secrets configured
- [ ] Verify PostgreSQL connection on dev server
- [ ] Document secret rotation procedures
- [ ] Consider adding similar validation for UAT/production environments

## Notes

- **SQLite Fallback:** While SQLite fallback is provided for flexibility, PostgreSQL is strongly recommended for environment parity
- **Empty vs Missing:** The fix handles both empty strings and missing environment variables correctly
- **Backward Compatible:** Changes are backward compatible with existing deployments
- **Logging:** Enhanced logging helps troubleshoot configuration issues in all environments
