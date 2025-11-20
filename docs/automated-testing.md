# Automated Testing Guide

## Overview

The ProjectMeats repository now includes a comprehensive automated testing workflow that runs on every pull request and can be manually triggered. This ensures code quality and prevents regressions before merging changes.

## Workflow: `40-automated-tests.yml`

### Automatic Triggers

The test workflow automatically runs when:
- A pull request is opened
- New commits are pushed to an open PR (synchronized)
- A PR is reopened
- A draft PR is marked as ready for review

### Manual Triggers

You can manually trigger the workflow from the GitHub Actions tab:

1. Go to **Actions** → **Automated Tests**
2. Click **Run workflow**
3. Choose the branch to test
4. Optionally skip frontend or backend tests using the checkboxes
5. Click **Run workflow**

## What Gets Tested

### Frontend Tests (`test-frontend` job)

- **Framework**: Jest with React Testing Library
- **Node Version**: 18.x
- **Tests Run**: All tests in `frontend/src` directory
- **Coverage**: Generates code coverage report
- **Type Checking**: Validates TypeScript types with `tsc`

**Commands executed**:
```bash
npm ci                    # Install dependencies
npm run test:ci          # Run tests with coverage
npm run type-check       # TypeScript validation
```

### Backend Tests (`test-backend` job)

- **Framework**: Django Test Suite
- **Python Version**: 3.12
- **Database**: PostgreSQL 15 (via service container)
- **Tests Run**: All tests in `backend/apps/` directory
- **Validation**: Migration validation with custom script
- **Code Quality**: Linting with flake8 and black (non-blocking)

**Commands executed**:
```bash
python manage.py check                    # Django system check
python manage.py migrate --noinput       # Apply migrations
.github/scripts/validate-migrations.sh   # Custom validation
python manage.py test apps/ --verbosity=2 # Run tests
flake8 . --exclude=migrations            # Linting
black --check . --exclude=migrations     # Code formatting check
```

## Test Results

### PR Comments

The workflow automatically posts comments to the pull request with:
- ✅/❌ Status indicators for each test suite
- Code coverage percentages (frontend)
- Links to detailed workflow logs
- Summary table of all test results

### Coverage Reports

Frontend coverage reports are uploaded as artifacts and retained for 7 days. You can download them from the workflow run page.

## Configuration

### Environment Variables (Backend Tests)

The backend tests run with the following environment:
```yaml
DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
SECRET_KEY: test-secret-key-for-testing-only
DEBUG: 'True'
ALLOWED_HOSTS: localhost,127.0.0.1
CI: 'true'
```

### Concurrency Control

To save resources and provide faster feedback:
- When you push new commits to a PR, any in-progress test runs are automatically cancelled
- Only the latest commit's tests will run

## Integration with Review Process

### Workflow: `33-planner-review-and-test`

When a PR is marked as "ready for review":
1. Automatically triggers the `40-automated-tests.yml` workflow
2. Adds the PR to the project board for tracking
3. Posts a notification comment on the PR

This ensures that all PRs ready for review have up-to-date test results.

## Troubleshooting

### Tests Failing Locally but Passing in CI

- Check Node.js version (should be 18.x)
- Check Python version (should be 3.12)
- Ensure PostgreSQL is running locally
- Review environment variables

### Tests Passing Locally but Failing in CI

- Clear `node_modules` and reinstall: `npm ci`
- Clear pip cache: `pip cache purge`
- Check for environment-specific code
- Review the workflow logs for detailed error messages

### Workflow Not Triggering

- Ensure the PR is not in draft mode
- Check that the workflow files exist in the target branch
- Verify GitHub Actions are enabled for the repository

## Skip Tests on Manual Runs

When manually triggering the workflow, you can skip specific test suites:
- **Skip Frontend Tests**: Check this option to only run backend tests
- **Skip Backend Tests**: Check this option to only run frontend tests

This is useful for:
- Testing specific changes that only affect one part of the stack
- Debugging test failures in isolation
- Saving workflow minutes

## Best Practices

1. **Keep Tests Fast**: Aim for test suites that complete in under 5 minutes
2. **Write Meaningful Tests**: Focus on testing behavior, not implementation details
3. **Maintain Coverage**: Strive to maintain or improve code coverage with each PR
4. **Fix Failing Tests Immediately**: Don't merge PRs with failing tests
5. **Review Test Results**: Always review the test summary before requesting review

## Related Documentation

- [GitHub Workflows README](../.github/workflows/README.md)
- [Frontend Testing Guide](../frontend/README.md)
- [Backend Testing Guide](../backend/docs/testing.md)
- [Contributing Guide](../CONTRIBUTING.md)

## Support

If you encounter issues with the automated testing workflow:
1. Check the workflow logs for detailed error messages
2. Review this documentation
3. Open an issue with the `ci/cd` label
4. Tag `@devops-vst` for CI/CD related questions
