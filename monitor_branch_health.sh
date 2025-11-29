#!/bin/bash
# Branch Health Monitoring Script
# Usage: ./monitor_branch_health.sh

set -e

OWNER="Meats-Central"
REPO="ProjectMeats"

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║             ProjectMeats Branch Health Monitor                           ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📅 Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Fetch latest
echo "🔄 Fetching latest changes..."
git fetch origin --quiet

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 BRANCH DIVERGENCE CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check main ahead of development
MAIN_AHEAD=$(git log development..origin/main --oneline 2>/dev/null | wc -l | tr -d ' ')
echo "🔍 Main ahead of development: $MAIN_AHEAD commits"

if [ "$MAIN_AHEAD" -eq 0 ]; then
    echo "   ✅ GOOD: No divergence"
elif [ "$MAIN_AHEAD" -le 3 ]; then
    echo "   ⚠️  WARNING: Minor divergence (acceptable during hotfix window)"
else
    echo "   ❌ ERROR: Significant divergence detected!"
    echo "   Action required: Create sync PR from main to development"
fi

echo ""

# Check UAT ahead of development
UAT_AHEAD=$(git log development..origin/uat --oneline 2>/dev/null | wc -l | tr -d ' ')
echo "🔍 UAT ahead of development: $UAT_AHEAD commits"

if [ "$UAT_AHEAD" -eq 0 ]; then
    echo "   ✅ GOOD: No divergence"
elif [ "$UAT_AHEAD" -le 5 ]; then
    echo "   ✅ ACCEPTABLE: Normal promotion window"
else
    echo "   ⚠️  WARNING: Large divergence (review needed)"
fi

echo ""

# Check main ahead of UAT
MAIN_AHEAD_UAT=$(git log origin/uat..origin/main --oneline 2>/dev/null | wc -l | tr -d ' ')
echo "🔍 Main ahead of UAT: $MAIN_AHEAD_UAT commits"

if [ "$MAIN_AHEAD_UAT" -eq 0 ]; then
    echo "   ✅ GOOD: No divergence"
elif [ "$MAIN_AHEAD_UAT" -le 5 ]; then
    echo "   ✅ ACCEPTABLE: Normal promotion window"
else
    echo "   ⚠️  WARNING: Large divergence (review needed)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛡️  BRANCH PROTECTION STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check rulesets
echo "📋 Checking repository rulesets..."
RULESETS=$(gh api repos/$OWNER/$REPO/rulesets --jq '.[] | select(.enforcement == "active") | {name: .name, branches: .conditions.ref_name.include}' 2>&1)

if [ $? -eq 0 ]; then
    echo "$RULESETS" | jq -r 'select(.branches != null) | "   ✅ Ruleset: \(.name) protecting \(.branches | join(", "))"'
else
    echo "   ⚠️  Unable to check protection status (may need admin permissions)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 RECENT WORKFLOW RUNS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📦 Last 3 production deployments:"
gh run list --workflow=13-prod-deployment.yml --limit 3 --json conclusion,createdAt,displayTitle --jq '.[] | "   \(if .conclusion == "success" then "✅" elif .conclusion == "failure" then "❌" else "⏳" end) \(.createdAt[:10]) - \(.displayTitle)"' 2>/dev/null || echo "   ⚠️  Unable to fetch workflow runs"

echo ""
echo "📦 Last 3 UAT deployments:"
gh run list --workflow=12-uat-deployment.yml --limit 3 --json conclusion,createdAt,displayTitle --jq '.[] | "   \(if .conclusion == "success" then "✅" elif .conclusion == "failure" then "❌" else "⏳" end) \(.createdAt[:10]) - \(.displayTitle)"' 2>/dev/null || echo "   ⚠️  Unable to fetch workflow runs"

echo ""
echo "📦 Last 3 dev deployments:"
gh run list --workflow=11-dev-deployment.yml --limit 3 --json conclusion,createdAt,displayTitle --jq '.[] | "   \(if .conclusion == "success" then "✅" elif .conclusion == "failure" then "❌" else "⏳" end) \(.createdAt[:10]) - \(.displayTitle)"' 2>/dev/null || echo "   ⚠️  Unable to fetch workflow runs"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Overall health assessment
if [ "$MAIN_AHEAD" -eq 0 ]; then
    echo "🎯 Repository Health: ✅ EXCELLENT"
    echo "   All branches properly aligned. GitFlow maintained."
elif [ "$MAIN_AHEAD" -le 3 ]; then
    echo "🎯 Repository Health: ✅ GOOD"
    echo "   Minor divergence within acceptable window."
else
    echo "🎯 Repository Health: ⚠️  NEEDS ATTENTION"
    echo "   Divergence detected. Review and sync required."
    echo ""
    echo "   🔧 Remediation Steps:"
    echo "   1. git checkout development"
    echo "   2. git checkout -b sync/main-to-dev-$(date +%Y%m%d)"
    echo "   3. git merge origin/main --no-edit"
    echo "   4. git push origin sync/main-to-dev-$(date +%Y%m%d)"
    echo "   5. gh pr create --base development --title 'sync: merge main hotfixes to development'"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 For more information:"
echo "   • BRANCH_PROTECTION_SETUP.md - Comprehensive guide"
echo "   • BRANCH_PROTECTION_QUICK_SETUP.md - Quick reference"
echo "   • BRANCH_DIVERGENCE_RESOLUTION_SUMMARY.md - Incident report"
echo ""
echo "🔗 Useful Links:"
echo "   • Branch Protection: https://github.com/$OWNER/$REPO/settings/branches"
echo "   • Workflow Runs: https://github.com/$OWNER/$REPO/actions"
echo "   • Repository Rules: https://github.com/$OWNER/$REPO/rules"
echo ""
