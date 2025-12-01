# ProjectMeats Documentation Hub

**Last Updated**: November 29, 2024  
Welcome to the ProjectMeats documentation! This page serves as your central navigation point for all project documentation.

> **Note**: We recently consolidated 67+ scattered documentation files into comprehensive guides. See [archived-2024-11/](archived-2024-11/) for historical reference.

## 📚 Quick Links

### Getting Started
- **[Main README](../README.md)** - Project overview and quick setup
- **[Quick Start Guide](../QUICK_START.md)** - 5-minute setup guide
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project

### Essential Guides (NEW - Consolidated)
- **[Migration Guide](MIGRATION_GUIDE.md)** ⭐ - Complete database migration guide with django-tenants
- **[Authentication Guide](AUTHENTICATION_GUIDE.md)** ⭐ - Authentication, permissions, and superuser management
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** ⭐ - Common issues and solutions
- **[3-Month Retrospective](lessons-learned/3-MONTH-RETROSPECTIVE.md)** ⭐ - Lessons learned and best practices

### Core Documentation

#### 🚀 Deployment & Infrastructure
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation
- **[Environment Configuration Guide](ENVIRONMENT_GUIDE.md)** - Environment setup and configuration
- **[Multi-Tenancy Guide](MULTI_TENANCY_GUIDE.md)** - Multi-tenancy architecture and setup
- **[CI/CD Workflows](workflows/)** - GitHub Actions workflows and automation

#### 🔧 Development Guides
- **[Developer Workflows](../DEVELOPER_WORKFLOWS.md)** ⭐ - Builds, tests, debugging workflows (NEW)
- **[Backend Architecture](BACKEND_ARCHITECTURE.md)** - Django backend structure and patterns
- **[Frontend Architecture](FRONTEND_ARCHITECTURE.md)** - React frontend structure and components
- **[Testing Strategy](TESTING_STRATEGY.md)** - Comprehensive testing guide
- **[Repository Best Practices](REPOSITORY_BEST_PRACTICES.md)** - Development workflow and standards
- **[Branch Workflow](../branch-workflow-checklist.md)** - Branch naming and workflow guide

#### 📋 Repository Maintenance
- **[Platform Core Components Audit](REPO_AUDIT_PLATFORM_CORE.md)** - Comprehensive repository audit report
- **[Cleanup Checklist](CLEANUP_CHECKLIST.md)** - Actionable cleanup tasks from audit
- **[Archived Documentation](archived-2024-11/)** - Historical documentation (Nov 2024 consolidation)

## 📁 Documentation Structure

```
docs/
├── README.md (this file)              # Documentation navigation hub
│
├── MIGRATION_GUIDE.md ⭐              # Complete database migration guide (NEW)
├── AUTHENTICATION_GUIDE.md ⭐         # Auth & permissions guide (NEW)
├── TROUBLESHOOTING.md ⭐              # Common issues and solutions (NEW)
│
├── BACKEND_ARCHITECTURE.md            # Django backend architecture and patterns
├── FRONTEND_ARCHITECTURE.md           # React frontend architecture and components
├── TESTING_STRATEGY.md                # Comprehensive testing guide
├── REPOSITORY_BEST_PRACTICES.md       # Development workflow and standards
├── ENVIRONMENT_GUIDE.md               # Environment configuration
├── DEPLOYMENT_GUIDE.md                # Comprehensive deployment guide
├── MULTI_TENANCY_GUIDE.md            # Multi-tenancy architecture
├── MIGRATION_BEST_PRACTICES.md       # Migration best practices
├── DATA_GUIDE.md                      # Data model documentation
├── UI_UX_ENHANCEMENTS.md             # UI/UX implementation
├── TODO_LOG.md                        # Development progress tracking
├── REPO_AUDIT_PLATFORM_CORE.md       # Repository audit report
├── CLEANUP_CHECKLIST.md              # Repository cleanup tasks
│
├── lessons-learned/                   # Lessons learned and retrospectives
│   └── 3-MONTH-RETROSPECTIVE.md ⭐   # Aug-Nov 2024 retrospective (NEW)
│
├── workflows/                         # CI/CD workflow documentation
│   ├── unified-workflow.md           # Main workflow documentation
│   ├── cicd-infrastructure.md        # CI/CD infrastructure
│   └── database-backup.md            # Database backup workflow
│
├── implementation-summaries/          # Feature implementation summaries
│   ├── dashboard-enhancement.md      # Dashboard enhancements
│   ├── deployment-optimization.md    # Deployment improvements
│   └── allowed-hosts-fix.md          # Configuration fixes
│
├── reference/                         # Reference documentation
│   └── environment-variables.md      # Environment variables reference
│
├── research/                          # Research and planning docs
│
└── archived-2024-11/ ⭐               # Archived documentation (NEW)
    ├── README.md                      # Archive index and migration guide
    ├── deployment/                    # (2 archived deployment docs)
    ├── migration/                     # (12 archived migration docs)
    ├── authentication/                # (13 archived auth docs)
    ├── multi-tenancy/                 # (10 archived tenant docs)
    ├── implementation/                # (10 archived implementation docs)
    ├── troubleshooting/               # (14 archived fix docs)
    ├── guest-mode/                    # (2 archived guest docs)
    └── other/                         # (3 archived misc docs)
```

### What's New? (November 2024 Consolidation)

