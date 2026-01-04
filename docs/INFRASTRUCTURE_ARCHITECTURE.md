# Infrastructure Architecture & Deployment Guide

**Last Updated:** January 4, 2026  
**Status:** Production-Ready Architecture  
**Architecture Pattern:** Host Nginx Reverse Proxy → Docker Containers

---

## 🏗️ Architecture Overview

### Current Issue (Before This Fix)

```
❌ ERR_CONNECTION_REFUSED on dev.meatscentral.com, uat.meatscentral.com, meatscentral.com

Why?
- Docker containers are running and healthy
- But NO process is listening on public-facing ports 80/443
- Containers bind to localhost:80 and localhost:8000 ONLY
- No reverse proxy routing external traffic to containers
```

### New Architecture (Industry Best Practice)

```
Internet
   │
   ▼
┌──────────────────────────────────────┐
│  Host Server (DigitalOcean Droplet)  │
│                                       │
│  ┌─────────────────────────────┐    │
│  │  Nginx (Host-Level)         │    │
│  │  Listens: 0.0.0.0:80, :443  │    │
│  │  SSL Termination            │    │
│  └───────────┬─────────────────┘    │
│              │                       │
│     ┌────────┴────────┐             │
│     ▼                 ▼             │
│  ┌───────────┐    ┌───────────┐    │
│  │ Frontend  │    │ Backend   │    │
│  │ Container │    │ Container │    │
│  │           │    │           │    │
│  │ Port:8080 │    │ Port:8000 │    │
│  │ (HTTP)    │    │ (HTTP)    │    │
│  └───────────┘    └───────────┘    │
│                                     │
└─────────────────────────────────────┘

Request Flow:
1. Browser → https://dev.meatscentral.com
2. Host Nginx → SSL termination
3. Host Nginx → Routes /api/* to backend:8000
4. Host Nginx → Routes /* to frontend:8080
5. Frontend container nginx → Serves React app
6. Backend container → Django API
```

---

## 🚀 Deployment Steps

### Step 1: Run Host Infrastructure Setup (One-Time Per Environment)

This script must be run **ONCE per environment** on the host server:

```bash
# SSH to the host server
ssh user@dev-server-ip

# Clone or pull latest code
cd /root/ProjectMeats
git pull origin development  # or uat, main

# Run setup script
sudo ./scripts/deployment/setup-host-infrastructure.sh dev dev.meatscentral.com 127.0.0.1

# For UAT:
# sudo ./scripts/deployment/setup-host-infrastructure.sh uat uat.meatscentral.com 127.0.0.1

# For Production:
# sudo ./scripts/deployment/setup-host-infrastructure.sh production meatscentral.com 127.0.0.1
```

**What this does:**
1. ✅ Installs nginx on host
2. ✅ Obtains Let's Encrypt SSL certificate
3. ✅ Deploys reverse proxy configuration
4. ✅ Sets up auto-renewal for SSL
5. ✅ Starts nginx on ports 80/443

### Step 2: Verify DNS Configuration

```bash
# Check DNS is pointing to the host server
dig +short dev.meatscentral.com
# Should return: <your-server-public-ip>

# Test from external network
curl -I http://dev.meatscentral.com/health
# Should return: HTTP/1.1 200 OK (after redirect to HTTPS)
```

### Step 3: Deploy Containers via GitHub Actions

The updated workflow now deploys containers with correct port mappings:

```bash
# Trigger deployment (via GitHub UI or push to branch)
# The workflow will:
# 1. Build Docker images
# 2. Run migrations
# 3. Deploy backend container (port 8000)
# 4. Deploy frontend container (port 8080) ← CHANGED FROM 80
```

**Manual trigger:**
1. Go to https://github.com/Meats-Central/ProjectMeats/actions
2. Select "Master Pipeline"
3. Click "Run workflow"
4. Choose environment (development/uat/production)
5. Click "Run workflow"

---

## 🔍 Verification & Testing

### Check Host Nginx

```bash
# SSH to host
ssh user@server

# Check nginx status
systemctl status nginx
# Should be: active (running)

# Test nginx config
nginx -t
# Should be: test is successful

# View nginx config
cat /etc/nginx/sites-enabled/projectmeats-dev
# Should contain proxy_pass directives

# Check nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Check Docker Containers

```bash
# Check containers are running
docker ps | grep -E 'pm-backend|pm-frontend'
# Should show both containers

# Check frontend is on port 8080 (NOT 80)
docker ps | grep pm-frontend
# Should show: 0.0.0.0:8080->80/tcp

# Check backend is on port 8000
docker ps | grep pm-backend
# Should show: 0.0.0.0:8000->8000/tcp

# Test frontend container directly
curl -I http://127.0.0.1:8080/
# Should return: HTTP/1.1 200 OK

# Test backend container directly
curl -I http://127.0.0.1:8000/api/v1/health/
# Should return: HTTP/1.1 200 OK
```

### Test External Access

```bash
# From your local machine (NOT from server)

# Test main domain
curl -I https://dev.meatscentral.com
# Should return: HTTP/2 200 (via SSL)

# Test backend API via proxy
curl https://dev.meatscentral.com/api/v1/health/
# Should return: {"status": "healthy"}

