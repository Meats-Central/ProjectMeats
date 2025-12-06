# Nginx Configuration Fix - Quick Reference

## The Issue
```
nginx: [emerg] unexpected end of file, expecting ';' or '}' in /etc/nginx/conf.d/pm-frontend.conf:13
```

## The Cause
Indented heredoc delimiter in deployment workflows:
```bash
# ❌ WRONG
cat > file <<NGINX
    content
    NGINX  # <- Indented delimiter NOT recognized by bash
```

## The Fix
Place heredoc delimiter at column 0:
```bash
# ✅ CORRECT
cat > file <<NGINX
content
NGINX  # <- Delimiter at column 0, properly recognized
```

## Validation Pattern
Always validate nginx config before reload:
```bash
# ✅ CORRECT - Validates and fails on error
if nginx -t; then
    systemctl reload nginx
else
    echo "Config validation failed!"
    cat /etc/nginx/conf.d/your-config.conf
    exit 1
fi

# ❌ WRONG - Suppresses errors
nginx -t && systemctl reload nginx || true
```

## Reference Nginx Config
```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

## Testing
```bash
# Test nginx config
docker run --rm -v "$(pwd)/deploy/nginx/frontend.conf:/etc/nginx/conf.d/default.conf:ro" \
  nginx:alpine nginx -t

# Expected: "nginx: configuration file /etc/nginx/nginx.conf test is successful"
```

## Files Modified
- `.github/workflows/11-dev-deployment.yml`
- `.github/workflows/12-uat-deployment.yml`
- `.github/workflows/13-prod-deployment.yml`
- `frontend/dockerfile`

## Full Documentation
See [docs/NGINX_CONFIG_FIX.md](/docs/NGINX_CONFIG_FIX.md) for complete details.
