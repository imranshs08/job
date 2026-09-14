#!/bin/bash
# Scaffold script for Advanced Logrotate Lab
set -euo pipefail

echo "================================================="
echo "🛠️ SETTING UP ADVANCED LOGROTATE ENVIRONMENT"
echo "================================================="

# 1. Check & Install Logrotate (RHEL/Alma/CentOS)
# command -v is the POSIX compliant way to check if a binary exists in the system PATH
if ! command -v logrotate &> /dev/null; then
    echo "[+] Logrotate not found. Installing via YUM (Yellowdog Updater Modified)..."
    sudo yum install -y logrotate  # The -y flag automatically assumes 'yes' to all installation prompts
else
    # Extract just the first line of the version output for cleaner terminal logging
    LOGROTATE_VER=$(logrotate --version | head -n 1)
    echo "[+] Logrotate is already installed: $LOGROTATE_VER"
fi

# 2. Scaffold Custom Application Logs
APP_LOG_DIR="/var/log/my_app"
APP_LOG_FILE="$APP_LOG_DIR/my_app.log"
echo "[+] Creating custom log directory at $APP_LOG_DIR"
sudo mkdir -p "$APP_LOG_DIR"
sudo touch "$APP_LOG_FILE"
sudo chmod 666 "$APP_LOG_FILE" # Grant write access securely (777 triggers logrotate security panic!)

# 3. Inject Custom Configuration into /etc/logrotate.d/
CONF_FILE="/etc/logrotate.d/my_app"
echo "[+] Deploying aggressive logrotate configuration to $CONF_FILE"

# Using a Heredoc (cat <<EOF) to safely inject a multi-line string block directly into a system file as root.
sudo bash -c "cat <<EOF > $CONF_FILE
$APP_LOG_DIR/*.log {
    su root root          # Mandates execution as root to pass strict SELinux ownership security rules
    size 10M              # Bypasses daily cron restrictions if the file breaches 10 Megabytes
    rotate 4              # Retain exactly 4 historical archives. The 5th is permanently deleted.
    compress              # Auto-gzip the older logs using /bin/gzip
    delaycompress         # Skip compression on tomorrow's rotation for rapid SRE querying ('my_app.log.1')
    missingok             # Suppress error codes if the log file hasn't been generated yet
    notifempty            # Do not process anything if the file is completely 0 bytes
    create 0644 root root # Create the brand-new log file immediately so the app has somewhere to write.
}
EOF"

echo "[+] Validation of Configuration File:"
# Verify the injection worked by streaming it back to the active console
cat "$CONF_FILE"
echo ""
echo "[+] Setup Complete! Next, run ./simulate_growth.sh to generate traffic."
