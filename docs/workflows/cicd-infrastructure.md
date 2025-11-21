# ProjectMeats3 Deployment Documentation

> **⚠️ ARCHIVED DOCUMENTATION**
> 
> This documentation describes a Docker and Terraform based deployment approach that is no longer actively used. The Docker and Terraform files referenced in this document have been moved to the `archived/` directory.
> 
> See `archived/README.md` for the location of archived files.

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

              ┌───────────────────────────────────────────────┐
              │                 GitHub Repository             │
              │  ├── development branch → Dev Environment     │
              │  ├── uat branch → UAT Environment             │
              │  └── main branch → Production Environment     │
              └───────────────────────────────────────────────┘
                                   │
                                   ▼
            ┌─────────────────────────────────────────────┐
            │        DigitalOcean Container Registry      │
            │   Stores built Docker images per branch     │
            │   (backend:dev, frontend:dev, uat, prod)    │
            └─────────────────────────────────────────────┘
                                   │
                                   ▼
     ┌─────────────────────────────────────────────┐   ┌─────────────────────────────────────────────┐
     │           DEV Droplets (Frontend/Backend)   │   │          UAT Droplets (Frontend/Backend)    │
     │   docker run pm-backend:dev-latest          │   │   docker run pm-backend:uat-latest          │
     │   docker run pm-frontend:dev-latest         │   │   docker run pm-frontend:uat-latest         │
     └─────────────────────────────────────────────┘   └─────────────────────────────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────────────┐
                        │   PROD Droplets (Live App)   │
                        │   pm-backend:prod-latest     │
                        │   pm-frontend:prod-latest    │
                        └──────────────────────────────┘


```
   
```

### Workflow Overview

The CI/CD pipeline (`deploy.yml`) automates building, testing, and deploying containerized services (**backend** and **frontend**) across **Development**, **UAT**, and **Production** environments.
It is triggered by branch merges or manual executions and uses **DigitalOcean Container Registry (DOCR)** for image management, while all environment configurations and secrets are managed in **GitHub Environments**.

* **Triggers**:

  * Push to `development` → Deploys to **DEV**
  * Push to `uat` → Deploys to **UAT**
  * Push to `main` → Deploys to **PROD**
  * Manual (`workflow_dispatch`) trigger supported for redeployment or rollback operations.

* **Permissions**:

  * `contents: read`
  * `packages: write`
  * `id-token: write` (for authentication with DOCR)

* **Jobs**:

  * **build_and_push_images**: Builds Docker images for backend and frontend, tags, and pushes them to DOCR.
  * **deploy_dev**: Deploys the new images automatically to the DEV environment when code is pushed to `development`.
  * **deploy_uat**: Deploys to the UAT environment after merging `development` into `uat`.
  * **deploy_prod**: Deploys to the production environment after approval and merging `uat` into `main`.

---

### Detailed Job Flow

1. **build_and_push_images**:

   * Checkout repository source code.
   * Setup both **Node.js** (for frontend) and **Python** (for backend) environments.
   * Install project dependencies.
   * Run tests for both backend and frontend.
   * Build Docker images for both services.
   * Tag images with `<environment>-<commit-sha>` and `<environment>-latest`.
   * Push tagged images to **DigitalOcean Container Registry**:

     * `registry.digitalocean.com/<registry>/backend:<tag>`
     * `registry.digitalocean.com/<registry>/frontend:<tag>`
   * Export image tags as reusable variables for downstream jobs.

2. **deploy_dev**:

   * Automatically triggered when the pipeline runs for the `development` branch.
   * Establishes SSH connection to the DEV droplet using secure GitHub secrets.
   * Writes environment variables to:

     * `/opt/pm/backend/.env`
     * `/opt/pm/frontend/env-config.js`
   * Pulls the latest images from DOCR.
   * Stops and removes previous container versions.
   * Runs new containers:

     * `pm-backend` exposed on port `8000`
     * `pm-frontend` served on port `80` (Nginx)
   * Runs database migrations and collects static assets.
   * Performs API and UI health checks.

3. **deploy_uat**:

   * Triggered after merging changes from `development` → `uat`.
   * Executes the same deployment sequence as **deploy_dev**, but with **UAT environment secrets**.
   * Pulls updated image tags (`uat-<sha>` and `uat-latest`) from DOCR.
   * Validates deployment through health checks:

     * Backend: `/api/v1/health/`
     * Frontend: root URL (index.html response).
   * Marks UAT deployment as complete after successful verification.

4. **deploy_prod**:

   * Triggered after merging **UAT** into **main**.
   * Requires **manual approval** through GitHub Environment Protection Rules before deployment.
   * Pulls production images (`prod-<sha>` and `prod-latest`) from DOCR.
   * Applies production-specific environment variables from GitHub Secrets.
   * Runs new containers using production configurations:

     * Gunicorn for Django backend.
     * Nginx for React frontend.
   * Executes health checks on both backend API and frontend domain.
   * Publishes deployment status summary to GitHub Actions logs.

