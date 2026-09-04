# 🔥 Production-Grade Linux Debugging Guide

> **Template Prompt:**
> *"Our production Node/VM is experiencing the following issue: [describe]. OS: [RHEL/Ubuntu]. Symptom: [paste alert or error]. Provide a step-by-step debugging approach with Linux CLI tools."*

---

## 🎯 Scenario: CPU Spike & High Load Average on Application Node

- **OS:** RHEL 9 / Ubuntu 22.04
- **Environment:** Production (Web/App Tier)
- **Symptom:** PagerDuty alert fires: `High Load Average > 15` and `CPU Usage > 95%`. Response latency has increased from `50ms` to `3000ms`.

---

## 📋 Phase 1: Triage — Assess the Panic Level

### Step 1.1 — How bad is the load? (`uptime`)

```bash
uptime
```

**Actual Output:**
```
 14:30:22 up 45 days, 12:04,  4 users,  load average: 22.45, 15.20, 8.10
```

> 🔴 **Red Flag:** Load average is `22.45` (1-min), `15.20` (5-min), `8.10` (15-min). The trend is spiking sharply upwards. Note: On a 4-core machine, anything above `4.00` is bottlenecking.

---

### Step 1.2 — Is it CPU, RAM, or I/O? (`top` / `htop`)

```bash
top -b -n 1 | head -n 15
```

**Actual Output:**
```
%Cpu(s): 85.2 us, 12.1 sy,  0.0 ni,  1.1 id,  1.4 wa,  0.0 hi,  0.2 si,  0.0 st
MiB Mem :  15892.2 total,    450.1 free,  14120.4 used,   1321.7 buff/cache
MiB Swap:   4096.0 total,    120.0 free,   3976.0 used.   1100.2 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
 7452 java      20   0   12.1g   9.2g  21.4m R 345.2  59.0 345:10.22 java -jar payment-api.jar
  921 root      20   0  210.5m  22.1m   9.4m R  45.0   0.1   1:22.45 journald
 7810 nginx     20   0  110.2m  15.5m   6.2m S  12.0   0.1   0:15.33 nginx -g daemon off;
```

> 🔴 **Red Flags Found:**
> 1. `%Cpu: 85.2 us` (User-space processes are pinning the CPU).
> 2. `wa: 1.4` (I/O Wait is low, meaning this is a pure CPU/Memory issue, not disk bottleneck).
> 3. `Swap limits:` Only 120MB free out of 4GB. The system is thrashing.
> 4. `PID 7452` (`java`) is consuming `345% CPU` (across >3 cores) and `59% MEM`.

---

## 📋 Phase 2: Deep Dive — Pinpoint the Rogue Process

### Step 2.1 — Check Thread-Level Utilization (`pidstat` / `top -H -p`)

We know PID 7452 is the issue. Let's see if it's one stuck thread (infinite loop) or many threads (high traffic).

```bash
pidstat -p 7452 -t 1 3
```

**Actual Output:**
```
14:32:01      TGID       TID    %usr   %system  %guest   %wait    %CPU   CPU  Command
14:32:02      7452         -  342.10     10.50    0.00    1.00  352.60     2  java
14:32:02         -      7489   99.00      0.50    0.00    0.00   99.50     0  |__java
14:32:02         -      7490   99.00      0.20    0.00    0.00   99.20     1  |__java
14:32:02         -      7491   99.50      0.60    0.00    0.00  100.10     3  |__java
```

> 🔴 **Observation:** Three specific Java threads (7489, 7490, 7491) are pinned at 100% CPU.

---

### Step 2.2 — Peek into the Process Execution (`strace` & logs)

What are those threads actively doing? Let's trace system calls.

```bash
strace -p 7489 -c
```

**Actual Output:**
```
% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 55.43    0.041234          15      2748       112 futex
 22.10    0.016432        2054         8           epoll_wait
 15.01    0.011156           5      2231           write
  7.46    0.005543           2      2771           read
------ ----------- ----------- --------- --------- ----------------
100.00    0.074365                  7758       112 total
```

If it's an infinite loop without I/O, `strace` might just hang. Next, check the Application logs:

```bash
journalctl -u payment-api --tail 50
```

**Actual Output:**
```
[ERROR] 2026-09-04 14:33:12 - java.lang.OutOfMemoryError: GC overhead limit exceeded
[WARN]  2026-09-04 14:33:12 - Garbage Collector taking > 98% of CPU time
```

> 🎯 **Root Cause Locked:** The JVM is out of heap memory. The CPUs are running at 100% specifically because the Garbage Collector (GC) is stuck in a death loop trying (and failing) to clear memory.

---

## 📋 Phase 3: The Fix (Incident Mitigation)

### Option A — Restart the Service (Drop the symptom)
The fastest way to restore latency for the API.

```bash
systemctl restart payment-api
```

### Option B — Capture Dump & Restart (Forensic approach)
Take a heap dump *before* killing it, so Devs can find the memory leak.

```bash
jmap -dump:live,format=b,file=/tmp/heapdump_panic.hprof 7452
systemctl restart payment-api
```

### Option C — Drop Traffic at Layer 4 (If un-killable)
If the Node is completely unresponsive, drain it from the AWS ALB / Nginx Load Balancer, or use `iptables` to block inbound ports so you can SSH in peace.

```bash
iptables -A INPUT -p tcp --dport 8080 -j DROP
```

---

## 📋 Phase 4: Prevention & Post-Mortem

### Root Cause
| Factor | Detail |
|--------|--------|
| **What broke** | High Load & CPU Spike to 100% |
| **Why it broke** | Application Memory Leak caused JVM Garbage Collector panic loop |
| **Result** | VM ran out of memory, began Swapping (disk thrashing), CPU pinned. |

### Better Configuration Checks
```bash
# 1. Disable swap for memory-intensive backend APIs (fail fast via OOM killer instead of thrashing)
swapoff -a
sed -i '/swap/d' /etc/fstab

# 2. Add resource limits via Systemd or Docker (cgroups)
# Edit /etc/systemd/system/payment-api.service
[Service]
MemoryLimit=10G
OOMScoreAdjust=500
```

---

## 🧠 Debug Decision Tree (Linux Performance Tuning)

```
Server Alert: High Response Latency
├── Check Load `uptime` → Load is High
│
├── Check Bottleneck `top`
│   ├── High `%us` (User CPU)
│   │   ├── Identify PID. Uses high MEM too? → Memory Leak / GC Death Spiral
│   │   └── Uses low MEM? → Infinite loop or heavy compute (regex, encryption)
│   │
│   ├── High `%wa` (I/O Wait)
│   │   ├── Disk is too slow or heavily saturated.
│   │   ├── Run `iostat -xz 1` or `iotop` to find the disk-heavy process.
│   │   └── Fix: Upgrade disk IOPS, optimize DB queries, separate log volumes.
│   │
│   └── High `%sy` (System/Kernel CPU)
│       └── Network interrupts or massive context switching. Check `dmesg -T`.
│
└── Check Load `uptime` → Load is NORMAL
    ├── The network logic is failing! 
    ├── Check DNS (`dig`, `nslookup`).
    ├── Check external dependencies (DB connection pools, external APIs down).
    └── Check local ports (`ss -tulnp`, `netstat`).
```
