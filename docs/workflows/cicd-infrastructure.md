# ProjectMeats3 Deployment Documentation

## Overview
ProjectMeats3 is a full-stack application designed for managing a meat brokerage business, featuring a Django backend with REST APIs and OpenAI integration for AI-assisted features (e.g., chat, document processing), and a React frontend for user interaction. The application is deployed across three environments: DEV, UAT, and PROD, using Digital Ocean infrastructure managed by Terraform. The CI/CD pipeline, built with GitHub Actions, automates building, testing, and deployment of Docker images to GitHub Container Registry (GHCR.io). Deployment uses SSH to remote droplets, where Docker Compose orchestrates services with Traefik for routing and Let’s Encrypt for TLS.

This documentation covers:
- Server architecture and setup.
- CI/CD workflow details.
- Deployment process.

(Note: Rollback strategies are excluded from this documentation as per instructions.)

## 1. Server Architecture and Setup

### Infrastructure Overview
The infrastructure is provisioned on Digital Ocean using Terraform, consisting of:
- **Three Droplets (VMs)**:
  - **DEV**: s-2vCPU-2GB (low-spec for cost savings), used for rapid iteration and testing.
  - **UAT**: s-2vCPU-2GB, mirrors PROD for staging and validation.
  - **PROD**: s-4vCPU-8GB (higher-spec for performance), hosts the live application.
  - OS: Ubuntu 22.04 LTS.
  - Region: NYC3 (configurable in `variables.tf`).
  - Networking: Public IPs with DNS records (`dev.meatscentral.com`, `uat.meatscentral.com`, `meatscentral.com`).
- **Managed Databases**:
  - PostgreSQL 15 for UAT and PROD (1vCPU/1GB RAM, 10 GiB SSD, 22 connections).
  - DEV uses local SQLite (`db.sqlite3`) for simplicity.
- **Security**:
  - SSH key-based access via `deploy` user (created via cloud-init in `user_data`).
  - UFW firewall: Allows ports 22 (SSH), 80 (HTTP), 443 (HTTPS).
  - DO firewall: Inbound rules for SSH and HTTP/HTTPS.
- **Application Components**:
  - **Backend**: Django with Gunicorn, exposed on port 8000.
  - **Frontend**: React SPA, served on port 3000.
  - **Routing**: Traefik for reverse proxy, handling `/api/` to backend and `/` to frontend, with auto-TLS via Let’s Encrypt.
  - **Storage**: Volumes for static files (`static_data` in UAT/PROD), PostgreSQL data (`pg_data` in DEV).
  - **Directories**: `/opt/projectmeats/` for env files, compose files, and logs (created with `deploy` ownership).

### Setup Process
1. **Terraform Configuration**:
   - Files: `main.tf` (resources), `variables.tf` (variables), `provider.tf` (provider), `outputs.tf` (outputs).
   - Key Resources:
     - `digitalocean_droplet.projectmeats_dev/uat/prod`: Creates droplets with `user_data` for setup (deploy user, Docker, Compose, firewall).
     - `digitalocean_database_cluster.projectmeats_uat_db/prod_db`: Creates PostgreSQL clusters.
     - `digitalocean_ssh_key.deploy_key`: Uploads SSH public key.
     - `digitalocean_record.dev_dns/uat_dns/prod_dns`: Sets A records.
   - Run:
     ```bash
     cd projectmeats-infra
     terraform init
     terraform apply
     ```
   - Outputs: Droplet IPs, database connection strings.

2. **Droplet Configuration (via `user_data`)**:
   - Creates `deploy` user with sudo privileges and SSH key access.
   - Installs Docker, Docker Compose, Python, Git.
   - Enables UFW with SSH/HTTP/HTTPS ports.
   - Creates `/opt/projectmeats/env` with `deploy` ownership.

3. **Manual Initial Setup (if Needed)**:
   - SSH to each droplet: `ssh deploy@<ip>`.
   - Clone repo: `git clone https://github.com/Meats-Central/ProjectMeats3.git /opt/projectmeats`.
   - Ensure `db.sqlite3` for DEV: `touch /opt/projectmeats/db.sqlite3; chown deploy:deploy /opt/projectmeats/db.sqlite3`.

