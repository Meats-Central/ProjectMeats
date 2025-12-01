# ProjectMeats

A multi-tenant SaaS business management platform for meat sales brokers, built with Django REST Framework and React TypeScript.

[![Build Status](https://github.com/Meats-Central/ProjectMeats/actions/workflows/11-dev-deployment.yml/badge.svg)](https://github.com/Meats-Central/ProjectMeats/actions)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup](#-setup)
- [Multi-Tenancy](#-multi-tenancy)
- [AI Features](#-ai-features)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

---

## 🎯 Overview

ProjectMeats manages suppliers, customers, purchase orders, accounts receivables, and related business entities with:

- **Multi-tenant architecture** using django-tenants for data isolation
- **AI Assistant** with Copilot-style UI and document processing
- **RESTful API** with OpenAPI documentation
- **95+ automated tests** for reliability

---

## 🚀 Quick Start

**One-liner to start everything:**

```bash
./start_dev.sh
```

That's it! The script handles PostgreSQL, dependencies, migrations, and server startup.

**Prerequisites**: Python 3.9+, Node.js 18+, PostgreSQL 15+

**Access your application:**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs/
- **Admin**: http://localhost:8000/admin/

---

## 🏗️ Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Backend | Django + DRF | 4.2.7 |
| Frontend | React + TypeScript | 18.2.0 |
| Database | PostgreSQL | 15+ |
| Multi-tenancy | django-tenants | 3.5.0 |
| AI | OpenAI GPT-4 | - |
| Testing | pytest + Jest | - |

---

## 📁 Project Structure

```
ProjectMeats/
├── backend/                 # Django REST Framework API
│   ├── apps/               # Business apps (suppliers, customers, etc.)
│   ├── projectmeats/       # Django project settings
│   └── requirements.txt
├── frontend/               # React TypeScript application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── screens/       # Application screens
│   │   └── services/      # API communication
│   └── package.json
├── mobile/                 # React Native mobile app
├── shared/                 # Cross-platform utilities
├── docs/                   # Documentation hub
├── config/                 # Centralized configuration
│   └── environments/      # Environment-specific configs
└── .github/               # CI/CD workflows
```

---

## 🔧 Setup

### Option 1: Automated (Recommended)

```bash
# Start everything
./start_dev.sh

# Stop servers
./stop_dev.sh
```

### Option 2: Using Make

```bash
make start    # Start all servers
make stop     # Stop all servers
make dev      # Start dev environment
make test     # Run all tests
```

### Option 3: Manual Setup

```bash
# 1. Set up environment
python config/manage_env.py setup development

# 2. Install dependencies
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 3. Set up pre-commit hooks (REQUIRED)
pre-commit install

# 4. Run migrations
cd backend && python manage.py migrate && cd ..

# 5. Start servers
make dev
```

For detailed setup, see [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md).

---

## 🏢 Multi-Tenancy

ProjectMeats implements **schema-based multi-tenancy** using django-tenants:

```
┌─────────────────────────────────────┐
│           PostgreSQL                │
├─────────────────────────────────────┤
│  public schema (shared data)        │
│  - Client/Domain (tenant registry)  │
│  - Core configurations              │
├─────────────────────────────────────┤
│  tenant_acme schema                 │
│  - Suppliers, Customers, Orders     │
├─────────────────────────────────────┤
│  tenant_beta schema                 │
│  - Isolated tenant data             │
└─────────────────────────────────────┘
```

**Key Features**:
- Complete data isolation per tenant
- Automatic schema routing via middleware
- Support for both schema-based and shared-schema patterns

For details, see [docs/MULTI_TENANCY_GUIDE.md](docs/MULTI_TENANCY_GUIDE.md).

---

## 🤖 AI Features

The AI Assistant provides:

- **Natural Language Queries**: "Show me supplier performance metrics"
- **Document Processing**: Drag & drop file upload and analysis
- **Entity Extraction**: Automatic data extraction from documents
- **Business Intelligence**: Performance analysis and insights

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Documentation Hub](docs/README.md) | Central navigation for all docs |
| [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) | Comprehensive deployment instructions |
| [Environment Guide](docs/ENVIRONMENT_GUIDE.md) | Environment configuration |
| [Security Guidelines](docs/SECURITY.md) | Security policies and best practices |
| [Roadmap](docs/ROADMAP.md) | Future plans and upgrades |
| [Contributing Guide](CONTRIBUTING.md) | How to contribute |

---

## 🛠️ Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes following [code style guidelines](CONTRIBUTING.md#-code-style-guidelines)
3. Run tests: `make test`
4. Submit PR with [conventional commit](CONTRIBUTING.md#pr-title-convention) title

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## 📞 Support

- **Documentation**: [docs/README.md](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/Meats-Central/ProjectMeats/issues)
- **Security**: [docs/SECURITY.md](docs/SECURITY.md)

---

**Last Updated**: November 2025
**Need help?** Check the [Documentation Hub](docs/README.md) or create an issue - the setup script handles 99% of common problems automatically.


## End-to-End Deployment Test - 2025-12-01 08:59:12 UTC

Testing complete deployment pipeline from development → UAT → production with all health check fixes applied.

