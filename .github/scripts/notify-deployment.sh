#!/bin/bash
# Deployment notification script for Slack/Teams webhooks
# Supports both success and failure notifications with rich formatting
# Usage: ./notify-deployment.sh <status> <environment> <component> [commit_sha] [error_message]

set -euo pipefail

# Arguments
STATUS="${1:-}"              # success | failure | warning
ENVIRONMENT="${2:-}"         # dev | uat | prod
COMPONENT="${3:-}"           # frontend | backend | full-stack
COMMIT_SHA="${4:-unknown}"
ERROR_MESSAGE="${5:-No error details provided}"

# Webhook URLs from environment variables
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
TEAMS_WEBHOOK_URL="${TEAMS_WEBHOOK_URL:-}"

# Validation
if [ -z "$STATUS" ] || [ -z "$ENVIRONMENT" ] || [ -z "$COMPONENT" ]; then
  echo "❌ Error: Missing required arguments"
  echo "Usage: $0 <status> <environment> <component> [commit_sha] [error_message]"
  echo ""
  echo "Arguments:"
  echo "  status       : success | failure | warning"
  echo "  environment  : dev | uat | prod"
  echo "  component    : frontend | backend | full-stack"
  echo "  commit_sha   : Git commit SHA (optional)"
  echo "  error_message: Error details for failures (optional)"
  exit 1
fi

# Get current timestamp
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Get GitHub context if available
GITHUB_RUN_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY:-Meats-Central/ProjectMeats}/actions/runs/${GITHUB_RUN_ID:-unknown}"
GITHUB_ACTOR="${GITHUB_ACTOR:-Unknown}"

# Determine color and emoji based on status
case "$STATUS" in
  success)
    COLOR="#28a745"
    EMOJI="✅"
    TITLE="Deployment Successful"
    ;;
  failure)
    COLOR="#dc3545"
    EMOJI="❌"
    TITLE="Deployment Failed"
    ;;
  warning)
    COLOR="#ffc107"
    EMOJI="⚠️"
    TITLE="Deployment Warning"
    ;;
  *)
    COLOR="#6c757d"
    EMOJI="ℹ️"
    TITLE="Deployment Notification"
    ;;
esac

# Format environment name
ENV_DISPLAY=$(echo "$ENVIRONMENT" | tr '[:lower:]' '[:upper:]')

# Construct Slack message payload
create_slack_payload() {
  cat <<EOF
{
  "attachments": [
    {
      "color": "$COLOR",
      "title": "$EMOJI $TITLE",
      "fields": [
        {
          "title": "Environment",
          "value": "$ENV_DISPLAY",
          "short": true
        },
        {
          "title": "Component",
          "value": "$COMPONENT",
          "short": true
        },
        {
          "title": "Commit",
          "value": "\`${COMMIT_SHA:0:7}\`",
          "short": true
        },
        {
          "title": "Triggered By",
          "value": "$GITHUB_ACTOR",
          "short": true
        },
        {
          "title": "Timestamp",
          "value": "$TIMESTAMP",
          "short": false
        }
EOF

  # Add error message for failures
  if [ "$STATUS" = "failure" ]; then
    cat <<EOF
        ,
        {
          "title": "Error Details",
          "value": "\`\`\`$ERROR_MESSAGE\`\`\`",
          "short": false
        }
EOF
  fi

  cat <<EOF
      ],
      "actions": [
        {
          "type": "button",
          "text": "View Workflow Run",
          "url": "$GITHUB_RUN_URL"
        }
      ],
      "footer": "ProjectMeats CI/CD",
      "footer_icon": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
      "ts": $(date +%s)
    }
  ]
}
EOF
}

