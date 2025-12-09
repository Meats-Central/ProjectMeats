#!/bin/bash
set -euo pipefail

echo "=================================================="
echo "CI/CD Pipeline Simplification - Cleanup Script"
echo "=================================================="
echo ""

# 1. Create Archive Directory
echo "Creating archive directory..."
mkdir -p .github/archived-workflows

# 2. Archive "Toy" Planner Workflows
echo "Archiving planner workflows..."
mv .github/workflows/31-planner-auto-add-issue.yml .github/archived-workflows/ 2>/dev/null || echo "  (31 not found)"
mv .github/workflows/32-planner-Auto-Assign-to-Copilot.yml .github/archived-workflows/ 2>/dev/null || echo "  (32 not found)"
mv .github/workflows/33-planner-review-and-test .github/archived-workflows/ 2>/dev/null || echo "  (33 not found)"
mv .github/workflows/34-planner-sprint-gen.yml .github/archived-workflows/ 2>/dev/null || echo "  (34 not found)"

# 3. Delete Redundant/Documentation Files in Workflows
echo "Removing documentation files from workflows directory..."
rm .github/workflows/FIX_HERE_DOC.md 2>/dev/null || echo "  (FIX_HERE_DOC.md not found)"
rm .github/workflows/WORKFLOW_MAINTENANCE_CHECKLIST.md 2>/dev/null || echo "  (WORKFLOW_MAINTENANCE_CHECKLIST.md not found)"

# 4. Archive Old "Per-Environment" Pipelines (Will be replaced by main-pipeline.yml)
echo "Archiving old per-environment deployment workflows..."
mv .github/workflows/11-dev-deployment.yml .github/archived-workflows/11-dev-deployment.yml.bak 2>/dev/null || echo "  (11-dev-deployment.yml not found)"
mv .github/workflows/12-uat-deployment.yml .github/archived-workflows/12-uat-deployment.yml.bak 2>/dev/null || echo "  (12-uat-deployment.yml not found)"
mv .github/workflows/13-prod-deployment.yml .github/archived-workflows/13-prod-deployment.yml.bak 2>/dev/null || echo "  (13-prod-deployment.yml not found)"
mv .github/workflows/promote-dev-to-uat.yml .github/archived-workflows/promote-dev-to-uat.yml.bak 2>/dev/null || echo "  (promote-dev-to-uat.yml not found)"
mv .github/workflows/promote-uat-to-main.yml .github/archived-workflows/promote-uat-to-main.yml.bak 2>/dev/null || echo "  (promote-uat-to-main.yml not found)"

echo ""
echo "=================================================="
echo "Cleanup Complete Summary"
echo "=================================================="
echo "✓ Planner workflows archived"
echo "✓ Documentation files removed"
echo "✓ Old deployment workflows archived"
echo ""
echo "Archived files location: .github/archived-workflows/"
echo ""
echo "Next Steps:"
echo "1. Create new workflows: reusable-deploy.yml and main-pipeline.yml"
echo "2. Test with workflow_dispatch before relying on automatic triggers"
echo "3. Update GitHub secrets for new workflow structure"
echo ""
