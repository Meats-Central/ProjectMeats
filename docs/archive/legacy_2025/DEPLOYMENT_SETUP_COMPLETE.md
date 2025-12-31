# Deployment 502 Error - FIXED! ✅

**Date:** December 6, 2025  
**Status:** ✅ **DEPLOYED AND WORKING**  
**Environment:** Development (dev.meatscentral.com)

---

## 🎉 Success Summary

The **502 Bad Gateway** errors have been resolved! The site is now fully functional:
- ✅ Frontend serving React app
- ✅ Backend API responding on `/api/`
- ✅ Django admin accessible on `/admin/`
- ✅ Static files serving correctly

**Test results:**
```bash
curl https://dev.meatscentral.com/api/v1/health/
# Returns: {"status": "healthy", "version": "1.0.0", "database": "healthy"}

curl https://dev.meatscentral.com/
# Returns: HTML with React app
```

---

## 🔍 Root Cause Analysis

### Architecture Discovery
The deployment uses **separate servers** per environment:
- **Backend Server**: Runs Django API on port 8000
- **Frontend Server**: Runs React app (port 8080) + Host Nginx (port 80/443)

### The Problems

1. **Frontend Container Crash Loop**
   - Container's nginx used `proxy_pass http://backend:8000`
   - Hostname `backend` didn't resolve → nginx failed to start
   - Container kept restarting infinitely

2. **Host Nginx Misconfiguration**
   - Used `proxy_pass http://localhost:8000`
   - Backend was on a **different server**, not localhost
   - Result: 502 Bad Gateway for all `/api/` requests

3. **Network Firewall Block**
   - Private network (10.17.0.x) blocked by DigitalOcean firewall
   - Port 8000 not open between servers
   - Solution: Use public IPs temporarily

---

## ✅ The Fix

### 1. Frontend Container
Added `--add-host` flag to resolve `backend` hostname:

```bash
docker run -d --name pm-frontend \
  --add-host backend:157.245.114.182 \
  -p 8080:80 \
  registry.digitalocean.com/.../projectmeats-frontend:tag
```

### 2. Host Nginx Configuration
Updated `/etc/nginx/sites-available/meatscentral` to proxy to backend's public IP:

```nginx
server {
    server_name dev.meatscentral.com;

    # Route API requests to Backend Server
    location ~ ^/(api|admin|static)/ {
        proxy_pass http://157.245.114.182:8000;  # Backend public IP
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Route everything else to Frontend Container
    location / {
        proxy_pass http://127.0.0.1:8080;  # Local frontend container
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

## 📋 Server Information

### Development Environment
| Server | Role | Public IP | Private IP |
|--------|------|-----------|------------|
| meatscentral-dev-backend | Django API | 157.245.114.182 | 10.17.0.11 |
| meatscentral-dev-frontend | React + Nginx | 104.131.186.75 | 10.17.0.13 |

### UAT Environment
| Server | Role | Public IP | Private IP |
|--------|------|-----------|------------|
| meatscentral-uat-backend | Django API | **TBD** | **TBD** |
| meatscentral-uat-frontend | React + Nginx | **TBD** | **TBD** |

### Production Environment
| Server | Role | Public IP | Private IP |
|--------|------|-----------|------------|
| meatscentral-prod-backend | Django API | **TBD** | **TBD** |
| meatscentral-prod-frontend | React + Nginx | **TBD** | **TBD** |

**To get IPs, SSH to each server and run:**
```bash
ip addr show eth0 | grep "inet "
```

---

## 🔧 Workflow Updates Applied

### Files Modified
- `.github/workflows/11-dev-deployment.yml`
- `.github/workflows/12-uat-deployment.yml`
- `.github/workflows/13-prod-deployment.yml`

### Changes Made

**1. Frontend Container Deployment**
```yaml
# Added --add-host flag
sudo docker run -d --name pm-frontend --restart unless-stopped \
  -p 8080:80 \
  --add-host backend:${{ secrets.DEV_BACKEND_IP }} \
  -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
  ${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:dev-${{ github.sha }}
```

**2. Host Nginx Configuration**
```yaml
# Updated proxy_pass to use backend IP
echo '    location ~ ^/(api|admin|static)/ {'
echo '        proxy_pass http://${{ secrets.DEV_BACKEND_IP }}:8000;'
```

---

## 🔐 GitHub Secrets Required

Add these secrets to your repository:

### Development
- `DEV_BACKEND_IP` = `157.245.114.182`

### UAT (Add after getting IPs)
- `UAT_BACKEND_IP` = **TBD**

### Production (Add after getting IPs)
- `PROD_BACKEND_IP` = **TBD**

**How to add secrets:**
1. Go to https://github.com/Meats-Central/ProjectMeats/settings/secrets/actions
2. Click "New repository secret"
3. Name: `DEV_BACKEND_IP`
4. Value: `157.245.114.182`
5. Click "Add secret"
6. Repeat for UAT and PROD when ready

---

## 🚀 Deployment Steps

### For Development (Ready Now!)
1. ✅ Secrets configured
2. ✅ Workflows updated
3. ✅ Server manually fixed
4. **Next deployment will work automatically**

### For UAT (When Ready)
1. SSH to UAT backend server, get IPs
2. SSH to UAT frontend server, get IPs
3. Add `UAT_BACKEND_IP` secret
4. Manually apply nginx config on UAT frontend server (like we did for dev)
5. Deploy

### For Production (When Ready)
1. SSH to Prod backend server, get IPs
2. SSH to Prod frontend server, get IPs
3. Add `PROD_BACKEND_IP` secret
4. Manually apply nginx config on Prod frontend server
5. Deploy

---

## 📝 Manual Setup for UAT/Production Servers

When you're ready to set up UAT or Production, run these commands on the **frontend server**:

```bash
# 1. Stop broken frontend container
sudo docker rm -f pm-frontend

# 2. Start with correct backend host
sudo docker run -d --name pm-frontend --restart unless-stopped \
  -p 8080:80 \
  --add-host backend:BACKEND_PUBLIC_IP \
  -v /opt/pm/frontend/env/env-config.js:/usr/share/nginx/html/env-config.js:ro \
  registry.digitalocean.com/meatscentral/projectmeats-frontend:ENVIRONMENT-TAG

# 3. Update nginx config
sudo nano /etc/nginx/sites-available/meatscentral
# Change proxy_pass lines to use BACKEND_PUBLIC_IP:8000

# 4. Reload nginx
sudo nginx -t && sudo systemctl reload nginx

# 5. Test
curl https://ENVIRONMENT_URL/api/v1/health/
```

---

## 🔍 Verification Commands

After deployment, run these tests:

```bash
# Test backend directly
curl http://BACKEND_PUBLIC_IP:8000/api/v1/health/
# Expected: {"status": "healthy", ...}

# Test through nginx
curl https://ENVIRONMENT_URL/api/v1/health/
# Expected: {"status": "healthy", ...}

# Test frontend
curl https://ENVIRONMENT_URL/
# Expected: HTML with React app

# Check container status
sudo docker ps | grep pm-
# Expected: Both frontend and backend running
```

---

## 📈 Future Optimization

**Recommended:** Configure DigitalOcean firewall to allow private network communication

### Benefits
- ✅ Lower latency (private network)
- ✅ No bandwidth costs
- ✅ Better security (traffic stays internal)
- ✅ Cheaper at scale

### Steps
1. Go to https://cloud.digitalocean.com/networking/firewalls
2. Find firewall attached to your droplets
3. Add Inbound Rule:
   - Protocol: TCP
   - Port: 8000
   - Source: `10.17.0.0/16` (your VPC network)
4. Test: `curl http://10.17.0.11:8000/api/v1/health/` (from frontend server)
5. Update secrets to use private IPs instead of public IPs
6. Update nginx configs to use private IPs

---

## 🎓 Lessons Learned

1. **Always check if services are on separate servers** - localhost doesn't work across servers
2. **Container hostnames need explicit resolution** - use `--add-host` for custom hostnames
3. **Test connectivity before assuming routing works** - curl direct IPs first
4. **Firewall rules matter** - private network communication requires explicit rules
5. **Public IPs work but aren't optimal** - use private network when possible

---

## 📞 Support

**If deployments still fail:**
1. Check GitHub Actions logs for the specific error
2. SSH to servers and verify containers are running
3. Test backend directly: `curl http://BACKEND_IP:8000/api/v1/health/`
4. Check nginx config: `sudo cat /etc/nginx/sites-available/meatscentral`
5. Check nginx error logs: `sudo tail -50 /var/log/nginx/error.log`

---

## ✅ Success Checklist

- [x] Development environment working
- [ ] UAT backend/frontend IPs collected
- [ ] UAT secrets added to GitHub
- [ ] UAT manually configured and tested
- [ ] Production backend/frontend IPs collected
- [ ] Production secrets added to GitHub
- [ ] Production manually configured and tested
- [ ] All environments deploying successfully via GitHub Actions

---

**The deployment pipeline is now fixed and ready to use!** 🚀
# Deployment Test 2025-12-07-002309