---



### Diagram
```
Push → development branch
│
├── Build & Push (backend + frontend images)
│
├── Test (unit + migration checks)
│
└── Deploy to DEV droplets (auto)
      │
      ├── UAT merge → auto deploy to UAT
      └── UAT approved → merge to main → deploy to PROD

```

## 3. Deployment Process

### Deployment Process

The deployment process is managed through **GitHub Actions** and executed automatically across all environments — **Development**, **UAT**, and **Production** — using **DigitalOcean Container Registry (DOCR)** and SSH-based Docker deployment.

---

### Deployment Sequence

1. **Build images** → GitHub Actions builds backend and frontend Docker images and pushes them to **DOCR**.
2. **Establish SSH connection** → The pipeline connects to the target droplet using credentials stored in GitHub Secrets.
3. **Inject environment variables** → Writes `.env` files for backend and frontend inside `/opt/pm/<service>/`.
4. **Pull new images** → The pipeline pulls the latest tagged images (`dev-latest`, `uat-latest`, `prod-latest`) from DOCR.
5. **Recreate containers** → Existing containers are stopped and replaced with updated ones.
6. **Validate health checks** → Confirms successful deployment through endpoint checks for both backend and frontend.

---

### Health Verification

* **Backend Health Check:**

  ```bash
  curl -I http://127.0.0.1:8000/api/v1/health/
  ```

* **Frontend Health Check:**

  ```bash
  curl -I http://127.0.0.1/
  ```

If any check fails, the pipeline halts and displays container logs for debugging.

---

### Rollback Procedure

#### Manual Rollback Steps

1. **Access the droplet:**

   ```bash
   ssh deploy@<server-ip>
   ```

2. **Pull the previous stable image:**

   ```bash
   docker pull registry.digitalocean.com/<registry>/<service>:uat-abc1234
   ```

3. **Replace the running container:**

   ```bash
   docker rm -f pm-backend
   docker run -d --name pm-backend --env-file /opt/pm/backend/.env \
   -p 8000:8000 registry.digitalocean.com/<registry>/backend:uat-abc1234
   ```

4. **Validate using health checks:**

   ```bash
   curl -I http://127.0.0.1:8000/api/v1/health/
   ```

> **Note:** Database migrations are not automatically reverted. Manual schema rollback may be required if changes were applied.

---

### Troubleshooting

#### Frontend Using `localhost` API

If the frontend continues calling `http://localhost:8000` after deployment:

* Verify container environment variables:

  ```bash
  docker exec -it pm-frontend printenv | grep REACT_APP
  ```
* If variables are correct, the issue is due to **React build-time variable injection**.
  Ensure `REACT_APP_API_BASE_URL` exists **during the build process**, or use a dynamic runtime configuration file like `env-config.js`.

---

#### Backend Not Connecting to Database

* Confirm the active database environment variables:

  ```bash
  docker exec -it pm-backend /bin/sh -c 'printenv | grep DATABASE'
  ```
* Ensure the value points to **PostgreSQL**, not SQLite.

---

#### Health Check Failures

* View container logs:

  ```bash
  docker logs pm-backend --tail 100
  docker logs pm-frontend --tail 100
  ```
* Restart containers if required:

  ```bash
  docker restart pm-backend pm-frontend
  ```

---

### Maintenance and Monitoring

| **Task**                   | **Frequency** | **Command / Action**            |
| -------------------------- | ------------- | ------------------------------- |
| Prune unused Docker images | Weekly        | `docker image prune -af`        |
| Check disk usage           | Weekly        | `df -h`                         |
| Rotate secrets             | Monthly       | Review GitHub Environments      |
| Verify database backups    | Monthly       | Validate DigitalOcean snapshots |

---

### Benefits Summary

| **Aspect**             | **Before**                  | **After**                                          |
| ---------------------- | --------------------------- | -------------------------------------------------- |
| **Deployment**         | Manual SSH commands         | Fully automated via GitHub Actions                 |
| **Configuration**      | Hardcoded on droplet        | Managed through GitHub Secrets                     |
| **Rollback**           | Manual file replacement     | Tag-based rollback through DOCR                    |
| **Infrastructure**     | Non-containerized           | Fully Dockerized setup                             |
| **Environment Parity** | Inconsistent between stages | Identical configurations across DEV, UAT, and PROD |
| **Reliability**        | High chance of drift        | Reproducible and standardized builds               |

---

**Maintained By:** DevOps Engineering — *Vital Steer LLC*
**Last Updated:** November 2025

---
