#!/bin/bash
# Forcefully simulates an uncontrollable log generation / memory leak event filling up disk space.
set -euo pipefail

LOG_DIR="/var/log/rundeck_lab_sim"
echo "================================================="
echo "💥 SIMULATING RUNAWAY APPLICATION LOG GENERATION"
echo "================================================="

echo "[+] Creating designated simulation directory at $LOG_DIR"
sudo mkdir -p "$LOG_DIR"

# Ensure enough iterations to hit 80% on this specific lab machine (Adjust '50' if needed)
# Be extremely careful not to run this permanently (it fills disk block by block)
echo "[!] Writing sequential massive log files..."
for i in {1..20}; do
    echo "[-] Writing log payload volume $i (100MB)..."
    sudo dd if=/dev/urandom of="$LOG_DIR/runaway_system_process_${i}.log" bs=1M count=100 status=none
    sleep 0.5 # Slight pause to let OS catch up
done

echo "[!] Runaway event complete. Run 'df -h' to see system suffocation."
