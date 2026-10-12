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

#### 📊 How to Check `systemd-journald` Disk Consumption at Any Given Moment:

```bash
# ------------------------------------------------------------------------------
# METHOD 1: NATIVE SRE QUERY (Instant total of archived & active journals)
# ------------------------------------------------------------------------------
# Queries systemd-journald directly for total allocated disk footprint
journalctl --disk-usage
# Output example: Archived and active journals take up 320.0M in the file system.

# ------------------------------------------------------------------------------
# METHOD 2: PHYSICAL FILESYSTEM CONSUMPTION CHECK VIA DU
# ------------------------------------------------------------------------------
# Check total size of persistent journal directory on disk
du -sh /var/log/journal/

# List individual active and archived .journal files ordered by size
ls -lhS /var/log/journal/$(cat /etc/machine-id)/

# ------------------------------------------------------------------------------
# METHOD 3: CHECK JOURNALD ACTIVE RUNTIME ENFORCEMENT & LOG LIMITS
# ------------------------------------------------------------------------------
# View live telemetry and cap enforcement calculated by the daemon
systemctl status systemd-journald | grep -E "using|capped"
# Output example:
# System Journal (/var/log/journal/...) is currently using 320.0M.
# Maximum System Journal size has been capped at 500.0M.

# ------------------------------------------------------------------------------
# METHOD 4: EMERGENCY ON-DEMAND VACUUM & VERIFICATION
# ------------------------------------------------------------------------------
# Immediately force journald to reclaim space down to 500MB
journalctl --vacuum-size=500M

# Purge any archived logs older than 7 days
journalctl --vacuum-time=7d
```

---

### Pillar 2: Configure Dedicated Agent Logrotate Policies

#### 🧠 The Architectural Challenge: The Java/JVM & Daemon File Locking Trap
Java applications (like **Rundeck**, Jenkins, Elasticsearch) and continuous security agents (like **MDATP**) open their log files on startup and **never close their file handles**. 

If standard logrotate moves or renames the active file (`mv service.log service.log.1`), the JVM continues writing to the old file descriptor pointing to the renamed file, completely ignoring the new file!
- **Rookie "Fix":** Restart the application daemon after every rotation (`postrotate systemctl restart service`).
- **Production Failure:** Restarting Rundeck or MDATP drops active automation pipelines, aborts in-flight deployments, and causes system interruptions.
- **Enterprise SRE Solution:** Use **`copytruncate`**!

---

#### 1. Rundeck Enterprise Logrotate (`/etc/logrotate.d/rundeck`)

```bash
cat << 'EOF' > /etc/logrotate.d/rundeck
/var/log/rundeck/*.log {
    # Frequency: Evaluated once per day by the system logrotate cron/timer
    daily
    
    # Retention Count: Retain 7 rotated log generations before permanently purging oldest
    rotate 7
    
    # Storage Optimization: Gzip compress (.gz) rotated archives to save ~85-90% disk space
    compress
    
    # Safety Buffer: Postpone compression of the most recent rotated file until next cycle
    # (prevents corrupting files if processes take a few seconds to finish writing)
    delaycompress
    
    # Resiliency: Do not throw errors or fail execution if the log file is missing
    missingok
    
    # Efficiency: Do not rotate or create empty archives if the log contains 0 bytes
    notifempty
    
    # ZERO-DOWNTIME ROTATION: Copy active file to archive, then truncate original in-place
    # (JVM continues writing seamlessly; NO SERVICE RESTARTS REQUIRED!)
    copytruncate
    
    # EMERGENCY OVERRIDE: Force immediate rotation if file reaches 100MB even before daily schedule
    maxsize 100M
}
EOF
```

---

#### 🔍 Directive-by-Directive Breakdown & Production Impact Analysis:

