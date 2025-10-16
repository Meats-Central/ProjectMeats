# ProjectMeats Documentation Hub

Welcome to the ProjectMeats documentation! This page serves as your central navigation point for all project documentation.

## 📚 Quick Links

### Getting Started
- **[Main README](../README.md)** - Project overview and quick setup
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation

### Core Documentation

#### 🚀 Deployment & Infrastructure
- **[Environment Configuration Guide](ENVIRONMENT_GUIDE.md)** - Environment setup and configuration
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation
- **[CI/CD Workflows](workflows/)** - GitHub Actions workflows and automation

#### 🔧 Development Guides
- **[Backend Architecture](BACKEND_ARCHITECTURE.md)** - Django backend structure and patterns
- **[Frontend Architecture](FRONTEND_ARCHITECTURE.md)** - React frontend structure and components
- **[Testing Strategy](TESTING_STRATEGY.md)** - Comprehensive testing guide
- **[Repository Best Practices](REPOSITORY_BEST_PRACTICES.md)** - Development workflow and standards
- **[Multi-Tenancy Guide](MULTI_TENANCY_GUIDE.md)** - Multi-tenancy implementation and usage
- **[UI/UX Enhancements](UI_UX_ENHANCEMENTS.md)** - UI/UX implementation guide
- **[TODO Log](TODO_LOG.md)** - Development progress and task tracking

#### 📋 Repository Maintenance
- **[Platform Core Components Audit](REPO_AUDIT_PLATFORM_CORE.md)** - Comprehensive repository audit report
- **[Cleanup Checklist](CLEANUP_CHECKLIST.md)** - Actionable cleanup tasks from audit

## 📁 Documentation Structure

```
docs/
├── README.md (this file)              # Documentation navigation hub
├── BACKEND_ARCHITECTURE.md            # Django backend architecture and patterns
├── FRONTEND_ARCHITECTURE.md           # React frontend architecture and components
├── TESTING_STRATEGY.md                # Comprehensive testing guide and best practices
├── REPOSITORY_BEST_PRACTICES.md       # Development workflow, code quality, and standards
├── ENVIRONMENT_GUIDE.md               # Environment configuration
├── DEPLOYMENT_GUIDE.md                # Comprehensive deployment guide
├── UI_UX_ENHANCEMENTS.md             # UI/UX implementation details
├── TODO_LOG.md                        # Development progress tracking
├── REPO_AUDIT_PLATFORM_CORE.md       # Platform core components audit
├── CLEANUP_CHECKLIST.md              # Repository cleanup tasks
├── guides/                            # Step-by-step guides
├── workflows/                         # CI/CD workflow documentation
│   ├── unified-workflow.md           # Main unified workflow documentation
│   ├── cicd-infrastructure.md        # CI/CD infrastructure details
│   └── database-backup.md            # Database backup workflow
├── reference/                         # Reference documentation
├── troubleshooting/                   # Troubleshooting guides
├── implementation-summaries/          # Feature implementation summaries
│   ├── dashboard-enhancement.md      # Dashboard enhancements
│   ├── dashboard-enhancement-issue.md # Dashboard enhancement issue details
│   ├── allowed-hosts-fix.md          # ALLOWED_HOSTS configuration fix
│   ├── multi-tenancy-implementation.md  # Multi-tenancy feature implementation
│   ├── data-model-enhancement.md     # Data model enhancements
│   ├── platform-core-refactoring.md  # Platform core components refactoring
│   ├── deployment-optimization.md    # Deployment optimizations
│   └── repository-refactoring-phase-1.md  # Repository refactoring phase 1
└── templates/                         # Documentation templates

archived/docs/                          # Archived documentation (in root/archived/)
├── README.md                          # Legacy documentation index
├── DEPLOYMENT_GUIDE.md               # Legacy deployment guide
├── QUICK_SETUP.md                    # Legacy quick setup
├── production_checklist.md           # Legacy production checklist
├── copilot-instructions.md           # Outdated Copilot instructions
├── copilot-log.md                    # Outdated Copilot log
└── DATA_MODEL_ENHANCEMENTS.md        # Superseded by implementation summary
```

## 🎯 Finding What You Need

### I want to...

**Deploy the application:**
- Start with [Deployment Guide](DEPLOYMENT_GUIDE.md) for comprehensive deployment instructions
- Reference [Environment Guide](ENVIRONMENT_GUIDE.md) for configuration details

**Set up my development environment:**
- Follow [Main README Quick Setup](../README.md#-quick-setup)
- Configure environment with [Environment Guide](ENVIRONMENT_GUIDE.md)

**Understand CI/CD workflows:**
- Read [Unified Workflow Documentation](workflows/unified-workflow.md)
- Review [CI/CD Infrastructure](workflows/cicd-infrastructure.md)
- Check [Database Backup Workflow](workflows/database-backup.md)

**Contribute to the project:**
- Read [Contributing Guide](../CONTRIBUTING.md)
- Review [TODO Log](TODO_LOG.md) for current tasks

**Maintain the repository:**
- Review [Repository Audit Report](REPO_AUDIT_PLATFORM_CORE.md)
- Follow [Cleanup Checklist](CLEANUP_CHECKLIST.md)

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
