# Enterprise SRE Runbook: RHEL 8.10 `/var` Storage Saturation & Enterprise Remediation

---

## 📑 Architecture Overview

In corporate enterprise environments (financial institutions, health-tech, telecom), production RHEL servers almost invariably host mandatory endpoint security agents and automation tooling:
- **Microsoft Defender for Endpoint (`mdatp`)**: Generates real-time RTP logs, trace ring buffers, telemetry caches (`/var/opt/microsoft/mdatp/`).
- **Qualys Cloud Agent (`qualys-cloud-agent`)**: Manifests, signature snapshots, scan deltas (`/var/opt/qualys/qualys-cloud-agent/`).
- **Rundeck Workload Automation**: Project executions, workflow execution logs, node dispatches, embedded database H2 dumps (`/var/lib/rundeck/` & `/var/log/rundeck/`).

When `/var` hits **100% capacity**, the system experiences severe cascading failure:
1. System logs (`/var/log/messages`, `journald`) stop recording or lock up disk write threads.
2. PID and lockfiles cannot be allocated in `/var/run` (or `/run`).
3. Services cannot write temporary transaction caches (`/var/tmp`), leading to **failed logins, SSH session termination, cron stoppage**, and out-of-storage cascades mimicking OOM behavior.

---

## 🛠️ Phase 1: Lab Environment Provisioning (RHEL 8.10)

### 1.1 Provisioning the VM

You can provision RHEL 8.10 via **Azure CLI**, **AWS CLI**, or **Local Hyper-V / Vagrant / KVM / VirtualBox**.

#### Option A: Azure CLI
```bash
# Set variables
RESOURCE_GROUP="rg-devops-lab"
LOCATION="eastus"
VM_NAME="rhel810-var-lab"
VNET_NAME="vnet-lab"
SUBNET_NAME="snet-lab"

az group create --name $RESOURCE_GROUP --location $LOCATION

az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name $VNET_NAME \
  --address-prefix 10.0.0.0/16 \
  --subnet-name $SUBNET_NAME \
  --subnet-prefix 10.0.1.0/24

az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image "RedHat:RHEL:8_10:latest" \
  --size Standard_B2s \
  --admin-username rheladmin \
  --generate-ssh-keys \
  --vnet-name $VNET_NAME \
  --subnet $SUBNET_NAME \
  --public-ip-sku Standard
```

#### Option B: Local Hyper-V / KVM / VirtualBox (Vagrantfile)
```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "generic/rhel8" # or local RHEL 8.10 ISO
  config.vm.hostname = "rhel810-lab"
  config.vm.network "private_network", ip: "192.168.56.20"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "4096"
    vb.cpus = 2
  end
end
```

---

### 1.2 Enterprise Disk Layout Setup (Dedicated `/var` LVM)

To recreate standard enterprise security compliance (CIS Benchmark / DISA STIG), `/var` should reside on its own Logical Volume. For this lab simulation, let's create a dedicated 5GB or 10GB virtual disk or loopback mount for `/var` so it can be filled rapidly.

```bash
# Connect as root
sudo -i

# Verify OS Version
cat /etc/redhat-release
# Output: Red Hat Enterprise Linux release 8.10 (Ootpa)

# If /var is already part of root partition, create a dedicated 4GB loop device for /var
# to accurately replicate a standalone /var partition:
mkdir -p /mnt/var_disk_backing
dd if=/dev/zero of=/mnt/var_disk_backing/var.img bs=1M count=4096

# Setup Loopback device & LVM
losetup /dev/loop10 /mnt/var_disk_backing/var.img
pvcreate /dev/loop10
vgcreate vg_var /dev/loop10
lvcreate -l 100%FREE -n lv_var vg_var
mkfs.xfs /dev/vg_var/lv_var

# Temporarily migrate current /var content
mkdir -p /mnt/new_var
mount /dev/vg_var/lv_var /mnt/new_var
rsync -avxHAX /var/ /mnt/new_var/
umount /mnt/new_var

# Mount as /var in /etc/fstab
UUID=$(blkid -s UUID -o value /dev/vg_var/lv_var)
echo "UUID=${UUID} /var xfs defaults 0 0" >> /etc/fstab
mount -a

# Confirm /var is on its own mount
df -hT /var
```

---

## ⚡ Phase 2: Installing & Simulating Enterprise Agents

In true enterprise environments, you have `mdatp`, `qualys-cloud-agent`, and `rundeck`. Let's create realistic directory structures, mock services, and simulated agent behaviors.

