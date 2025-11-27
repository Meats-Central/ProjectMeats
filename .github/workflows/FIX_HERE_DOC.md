# Bash Here-Document Fix in Dev Deployment Workflow

## Problem
The dev deployment workflow (`11-dev-deployment.yml`) had a bash syntax error caused by an unclosed here-document in the `test-backend` job. The here-document used `<< 'EOF'` to create a Python script, but the closing `EOF` delimiter was indented with spaces (due to YAML's literal block scalar indentation), which prevented bash from recognizing it as the closing delimiter.

## Solution
Refactored the script generation to use a command group with multiple `echo` statements instead of a here-document:
```bash
{
  echo "line 1"
  echo "line 2"
  ...
} > /tmp/setup_tenant.py
```

This approach:
- Avoids the EOF delimiter recognition issue entirely
- Maintains YAML validity (no unindented lines within the block scalar)
- Generates the same Python script content
- Is more portable and easier to maintain

## Testing
- Validated YAML structure using Python's yaml module
- Validated bash syntax using `bash -n`
- Validated generated Python syntax using `python -m py_compile`

## References
- GitHub Actions run with error: https://github.com/Meats-Central/ProjectMeats/actions/runs/19728238551/job/56523744950
- Bash here-document documentation: https://www.gnu.org/software/bash/manual/html_node/Redirections.html
