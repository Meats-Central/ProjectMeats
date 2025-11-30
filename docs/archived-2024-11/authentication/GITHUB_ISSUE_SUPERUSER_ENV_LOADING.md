# Fix Superuser Creation/Sync Failures in UAT/Prod During Tests Despite Set Secrets

## Issue Type
🐛 Bug Fix

## Priority
🔴 High - Affects CI/CD reliability and multi-tenancy testing

## Description

The `setup_superuser` management command fails during test execution in CI/CD pipelines with errors like:

```
❌ Superuser email is required in staging environment!
```

This occurs even when secrets are properly configured in GitHub environments (uat2-backend/prod2-backend), because the command doesn't handle test contexts gracefully.

### Error Examples

From GitHub Actions run [18454830855](https://github.com/Meats-Central/ProjectMeats/actions/runs/18454830855):

```
ERROR: ❌ Superuser email is required in staging environment!
ValueError: Superuser email environment variable must be set in staging environment
```

## Root Cause

The `setup_superuser.py` command has inconsistent environment variable loading for test contexts:

1. **Strict validation in all environments**: The command raises `ValueError` when env vars are missing, even in test contexts
2. **No test context detection**: Doesn't distinguish between actual production deployments and test runs
3. **Missing graceful fallbacks**: No default values for test scenarios
4. **Inadequate logging**: Doesn't clearly show which vars are loaded vs. missing

### Code Issues

```python
# Current problematic code in setup_superuser.py
if not email:
    error_msg = f'❌ Superuser email is required in {django_env} environment!'
    logger.error(error_msg)
    self.stdout.write(self.style.ERROR(error_msg))
    raise ValueError(  # ❌ Raises even in tests!
        f'Superuser email environment variable must be set in {django_env} environment'
    )
```

## Impact on Multi-Tenancy Reliability

- **CI/CD Pipeline Failures**: Tests fail when setup_superuser is called during test setup
- **Inconsistent Behavior**: Works in production but fails in tests, making multi-tenancy testing difficult
- **False Positives**: Test failures don't indicate actual deployment issues
- **Developer Friction**: Developers can't easily run tests locally without setting all production secrets

## Proposed Solution

### 1. Update `backend/apps/core/management/commands/setup_superuser.py`

**Add test context detection:**
```python
# Detect test context
is_test_context = 'test' in django_env.lower() or os.getenv('DJANGO_SETTINGS_MODULE', '').endswith('test')
```

**Wrap `os.environ.get()` with graceful defaults for tests:**
```python
# Apply defaults for missing values in test context
if is_test_context:
    if not username:
        username = 'testadmin'
        logger.warning(f'Test context: using default username={username}')
    if not email:
        email = f'{username}@example.com'
        logger.warning(f'Test context: using default email={email}')
    if not password:
        password = 'testpass123'
        logger.warning(f'Test context: using default password (hidden)')
```

**Log warnings instead of errors for non-prod:**
```python
if not email:
    error_msg = f'❌ Superuser email is required in {django_env} environment!'
    if is_production_env and not is_test_context:
        logger.error(error_msg)
        self.stdout.write(self.style.ERROR(error_msg))
        raise ValueError(...)
    else:
        logger.warning(error_msg + ' (non-production, continuing with defaults)')
        email = f'{username}@example.com'
```

**Add verbose logging for loaded vars:**
```python
logger.info(f'Staging/UAT mode: loaded STAGING_SUPERUSER_EMAIL: {"set" if email else "missing"}')
```

**Handle username=None cases:**
```python
if is_test_context and not username:
    username = 'testadmin'
```

### 2. Update `.github/workflows/unified-deployment.yml`

Export test-specific env vars in test job:

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

### 3. Create Tests with Mocks

Create `backend/apps/core/tests/test_setup_superuser.py`:

```python
from unittest import mock
from django.core.management import call_command
from django.test import TestCase

class SetupSuperuserCommandTests(TestCase):
    def test_command_runs_with_no_env_vars_in_test_context(self):
        """Test that command uses defaults when no env vars set in test context."""
        with mock.patch.dict('os.environ', {'DJANGO_ENV': 'test'}, clear=True):
            with mock.patch('os.getenv') as mock_getenv:
                def getenv_side_effect(key, default=None):
                    if key == 'DJANGO_ENV':
                        return 'test'
                    return default
                
                mock_getenv.side_effect = getenv_side_effect
                call_command('setup_superuser')  # Should not raise error
```

### 4. Update Documentation

Add section to `docs/DEPLOYMENT_GUIDE.md`:

```markdown
## Secret Validation in CI/CD and Tests

### Test Context Detection
The command automatically detects test contexts and applies appropriate behavior...

### GitHub Actions Configuration
The unified deployment workflow includes test-specific environment variables...

### Mocking Secrets in Tests
When writing tests that use the setup_superuser command, use @patch...
```

## Acceptance Criteria

- [ ] `setup_superuser.py` detects test context and uses safe defaults
- [ ] Command logs warnings instead of errors for missing vars in non-prod
- [ ] Verbose logging shows which vars are "set" or "missing"
- [ ] Username=None cases handled gracefully with defaults or custom exceptions
- [ ] Workflow exports test-specific env vars (STAGING_SUPERUSER_*, PRODUCTION_SUPERUSER_*)
- [ ] Tests in `test_setup_superuser.py` use `@patch('os.environ.get')` to simulate missing vars
- [ ] Tests assert no failures when vars are missing in test context
- [ ] Documentation includes secret validation section for CI/tests
- [ ] No duplicate command logic found in other apps
- [ ] `python manage.py test apps/` passes locally
- [ ] Full workflow run shows no 'required' errors in logs

## Testing Checklist

- [ ] Run `python manage.py test apps.core.tests.test_setup_superuser` - all tests pass
- [ ] Run `python manage.py test apps/` - all tests pass
- [ ] Trigger GitHub Actions workflow - test job succeeds
- [ ] Check deployment logs - no "required in staging environment" errors
- [ ] Verify UAT deployment - superuser created successfully
- [ ] Verify production deployment - strict validation still works

## References

- **Django Environment Variables**: https://docs.djangoproject.com/en/4.2/topics/settings/#envvar-DJANGO_SETTINGS_MODULE
- **12-Factor App Config**: https://12factor.net/config
- **OWASP Secrets Management**: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- **GitHub Actions Run 18454830855**: https://github.com/Meats-Central/ProjectMeats/actions/runs/18454830855

## Related Files

- `backend/apps/core/management/commands/setup_superuser.py`
- `backend/apps/core/tests/test_setup_superuser.py` (new)
- `.github/workflows/unified-deployment.yml`
- `docs/DEPLOYMENT_GUIDE.md`

## Labels

- `bug`
- `ci/cd`
- `testing`
- `multi-tenancy`
- `priority:high`
