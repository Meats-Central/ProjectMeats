# ProjectMeats — Deployment Modernization & Unified CI/CD

## Overview

ProjectMeats has moved from manual VM-based deployments to a fully containerized, automated CI/CD process on DigitalOcean. Previously, code and configs lived directly on droplets with secrets hardcoded on hosts. Now, Docker images are built by GitHub Actions, pushed to DigitalOcean Container Registry (DOCR), and deployed per environment (Development, UAT, Production) onto dedicated frontend and backend droplets. All secrets are managed centrally via GitHub Environments/Secrets.


---

## 1) Modernization Summary

### Before (Legacy VM installs)

* App ran directly on DigitalOcean droplets without Docker.
* Config and dependencies installed manually on hosts.
* Secrets (DB URL, API keys) hardcoded on VMs.
* Manual SSH deploys and service restarts, frequent drift and risk.

### After (Containerized + Automated)

* **Dockerized** backend (Django) and frontend (React).
* **Images** built in GitHub Actions, **pushed to DOCR**.
* **Per-environment droplets**: separate frontend and backend droplets for Dev, UAT, and Prod.
* **GitHub Environments/Secrets** hold all sensitive config.
* **Automated deployments** on merges to the target branches, with health checks and clear rollbacks.

---

## 2) Workflow Architecture

**Branch Strategy → Environments**

* `development` → **Development** deploy
* `uat` → **UAT (staging)** deploy
* `main` → **Production** deploy

### Architecture Diagram
```
GitHub Repository (Push Trigger)
    |
    ├─── development branch
    |    └─── Deploy to Development
    |    
    ├─── uat branch
    |    └─── Deploy to uat staging
    |
    └─── main branch
         └─── Deploy to Production

Each Environment:
┌─────────────────────────────────┐
│  DigitalOcean Droplet           │
│  ┌───────────────────────────┐  │
│  │  Nginx (Reverse Proxy)    │  │
│  └───────────┬───────────────┘  │
│              │                   │
│     ┌────────┴────────┐         │
│     │                 │         │
│  ┌──▼────┐      ┌────▼──────┐  │
│  │Backend│      │ Frontend  │  │
│  │Django │      │  React    │  │
│  │+Gunic.│      │   SPA     │  │
│  │Super. │      │  (build)  │  │
│  └───────┘      └───────────┘  │
│     │                           │
│  ┌──▼────┐                      │
│  │PostgreSQL                    │
│  │Database│                     │
│  └────────┘                     │
└─────────────────────────────────┘
```
### Job Flow
```
┌─────────────────────────┐
│  detect-changes         │ ← Detects backend/frontend changes
└───────────┬─────────────┘
            │
     ┌──────┴──────┐
     │             │
┌────▼────┐   ┌───▼─────┐
│test-    │   │test-    │ ← Run tests in parallel
│backend  │   │frontend │
└────┬────┘   └───┬─────┘
     │            │
     └──────┬─────┘
            │
  ┌─────────┴──────────┐
  │                    │
  │   development branch:
  │  ┌─────────────────────────┐
  │  │ deploy-backend-dev      │
  │  │ deploy-frontend-dev     │
  │  │                         │
  │  │                         │
  │  └─────────────────────────┘
  
```
1. Developer merges to `development`.
   GitHub Actions builds & pushes images, deploys to Dev frontend/backend droplets.
2. After validation, create PR to `uat`, merge → deploy to UAT droplets.
3. After UAT sign-off, create PR to `main`, merge → deploy to Prod droplets.

**Jobs (per applicable env):**

* **Build & Push**: Build Docker images, push to DOCR.
* **Test**: Frontend unit/types; Backend migrations/tests.
* **Deploy**: Pull image on droplet, run migrations (backend), swap containers, reload Nginx, health check.

---

## 3) Environment Layout

Each environment uses **two droplets**:

* **Backend Droplet** (Django + Gunicorn inside container, exposed on `:8000`)
* **Frontend Droplet** (Nginx static SPA container exposed on `:80` internally and proxied externally)

**Environment Table**

