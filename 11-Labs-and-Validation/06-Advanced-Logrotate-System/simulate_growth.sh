#!/bin/bash
# Emulates rapid application activity to breach the 10MB size limit
set -euo pipefail

APP_LOG_FILE="/var/log/my_app/my_app.log"

echo "================================================="
echo "📈 SIMULATING AGGRESSIVE APPLICATION LOG GROWTH"
echo "================================================="

if [ ! -f "$APP_LOG_FILE" ]; then
    # -f tests if the file exists and is a regular file. If false (!), trigger an exit to prevent script failure
    echo "[-] Log file not found! Did you run setup_lab.sh?"
    exit 1 # Exit 1 signifies a standard failure code back to the OS
fi

echo "[+] Pumping 15MB of dummy text into $APP_LOG_FILE..."

# Generate approx 15MB of data quickly
# 'dd if=/dev/urandom': Reads high-entropy random data from the Linux kernel
# 'bs=1M count=15': Grabs 1 Megabyte block 15 times (Total exactly 15MB)
# '| base64': We pipe it into base64 to ensure it remains readable ASCII text. Raw binary breaks text editors!
sudo dd if=/dev/urandom bs=1M count=15 | base64 > "$APP_LOG_FILE" 2>/dev/null

# Extract the human-readable size of the file (e.g. "15M") using du and stripping the path via cut
CURRENT_SIZE=$(du -sh "$APP_LOG_FILE" | cut -f1)
echo "[+] Simulation finished! Current log size is: $CURRENT_SIZE"
echo "[!] The log has breached the 10MB threshold. It is ready for rotation."