### 2.1 Microsoft Defender for Endpoint (`mdatp`) Footprint
```bash
# Standard directory layout for mdatp on RHEL
mkdir -p /var/opt/microsoft/mdatp/log
mkdir -p /var/opt/microsoft/mdatp/crashdumps
mkdir -p /var/opt/microsoft/mdatp/wdavdaemon

# Create a mock daemon service that writes continuous verbose diagnostics
cat << 'EOF' > /etc/systemd/system/mdatp-simulator.service
[Unit]
Description=Microsoft Defender for Endpoint Simulator
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'while true; do echo "[$(date --rfc-3339=ns)] [INFO] Real-time scan engine telemetry trace thread id $(shuf -i 1000-9999 -n 1) packet inspection payload hash: $(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 256)" >> /var/opt/microsoft/mdatp/log/wdavdaemon.log; sleep 0.05; done'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now mdatp-simulator.service
```

### 2.2 Qualys Cloud Agent Footprint
```bash
# Standard directory layout for Qualys Cloud Agent
mkdir -p /var/opt/qualys/qualys-cloud-agent/data/snapshots
mkdir -p /var/opt/qualys/qualys-cloud-agent/log

# Create a mock Qualys daemon that dumps daily scan snapshots
cat << 'EOF' > /etc/systemd/system/qualys-simulator.service
[Unit]
Description=Qualys Cloud Agent Simulator
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'while true; do dd if=/dev/urandom of=/var/opt/qualys/qualys-cloud-agent/data/snapshots/vuln_scan_manifest_$(date +%s).snap bs=1M count=20 2>/dev/null; sleep 30; done'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now qualys-simulator.service
```

### 2.3 Rundeck Workload Automation Footprint
```bash
# Standard directory layout for Rundeck on Linux
mkdir -p /var/log/rundeck
mkdir -p /var/lib/rundeck/logs/rundeck/project-PROD-BATCH/job
mkdir -p /var/lib/rundeck/data

# Create Rundeck log generator simulating unmanaged execution logs
cat << 'EOF' > /etc/systemd/system/rundeck-simulator.service
[Unit]
Description=Rundeck Automation Engine Simulator
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'JOB_ID=10928; while true; do dd if=/dev/urandom of="/var/lib/rundeck/logs/rundeck/project-PROD-BATCH/job/${JOB_ID}/execution-$(date +%s%N).log" bs=512K count=10 2>/dev/null; echo "[$(date)] Job execution output log trace..." >> /var/log/rundeck/service.log; sleep 2; done'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now rundeck-simulator.service
```

---

## 🔥 Phase 3: Inducing 100% `/var` Disk Space Exhaustion

To expedite the outage and witness the crash cascade:

```bash
# Accelerate log explosion to hit 100% usage within seconds
fallocate -l 3500M /var/log/messages.burst || dd if=/dev/zero of=/var/log/messages.burst bs=1M count=3500

# Verify disk state
df -h /var
```

### The Outage Symptoms:
1. `df -h /var` shows `Use% 100%` and `Avail 0`.
2. Running `touch /var/tmp/test.txt` yields `No space left on device`.
3. Try starting a service:
   ```bash
   systemctl restart chronyd
   ```
   *Fails with `Failed to write chrony state: No space left on device`*.
4. Look at `journalctl -xe` or system logs: dropped packets, failed authentication tokens, auditd buffer full alerts (`auditd: audit_backlog_limit exceeded`).

---

## 🚨 Phase 4: Emergency Incident Triage (The War Room First-Aid)

When an on-call engineer receives an alert: **"CRITICAL: /var filesystem at 100% on rhel-prod-app01"**:

### Step 4.1: Identify Mounts and Inodes
```bash
# Check block storage usage
df -hT /var

# CRITICAL CHECK: Inode exhaustion (Often overlooked - disk says 90% but files cannot be created!)
df -ih /var
```

### Step 4.2: Identify the Top Offenders (Top Space Consumers)
```bash
# Find top 10 largest directories in /var without crossing filesystem boundaries (-x flag)
du -xh /var | sort -rh | head -n 15

# Find largest individual files (> 100MB)
find /var -xdev -type f -size +100M -exec ls -lh {} + | awk '{ print $9 ": " $5 }'
```

### Step 4.3: The "Deleted but Held Open" Gotcha (Ghost Disk Usage)
> [!WARNING]
> **Junior Mistake**: Running `rm -f /var/log/large_file.log`. If a running process still has a file descriptor open, the file blocks are NOT released by Linux! `df -h` will still show 100% full, but `du -sh` will show empty!

```bash
# Check for unlinked open files consuming space
lsof +L1 /var
# or:
lsof /var | grep -i "(deleted)"
```

