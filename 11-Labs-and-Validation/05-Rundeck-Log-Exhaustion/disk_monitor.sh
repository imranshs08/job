#!/bin/bash
# Monitors a designated volume mount, triggers email alert, and compresses oldest logs if > 80% full
set -eo pipefail

MONITOR_DIR="/var/log/rundeck_lab_sim"
TARGET_MOUNT="/" # Set to root mount for simulation, change to /var on enterprise VMs if partitioned

# Grab integer usage percentage of target mount point
USAGE_STR=$(df -h "$TARGET_MOUNT" | awk 'NR==2 {print $5}')
USAGE_INT=${USAGE_STR%\%}

echo "[*] Current system disk consumption on $TARGET_MOUNT is at: ${USAGE_INT}%"

if [ "$USAGE_INT" -gt 80 ]; then
    echo "================================================="
    echo "🚨 CRITICAL THRESHOLD BREACHED ( > 80% Usage )"
    echo "================================================="
    
    # 1. Dispatch HTML alert to SRE team using Brevo SMTP script
    echo "[+] Triggering SEV-1 notification..."
    python3 ./mail_notifier.py "$USAGE_INT"
    
    # 2. Defensively compress un-rotated standard log files.
    # We target specifically '*.log' and skip anything already '.gz'
    echo "[+] Initiating automated self-healing log rotation on $MONITOR_DIR..."
    
    # Check if files exist to avoid throwing find errors
    if [ "$(ls -A "$MONITOR_DIR"/*.log 2>/dev/null)" ]; then
        # -exec gzip compresses them in place, heavily reducing du (disk usage) space.
        # Modified to only target logs strictly older than 2 days to maintain immediate recent logs!
        sudo find "$MONITOR_DIR" -type f -name "*.log" -mtime +2 -exec gzip -v {} \+
        echo "[+] Remediation successful. Files archived."
    else
         echo "[-] No uncompressed .log files older than 2 days found to compress!"
    fi
    
    # Post-mortem telemetry
    NEW_USAGE=$(df -h "$TARGET_MOUNT" | awk 'NR==2 {print $5}')
    echo "[*] Crisis averted. System stabilized at: $NEW_USAGE"
else
    echo "[+] Disk volume operating within safe parameters."
fi