| Environment | Branch        | Droplets                        | Container Images (tags)                                        |
| ----------- | ------------- | ------------------------------- | -------------------------------------------------------------- |
| Dev         | `development` | `dev-backend`, `dev-frontend`   | `backend:dev-<sha>`, `backend:dev-latest`, `frontend:dev-*`    |
| UAT         | `uat`         | `uat-backend`, `uat-frontend`   | `backend:uat-<sha>`, `backend:uat-latest`, `frontend:uat-*`    |
| Prod        | `main`        | `prod-backend`, `prod-frontend` | `backend:prod-<sha>`, `backend:prod-latest`, `frontend:prod-*` |

## 4. Environment Configuration

### Required GitHub Secrets

#### Repository-Level Secrets (Shared)
- `GIT_TOKEN`: GitHub Personal Access Token for repository access
- `SSH_PASSWORD`: SSH password for staging server
- `DEV_SSH_PASSWORD`: SSH password for development server

### How to Add Secrets to Environments

**Repository-Level Secrets** (Settings → Secrets and variables → Actions → Repository secrets):
1. Click **New repository secret**
2. Enter secret name (e.g., `GIT_TOKEN`)
3. Enter secret value
4. Click **Add secret**

**Environment-Specific Secrets** (Settings → Environments → [Environment Name] → Environment secrets):
1. Click on the environment name (e.g., `dev-backend`)
2. Scroll to **Environment secrets** section
3. Click **Add secret**
4. Enter secret name and value
5. Click **Add secret**

#### Development Environment (`dev-backend` and `dev-frontend`)

**Repository Secrets (Shared across dev-backend and dev-frontend):**
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `DEV_HOST` | Development server IP/hostname | `192.168.1.100` or `dev.yourdomain.com` |
| `DEV_USER` | SSH username | `django` |
| `DEV_SSH_PASSWORD` | SSH password for development server | `your-secure-password` |

**Environment Secrets for `dev-backend`:**
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `DEV_API_URL` | Backend API URL | `https://dev-api.yourdomain.com` or `http://192.168.1.100` |

**Environment Secrets for `dev-frontend`:**
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `DEV_URL` | Frontend URL | `https://dev.yourdomain.com` |
| `REACT_APP_API_BASE_URL` | Backend API URL for frontend | `https://dev-api.yourdomain.com` |
| `REACT_APP_AI_ASSISTANT_ENABLED` | Enable AI features | `true` |
| `REACT_APP_ENABLE_DOCUMENT_UPLOAD` | Enable document uploads | `true` |
| `REACT_APP_ENABLE_CHAT_EXPORT` | Enable chat exports | `true` |
| `REACT_APP_MAX_FILE_SIZE` | Max upload size in bytes | `10485760` (10MB) |
| `REACT_APP_SUPPORTED_FILE_TYPES` | Allowed file extensions | `.pdf,.doc,.docx,.txt` |
| `REACT_APP_ENABLE_DEBUG` | Debug mode | `true` |
| `REACT_APP_ENABLE_DEVTOOLS` | DevTools enabled | `true` |

#### Staging Environment (`uat2-backend` and `uat2`)

**Repository Secrets (Shared):**
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `STAGING_HOST` | Staging server IP/hostname | `192.168.1.101` or `uat.yourdomain.com` |
| `STAGING_USER` | SSH username | `django` |
| `SSH_PASSWORD` | SSH password for staging server | `your-secure-password` |

