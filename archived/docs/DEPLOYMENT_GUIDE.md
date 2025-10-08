# ProjectMeats3 - Complete Digital Ocean App Platform Deployment Guide

This is the **single comprehensive guide** for deploying ProjectMeats3 to Digital Ocean App Platform with managed PostgreSQL database. This guide replaces all previous deployment documentation and provides everything needed for a smooth dev → staging → production pipeline.

## 🎯 Overview

ProjectMeats3 is a modern Django REST Framework + React TypeScript application optimized for Digital Ocean App Platform deployment. This setup provides:

- **Automated CI/CD pipeline** with GitHub Actions
- **Environment separation** (development, staging, production)
- **Managed PostgreSQL database** with automatic backups
- **Health monitoring** and comprehensive logging
- **Production-ready security** configurations
- **One-command deployment** process

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                Digital Ocean App Platform                   │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Frontend      │   Backend API   │   Managed Database      │
│   (React TS)    │   (Django REST) │   (PostgreSQL 15)       │
│   Port: 3000    │   Port: 8080    │   Auto-managed          │
├─────────────────┼─────────────────┼─────────────────────────┤
│ Static serving  │ Health checks   │ Automated backups       │
│ Build: npm      │ Migrations      │ Connection pooling      │
│ Serve: serve    │ Static files    │ High availability       │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## 📋 Prerequisites

Before deployment, ensure you have:

1. **Digital Ocean Account** with billing enabled
2. **GitHub Repository** access (Meats-Central/ProjectMeats3)
3. **Domain name** (optional but recommended)
4. **Email service** credentials (for notifications)

## 🚀 Deployment Process

### Step 1: Digital Ocean Setup

1. **Create Digital Ocean Account**
   ```bash
   # Visit: https://cloud.digitalocean.com/
   # Sign up and verify your account
   ```

