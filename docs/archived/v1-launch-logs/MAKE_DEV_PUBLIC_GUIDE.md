# Make dev.meatscentral.com Publicly Accessible

## IMPORTANT: Use FRONTEND Server Only

Your architecture has **TWO servers** per environment:
- **Backend Server**: Django app (private, internal only)
- **Frontend Server**: React app + Nginx reverse proxy (public-facing)

**Point DNS to: FRONTEND Server only**

```
Traffic Flow:
Internet → dev.meatscentral.com (Frontend Server nginx:80)
           ├── /api/** → Backend Server:8000 (private IP)
           └── /** → Frontend Container:8080
```

---

## Step 1: Identify Frontend Server

### In DigitalOcean Dashboard
1. Go to https://cloud.digitalocean.com/droplets
2. Look for the droplet that matches `DEV_FRONTEND_HOST` secret
3. This is typically named something like `pm-dev-frontend` or similar
4. **Copy its Public IPv4 address**

Example: `164.92.123.45`

---

## Step 2: Configure DNS Record

### Add A Record
In your DNS provider (Cloudflare, Route53, etc.):
```
Type: A
Name: dev
Value: <FRONTEND_SERVER_PUBLIC_IP>
TTL: 3600
Proxy: OFF (no CDN)
```

### Verify DNS Propagation (wait 5-10 min)
```bash
nslookup dev.meatscentral.com
# Should return: <FRONTEND_SERVER_PUBLIC_IP>
```

---

## Step 3: Open Firewall (DigitalOcean)

1. Go to **Networking** → **Firewalls**
2. Find firewall attached to **frontend server**
3. Click **Edit** → **Inbound Rules**
4. Add rules:
   ```
   Type: HTTP
   Protocol: TCP
   Port: 80
   Sources: All IPv4 (0.0.0.0/0), All IPv6 (::/0)
   
   Type: HTTPS
   Protocol: TCP
   Port: 443
   Sources: All IPv4 (0.0.0.0/0), All IPv6 (::/0)
   ```
5. Save

---

## Step 4: Open Server Firewall (UFW)

SSH into **FRONTEND server**:
```bash
ssh <your-user>@<FRONTEND_SERVER_IP>

# Check current rules
sudo ufw status

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Reload firewall
sudo ufw reload

# Verify rules
sudo ufw status numbered
```

Expected output:
```
Status: active

     To                         Action      From
     --                         ------      ----
[ 1] 22/tcp                     ALLOW IN    Anywhere
[ 2] 80/tcp                     ALLOW IN    Anywhere
[ 3] 443/tcp                    ALLOW IN    Anywhere
```

---

## Step 5: Verify Setup

### Check Nginx is Running
```bash
# On frontend server
sudo systemctl status nginx

# Verify listening on port 80
sudo netstat -tlnp | grep :80
# Should show: 0.0.0.0:80 ... nginx

# Check nginx config
sudo nginx -t
sudo cat /etc/nginx/conf.d/pm-frontend.conf
```

### Check Containers Running
```bash
# Frontend container
sudo docker ps | grep pm-frontend
# Should show: Up X minutes, 0.0.0.0:8080->80/tcp

# Test locally
curl -I http://localhost:80
# Should return: HTTP/1.1 200 OK
```

### Test from Your Machine
```bash
# DNS resolution
nslookup dev.meatscentral.com

# HTTP connection
curl -I http://dev.meatscentral.com

# Test frontend
curl http://dev.meatscentral.com

# Test backend API through nginx
curl http://dev.meatscentral.com/api/v1/health/
```

### Test in Browser
Open: http://dev.meatscentral.com

---

## Step 6 (Optional): Add HTTPS

Once HTTP works, add SSL certificate:

```bash
ssh <frontend-server>

# Install certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d dev.meatscentral.com

# Follow prompts and enable redirect

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## Backend Server Configuration

**DO NOT** configure DNS for backend server:
- Backend should remain **private** (internal network only)
- Frontend nginx proxies to backend via `DEV_BACKEND_IP` (private IP)
- This is proper security architecture

If backend needs to communicate with frontend:
- Use the **private IP** or VPC network
- Already configured in deployment via `DEV_BACKEND_IP` secret

---

## Troubleshooting

### DNS doesn't resolve
```bash
# Check with Google DNS
nslookup dev.meatscentral.com 8.8.8.8

# If fails, wait 15-30 minutes for propagation
# Or clear local DNS cache
```

### Connection timeout
```bash
# Verify you're using FRONTEND server IP, not backend
# Check DigitalOcean firewall (most common issue)
# Check UFW on frontend server: sudo ufw status
```

### 502 Bad Gateway
```bash
# Backend server not reachable from frontend
# Check DEV_BACKEND_IP is set correctly in GitHub secrets
# Verify backend container running on backend server
# Check private network connectivity between servers
```

### 404 or blank page
```bash
# Frontend container issue
sudo docker ps | grep pm-frontend
sudo docker logs pm-frontend --tail 100

# Restart if needed
sudo docker restart pm-frontend
```

---

## Quick Checklist

- [ ] Identified FRONTEND server (not backend)
- [ ] Got frontend server public IP: `_______________`
- [ ] Created DNS A record: dev → frontend IP
- [ ] DNS resolves correctly
- [ ] Opened port 80/443 in DigitalOcean firewall (frontend)
- [ ] Opened port 80/443 in UFW on frontend server
- [ ] Nginx running on frontend server
- [ ] Frontend container running on frontend:8080
- [ ] Can curl from frontend server: `curl -I http://localhost`
- [ ] Can access from browser: http://dev.meatscentral.com

---

## Security Warning

⚠️ **Making dev publicly accessible means anyone can access it**
- Consider adding HTTP Basic Auth
- Or use IP whitelist in nginx
- Or keep dev private and use VPN/SSH tunnel

**Recommended for production environments**: Always use VPN or bastion host.

---

## Summary

```bash
# On your machine:
nslookup dev.meatscentral.com  # Should return FRONTEND server IP
curl -I http://dev.meatscentral.com  # Should return HTTP 200
open http://dev.meatscentral.com  # Should load in browser

# On FRONTEND server:
sudo ufw status  # Should allow 80, 443
sudo systemctl status nginx  # Should be active
sudo docker ps | grep pm-  # Both containers running
curl -I http://localhost  # Should return HTTP 200
```

**Remember**: DNS points to FRONTEND server only. Backend stays private.
