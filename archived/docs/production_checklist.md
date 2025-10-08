# ProjectMeats3 Production Deployment Checklist

**🚀 For complete deployment guide, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

This checklist focuses on the centralized environment configuration system that complements the main deployment process.

## Pre-Deployment Tasks ✅

### Environment Configuration (CENTRALIZED SYSTEM)
- [ ] **Set up environment using centralized configuration**
  ```bash
  # For staging
  python config/manage_env.py setup staging
  
  # For production  
  python config/manage_env.py setup production
  ```
- [ ] **Validate environment configuration**
  ```bash
  python config/manage_env.py validate
  ```
- [ ] **Set environment-specific secrets** (see `config/manage_env.py generate-secrets`)
- [ ] **Review main deployment guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- [ ] **Review environment guide**: `docs/ENVIRONMENT_GUIDE.md`
- [ ] **Review CI/CD pipeline**: `.github/workflows/ci-cd.yml`

### Backend Configuration (Legacy - Use Above Instead)
- [ ] Update `SECRET_KEY` to a strong, unique value
- [ ] Set `DEBUG=False` in production settings
- [ ] Configure PostgreSQL database for production
- [ ] Update `ALLOWED_HOSTS` with production domain
- [ ] Configure static file serving (WhiteNoise or CDN)
- [ ] Set up environment variables for sensitive data
- [ ] Configure CORS settings for production frontend domain
- [ ] Set up SSL/HTTPS configuration
- [ ] Configure email backend for notifications
- [ ] Set up logging and monitoring

### Frontend Configuration (Legacy - Use Above Instead) 
- [ ] Update `REACT_APP_API_BASE_URL` to production backend URL
- [ ] Configure environment-specific variables
- [ ] Optimize build for production (`npm run build`)
- [ ] Set up CDN for static assets (optional)
- [ ] Configure error tracking (Sentry, etc.)

### AI Assistant Configuration
- [ ] Configure AI provider API keys (OpenAI, Anthropic, etc.)
- [ ] Set up document storage (AWS S3, Google Cloud, etc.)
- [ ] Configure file upload limits and validation
- [ ] Set up background task processing (Celery/Redis)
- [ ] Test AI response generation
- [ ] Validate document processing pipelines

### Database & Data
- [ ] Run database migrations
- [ ] Create superuser account
- [ ] Set up database backups
- [ ] Configure database connection pooling
- [ ] Optimize database indexes
- [ ] Set up monitoring and alerts

### Security
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure secure headers
- [ ] Set up CSRF protection
- [ ] Configure authentication and authorization
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Configure secure session management

## Digital Ocean App Platform Deployment ✅

### App Configuration
- [ ] Create new App in Digital Ocean
- [ ] Connect GitHub repository
- [ ] Configure build and run commands
- [ ] Set up environment variables
- [ ] Configure domains and SSL
- [ ] Set up database component (PostgreSQL)
- [ ] Configure static file serving

### Build Commands
```yaml
# Backend (Python/Django)
build_command: |
  pip install -r requirements.txt
  python manage.py collectstatic --noinput
  python manage.py migrate --noinput

run_command: python -m gunicorn --worker-tmp-dir /dev/shm projectmeats.wsgi

# Frontend (React/Node.js)  
build_command: npm run build
run_command: serve -s build
```

### Environment Variables (NEW CENTRALIZED SYSTEM)

**Use the centralized environment configuration system:**

```bash
# Set up production environment
python config/manage_env.py setup production

# Generate secure secrets
python config/manage_env.py generate-secrets

# Validate configuration
python config/manage_env.py validate
```

**Environment variables are now managed through:**
- `config/environments/production.env` - Production-specific configuration
- `config/shared/backend.env.template` - Backend template
- `config/shared/frontend.env.template` - Frontend template

**Key variables to configure:**
- `PRODUCTION_SECRET_KEY` - Django secret key
- `PRODUCTION_DB_*` - Database connection details  
- `PRODUCTION_*_DOMAIN` - Domain configurations
- `PRODUCTION_*_API_KEY` - AI service keys
- `PRODUCTION_S3_*` - AWS S3 storage configuration

For complete documentation, see: `docs/ENVIRONMENT_GUIDE.md`

### Legacy Environment Variables (DEPRECATED)
```
# Backend
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,app.platform.digitalocean.app
DATABASE_URL=postgresql://username:password@host:port/database
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com

# AI Configuration
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Frontend
REACT_APP_API_BASE_URL=https://your-backend-domain.com/api/v1
REACT_APP_AI_ASSISTANT_ENABLED=true
```

## Performance Optimization ✅

### Backend Optimization
- [ ] Enable database query optimization
- [ ] Configure caching (Redis/Memcached)
- [ ] Set up background task processing
- [ ] Optimize API response times
- [ ] Enable database connection pooling
- [ ] Configure static file compression

### Frontend Optimization
- [ ] Enable code splitting and lazy loading
- [ ] Optimize bundle size
- [ ] Configure service worker for caching
- [ ] Optimize images and assets
- [ ] Enable gzip compression
- [ ] Set up performance monitoring

## Monitoring & Maintenance ✅

### Logging
- [ ] Configure application logging
- [ ] Set up error tracking
- [ ] Configure performance monitoring
- [ ] Set up uptime monitoring
- [ ] Configure log rotation and storage

### Backup & Recovery
- [ ] Set up automated database backups
- [ ] Test backup restoration process
- [ ] Configure file storage backups
- [ ] Document recovery procedures
- [ ] Set up monitoring alerts

### Updates & Maintenance
- [ ] Document deployment process
- [ ] Set up CI/CD pipeline
- [ ] Configure automated testing
- [ ] Plan regular maintenance windows
- [ ] Document troubleshooting procedures

## Testing Checklist ✅

### Functional Testing
- [ ] User authentication and authorization
- [ ] AI chat functionality with various prompts
- [ ] Document upload and processing
- [ ] File validation and error handling
- [ ] API endpoint responses
- [ ] Database operations and migrations
- [ ] Frontend responsive design

### Performance Testing
- [ ] Load testing for API endpoints
- [ ] File upload performance testing
- [ ] AI response time testing
- [ ] Database query performance
- [ ] Frontend loading times

### Security Testing
- [ ] Authentication security
- [ ] Input validation and sanitization
- [ ] File upload security
- [ ] CSRF protection
- [ ] SQL injection prevention
- [ ] XSS protection

## Go-Live Tasks ✅

### Final Steps
- [ ] DNS configuration
- [ ] SSL certificate installation
- [ ] Final smoke testing
- [ ] User acceptance testing
- [ ] Documentation updates
- [ ] Team training and handover
- [ ] Go-live communication
- [ ] Post-deployment monitoring

### Post-Deployment
- [ ] Monitor application performance
- [ ] Check error logs and alerts
- [ ] Validate all functionality
- [ ] User feedback collection
- [ ] Performance metrics review
- [ ] Security audit
- [ ] Backup verification

## Rollback Plan ✅

### Emergency Procedures
- [ ] Document rollback steps
- [ ] Test rollback procedures
- [ ] Prepare emergency contacts
- [ ] Set up incident response plan
- [ ] Configure monitoring alerts
- [ ] Plan communication strategy

---

**Note**: This checklist is specifically tailored for Digital Ocean App Platform deployment but can be adapted for other cloud providers.