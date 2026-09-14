#!/bin/bash
# Scaffold script for Advanced Logrotate Lab
set -euo pipefail

echo "================================================="
echo "🛠️ SETTING UP ADVANCED LOGROTATE ENVIRONMENT"
echo "================================================="

# 1. Check & Install Logrotate (RHEL/Alma/CentOS)
if ! command -v logrotate &> /dev/null; then
    echo "[+] Logrotate not found. Installing via YUM..."
    sudo yum install -y logrotate
else
    LOGROTATE_VER=$(logrotate --version | head -n 1)
    echo "[+] Logrotate is already installed: $LOGROTATE_VER"
fi

# 2. Scaffold Custom Application Logs
APP_LOG_DIR="/var/log/my_app"
APP_LOG_FILE="$APP_LOG_DIR/my_app.log"
echo "[+] Creating custom log directory at $APP_LOG_DIR"
sudo mkdir -p "$APP_LOG_DIR"
sudo touch "$APP_LOG_FILE"
sudo chmod 777 "$APP_LOG_FILE" # For lab write access

# 3. Inject Custom Configuration into /etc/logrotate.d/
CONF_FILE="/etc/logrotate.d/my_app"
echo "[+] Deploying aggressive logrotate configuration to $CONF_FILE"

sudo bash -c "cat <<EOF > $CONF_FILE
$APP_LOG_DIR/*.log {
    size 10M
    rotate 4
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF"

echo "[+] Validation of Configuration File:"
cat "$CONF_FILE"
echo ""
echo "[+] Setup Complete! Next, run ./simulate_growth.sh to generate traffic."
