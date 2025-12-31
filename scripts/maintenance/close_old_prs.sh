#!/bin/bash
# Script to close old PRs that pre-date the Golden Pipeline

set -e

echo "=== PR Cleanup Script ==="
echo "This script will close PRs that pre-date the Golden Pipeline architecture"
echo ""

# PRs to close (based on dates and content)
# Anything before PR #1360 (Dec 15) is likely pre-Golden Pipeline

OLD_PRS=(
  1336  # fix: Add tenant field to Supplier model (superseded)
  1310  # feat: Integrate bastion mode (superseded)
  1241  # [WIP] Fix merge conflicts (WIP/stale)
  1234  # feat: modernize frontend build (superseded by Vite plan)
  1200  # Ideal Plan Refactor (superseded)
  1199  # Merge UAT into development (old merge)
  1193  # Merge main into development (old merge)
  1192  # Resolve merge conflicts (old conflicts)
  1191  # Main (stale)
  1186  # Add phoenix_init management command (superseded)
  1185  # Database Migration Reset (superseded)
  1184  # Verify legacy Client cleanup (completed)
  1178  # Verify syntax correctness (old verification)
  1177  # Verify dependency file syntax (old verification)
  1137  # Phase 2: Configure unified infrastructure (superseded)
)

CLOSE_MESSAGE="Closing as superseded by the Golden Pipeline architecture updates.

This PR pre-dates the Golden Pipeline implementation and is no longer relevant to the current architecture. The functionality has either been:
- Implemented in a different way
- Superseded by newer architectural decisions
- Resolved through other PRs

For current development practices, please refer to:
- [GOLDEN_PIPELINE.md](https://github.com/Meats-Central/ProjectMeats/blob/development/docs/GOLDEN_PIPELINE.md)
- [CONTRIBUTING.md](https://github.com/Meats-Central/ProjectMeats/blob/development/docs/CONTRIBUTING.md)

If this functionality is still needed, please create a new PR following the current contribution guidelines."

echo "PRs to close: ${#OLD_PRS[@]}"
echo ""

# Dry run first
echo "DRY RUN - showing PRs that would be closed:"
for pr in "${OLD_PRS[@]}"; do
  echo "  #$pr - $(gh pr view $pr --json title -q .title 2>/dev/null || echo 'Not found')"
done

echo ""
read -p "Proceed with closing these PRs? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted. No PRs were closed."
  exit 0
fi

echo ""
echo "Closing PRs..."

for pr in "${OLD_PRS[@]}"; do
  echo "Closing PR #$pr..."
  gh pr close $pr --comment "$CLOSE_MESSAGE" 2>&1 | head -5
  sleep 1  # Rate limiting
done

echo ""
echo "✅ PR cleanup complete!"
echo ""
echo "Summary:"
echo "  - Closed: ${#OLD_PRS[@]} PRs"
echo "  - Reason: Superseded by Golden Pipeline"
echo ""
echo "Next steps:"
echo "  - Review remaining open PRs"
echo "  - Keep only active development PRs"
echo "  - Ensure all new PRs follow Golden Pipeline patterns"
