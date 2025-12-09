#!/bin/bash
# Bulk Delete GitHub Actions Workflow Runs
# 
# This script deletes workflow runs older than 30 days using GitHub CLI (gh).
# It includes filters for failed runs and Dependabot triggers, with confirmation
# prompts and comprehensive logging.
#
# Requirements:
#   - GitHub CLI (gh) installed and authenticated
#   - PAT with 'repo' and 'workflow' scopes
#
# Usage:
#   ./bulk-delete-workflow-runs.sh [OPTIONS]
#
# Options:
#   --dry-run         Show what would be deleted without actually deleting
#   --auto-confirm    Skip confirmation prompts (use with caution)
#   --days N          Delete runs older than N days (default: 30)
#   --status STATUS   Filter by status: failed, success, cancelled, all (default: all)
#   --actor ACTOR     Filter by Dependabot or specific actor
#   --help            Show this help message

set -euo pipefail

# Configuration
REPO="${GITHUB_REPOSITORY:-Meats-Central/ProjectMeats}"
DEFAULT_DAYS=30
DEFAULT_STATUS="all"
DRY_RUN=false
AUTO_CONFIRM=false
LOG_FILE="workflow-deletion-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
DAYS=$DEFAULT_DAYS
STATUS=$DEFAULT_STATUS
ACTOR=""

show_help() {
  grep '^#' "$0" | grep -v '#!/bin/bash' | sed 's/^# //' | sed 's/^#//'
  exit 0
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    --auto-confirm)
      AUTO_CONFIRM=true
      shift
      ;;
    --days)
      DAYS="$2"
      shift 2
      ;;
    --status)
      STATUS="$2"
      shift 2
      ;;
    --actor)
      ACTOR="$2"
      shift 2
      ;;
    --help)
      show_help
      ;;
    *)
      echo -e "${RED}Error: Unknown option $1${NC}"
      show_help
      ;;
  esac
done

