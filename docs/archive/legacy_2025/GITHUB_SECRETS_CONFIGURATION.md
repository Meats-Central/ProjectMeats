# GitHub Secrets Configuration Guide

This document describes the GitHub repository secrets required for CI/CD deployments.

## Overview

ProjectMeats uses separate servers for frontend and backend deployments in each environment (dev, UAT, production). Each environment requires its own set of secrets to be configured in the GitHub repository settings.

## Secret Configuration Location

Navigate to: **Repository Settings → Secrets and variables → Actions**

## Development Environment Secrets

### Frontend Server (IP: 104.131.186.75)

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `DEV_FRONTEND_HOST` | Frontend server hostname or IP address | `104.131.186.75` or `dev-frontend.example.com` |
| `DEV_FRONTEND_USER` | SSH username for frontend server | `ubuntu` or `django` |
| `DEV_FRONTEND_PASSWORD` | SSH password for frontend server | `<secure-password>` |

### Backend Server (IP: 142.93.73.23)

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `DEV_HOST` | Backend server hostname or IP address | `142.93.73.23` or `dev-backend.example.com` |
| `DEV_USER` | SSH username for backend server | `django` |
| `DEV_SSH_PASSWORD` | SSH password for backend server | `<secure-password>` |

### Other Development Secrets

| Secret Name | Description |
|------------|-------------|
| `DEV_DATABASE_URL` | PostgreSQL connection string |
| `DEV_SECRET_KEY` | Django secret key |
| `DEV_BACKEND_IP` | Backend IP used in frontend nginx config |
| `DEV_URL` | Frontend URL for health checks |
| `VITE_API_BASE_URL` | API base URL for frontend app (Vite build) |
| `DO_ACCESS_TOKEN` | DigitalOcean container registry token |

## UAT/Staging Environment Secrets

### Frontend Server

| Secret Name | Description |
|------------|-------------|
| `STAGING_HOST` | Frontend/staging server hostname or IP |
| `STAGING_USER` | SSH username for staging server |
| `SSH_PASSWORD` | SSH password for staging server |

### Backend Server

(Configure similar to development with `UAT_` or `STAGING_` prefix)

## Production Environment Secrets

### Frontend Server

| Secret Name | Description |
|------------|-------------|
| `PROD_FRONTEND_HOST` | Production frontend server hostname or IP |
| `PROD_FRONTEND_USER` | SSH username for production frontend |
| `PROD_FRONTEND_PASSWORD` | SSH password for production frontend |

### Backend Server

| Secret Name | Description |
|------------|-------------|
| `PROD_HOST` | Production backend server hostname or IP |
| `PROD_USER` | SSH username for production backend |
| `PROD_SSH_PASSWORD` | SSH password for production backend |

## Important Notes

1. **Separate Servers**: Frontend and backend are deployed on separate servers in each environment.

2. **Secret Naming Convention**:
   - Development: `DEV_*`
   - UAT/Staging: `UAT_*` or `STAGING_*`
   - Production: `PROD_*`

3. **SSH Authentication**: Currently using password-based SSH authentication. Consider migrating to SSH keys for improved security.

4. **IP Addresses vs Hostnames**: You can use either IP addresses or hostnames that resolve to the correct server.

5. **Firewall Configuration**: Ensure that port 22 (SSH) is accessible from GitHub Actions IP ranges on all deployment servers.

## Troubleshooting

### SSH Connection Failures

If deployments fail with SSH connection errors:

1. Verify the server is accessible from the internet
2. Check SSH service is running: `sudo systemctl status ssh`
3. Verify port 22 is open: `sudo ss -tlnp | grep :22`
4. Check firewall rules allow GitHub Actions IP ranges
5. Verify credentials in GitHub Secrets are correct
6. Check server logs: `sudo tail -f /var/log/auth.log`

### GitHub Actions IP Ranges

GitHub Actions runners connect from dynamic IP addresses. For firewall configuration, see:
- https://api.github.com/meta (includes IP ranges)
- https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners#ip-addresses

## Related Documentation

- [GitHub Actions Workflow Instructions](../.github/copilot-instructions.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Nginx Configuration](./NGINX_CONFIG_FIX.md)

## Security Best Practices

1. **Use Strong Passwords**: Ensure all SSH passwords are strong and unique
2. **Rotate Credentials**: Regularly rotate SSH passwords and API tokens
3. **Limit Access**: Restrict SSH access to only necessary IP ranges
4. **Monitor Logs**: Regularly review authentication logs for suspicious activity
5. **Consider SSH Keys**: Migrate from password to key-based authentication when possible