**Environment Secrets for `uat2-backend`:**
| Secret Name | Description | Example Value | Required |
|-------------|-------------|---------------|----------|
| `STAGING_API_URL` | Staging backend API URL | `https://uat-api.yourdomain.com` | ✅ Yes |
| `STAGING_SUPERUSER_USERNAME` | Admin username for staging | `admin` | ✅ Yes |
| `STAGING_SUPERUSER_EMAIL` | Admin email for staging | `admin@yourdomain.com` | ✅ Yes |
| `STAGING_SUPERUSER_PASSWORD` | Admin password for staging | `SecurePassword123!` | ✅ Yes |
| `STAGING_SECRET_KEY` | Django secret key | Generate with `get_random_secret_key()` | ✅ Yes |
| `STAGING_DB_USER` | PostgreSQL database username | `projectmeats_staging` | ✅ Yes |
| `STAGING_DB_PASSWORD` | PostgreSQL database password | `db_secure_password` | ✅ Yes |
| `STAGING_DB_HOST` | PostgreSQL database host | `localhost` or `db.yourdomain.com` | ✅ Yes |
| `STAGING_DB_PORT` | PostgreSQL database port | `5432` | ✅ Yes |
| `STAGING_DB_NAME` | PostgreSQL database name | `projectmeats_staging` | ✅ Yes |
| `STAGING_DOMAIN` | Main staging domain | `uat.yourdomain.com` | ✅ Yes |
| `STAGING_API_DOMAIN` | API staging domain | `uat-api.yourdomain.com` | ✅ Yes |
| `STAGING_FRONTEND_DOMAIN` | Frontend staging domain | `uat.yourdomain.com` | ✅ Yes |
| `STAGING_OPENAI_API_KEY` | OpenAI API key | `sk-...` | ⚪ Optional |
| `STAGING_ANTHROPIC_API_KEY` | Anthropic API key | `sk-ant-...` | ⚪ Optional |
| `STAGING_EMAIL_HOST` | SMTP server hostname | `smtp.gmail.com` | ⚪ Optional |
| `STAGING_EMAIL_USER` | SMTP username | `noreply@yourdomain.com` | ⚪ Optional |
| `STAGING_EMAIL_PASSWORD` | SMTP password | `email_password` | ⚪ Optional |
| `STAGING_REDIS_HOST` | Redis server host | `localhost` | ⚪ Optional |
| `STAGING_REDIS_PORT` | Redis server port | `6379` | ⚪ Optional |
| `STAGING_SENTRY_DSN` | Sentry error tracking DSN | `https://...@sentry.io/...` | ⚪ Optional |

**⚠️ Important Notes for Staging Secrets:**
1. **Currently Implemented**: The GitHub Actions workflow currently only passes `STAGING_SUPERUSER_*` credentials to the deployment script
2. **Requires Workflow Update**: To use the database and other secrets listed above, the workflow file `.github/workflows/unified-deployment.yml` must be updated to export these environment variables during the deployment step (similar to how Development deployment handles `DEVELOPMENT_DB_*` variables)
3. **Server Configuration**: In the meantime, these variables must be manually configured on the staging server's environment (e.g., in `/etc/environment`, systemd service files, or shell profile)
4. **Alignment**: The `config/environments/staging.env` file uses placeholder syntax (e.g., `${STAGING_DB_USER}`) that matches these secret names for consistency

**Environment Secrets for `uat2` (staging frontend):**
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `STAGING_URL` | Staging frontend URL | `https://uat.yourdomain.com` |
| `REACT_APP_API_BASE_URL` | Staging backend API URL | `https://uat-api.yourdomain.com` |
| `REACT_APP_AI_ASSISTANT_ENABLED` | Enable AI features | `true` |
| `REACT_APP_ENABLE_DOCUMENT_UPLOAD` | Enable document uploads | `true` |
| `REACT_APP_ENABLE_CHAT_EXPORT` | Enable chat exports | `true` |
| `REACT_APP_MAX_FILE_SIZE` | Max upload size in bytes | `10485760` (10MB) |
| `REACT_APP_SUPPORTED_FILE_TYPES` | Allowed file extensions | `.pdf,.doc,.docx,.txt` |
| `REACT_APP_ENABLE_DEBUG` | Debug mode | `true` |
| `REACT_APP_ENABLE_DEVTOOLS` | DevTools enabled | `true` |

#### Production Environment (`prod2-backend` and `prod2-frontend`)

**Repository Secrets (Shared):**
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `PRODUCTION_HOST` | Production server IP/hostname | `192.168.1.102` or `yourdomain.com` |
| `PRODUCTION_USER` | SSH username | `django` |
| `SSH_PASSWORD` | SSH password for production server | `your-secure-password` |

**Environment Secrets for `prod2-backend`:**
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `PRODUCTION_API_URL` | Production backend API URL | `https://api.yourdomain.com` |

**Environment Secrets for `prod2-frontend`:**
| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `PRODUCTION_URL` | Production frontend URL | `https://yourdomain.com` |
| `REACT_APP_API_BASE_URL` | Production backend API URL | `https://api.yourdomain.com` |
| `REACT_APP_AI_ASSISTANT_ENABLED` | Enable AI features | `true` |
| `REACT_APP_ENABLE_DOCUMENT_UPLOAD` | Enable document uploads | `true` |
| `REACT_APP_ENABLE_CHAT_EXPORT` | Enable chat exports | `true` |
| `REACT_APP_MAX_FILE_SIZE` | Max upload size in bytes | `10485760` (10MB) |
| `REACT_APP_SUPPORTED_FILE_TYPES` | Allowed file extensions | `.pdf,.doc,.docx,.txt` |
| `REACT_APP_ENABLE_DEBUG` | Debug mode | `false` ⚠️ |
| `REACT_APP_ENABLE_DEVTOOLS` | DevTools enabled | `false` ⚠️ |

