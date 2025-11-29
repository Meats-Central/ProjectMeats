# GitHub Actions Workflow Maintenance Checklist

## 🚨 Before Editing Workflows

- [ ] Read `docs/DEPLOYMENT_STABILITY_GUIDE.md`
- [ ] Understand heredoc escaping rules (see below)
- [ ] Have rollback plan ready

---

## ✅ Pre-Commit Checklist

### For ANY workflow changes:

1. **Validate YAML syntax:**
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('.github/workflows/11-dev-deployment.yml'))"
   ```

2. **Check heredoc escaping:**
   ```bash
   # Look for problematic patterns
   grep -n '\\$\$(' .github/workflows/11-dev-deployment.yml
   # Should return nothing! Use $(cmd) not \$(cmd)
   ```

3. **Test bash syntax locally:**
   ```bash
   # Test command substitution
   bash -c 'RESULT=$(echo "test"); echo $RESULT'
   
   # Test arithmetic
   bash -c 'COUNT=1; COUNT=$((COUNT + 1)); echo $COUNT'
   ```

4. **Dry-run workflow (if possible):**
   ```bash
   # Manual trigger to test
   gh workflow run 11-dev-deployment.yml --ref your-branch
   ```

---

## 🔍 Code Review Focus Areas

When reviewing workflow PRs, check:

### 1. Heredoc Escaping (CRITICAL!)

❌ **WRONG:**
```yaml
<<'SSH'
  HTTP_CODE=\$(curl ...)     # ❌ Syntax error!
  COUNT=\$((COUNT + 1))      # ❌ Syntax error!
SSH
```

✅ **CORRECT:**
```yaml
<<'SSH'
  HTTP_CODE=$(curl ...)      # ✅ Command substitution
  COUNT=$((\$COUNT + 1))     # ✅ Arithmetic expansion
  echo \$HOME                # ✅ Variable reference
SSH
```

### 2. Common Mistakes

- [ ] No `\$(` in quoted heredocs
- [ ] No `\$((` in quoted heredocs  
- [ ] Variables use `\$VAR` (with backslash)
- [ ] Secrets not hardcoded
- [ ] Error handling present (`|| exit 1`)

### 3. Security

- [ ] No secrets in logs
- [ ] Proper permission scopes
- [ ] SSH keys/passwords from secrets only
- [ ] No sensitive data in error messages

---

## 📋 Heredoc Escaping Quick Reference

### In `<<'SSH'` (Quoted Heredoc)

| Need | Syntax | Example |
|------|--------|---------|
| Variable | `\$VAR` | `echo \$HOME` |
| Command | `$(cmd)` | `RESULT=$(date)` |
| Arithmetic | `$((\$X + 1))` | `COUNT=$((\$COUNT + 1))` |
| Subshell | `(cmds)` | `(cd /tmp && ls)` |

**Rule:** Only escape `$` in simple variable references, NOT in `$(` or `$((`

---

## 🧪 Testing Workflow Changes

### 1. Local Syntax Test
```bash
# Create test script
cat > /tmp/test-heredoc.sh << 'TEST'
#!/bin/bash
ATTEMPT=1
MAX_ATTEMPTS=5
while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://example.com || echo "000")
  if [ "$HTTP_CODE" = "200" ]; then
    echo "Success"
    break
  fi
  echo "Attempt $ATTEMPT failed"
  ATTEMPT=$(($ATTEMPT + 1))
done
TEST

# Test it
bash /tmp/test-heredoc.sh
```

### 2. Branch Testing
```bash
# Push to feature branch first
git checkout -b test/workflow-change
git push -u origin test/workflow-change

# Trigger workflow on test branch
gh workflow run 11-dev-deployment.yml --ref test/workflow-change

# Monitor
gh run watch
```

### 3. Review Logs
```bash
# Get latest run
gh run list --workflow=11-dev-deployment.yml --limit 1

# View logs
gh run view <run-id> --log
```

---

## 🚑 Emergency Procedures

### If Deployment Fails After Merge

1. **Get failure details:**
   ```bash
   gh run list --workflow=11-dev-deployment.yml --limit 1 --json conclusion,url
   gh run view <run-id> --log-failed
   ```

2. **Quick diagnosis:**
   - **"syntax error near unexpected token"** → Heredoc escaping issue
   - **"Container failed to start"** → Environment/config issue
   - **"Health check failed"** → Application issue

3. **Immediate action:**
   ```bash
   # Revert the commit
   git revert <commit-sha>
   git push origin development
   
   # Or create hotfix
   git checkout -b hotfix/revert-workflow-change
   # Make fix
   git push -u origin hotfix/revert-workflow-change
   gh pr create --base development
   ```

4. **Escalate if:**
   - Not fixed within 15 minutes
   - Production is affected
   - Unclear root cause

---

## 📚 Additional Resources

- **Full Guide:** `docs/DEPLOYMENT_STABILITY_GUIDE.md`
- **Fix History:** `SDLC_LOOP_DEPLOYMENT_FIX.md`
- **Workflow File:** `.github/workflows/11-dev-deployment.yml`

---

## 💡 Pro Tips

1. **Always test locally first** - Run bash commands in a shell before putting in workflow
2. **Use shellcheck** - Install and run on extracted scripts
3. **Keep it simple** - Complex heredocs are error-prone; consider composite actions
4. **Document changes** - Explain WHY, not just WHAT
5. **Monitor first run** - Always watch the first deployment after changes

---

**Remember:** A failed deployment blocks the entire team. When in doubt, ask for review! 🤝

---

**Last Updated:** 2025-11-29  
**Maintained by:** DevOps Team
