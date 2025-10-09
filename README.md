# ProjectMeats

A business management application for meat sales brokers, migrated from PowerApps to Django REST Framework (backend) and React TypeScript (frontend). Manages suppliers, customers, purchase orders, accounts receivables, and related business entities with an AI Assistant featuring Copilot-style UI and document processing.

## 🚀 Quick Start (5 Minutes)

**📖 For deployment, see [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Comprehensive deployment guide**

**Prerequisites**: Python 3.9+, Node.js 16+

```bash
# Option 1: Automated Setup (Recommended)
python setup_env.py

# Option 2: Centralized Environment Configuration
python config/manage_env.py setup development
```

The automated setup script configures everything needed including authentication, database, and AI features. For advanced environment management, use the centralized configuration system detailed below.

## 🏗️ Technology Stack

- **Backend**: Django 4.2.7 + Django REST Framework + PostgreSQL
- **Frontend**: React 18.2.0 + TypeScript + Styled Components  
- **AI Assistant**: OpenAI GPT-4 integration with modern Copilot-style interface
- **Authentication**: Django User system with profile management
- **API**: RESTful endpoints with OpenAPI documentation
- **Testing**: 95+ comprehensive backend tests

## 📁 Project Structure

```
ProjectMeats3/
├── backend/                    # Django REST Framework API
│   ├── apps/                  # Business entities (9 complete)
│   │   ├── accounts_receivables/  # Customer payments
│   │   ├── suppliers/            # Supplier management
│   │   ├── customers/            # Customer relationships
│   │   ├── purchase_orders/      # Order processing
│   │   ├── plants/              # Processing facilities
│   │   ├── contacts/            # Contact management
│   │   └── core/                # Shared utilities
│   └── requirements.txt
├── frontend/                   # React TypeScript application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── screens/           # Main application screens
│   │   ├── services/         # API communication
│   │   └── shared/           # Shared utilities (re-exports from /shared)
│   └── package.json
├── mobile/                     # React Native mobile app
│   └── src/
│       └── shared/            # Shared utilities (re-exports from /shared)
├── shared/                     # Cross-platform shared utilities
│   └── utils.ts              # Common TypeScript utilities
├── docs/                      # Documentation
├── archived/                  # Archived files (legacy docs, outdated code)
│   ├── docs/                  # Archived documentation
│   └── code/                  # Archived code/config files
└── config/                    # Centralized configuration
```

## 🚀 Quick Setup

### Recommended Setup (Centralized Configuration)
```bash
# 1. Set up environment using centralized configuration
python config/manage_env.py setup development

# 2. Install dependencies  
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 3. Run database migrations
cd backend && python manage.py migrate && cd ..

# 4. Start development servers
make dev
```

### Alternative Setup (Legacy)
```bash
# Use the legacy setup script
python setup_env.py
```

### Environment Configuration

This project uses a **centralized environment configuration system** for better maintainability:

- **📁 config/environments/** - Environment-specific configurations (dev/staging/prod)
- **🔧 config/manage_env.py** - Environment management script
- **📖 docs/ENVIRONMENT_GUIDE.md** - Complete configuration guide

**Quick Commands:**
```bash
python config/manage_env.py setup development  # Set up dev environment
python config/manage_env.py setup staging      # Set up staging environment  
python config/manage_env.py setup production   # Set up production environment
python config/manage_env.py validate           # Validate current configuration
```

**Prerequisites**: Python 3.9+, Node.js 16+, Git

### Option 1: Quick Setup (Automated)
```bash
# 1. Clone and enter directory
git clone https://github.com/Meats-Central/ProjectMeats3.git
cd ProjectMeats3

# 2. Run setup (handles everything automatically)
python setup_env.py

# 3. Start development servers
make dev
# Windows: run backend and frontend in separate terminals
```

### Option 2: Centralized Environment Management
```bash
# 1. Set up environment using centralized configuration
python config/manage_env.py setup development

# 2. Install dependencies  
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 3. Run database migrations
cd backend && python manage.py migrate && cd ..

# 4. Start development servers
make dev
```

**Access your application:**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

> **Note**: Default superuser credentials are set via environment variables. See `config/environments/development.env` for the `SUPERUSER_USERNAME`, `SUPERUSER_EMAIL`, and `ENVIRONMENT_SUPERUSER_PASSWORD` settings.

## 👤 Superuser Management

The application provides two management commands for superuser handling:

### `setup_superuser` - Password Synchronization

Syncs superuser password from environment variables during deployment. **Always updates password** when user exists.

```bash
# Sync superuser password from environment
make sync-superuser

# Or directly
cd backend && python manage.py setup_superuser
```

**Required Environment Variable:**
- `ENVIRONMENT_SUPERUSER_PASSWORD` - Password to sync (required in production/staging)

**Use Cases:**
- ✅ Deployment automation (runs on every deploy)
- ✅ Password rotation
- ✅ Environment-specific password management

### `create_super_tenant` - Full Tenant Setup

Creates superuser, root tenant, and links them together. Idempotent and safe to run multiple times.

```bash
# Create or update superuser and tenant
make superuser

# Or directly
cd backend && python manage.py create_super_tenant
```

**Environment Configuration:**

**Development Environment:**
```bash
# Set in config/environments/development.env
SUPERUSER_USERNAME=admin
SUPERUSER_EMAIL=admin@meatscentral.com
SUPERUSER_PASSWORD=DevAdmin123!SecurePass
ENVIRONMENT_SUPERUSER_PASSWORD=DevAdmin123!SecurePass
```

**Staging/Production Environments:**
Set these as deployment secrets (GitHub Secrets, AWS Secrets Manager, etc.):
- `SUPERUSER_USERNAME` - Admin username (default: admin)
- `SUPERUSER_EMAIL` - Admin email address
- `SUPERUSER_PASSWORD` - Initial password for tenant creation
- `ENVIRONMENT_SUPERUSER_PASSWORD` - Current/rotated password (required)

**Deployment Integration:**

Both commands run automatically during deployment:
1. `setup_superuser` - Syncs password from environment
2. `create_super_tenant` - Ensures tenant infrastructure exists

## 🔧 Development Guide

### Technology Stack
- **Backend**: Django 4.2.7 + REST Framework + SQLite/PostgreSQL
- **Frontend**: React 18.2.0 + TypeScript + Styled Components
- **AI Assistant**: OpenAI GPT-4 + Copilot-style interface
- **Testing**: 95+ backend tests

### Project Structure
```
ProjectMeats3/
├── backend/           # Django API with 9 business apps
├── frontend/          # React TypeScript application
├── Makefile          # Development commands
├── setup_env.py        # Development environment setup script
```

### Essential Commands
```bash
# Development
make dev              # Start both servers
make backend          # Backend only
make frontend         # Frontend only

# Database
make migrate          # Apply migrations
make migrations       # Create migrations

# Testing & Quality
make test             # Run all tests
make format           # Format code
make lint             # Lint code
make clean            # Clean artifacts
```

### AI Assistant Features
- **Chat Interface**: Natural language business queries
- **Document Processing**: Drag & drop file upload and analysis
- **Entity Extraction**: Automatic data extraction from documents
- **Business Intelligence**: Performance metrics and analysis

### Common Issues & Fixes

**Authentication errors**: 
```bash
python setup_env.py  # Recreates all configs
```

**Module not found errors**:
```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

**CORS errors**: Ensure both servers are running on correct ports (8000/3000)

## 🚀 Production Deployment

**📖 See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for complete step-by-step deployment instructions**

### Deployment Process
The application is deployed via SSH to development, UAT, and production servers. See the deployment guide for detailed instructions on:
- Environment setup and configuration
- SSH-based deployment process
- Database migrations and backups
- Monitoring and troubleshooting

**That's it!** The USER_DEPLOYMENT_GUIDE walks you through each step with a simple checklist format.

### Deployment Testing & Validation
```bash
# Test your deployment configuration before deploying
make deploy-test

# Run comprehensive deployment validation
make deploy-check

# Test a live deployment health
make health-check URL=https://your-app.ondigitalocean.app

# Simulate the full deployment process
python simulate_deployment.py --environment production
```

## 📋 Business Entities (Migration Status)

**Completed** ✅:
- **Accounts Receivables** - Customer payment tracking
- **Suppliers** - Supplier management  
- **Customers** - Customer relationships
- **Purchase Orders** - Order processing
- **Plants** - Processing facilities
- **Contacts** - Contact management
- **User Profiles** - Authentication system
- **AI Assistant** - Document processing and chat

## 🧪 Testing

```bash
make test              # All tests
make test-backend      # Django tests only  
make test-frontend     # React tests only
```

**Coverage**: 95+ backend tests covering all business logic, API endpoints, and data models.

## 🛠️ Deployment Tools

This repository includes comprehensive deployment tools:

- **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** - Complete deployment documentation
- **[test_deployment.py](test_deployment.py)** - Automated deployment configuration validation
- **[health_check.py](health_check.py)** - Live application health verification  
- **[simulate_deployment.py](simulate_deployment.py)** - Full deployment process simulation
- **Makefile commands** - `make deploy-test`, `make deploy-check`, `make health-check`

## 🛠️ Contributing

1. **Setup**: Follow Quick Start guide above
2. **Standards**: Use existing patterns from implemented entities
3. **Testing**: Add tests for new functionality
4. **Code Quality**: Run `make format` and `make lint` before commits

## 📚 Documentation

### Essential Documentation
- **[Documentation Hub](docs/README.md)** - Central navigation for all documentation
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation

### Architecture & Development
- **[Backend Architecture](docs/BACKEND_ARCHITECTURE.md)** - Django backend structure and patterns
- **[Frontend Architecture](docs/FRONTEND_ARCHITECTURE.md)** - React frontend structure and components
- **[Testing Strategy](docs/TESTING_STRATEGY.md)** - Comprehensive testing guide
- **[Repository Best Practices](docs/REPOSITORY_BEST_PRACTICES.md)** - Development workflow and standards

### Deployment & Infrastructure
- **[Environment Guide](docs/ENVIRONMENT_GUIDE.md)** - Environment configuration
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation

### CI/CD & Workflows
- **[Unified Workflow](docs/workflows/unified-workflow.md)** - Main CI/CD workflow documentation
- **[CI/CD Infrastructure](docs/workflows/cicd-infrastructure.md)** - Infrastructure details
- **[Database Backup](docs/workflows/database-backup.md)** - Backup workflow documentation

### Implementation Summaries
- **[Dashboard Enhancement](docs/implementation-summaries/dashboard-enhancement.md)** - Dashboard improvements
- **[Deployment Optimization](docs/implementation-summaries/deployment-optimization.md)** - Deployment improvements
- **[ALLOWED_HOSTS Fix](docs/implementation-summaries/allowed-hosts-fix.md)** - Configuration fix details

## 📚 Reference

### URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Panel**: http://localhost:8000/admin/

### Default Credentials
- **Username**: admin
- **Password**: WATERMELON1219

### AI Assistant Demo Commands
- "Show me supplier performance metrics"
- "Help me analyze purchase orders"
- "Review customer order patterns" 
- Upload documents via drag & drop

---

**Need help?** Check the [Documentation Hub](docs/README.md) or create an issue - the setup script handles 99% of common problems automatically.
