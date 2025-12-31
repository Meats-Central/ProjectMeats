# Bastion Mode Migration PoC - Documentation

## Overview

Two Proof-of-Concept workflows validate different approaches for running database migrations against private databases through SSH tunneling (bastion mode).

## Workflows

### 1. `poc-bastion-migration.yml` - Lightweight Approach ✅ VALIDATED

**Status:** Successfully tested on 2025-12-09

**Approach:** Direct Python execution on GitHub Actions runner

**How it works:**
```
GitHub Runner → SSH Tunnel → Bastion Host → Private Database
                    ↓
            Python/Django runs on runner
            Connects to localhost:5433
```

**Steps:**
1. SSH tunnel: `ssh -L 5433:$DB_HOST:$DB_PORT $USER@$BASTION_HOST`
2. Install Python dependencies with pip
3. Run `python manage.py showmigrations` directly on runner
4. Database connection: `postgresql://user:pass@127.0.0.1:5433/dbname`

**Pros:**
- ✅ Fast execution (no Docker overhead)
- ✅ Simple debugging (direct logs)
- ✅ Low resource usage
- ✅ Already proven to work

**Cons:**
- ❌ Dependency drift risk (runner vs production)
- ❌ Doesn't test actual deployment image
- ❌ Runner environment != production environment

**When to use:**
- Quick testing
- Development iterations
- Debugging migration issues

---

### 2. `poc-bastion-docker.yml` - Production-Ready Approach 🚀 RECOMMENDED

**Status:** Ready for testing

**Approach:** Containerized execution using production Docker image

**How it works:**
```
GitHub Runner → SSH Tunnel → Bastion Host → Private Database
                    ↓
        Docker Container (--network host)
        Uses production image from DOCR
        Connects to localhost:5433
```

**Steps:**
1. SSH tunnel: `ssh -L 5433:$DB_HOST:$DB_PORT $USER@$BASTION_HOST`
2. Login to DigitalOcean Container Registry
3. Pull production image: `registry.digitalocean.com/meatscentral/projectmeats-backend:dev-latest`
4. Run migrations in container: `docker run --network host ... python manage.py showmigrations`
5. Database connection: `postgresql://user:pass@127.0.0.1:5433/dbname`

**Pros:**
- ✅ Tests actual deployment image
- ✅ Perfect production parity
- ✅ Isolated environment
- ✅ Same image used in deployment
- ✅ Validates container networking

**Cons:**
- ❌ Slower (Docker image pull)
- ❌ Requires registry authentication
- ❌ More complex debugging

**When to use:**
- Production deployments
- Staging/UAT environments
- Final validation before release
- **Integration into `reusable-deploy.yml`**

---

## Technical Deep Dive

### SSH Tunnel Mechanics

Both workflows use the same tunneling approach:

```bash
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -f -N \
  -L 5433:$DB_HOST:$DB_PORT \
  $USER@$BASTION_HOST
```

**Flags explained:**
- `-L 5433:$DB_HOST:$DB_PORT` - Forward local port 5433 to remote database
- `-f` - Background the SSH connection
- `-N` - Don't execute remote commands (tunnel only)
- `-o StrictHostKeyChecking=no` - Accept host key automatically (CI environment)

**Result:** The runner's `localhost:5433` now connects to the private database through the bastion host.

---

### Docker Networking: `--network host`

**Critical for Linux runners:** Docker containers run in isolated networks by default and cannot access `localhost` on the host.

**Solution:** `--network host` shares the runner's network stack with the container.

```bash
docker run --rm \
  --network host \  # <-- Container shares runner's network
  -e DATABASE_URL="postgresql://user:pass@127.0.0.1:5433/db" \
  image:tag \
  python manage.py migrate
```

**What this means:**
- Container's `127.0.0.1:5433` = Runner's `127.0.0.1:5433` = SSH tunnel endpoint
- No need for `host.docker.internal` or bridge networking
- Container can access all runner's localhost services

**Security note:** `--network host` bypasses Docker's network isolation. This is acceptable in CI environments but should be used carefully.

---

## Environment Secrets Required

Both workflows require the same secrets in the GitHub environment (e.g., `dev-backend`):

### SSH/Bastion Secrets
- `DEV_SSH_PASSWORD` - Password for SSH authentication
- `DEV_USER` - SSH username (e.g., `django`)
- `DEV_HOST` - Bastion host IP/hostname

### Database Connection Secrets
- `DEV_DB_HOST` - Private database host (e.g., `db-postgresql-nyc3-12345-do-user-123456-0.db.ondigitalocean.com`)
- `DEV_DB_PORT` - Database port (usually `25060` for DO Managed Postgres)
- `DEV_DB_USER` - Database username
- `DEV_DB_PASSWORD` - Database password
- `DEV_DB_NAME` - Database name

### Django Secrets
- `DEV_DJANGO_SETTINGS_MODULE` - Settings module (e.g., `backend.settings.development`)
- `DEV_SECRET_KEY` - Django secret key

### Container Registry (Docker approach only)
- `DO_ACCESS_TOKEN` - DigitalOcean access token for DOCR

---

## Comparison Matrix

| Feature | Lightweight (`poc-bastion-migration.yml`) | Docker (`poc-bastion-docker.yml`) |
|---------|-------------------------------------------|-----------------------------------|
| **Execution Environment** | Runner Python | Production Docker Image |
| **Speed** | ⚡ Fast | 🐢 Slower (image pull) |
| **Production Parity** | ⚠️ Partial | ✅ Perfect |
| **Dependencies** | pip install | Baked in image |
| **Debugging** | 😊 Easy | 😐 Moderate |
| **Resource Usage** | 💚 Low | 💛 Medium |
| **Image Testing** | ❌ No | ✅ Yes |
| **Registry Required** | ❌ No | ✅ Yes |
| **Network Complexity** | 🟢 Simple | 🟡 Moderate |
| **Production Ready** | 🟡 For dev | 🟢 For all envs |

