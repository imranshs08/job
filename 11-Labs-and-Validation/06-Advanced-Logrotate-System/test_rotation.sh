#!/bin/bash
# Demonstrates dry-runs and forceful execution of logrotate
set -euo pipefail

CONF_FILE="/etc/logrotate.d/my_app"
APP_LOG_DIR="/var/log/my_app"

echo "================================================="
echo "🔄 EXECUTING ADVANCED LOGROTATE TESTING SEQUENCE"
echo "================================================="

echo "[1/3] Running a dry-run (debug mode) without modifying files..."
echo "Command: logrotate -d $CONF_FILE"
sudo logrotate -d "$CONF_FILE"
echo "-------------------------------------------------"

echo "[2/3] Forcing execution regardless of daily cron intervals..."
echo "Command: logrotate -vf $CONF_FILE"
# -v for verbose output, -f for force 
sudo logrotate -vf "$CONF_FILE"
echo "-------------------------------------------------"

echo "[3/3] Validating rotation and compression in $APP_LOG_DIR..."
ls -lh "$APP_LOG_DIR"

echo ""
echo "[+] SUCCESS: Notice the original my_app.log is now 0 bytes."
echo "[+] Notice my_app.log.1 exists (uncompressed due to 'delaycompress')."
echo "[+] If you run the simulation and test scripts again, you will see .gz files generated!"