**⚠️ Important**: Production should have `REACT_APP_ENABLE_DEBUG` and `REACT_APP_ENABLE_DEVTOOLS` set to `false` for security.

### Quick Reference: Secrets Checklist

Use this checklist when setting up a new environment:

**Repository Secrets (Settings → Secrets and variables → Actions):**
- [ ] `GIT_TOKEN` - GitHub Personal Access Token
- [ ] `DEV_HOST` - Development server IP
- [ ] `DEV_USER` - Development SSH user
- [ ] `DEV_SSH_PASSWORD` - Development SSH password
- [ ] `STAGING_HOST` - Staging server IP
- [ ] `STAGING_USER` - Staging SSH user
- [ ] `SSH_PASSWORD` - Staging SSH password
- [ ] `PRODUCTION_HOST` - Production server IP
- [ ] `PRODUCTION_USER` - Production SSH user

**Environment: dev-backend**
- [ ] `DEV_API_URL`

**Environment: dev-frontend**
- [ ] `DEV_URL`
- [ ] `REACT_APP_API_BASE_URL`
- [ ] `REACT_APP_AI_ASSISTANT_ENABLED`
- [ ] `REACT_APP_ENABLE_DOCUMENT_UPLOAD`
- [ ] `REACT_APP_ENABLE_CHAT_EXPORT`
- [ ] `REACT_APP_MAX_FILE_SIZE`
- [ ] `REACT_APP_SUPPORTED_FILE_TYPES`
- [ ] `REACT_APP_ENABLE_DEBUG` (set to `true`)
- [ ] `REACT_APP_ENABLE_DEVTOOLS` (set to `true`)

**Environment: uat2-backend**
- [ ] `STAGING_API_URL`
- [ ] `STAGING_SUPERUSER_USERNAME`
- [ ] `STAGING_SUPERUSER_EMAIL`
- [ ] `STAGING_SUPERUSER_PASSWORD`
- [ ] `STAGING_SECRET_KEY`
- [ ] `STAGING_DB_USER`
- [ ] `STAGING_DB_PASSWORD`
- [ ] `STAGING_DB_HOST`
- [ ] `STAGING_DB_PORT`
- [ ] `STAGING_DB_NAME`
- [ ] `STAGING_DOMAIN`
- [ ] `STAGING_API_DOMAIN`
- [ ] `STAGING_FRONTEND_DOMAIN`
- [ ] `STAGING_OPENAI_API_KEY` (optional)
- [ ] `STAGING_ANTHROPIC_API_KEY` (optional)
- [ ] `STAGING_EMAIL_HOST` (optional)
- [ ] `STAGING_EMAIL_USER` (optional)
- [ ] `STAGING_EMAIL_PASSWORD` (optional)
- [ ] `STAGING_REDIS_HOST` (optional)
- [ ] `STAGING_REDIS_PORT` (optional)
- [ ] `STAGING_SENTRY_DSN` (optional)

**Environment: uat2**
- [ ] `STAGING_URL`
- [ ] `REACT_APP_API_BASE_URL`
- [ ] All other `REACT_APP_*` variables (same as dev-frontend)

**Environment: prod2-backend**
- [ ] `PRODUCTION_API_URL`

**Environment: prod2-frontend**
- [ ] `PRODUCTION_URL`
- [ ] `REACT_APP_API_BASE_URL`
- [ ] All other `REACT_APP_*` variables
- [ ] `REACT_APP_ENABLE_DEBUG` (set to `false`) ⚠️
- [ ] `REACT_APP_ENABLE_DEVTOOLS` (set to `false`) ⚠️

> **Note:** Images are tagged with short commit SHA and a moving `*-latest` for quick rollbacks.

---

## 4) Containerization

### Backend (Django)

* Multi-stage Docker build installs Python deps and app code.
* Entrypoint runs Gunicorn, app listens on `0.0.0.0:8000`.
* Migrations executed during deployment using the same image + `.env`.

