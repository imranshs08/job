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
# The '-d' (debug) flag tells logrotate to read the file, calculate what it *would* do, print the output, 
# but actually touch nothing on disk. This is how SREs prevent breaking production config files!
sudo logrotate -d "$CONF_FILE"
echo "-------------------------------------------------"

echo "[2/3] Forcing execution regardless of daily cron intervals..."
echo "Command: logrotate -vf $CONF_FILE"
# The '-v' (verbose) flag provides dense stdout logging.
# The '-f' (force) flag completely ignores the /var/lib/logrotate/status state memory file and forces the rotation IMMEDIATELY.
sudo logrotate -vf "$CONF_FILE"
echo "-------------------------------------------------"

echo "[3/3] Validating rotation and compression in $APP_LOG_DIR..."
ls -lh "$APP_LOG_DIR"

echo ""
echo "[+] SUCCESS: Notice the original my_app.log is now 0 bytes."
echo "[+] Notice my_app.log.1 exists (uncompressed due to 'delaycompress')."
echo "[+] If you run the simulation and test scripts again, you will see .gz files generated!"
