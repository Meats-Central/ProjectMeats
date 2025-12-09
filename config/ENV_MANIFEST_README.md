# Environment Manifest System (v3.0)

**Single Source of Truth for Environment Variables and Secret Mapping**

## Overview

The Environment Manifest System provides explicit mapping between runtime variables and GitHub Secrets, eliminating guesswork and preventing deployment failures caused by inconsistent naming conventions.

## Key Files

- **`config/env.manifest.json`** - The authoritative source for all environment variable and secret mappings
- **`config/manage_env.py`** - Management tool with audit capabilities
- **`.github/ai-context/env-handling.md`** - Detailed guide for AI agents and developers

## Quick Start

### View All Secrets Mapping
```bash
cat config/env.manifest.json | jq '.variables'
```

### Audit Secret Health
```bash
python config/manage_env.py audit
```

This command:
- ✅ Retrieves secrets from GitHub (requires `gh` CLI)
- ✅ Compares against manifest definitions
- 🧟 Reports **Zombie Secrets** (in GitHub, not in manifest)
- ❌ Reports **Missing Secrets** (in manifest, not in GitHub)

### Example Audit Output
```
======================================================================
🔍 ENVIRONMENT MANIFEST AUDIT
======================================================================
✓ Loaded manifest v3.0
✓ Retrieved 25 secrets from GitHub
✓ Extracted 22 expected secrets from manifest

======================================================================
🧟 ZOMBIE SECRETS (In GitHub, NOT in manifest):
----------------------------------------------------------------------
  • DEPRECATED_OLD_SECRET
  • TEMP_TEST_SECRET

Total: 2 zombie secret(s)

======================================================================
❌ MISSING SECRETS (In manifest, NOT in GitHub):
----------------------------------------------------------------------
  • PROD_NEW_FEATURE_KEY

Total: 1 missing secret(s)

======================================================================
⚠️  AUDIT INCOMPLETE: Discrepancies found
   - 2 zombie secret(s) should be removed or added to manifest
   - 1 missing secret(s) must be added to GitHub
```

## Manifest Structure

### Environment Definitions
```json
{
  "environments": {
    "dev-backend": {
      "type": "backend",
      "prefix": "DEV",
      "django_settings": "projectmeats.settings.development"
    },
    "dev-frontend": {
      "type": "frontend",
      "prefix": "DEV",
      "url": "https://dev.meatscentral.com"
    }
  }
}
```

### Variable Categories
- **`infrastructure`**: Server, SSH, database host configuration
- **`application`**: Application-level secrets (DB connection, secret keys)
- **`frontend_runtime`**: Frontend environment variables

### Secret Mapping Types

#### 1. Explicit Mapping (Recommended)
Use when naming is inconsistent:

```json
"BASTION_HOST": {
  "description": "Droplet IP",
  "ci_secret_mapping": {
    "dev-backend": "DEV_HOST",
    "uat2-backend": "UAT_HOST",
    "prod2-backend": "PROD_HOST"
  }
}
```

**In Workflow:**
```yaml
- name: Deploy Dev Backend
  env:
    HOST: ${{ secrets.DEV_HOST }}  # Exact name from manifest

- name: Deploy UAT Backend
  env:
    HOST: ${{ secrets.UAT_HOST }}  # Different name per environment
```

#### 2. Pattern-Based Mapping
Use when naming follows consistent pattern:

```json
"SECRET_KEY": {
  "ci_secret_pattern": "{PREFIX}_SECRET_KEY",
  "required": true
}
```

**Expands to:**
- `DEV_SECRET_KEY`
- `UAT_SECRET_KEY`
- `PROD_SECRET_KEY`

**In Workflow:**
```yaml
- name: Deploy
  env:
    SECRET_KEY: ${{ secrets[format('{0}_SECRET_KEY', matrix.prefix)] }}
```

#### 3. Computed Values
Use for values derived from environment configuration:

```json
"DJANGO_SETTINGS_MODULE": {
  "description": "Settings path (Injected via env var, mapped from manifest)",
  "value_source": "environment_config"
}
```

**Value comes from `environments.*.django_settings` in manifest.**

## Legacy Naming Conventions

⚠️ **ProjectMeats has intentional inconsistencies:**

### SSH Password (Shared vs Unique)
```json
"BASTION_SSH_PASSWORD": {
  "description": "SSH Password (Legacy Shared Secret for UAT/Prod)",
  "ci_secret_mapping": {
    "dev-backend": "DEV_SSH_PASSWORD",  // Unique
    "uat2-backend": "SSH_PASSWORD",      // Shared
    "prod2-backend": "SSH_PASSWORD"      // Shared (same as UAT)
  }
}
```

