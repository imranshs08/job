# Enterprise SRE Runbook: RHEL 8.10 `/var` Storage Saturation & Enterprise Remediation

---

## 📑 Table of Contents
1. [Architecture & Production Context](#-architecture--production-context)
2. [Why Services Fail: The `/var` Domino Cascade (e.g., chronyd, rsyslogd)](#-why-services-fail-the-var-domino-cascade)
3. [Phase 1: Lab Environment Provisioning](#-phase-1-lab-environment-provisioning-rhel-810)
4. [Phase 2: Deploying Simulated Enterprise Agents (MDATP, Qualys, Rundeck)](#-phase-2-installing--simulating-enterprise-agents)
5. [Phase 3: Inducing 100% `/var` Storage Saturation](#-phase-3-inducing-100-var-disk-space-exhaustion)
6. [Phase 4: SRE Incident Triage & Forensic Analysis (The War Room)](#-phase-4-emergency-incident-triage-the-war-room-first-aid)
7. [Phase 5: Emergency First-Aid (Zero-Downtime Log Truncation)](#-phase-5-emergency-first-aid-zero-downtime-truncation)
8. [Phase 6: Enterprise Permanent Remediation Architecture](#-phase-6-enterprise-permanent-remediation-architecture)
9. [Phase 7: End-to-End Validation & Load Testing](#-phase-7-validation--verification)
10. [Executive Summary & Senior DevOps Interview Traps](#-summary-of-best-practices--interview-takeaways)

---

## 🏢 Architecture & Production Context

In enterprise environments (finance, banking, health-tech, defense), production Red Hat Enterprise Linux (RHEL) servers are mandated to run security and operational agents:

| Tool / Agent | Default Storage Footprint | Risk Profile |
|---|---|---|
| **Microsoft Defender for Endpoint (`mdatp`)** | `/var/opt/microsoft/mdatp/` | Real-time inspection ring buffers, diagnostic dumps, scan engine crash dumps. |
| **Qualys Cloud Agent (`qualys-cloud-agent`)** | `/var/opt/qualys/qualys-cloud-agent/` | Local snapshot deltas, signature manifests, asset vulnerability database dumps. |
| **Rundeck Workload Automation** | `/var/lib/rundeck/` & `/var/log/rundeck/` | Execution logs for hundreds of scheduled jobs, JSON step traces, console output. |
| **System Logging (`rsyslogd` & `journald`)** | `/var/log/messages`, `/var/log/journal/` | Bursting debug events from agents eating up gigabytes per hour. |

---

## 💥 Why Services Fail: The `/var` Domino Cascade

When `/var` hits **100% disk usage**, the operating system suffers a catastrophic cascading failure:

### 1. `chronyd` (Network Time Protocol Daemon)
- **What it does:** Synchronizes the server clock down to microseconds with upstream NTP servers.
- **Why it crashes:** It continuously writes drift telemetry and clock offset state into `/var/lib/chrony/drift` and allocates sockets in `/var/run/chrony/`.
- **The Production Risk:** If `chronyd` fails and the system clock drifts even by a few seconds:
  - **TLS/SSL Handshakes Fail:** Certificates appear either "not yet valid" or "expired".
  - **Cloud Authentication Breaks:** OAuth tokens, JWTs, and Azure Managed Identity tokens get rejected.
  - **Distributed DB Outage:** PostgreSQL/CockroachDB/Kafka fail due to out-of-order consensus timestamps.

### 2. `rsyslogd` & `systemd-journald`
- **What it does:** Collects all kernel and service log entries.
- **Why it crashes:** Throws `fopen() failed for path: '/var/lib/rsyslog/imjournal.state.tmp': No space left on device`.
- **The Production Risk:** Audit compliance is violated, security events are lost, and diagnostic visibility is blinded.

### 3. Shell Sessions & Crontab
- **Why it fails:** New SSH logins fail because `/var/log/lastlog` and `/var/run/utmp` cannot be updated. Cron daemon skips scheduled execution because it cannot allocate spool lockfiles in `/var/spool/cron`.

---

## 🛠️ Phase 1: Lab Environment Provisioning (RHEL 8.10)

### 1.1 Provisioning with Automated Multi-SKU Failover (Azure CLI)

In cloud environments like Azure `eastus`, quota limits often cause `SkuNotAvailable` errors for `Standard_B2s`. This script automatically tests viable SKUs until provisioning succeeds:

```bash
# ------------------------------------------------------------------------------
# STEP 1.1: DEFINE LAB ENVIRONMENT PARAMETERS
# ------------------------------------------------------------------------------
RESOURCE_GROUP="rg-devops-lab"
LOCATION="eastus"
VM_NAME="rhel810-var-lab"
VNET_NAME="vnet-lab"
SUBNET_NAME="snet-lab"

# Create the Resource Group to isolate lab assets
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create the Virtual Network (10.0.0.0/16) and a dedicated Subnet (10.0.1.0/24)
az network vnet create \
  --resource-group $RESOURCE_GROUP \
  --name $VNET_NAME \
  --address-prefix 10.0.0.0/16 \
  --subnet-name $SUBNET_NAME \
  --subnet-prefix 10.0.1.0/24

# Candidate SKUs ordered by cost-efficiency and regional availability
CANDIDATE_SIZES=("Standard_D2s_v3" "Standard_B2ms" "Standard_D2as_v4" "Standard_D2s_v5" "Standard_B2s")

# Loop through candidate sizes to bypass regional capacity constraints
for SIZE in "${CANDIDATE_SIZES[@]}"; do
  echo "==> Attempting to provision VM with size: $SIZE..."
  if az vm create \
    --resource-group "$RESOURCE_GROUP" \
    --name "$VM_NAME" \
    --image "RedHat:RHEL:8_10:latest" \
    --size "$SIZE" \
    --admin-username rheladmin \
    --generate-ssh-keys \
    --vnet-name "$VNET_NAME" \
    --subnet "$SUBNET_NAME" \
    --public-ip-sku Standard; then
      echo "✅ Successfully deployed $VM_NAME with size $SIZE!"
      break
  else
    echo "⚠️ Capacity restricted for $SIZE in $LOCATION. Trying next SKU..."
  fi
done
```

---

### 1.2 Enterprise Disk Layout Verification

Connect via SSH:
```bash
# Obtain public IP address
az vm list-ip-addresses -g rg-devops-lab -n rhel810-var-lab --output table

# Connect as rheladmin
ssh -i ~/.ssh/id_rsa rheladmin@<PUBLIC_IP>

# Elevate privileges to root
sudo -i
```

Verify the native LVM partition layout:
```bash
# Inspect all filesystems and their mount points
df -hT
```

> [!NOTE]
> Azure's official RHEL 8.10 image (`RedHat:RHEL:8_10:latest`) already configures a dedicated enterprise LVM volume for `/var`:
> ```text
> Filesystem                Type  Size  Used Avail Use% Mounted on
> /dev/mapper/rootvg-varlv  xfs   8.0G  371M  7.7G   5% /var
> ```
> *Note: If you are running on custom bare-metal or local hypervisors where `/var` is unified under root `/`, create a dedicated loop device for `/var` as documented in older lab setups.*

---

## ⚡ Phase 2: Installing & Simulating Enterprise Agents

We will now recreate realistic directory structures and background daemons for Microsoft Defender for Endpoint (`mdatp`), Qualys Cloud Agent, and Rundeck.

```bash
# ------------------------------------------------------------------------------
# 2.1 SETUP MICROSOFT DEFENDER FOR ENDPOINT (MDATP) FOOTPRINT & SIMULATOR
# ------------------------------------------------------------------------------
# Create standard production directory paths for MDATP
mkdir -p /var/opt/microsoft/mdatp/log \
         /var/opt/microsoft/mdatp/crashdumps \
         /var/opt/microsoft/mdatp/wdavdaemon

# Deploy systemd unit simulating continuous real-time protection telemetry writes
cat << 'EOF' > /etc/systemd/system/mdatp-simulator.service
[Unit]
Description=Microsoft Defender for Endpoint Telemetry Simulator
After=network.target

[Service]
Type=simple
# Writes continuous inspection logs with realistic timestamps and random packet hashes
ExecStart=/bin/bash -c 'while true; do echo "[$(date --rfc-3339=ns)] [INFO] Real-time scan engine telemetry trace thread id $(shuf -i 1000-9999 -n 1) packet inspection payload hash: $(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 256)" >> /var/opt/microsoft/mdatp/log/wdavdaemon.log; sleep 0.05; done'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# ------------------------------------------------------------------------------
# 2.2 SETUP QUALYS CLOUD AGENT FOOTPRINT & SIMULATOR
# ------------------------------------------------------------------------------
# Create standard Qualys snapshot cache directories
mkdir -p /var/opt/qualys/qualys-cloud-agent/data/snapshots \
         /var/opt/qualys/qualys-cloud-agent/log

# Deploy systemd unit simulating periodic vulnerability manifest dumps (20MB every 15s)
cat << 'EOF' > /etc/systemd/system/qualys-simulator.service
[Unit]
Description=Qualys Cloud Agent Snapshot Simulator
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'while true; do dd if=/dev/urandom of=/var/opt/qualys/qualys-cloud-agent/data/snapshots/vuln_scan_manifest_$(date +%s).snap bs=1M count=20 2>/dev/null; sleep 15; done'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# ------------------------------------------------------------------------------
# 2.3 SETUP RUNDECK WORKLOAD AUTOMATION FOOTPRINT & SIMULATOR
# ------------------------------------------------------------------------------
# Create standard directories for Rundeck project execution output
mkdir -p /var/log/rundeck \
         /var/lib/rundeck/logs/rundeck/project-PROD-BATCH/job \
         /var/lib/rundeck/data

# Deploy systemd unit simulating batch execution log generation
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

# Reload systemd manager and enable all 3 background simulators
systemctl daemon-reload
systemctl enable --now mdatp-simulator.service qualys-simulator.service rundeck-simulator.service

# Confirm all 3 services are active and running
systemctl status mdatp-simulator qualys-simulator rundeck-simulator --no-pager
```

---

## 🔥 Phase 3: Inducing 100% `/var` Disk Space Exhaustion

Now accelerate the exhaustion to push `/var` to 100% capacity:

```bash
# Check current available space on /var before burst
df -h /var

# Rapidly fill the remaining space on /var using fallocate or dd
fallocate -l 3500M /var/log/messages.burst || dd if=/dev/zero of=/var/log/messages.burst bs=1M count=3500

# Push any remaining megabytes to hit absolute 100% saturation (0 bytes available)
dd if=/dev/zero of=/var/log/messages.burst2 bs=1M count=300 2>/dev/null || true

# Verify that /var is at 100% capacity
df -h /var
```

Expected output:
```text
Filesystem                   Size  Used Avail Use% Mounted on
/dev/mapper/rootvg-varlv     4.0G  4.0G  260K 100% /var
```

### Witnessing the Outage
```bash
# 1. Attempt to write to temporary storage (FAILS)
touch /var/tmp/incident-test.txt
# Output: touch: cannot touch '/var/tmp/incident-test.txt': No space left on device

# 2. Restart NTP time synchronization service (FAILS)
systemctl restart chronyd

# 3. Inspect system journal to observe write errors
journalctl -n 15 --no-pager
# Output includes:
# rsyslogd: imjournal: fopen() failed for path: '/var/lib/rsyslog/imjournal.state.tmp': No space left on device
# /bin/bash: line 0: echo: write error: No space left on device
```

---

## 🚨 Phase 4: Emergency Incident Triage (The War Room First-Aid)

When responding to an on-call alert for high disk utilization, follow this systematic procedure:

### Step 4.1: Check Inode vs Block Exhaustion
```bash
# Check storage block capacity
df -hT /var

# CRITICAL CHECK: Inode exhaustion (Often overlooked in SRE interviews!)
# If inodes hit 100%, no new files can be created even if df -h shows 50GB free!
df -ih /var
```

### Step 4.2: Find Top Storage Offenders
```bash
# Find top 10 largest directories within the /var filesystem (-x prevents crossing mount points)
du -xh /var | sort -rh | head -n 10

# Locate large individual files exceeding 50MB
find /var -xdev -type f -size +50M -exec ls -lh {} + | awk '{ print $9 ": " $5 }'
```

### Step 4.3: Detect Ghost Files ("Deleted but Held Open")
```bash
# Check for files that were deleted with 'rm', but space is NOT released because
# a running daemon still holds an active file descriptor:
lsof +L1 /var
# Alternative syntax:
lsof /var | grep -i "(deleted)"
```

---

## 🩹 Phase 5: Emergency First-Aid (Zero-Downtime Truncation)

### 🔬 Deep Dive: Linux Kernel Internals (Inodes, File Descriptors, & Truncation)

To understand why these commands are engineered this way, look at how the Linux kernel organizes storage:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            LINUX FILE ARCHITECTURE                          │
├───────────────────┬───────────────────────────────┬─────────────────────────┤
│ 1. Dentry (Name)  │ 2. Inode (Metadata)           │ 3. Data Blocks (Disk)   │
│ "service.log"     │ - Inode #1048576              │ [Block A] [Block B]     │
│                   │ - Permissions, Owner, Size    │ [Block C] [Block D]     │
│                   │ - Open FD Reference Count: 1  │ (Consuming physical GB) │
└───────────────────┴───────────────────────────────┴─────────────────────────┘
```

#### Why `rm -f /var/log/service.log` is Disastrous in Production:
1. `rm` is simply an **unlink** system call. It only removes the human-readable **Dentry** (the filename).
2. If an active process (Java Rundeck, MDATP daemon, or Rsyslog) still has the file open, it holds an active **File Descriptor (FD)** pointing directly to the Inode.
3. The kernel sees the file's **reference count is > 0**. Therefore, **the physical data blocks are NOT released!**
4. **The Critical Production Consequence:**
   - The file disappears from `ls`.
   - **`df -h /var` STILL SHOWS 100% DISK USAGE!**
   - You now have "ghost storage" that cannot be seen or easily freed without hunting down the PID via `lsof +L1 /var` or killing production processes.

#### Why `truncate -s 0` or `> file.log` is the Senior SRE Gold Standard:
1. The **Dentry** (filename) and **Inode** stay intact.
2. The kernel invokes `ftruncate()`, resets the file length to **0 bytes**, and **instantly releases all data blocks back to the free disk pool**.
3. The running daemon continues writing to its open File Descriptor without interruption starting from offset 0.
4. **`df -h /var` drops from 100% to normal levels within milliseconds** with **ZERO process crashes and ZERO downtime!**

---

### Executing Emergency Zero-Downtime Truncation:

```bash
# ------------------------------------------------------------------------------
# STEP 5.1: TRUNCATE STATIC BURST LOG GENERATORS
# ------------------------------------------------------------------------------
# Truncate test burst files to 0 bytes (releases blocks immediately)
truncate -s 0 /var/log/messages.burst
truncate -s 0 /var/log/messages.burst2 2>/dev/null || true

# ------------------------------------------------------------------------------
# STEP 5.2: ZERO-OUT ACTIVE DAEMON LOGS IN-PLACE WITHOUT SERVICE RESTARTS
# ------------------------------------------------------------------------------
# Using '>' opens the file in O_WRONLY | O_TRUNC mode.
# MDATP daemon and Rundeck keep writing uninterrupted without leaking file descriptors.
# '2>/dev/null || true' ensures defensive execution in automated pipelines.
> /var/opt/microsoft/mdatp/log/wdavdaemon.log 2>/dev/null || true
> /var/log/rundeck/service.log 2>/dev/null || true

# ------------------------------------------------------------------------------
# STEP 5.3: VERIFY RECOVERED CAPACITY INSTANTLY
# ------------------------------------------------------------------------------
# Confirm that disk blocks were released to the OS immediately
df -hT /var
```

### Production Impact Comparison Matrix:

| Action | Running Process Impact | Is Disk Space Freed Instantly? | Production Outage Risk |
|---|---|---|---|
| **`rm -f logfile.log`** | Process continues writing to an invisible open File Descriptor. | ❌ **NO**. Disk remains at 100% until process is killed/restarted. | ⚠️ **HIGH**. Causes FD leaks and necessitates service restarts. |
| **`truncate -s 0 logfile.log`** or **`> logfile.log`** | Process keeps running seamlessly; next log line writes at offset 0. | ✅ **YES**. Storage is reclaimed in milliseconds. | 🛡️ **ZERO DOWNTIME**. Clean, non-disruptive remediation. |

---

## 🛡️ Phase 6: Enterprise Permanent Remediation Architecture

A true enterprise solution prevents recurrence using a 5-pillar approach:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   ENTERPRISE /var REMEDIATION ARCHITECTURE                   │
├─────────────────┬─────────────────┬──────────────────┬──────────────────────┤
│ 1. Journald     │ 2. Logrotate    │ 3. Rundeck       │ 4. Storage Sentinel  │
│ Strict Caps     │ Agent Policies  │ Execution Purge  │ Automated Watchdog   │
│ (500M max limit)│ (maxsize 50M)   │ (14-day prune)   │ (5-min Timer Auto-Rx)│
└─────────────────┴─────────────────┴──────────────────┴──────────────────────┘
```

### Pillar 1: Harden `systemd-journald` Retention & Storage Limits

#### 🧠 The Underlying Architectural Problem: Default Journald Behavior
By default on RHEL 8.10, `systemd-journald` uses an unconstrained rule:
- It allows journal logs to consume **up to 10% of the entire filesystem** (capped at a massive **4GB**).
- If your `/var` is 8GB, journald alone will greedily claim up to **800MB - 4GB**!
- If noisy security agents (like MDATP or Qualys) log thousands of debug lines per minute, journald expands rapidly until it chokes out application write threads.

#### 📁 Why Use Drop-In Configuration (`/etc/systemd/journald.conf.d/`)?
In enterprise Linux engineering, **never directly edit `/etc/systemd/journald.conf`**:
- Package upgrades via `dnf`/`yum` can overwrite `/etc/systemd/journald.conf` or trigger `.rpmnew` conflicts.
- Creating a drop-in override (`00-disk-limits.conf` inside `journald.conf.d/`) ensures modular, immutable configuration that survives OS patch cycles and conforms to Infrastructure-as-Code (Ansible/Puppet) best practices.

```bash
# ------------------------------------------------------------------------------
# STEP 6.1.1: CREATE SYSTEMD JOURNAL DROP-IN OVERRIDE DIRECTORY
# ------------------------------------------------------------------------------
# Any file ending in .conf inside this directory overrides default journal settings
mkdir -p /etc/systemd/journald.conf.d

# ------------------------------------------------------------------------------
# STEP 6.1.2: APPLY HARD DISK LIMITS AND RETENTION POLICIES
# ------------------------------------------------------------------------------
cat << 'EOF' > /etc/systemd/journald.conf.d/00-disk-limits.conf
[Journal]
# Enforces writing logs persistently to /var/log/journal/ (survives reboots)
Storage=persistent

# Compresses log data objects larger than default threshold using XZ/LZ4
Compress=yes

# HARD MAXIMUM: Cap total journal storage across all archived files to 500MB
SystemMaxUse=500M

# SAFETY BUFFER: Ensure journald stops writing if /var has less than 500MB free
SystemKeepFree=500M

# ROTATION TRIGGER: Rotate active journal file once it reaches 50MB
SystemMaxFileSize=50M

# RETENTION EXPIRATION: Automatically purge archived journals older than 14 days
MaxRetentionSec=14day
EOF

# ------------------------------------------------------------------------------
# STEP 6.1.3: RESTART JOURNALD & PERFORM IMMEDIATE PHYSICAL VACUUM
# ------------------------------------------------------------------------------
# Restart daemon to compile and load the new drop-in rules
systemctl restart systemd-journald

# Force immediate garbage collection: purges oldest journal entries until disk usage <= 500M
journalctl --vacuum-size=500M

# (Alternative/Supplementary) Purge journals older than retention limit immediately
journalctl --vacuum-time=14d
```

---

#### 🔍 Parameter-by-Parameter Breakdown & Production Impact Analysis:

| Configuration Parameter | Value | Technical Mechanism | Production Impact & SRE Why |
|---|---|---|---|
| **`Storage=persistent`** | `persistent` | Stores journals under `/var/log/journal/`. | Ensures critical post-mortem crash logs survive unexpected kernel panics or power outages. |
| **`Compress=yes`** | `yes` | Compresses binary log payloads using LZ4/ZSTD algorithms. | Reduces physical disk usage by up to **60-70%** for repetitive agent messages. |
| **`SystemMaxUse`** | `500M` | Sets a strict ceiling on the total disk space all journal files can occupy. | **Prevents 100% Outage:** Stops journald from expanding to the 4GB default, saving `/var` from saturation. |
| **`SystemKeepFree`** | `500M` | Instructs journald to stop writing if free space on `/var` drops below 500MB. | **Protects Other Daemons:** Guarantees a 500MB survival runway for `chronyd`, `sshd`, and PID files. |
| **`SystemMaxFileSize`** | `50M` | Dictates the maximum size of a single journal file before it is sealed and rotated. | Prevents individual corrupt journal files from locking large chunks of disk space. |
| **`MaxRetentionSec`** | `14day` | Time-based garbage collection: drops entries older than 2 weeks. | Enforces compliance data retention without manual cron scripts. |
| **`journalctl --vacuum-size`** | `500M` | Synchronously executes garbage collection to truncate and delete old archived chunks. | **Instant Emergency Recovery:** Instantly frees multiple gigabytes of space during an active P1/P0 triage. |

---

### Pillar 2: Configure Dedicated Agent Logrotate Policies

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
    # copytruncate allows rotating active logs without restarting Rundeck JVM
    copytruncate
    # Force rotation as soon as file hits 100M even before daily schedule
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

#### 3. Qualys Snapshot Auto-Cleaner (`/etc/cron.daily/qualys-snapshot-cleanup`)
```bash
cat << 'EOF' > /etc/cron.daily/qualys-snapshot-cleanup
#!/bin/bash
# Remove vulnerability scan snapshot deltas older than 7 days
find /var/opt/qualys/qualys-cloud-agent/data/snapshots/ -type f -name "*.snap" -mtime +7 -delete 2>/dev/null || true
exit 0
EOF

chmod +x /etc/cron.daily/qualys-snapshot-cleanup

# Test all logrotate syntax without executing
logrotate -d /etc/logrotate.conf
```

---

### Pillar 3: Rundeck Automated Execution History Purger

Rundeck creates thousands of JSON/XML step executions under `/var/lib/rundeck/logs/`. We automate retention enforcement:

```bash
cat << 'EOF' > /usr/local/bin/rundeck-cleaner.sh
#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/var/lib/rundeck/logs/rundeck"
RETENTION_DAYS=14

echo "[$(date)] Starting Rundeck Execution Log Purge (> ${RETENTION_DAYS} days)..."

if [ -d "$LOG_DIR" ]; then
    # Purge execution files older than 14 days
    find "$LOG_DIR" -type f -name "*.log" -mtime +"$RETENTION_DAYS" -delete
    # Remove empty job directories
    find "$LOG_DIR" -type d -empty -delete
    echo "[$(date)] Cleanup completed successfully."
fi
EOF

chmod 750 /usr/local/bin/rundeck-cleaner.sh

# Schedule daily execution at 02:00 AM via cron
echo "0 2 * * * root /usr/local/bin/rundeck-cleaner.sh > /dev/null 2>&1" > /etc/cron.d/rundeck-cleaner
```

---

### Pillar 4: LVM Online Filesystem Expansion (Without Downtime)

When genuine workload growth requires extending `/var`:

```bash
# 1. Check Volume Group free space
vgs

# 2. Check current Logical Volume size
lvs /dev/vg_var/lv_var 2>/dev/null || lvs /dev/mapper/rootvg-varlv

# 3. Expand the LVM Logical Volume and online-resize the XFS filesystem simultaneously (-r flag):
# If using the Azure native rootvg:
# lvextend -r -L +2G /dev/mapper/rootvg-varlv
# If using custom loopback vg_var:
# lvextend -r -L +1G /dev/vg_var/lv_var

# 4. Verify expanded capacity immediately available:
df -hT /var
```

---

### Pillar 5: Enterprise Storage Sentinel Watchdog (Systemd Timer)

Deploy an autonomous early-warning and self-healing watchdog that runs every 5 minutes:

```bash
# 1. Deploy the Sentinel script
cat << 'EOF' > /usr/local/bin/var-disk-sentinel.sh
#!/usr/bin/env bash
set -euo pipefail

TARGET_MOUNT="/var"
CRITICAL_THRESHOLD=90

# Calculate current utilization percentage
CURRENT_USAGE=$(df -P "$TARGET_MOUNT" | awk 'NR==2 {gsub("%","",$5); print $5}')

if [ "$CURRENT_USAGE" -ge "$CRITICAL_THRESHOLD" ]; then
    logger -t var-sentinel -p user.crit "EMERGENCY: ${TARGET_MOUNT} is at ${CURRENT_USAGE}%. Auto-triage initiated."
    
    # Auto-action 1: Zero out known oversized runaway agent logs
    for logfile in /var/opt/microsoft/mdatp/log/wdavdaemon.log /var/log/rundeck/service.log; do
        if [ -f "$logfile" ] && [ $(stat -c%s "$logfile") -gt 52428800 ]; then
            > "$logfile"
            logger -t var-sentinel "Truncated runaway log: $logfile"
        fi
    done
    
    # Auto-action 2: Force journald vacuum down to 200MB
    journalctl --vacuum-size=200M
    
    # Auto-action 3: Trigger emergency logrotate run
    /usr/sbin/logrotate -f /etc/logrotate.conf 2>/dev/null || true
    
    NEW_USAGE=$(df -P "$TARGET_MOUNT" | awk 'NR==2 {print $5}')
    logger -t var-sentinel "Auto-triage completed. Recovered usage: ${NEW_USAGE}"
fi
EOF

chmod 750 /usr/local/bin/var-disk-sentinel.sh

# 2. Create the Systemd Service definition
cat << 'EOF' > /etc/systemd/system/var-sentinel.service
[Unit]
Description=Storage Sentinel Watchdog for /var
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/var-disk-sentinel.sh
EOF

# 3. Create the Systemd Timer (Every 5 minutes)
cat << 'EOF' > /etc/systemd/system/var-sentinel.timer
[Unit]
Description=Run Storage Sentinel Watchdog every 5 minutes

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
EOF

# 4. Activate the Sentinel Timer
systemctl daemon-reload
systemctl enable --now var-sentinel.timer
```

---

## 🎯 Phase 7: Validation & Verification

Confirm the self-healing sentinel and all policies are functioning:

```bash
# 1. Verify Sentinel Timer is scheduled
systemctl list-timers var-sentinel.timer

# 2. Check /var disk space is healthy
df -hT /var

# 3. Restart chronyd and verify successful operation
systemctl restart chronyd
systemctl status chronyd --no-pager

# 4. Inspect system log for Sentinel telemetry
journalctl -t var-sentinel -n 20 --no-pager
```

---

## 📋 Summary of Best Practices & Interview Takeaways

| Scenario / Interview Question | Junior Answer (Fails) | Senior SRE Answer (Passes) |
|---|---|---|
| **"How do you free space from a rapidly growing log file?"** | `rm -f /var/log/service.log` | `truncate -s 0 /var/log/service.log` or `> /var/log/service.log`. Explaining that `rm` leaks open file descriptors if the process is running. |
| **"`df -h` shows 100% full, but `du -sh` shows only 10GB used. What is happening?"** | "File system is corrupted; reboot the server." | Unlinked files are still open by a process. Use `lsof +L1 /var` or `lsof /var \| grep deleted` to find the holding PID and signal/reload it. |
| **"`df -h` shows 40% usage, but users get 'No space left on device'. Why?"** | "The hard disk has bad sectors." | Inode exhaustion. Check `df -ih`. Rundeck or application micro-logs created millions of 0-byte files, consuming all metadata inodes. |
| **"Why is `chronyd` failing when `/var` is full?"** | "NTP doesn't depend on disk." | `chronyd` writes drift metrics to `/var/lib/chrony/drift` and sockets to `/var/run/chrony/`. Outage leads to clock drift and TLS certificate failures across the fleet. |
| **"How do you prevent logrotate from crashing services while rotating?"** | Stop the service, rotate, start service. | Use `copytruncate` directive in logrotate configuration to copy and zero out the live log without stopping the daemon. |
