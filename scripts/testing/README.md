# Testing & Simulation Scripts

This directory contains scripts for testing, simulation, and demonstration purposes.

## Purpose

These scripts are used for:
- Testing deployment procedures
- Simulating production scenarios
- Health checks and monitoring
- Demonstrating features
- Notification testing

## Scripts

### Testing & Simulation
- `simulate_deployment.py` - Simulate deployment scenarios for testing
- `demo_manifest_extraction.py` - Demonstrate environment manifest extraction

### Health & Monitoring
- `health_check.py` - Perform health checks on running services

### Notifications
- `TEST_NOTIFY.sh` - Test notification systems (Slack, email, etc.)

## Usage

These scripts are primarily used during development and testing phases:

```bash
# Test deployment simulation
python scripts/testing/simulate_deployment.py

# Run health checks
python scripts/testing/health_check.py

# Test notifications
./scripts/testing/TEST_NOTIFY.sh
```

## Notes

- These scripts are safe to run in any environment (dev, UAT, or production)
- They do not modify production data
- Some scripts may require environment variables to be set
- Review each script's documentation for specific requirements

For integration tests that interact with the Django application, see `backend/tests/integration/`.
