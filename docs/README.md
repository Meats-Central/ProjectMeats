# ProjectMeats Documentation Hub

Welcome to the ProjectMeats documentation! This page serves as your central navigation point for all project documentation.

## 📚 Quick Links

### Getting Started
- **[Main README](../README.md)** - Project overview and quick setup
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project
- **[User Deployment Guide](../USER_DEPLOYMENT_GUIDE.md)** - Step-by-step deployment (30 minutes)

### Core Documentation

#### 🚀 Deployment & Infrastructure
- **[Environment Configuration Guide](ENVIRONMENT_GUIDE.md)** - Environment setup and configuration
- **[Deployment Guide](DEPLOYMENT_GUIDE.md)** - Comprehensive deployment documentation
- **[CI/CD Workflows](workflows/)** - GitHub Actions workflows and automation

#### 🔧 Development Guides
- **[Core Architecture](CORE_ARCHITECTURE.md)** - Core components and base models architecture
- **[UI/UX Enhancements](UI_UX_ENHANCEMENTS.md)** - UI/UX implementation guide
- **[TODO Log](TODO_LOG.md)** - Development progress and task tracking

## 📁 Documentation Structure

```
docs/
├── README.md (this file)              # Documentation navigation hub
├── CORE_ARCHITECTURE.md               # Core components and base models
├── ENVIRONMENT_GUIDE.md               # Environment configuration
├── DEPLOYMENT_GUIDE.md                # Comprehensive deployment guide
├── UI_UX_ENHANCEMENTS.md             # UI/UX implementation details
├── TODO_LOG.md                        # Development progress tracking
├── guides/                            # Step-by-step guides
├── workflows/                         # CI/CD workflow documentation
│   ├── unified-workflow.md           # Main unified workflow documentation
│   ├── cicd-infrastructure.md        # CI/CD infrastructure details
│   └── database-backup.md            # Database backup workflow
├── reference/                         # Reference documentation
│   ├── testing-deployment-monitor.md # Deployment monitoring testing
│   └── example-issue.md              # Example generated issue
├── troubleshooting/                   # Troubleshooting guides
├── implementation-summaries/          # Feature implementation summaries
│   ├── dashboard-enhancement.md      # Dashboard enhancements
│   └── allowed-hosts-fix.md          # ALLOWED_HOSTS configuration fix
├── templates/                         # Documentation templates
└── legacy/                            # Archived documentation
    ├── README.md                      # Legacy documentation index
    ├── DEPLOYMENT_GUIDE.md           # Legacy deployment guide
    ├── QUICK_SETUP.md                # Legacy quick setup
    └── production_checklist.md       # Legacy production checklist
```

## 🎯 Finding What You Need

### I want to...

**Deploy the application:**
- Start with [User Deployment Guide](../USER_DEPLOYMENT_GUIDE.md) for step-by-step instructions
- Reference [Environment Guide](ENVIRONMENT_GUIDE.md) for configuration details
- Check [Deployment Guide](DEPLOYMENT_GUIDE.md) for comprehensive information

**Set up my development environment:**
- Follow [Main README Quick Setup](../README.md#-quick-setup)
- Configure environment with [Environment Guide](ENVIRONMENT_GUIDE.md)
- Understand core models with [Core Architecture](CORE_ARCHITECTURE.md)

**Understand CI/CD workflows:**
- Read [Unified Workflow Documentation](workflows/unified-workflow.md)
- Review [CI/CD Infrastructure](workflows/cicd-infrastructure.md)
- Check [Database Backup Workflow](workflows/database-backup.md)

**Contribute to the project:**
- Read [Contributing Guide](../CONTRIBUTING.md)
- Review [TODO Log](TODO_LOG.md) for current tasks

**Troubleshoot issues:**
- Check relevant guide's troubleshooting section
- Review [legacy deployment guide](legacy/DEPLOYMENT_GUIDE.md#-troubleshooting) for detailed troubleshooting

**Learn about implemented features:**
- Browse [implementation summaries](implementation-summaries/)
- Review [UI/UX Enhancements](UI_UX_ENHANCEMENTS.md)

## 🔑 Documentation Principles

### Sources of Truth (Most Recent Updates)
Based on git history analysis (latest: 2025-10-05):

- **Deployment**: [USER_DEPLOYMENT_GUIDE.md](../USER_DEPLOYMENT_GUIDE.md) - Streamlined, tested deployment guide
- **CI/CD**: [Unified Workflow](workflows/unified-workflow.md) - Most comprehensive workflow documentation
- **Environment**: [ENVIRONMENT_GUIDE.md](ENVIRONMENT_GUIDE.md) - Centralized environment configuration
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- **Development Progress**: [TODO_LOG.md](TODO_LOG.md) - Current development status

### When Documentation Conflicts
If you find conflicting information:
1. Trust the source of truth listed above for each topic
2. Recent documentation (in main docs/ folder) supersedes legacy documentation
3. [USER_DEPLOYMENT_GUIDE.md](../USER_DEPLOYMENT_GUIDE.md) is the preferred deployment guide
4. Legacy documentation is preserved in `legacy/` for reference only

## 📝 Maintaining Documentation

### Documentation Location Guidelines
- **Root directory** (max 5 files): README.md, CONTRIBUTING.md, USER_DEPLOYMENT_GUIDE.md, and critical top-level docs
- **docs/** directory: All detailed documentation
- **docs/workflows/**: CI/CD and automation documentation
- **docs/implementation-summaries/**: Feature implementation details
- **docs/legacy/**: Archived/outdated documentation

### Naming Conventions
- Use descriptive, kebab-case filenames (e.g., `deployment-guide.md`)
- Keep implementation summaries in past tense (e.g., `dashboard-enhancement.md`)
- Prefix test/example files clearly (e.g., `example-issue.md`)

## 🆘 Need Help?

- **For deployment issues**: Check [Deployment Guide Troubleshooting](DEPLOYMENT_GUIDE.md#troubleshooting)
- **For environment issues**: See [Environment Guide Troubleshooting](ENVIRONMENT_GUIDE.md#troubleshooting)
- **For general questions**: Create an issue or check [Contributing Guide](../CONTRIBUTING.md)

---

**Last Updated**: January 2025  
**Maintained By**: ProjectMeats Development Team
