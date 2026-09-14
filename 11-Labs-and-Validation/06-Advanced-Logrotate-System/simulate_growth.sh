#!/bin/bash
# Emulates rapid application activity to breach the 10MB size limit
set -euo pipefail

APP_LOG_FILE="/var/log/my_app/my_app.log"

echo "================================================="
echo "📈 SIMULATING AGGRESSIVE APPLICATION LOG GROWTH"
echo "================================================="

if [ ! -f "$APP_LOG_FILE" ]; then
    echo "[-] Log file not found! Did you run setup_lab.sh?"
    exit 1
fi

echo "[+] Pumping 15MB of dummy text into $APP_LOG_FILE..."
# Generate approx 15MB of data quickly
sudo dd if=/dev/urandom bs=1M count=15 | base64 > "$APP_LOG_FILE" 2>/dev/null

CURRENT_SIZE=$(du -sh "$APP_LOG_FILE" | cut -f1)
echo "[+] Simulation finished! Current log size is: $CURRENT_SIZE"
echo "[!] The log has breached the 10MB threshold. It is ready for rotation."
