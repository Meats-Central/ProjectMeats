# ProjectMeats Documentation Hub

**Last Updated**: December 2025  

Welcome to the ProjectMeats documentation! This page serves as your **central navigation point** for all project documentation.

---

## 📋 Table of Contents

| Section | Description |
|---------|-------------|
| [🚀 Quick Links](#-quick-links) | Essential links to get started |
| [📖 Getting Started](#getting-started) | Setup and onboarding guides |
| [🏗️ Architecture & Development](#-architecture--development) | Backend, frontend, and testing guides |
| [🚀 Deployment & Infrastructure](#-deployment--infrastructure) | Deployment, CI/CD, and environment guides |
| [🔐 Security & Best Practices](#-security--best-practices) | Security guidelines and multi-tenancy standards |
| [📁 Documentation Structure](#-documentation-structure) | How documentation is organized |
| [🎯 Finding What You Need](#-finding-what-you-need) | Topic-based navigation |

---

## 🚀 Quick Links

### Getting Started
- **[Main README](../README.md)** - Project overview and quick setup
- **[Quick Start Guide](../QUICK_START.md)** - 5-minute setup guide
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project

### Essential Guides
- **[Migration Guide](MIGRATION_GUIDE.md)** ⭐ - Complete database migration guide with django-tenants
- **[Authentication Guide](AUTHENTICATION_GUIDE.md)** ⭐ - Authentication, permissions, and superuser management
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** ⭐ - Common issues and solutions
- **[Security Guidelines](SECURITY.md)** ⭐ - Vulnerability reporting and security best practices
- **[Roadmap](ROADMAP.md)** ⭐ - Future plans and upgrade recommendations

### Core Documentation

#### 🚀 Deployment & Infrastructure
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation
- **[Environment Configuration Guide](ENVIRONMENT_GUIDE.md)** - Environment setup and configuration
- **[Multi-Tenancy Guide](MULTI_TENANCY_GUIDE.md)** - Multi-tenancy architecture and setup
- **[CI/CD Workflows](workflows/)** - GitHub Actions workflows and automation

#### 🔧 Development Guides
- **[Backend Architecture](BACKEND_ARCHITECTURE.md)** - Django backend structure and patterns
- **[Frontend Architecture](FRONTEND_ARCHITECTURE.md)** - React frontend structure and components
- **[Testing Strategy](TESTING_STRATEGY.md)** - Comprehensive testing guide
- **[Repository Best Practices](REPOSITORY_BEST_PRACTICES.md)** - Development workflow and standards
- **[Branch Workflow](../branch-workflow-checklist.md)** - Branch naming and workflow guide

#### 📋 Repository Maintenance
- **[Platform Core Components Audit](REPO_AUDIT_PLATFORM_CORE.md)** - Comprehensive repository audit report
- **[Cleanup Checklist](CLEANUP_CHECKLIST.md)** - Actionable cleanup tasks from audit
- **[Archived Documentation](archived-2024-11/)** - Historical documentation (Nov 2024 consolidation)

---

## 🏗️ Best Practices

### Monorepo Structure Guidelines

Following [GitHub's repository best practices](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories):

1. **Clear README**: Every project should have a comprehensive README with setup instructions
2. **Topics and Tags**: Use repository topics for discoverability
3. **Branch Protection**: Protect `main`, `uat`, and `development` branches
4. **Issue Templates**: Use standardized issue and PR templates
5. **CODEOWNERS**: Define code ownership for automated review assignment

### Django/React Monorepo Standards

| Component | Location | Technology |
|-----------|----------|------------|
| Backend API | `backend/` | Django 4.2.7 + DRF |
| Frontend Web | `frontend/` | React 18.2.0 + TypeScript |
| Mobile App | `mobile/` | React Native |
| Shared Code | `shared/` | Cross-platform utilities |
| Documentation | `docs/` | Markdown |
| Configuration | `config/` | Environment configs |

### Code Style Standards

**Backend (Python):**
- Follow PEP 8 style guide
- Use `black` for formatting
- Use `flake8` for linting
- Use `isort` for import sorting
- Add type hints where appropriate

**Frontend (TypeScript/React):**
- Use TypeScript for type safety
- Use `eslint` for linting
- Use `prettier` for formatting
- Follow React hooks patterns

---

## 🔐 Security & Best Practices

### SaaS Multi-Tenancy Standards

ProjectMeats implements enterprise-grade multi-tenancy following industry best practices:

#### Isolation Strategies

| Strategy | Implementation | Use Case |
|----------|----------------|----------|
| Schema-based | django-tenants | Complete data isolation |
| Row-level Security | Tenant FK filtering | Shared schema with isolation |
| Application-level | Middleware + Views | Request-scoped tenant context |

#### Security Standards (OWASP/GDPR Compliance)

1. **Data Isolation**: Strict tenant data separation using PostgreSQL schemas
2. **RBAC**: Role-Based Access Control with tenant-scoped permissions
3. **Audit Logging**: Track all data access and modifications
4. **Encryption**: Data encryption at rest and in transit
5. **Minimal Privileges**: Database users have only necessary permissions

For detailed security guidelines, see **[SECURITY.md](SECURITY.md)**.

---

## 📁 Documentation Structure

```
docs/
├── README.md (this file)              # Documentation navigation hub
│
├── SECURITY.md ⭐                      # Security guidelines and vulnerability reporting
├── ROADMAP.md ⭐                       # Future plans and upgrades
├── MIGRATION_GUIDE.md ⭐               # Complete database migration guide
├── AUTHENTICATION_GUIDE.md ⭐          # Auth & permissions guide
├── TROUBLESHOOTING.md ⭐               # Common issues and solutions
│
├── BACKEND_ARCHITECTURE.md            # Django backend architecture
├── FRONTEND_ARCHITECTURE.md           # React frontend architecture
├── TESTING_STRATEGY.md                # Comprehensive testing guide
├── REPOSITORY_BEST_PRACTICES.md       # Development workflow standards
├── ENVIRONMENT_GUIDE.md               # Environment configuration
├── DEPLOYMENT_GUIDE.md                # Deployment procedures
├── MULTI_TENANCY_GUIDE.md             # Multi-tenancy architecture
├── MIGRATION_BEST_PRACTICES.md        # Migration best practices
│
├── environment-variables.md           # Environment variables reference
│
├── lessons-learned/                   # Retrospectives and lessons
│   └── 3-MONTH-RETROSPECTIVE.md      # Aug-Nov 2024 retrospective
│
├── workflows/                         # CI/CD workflow documentation
│   ├── unified-workflow.md           # Main workflow docs
│   ├── cicd-infrastructure.md        # Infrastructure details
│   └── database-backup.md            # Backup workflow
│
├── implementation-summaries/          # Feature implementation docs
│
├── reference/                         # Reference documentation
│
└── archived-2024-11/                  # Archived documentation
```

---

## 🎯 Finding What You Need

### I want to...

**Set up my development environment:**
- Follow [Main README Quick Setup](../README.md#-quick-setup)
- Configure environment with [Environment Guide](ENVIRONMENT_GUIDE.md)
- Check [Migration Guide](MIGRATION_GUIDE.md) for database setup

**Deploy the application:**
- Start with [Deployment Guide](DEPLOYMENT_GUIDE.md) for comprehensive instructions
- Reference [Environment Guide](ENVIRONMENT_GUIDE.md) for configuration details
- Check [Troubleshooting Guide](TROUBLESHOOTING.md) for deployment issues

**Fix a database migration issue:**
- Check [Migration Guide](MIGRATION_GUIDE.md) for comprehensive patterns
- See [Troubleshooting Guide](TROUBLESHOOTING.md) for common problems

**Set up authentication or manage users:**
- Read [Authentication Guide](AUTHENTICATION_GUIDE.md) for complete auth system
- Learn about superuser management and environment-specific credentials

**Understand multi-tenancy:**
- Read [Multi-Tenancy Guide](MULTI_TENANCY_GUIDE.md) for architecture overview
- See [Migration Guide](MIGRATION_GUIDE.md) for django-tenants migration patterns
- Review [Security Guidelines](SECURITY.md) for isolation best practices

**Report a security vulnerability:**
- See [Security Guidelines](SECURITY.md) for responsible disclosure process

**Contribute to the project:**
- Read [Contributing Guide](../CONTRIBUTING.md)
- Review [Branch Workflow Checklist](../branch-workflow-checklist.md)
- Check [Repository Best Practices](REPOSITORY_BEST_PRACTICES.md)

**Debug an issue:**
- Start with [Troubleshooting Guide](TROUBLESHOOTING.md)
- Check [Migration Guide](MIGRATION_GUIDE.md) for database issues
- See [Authentication Guide](AUTHENTICATION_GUIDE.md) for auth problems

**Understand CI/CD workflows:**
- Read [Unified Workflow Documentation](workflows/unified-workflow.md)
- Review [CI/CD Infrastructure](workflows/cicd-infrastructure.md)
- Check [Database Backup Workflow](workflows/database-backup.md)

**Find old documentation:**
- Browse [Archived Documentation](archived-2024-11/)

---

## 🔑 Documentation Principles

### Sources of Truth

| Topic | Source Document |
|-------|-----------------|
| Deployment | [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) |
| CI/CD | [workflows/unified-workflow.md](workflows/unified-workflow.md) |
| Environment | [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) |
| Contributing | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Security | [SECURITY.md](SECURITY.md) |
| Development Progress | [TODO_LOG.md](TODO_LOG.md) |

### When Documentation Conflicts

If you find conflicting information:
1. Trust the source of truth listed above for each topic
2. Recent documentation (in main docs/ folder) supersedes archived documentation
3. Archived documentation is preserved in `archived-2024-11/` for reference only

---

## 📝 Maintaining Documentation

### Documentation Location Guidelines

| Location | Content |
|----------|---------|
| Root directory | README.md, CONTRIBUTING.md, critical top-level docs (max 5) |
| `docs/` | All detailed documentation |
| `docs/workflows/` | CI/CD and automation documentation |
| `docs/implementation-summaries/` | Feature implementation details |
| `archived/docs/` | Archived/outdated documentation |

### Naming Conventions

- Use descriptive, kebab-case filenames (e.g., `deployment-guide.md`)
- Keep implementation summaries in past tense
- Prefix test/example files clearly for temporary files

---

## 🆘 Need Help?

- **For deployment issues**: Check [Deployment Guide Troubleshooting](DEPLOYMENT_GUIDE.md#troubleshooting)
- **For environment issues**: See [Environment Guide Troubleshooting](ENVIRONMENT_GUIDE.md#troubleshooting)
- **For security concerns**: Review [Security Guidelines](SECURITY.md)
- **For general questions**: Create an issue or check [Contributing Guide](../CONTRIBUTING.md)

---

**Last Updated**: December 2025  
**Maintained By**: ProjectMeats Development Team
