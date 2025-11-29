# PR Summary: Resolve Bash Here-Document Syntax Error in 11-dev-deployment.yml

## Title
**Resolve bash here-document syntax error in 11-dev-deployment.yml**

## Description

Addresses unexpected end-of-file error in temp script (line 60) due to missing/misplaced EOF delimiter in PostgreSQL/migration run step. 

### Root Cause
The dev deployment workflow failed with the following error:
```
/home/runner/work/_temp/cd4a59fa-cdde-415c-aaf0-8070f47de692.sh: line 59: warning: here-document at line 16 delimited by end-of-file (wanted `EOF')
/home/runner/work/_temp/cd4a59fa-cdde-415c-aaf0-8070f47de692.sh: line 60: syntax error: unexpected end of file
Error: Process completed with exit code 2.
```

**Failed Run**: https://github.com/Meats-Central/ProjectMeats/actions/runs/19728238551/job/56523744950

The issue occurred in the `test-backend` job, specifically in the "Setup tenant schemas and run tests" step. The script used a here-document (`<< 'EOF'`) to generate `/tmp/setup_tenant.py` for django-tenants tenant setup. However, due to YAML's literal block scalar indentation rules, the closing `EOF` delimiter was indented with spaces, preventing bash from recognizing it as the closing delimiter.

### Solution Implemented

**Refactored the script generation to eliminate the here-document entirely**, replacing it with a command group using multiple `echo` statements:

```bash
{
  echo "from apps.tenants.models import Client, Domain"
  echo "from django.db import connection"
  # ... more echo statements
} > /tmp/setup_tenant.py
```

This approach:
- ✅ Completely avoids the EOF delimiter recognition issue
- ✅ Maintains YAML validity (no unindented lines within block scalar)
- ✅ Generates identical Python script content
- ✅ More portable and easier to maintain
- ✅ Validated with bash syntax checker, YAML parser, and Python syntax validator

### Changes Made

1. **`.github/workflows/11-dev-deployment.yml`** (lines 442-500):
   - Added comment: `# Fixed unclosed here-document for bash syntax error`
   - Replaced `cat > /tmp/setup_tenant.py << 'EOF' ... EOF` with command group using echo statements
   - Removed now-unnecessary `sed` command that was stripping whitespace

2. **`.github/workflows/FIX_HERE_DOC.md`**:
   - Added comprehensive documentation explaining the issue and solution

### Testing & Validation

- ✅ YAML structure validated using Python's `yaml.safe_load()`
- ✅ Bash syntax validated using `bash -n`
- ✅ Generated Python script validated using `python -m py_compile`
- ✅ Existing YAML linter job (`lint-yaml`) already in workflow

### Impact

- **Minimal changes**: Only modified the problematic script generation section
- **No functional changes**: Generates identical Python script and behavior
- **No breaking changes**: Preserves all existing logic and compatibility
- **Resolves blocked deployments**: Fixes the failing dev deployment workflow

### Compatibility

- ✅ Django 4.2.7
- ✅ PostgreSQL 14/15
- ✅ django-tenants (multi-tenancy)
- ✅ Python 3.12
- ✅ GitHub Actions workflow syntax

### References

- Bash here-document documentation: https://www.gnu.org/software/bash/manual/html_node/Redirections.html
- YAML literal block scalars: https://yaml.org/spec/1.2.2/#812-literal-style
- Original workflow file: https://github.com/Meats-Central/ProjectMeats/blob/ead7486f3d4dee80b67122c6832a0d982b34fca7/.github/workflows/11-dev-deployment.yml

---

**Note**: This PR follows Google monorepo guidelines and repository standards for minimal, surgical changes to resolve the specific issue without introducing unrelated modifications.
