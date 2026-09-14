#!/bin/bash
# Enterprise Log Cleanup Script 
# Built to be executed via a scheduled CronJob.
# Purpose: Permanently delete compressed (.gz) log archives older than 7 days to fully free up Inodes and Blocks.
set -eo pipefail

echo "================================================="
echo "🧹 ROUTINE AUTOMATED LOG CLEANUP (CRON)"
echo "================================================="

TARGET_DIR="/var/log/rundeck_lab_sim"
RETENTION_DAYS=7

# Validate directory exists to avoid finding in root
if [ ! -d "$TARGET_DIR" ]; then
    echo "[-] Directory $TARGET_DIR does not exist. Exiting safely."
    exit 0
fi

echo "[*] Scanning $TARGET_DIR for compressed logs older than $RETENTION_DAYS days..."

# Use 'find' to target files (-type f), matching pattern (-name '*.gz'), older than days (-mtime +7)
# And pipe them into the delete executable
# We use + instead of \; so rm is executed once with all files, reducing overhead
if [ "$(find "$TARGET_DIR" -type f -name "*.gz" -mtime +$RETENTION_DAYS 2>/dev/null)" ]; then
    echo "[!] Older archives found. Proceeding with hard deletion..."
    sudo find "$TARGET_DIR" -type f -name "*.gz" -mtime +$RETENTION_DAYS -exec rm -vf {} \+
    echo "[+] Cleanup complete. Old data purged from storage array."
else
    echo "[+] No legacy log archives found exceeding $RETENTION_DAYS days. System is optimal."
fi

# Show final stats
echo "[*] Current Disk Status:"
df -h /
