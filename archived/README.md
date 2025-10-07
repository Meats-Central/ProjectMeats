# Archived Files

This directory contains Docker and Terraform related files that are no longer actively used in the project.

## Contents

### docker/
Contains archived Docker-related files:
- `Dockerfile.backend` - Backend Docker image definition
- `Dockerfile.frontend` - Frontend Docker image definition
- `docker-compose.dev.yml` - Development environment compose file (root)
- `docker-compose.prod.yml` - Production environment compose file (root)
- `docker-compose.uat.yml` - UAT environment compose file (root)
- `docker-compose.dev.config.yml` - Development environment compose file (from config/deployment)
- `docker-compose.prod.config.yml` - Production environment compose file (from config/deployment)
- `docker-compose.staging.config.yml` - Staging environment compose file (from config/deployment)

### deployment-scripts/
Contains archived deployment scripts:
- `deploy_via_compose.sh` - Docker Compose deployment script
- `_ssh.sh` - SSH helper script

### terraform/
Contains archived Terraform infrastructure-as-code files:
- `main.tf` - Main Terraform configuration
- `outputs.tf` - Terraform outputs
- `providers.tf` - Terraform provider configuration
- `variables.tf` - Terraform variables
- `terraform.gitignore` - Terraform-specific gitignore
- `.terraform.lock.hcl` - Terraform dependency lock file

## Note

These files have been archived as the project has moved away from Docker-based and Terraform-based deployment strategies. They are kept for historical reference and potential future use.
