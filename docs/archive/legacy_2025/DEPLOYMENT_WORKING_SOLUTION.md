# Deployment 502 Error - RESOLVED ✅

**Date:** December 6, 2025  
**Status:** ✅ **WORKING**

---

## 🎯 Root Cause

**Architecture:** Two separate servers per environment
- Backend server: Runs Django API on port 8000
- Frontend server: Runs React app + Host Nginx

**The Problem:**
1. Frontend container's internal nginx used `proxy_pass http://backend:8000` (hostname doesn't resolve)
2. Host nginx used `proxy_pass http://localhost:8000` (backend is on different server)
3. Private network blocked by firewall (port 8000 not open between servers)

**The 502 errors were caused by nginx trying to proxy to non-existent/unreachable backends.**

---

## ✅ Working Solution

### Server IPs (Dev Environment)
- **Backend**: `157.245.114.182` (public), `10.17.0.11` (private)
- **Frontend**: `104.131.186.75` (public), `10.17.0.13` (private)

### Frontend Container Fix
```bash
# Add backend hostname pointing to backend's IP
docker run -d --name pm-frontend \
  --add-host backend:157.245.114.182 \
  -p 8080:80 \
  registry.digitalocean.com/.../projectmeats-frontend:tag
```

### Host Nginx Configuration
```nginx
server {
    server_name dev.meatscentral.com;

    # Route API, Admin, Static to Backend Server
    location ~ ^/(api|admin|static)/ {
        proxy_pass http://157.245.114.182:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Route Everything Else to Frontend Container
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/dev.meatscentral.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dev.meatscentral.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
```

---

## 🔧 Workflow Changes Required

### Development Workflow (`.github/workflows/11-dev-deployment.yml`)

**Backend Deployment:**
- No changes needed (already working)

**Frontend Deployment:**
Update the `docker run` command to add backend host:

```yaml
sudo docker run -d --name pm-frontend --restart unless-stopped \
  -p 8080:80 \
  --add-host backend:157.245.114.182 \
  -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
  "$REG/$IMG:$TAG"
```

**Frontend Nginx Configuration:**
Update the nginx config generation to use backend public IP:

```bash
location ~ ^/(api|admin|static)/ {
    proxy_pass http://157.245.114.182:8000;
    # ... rest of config
}
```

---

## 📋 Server Information Needed

To fix UAT and Production, we need:

### UAT Environment
- [ ] Backend public IP: `???`
- [ ] Backend private IP: `???`
- [ ] Frontend public IP: `???`
- [ ] Frontend private IP: `???`

### Production Environment
- [ ] Backend public IP: `???`
- [ ] Backend private IP: `???`
- [ ] Frontend public IP: `???`
- [ ] Frontend private IP: `???`

**To get these IPs, SSH to each server and run:**
```bash
ip addr show eth0 | grep "inet "
```

---

## 🚀 Deployment Verification

After fixing the workflows, verify with:

```bash
# Test backend directly
curl http://BACKEND_PUBLIC_IP:8000/api/v1/health/

# Test through host nginx
curl https://ENVIRONMENT_URL/api/v1/health/

# Test frontend
curl https://ENVIRONMENT_URL/
```

**Expected:** All return 200 OK

---

## 📝 Future Optimization

**Recommended:** Fix DigitalOcean firewall to allow private network communication

1. Go to https://cloud.digitalocean.com/networking/firewalls
2. Add Inbound Rule:
   - Protocol: TCP
   - Port: 8000
   - Source: `10.17.0.0/16` (VPC network)

3. Update workflows to use private IPs instead of public IPs

**Benefits:**
- ✅ Lower latency
- ✅ No bandwidth costs
- ✅ Better security (traffic stays in private network)

---

## 📄 Files Modified

- `/etc/nginx/sites-available/meatscentral` (on frontend server)
- Frontend container run command (in deployment workflow)

**Files to Update:**
- `.github/workflows/11-dev-deployment.yml`
- `.github/workflows/12-uat-deployment.yml`
- `.github/workflows/13-prod-deployment.yml`

