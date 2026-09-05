# 🔥 Production-Grade Debugging Guide: Rundeck Systemd Hardening & OOM Recovery

## 🎯 Scenario
- **Cluster/Environment:** Enterprise Bare-Metal Linux Node (Ubuntu 22.04 LTS / RHEL 8)
- **Namespace:** Operating System Level (`/etc/rundeck` & `/var/lib/rundeck`)
- **Symptom:** A massive Rundeck (Java-based) automation job ran a concurrent script across 5,000 nodes, causing the Rundeck process to exhaust all host memory. Because it was running via a legacy unconstrained init script, it consumed 100% of the host RAM, triggering a catastrophic Out-Of-Memory (OOM) kernel panic that brought down the entire Linux automation server.

## 🧠 Core Concepts: Rundeck & Java Memory Constraints
Before debugging, understand how underlying technologies restrict Java applications:
* **Java Heap Space (`-Xmx`/`-Xms`):** Limits how much memory the Java Virtual Machine (JVM) *itself* is allowed to use internally. If exceeded, the app throws `java.lang.OutOfMemoryError` but the host OS remains safe.
* **Systemd Cgroups (`MemoryLimit`):** A strict Linux kernel boundary. If Rundeck's Java process forces the OS beyond this limit (due to off-heap memory or excessive threads), the Linux kernel mercilessly kills it (OOM Killer) to protect the server.
* **Unit File (`rundeckd.service`):** The declarative systemd configuration file that wraps the application in a secure sandbox, preventing it from executing as `root`.

---

## 📋 Phase 1: Triage — Confirm the Problem
Immediate commands to inspect what killed the automation node and state of the app:

```bash
# 1. Check if the Rundeck Java process is running and its resource footprint
ps -eo pid,user,%cpu,%mem,cmd | grep rundeck

# 2. Check total system memory availability on the host
free -h
```

**Actual Output:**
```text
rundeck   8732  99.9  96.5 /usr/bin/java -Xmx8g -Xms8g -jar rundeck.war
```
> 🔴 **Red Flag:** Rundeck is consuming 96.5% of host memory. The Java Heap is set to 8GB (`-Xmx8g`), but the underlying Linux OS only has 8GB of total RAM! The Java off-heap overhead is completely choking the host OS.

## 📋 Phase 2: Deep Dive — Logs & Resource Analysis
Confirm in the kernel ring buffer that the OS previously crashed due to Rundeck.

```bash
# Search kernel logs for the exact process the Linux OOM Killer terminated
dmesg -T | grep -i -C 2 "Out of memory"

# Check standard system logs for termination signals
journalctl -k | grep -i "killed process"
```

**Actual Output:**
```text
[Tue Sep 06 01:45:10 2026] Out of memory: Killed process 8732 (java) total-vm:9844304kB, anon-rss:8192450kB, file-rss:0kB, shmem-rss:0kB
[Tue Sep 06 01:45:10 2026] oom_reaper: reaped process 8732 (java), now anon-rss:0kB, file-rss:0kB, shmem-rss:0kB
```
> 🔴 **Red Flag:** The Linux Kernel invoked the OOM Killer specifically on PID 8732 (Java/Rundeck) because its memory footprint exceeded physical bounds with no systemd restrictions in place.

## 📋 Phase 3: The Fix

### Option A: The Fastest Mitigation (JVM Tuning)
Temporarily modify the Rundeck profile to drastically lower the Java Heap so the OS can breathe, then restart.
```bash
sudo vim /etc/rundeck/profile
# Change: RDECK_JVM="-Xmx2048m -Xms2048m"
sudo systemctl restart rundeckd
```

### Option B: The Proper Fix (Hardened Systemd Service File)
To permanently secure the application, we implement absolute cgroup limits at the OS level so a runaway job can never crash the parent host again.

```bash
sudo vim /etc/systemd/system/rundeckd.service
```

**File Contents (`rundeckd.service`):**
```ini
[Unit]
Description=Rundeck Automation Job Scheduler
After=network.target syslog.target multi-user.target

[Service]
# Security: Run as a non-privileged user, NEVER ROOT
User=rundeck
Group=rundeck

# Environment and Execution
EnvironmentFile=/etc/rundeck/profile
WorkingDirectory=/var/lib/rundeck
ExecStart=/usr/bin/java ${RDECK_JVM} -jar /var/lib/rundeck/bootstrap/rundeckd.war

# Resilience: Auto-restart on crash (e.g. if killed by OOM)
Restart=always
RestartSec=10s

# Hardware Hardening: Absolute Kernel Limits
# If JVM `-Xmx` fails, systemd guarantees it won't exceed 3GB RAM total
MemoryLimit=3G
CPUQuota=200%

# Security Hardening: File System Sandboxing
ProtectSystem=full
ProtectHome=true
NoNewPrivileges=true

# Logging: Send stdout/stderr securely to Journald
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=rundeckd

[Install]
WantedBy=multi-user.target
```