✨ **4 New Comprehensive Guides**:
- `MIGRATION_GUIDE.md` - Consolidates 12 migration documents
- `AUTHENTICATION_GUIDE.md` - Consolidates 13 auth documents
- `TROUBLESHOOTING.md` - Consolidates 14 troubleshooting documents
- `lessons-learned/3-MONTH-RETROSPECTIVE.md` - 3-month development summary

📦 **67 Files Archived**: All redundant documentation moved to `archived-2024-11/` with complete cross-references.

## 🎯 Finding What You Need

### I want to...

**Fix a database migration issue:**
- Check [Migration Guide](MIGRATION_GUIDE.md) for comprehensive migration patterns
- See [Troubleshooting Guide](TROUBLESHOOTING.md) for common migration problems

**Set up authentication or manage users:**
- Read [Authentication Guide](AUTHENTICATION_GUIDE.md) for complete auth system
- Learn about superuser management and environment-specific credentials

**Understand what happened in the last 3 months:**
- Read [3-Month Retrospective](lessons-learned/3-MONTH-RETROSPECTIVE.md) for lessons learned
- Review key improvements and recommendations

**Deploy the application:**
- Start with [Deployment Guide](DEPLOYMENT_GUIDE.md) for comprehensive deployment instructions
- Reference [Environment Guide](ENVIRONMENT_GUIDE.md) for configuration details
- Check [Troubleshooting Guide](TROUBLESHOOTING.md) for deployment issues

**Set up my development environment:**
- Follow [Main README Quick Setup](../README.md#-quick-setup)
- Configure environment with [Environment Guide](ENVIRONMENT_GUIDE.md)
- Check [Migration Guide](MIGRATION_GUIDE.md) for database setup
- Reference [Developer Workflows](../DEVELOPER_WORKFLOWS.md) for builds, tests, and debugging

**Run tests or debug code:**
- Check [Developer Workflows](../DEVELOPER_WORKFLOWS.md) for testing and debugging commands
- Read [Testing Strategy](TESTING_STRATEGY.md) for comprehensive testing guide
- See [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues

**Understand multi-tenancy:**
- Read [Multi-Tenancy Guide](MULTI_TENANCY_GUIDE.md) for architecture overview
- See [Migration Guide](MIGRATION_GUIDE.md) for django-tenants migration patterns

**Debug an issue:**
- Start with [Troubleshooting Guide](TROUBLESHOOTING.md) - covers most common issues
- Check [Migration Guide](MIGRATION_GUIDE.md) for database-specific issues
- See [Authentication Guide](AUTHENTICATION_GUIDE.md) for auth-related problems

**Understand CI/CD workflows:**
- Read [Unified Workflow Documentation](workflows/unified-workflow.md)
- Review [CI/CD Infrastructure](workflows/cicd-infrastructure.md)
- Check [Database Backup Workflow](workflows/database-backup.md)

**Contribute to the project:**
- Read [Contributing Guide](../CONTRIBUTING.md)
- Review [Branch Workflow Checklist](../branch-workflow-checklist.md)
- Check [Repository Best Practices](REPOSITORY_BEST_PRACTICES.md)

**Find old documentation:**
- Browse [Archived Documentation](archived-2024-11/) for historical reference
- Read [Archive README](archived-2024-11/README.md) for migration guide

**Troubleshoot issues:**
- Check relevant guide's troubleshooting section
- Review [archived deployment guide](../archived/docs/DEPLOYMENT_GUIDE.md#-troubleshooting) for detailed troubleshooting

**Learn about implemented features:**
- Browse [implementation summaries](implementation-summaries/)
- Review [UI/UX Enhancements](UI_UX_ENHANCEMENTS.md)

## 🔑 Documentation Principles

### Sources of Truth (Most Recent Updates)
Based on git history analysis (latest: 2025-10-05):

- **Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Comprehensive deployment guide
- **CI/CD**: [Unified Workflow](workflows/unified-workflow.md) - Most comprehensive workflow documentation
- **Environment**: [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) - Centralized environment configuration
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- **Development Progress**: [TODO_LOG.md](TODO_LOG.md) - Current development status

### When Documentation Conflicts
If you find conflicting information:
1. Trust the source of truth listed above for each topic
2. Recent documentation (in main docs/ folder) supersedes archived documentation
3. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) is the preferred deployment guide
4. Archived documentation is preserved in `archived/docs/` for reference only

## 📝 Maintaining Documentation

### Documentation Location Guidelines
- **Root directory** (max 5 files): README.md, CONTRIBUTING.md, and critical top-level docs
- **docs/** directory: All detailed documentation
- **docs/workflows/**: CI/CD and automation documentation
- **docs/implementation-summaries/**: Feature implementation details
- **archived/docs/**: Archived/outdated documentation (in root/archived/)

### Naming Conventions
- Use descriptive, kebab-case filenames (e.g., `deployment-guide.md`)
- Keep implementation summaries in past tense (e.g., `dashboard-enhancement.md`)
- Prefix test/example files clearly for temporary files

## 🆘 Need Help?

- **For deployment issues**: Check [Deployment Guide Troubleshooting](DEPLOYMENT_GUIDE.md#troubleshooting)
- **For environment issues**: See [Environment Guide Troubleshooting](ENVIRONMENT_GUIDE.md#troubleshooting)
- **For general questions**: Create an issue or check [Contributing Guide](../CONTRIBUTING.md)

---

**Last Updated**: January 2025  
**Maintained By**: ProjectMeats Development Team
