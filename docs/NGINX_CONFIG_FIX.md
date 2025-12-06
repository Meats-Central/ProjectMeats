# Nginx Configuration Fix Documentation

## Problem Statement

The frontend deployment jobs were failing due to malformed nginx configuration files generated during deployment. The issue manifested as:

- **Error**: `nginx: [emerg] unexpected end of file, expecting ';' or '}' in /etc/nginx/conf.d/pm-frontend.conf:13`
- **Impact**: Nginx startup failures, HTTP 502 errors on health checks, deployment failures

## Root Cause

The deployment workflows (dev, UAT, and production) were using heredoc syntax incorrectly to generate nginx configuration files. Specifically:

### Issue 1: Indented Heredoc Delimiter
```bash
# ❌ WRONG - Delimiter is indented
sudo bash -c 'cat > /etc/nginx/conf.d/pm-frontend.conf <<NGINX
            server {
              listen 80;
              ...
            }
            NGINX'  # <- This delimiter will NOT be recognized
```

When using `<<DELIMITER`, the closing delimiter **must** be at column 0 (not indented). If it's indented, bash doesn't recognize it as the delimiter and continues reading until EOF, resulting in:
- The literal text `NGINX` being included in the config file
- Malformed nginx configuration
- Bash warning: "here-document delimited by end-of-file"

### Issue 2: Missing Validation
The original code used `|| true` which suppressed errors:
```bash
sudo nginx -t && sudo systemctl reload nginx || true
```

This meant even if nginx config was invalid, the deployment would continue, leading to:
- Nginx not reloading with new config
- Old/broken configs remaining active
- Silent failures

## Solution

### 1. Fixed Heredoc Syntax
```bash
# ✅ CORRECT - Delimiter at column 0
sudo bash -c 'cat > /etc/nginx/conf.d/pm-frontend.conf <<NGINX
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
NGINX'  # <- Delimiter at column 0, properly recognized
```

### 2. Added Explicit Validation
```bash
# Validate nginx configuration before applying
echo "Validating nginx configuration..."
if sudo nginx -t; then
  echo "✓ Nginx configuration is valid"
  sudo systemctl reload nginx
  echo "✓ Nginx reloaded successfully"
else
  echo "✗ Nginx configuration validation failed!"
  echo "Config file content:"
  sudo cat /etc/nginx/conf.d/pm-frontend.conf
  exit 1
fi
```

### 3. Updated Frontend Dockerfile
Added an entrypoint script that validates nginx config before starting:

```dockerfile
# Create entrypoint script with nginx validation
RUN cat > /docker-entrypoint.sh <<'EOF'
#!/bin/bash
set -e

echo "=== Validating nginx configuration ==="
if nginx -t -c /etc/nginx/nginx.conf; then
    echo "✓ Nginx configuration is valid"
else
    echo "✗ Nginx configuration validation failed!"
    echo ""
    echo "Configuration files:"
    echo "===================="
    echo "Main config: /etc/nginx/nginx.conf"
    echo "Default config: /etc/nginx/conf.d/default.conf"
    echo ""
    echo "Content of /etc/nginx/conf.d/default.conf:"
    cat /etc/nginx/conf.d/default.conf
    exit 1
fi

echo "=== Starting nginx ==="
exec nginx -g 'daemon off;'
EOF

RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
```

## Files Changed

1. `.github/workflows/11-dev-deployment.yml` - Dev deployment workflow
2. `.github/workflows/12-uat-deployment.yml` - UAT deployment workflow  
3. `.github/workflows/13-prod-deployment.yml` - Production deployment workflow
4. `frontend/dockerfile` - Frontend Docker image build

## Testing

### Manual Validation Test
```bash
# Test the corrected nginx config
docker run --rm -v "$(pwd)/deploy/nginx/frontend.conf:/etc/nginx/conf.d/default.conf:ro" \
  nginx:alpine nginx -t

# Expected output:
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Heredoc Pattern Test
```bash
# Test heredoc with non-indented delimiter
bash -c 'cat > /tmp/test.conf <<EOF
server {
    listen 80;
}
EOF'

# Should create valid file without warnings
cat /tmp/test.conf
```

## Prevention for Future Contributors

### Heredoc Best Practices

1. **Always place the closing delimiter at column 0**:
   ```bash
   # ✅ CORRECT
   cat > file <<EOF
   content
   EOF
   
   # ❌ WRONG
   cat > file <<EOF
   content
       EOF  # Indented - won't work
   ```

2. **Use `<<-` if you want to allow indentation** (tabs only):
   ```bash
   # This allows tabs before delimiter (but not spaces)
   cat > file <<-EOF
   	content
   	EOF  # Tab-indented - OK with <<-
   ```

3. **Quote the delimiter to prevent variable expansion** when needed:
   ```bash
   # Prevent expansion
   cat > file <<'EOF'
   $variable will be literal
   EOF
   ```

### Nginx Validation Best Practices

1. **Always validate before reload**:
   ```bash
   if nginx -t; then
       systemctl reload nginx
   else
       echo "Config validation failed"
       exit 1
   fi
   ```

2. **Never suppress validation errors**:
   ```bash
   # ❌ WRONG - Hides errors
   nginx -t && systemctl reload nginx || true
   
   # ✅ CORRECT - Fails on error
   nginx -t && systemctl reload nginx
   ```

3. **Provide detailed error output**:
   ```bash
   if ! nginx -t; then
       echo "Configuration validation failed!"
       echo "Config content:"
       cat /etc/nginx/conf.d/your-config.conf
       exit 1
   fi
   ```

## Reference Configuration

The corrected nginx reverse proxy configuration:

```nginx
server {
    listen 80;
    server_name _;
    
    # Proxy to frontend container on port 8080
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Proxy timeouts for better reliability
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Key Elements
- ✅ Opening `server {` brace
- ✅ All directives end with semicolons
- ✅ All location blocks properly closed
- ✅ Closing `}` brace for server block
- ✅ No syntax errors

## Monitoring and Alerts

To prevent similar issues in the future:

1. **Pre-deployment validation**: All three workflows now validate nginx config before applying
2. **Container startup validation**: Frontend Dockerfile validates config before starting nginx
3. **Explicit error messages**: Clear output when validation fails
4. **Exit on failure**: Deployments fail fast with clear error messages

## Related Documentation

- [Deployment Workflows Guide](/branch-workflow-checklist.md)
- [Frontend Dockerfile](/frontend/dockerfile)
- [Nginx Configuration](/deploy/nginx/frontend.conf)

## Changelog

- **2025-12-06**: Fixed heredoc delimiter placement and added validation in all deployment workflows
- **2025-12-06**: Added nginx validation to frontend Dockerfile entrypoint
- **2025-12-06**: Added comprehensive error handling and documentation
