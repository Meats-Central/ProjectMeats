# Integration Tests

This directory contains integration tests that validate the complete application stack.

## Purpose

These tests verify:
- End-to-end deployment procedures
- Guest mode functionality
- Invitation system
- Security hardening measures
- Cross-component integration

## Test Scripts

### Deployment Testing
- `test_deployment.py` - Test deployment procedures and validation
- `test_deployment.sh` - Shell-based deployment testing

### Feature Testing
- `test_guest_mode.py` - Test guest user access and permissions
- `test_invitations.py` - Test invitation system workflows

### Security Testing
- `test_hardening.sh` - Verify security hardening measures

## Running Tests

These scripts can be run individually or as part of the test suite:

```bash
# Run specific integration test
python backend/tests/integration/test_guest_mode.py

# Run all integration tests
python manage.py test backend/tests/integration/

# Run deployment validation
./backend/tests/integration/test_deployment.sh
```

## Requirements

- Tests may require:
  - Django environment configured
  - Database access
  - Test user credentials
  - Environment variables set

## Notes

- These are **integration tests**, not unit tests - they test multiple components together
- Some tests may take longer to run than unit tests
- Tests should be idempotent (safe to run multiple times)
- Test data is cleaned up after each test run

For unit tests, see `backend/apps/*/tests/` directories.
