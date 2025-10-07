# ProjectMeats Environment Configuration

This directory contains centralized environment configuration files for all deployment environments.

## Directory Structure

```
config/
├── README.md                    # This file
├── environments/               # Environment-specific configurations
│   ├── development.env        # Development environment
│   ├── staging.env           # Staging environment  
│   └── production.env        # Production environment
├── shared/                    # Shared configuration templates
│   ├── backend.env.template  # Backend environment template
│   └── frontend.env.template # Frontend environment template
└── deployment/               # Deployment configurations
    ├── docker-compose.dev.yml
    ├── docker-compose.staging.yml
    └── docker-compose.prod.yml
```

## Environment Management

### Quick Start
1. Copy the appropriate environment file to create `.env` files:
   ```bash
   # Development
   cp config/environments/development.env backend/.env
   cp config/shared/frontend.env.template frontend/.env.local
   
   # Staging
   cp config/environments/staging.env backend/.env
   cp config/shared/frontend.env.template frontend/.env.local
   
   # Production
   cp config/environments/production.env backend/.env
   cp config/shared/frontend.env.template frontend/.env.local
   ```

2. Update environment-specific values in the copied files

### Environment Variables

#### Backend Variables
- **Django Settings**: `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- **Database**: `DATABASE_URL`
- **CORS**: `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`
- **AI Services**: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- **Email**: `EMAIL_*` settings
- **Storage**: `MEDIA_ROOT`, `STATIC_ROOT`
- **Security**: SSL and HSTS settings for production

#### Frontend Variables  
- **API**: `REACT_APP_API_BASE_URL`
- **Environment**: `REACT_APP_ENVIRONMENT`
- **Features**: `REACT_APP_AI_ASSISTANT_ENABLED`
- **Upload**: `REACT_APP_MAX_FILE_SIZE`, `REACT_APP_SUPPORTED_FILE_TYPES`

### Deployment Environments

#### Development
- Local development with SQLite
- Debug mode enabled
- CORS allows localhost
- File uploads to local media directory

#### Staging  
- Staging server with PostgreSQL
- Debug mode disabled
- CORS for staging domain
- File uploads to staging storage

#### Production
- Production server with PostgreSQL
- Security features enabled
- HTTPS enforced
- CDN for static files
- Production logging and monitoring

### Best Practices

1. **Never commit actual .env files** - only templates and examples
2. **Use strong secrets** - generate unique keys for each environment
3. **Validate configurations** - check all required variables are set
4. **Document changes** - update this README when adding new variables
5. **Test deployments** - validate each environment before go-live

### Security Guidelines

- Use different secrets for each environment
- Enable HTTPS and HSTS in production
- Restrict CORS origins to specific domains
- Use environment-specific database credentials
- Enable logging and monitoring in production
- Regular security audits and updates

### Troubleshooting

Common issues and solutions:
- **CORS errors**: Check CORS_ALLOWED_ORIGINS matches frontend domain
- **Database errors**: Verify DATABASE_URL format and credentials
- **AI errors**: Ensure API keys are valid and have sufficient credits
- **File upload errors**: Check file size limits and supported types

## Additional Documentation

For comprehensive environment configuration documentation, see:
- **[Environment Guide](../docs/ENVIRONMENT_GUIDE.md)** - Complete environment configuration guide
- **[Documentation Hub](../docs/README.md)** - Central documentation navigation
- **[User Deployment Guide](../USER_DEPLOYMENT_GUIDE.md)** - Deployment instructions