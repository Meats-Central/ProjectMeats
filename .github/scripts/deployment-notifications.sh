#!/bin/bash
# Deployment Notification Handler
# Sends notifications about deployment status

set -euo pipefail

ENVIRONMENT="${1:-}"
STATUS="${2:-}"  # started, success, failed, rollback
COMPONENT="${3:-all}"
MESSAGE="${4:-}"

if [ -z "$ENVIRONMENT" ] || [ -z "$STATUS" ]; then
    echo "Usage: $0 <environment> <started|success|failed|rollback> [component] [message]"
    exit 1
fi

# Emoji mapping
declare -A EMOJI=(
    ["started"]="🚀"
    ["success"]="✅"
    ["failed"]="❌"
    ["rollback"]="⏮️"
    ["warning"]="⚠️"
)

# Color mapping
declare -A COLOR=(
    ["started"]="#0066CC"
    ["success"]="#00CC66"
    ["failed"]="#CC0000"
    ["rollback"]="#FF9900"
    ["warning"]="#FFCC00"
)

TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
DEPLOYMENT_ID="${GITHUB_RUN_ID:-$(date +%s)}"

# Format notification message
format_message() {
    local title="${EMOJI[$STATUS]} Deployment $STATUS: $ENVIRONMENT ($COMPONENT)"
    
    cat <<EOF
**Deployment Notification**

**Environment:** $ENVIRONMENT
**Component:** $COMPONENT
**Status:** ${STATUS^^}
**Time:** $TIMESTAMP
**Deployment ID:** $DEPLOYMENT_ID
**Triggered by:** ${GITHUB_ACTOR:-System}
**Branch:** ${GITHUB_REF_NAME:-N/A}
**Commit:** ${GITHUB_SHA:0:7}

${MESSAGE:+**Details:** $MESSAGE}

---
*Automated deployment notification*
EOF
}

# Send to GitHub (create annotation)
notify_github() {
    if [ -n "${GITHUB_ACTIONS:-}" ]; then
        case "$STATUS" in
            success)
                echo "::notice title=Deployment Success::$ENVIRONMENT deployment completed successfully"
                ;;
            failed)
                echo "::error title=Deployment Failed::$ENVIRONMENT deployment failed - $MESSAGE"
                ;;
            rollback)
                echo "::warning title=Deployment Rollback::$ENVIRONMENT deployment rolled back - $MESSAGE"
                ;;
            started)
                echo "::notice title=Deployment Started::$ENVIRONMENT deployment initiated"
                ;;
        esac
    fi
}

# Send to Slack (if webhook configured)
notify_slack() {
    if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
        local payload=$(cat <<EOF
{
    "attachments": [
        {
            "color": "${COLOR[$STATUS]}",
            "title": "${EMOJI[$STATUS]} Deployment $STATUS",
            "fields": [
                {
                    "title": "Environment",
                    "value": "$ENVIRONMENT",
                    "short": true
                },
                {
                    "title": "Component",
                    "value": "$COMPONENT",
                    "short": true
                },
                {
                    "title": "Status",
                    "value": "${STATUS^^}",
                    "short": true
                },
                {
                    "title": "Deployment ID",
                    "value": "$DEPLOYMENT_ID",
                    "short": true
                },
                {
                    "title": "Branch",
                    "value": "${GITHUB_REF_NAME:-N/A}",
                    "short": true
                },
                {
                    "title": "Commit",
                    "value": "${GITHUB_SHA:0:7}",
                    "short": true
                }
            ],
            "footer": "ProjectMeats Deployment",
            "ts": $(date +%s)
        }
    ]
}
EOF
)
        curl -X POST -H 'Content-type: application/json' \
            --data "$payload" \
            "$SLACK_WEBHOOK_URL" \
            2>/dev/null || echo "Warning: Slack notification failed"
    fi
}

# Log to file
log_notification() {
    local log_file="/tmp/pm-deployment-notifications.log"
    echo "[$(date -Iseconds)] [$STATUS] $ENVIRONMENT/$COMPONENT: $MESSAGE" >> "$log_file"
}

# Main notification handler
main() {
    echo "Sending deployment notification: $STATUS"
    
    notify_github
    notify_slack
    log_notification
    
    echo "Notification sent successfully"
}

main
