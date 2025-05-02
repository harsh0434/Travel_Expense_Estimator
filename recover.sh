#!/bin/bash

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Create temporary directory for extraction
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Extract backup
echo "Extracting backup..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Restore Firebase data
echo "Restoring Firebase data..."
FIREBASE_BACKUP=$(find "$TEMP_DIR" -name "*.json")
if [ -n "$FIREBASE_BACKUP" ]; then
    firebase firestore:import "$FIREBASE_BACKUP"
else
    echo "No Firebase backup found in the archive"
    exit 1
fi

# Restore SSL certificates
echo "Restoring SSL certificates..."
CERT_DIR=$(find "$TEMP_DIR" -name "*.certificates")
if [ -n "$CERT_DIR" ]; then
    rm -rf certificates
    cp -r "$CERT_DIR" certificates
else
    echo "No SSL certificates found in the archive"
    exit 1
fi

# Restore environment variables
echo "Restoring environment variables..."
ENV_FILE=$(find "$TEMP_DIR" -name "*.env")
if [ -n "$ENV_FILE" ]; then
    cp "$ENV_FILE" .env
else
    echo "No environment variables found in the archive"
    exit 1
fi

# Clean up
echo "Cleaning up..."
rm -rf "$TEMP_DIR"

echo "Recovery completed successfully!" 