2. **Generate API Token**
   - Go to API → Personal Access Tokens
   - Generate new token with **read/write** permissions
   - Copy token (you'll need it for GitHub Actions)

3. **Install Digital Ocean CLI (Optional)**
   ```bash
   # macOS
   brew install doctl
   
   # Linux
   snap install doctl
   
   # Windows
   choco install doctl
   
   # Authenticate
   doctl auth init --access-token YOUR_TOKEN
   ```

### Step 2: Environment Configuration

**🎯 RECOMMENDED: Use Centralized Environment Management**

ProjectMeats3 includes a centralized environment configuration system that works seamlessly with Digital Ocean deployments:

```bash
# Quick setup for production environment
python config/manage_env.py setup production

# Generate secure secrets
python config/manage_env.py generate-secrets

# Validate configuration before deployment
python config/manage_env.py validate
```

This system provides:
- Pre-configured production settings optimized for Digital Ocean
- Automated secret generation
- Environment validation and best practices
- Easy environment switching (dev/staging/prod)

For complete documentation: `docs/ENVIRONMENT_GUIDE.md`

**Alternative: Manual Configuration**

1. **Backend Environment Variables**
   
   Copy `backend/.env.production.example` to your local settings and configure:
   
   ```bash
   # Required - Generate a strong secret key
   SECRET_KEY=your-ultra-secure-secret-key-minimum-50-characters-long
   
   # Required - Will be set automatically by Digital Ocean
   # DATABASE_URL=postgresql://username:password@host:port/database
   
   # Required - Your domain (or use Digital Ocean's provided domain)
   ALLOWED_HOSTS=your-domain.com,projectmeats3-app.ondigitalocean.app
   
   # Required - Frontend domain for CORS
   CORS_ALLOWED_ORIGINS=https://your-domain.com,https://projectmeats3-app.ondigitalocean.app
   
   # Optional - Email configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-specific-password
   
   # Optional - Admin URL (for security)
   ADMIN_URL=your-secret-admin-path/
   ```

2. **Frontend Environment Variables**
   
   The frontend environment is configured automatically via `app.yaml`, but you can customize:
   
   ```bash
   # Will be set automatically
   REACT_APP_API_BASE_URL=https://your-domain.com/api/v1
   ```

### Step 3: GitHub Actions Setup

1. **Add Repository Secrets**
   
   Go to your GitHub repository → Settings → Secrets and Variables → Actions:
   
   ```
   DIGITALOCEAN_ACCESS_TOKEN = your_digital_ocean_api_token
   ```

2. **Configure Branch Protection** (Recommended)
   
   - Go to Settings → Branches
   - Add rule for `main` branch
   - Enable "Require status checks to pass"
   - Select: Backend Tests, Frontend Tests

### Step 4: Digital Ocean App Platform Deployment

1. **Create New App**
   
   Using Digital Ocean Dashboard:
   ```bash
   # Via Web UI:
   # 1. Go to Apps → Create App
   # 2. Connect GitHub repository: Meats-Central/ProjectMeats3
   # 3. Upload the app.yaml file from the repository root
   # 4. Configure environment variables
   # 5. Deploy
   ```
   
   Using CLI:
   ```bash
   # Clone repository locally
   git clone https://github.com/Meats-Central/ProjectMeats3.git
   cd ProjectMeats3
   
   # Create app from spec
   doctl apps create --spec app.yaml
   
   # Get app ID and set environment variables
   doctl apps list
   APP_ID="your-app-id"
   
   # Set required environment variables
   doctl apps update $APP_ID --spec app.yaml
   ```

2. **Configure Environment Variables in Digital Ocean**
   
   In the Digital Ocean dashboard, add these environment variables:
   
   **Backend Service (api):**
   - `SECRET_KEY`: Your production secret key
   - `ADMIN_URL`: Your secure admin path
   - `EMAIL_HOST`: Your email SMTP server
   - `EMAIL_HOST_USER`: Your email username
   - `EMAIL_HOST_PASSWORD`: Your email password
   
   **Frontend Service (web):**
   - Environment variables are automatically configured via `app.yaml`

3. **Deploy Application**
   
   ```bash
   # Trigger deployment
   doctl apps create-deployment $APP_ID
   
   # Monitor deployment
   doctl apps get-deployment $APP_ID $DEPLOYMENT_ID
   ```

### Step 5: Post-Deployment Setup

1. **Database Migration**
   
   The first deployment automatically runs migrations, but to manually run:
   ```bash
   # Via Digital Ocean console or:
   doctl apps logs $APP_ID --type=build
   ```

2. **Create Superuser**
   
   Access the backend container console:
   ```bash
   # Via Digital Ocean dashboard → App → api service → Console
   python manage.py createsuperuser
   ```

3. **Health Check Verification**
   
   ```bash
   # Check application health
   curl https://your-domain.com/api/v1/health/
   
   # Detailed health check
   curl https://your-domain.com/api/v1/health/detailed/
   ```

4. **SSL Configuration**
   
   - Digital Ocean automatically provisions SSL certificates
   - For custom domains, add DNS records as instructed
   - Verify HTTPS is working: `https://your-domain.com`

## 🔧 Development Workflow

### Local Development

```bash
# Clone repository
git clone https://github.com/Meats-Central/ProjectMeats3.git
cd ProjectMeats3

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm start
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/v1
- Admin: http://localhost:8000/admin

### Deployment Workflow

```mermaid
graph LR
    A[Development] -->|git push develop| B[Staging]
    B -->|git push main| C[Production]
    
    subgraph "Automated Testing"
        D[Backend Tests]
        E[Frontend Tests]
        F[Security Scan]
    end
    
    A --> D
    A --> E
    B --> F
    F --> C
```

1. **Development Environment**
   ```bash
   git checkout develop
   # Make changes
   git add .
   git commit -m "Your changes"
   git push origin develop
   ```
   → Automatically deploys to staging

2. **Production Deployment**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```
   → Automatically deploys to production after all tests pass

## 🎛️ Environment Management

### Development
- **URL**: http://localhost:3000
- **Database**: SQLite (local)
- **Debug**: Enabled
- **Hot reload**: Enabled

### Staging  
- **URL**: https://projectmeats3-staging.ondigitalocean.app
- **Database**: PostgreSQL (managed)
- **Debug**: Disabled
- **Purpose**: Pre-production testing

### Production
- **URL**: https://your-domain.com
- **Database**: PostgreSQL (managed with backups)
- **Debug**: Disabled
- **Security**: Full HTTPS, security headers

## 🔍 Monitoring & Maintenance

### Health Monitoring

```bash
# Basic health check
curl https://your-domain.com/api/v1/health/

# Detailed system health
curl https://your-domain.com/api/v1/health/detailed/

# Readiness check
curl https://your-domain.com/api/v1/ready/
```

### Log Management

```bash
# View application logs
doctl apps logs $APP_ID --type=run

# View build logs
doctl apps logs $APP_ID --type=build

# Follow live logs
doctl apps logs $APP_ID --follow
```

### Database Management

```bash
# Database backups (automatic via Digital Ocean)
doctl databases backup list $DATABASE_ID

# Manual backup
doctl databases backup create $DATABASE_ID

# Connection info
doctl databases connection $DATABASE_ID
```

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   doctl apps logs $APP_ID --type=build
   
   # Common fixes:
   # - Verify requirements.txt versions
   # - Check environment variables
   # - Ensure package.json has correct scripts
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   doctl databases get $DATABASE_ID
   
   # Verify connection string
   doctl databases connection $DATABASE_ID
   ```

3. **Health Check Failures**
   ```bash
   # Check detailed health
   curl https://your-domain.com/api/v1/health/detailed/
   
   # Common causes:
   # - Database connectivity
   # - Disk space
   # - Memory usage
   ```

4. **CORS Issues**
   ```bash
   # Verify CORS settings in environment variables
   echo $CORS_ALLOWED_ORIGINS
   
   # Should include your frontend domain
   ```

### Emergency Rollback

```bash
# List recent deployments
doctl apps list-deployments $APP_ID

# Rollback to previous deployment
doctl apps rollback-deployment $APP_ID $PREVIOUS_DEPLOYMENT_ID
```

## 🔒 Security Checklist

- [x] **Environment Variables**: All secrets stored securely
- [x] **HTTPS**: SSL certificates auto-provisioned
- [x] **Database**: Managed PostgreSQL with encryption
- [x] **Headers**: Security headers configured
- [x] **CORS**: Properly configured for frontend domain
- [x] **Admin**: Secure admin URL path
- [x] **Dependencies**: Regular security updates via CI/CD

## 💰 Cost Estimation

### Digital Ocean Costs (Monthly)

| Component | Size | Cost |
|-----------|------|------|
| App Platform | Basic | $5-12 |
| Managed PostgreSQL | Basic | $15 |
| **Total** | | **~$20-27/month** |

### Scaling Options

- **Basic**: 1 instance, suitable for development/small usage
- **Professional**: Multiple instances, load balancing
- **Enterprise**: High availability, dedicated resources

## 📞 Support & Maintenance

### Regular Maintenance Tasks

1. **Weekly**
   - Review application logs
   - Monitor health check status
   - Check database performance

2. **Monthly**
   - Update dependencies (automated via CI/CD)
   - Review security scan results
   - Test backup restoration process

3. **Quarterly**
   - Performance optimization review
   - Security audit
   - Capacity planning review

### Getting Help

1. **Application Issues**: Check logs and health endpoints
2. **Digital Ocean Issues**: Submit support ticket
3. **Code Issues**: Create GitHub issue in repository

---

## 🎉 Conclusion

This deployment setup provides:

✅ **Production-ready** Django + React application  
✅ **Automated CI/CD** with comprehensive testing  
✅ **Scalable infrastructure** on Digital Ocean  
✅ **Security best practices** implemented  
✅ **Easy maintenance** with health monitoring  
✅ **Cost-effective** hosting solution  

Your ProjectMeats3 application is now enterprise-ready with industry-leading deployment practices!

---

**Need help?** Check the troubleshooting section above or create an issue in the repository.