| Directive | What It Does (Technical Mechanism) | Production Impact & SRE Why |
|---|---|---|
| **`/var/log/rundeck/*.log`** | Wildcard path matching all log outputs in the directory. | Automatically captures newly introduced Rundeck project and service logs without manual updates. |
| **`daily`** | Enforces evaluation on a daily schedule. | Prevents logs from growing unchecked across weeks; ensures fresh daily audit boundaries. |
| **`rotate 7`** | Keeps exactly 7 historical archive files (`.1.gz` through `.7.gz`) and purges the 8th. | **Predictable Capacity Planning:** Caps total historical directory footprint (e.g., `7 * 100MB max = ~700MB` uncompressed, `<100MB` compressed). |
| **`compress`** | Pipes rotated files through gzip compression. | **Saves 85% Disk Space:** Text logs compress exceptionally well, turning 100MB logs into ~10-15MB. |
| **`delaycompress`** | Leaves `service.log.1` uncompressed; compresses it to `service.log.2.gz` on the *next* rotation. | **Prevents File Corruption:** Solves race conditions where daemons or tailing monitoring agents still read the tail of the rotated file during rotation. |
| **`missingok`** | Suppresses logrotate failure codes if the file does not exist. | **Automation Safety:** Prevents cron alert noise and stops systemd logrotate timers from failing when jobs haven't logged yet. |
| **`notifempty`** | Skips rotation if the file is 0 bytes. | **Avoids Clutter:** Prevents generating useless sequences of empty `.1.gz`, `.2.gz` files when systems are idle. |
| **`copytruncate`** | 1. Copies active file to backup.<br>2. Immediately truncates original file to 0 bytes in-place (`truncate -s 0`). | **ZERO DOWNTIME / NO JVM RESTARTS:** The running JVM never loses its file descriptor. Production jobs never fail during log management. |
| **`maxsize 100M`** | Triggers rotation if file hits 100MB, even if 24 hours haven't elapsed. | **Shield Against Log Explosions:** If Rundeck enters a debug loop generating gigabytes, `maxsize` rotates immediately before `/var` fills up! |

---

#### 2. Microsoft Defender for Endpoint Logrotate (`/etc/logrotate.d/mdatp`)

#### 🧠 The Architectural Challenge: Endpoint Security Log Bloat
Microsoft Defender for Endpoint (`mdatp`) runs continuous real-time antivirus, memory inspection, and network socket monitoring daemons (`wdavdaemon`). In high-throughput production environments (e.g., reverse proxies, database clusters, build agents), `mdatp` generates gigabytes of packet inspection traces into `/var/opt/microsoft/mdatp/log/wdavdaemon.log`.
- **Rookie "Fix":** Stopping or killing `mdatp` to free disk.
- **Enterprise Security Violation:** Disabling `mdatp` flags immediate Sev-1 SOC alerts, removes endpoint compliance, and leaves the server vulnerable to zero-day exploits.
- **Enterprise SRE Solution:** Configure strict logrotate with `copytruncate` and a tighter `maxsize 50M` cap.

```bash
cat << 'EOF' > /etc/logrotate.d/mdatp
/var/opt/microsoft/mdatp/log/*.log {
    # Frequency: Evaluated daily by system logrotate
    daily
    
    # Retention Count: Retain 5 rotated generations (caps historical storage to ~250MB)
    rotate 5
    
    # Storage Optimization: Gzip compress (.gz) historical traces
    compress
    
    # Safety Buffer: Postpone compression of the newest archive by 1 cycle
    delaycompress
    
    # Resiliency: Do not throw errors if logs haven't initialized yet
    missingok
    
    # Efficiency: Skip rotation if the log file is empty
    notifempty
    
    # ZERO-DOWNTIME ROTATION: Copy and truncate active log in-place
    # (Microsoft wdavdaemon keeps running without dropping real-time protection!)
    copytruncate
    
    # EMERGENCY OVERRIDE: Force immediate rotation at 50MB (strict ceiling)
    maxsize 50M
}
EOF
```

---

#### 🔍 MDATP Directive Breakdown & Production Impact Analysis:

| Directive | Technical Mechanism | Production Impact & SRE Why |
|---|---|---|
| **`rotate 5`** | Limits stored historical archives to 5 generations. | **Prevents Security Storage Sprawl:** Caps total MDATP historical footprint to maximum `5 * 50MB = 250MB` uncompressed, `<40MB` compressed. |
| **`maxsize 50M`** | Triggers instant rotation when log hits 50MB regardless of hour. | **Early Warning Defense:** Security agents burst faster than standard apps during scan cycles; 50MB ceiling prevents saturating small `/var` partitions. |
| **`copytruncate`** | Zeros the live file descriptor without stopping the daemon. | **Continuous Protection:** Prevents security blind spots. Stopping `mdatp` even for 5 seconds breaches SOC Zero-Trust policies. |

---

#### 3. Qualys Cloud Agent Snapshot Auto-Cleaner (`/etc/cron.daily/qualys-snapshot-cleanup`)