# Construct Teams message payload (Adaptive Card format)
create_teams_payload() {
  cat <<EOF
{
  "@type": "MessageCard",
  "@context": "https://schema.org/extensions",
  "summary": "$TITLE - $ENV_DISPLAY",
  "themeColor": "${COLOR:1}",
  "title": "$EMOJI $TITLE",
  "sections": [
    {
      "activityTitle": "Deployment to $ENV_DISPLAY",
      "activitySubtitle": "$TIMESTAMP",
      "facts": [
        {
          "name": "Environment:",
          "value": "$ENV_DISPLAY"
        },
        {
          "name": "Component:",
          "value": "$COMPONENT"
        },
        {
          "name": "Commit:",
          "value": "${COMMIT_SHA:0:7}"
        },
        {
          "name": "Triggered By:",
          "value": "$GITHUB_ACTOR"
        }
EOF

  # Add error message for failures
  if [ "$STATUS" = "failure" ]; then
    cat <<EOF
        ,
        {
          "name": "Error Details:",
          "value": "$ERROR_MESSAGE"
        }
EOF
  fi

  cat <<EOF
      ]
    }
  ],
  "potentialAction": [
    {
      "@type": "OpenUri",
      "name": "View Workflow Run",
      "targets": [
        {
          "os": "default",
          "uri": "$GITHUB_RUN_URL"
        }
      ]
    }
  ]
}
EOF
}

# Send notification to Slack
send_slack_notification() {
  if [ -z "$SLACK_WEBHOOK_URL" ]; then
    echo "ℹ️  Slack webhook URL not configured, skipping Slack notification"
    return 0
  fi

  echo "📤 Sending Slack notification..."
  
  local payload
  payload=$(create_slack_payload)
  
  local response
  response=$(curl -X POST \
    -H "Content-Type: application/json" \
    -d "$payload" \
    --max-time 10 \
    --retry 3 \
    --retry-delay 2 \
    -w "\n%{http_code}" \
    "$SLACK_WEBHOOK_URL" 2>/dev/null)
  
  local http_code
  http_code=$(echo "$response" | tail -n1)
  
  if [ "$http_code" = "200" ]; then
    echo "✓ Slack notification sent successfully"
    return 0
  else
    echo "⚠️  Slack notification failed (HTTP $http_code)"
    return 1
  fi
}

# Send notification to Teams
send_teams_notification() {
  if [ -z "$TEAMS_WEBHOOK_URL" ]; then
    echo "ℹ️  Teams webhook URL not configured, skipping Teams notification"
    return 0
  fi

  echo "📤 Sending Teams notification..."
  
  local payload
  payload=$(create_teams_payload)
  
  local response
  response=$(curl -X POST \
    -H "Content-Type: application/json" \
    -d "$payload" \
    --max-time 10 \
    --retry 3 \
    --retry-delay 2 \
    -w "\n%{http_code}" \
    "$TEAMS_WEBHOOK_URL" 2>/dev/null)
  
  local http_code
  http_code=$(echo "$response" | tail -n1)
  
  if [ "$http_code" = "200" ] || [ "$http_code" = "202" ]; then
    echo "✓ Teams notification sent successfully"
    return 0
  else
    echo "⚠️  Teams notification failed (HTTP $http_code)"
    return 1
  fi
}

# Main execution
echo "=== Deployment Notification ==="
echo "Status: $STATUS"
echo "Environment: $ENV_DISPLAY"
echo "Component: $COMPONENT"
echo "Commit: ${COMMIT_SHA:0:7}"
echo "=============================="

# Check if any webhook is configured
if [ -z "$SLACK_WEBHOOK_URL" ] && [ -z "$TEAMS_WEBHOOK_URL" ]; then
  echo "ℹ️  No notification webhooks configured, skipping notifications"
  echo "   Set SLACK_WEBHOOK_URL or TEAMS_WEBHOOK_URL to enable notifications"
  exit 0
fi

# Send notifications (continue even if one fails)
slack_result=0
teams_result=0

send_slack_notification || slack_result=$?
send_teams_notification || teams_result=$?

# Determine overall result
if [ $slack_result -ne 0 ] && [ $teams_result -ne 0 ]; then
  echo "⚠️  All notifications failed (non-critical)"
  exit 0  # Don't fail the workflow
fi

echo "✓ Notification process completed"
exit 0
