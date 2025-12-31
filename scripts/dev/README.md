# Development Scripts

This directory contains scripts for local development environment setup and management.

## Purpose

These scripts help developers:
- Set up local development environments
- Start and stop development servers
- Seed test data
- Configure environment variables

## Scripts

### Environment Setup
- `setup.py` - Initial project setup
- `setup_env.py` - Environment variable configuration
- `seed_data.py` - Seed database with test data

### Development Server Management
- `start_dev.sh` - Start local development servers (frontend + backend)
- `stop_dev.sh` - Stop local development servers

## Quick Start

```bash
# First time setup
python scripts/dev/setup_env.py

# Start development servers
./scripts/dev/start_dev.sh

# Seed test data (optional)
python scripts/dev/seed_data.py

# Stop servers when done
./scripts/dev/stop_dev.sh
```

## Notes

- These scripts assume you have Docker and Docker Compose installed
- Review `setup_env.py` to configure your local environment variables
- The `seed_data.py` script is useful for populating a fresh database with sample data

For more details, see the main [Local Development Guide](/docs/LOCAL_DEVELOPMENT.md).
