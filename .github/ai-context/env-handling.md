# AI Context: Environment & Secret Management

**SOURCE OF TRUTH:** `config/env.manifest.json`

## Rules for AI & Developers

### 1. No Guessing
- **Do not infer secret names from prefixes**
- Always use the exact `ci_secret_mapping` defined in `config/env.manifest.json`
- If a secret mapping is not explicitly defined, it does not exist

### 2. Legacy Handling
- `SSH_PASSWORD` is **shared** between UAT and Production environments
- `DEV_SSH_PASSWORD` is **unique** to the Development environment
- This inconsistency is intentional and documented in the manifest

### 3. Frontend Environment Variables
- `REACT_APP_API_BASE_URL` has the **same name** across all environments
- Each environment (dev-frontend, uat2-frontend, prod2-frontend) has **different values**
- The secret is environment-scoped in GitHub Actions

### 4. Pattern-Based Secrets
Some secrets use patterns with `{PREFIX}` substitution:
- `{PREFIX}_SECRET_KEY` → `DEV_SECRET_KEY`, `UAT_SECRET_KEY`, `PROD_SECRET_KEY`
- `{PREFIX}_DB_HOST` → `DEV_DB_HOST`, `UAT_DB_HOST`, `PROD_DB_HOST`

### 5. Value Sources
Variables have different sources:
- **`ci_secret_mapping`**: Explicit mapping to GitHub secret names
- **`ci_secret_pattern`**: Pattern-based naming using environment prefix
- **`value_source: environment_config`**: Derived from manifest environment configuration

## How to Use the Manifest

### For Workflow Files
```yaml
# ✅ CORRECT: Use exact secret name from manifest
env:
  SSH_PASSWORD: ${{ secrets.SSH_PASSWORD }}  # For UAT/Prod
  SSH_PASSWORD: ${{ secrets.DEV_SSH_PASSWORD }}  # For Dev

# ❌ WRONG: Guessing or inferring names
env:
  SSH_PASSWORD: ${{ secrets.UAT_SSH_PASSWORD }}  # Does not exist!
```

### For Secret Audits
```bash
# Run the audit command to find zombie and missing secrets
python config/manage_env.py audit
```

### For Documentation
When documenting environment setup:
1. Reference the manifest as the authoritative source
2. Copy exact secret names from the manifest
3. Note any legacy patterns explicitly

## Manifest Structure

### Environment Definitions
Each environment has:
- `type`: backend or frontend
- `prefix`: Used for pattern-based secret names
- `django_settings`: (Backend only) Django settings module path
- `url`: (Frontend only) Deployment URL

### Variable Categories
- **`infrastructure`**: Server, SSH, database host configuration
- **`application`**: Application-level secrets (DB connection, secret keys)
- **`frontend_runtime`**: Frontend environment variables

### Secret Mapping Types
1. **Explicit Mapping** (`ci_secret_mapping`):
   ```json
   "ci_secret_mapping": {
     "dev-backend": "DEV_HOST",
     "uat2-backend": "UAT_HOST"
   }
   ```

2. **Pattern-Based** (`ci_secret_pattern`):
   ```json
   "ci_secret_pattern": "{PREFIX}_SECRET_KEY"
   ```

3. **Computed** (`value_source`):
   ```json
   "value_source": "environment_config"
   ```

## Troubleshooting

### Secret Not Found in GitHub
1. Check the manifest for the exact secret name
2. Run `python config/manage_env.py audit` to see missing secrets
3. Add the secret to GitHub with the exact name from the manifest

### Workflow Using Wrong Secret
1. Find the environment in the manifest (e.g., `uat2-backend`)
2. Locate the variable (e.g., `BASTION_HOST`)
3. Use the exact secret name from `ci_secret_mapping` (e.g., `UAT_HOST`)

### Adding New Secrets
1. Add to `config/env.manifest.json` first
2. Choose appropriate mapping type (explicit, pattern, or computed)
3. Update workflows to reference the manifest
4. Add the actual secret to GitHub
5. Run audit to verify

## Why This System Exists

ProjectMeats has evolved over time, resulting in:
- Inconsistent naming conventions (`DEV_SSH_PASSWORD` vs `SSH_PASSWORD`)
- Shared secrets across environments (UAT/Prod SSH password)
- Multiple environment types (backend vs frontend)
- Pattern-based naming that isn't always followed

The manifest explicitly documents **what actually exists**, not what "should" exist, eliminating guesswork and preventing deployment failures.
