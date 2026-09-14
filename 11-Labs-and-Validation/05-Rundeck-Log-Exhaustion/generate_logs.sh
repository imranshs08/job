#!/bin/bash
# Forcefully simulates an uncontrollable log generation event with artificial timestamp spoofing.
set -euo pipefail

LOG_DIR="/var/log/rundeck_lab_sim"
echo "================================================="
echo "💥 SIMULATING RUNAWAY LOG GENERATION & TIME SPOOFING"
echo "================================================="

echo "[+] Creating designated simulation directory at $LOG_DIR"
sudo mkdir -p "$LOG_DIR"

echo "[!] Creating TIER 1: Fresh Raw Logs (Will NOT be compressed - newer than 2 days)"
# Create 5 logs and spoof time to yesterday
for i in {1..5}; do
    PAYLOAD="$LOG_DIR/fresh_app_${i}.log"
    sudo dd if=/dev/urandom of="$PAYLOAD" bs=1M count=20 status=none
    sudo touch -d "1 day ago" "$PAYLOAD"
done

echo "[!] Creating TIER 2: Stale Raw Logs (WILL be compressed - older than 2 days)"
# Create 5 logs and spoof time to 4 days ago
for i in {1..5}; do
    PAYLOAD="$LOG_DIR/stale_app_${i}.log"
    sudo dd if=/dev/urandom of="$PAYLOAD" bs=1M count=30 status=none
    sudo touch -d "4 days ago" "$PAYLOAD"
done

echo "[!] Creating TIER 3: Recent Archives (Will NOT be deleted - compressed but newer than 7 days)"
# Create 5 dummy .gz archives and spoof time to 5 days ago
for i in {1..5}; do
    PAYLOAD="$LOG_DIR/recent_archive_${i}.log.gz"
    sudo dd if=/dev/urandom of="$PAYLOAD" bs=1M count=10 status=none
    sudo touch -d "5 days ago" "$PAYLOAD"
done

echo "[!] Creating TIER 4: Legacy Archives (WILL be deleted - compressed and older than 7 days)"
# Create 5 dummy .gz archives and spoof time to 10 days ago
for i in {1..5}; do
    PAYLOAD="$LOG_DIR/legacy_archive_${i}.log.gz"
    sudo dd if=/dev/urandom of="$PAYLOAD" bs=1M count=10 status=none
    sudo touch -d "10 days ago" "$PAYLOAD"
done

echo "[+] Multi-stage time simulation complete."
echo "     -> Run './disk_monitor.sh' to test the 2-day compression logic."
echo "     -> Run './cleanup_logs.sh' to test the 7-day deletion logic."