### Step 4.4: Safe Emergency Truncation (Zeroing Files without Crashing Processes)
Instead of deleting files that active daemons are writing to, **truncate them to 0 bytes**:

```bash
# Truncate large files safely:
truncate -s 0 /var/log/messages.burst

# For any active log file held by a process:
> /var/opt/microsoft/mdatp/log/wdavdaemon.log
> /var/log/rundeck/service.log

# Verify space was instantly freed without restarting the processes:
df -h /var
```

---

## 🛡️ Phase 5: Enterprise Permanent Remediation Architecture

A permanent enterprise fix requires a 5-pillar strategy:
1. **Pillar 1: Systemd Journald Caps & Auto-Vacuum**
2. **Pillar 2: Enterprise Logrotate Configuration (Rundeck, Qualys, MDATP)**
3. **Pillar 3: Rundeck Built-in Execution Cleanup Automation**
4. **Pillar 4: Dynamic LVM Volume Extension & Filesystem Resizing**
5. **Pillar 5: Automated Disk Sentinel Watchdog (Early Warning & Auto-Triage)**

---

### Pillar 1: Harden `systemd-journald` Retention
By default, `systemd-journald` can consume up to 10% of the filesystem or 4GB.

```bash
# Edit /etc/systemd/journald.conf
cat << 'EOF' > /etc/systemd/journald.conf.d/00-disk-limits.conf
[Journal]
Storage=persistent
Compress=yes
SystemMaxUse=500M
SystemKeepFree=1G
SystemMaxFileSize=50M
MaxRetentionSec=14day
EOF

# Restart journald and trigger immediate vacuum
systemctl restart systemd-journald
journalctl --vacuum-size=500M
```

---

### Pillar 2: Configure Enterprise Logrotate Policies
Create dedicated `/etc/logrotate.d/` configurations for all agents.

#### 1. Rundeck Logrotate (`/etc/logrotate.d/rundeck`)
```bash
cat << 'EOF' > /etc/logrotate.d/rundeck
/var/log/rundeck/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
    maxsize 100M
}
EOF
```

#### 2. Microsoft Defender for Endpoint Logrotate (`/etc/logrotate.d/mdatp`)
```bash
cat << 'EOF' > /etc/logrotate.d/mdatp
/var/opt/microsoft/mdatp/log/*.log {
    daily
    rotate 5
    compress
    missingok
    notifempty
    copytruncate
    maxsize 50M
}
EOF
```

#### 3. Qualys Cloud Agent Snapshot Pruning
Qualys snapshots need daily retention pruning:
```bash
cat << 'EOF' > /etc/cron.daily/qualys-snapshot-cleanup
#!/bin/bash
# Remove Qualys snapshot manifests older than 7 days
find /var/opt/qualys/qualys-cloud-agent/data/snapshots/ -type f -name "*.snap" -mtime +7 -delete
exit 0
EOF
chmod +x /etc/cron.daily/qualys-snapshot-cleanup
```

Test all logrotate rules:
```bash
logrotate -d /etc/logrotate.conf  # Dry run
logrotate -f /etc/logrotate.conf  # Force execution
```

---

### Pillar 3: Rundeck Execution Log Cleaner Architecture
Rundeck generates thousands of JSON/XML execution logs under `/var/lib/rundeck/logs/`.

#### Enterprise Cleaner Script (`/usr/local/bin/rundeck-cleaner.sh`)
```bash
cat << 'EOF' > /usr/local/bin/rundeck-cleaner.sh
#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/var/lib/rundeck/logs/rundeck"
RETENTION_DAYS=14

echo "[$(date)] Starting Rundeck Execution Log Purge (Older than ${RETENTION_DAYS} days)..."

if [ -d "$LOG_DIR" ]; then
    # Purge execution log files older than retention policy
    find "$LOG_DIR" -type f -name "*.log" -mtime +"$RETENTION_DAYS" -delete
    # Remove empty directories
    find "$LOG_DIR" -type d -empty -delete
    echo "[$(date)] Rundeck Execution Log Purge Completed Successfully."
else
    echo "[WARN] Directory ${LOG_DIR} does not exist. Skipping."
fi
EOF

chmod 750 /usr/local/bin/rundeck-cleaner.sh

# Add to root crontab (runs at 02:00 AM daily)
echo "0 2 * * * root /usr/local/bin/rundeck-cleaner.sh > /var/log/rundeck-cleaner.log 2>&1" > /etc/cron.d/rundeck-cleaner
```

---

