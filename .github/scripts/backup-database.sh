#!/bin/bash
# Database backup script for deployments
# Creates timestamped database backup before migrations

set -euo pipefail

echo "=== Database Backup Script ==="

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/home/django/ProjectMeats/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_${TIMESTAMP}.sql"
KEEP_BACKUPS=${KEEP_BACKUPS:-7}  # Keep last 7 backups

# Extract database credentials from DATABASE_URL
# Format: postgresql://user:password@host:port/dbname
if [ -z "${DATABASE_URL:-}" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

echo "Parsing DATABASE_URL..."
# Parse DATABASE_URL
DB_PROTO=$(echo $DATABASE_URL | grep :// | sed -e's,^\(.*://\).*,\1,g')
DB_URL=$(echo ${DATABASE_URL/$DB_PROTO/})
DB_USER=$(echo $DB_URL | grep @ | cut -d@ -f1 | cut -d: -f1)
DB_PASS=$(echo $DB_URL | grep @ | cut -d@ -f1 | grep : | cut -d: -f2)
DB_HOST=$(echo $DB_URL | grep @ | cut -d@ -f2 | cut -d: -f1 | cut -d/ -f1)
DB_PORT=$(echo $DB_URL | grep @ | cut -d@ -f2 | cut -d: -f2 | cut -d/ -f1)
DB_NAME=$(echo $DB_URL | grep @ | cut -d@ -f2 | cut -d/ -f2 | cut -d? -f1)

# Defaults
DB_PORT=${DB_PORT:-5432}

echo "Database: $DB_NAME"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"

# Create backup directory if it doesn't exist
sudo mkdir -p "$BACKUP_DIR"

# Create backup
echo ""
echo "Creating database backup: $BACKUP_FILE"
if PGPASSWORD="$DB_PASS" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" | sudo tee "$BACKUP_FILE" > /dev/null; then
    echo "✅ Database backup created successfully"
    
    # Compress backup
    echo "Compressing backup..."
    sudo gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"
    echo "✅ Backup compressed: $BACKUP_FILE"
    
    # Set permissions
    sudo chmod 600 "$BACKUP_FILE"
    
    # Get file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Backup size: $SIZE"
else
    echo "❌ ERROR: Database backup failed"
    exit 1
fi

# Clean up old backups (keep last N backups)
echo ""
echo "Cleaning up old backups (keeping last $KEEP_BACKUPS)..."
BACKUP_COUNT=$(sudo ls -1 "$BACKUP_DIR"/db_backup_*.sql.gz 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt "$KEEP_BACKUPS" ]; then
    TO_DELETE=$((BACKUP_COUNT - KEEP_BACKUPS))
    echo "Deleting $TO_DELETE old backup(s)..."
    sudo ls -1t "$BACKUP_DIR"/db_backup_*.sql.gz | tail -n "$TO_DELETE" | sudo xargs rm -f
    echo "✅ Old backups cleaned up"
else
    echo "Only $BACKUP_COUNT backup(s) exist, no cleanup needed"
fi

echo ""
echo "=== Backup Complete ==="
echo "Backup file: $BACKUP_FILE"
echo "To restore: gunzip -c $BACKUP_FILE | PGPASSWORD=\$DB_PASS psql -h $DB_HOST -p $DB_PORT -U $DB_USER $DB_NAME"
exit 0