---

## Integration Recommendations

### Phase 1: Validate Docker Approach ✅ CURRENT

1. **Test `poc-bastion-docker.yml`:**
   - Run manually via workflow_dispatch
   - Use `dev-backend` environment
   - Verify `showmigrations` succeeds
   - Check logs for any issues

### Phase 2: Integrate into Deployment Pipeline

2. **Update `reusable-deploy.yml`:**
   - Replace current SSH-to-server migration step
   - Use Docker-based approach with SSH tunnel
   - Add to `migrate` job:

   ```yaml
   migrate:
     needs: [test-backend]
     runs-on: ubuntu-latest
     environment: ${{ inputs.backend_environment }}
     steps:
       - name: Install SSH tools
         run: sudo apt-get install -y openssh-client sshpass
       
       - name: Setup SSH tunnel
         env:
           SSH_PASSWORD: ${{ secrets.DEV_SSH_PASSWORD }}
         run: |
           sshpass -e ssh -f -N -L 5433:${{ secrets.DEV_DB_HOST }}:${{ secrets.DEV_DB_PORT }} \
             ${{ secrets.DEV_USER }}@${{ secrets.DEV_HOST }}
       
       - name: Run migrations in Docker
         run: |
           docker run --rm --network host \
             -e DATABASE_URL="postgresql://${{ secrets.DEV_DB_USER }}:${{ secrets.DEV_DB_PASSWORD }}@127.0.0.1:5433/${{ secrets.DEV_DB_NAME }}" \
             -e DJANGO_SETTINGS_MODULE="${{ secrets.DEV_DJANGO_SETTINGS_MODULE }}" \
             -e SECRET_KEY="${{ secrets.DEV_SECRET_KEY }}" \
             ${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:${{ inputs.environment }}-${{ github.sha }} \
             python manage.py migrate --fake-initial --noinput
       
       - name: Cleanup tunnel
         if: always()
         run: pkill -f "ssh.*5433" || true
   ```

### Phase 3: Multi-Environment Rollout

3. **Test in stages:**
   - ✅ Dev environment first
   - ⏭️ UAT environment (validate with `uat2-backend`)
   - ⏭️ Production (final validation with `prod2-backend`)

4. **Update secrets for each environment:**
   - Create `UAT_*` and `PROD_*` versions of all secrets
   - Or use environment-scoped secrets (recommended)

### Phase 4: Cleanup

5. **Remove old migration approach:**
   - Delete SSH-to-deployment-server logic
   - Remove venv dependencies from deployment servers
   - Update documentation

---

## Troubleshooting

### Issue: "Bad local forwarding specification"

**Cause:** Environment variables are empty or incorrectly named

**Solution:** Verify secret names match environment (use `DEV_*` prefix for `dev-backend`)

### Issue: Docker container can't connect to tunnel

**Cause:** Not using `--network host`

**Solution:** Ensure `--network host` flag is present in `docker run` command

### Issue: SSH tunnel hangs or fails

**Cause:** Bastion host unreachable or credentials incorrect

**Solution:**
- Verify `DEV_HOST` is accessible from GitHub runners
- Check `DEV_SSH_PASSWORD` is correct
- Ensure user has SSH access

### Issue: Database connection refused

**Cause:** DB host/port incorrect or database firewall

**Solution:**
- Verify `DEV_DB_HOST` and `DEV_DB_PORT` are correct
- Ensure database allows connections from bastion host
- Check DO managed database firewall rules

### Issue: Image pull fails

**Cause:** Registry authentication or image doesn't exist

**Solution:**
- Verify `DO_ACCESS_TOKEN` is valid
- Check image tag exists: `registry.digitalocean.com/meatscentral/projectmeats-backend:dev-latest`
- Run build workflow first if needed

---

## Success Metrics

### Expected Output (Docker Approach)

```
================================
Creating SSH Tunnel
================================
Target: db-postgresql-nyc3-12345-do-user-123456-0.db.ondigitalocean.com:25060
Via Bastion: django@143.198.123.45
Local Port: 5433

✓ SSH tunnel established

================================
Testing Tunnel from Runner
================================
PostgreSQL 15.x ...
✓ Runner can connect through tunnel

================================
Pulling Docker Image
================================
Image: registry.digitalocean.com/meatscentral/projectmeats-backend:dev-latest
✓ Image pulled successfully

================================
Testing Docker Container Access
================================
Running container with --network host...
Database URL: postgresql://user:***@127.0.0.1:5433/dbname

accounts
 [X] 0001_initial
 [X] 0002_auto_20231015_1234
...
✓ Docker container successfully accessed database through tunnel!

================================
✅ DOCKER BASTION MODE SUCCESS
================================
```

---

## Next Steps

1. **Test the Docker approach:** Run `poc-bastion-docker.yml` manually
2. **Compare results:** Both should produce identical migration lists
3. **Choose approach:** Docker is recommended for production
4. **Integrate:** Update `reusable-deploy.yml` with chosen approach
5. **Document:** Update deployment docs with new workflow
6. **Monitor:** Watch first production deployment closely

---

## Questions?

- **Why two workflows?** To validate different approaches and choose the best one
- **Which should we use?** Docker approach for production, lightweight for development
- **Can we use both?** Yes, keep lightweight for quick iteration, use Docker for releases
- **Is this secure?** Yes, tunnel only exists during workflow run, automatically cleaned up
- **What about UAT/Prod?** Same pattern, just change environment and use appropriate secrets

---

*Last Updated: 2025-12-09*
*Status: Docker PoC ready for testing, Lightweight PoC validated*
