#!/bin/bash

# Set variables
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="travel_app_backup_$TIMESTAMP"
FIREBASE_BACKUP_FILE="$BACKUP_NAME.json"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Export Firebase data
echo "Exporting Firebase data..."
firebase firestore:export "$BACKUP_DIR/$FIREBASE_BACKUP_FILE"

# Backup SSL certificates
echo "Backing up SSL certificates..."
cp -r certificates "$BACKUP_DIR/$BACKUP_NAME.certificates"

# Backup environment variables
echo "Backing up environment variables..."
cp .env "$BACKUP_DIR/$BACKUP_NAME.env"

# Create a tar archive of the backup
echo "Creating backup archive..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    "$BACKUP_DIR/$FIREBASE_BACKUP_FILE" \
    "$BACKUP_DIR/$BACKUP_NAME.certificates" \
    "$BACKUP_DIR/$BACKUP_NAME.env"

# Clean up temporary files
echo "Cleaning up temporary files..."
rm -rf "$BACKUP_DIR/$FIREBASE_BACKUP_FILE" \
       "$BACKUP_DIR/$BACKUP_NAME.certificates" \
       "$BACKUP_DIR/$BACKUP_NAME.env"

# Upload backup to cloud storage (example using AWS S3)
if [ -n "$AWS_BUCKET" ]; then
    echo "Uploading backup to AWS S3..."
    aws s3 cp "$BACKUP_DIR/$BACKUP_NAME.tar.gz" "s3://$AWS_BUCKET/backups/"
fi

# Clean up old backups (keep last 7 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "travel_app_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed successfully!" 