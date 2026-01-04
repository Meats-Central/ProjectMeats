# URGENT: Fix ERR_CONNECTION_REFUSED on All Environments

**Issue:** dev.meatscentral.com, uat.meatscentral.com, and meatscentral.com all return `ERR_CONNECTION_REFUSED`

**Root Cause:** No host-level reverse proxy is configured. Containers are running but not exposed to internet.

**Solution:** Deploy host-level nginx reverse proxy (5-10 minutes per environment)

---

## Quick Fix Steps (For Each Environment)

### 1. Preparation (Local Machine)

```bash
# Ensure latest code is on GitHub
cd /workspaces/ProjectMeats
git add -A
git commit -m "fix: deploy host-level nginx reverse proxy for all environments"
git push origin development  # Or uat, main for those environments
```

### 2. Deploy to Dev Environment

```bash
# SSH to dev server
ssh django@dev-server-ip

# Navigate to project directory (or clone if not present)
cd /root/ProjectMeats || git clone https://github.com/Meats-Central/ProjectMeats.git /root/ProjectMeats
cd /root/ProjectMeats
git pull origin development

# Run infrastructure setup (ONE TIME ONLY)
sudo ./scripts/deployment/setup-host-infrastructure.sh dev dev.meatscentral.com 127.0.0.1

# Expected output:
# ✓ Nginx installed
# ✓ SSL certificate obtained
# ✓ Reverse proxy configured
# ✓ Nginx reloaded

# Verify nginx is running
systemctl status nginx

# Test external access
curl -I https://dev.meatscentral.com/health
# Should return: HTTP/2 200

# If containers aren't running, redeploy via GitHub Actions
# Go to: https://github.com/Meats-Central/ProjectMeats/actions
# Run "Master Pipeline" on development branch
```

### 3. Deploy to UAT Environment

```bash
# SSH to UAT server
ssh django@uat-server-ip

# Navigate to project directory
cd /root/ProjectMeats
git pull origin uat

# Run infrastructure setup
sudo ./scripts/deployment/setup-host-infrastructure.sh uat uat.meatscentral.com 127.0.0.1

# Verify
curl -I https://uat.meatscentral.com/health

# Redeploy containers if needed (GitHub Actions on uat branch)
```

### 4. Deploy to Production Environment

```bash
# SSH to production server
ssh django@prod-server-ip

# Navigate to project directory
cd /root/ProjectMeats
git pull origin main

# Run infrastructure setup
sudo ./scripts/deployment/setup-host-infrastructure.sh production meatscentral.com 127.0.0.1

# Verify
curl -I https://meatscentral.com/health

# Redeploy containers if needed (GitHub Actions on main branch)
```

---

## Verification (All Environments)

```bash
# On the server

# 1. Check host nginx is running
systemctl status nginx
# Should be: active (running)

# 2. Check containers are running
docker ps | grep -E 'pm-backend|pm-frontend'
# Should show both containers

# 3. Check frontend is on port 8080 (not 80)
docker ps | grep pm-frontend
# Should show: 0.0.0.0:8080->80/tcp

# 4. Test internal access
curl http://127.0.0.1:8080/        # Frontend
curl http://127.0.0.1:8000/api/v1/health/  # Backend

# 5. Test external access (from your local machine)
curl -I https://dev.meatscentral.com
curl https://dev.meatscentral.com/api/v1/health/
```

---

## If Containers Need Redeployment

After setting up host nginx, redeploy containers with updated port mappings:

**Via GitHub Actions:**
1. Go to: https://github.com/Meats-Central/ProjectMeats/actions
2. Click "Master Pipeline"
3. Click "Run workflow"
4. Select environment (development/uat/production)
5. Click "Run workflow"

**Wait for:** Build → Test → Migrate → Deploy (~5-10 minutes)

**New port mapping:**
- Frontend: `0.0.0.0:8080->80/tcp` (changed from 80->80)
- Backend: `0.0.0.0:8000->8000/tcp` (no change)

---

## Expected Timeline

| Environment | Time Required | Steps |
|-------------|---------------|-------|
| Dev | 10 minutes | Setup nginx + redeploy containers |
| UAT | 10 minutes | Setup nginx + redeploy containers |
| Production | 10 minutes | Setup nginx + redeploy containers |
| **TOTAL** | **30 minutes** | All environments fixed |

---

## Critical Notes

1. **Run setup script ONLY ONCE per environment** - It obtains SSL certificates
2. **Order matters:** Host nginx → THEN → Redeploy containers
3. **DNS must be correct:** Each domain must point to the correct server IP
4. **Firewall must allow:** Ports 80 and 443 from internet
5. **Let's Encrypt rate limit:** Max 5 certificate requests per domain per week

---

## Troubleshooting

### Setup script fails on SSL certificate

**Error:** `Failed to obtain SSL certificate`

**Fix:**
```bash
# Check DNS
dig +short dev.meatscentral.com
# Should return server IP

# Check port 80 is accessible
curl http://dev.meatscentral.com/.well-known/acme-challenge/test
# Should NOT be connection refused

# Check firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Retry certificate
sudo certbot certonly --webroot -w /var/www/certbot -d dev.meatscentral.com
```

### Nginx won't start

**Error:** `nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)`

**Fix:**
```bash
# Find what's using port 80
sudo lsof -i :80

# Kill old nginx or apache
sudo systemctl stop apache2
sudo killall nginx

# Start nginx
sudo systemctl start nginx
```

### Containers not updated after workflow

**Issue:** Frontend still tries to use port 80

**Fix:**
```bash
# Manually stop and remove old containers
docker rm -f pm-frontend pm-backend

# Manually run with correct ports
docker run -d --name pm-frontend \
  --restart unless-stopped \
  -p 8080:80 \
  registry.digitalocean.com/meatscentral/projectmeats-frontend:dev-<SHA>

docker run -d --name pm-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file /home/django/ProjectMeats/backend/.env \
  registry.digitalocean.com/meatscentral/projectmeats-backend:dev-<SHA>
```

---

## Success Criteria

✅ All three environments (dev, uat, prod) return:
```bash
curl -I https://dev.meatscentral.com
# HTTP/2 200 OK

curl https://dev.meatscentral.com/api/v1/health/
# {"status": "healthy"}
```

✅ Browser loads app without errors
✅ No CORS errors in DevTools console
✅ Login and API calls work

---

## Post-Deployment

After all environments are working:

1. **Document the fix:** Update CHANGELOG.md
2. **Monitor logs:** Check for any errors
3. **Update runbooks:** Document new architecture
4. **Test SSL renewal:** `sudo certbot renew --dry-run`
5. **Backup configs:** Save `/etc/nginx/sites-available/projectmeats-*`

---

**Last Updated:** January 4, 2026  
**Status:** Ready to execute  
**Estimated Total Time:** 30 minutes for all environments