**Why?** Historical reasons. UAT and Prod share infrastructure.

### Frontend Variables (Same Name, Different Values)
```json
"REACT_APP_API_BASE_URL": {
  "ci_secret_pattern": "REACT_APP_API_BASE_URL",
  "description": "API URL (Must be defined in each *-frontend environment)"
}
```

**GitHub Configuration:**
- Secret name: `REACT_APP_API_BASE_URL`
- Different values per environment scope (dev-frontend, uat2-frontend, prod2-frontend)

## Common Workflows

### Adding New Secrets

1. **Update Manifest:**
   ```bash
   vim config/env.manifest.json
   ```
   
   Add to appropriate category:
   ```json
   "NEW_API_KEY": {
     "description": "Third-party API key",
     "ci_secret_mapping": {
       "dev-backend": "DEV_NEW_API_KEY",
       "uat2-backend": "UAT_NEW_API_KEY",
       "prod2-backend": "PROD_NEW_API_KEY"
     }
   }
   ```

2. **Add Secrets to GitHub:**
   ```bash
   gh secret set DEV_NEW_API_KEY --body "dev-key-value"
   gh secret set UAT_NEW_API_KEY --body "uat-key-value"
   gh secret set PROD_NEW_API_KEY --body "prod-key-value"
   ```

3. **Verify:**
   ```bash
   python config/manage_env.py audit
   ```

4. **Update Workflows:**
   ```yaml
   env:
     NEW_API_KEY: ${{ secrets.DEV_NEW_API_KEY }}
   ```

### Cleaning Up Zombie Secrets

1. **Run Audit:**
   ```bash
   python config/manage_env.py audit
   ```

2. **Review Zombies:**
   - If still needed → Add to manifest
   - If obsolete → Remove from GitHub

3. **Remove from GitHub:**
   ```bash
   gh secret remove ZOMBIE_SECRET_NAME
   ```

4. **Verify:**
   ```bash
   python config/manage_env.py audit
   ```

### Resolving Missing Secrets

1. **Run Audit:**
   ```bash
   python config/manage_env.py audit
   ```

2. **Add Missing Secrets:**
   ```bash
   gh secret set MISSING_SECRET_NAME --body "secret-value"
   ```

3. **Verify:**
   ```bash
   python config/manage_env.py audit
   ```

## Integration with CI/CD

### Before Deployment
```yaml
- name: Audit Secrets
  run: python config/manage_env.py audit
```

### In Deployment Workflows
```yaml
# ✅ CORRECT: Use exact secret name from manifest
- name: Deploy Backend
  environment: uat2-backend
  env:
    HOST: ${{ secrets.UAT_HOST }}              # From manifest
    USER: ${{ secrets.UAT_USER }}              # From manifest
    SSH_PASSWORD: ${{ secrets.SSH_PASSWORD }}  # Shared (UAT/Prod)
    DATABASE_URL: ${{ secrets.UAT_DATABASE_URL }}

# ❌ WRONG: Guessing names
- name: Deploy Backend
  env:
    HOST: ${{ secrets.UAT2_HOST }}  # Does not exist!
```

## Troubleshooting

### "Secret not found" Error in Workflow

1. Find environment in manifest (e.g., `uat2-backend`)
2. Locate variable (e.g., `BASTION_HOST`)
3. Use exact name from `ci_secret_mapping`: `UAT_HOST`

### GitHub CLI Not Found

Install GitHub CLI:
```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate
gh auth login
```

### Audit Shows False Positives

Some secrets may be infrastructure-level and not in manifest:
- `GITHUB_TOKEN` (automatic)
- `ACTIONS_*` (GitHub Actions system secrets)
- Repository-level secrets used across multiple projects

**Action:** Add these to manifest if they're project-specific, or document them separately.

## Best Practices

### ✅ DO
- Always check manifest before adding workflow secrets
- Run audit after secret changes
- Use explicit mappings for clarity
- Document legacy naming in manifest descriptions
- Keep manifest in sync with GitHub

### ❌ DON'T
- Guess secret names from patterns
- Assume consistent naming conventions
- Skip audit before deployments
- Hardcode secret names in workflows without checking manifest
- Create secrets without updating manifest first

## References

- **Manifest**: `config/env.manifest.json`
- **AI Context**: `.github/ai-context/env-handling.md`
- **Copilot Instructions**: `.github/copilot-instructions.md` (Secret Management section)
- **Management Tool**: `config/manage_env.py`

## Version History

- **v3.0** - Added frontend support, explicit legacy mapping, audit command
- **v2.x** - Pattern-based secrets (deprecated)
- **v1.x** - Initial environment configuration system
