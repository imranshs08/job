#!/bin/bash
# Teardown script for Advanced Logrotate Lab
set -euo pipefail

echo "================================================="
echo "🧽 TEAR DOWN & CLEANUP: LOGROTATE LAB"
echo "================================================="

APP_LOG_DIR="/var/log/my_app"
CONF_FILE="/etc/logrotate.d/my_app"

# 1. Remove the custom configuration file
if [ -f "$CONF_FILE" ]; then
    echo "[-] Removing configuration drop-in: $CONF_FILE"
    sudo rm -f "$CONF_FILE"
fi

# 2. Hard delete the application directory and all rotated logs
if [ -d "$APP_LOG_DIR" ]; then
    echo "[-] Deleting application logs and archives from: $APP_LOG_DIR"
    sudo rm -rf "$APP_LOG_DIR"
fi

echo "[+] System restored to pre-lab state. Global logrotate unaffected."
