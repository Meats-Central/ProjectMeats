# ProjectMeats Environment Configuration - Quick Reference

> **📖 For comprehensive documentation, see [docs/ENVIRONMENT_GUIDE.md](../docs/ENVIRONMENT_GUIDE.md)**

This is a quick reference guide for environment configuration. For detailed information, troubleshooting, and advanced configurations, please refer to the complete Environment Guide.

---

## 🔒 Security Guidelines

### 1. Secret Key Management
```bash
# Generate secure keys for each environment
python config/manage_env.py generate-secrets

# Store in environment variable management system (not in code)
# Development: .env files (not committed)
# Staging/Production: Platform secret management (Heroku, AWS, DigitalOcean, etc.)
```

### 2. Database Security
```bash
# Use different databases for each environment
# Development: SQLite or local PostgreSQL
# Staging: Shared PostgreSQL with staging prefix
# Production: Dedicated PostgreSQL with backups
```

### 3. API Keys
```bash
# Use separate API keys for each environment
# Development: Optional/test keys
# Staging: Staging/test keys with limited quotas
# Production: Production keys with full access
```

## 📁 Directory Structure (Industry Standard)

```
ProjectMeats3/
├── config/                     # ✅ Centralized configuration
│   ├── environments/          # Environment-specific configs
│   ├── shared/               # Shared templates
│   ├── deployment/           # Docker & deployment configs
│   └── manage_env.py        # Environment management script
├── docs/                     # ✅ Documentation
│   ├── ENVIRONMENT_GUIDE.md # Complete environment guide
│   └── legacy/              # Archived deployment docs
├── USER_DEPLOYMENT_GUIDE.md  # ✅ Main deployment guide (30-min)
├── backend/                  # Django application
├── frontend/                 # React application
└── scripts/                  # Utility scripts (future)
```

## 🚀 Deployment Commands Summary

### Quick Setup (Any Environment)
```bash
# Development
python config/manage_env.py setup development
make env-dev

# Staging  
python config/manage_env.py setup staging
make env-staging

# Production
python config/manage_env.py setup production
make env-prod
```

### Validation
```bash
python config/manage_env.py validate
make env-validate
```

### Complete Development Setup
```bash
# 1. Environment setup
python config/manage_env.py setup development

# 2. Dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 3. Database
cd backend && python manage.py migrate && cd ..

# 4. Start servers
make dev
```

## 🔧 Environment Variables Reference

| Variable | Development | Staging | Production |
|----------|-------------|---------|------------|
| `DEBUG` | `True` | `False` | `False` |
| `SECRET_KEY` | Generated | `${STAGING_SECRET_KEY}` | `${PRODUCTION_SECRET_KEY}` |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | PostgreSQL | PostgreSQL + pooling |
| `CORS_ALLOWED_ORIGINS` | `localhost:3000` | Staging domain | Production domain only |
| `SECURE_SSL_REDIRECT` | `False` | `True` | `True` |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` |

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Generate environment-specific secrets
- [ ] Configure database connections
- [ ] Set up domain configurations
- [ ] Configure AI service API keys
- [ ] Validate all configurations

### Deployment
- [ ] Run environment setup command
- [ ] Validate configuration
- [ ] Deploy using platform-specific method
- [ ] Run database migrations
- [ ] Test application functionality

### Post-Deployment
- [ ] Monitor application logs
- [ ] Test all major features
- [ ] Verify security settings
- [ ] Set up monitoring and alerts

This centralized system eliminates configuration confusion and ensures consistent, secure deployments across all environments.