### ASCII Architecture Diagram
```
    +--------------+           +--------------+     +--------------+
    | DEV Droplet  |           | UAT Droplet  |     | PROD Droplet |
    | 1vCPU/1GB    |           | 2vCPU/2GB    |     | 4vCPU/8GB    |
    | SQLite       |           | PostgreSQL   |     | PostgreSQL   |
    +--------------+           +--------------+     +--------------+
    | Traefik      |           | Traefik      |     | Traefik      |
    | Django API   |           | Django API   |     | Django API   |
    | React SPA    |           | React SPA    |     | React SPA    |
    +--------------+           +--------------+     +--------------+
           |                           |                   |
 DNS: dev.meatscentral.com | uat.meatscentral.com | prod.meatscentral.com
```

## 2. CI/CD Workflow Details

### Workflow Overview
The CI/CD pipeline (`ci-cd.yml`) automates building, testing, and deploying the application to DEV, UAT, and PROD. Triggered by pushes to `dev`, `main_rep`, or `main`, or manual dispatch, it uses GitHub Container Registry (GHCR.io) for image storage.

- **Triggers**:
  - Push to `dev`, `main_rep`, or `main`.
  - Manual (`workflow_dispatch`).

- **Permissions**:
  - `contents: read`, `packages: write` (for GHCR.io).

- **Jobs**:
  - **build_test_package**: Builds/tests backend (Django) and frontend (React), pushes images to GHCR.io.
  - **deploy_dev**: Deploys to DEV if on `dev` branch.
  - **promote_and_deploy_uat**: Deploys to UAT after DEV.
  - **deploy_prod**: Deploys to PROD after UAT, with manual approval.

### Detailed Job Flow
1. **build_test_package**:
   - Checkout code.
   - Setup Python/Node, install dependencies, run tests.
   - Build and push images to GHCR.io (e.g., `ghcr.io/meats-central/projectmeats-backend:<sha>`, `ghcr.io/meats-central/projectmeats-frontend:<sha>`).
   - Outputs image tags for deployments.

2. **deploy_dev**:
   - Render `dev.env` and `image.env`.
   - Upload env/compose files via SSH.
   - Deploy using `deploy_via_compose.sh` (login, pull, migrate, up -d, healthcheck).
   - Validate deployment.

3. **promote_and_deploy_uat**:
   - Similar to DEV, but for UAT.

4. **deploy_prod**:
   - Similar to UAT, but requires approval.

### Diagram
```
Push to dev/main_rep/main
|
v
build_test_package (Build/Test/Push Images)
|
v
deploy_dev (Deploy DEV, Validate)
|
v
promote_and_deploy_uat (Deploy UAT, Validate)
|
v
deploy_prod (Manual Approval, Deploy PROD, Validate)
```

## 3. Deployment Process

### Deployment Flow
- **Trigger**: Push to `dev`, `main_rep`, or `main` builds images and deploys to DEV/UAT automatically; PROD requires approval.
- **Image Management**: Images tagged with commit SHA and `latest`, pushed to GHCR.io.
- **Remote Deployment**:
  - SSH to droplet using `deploy` user.
  - Pull images, run migrations (all envs), collectstatic (UAT/PROD).
  - Start services with `docker compose up -d` (Traefik, API, Web).
  - Health/smoke checks verify deployment.

### Step-by-Step Deployment
1. **Build Images**: `build_test_package` builds backend/frontend, pushes to GHCR.io.
2. **Env Rendering**: Each job renders environment-specific `.env` files.
3. **Upload Files**: Env and compose files uploaded to `/opt/projectmeats`.
4. **Execute Script**: `deploy_via_compose.sh` handles:
   - GHCR.io login with `GITHUB_TOKEN`.
   - Pull images (`ghcr.io/meats-central/projectmeats-backend:<sha>`, `ghcr.io/meats-central/projectmeats-frontend:<sha>`).
   - Migrations (all envs) and collectstatic (UAT/PROD).
   - `docker compose up -d`.
   - Health/smoke checks (local `http://127.0.0.1:8000/healthz`, public `https://${APP_DOMAIN}/healthz`).
5. **Cleanup**: `remote-docker-cleanup` prunes old images, keeping 2 latest.

### Troubleshooting
- Check GitHub Actions logs for errors (e.g., pull failures, migration issues).
- SSH to droplets (`ssh deploy@<ip>`) for:
  - `docker ps` (running containers).
  - `docker logs <container>` (service logs).
  - `docker images` (available images).
- Verify DNS resolution: `dig dev.meatscentral.com`.

---