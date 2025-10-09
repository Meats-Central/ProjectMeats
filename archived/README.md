# Archived Files

This directory contains files that are no longer actively used in the project but are kept for historical reference.

## Contents

### docs/
Contains archived documentation files:
- **Legacy deployment documentation** (from docs/legacy/):
  - `DEPLOYMENT_GUIDE.md` - Original comprehensive deployment guide (replaced by docs/DEPLOYMENT_GUIDE.md)
  - `QUICK_SETUP.md` - Original quick setup guide (consolidated into main guide)
  - `production_checklist.md` - Original production checklist (integrated into DEPLOYMENT_GUIDE.md)
  - `README.md` - Explains legacy status
- **Outdated deployment guide**:
  - `USER_DEPLOYMENT_GUIDE.md` - DigitalOcean App Platform deployment guide (project uses SSH-based deployment)

### code/
Contains archived code and configuration files:
- **Configuration files** (moved from root):
  - `app.yaml` - Google App Platform config (not used for DigitalOcean deployment)
  - `pyproject.toml` - Python project config (project uses requirements.txt)
  - `.python-version` - Python version file (use pyenv or Dockerfile for version control)
- **Deployment files**:
  - `deploy/` - Legacy deployment scripts (superseded by simulate_deployment.py)
  - `ci-cd.yml.sajid-workflow-backup` - Backup workflow file

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

## Rationale

### Documentation Archive (docs/)
- **Legacy deployment docs**: Replaced by streamlined docs/DEPLOYMENT_GUIDE.md

### Code Archive (code/)
- **app.yaml**: DigitalOcean App Platform spec file (project uses SSH-based deployment instead)
- **.python-version**: Version control handled by pyenv or Dockerfile
- **deploy/**: Superseded by SSH-based deployment in workflows
- **Workflow backups**: Development artifacts, not needed in active workflows

### Infrastructure Archive (docker/, deployment-scripts/, terraform/)
- Project has moved away from Docker-based and Terraform-based deployment strategies
- Files kept for historical reference and potential future use

## Current Documentation

For active documentation, see:
- **Main Guide**: [USER_DEPLOYMENT_GUIDE.md](../USER_DEPLOYMENT_GUIDE.md)
- **Documentation Hub**: [docs/README.md](../docs/README.md)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)
