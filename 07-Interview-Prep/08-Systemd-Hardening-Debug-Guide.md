# 🔥 Production-Grade Systemd Debugging & Hardening Guide

## 🎯 Scenario
- **Cluster/Environment:** Bare-Metal Linux Node (Ubuntu 22.04 LTS)
- **Namespace:** Operating System Level (`/opt/app`)
- **Symptom:** A massive Go API binary running in the background suffered a memory leak. Because it was running loosely without constraints (e.g., via `nohup` or a basic init script), it consumed 100% of the host RAM, triggering a catastrophic Out-Of-Memory (OOM) kernel panic that brought down the entire Linux node.

## 🧠 Core Concepts: Systemd & Hardening Fundamentals
Before debugging, ensure you understand these fundamental Linux mechanics:
* **Systemd:** The modern init system (PID 1) used by almost all Linux distributions (Ubuntu, RHEL) to manage boot processes, services, and daemons.
* **Unit File (`.service`):** A declarative configuration file placed in `/etc/systemd/system/` that tells systemd precisely *how* to run, restart, and restrict an application.
* **Cgroups (Control Groups):** A foundational Linux kernel feature seamlessly integrated into systemd. It is the mechanism that actually enforces the `MemoryLimit` and `CPUQuota` restrictions.
* **Journald:** The native logging system for systemd. It automatically captures all standard output (`stdout`) and standard error (`stderr`) from your service without external log rotation tools.

---

## 📋 Phase 1: Triage — Confirm the Problem
Immediate commands to inspect what killed the node and what the current state of the application is:

```bash
# Check if the process is currently running and who owns it
ps aux | grep /opt/app/binary

# Check system memory consumption
free -m
```

**Actual Output:**
```text
root      4592  99.9  95.4 3459020 3100450 ?   Sl   10:14   4:10 /opt/app/binary
```
> 🔴 **Red Flag:** The Go API is running as `root` (massive security risk) and consuming 95.4% of total system memory (3.1 GB out of 3.2 GB).

## 📋 Phase 2: Deep Dive — Logs & Resource Analysis
Dig into the Linux kernel ring buffer to confirm if this process previously caused a node crash via the OOM Killer.

```bash
# Search kernel logs for OOM events
dmesg -T | grep -i "out of memory"

# Check standard system logs
journalctl -k | grep -i "killed process"
```

**Actual Output:**
```text
[Tue Sep 06 01:14:22 2026] Out of memory: Killed process 4592 (binary) total-vm:4194304kB, anon-rss:3300450kB, file-rss:0kB, shmem-rss:0kB
```
> 🔴 **Red Flag:** The Linux Kernel explicitly killed the Go API because it exhausted all available RAM. There were no limits placed on the process.

## 📋 Phase 3: The Fix

### Option A: The Fastest/Inline Mitigation (Temporary)
Immediately restart the binary with a strict shell-level memory limit using `ulimit`.
```bash
ulimit -v 2097152; nohup su -c '/opt/app/binary' api_user &
```

### Option B: The Proper Fix (Hardened Systemd Service File)
To permanently secure the application, we create a strict systemd service file with built-in auto-restart, logging, and rigid resource constraints.

```bash
sudo vim /etc/systemd/system/go-api.service
```

**File Contents (`go-api.service`):**
```ini
[Unit]
Description=Massive Go API Application
After=network.target

[Service]
# Security: Run as a non-privileged user, NEVER ROOT
User=api
Group=api

# Execution
Type=simple
WorkingDirectory=/opt/app
ExecStart=/opt/app/binary

# Resilience: Auto-restart on crash
Restart=always
RestartSec=5s

# Hardening: Strict Resource Constraints
MemoryLimit=2G
CPUQuota=150%

# Hardening: Security Sandboxing
ProtectSystem=full
ProtectHome=true
NoNewPrivileges=true

# Logging: Send stdout/stderr natively to Journald
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=go-api

[Install]
WantedBy=multi-user.target
```

### Option C: The Emergency Rollback
If the hardened systemd file fails permissions immediately (e.g., the app actually requires root to bind to port 80), fallback to the original state while routing through a proxy like Nginx:
```bash
sudo systemctl stop go-api
sudo /opt/app/binary &  # Restart manually until port 80 dependencies are resolved
```

## 📋 Phase 5: Verify the Fix
Reload the systemd daemon to read the new file, start the service, and verify its strict constraints.

```bash
# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable go-api
sudo systemctl start go-api

# Verify it is restricted and logging properly
sudo systemctl status go-api
```

**Actual Output:**
```text
● go-api.service - Massive Go API Application
     Loaded: loaded (/etc/systemd/system/go-api.service; enabled)
     Active: active (running) since Tue 2026-09-06 02:20:10 UTC; 15s ago
   Main PID: 8901 (binary)
      Tasks: 6
     Memory: 45.1M (limit: 2.0G)   <-- 🟢 LIMIT SUCCESSFULLY APPLIED
        CPU: 12ms
     CGroup: /system.slice/go-api.service
             └─8901 /opt/app/binary

Sep 06 02:20:10 node-1 go-api[8901]: Server started on port 8080
```

## 📋 Phase 6: Root Cause Summary & Prevention

| What broke | Why it broke | Exit Code |
| :--- | :--- | :--- |
| Whole Linux Node Crashed | Go API suffered a memory leak and had no resource restrictions. | `137` (SIGKILL by OS OOM-Killer) |
| Severe Security Risk | Application was executed as the `root` user manually. | N/A |

### Prevention Checklist:
- [x] Configure systemd `MemoryLimit=2G` to confine the application using cgroups.
- [x] Create a dedicated unprivileged user (`sudo useradd -r -s /bin/false api`).
- [x] Use `StandardOutput=syslog` so logs go securely to `journalctl` instead of filling up a `.txt` file endlessly.

## 🧠 Debug Decision Tree

```text
Service Down / Node Unresponsive?
├── Are there OOM logs in dmesg? (dmesg -T | grep OOM)
│   ├── YES → Check process limits
│   │   ├── Limits exist? → App has massive leak, page developers.
│   │   └── No limits? → Wrap process in Systemd with MemoryLimit=.
│   └── NO → Go to Systemctl Status
│
├── systemctl status go-api
│   ├── Active (running) → Check network/firewall (ufw status).
│   ├── Failed (Code=exited, Status=1) → App crashed on startup.
│   │   └── journalctl -u go-api -n 50 → Check App stack trace.
│   └── Failed (Code=killed, Signal=SYS) → Systemd Sandboxing blocked it (e.g., ProtectSystem=true).
```

## ⚡ Quick Reference Commands

```bash
# Core Systemd lifecycle commands
sudo systemctl daemon-reload
sudo systemctl start go-api
sudo systemctl status go-api
sudo systemctl restart go-api

# Debugging Systemd Logs
journalctl -u go-api -f            # Follow live logs
journalctl -u go-api --since "1 hour ago"

# Checking active cgroup limits
systemctl show go-api -p MemoryLimit
```