## 📋 Phase 5: Verify the Fix
Reload the systemd daemon to ingest the new cgroup constraints and start Rundeck.

```bash
# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable rundeckd
sudo systemctl start rundeckd

# Verify systemd cgroups have successfully sandboxed the application
sudo systemctl status rundeckd
```

**Actual Output:**
```text
● rundeckd.service - Rundeck Automation Job Scheduler
     Loaded: loaded (/etc/systemd/system/rundeckd.service; enabled)
     Active: active (running) since Tue 2026-09-06 02:48:10 UTC; 45s ago
   Main PID: 10452 (java)
      Tasks: 42
     Memory: 2.1G (limit: 3.0G)   <-- 🟢 OS KERNEL LIMIT OFFICIALLY ENFORCED
        CPU: 18.4s
     CGroup: /system.slice/rundeckd.service
             └─10452 /usr/bin/java -Xmx2048m -Xms2048m -jar rundeckd.war

Sep 06 02:48:15 node-1 rundeckd[10452]: [INFO ] BootStrap - Starting Rundeck...
```

## 📋 Phase 6: Root Cause Summary & Prevention

| What broke | Why it broke | Exit Code |
| :--- | :--- | :--- |
| Node Kernel Panic | Rundeck JVM Heap (`-Xmx8g`) was equal to physical OS hardware limits. Java off-heap overhead pushed it over the edge. | `137` (SIGKILL by OS OOM) |
| Systemd Exposure | The service was lacking foundational `MemoryLimit` cgroup restrictions to confine it. | N/A |

### Prevention Checklist:
- [x] Hardcode `MemoryLimit=3G` inside the `.service` file.
- [x] Configure Java JVM limits (`-Xmx2g`) to always be *smaller* than the Systemd limit to allow overhead buffer space.
- [x] Ensure `User=rundeck` and `NoNewPrivileges=true` to prevent horizontal privilege escalation if a Rundeck job is compromised.

### 🛑 What happens when Systemd Limit is breached?
When the `MemoryLimit` boundary is hit, the impact is divided into two areas:
1. **The Server Impact (🟢 Highly Positive):** The host OS is saved. The kernel doesn't panic. SSH stays up, and other databases on the same server are completely unaffected because the memory theft was contained in a cgroup sandbox.
2. **The App Impact (🔴 Highly Destructive):** Systemd executes the Rundeck process with a violent `SIGKILL` (Exit 137). It does not let Rundeck gracefully save data or finish database transactions, resulting in immediate downtime and aborted jobs. 
*That is why we configure `Restart=always` to recover immediately, and set our Java `-Xmx` limit lower than the Systemd limit so Java can exit gracefully on its own first (as a `java.lang.OutOfMemoryError`) before Systemd has to use a `SIGKILL`!*

## 🧠 Debug Decision Tree

```text
Rundeck Web UI Down / Timeout?
├── Are there OOM logs in dmesg? (dmesg -T | grep OOM)
│   ├── YES → Check Java Heap Profile (/etc/rundeck/profile)
│   │   ├── Heap is 100% of OS RAM? → Reduce -Xmx to 70% of System RAM.
│   │   └── Heap is low, but OS crashed? → Set systemd MemoryLimit= to block OS theft.
│   └── NO → Go to Systemctl Status
│
├── systemctl status rundeckd
│   ├── Active (running) → App is running. Check Nginx reverse proxy logs.
│   ├── Failed (Code=exited, Status=1) → Java crash (Check JVM stdout in journalctl).
│   │   └── journalctl -u rundeckd | tail -n 50 (Look for exceptions).
│   └── Failed (Code=killed, Signal=SYS) → Systemd Security blocked it (ProtectSystem).
```

## ⚡ Quick Reference Commands

```bash
# Fully reload Systemd and sync changes
sudo systemctl daemon-reload
sudo systemctl restart rundeckd

# View live Rundeck logs flowing through Journald securely
journalctl -u rundeckd -f

# Emergency check for Java running processes and heap arguments
ps -ef | grep java | grep rundeck

# Check dynamic CGroup limits applied by Systemd
systemctl show rundeckd -p MemoryLimit
```