### Pillar 4: LVM Online Filesystem Expansion (Without Downtime)

When `/var` genuinely requires more capacity in production:

```bash
# 1. Inspect Volume Group capacity
vgs
lvs

# 2. If you added physical disk to VG:
# pvcreate /dev/sdX
# vgextend vg_var /dev/sdX

# 3. Extend the Logical Volume and underlying XFS filesystem online:
# Note: For XFS use -r (resizefs) flag with lvextend:
lvextend -r -L +2G /dev/vg_var/lv_var

# Verify the new expanded capacity
df -hT /var
```

---

### Pillar 5: Automated Enterprise Disk Sentinel & Early Warning System

Deploy an automated watchdog script that checks `/var` every 5 minutes. If usage exceeds 85%, it alerts SRE/Monitoring; if it hits 92%, it triggers automated triage/truncation.

```bash
cat << 'EOF' > /usr/local/bin/var-disk-sentinel.sh
#!/usr/bin/env bash
set -euo pipefail

TARGET_MOUNT="/var"
WARNING_THRESHOLD=80
CRITICAL_THRESHOLD=90

CURRENT_USAGE=$(df -P "$TARGET_MOUNT" | awk 'NR==2 {gsub("%","",$5); print $5}')

logger -t var-sentinel "Current ${TARGET_MOUNT} capacity: ${CURRENT_USAGE}%"

if [ "$CURRENT_USAGE" -ge "$CRITICAL_THRESHOLD" ]; then
    logger -t var-sentinel -p user.crit "EMERGENCY: ${TARGET_MOUNT} is at ${CURRENT_USAGE}%. Executing emergency auto-triage."
    
    # 1. Truncate simulated/known oversized agent logs
    for logfile in /var/opt/microsoft/mdatp/log/wdavdaemon.log /var/log/rundeck/service.log; do
        if [ -f "$logfile" ] && [ $(stat -c%s "$logfile") -gt 52428800 ]; then
            > "$logfile"
            logger -t var-sentinel "Truncated large log: $logfile"
        fi
    done
    
    # 2. Vacuum systemd journal to 200M immediately
    journalctl --vacuum-size=200M
    
    # 3. Trigger emergency logrotate
    /usr/sbin/logrotate -f /etc/logrotate.conf
    
    logger -t var-sentinel "Emergency auto-triage complete. New usage: $(df -P "$TARGET_MOUNT" | awk 'NR==2 {print $5}')"
fi
EOF

chmod 750 /usr/local/bin/var-disk-sentinel.sh

# Setup Systemd Timer (Every 5 minutes)
cat << 'EOF' > /etc/systemd/system/var-sentinel.service
[Unit]
Description=Storage Sentinel Watchdog for /var

[Service]
Type=oneshot
ExecStart=/usr/local/bin/var-disk-sentinel.sh
EOF

cat << 'EOF' > /etc/systemd/system/var-sentinel.timer
[Unit]
Description=Run Storage Sentinel Watchdog every 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now var-sentinel.timer
```

---

## 🎯 Phase 6: Validation & Verification

Run these commands to prove the solution works under heavy load:

```bash
# 1. Check timer status
systemctl list-timers var-sentinel.timer

# 2. Trigger high load again
dd if=/dev/zero of=/var/opt/microsoft/mdatp/log/wdavdaemon.log bs=1M count=1500

# 3. Check /var usage before sentinel runs
df -h /var

# 4. Manually invoke sentinel
/usr/local/bin/var-disk-sentinel.sh

# 5. Inspect syslog to verify automated rescue
journalctl -t var-sentinel -n 20

# 6. Verify space recovered
df -h /var
```

---

## 📋 Summary of Best Practices & Interview Takeaways

| Incident Vector | Bad Approach (Rookie Mistake) | Enterprise SRE Standard |
|---|---|---|
| **High disk usage** | Deleting active file (`rm log.txt`) | Truncating file (`> log.txt` or `truncate -s 0`) |
| **Space not freeing** | Rebooting server blindly | `lsof +L1 /var` to locate deleted file descriptors and restart only that PID |
| **Log rotation** | Relying on default logrotate | Enforcing `maxsize`, `copytruncate`, and retention limits in `/etc/logrotate.d/` |
| **Journald bloat** | Disabling journald | Setting `SystemMaxUse=500M` in `journald.conf.d/` and auto-vacuuming |
| **Rundeck executions** | Manual GUI purging | Automated cron/API execution pruner |
| **Disk capacity** | Single flat `/` partition | Dedicated LVM `/var` and `/var/log` with dynamic LVM online growth (`lvextend -r`) |
