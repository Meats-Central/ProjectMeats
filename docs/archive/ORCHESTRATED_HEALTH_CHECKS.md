# Orchestrated Health Checks Implementation Guide

## Overview
This document describes the standardized health check mechanism for ProjectMeats deployments.

## Components

### 1. Health Check Script
**Location**: `.github/scripts/health-check.sh`

**Purpose**: Reusable bash script for health checks with retry logic and detailed diagnostics.

**Usage**:
```bash
./health-check.sh <url> [max_attempts] [delay_seconds]
```

**Examples**:
```bash
# Local backend health check
./health-check.sh "http://localhost:8000/api/v1/health/" 20 5

# Production health check
./health-check.sh "https://meatscentral.com/api/v1/health/" 15 10
```

**Features**:
- Configurable retry attempts and delays
- Detailed error diagnostics
- HTTP status code validation
- Network failure detection
- Exit codes: 0 (success), 1 (failure)

### 2. Composite Action
**Location**: `.github/actions/health-check/action.yml`

**Purpose**: GitHub Actions composite action for orchestrated health checks.

**Inputs**:
| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `health-url` | Yes | - | Health endpoint URL |
| `max-attempts` | No | `20` | Maximum retry attempts |
| `delay-seconds` | No | `5` | Delay between retries |
| `initial-wait` | No | `10` | Wait before first check |

**Outputs**:
| Output | Description |
|--------|-------------|
| `success` | Whether check passed (true/false) |
| `http-code` | Final HTTP response code |
| `attempts` | Number of attempts made |

**Usage in Workflows**:
```yaml
- name: Health check backend
  uses: ./.github/actions/health-check
  with:
    health-url: 'http://localhost:8000/api/v1/health/'
    max-attempts: '20'
    delay-seconds: '5'
    initial-wait: '10'
```

## Integration with Deployment Workflows

### Dev Deployment
Replace ad-hoc curl loops with:
```yaml
- name: Health check (Backend)
  uses: ./.github/actions/health-check
  with:
    health-url: '${{ secrets.DEV_BACKEND_HEALTH_URL }}'
    max-attempts: '20'
    delay-seconds: '3'
```

### UAT Deployment
```yaml
- name: Post-deployment health check
  uses: ./.github/actions/health-check
  with:
    health-url: 'https://uat.meatscentral.com/api/v1/health/'
    max-attempts: '15'
    delay-seconds: '5'
```

### Production Deployment
```yaml
- name: Production health check
  uses: ./.github/actions/health-check
  with:
    health-url: 'https://meatscentral.com/api/v1/health/'
    max-attempts: '20'
    delay-seconds: '10'
    initial-wait: '15'
```

### SSH-Based Deployments
For remote server health checks via SSH:
```yaml
- name: Remote health check
  env:
    SSHPASS: ${{ secrets.SSH_PASSWORD }}
  run: |
    sshpass -e ssh ${{ secrets.USER }}@${{ secrets.HOST }} <<'HEALTH'
    curl -fsS --max-time 15 http://localhost:8000/api/v1/health/ || exit 1
    HEALTH
```

Or copy the script and run remotely:
```yaml
- name: Remote health check
  env:
    SSHPASS: ${{ secrets.SSH_PASSWORD }}
  run: |
    sshpass -e scp .github/scripts/health-check.sh ${{ secrets.USER }}@${{ secrets.HOST }}:/tmp/
    sshpass -e ssh ${{ secrets.USER }}@${{ secrets.HOST }} <<'HEALTH'
    chmod +x /tmp/health-check.sh
    /tmp/health-check.sh "http://localhost:8000/api/v1/health/" 20 5
    HEALTH
```

## Benefits

### Consistency
- Same health check logic across all environments
- Standardized retry behavior
- Uniform diagnostics

### Maintainability
- Single source of truth for health checks
- Easy to update retry logic
- Centralized error handling

### Observability
- Detailed failure diagnostics
- HTTP code logging
- Attempt tracking

### Security
- No hardcoded credentials
- Environment-specific URLs via secrets
- Configurable timeouts

## Tenant Middleware Compatibility

The health check endpoint must bypass tenant middleware to avoid ALLOWED_HOSTS issues:

**Backend Configuration** (`backend/projectmeats/urls.py`):
```python
# Health check endpoint (bypasses tenant middleware)
urlpatterns = [
    path('api/v1/health/', health_check_view, name='health-check'),
    # ... other patterns
]
```

**Health Check View**:
```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health_check_view(request):
    return JsonResponse({'status': 'healthy'}, status=200)
```

## Troubleshooting

### Health Check Fails with HTTP 000
**Cause**: Network failure, DNS issue, or service not running

**Solutions**:
1. Verify service is running: `docker ps | grep backend`
2. Check service logs: `docker logs pm-backend`
3. Test connectivity: `curl -v http://localhost:8000/api/v1/health/`
4. Verify firewall rules
5. Check DNS resolution

### Health Check Fails with HTTP 400/403/500
**Cause**: Application error or middleware issue

**Solutions**:
1. Check ALLOWED_HOSTS settings
2. Verify CSRF middleware configuration
3. Review tenant middleware bypass
4. Check application logs for errors
5. Test with Host header: `curl -H "Host: domain.com" http://localhost:8000/api/v1/health/`

### Health Check Times Out
**Cause**: Service initialization taking too long

**Solutions**:
1. Increase `initial-wait` parameter
2. Increase `max-attempts` parameter
3. Check database connectivity
4. Review migration job completion
5. Verify no blocking operations in startup

## Migration from Ad-Hoc Checks

### Before (Ad-Hoc)
```yaml
- name: Health check
  run: |
    for i in {1..10}; do
      if curl -fsS "${{ secrets.BACKEND_URL }}" > /dev/null; then
        exit 0
      fi
      sleep 3
    done
    exit 1
```

### After (Orchestrated)
```yaml
- name: Health check
  uses: ./.github/actions/health-check
  with:
    health-url: '${{ secrets.BACKEND_URL }}'
    max-attempts: '10'
    delay-seconds: '3'
```

## Best Practices

1. **Use Environment-Specific Secrets**
   - Store health URLs in GitHub environment secrets
   - Different timeouts for dev/uat/prod

2. **Set Appropriate Timeouts**
   - Dev: Quick checks (10 attempts, 3s delay)
   - UAT: Moderate (15 attempts, 5s delay)
   - Prod: Conservative (20 attempts, 10s delay)

3. **Initial Wait Period**
   - Allow service initialization time
   - Dev: 5-10s
   - Prod: 10-15s

4. **Health Endpoint Design**
   - Keep endpoint lightweight
   - Bypass authentication/tenant middleware
   - Return 200 on success
   - Include basic service checks (DB connectivity)

5. **Logging and Diagnostics**
   - Log all health check attempts
   - Include HTTP codes in failures
   - Capture container logs on failure

## Future Enhancements

1. **Advanced Health Metrics**
   - Database connection pool status
   - Memory usage
   - Queue depth
   - Response time

2. **Slack/Teams Notifications**
   - Alert on health check failures
   - Include diagnostics in notification

3. **Prometheus Integration**
   - Export health check metrics
   - Track success rate over time
   - Alert on degradation

4. **Docker Health Integration**
   - Use `HEALTHCHECK` in Dockerfile
   - Docker Compose health dependencies
   - Automatic container restart on failure

## References

- Health Check Script: `.github/scripts/health-check.sh`
- Composite Action: `.github/actions/health-check/action.yml`
- Smoke Tests: `.github/scripts/smoke-tests.sh`
- Deployment Workflows: `.github/workflows/*deployment*.yml`
