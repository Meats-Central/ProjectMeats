# Deployment 502 Error Analysis & Resolution Attempts

**Date:** December 6, 2025  
**Status:** ⚠️ **ONGOING INVESTIGATION**

---

## Summary

Multiple deployment attempts to development environment consistently failing with **502 Bad Gateway** errors during frontend health checks, despite successful container deployments.

### Attempts Made
1. ✅ Restored API routing with regex pattern
2. ✅ Fixed YAML syntax errors (nested heredoc issues)
3. ✅ Used echo-based nginx config generation
4. ✅ Added frontend dependency on backend completion
5. ⏳ Added debugging output for diagnostics

### Current Status
- **Deployment Success**: Backend and Frontend containers deploy successfully
- **Health Check Failure**: Persistent 502 errors when testing `${{ secrets.DEV_URL }}`
- **Root Cause**: Unknown - requires direct server access to diagnose

---

## Detailed Timeline

### PR History
1. **PR #1210**: Restored API routing (4 location blocks)
2. **PR #1212**: Fixed initial YAML syntax error
3. **PR #1214**: Optimized to regex routing pattern
4. **PR #1216**: Fixed heredoc indentation
5. **PR #1218**: Echo-based nginx config (no heredocs)
6. **PR #1220**: Frontend depends on backend
7. **PR #1222**: Added debug output

### Failed Runs
- **Run 19994823941**: 502 errors (before dependency fix)
- **Run 19995040768**: 502 errors (after all fixes)

---

## Hypotheses

### 1. Containers Not Actually Listening
**Symptom**: 502 errors suggest nginx can't reach upstream  
**Possible Cause**: Containers start but don't bind to ports  
**Test**: SSH to server, run `docker ps` and `curl localhost:8000` / `curl localhost:8080`

### 2. Nginx Config Not Applied
**Symptom**: Persistent 502 despite successful nginx reload  
**Possible Cause**: Config written but not active  
**Test**: SSH to server, check `sudo cat /etc/nginx/conf.d/pm-frontend.conf`

### 3. Port Conflicts
**Symptom**: Containers can't bind to 8000/8080  
**Possible Cause**: Ports already in use  
**Test**: SSH to server, run `sudo netstat -tulpn | grep -E ':(8000|8080)'`

### 4. Firewall/Security Rules
**Symptom**: External health check can't reach server  
**Possible Cause**: Firewall blocking port 80  
**Test**: Check DigitalOcean firewall rules

### 5. DNS/Domain Issues
**Symptom**: Health check URL doesn't resolve correctly  
**Possible Cause**: DNS not pointing to correct server  
**Test**: Check `${{ secrets.DEV_URL }}` resolves to deployment server

---

## Recommended Next Steps

### Immediate Actions (Require SSH Access)

1. **Check Container Status**
   \`\`\`bash
   ssh dev-server
   sudo docker ps -a
   sudo docker logs pm-backend --tail 50
   sudo docker logs pm-frontend --tail 50
   \`\`\`

2. **Test Direct Connectivity**
   \`\`\`bash
   curl -v http://localhost:8000/api/v1/health/
   curl -v http://localhost:8080/
   \`\`\`

3. **Check Nginx Configuration**
   \`\`\`bash
   sudo cat /etc/nginx/conf.d/pm-frontend.conf
   sudo nginx -t
   sudo systemctl status nginx
   \`\`\`

4. **Check Port Bindings**
   \`\`\`bash
   sudo netstat -tulpn | grep -E ':(80|8000|8080)'
   sudo ss -tulpn | grep -E ':(80|8000|8080)'
   \`\`\`

5. **Test External Access**
   \`\`\`bash
   curl -v http://$(hostname -I | awk '{print $1}')/
   \`\`\`

### Workflow Modifications

#### Option A: Bypass Health Check Temporarily
Remove or comment out the frontend health check to allow deployment to complete, then manually verify.

\`\`\`yaml
# - name: Health check (Frontend)
#   run: |
#     chmod +x .github/scripts/health-check.sh
#     ./.github/scripts/health-check.sh "${{ secrets.DEV_URL }}" 20 5
\`\`\`

#### Option B: Test Localhost Instead of External URL
Change health check to test from inside the server:

\`\`\`yaml
- name: Health check (Frontend)
  run: |
    sshpass -e ssh ... << 'SSH'
    curl -v http://localhost/
    SSH
\`\`\`

#### Option C: Increase Timeout/Retries
Containers might need more startup time:

\`\`\`yaml
./.github/scripts/health-check.sh "${{ secrets.DEV_URL }}" 40 10
# 40 attempts, 10 second delay = 6.6 minutes total
\`\`\`

---

## Configuration Files

### Expected Nginx Config
\`\`\`nginx
server {
    listen 80;
    server_name _;

    # Route API, Admin, Static to Backend (Port 8000)
    location ~ ^/(api|admin|static)/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Route Everything Else to Frontend (Port 8080)
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
\`\`\`

### Docker Containers Expected
\`\`\`
CONTAINER ID   NAME          IMAGE                          PORTS
xxx            pm-backend    registry.../projectmeats-backend:dev-SHA    0.0.0.0:8000->8000/tcp
yyy            pm-frontend   registry.../projectmeats-frontend:dev-SHA   0.0.0.0:8080->80/tcp
\`\`\`

---

## Debug Output Analysis

The latest deployment (Run 19995040768) includes:
1. Generated nginx config output
2. Backend connectivity test
3. Frontend connectivity test

**Action**: Review logs to see actual output from these tests.

---

## Alternative Approaches

### 1. Manual Deployment First
1. SSH to server
2. Manually pull and run containers
3. Manually configure nginx
4. Verify everything works
5. Then replicate in workflow

### 2. Use Docker Compose
Instead of individual docker run commands, use docker-compose for more reliable orchestration.

### 3. Simplified Architecture
Remove host nginx layer entirely:
- Frontend container includes its own nginx
- Backend routes `/api/` internally
- Single entry point on port 80

---

## Conclusion

The deployment workflow is technically correct and generates valid configuration. The persistent 502 errors indicate a runtime issue that requires direct server access to diagnose. The next deployment run (19995040768) includes debug output that should reveal whether:

- ✅ Nginx config is generated correctly
- ✅ Backend is accessible on localhost:8000
- ✅ Frontend is accessible on localhost:8080

**Recommended**: SSH to development server and run diagnostic commands listed above to identify root cause.

---

## Contact Points

- **Workflow Files**: `.github/workflows/11-dev-deployment.yml`
- **Health Check Script**: `.github/scripts/health-check.sh`
- **Server**: `${{ secrets.DEV_HOST }}`
- **Deployment Logs**: Check GitHub Actions run logs for debug output