# Test in browser
# Open: https://dev.meatscentral.com
# Should load the React app
# Check DevTools → Network → No CORS errors
```

---

## 🛠️ Configuration Files

### Host Nginx Config

**Location:** `/etc/nginx/sites-available/projectmeats-<env>`

**Generated from:** `deploy/nginx/host-reverse-proxy.conf.template`

**Key Routes:**
- `/api/*` → Backend container (127.0.0.1:8000)
- `/admin/*` → Backend container (127.0.0.1:8000)
- `/static/*` → Backend container (127.0.0.1:8000)
- `/media/*` → Backend container (127.0.0.1:8000)
- `/*` → Frontend container (127.0.0.1:8080)

### SSL Certificates

**Location:** `/etc/letsencrypt/live/<domain>/`
- `fullchain.pem` - Full certificate chain
- `privkey.pem` - Private key

**Auto-renewal:** Configured via cron (daily at 3 AM)

### Container Ports

| Service  | Host Port | Container Port | Access       |
|----------|-----------|----------------|--------------|
| Frontend | 8080      | 80             | Host nginx   |
| Backend  | 8000      | 8000           | Host nginx   |
| Host nginx | 80, 443 | N/A            | Public internet |

---

## 🔥 Troubleshooting

### Issue: ERR_CONNECTION_REFUSED

**Cause:** Host nginx is not running or not configured

**Fix:**
```bash
# Check nginx status
systemctl status nginx

# If not running
sudo systemctl start nginx

# If config error
sudo nginx -t
# Fix errors shown

# Reload nginx
sudo systemctl reload nginx
```

### Issue: 502 Bad Gateway

**Cause:** Containers are not running or not reachable

**Fix:**
```bash
# Check containers
docker ps | grep -E 'pm-backend|pm-frontend'

# If not running, check logs
docker logs pm-frontend --tail 50
docker logs pm-backend --tail 50

# Restart containers
docker restart pm-frontend pm-backend

# Or redeploy via GitHub Actions
```

### Issue: SSL Certificate Error

**Cause:** Certificate not found or expired

**Fix:**
```bash
# Check certificate
sudo certbot certificates

# Renew certificate
sudo certbot renew

# Test renewal (dry-run)
sudo certbot renew --dry-run

# Reload nginx after renewal
sudo systemctl reload nginx
```

### Issue: Frontend loads but API calls fail (CORS errors)

**Cause:** Frontend environment variable points to wrong URL

**Fix:**
1. Check GitHub secret `REACT_APP_API_BASE_URL`
2. Should be: `https://dev.meatscentral.com` (same domain, NO /api/v1)
3. Update secret via GitHub UI
4. Redeploy frontend to bake in new value

### Issue: Port 80 already in use

**Cause:** Another service is using port 80

**Fix:**
```bash
# Find what's using port 80
sudo lsof -i :80

# If it's an old nginx or apache
sudo systemctl stop apache2  # or httpd

# Remove conflicting services
sudo apt remove apache2

# Restart nginx
sudo systemctl restart nginx
```

---

## 📋 Deployment Checklist

Before declaring environment "working":

- [ ] DNS points to host server IP
- [ ] Host nginx is running (`systemctl status nginx`)
- [ ] SSL certificate is valid (`certbot certificates`)
- [ ] Both containers are running (`docker ps`)
- [ ] Frontend is on port 8080 (`docker ps | grep 8080`)
- [ ] Backend is on port 8000 (`docker ps | grep 8000`)
- [ ] Host nginx routes `/api/` to backend (`curl http://127.0.0.1:8000/api/v1/health/`)
- [ ] Host nginx routes `/` to frontend (`curl http://127.0.0.1:8080/`)
- [ ] External HTTPS works (`curl https://<domain>/health`)
- [ ] External API works (`curl https://<domain>/api/v1/health/`)
- [ ] Browser can load app (no CORS errors)

---

## 🎯 Key Changes Summary

### Before (Broken)
- Frontend container tried to bind to host port 80 → CONFLICT
- No host-level nginx → No external access
- SSL inside container → More complex

### After (Fixed)
- Host nginx on ports 80/443 → External access works
- Frontend container on port 8080 → No port conflict
- SSL termination at host nginx → Simpler, more secure
- Industry best practice architecture

---

## 📚 Related Documentation

- **Nginx Template:** `deploy/nginx/host-reverse-proxy.conf.template`
- **Setup Script:** `scripts/deployment/setup-host-infrastructure.sh`
- **Workflow Config:** `.github/workflows/reusable-deploy.yml`
- **SSL Guide:** `docs/SSL_SETUP.md`
- **Unified Proxy Architecture:** `docs/UNIFIED_PROXY_ARCHITECTURE.md`

---

## 🚨 Important Notes

1. **Run setup script ONLY ONCE per environment** - It obtains SSL certificates and configures nginx
2. **Always deploy containers AFTER host nginx is configured** - Order matters
3. **Frontend container MUST use port 8080** - Port 80 is reserved for host nginx
4. **Never expose Docker containers directly to internet** - Always use host nginx as gateway
5. **SSL certificates auto-renew** - No manual intervention needed

---

**Last Updated:** January 4, 2026  
**Architecture Status:** Production-Ready  
**Next Review:** Before next deployment