### Frontend (React)

* Multi-stage Docker build compiles the SPA and serves via Nginx.
* Runtime env handled by injected container environment or a mounted config file when needed.
* Healthcheck probes index.

**Dockerfile locations**

* Backend: `backend/Dockerfile`
* Frontend: `frontend/Dockerfile`

**Diagram (placeholder):**
![Containerization](docs/assets/diagrams/pm-containers.png)

---

## 5) Secrets & Configuration

### Source of Truth: GitHub Environments/Secrets

* **Environment Secrets** per environment: Dev, UAT, Prod.
* **Repository Secrets** for shared items (e.g., DO token, SSH passwords if used).
* No secrets are stored on droplets or in the repo.

**Common Frontend Secrets (per env)**

* `REACT_APP_API_BASE_URL`
* `REACT_APP_AI_ASSISTANT_ENABLED`
* `REACT_APP_ENABLE_DOCUMENT_UPLOAD`
* `REACT_APP_ENABLE_CHAT_EXPORT`
* `REACT_APP_MAX_FILE_SIZE`
* `REACT_APP_SUPPORTED_FILE_TYPES`
* `REACT_APP_ENABLE_DEBUG`, `REACT_APP_ENABLE_DEVTOOLS`

**Common Backend Secrets (per env)**

* `DJANGO_SETTINGS_MODULE`
* `SECRET_KEY`
* `DATABASE_URL` (or `DB_*` variables)
* `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`
* Email settings, feature flags, etc.
### GitHub Environments Architecture
```
Repository: ProjectMeats
│
├── Environments
    ├── dev-backend
    │   ├── Protection: None
    │   └── Secrets: DEV_API_URL
    │
    ├── dev-frontend
    │   ├── Protection: None
    │   └── Secrets: DEV_URL, REACT_APP_*
    │
    ├── uat2-backend
    │   ├── Protection: Optional reviewers
    │   └── Secrets: STAGING_API_URL
    │
    ├── uat2
    │   ├── Protection: Optional reviewers
    │   └── Secrets: STAGING_URL, REACT_APP_*
    │
    ├── prod2-backend
    │   ├── Protection: Required reviewers ✓
    │   └── Secrets: PRODUCTION_API_URL
    │
    └── prod2-frontend
        ├── Protection: Required reviewers ✓
        └── Secrets: PRODUCTION_URL, REACT_APP_*

---




```

This shows which DB the app is actually using inside the container.
## 6) Databases

* **Dev DB** created as a **clone of the UAT DB** to mirror schema and test with realistic data.
* Each environment connects to its **own isolated database**.
* Connection strings are provided via `DATABASE_URL` or `DB_*` secrets.

**Verifying DB connection in a running backend container**

```bash
# On the backend droplet:
docker exec -it pm-backend /bin/sh -c 'python - <<PY
import os
for k in ["DATABASE_URL","DB_ENGINE","DB_NAME","DB_HOST","DB_PORT","DB_USER"]:
    print(k, "=", os.environ.get(k))
PY'
```
---

## 7) CI/CD Workflows

* **Build & Push**: Triggered by push to the target branch. Builds both images, pushes to DOCR.
* **Test**:

  * Frontend: `npm ci`, `npm run test:ci`, `npm run type-check`
  * Backend: migrations check + unit tests against a Postgres service
* **Deploy**:

  * Writes `.env` on target droplet from environment secrets
  * Pulls image, runs migrations, collectstatic (backend)
  * Recreates container with `--restart unless-stopped`
  * Nginx reload and health checks

**Pipeline Diagram (placeholder):**
![CI/CD Pipeline](docs/assets/diagrams/pm-pipeline.png)

---

## 8) Rollback Strategy

Rollbacks are **image-based**. Each deployment uses both a pinned tag (`env-<sha>`) and a moving tag (`env-latest`).

**Quick rollback (frontend/backend):**

```bash
# On the droplet:
REG="registry.digitalocean.com/<your-registry>"
IMG="<frontend-or-backend-repo>"
TAG="env-<previous_sha>"   # e.g., dev-abc1234, uat-xyz7890, prod-0fedcba

sudo docker pull "$REG/$IMG:$TAG"
sudo docker rm -f pm-<service> || true
sudo docker run -d --name pm-<service> --restart unless-stopped \
  -p <host_port:container_port> \
  --env-file /path/to/.env \
  $REG/$IMG:$TAG

# Optionally reload nginx if frontend:
sudo nginx -t && sudo systemctl reload nginx
```

