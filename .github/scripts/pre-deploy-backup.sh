#!/bin/bash
# Database Backup Before Deployment
# Creates a backup of the database before any deployment changes

set -euo pipefail

ENVIRONMENT="${1:-}"
DB_HOST="${2:-}"
DB_NAME="${3:-}"
DB_USER="${4:-}"
DB_PASSWORD="${5:-}"

if [ -z "$ENVIRONMENT" ] || [ -z "$DB_HOST" ]; then
    echo "Usage: $0 <environment> <db_host> <db_name> <db_user> <db_password>"
    exit 1
fi

BACKUP_DIR="/tmp/pm-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/pm_${ENVIRONMENT}_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "=== Database Backup: $ENVIRONMENT ==="
echo "Host: $DB_HOST"
echo "Database: $DB_NAME"
echo "Backup file: $BACKUP_FILE"

# Create backup
export PGPASSWORD="$DB_PASSWORD"

if pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✓ Backup created successfully: $BACKUP_SIZE"
    
    # Keep only last 10 backups
    ls -t "${BACKUP_DIR}"/pm_${ENVIRONMENT}_*.sql.gz | tail -n +11 | xargs rm -f 2>/dev/null || true
    echo "✓ Old backups cleaned up"
    
    echo "$BACKUP_FILE"
    exit 0
else
    echo "✗ Backup failed"
    exit 1
fi
