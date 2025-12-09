# Deployment Quick Reference

**🏆 GOLDEN STATE REFERENCE:** See `GOLDEN_PIPELINE_REFERENCE.md` for complete verified working configuration.

## Quick Links

- **Golden Pipeline Reference:** [GOLDEN_PIPELINE_REFERENCE.md](./GOLDEN_PIPELINE_REFERENCE.md) - ⭐ PRIMARY REFERENCE
- **Branch Workflow:** [branch-workflow-checklist.md](./branch-workflow-checklist.md)
- **Archived Docs:** [archived/old-deployment-docs/](./archived/old-deployment-docs/)

## TL;DR

```bash
# Verify you're on correct versions
cd frontend && npm list react react-dom
# Should show: react@18.2.0, react-dom@18.2.0

# Deploy flow
feature → development → UAT → production
```

## Critical Success Factors

1. **React version MUST be 18.2.0** (not 19.x)
2. **Always use `npm ci`** (not `npm install`)
3. **Follow branch flow** (never push directly to main/uat)
4. **Job name is `migrate`** (not `run-migrations`)

## When Things Break

1. Compare your branch against `main` commit `880eff8e`
2. Check frontend/package.json dependencies
3. Verify workflow job names match
4. See troubleshooting in GOLDEN_PIPELINE_REFERENCE.md

---

**Last successful E2E deployment:** 2025-12-04 09:11-09:29 UTC  
**Golden commit:** 880eff8e (main), 0e54bc2a (uat), 68a661c4 (dev)