> **Note:** DB migrations are not auto-rolled back. If a new migration broke runtime, you may need a forward-fix migration.

---

## 9) Troubleshooting

### Health check fails after deploy

* Check container logs:

  ```bash
  docker logs --tail 200 pm-backend
  docker logs --tail 200 pm-frontend
  ```
* Verify port binding:

  ```bash
  docker ps --format "table {{.Names}}\t{{.Ports}}"
  ```
* Validate Nginx:

  ```bash
  sudo nginx -t && sudo systemctl reload nginx
  ```
* Hit API health endpoint on droplet:

  ```bash
  curl -I http://127.0.0.1:8000/api/v1/health/
  ```

### Frontend still calling `http://localhost:8000/...`

This indicates the SPA was built with a fallback base URL. Confirm one of these patterns is implemented:

* **Runtime env** injection (preferred): App reads `process.env.REACT_APP_*` **at runtime** via an env injection script or mounted config.
* If the app **reads env only at build time**, ensure the correct `REACT_APP_API_BASE_URL` is present **during `npm run build`**. Otherwise, the compiled bundle bakes in localhost.

### Database mismatch (SQLite vs Postgres)

* Dump environment variables inside container (see section 6).
* Confirm `DATABASE_URL` exists and `DB_ENGINE=django.db.backends.postgresql` when using Postgres.
* Test DB connectivity:

  ```bash
  docker exec -it pm-backend /bin/sh -c 'python manage.py showmigrations'
  ```

### Permission issues

* Ensure deployment user can write the `.env` path and Nginx config reloads.
* Confirm mounted volumes exist and are writable (e.g., `/home/django/ProjectMeats/media`).

---

## 10) Governance & Approvals

* **Dev → UAT PR:** Created automatically (or manually) after merge to `development`. UAT deploys on `uat` merge.
* **UAT → Prod PR:** Created after UAT approval. Production deploys on `main` merge.
* **Protection Rules:** Use GitHub Environment protection for Prod (required reviewers, restrict to `main`).

**PR Automation Diagram (placeholder):**
![PR Automation](docs/assets/diagrams/pm-pr-automation.png)

---

## 11) Ops Playbook

**Daily**

* Watch last pipeline runs (build, test, deploy).
* Check health endpoints after each deploy.
* Rotate keys/secrets on a schedule.

**Weekly**

* Review droplet disk usage, Docker image cache:

  ```bash
  df -h
  docker image prune -af
  ```
* Verify backups/versioned tags available for quick rollback.

**Monthly**

* Update base images, dependencies.
* Review environment secrets and documentation for drift.

---

## 12) Benefits Snapshot

| Area                | Before                 | After                                       |
| ------------------- | ---------------------- | ------------------------------------------- |
| Deployments         | Manual SSH, scripts    | Automated in Actions, per-env pipelines     |
| Runtime isolation   | Host processes         | Containers per service                      |
| Config/Secrets      | On servers (hardcoded) | GitHub Environments/Secrets (encrypted)     |
| Environment parity  | Drift across hosts     | Reproducible containers, same build chain   |
| Rollback            | Manual, error-prone    | Tag-based image rollback                    |
| Security posture    | Moderate               | Improved (no host secrets, least privilege) |
| Speed & reliability | Slower, inconsistent   | Faster, standardized, observable            |

---

## 13) Appendix

**Image Naming Convention**

* Backend: `registry.digitalocean.com/<registry>/<repo-backend>:<env>-<shortsha>` and `<env>-latest`
* Frontend: `registry.digitalocean.com/<registry>/<repo-frontend>:<env>-<shortsha>` and `<env>-latest`

**Environments Summary**

| Env  | Branch        | GitHub Envs                     |
| ---- | ------------- | ------------------------------- |
| Dev  | `development` | `dev-backend`, `dev-frontend`   |
| UAT  | `uat`         | `uat2-backend`, `uat2`   |
| Prod | `main`        | `prod2-backend`, `prod2-frontend` |


---


**Last Updated**: 2025
**Maintained By**: Development Team
**Workflow Version**: ci/cd Deployment v1.0
---