#### 🧠 The Architectural Challenge: Orphaned Vulnerability Manifests
The Qualys Cloud Agent periodically captures full-system vulnerability snapshots and diagnostic manifest deltas (`.snap` files) under `/var/opt/qualys/qualys-cloud-agent/data/snapshots/`.
- If an agent fails to upload to the Qualys Cloud Gateway (e.g., temporary proxy timeout, firewall block), these un-uploaded snapshots accumulate locally.
- Each snapshot can be 20MB–100MB. Within days, hundreds of orphaned `.snap` files consume multiple gigabytes of `/var`.
- Because these are binary snapshots (not continuous logs), logrotate cannot manage them. An automated time-decay cleaner is required.

```bash
cat << 'EOF' > /etc/cron.daily/qualys-snapshot-cleanup
#!/usr/bin/env bash
set -euo pipefail

SNAPSHOT_DIR="/var/opt/qualys/qualys-cloud-agent/data/snapshots"
RETENTION_DAYS=7

# Remove vulnerability scan snapshot deltas older than 7 days
# '-mtime +7' finds files modified more than 7*24 hours ago
# '-delete' purges them directly at the kernel level without xargs overhead
if [ -d "$SNAPSHOT_DIR" ]; then
    find "$SNAPSHOT_DIR" -type f -name "*.snap" -mtime +"$RETENTION_DAYS" -delete 2>/dev/null || true
fi

exit 0
EOF

# Grant execute permissions so system cron runs it daily
chmod +x /etc/cron.daily/qualys-snapshot-cleanup

# Dry-run test all logrotate syntax to verify zero syntax errors
logrotate -d /etc/logrotate.conf
```

---

#### 🔍 Qualys Cleaner Breakdown & Production Impact Analysis:

| Component | Technical Mechanism | Production Impact & SRE Why |
|---|---|---|
| **`/etc/cron.daily/`** | Standard Red Hat daily execution queue (managed by `anacron`). | Ensures the cleanup runs daily even if the VM was temporarily stopped or suspended. |
| **`-mtime +7`** | Matches snapshot files modified > 7 days ago. | Preserves active scan manifests while pruning stale, non-uploaded orphan deltas. |
| **`-delete`** | Native `find` system call to unlink files. | **High Performance:** Avoids piping through `| xargs rm`, eliminating process fork overhead on millions of files. |

---

### Pillar 3: Rundeck Automated Execution History Purger

#### 🧠 The Architectural Challenge: Inode Exhaustion from Execution Records
Rundeck Workload Automation records every step of every scheduled and ad-hoc job into `/var/lib/rundeck/logs/rundeck/project-PROD-BATCH/job/<job-id>/execution-<id>.log`.
- In a microservices or financial batch infrastructure running thousands of jobs per hour, Rundeck generates **millions of tiny log and state files**.
- **The Sneaky Outage (Inode Exhaustion):** Even if each file is only 2KB and takes up minimal disk space, they consume **all available filesystem inodes** (`df -ih` hits 100%).
- Once inodes are exhausted, **no application can create a new file**, crashing the server even though `df -h` shows 80% free disk space!

```bash
cat << 'EOF' > /usr/local/bin/rundeck-cleaner.sh
#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="/var/lib/rundeck/logs/rundeck"
RETENTION_DAYS=14

echo "[$(date)] Starting Rundeck Execution Log Purge (> ${RETENTION_DAYS} days)..."

if [ -d "$LOG_DIR" ]; then
    # STEP 1: Purge execution log files older than 14 days
    find "$LOG_DIR" -type f -name "*.log" -mtime +"$RETENTION_DAYS" -delete
    
    # STEP 2: Purge empty job subdirectories left behind (reclaims dentry directory inodes!)
    find "$LOG_DIR" -type d -empty -delete
    
    echo "[$(date)] Cleanup completed successfully."
fi
EOF

# Grant execution rights to root owner only (prevents unprivileged tampering)
chmod 750 /usr/local/bin/rundeck-cleaner.sh

# Schedule daily automated execution at 02:00 AM via cron
echo "0 2 * * * root /usr/local/bin/rundeck-cleaner.sh > /dev/null 2>&1" > /etc/cron.d/rundeck-cleaner
```

---

#### 🔍 Rundeck Purger Breakdown & Production Impact Analysis:

| Step / Command | Technical Mechanism | Production Impact & SRE Why |
|---|---|---|
| **`find ... -name "*.log" -mtime +14 -delete`** | Searches recursively and deletes execution traces older than 14 days. | **Frees Both Blocks & Inodes:** Keeps execution logs compliant with 2-week enterprise audit windows while removing dead files. |
| **`find ... -type d -empty -delete`** | Unlinks empty leaf directories recursively. | **Reclaims Inode Tables:** In Linux, every directory consumes an inode. Cleaning thousands of empty job folders prevents inode exhaustion. |
| **`chmod 750`** | `rwxr-x---`: Read, write, execute for root; read/execute for root group; zero access for others. | **Enterprise Security Compliance:** Adheres to CIS Benchmark by locking administrative maintenance scripts against unauthorized tampering. |
| **`0 2 * * *`** | Runs nightly at 02:00 AM off-peak hours. | **Zero Resource Contention:** Executes during minimum server workload, avoiding I/O spikes during business hours. |

---

### 🤝 Cross-Team SRE Alignment & Questionnaires (Before Modifying Policies)

In a production enterprise, an SRE cannot unilaterally change logrotate retention without consulting the application and security owners. Use these battle-tested questionnaires to gather their exact requirements:

#### 📋 Questionnaire 1: To the Automation / Rundeck Platform Team
```text
Subject: RFC: Log Rotation & Retention Policy for Rundeck on RHEL Hosts

Hi Rundeck Team,

To prevent /var filesystem exhaustion while ensuring no loss of execution history, we are standardizing logrotate policies. Please confirm your requirements:

1. Local Service Log Retention:
   Current baseline: 7 days (rotate 7).
   Question: Do you need more than 7 days of local /var/log/rundeck/service.log, or are these forwarded to centralized SIEM/Splunk/Elastic?

2. Max Size Ceiling (maxsize):
   Current baseline: 100MB (maxsize 100M).
   Question: During month-end batch runs, is 100MB per file acceptable before triggering rotation?

3. Execution Step History (/var/lib/rundeck/logs/):
   Current baseline: 14 days purge via cron.
   Question: Does compliance mandate keeping raw step execution logs on local disk for longer than 14 days? If so, can we offload them to S3/Azure Blob Storage?

4. Zero-Downtime Verification:
   Question: Confirm your JVM logging appender handles in-place truncation (copytruncate) without requiring service restarts.
```

#### 📋 Questionnaire 2: To the InfoSec / SOC Team (MDATP Owner)
```text
Subject: RFC: Microsoft Defender for Endpoint (mdatp) Log Rotation Limits

Hi SecOps / SOC Team,

To maintain CIS Benchmark storage compliance and prevent telemetry bursts from saturating /var, we are implementing a managed logrotate policy for /var/opt/microsoft/mdatp/log/. Please confirm:

1. Local Telemetry Retention:
   Current baseline: 5 days (rotate 5).
   Question: What is the minimum local retention required for wdavdaemon.log, assuming real-time alerts are streamed to Microsoft Defender XDR?

2. Max Size Ceiling:
   Current baseline: 50MB (maxsize 50M).
   Question: Is a 50MB per-file ceiling acceptable before forcing rotation?

3. Crash Dump Retention (/var/opt/microsoft/mdatp/crashdumps/):
   Question: Can we configure an auto-purge policy for diagnostic core dumps older than 48 hours once telemetry is submitted to Microsoft?

4. Production Logging Level:
   Question: Is Defender configured for 'info' or 'debug'? If currently in debug, when will it be reverted to standard info logging?
```

---

#### 🎛️ How to Update Policies Based on Team Responses:

| Team Feedback | Action to Take in Logrotate Configuration |
|---|---|
| **Rundeck Team:** *"We need 14 days of local history."* | Change `rotate 7` ➔ `rotate 14` in `/etc/logrotate.d/rundeck`. |
| **Rundeck Team:** *"All logs are streamed to Splunk in real-time."* | Reduce `rotate 7` ➔ `rotate 3` (saves substantial disk space!). |
| **Rundeck Team:** *"Month-end jobs write 500MB logs."* | Increase `maxsize 100M` ➔ `maxsize 200M`. |
| **SOC Team:** *"Defender XDR stores all audit records in cloud."* | Keep `rotate 5` (or drop to `rotate 3`) with `maxsize 50M`. |
| **SOC Team:** *"Regulatory compliance mandates 30 days of raw local logs."* | Set `rotate 30`, keep `compress` enabled, and expand the LVM volume (`lvextend -r -L +10G /dev/mapper/rootvg-varlv`). |

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