# Logging function
log() {
  local level=$1
  shift
  local message="$*"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# Check if gh is installed and authenticated
check_prerequisites() {
  if ! command -v gh &> /dev/null; then
    log "ERROR" "GitHub CLI (gh) is not installed. Please install it first."
    log "ERROR" "Visit: https://cli.github.com/manual/installation"
    exit 1
  fi

  if ! gh auth status &> /dev/null; then
    log "ERROR" "GitHub CLI is not authenticated. Please run: gh auth login"
    exit 1
  fi

  log "INFO" "Prerequisites check passed"
}

# Calculate cutoff date
calculate_cutoff_date() {
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    date -u -v-${DAYS}d '+%Y-%m-%dT%H:%M:%SZ'
  else
    # Linux
    date -u -d "$DAYS days ago" '+%Y-%m-%dT%H:%M:%SZ'
  fi
}

# Get workflow runs to delete
get_workflow_runs() {
  local cutoff_date=$1
  local query="created:<$cutoff_date"
  
  # Add status filter if not 'all'
  if [[ "$STATUS" != "all" ]]; then
    query="$query status:$STATUS"
  fi
  
  # Add actor filter if specified
  if [[ -n "$ACTOR" ]]; then
    query="$query actor:$ACTOR"
  fi
  
  log "INFO" "Fetching workflow runs with query: $query"
  
  # Use GitHub API to get workflow runs
  # Note: gh api handles pagination automatically with --paginate
  gh api \
    --paginate \
    -H "Accept: application/vnd.github+json" \
    "/repos/$REPO/actions/runs?per_page=100" \
    --jq ".workflow_runs[] | select(.created_at < \"$cutoff_date\") | 
           select(if \"$STATUS\" != \"all\" then .conclusion == \"$STATUS\" else true end) |
           select(if \"$ACTOR\" != \"\" then .actor.login == \"$ACTOR\" else true end) |
           {id: .id, name: .name, conclusion: .conclusion, created_at: .created_at, actor: .actor.login, run_number: .run_number}"
}

# Delete workflow run with rate limiting
delete_workflow_run() {
  local run_id=$1
  local run_name=$2
  local run_number=$3
  
  if [[ "$DRY_RUN" == true ]]; then
    log "DRY-RUN" "Would delete: Run #$run_number - $run_name (ID: $run_id)"
    return 0
  fi
  
  # Attempt deletion with retry logic
  local max_retries=3
  local retry_count=0
  
  while [[ $retry_count -lt $max_retries ]]; do
    if gh api \
      --method DELETE \
      -H "Accept: application/vnd.github+json" \
      "/repos/$REPO/actions/runs/$run_id" &> /dev/null; then
      log "SUCCESS" "Deleted: Run #$run_number - $run_name (ID: $run_id)"
      return 0
    else
      retry_count=$((retry_count + 1))
      if [[ $retry_count -lt $max_retries ]]; then
        log "WARN" "Retry $retry_count/$max_retries for run $run_id"
        sleep 2
      fi
    fi
  done
  
  log "ERROR" "Failed to delete run $run_id after $max_retries attempts"
  return 1
}

# Main execution
main() {
  echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║   GitHub Actions Workflow Runs Bulk Deletion Tool           ║${NC}"
  echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  
  log "INFO" "Starting bulk deletion process"
  log "INFO" "Repository: $REPO"
  log "INFO" "Delete runs older than: $DAYS days"
  log "INFO" "Status filter: $STATUS"
  log "INFO" "Actor filter: ${ACTOR:-none}"
  log "INFO" "Dry run: $DRY_RUN"
  log "INFO" "Log file: $LOG_FILE"
  echo ""
  
  # Check prerequisites
  check_prerequisites
  
  # Calculate cutoff date
  cutoff_date=$(calculate_cutoff_date)
  log "INFO" "Cutoff date: $cutoff_date"
  echo ""
  
  # Get workflow runs
  log "INFO" "Fetching workflow runs to delete..."
  runs_json=$(get_workflow_runs "$cutoff_date")
  
  if [[ -z "$runs_json" ]]; then
    echo -e "${GREEN}✓ No workflow runs found matching the criteria${NC}"
    log "INFO" "No workflow runs to delete"
    exit 0
  fi
  
  # Count runs
  run_count=$(echo "$runs_json" | jq -s 'length')
  
  echo -e "${YELLOW}Found $run_count workflow runs to delete${NC}"
  echo ""
  
  # Show summary
  echo "Summary of runs to delete:"
  echo "$runs_json" | jq -r '"  • Run #\(.run_number) - \(.name) (\(.conclusion)) - \(.created_at)"' | head -20
  
  if [[ $run_count -gt 20 ]]; then
    echo "  ... and $((run_count - 20)) more runs"
  fi
  echo ""
  
  # Confirmation prompt
  if [[ "$AUTO_CONFIRM" != true ]] && [[ "$DRY_RUN" != true ]]; then
    echo -e "${RED}⚠️  WARNING: This will permanently delete $run_count workflow runs!${NC}"
    read -p "Are you sure you want to proceed? (yes/no): " confirmation
    
    if [[ "$confirmation" != "yes" ]]; then
      echo -e "${YELLOW}Deletion cancelled by user${NC}"
      log "INFO" "Deletion cancelled by user"
      exit 0
    fi
  fi
  
  # Delete runs
  log "INFO" "Starting deletion of $run_count runs..."
  deleted_count=0
  failed_count=0
  
  echo "$runs_json" | jq -c '.' | while read -r run; do
    run_id=$(echo "$run" | jq -r '.id')
    run_name=$(echo "$run" | jq -r '.name')
    run_number=$(echo "$run" | jq -r '.run_number')
    
    if delete_workflow_run "$run_id" "$run_name" "$run_number"; then
      deleted_count=$((deleted_count + 1))
    else
      failed_count=$((failed_count + 1))
    fi
    
    # Rate limiting: sleep briefly between deletions
    sleep 0.5
  done
  
  echo ""
  echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║                    Deletion Complete                         ║${NC}"
  echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  
  if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}DRY RUN: Would have deleted $run_count runs${NC}"
    log "INFO" "Dry run completed - would have deleted $run_count runs"
  else
    echo -e "${GREEN}✓ Successfully processed $run_count runs${NC}"
    log "INFO" "Deletion completed"
    log "INFO" "Total runs processed: $run_count"
  fi
  
  echo ""
  echo "Log file: $LOG_FILE"
  log "INFO" "Script execution completed"
}

# Run main function
main "$@"
