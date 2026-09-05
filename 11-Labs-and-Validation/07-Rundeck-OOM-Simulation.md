# 🧪 Lab Simulation: Rundeck OOM & Systemd Cgroup Hardening

This lab provides step-by-step instructions to safely simulate a catastrophic memory leak (like our Rundeck disaster) and then implement a Systemd Cgroup limit to contain the blast radius.

> **Environment:** Do this in a free Ubuntu sandbox like [Killercoda](https://killercoda.com/playgrounds/scenario/ubuntu) so you don't crash your local PC!

---

## 💥 Phase 1: Creating the "Fake Rundeck" Memory Hog

First, we will create a simple script that acts like our runaway Rundeck Java process. It will rapidly consume memory until the server dies.

### Step 1.1: Write the Memory Hog Script
```bash
cat << 'EOF' > /tmp/fake-rundeck.py
#!/usr/bin/env python3
import time

print("🟢 Fake Rundeck Job Started: Allocating Memory...")
memory_hog = []

try:
    while True:
        # Allocate 10MB of memory chunks repeatedly
        memory_hog.append(' ' * 10 * 1024 * 1024)
        time.sleep(0.05)
except MemoryError:
    print("🔴 Python caught a memory error!")
EOF

chmod +x /tmp/fake-rundeck.py
```

---

## 🚨 Phase 2: The Unconstrained Disaster (Baseline)

Let's run this script wildly in the background without any Systemd rules, just like a poorly configured `/etc/init.d/` script.

### Step 2.1: Run the Script and Watch it Crash the OS
Run the script in the background, and dynamically watch your server's free memory plummet to 0.

```bash
# Run in background
/tmp/fake-rundeck.py &

# Watch memory immediately drain (Press Ctrl+C when the script gets killed)
watch -n 1 free -m
```

### Step 2.2: Verify the OS Kernel Panic (OOM)
When the `fake-rundeck.py` script is suddenly killed, it wasn't the script that decided to stop. The Linux Kernel stepped in with an emergency "OOM Kill" to save the OS from crashing.

```bash
# Check the exact Linux Kernel ring buffer logs
dmesg -T | grep -i -C 2 "Out of memory"
```
**Expected Output:**
```text
[Tue Sep 06 14:02:11 2026] Out of memory: Killed process 3842 (fake-rundeck.py) total-vm:4096000kB...
```
*Notice how dangerous this is: The system reached absolute zero bytes of memory before stepping in.*

---

## 🛡️ Phase 3: Implementing the Fix (Systemd Hardening)

To prevent the OS from ever being threatened again, we will wrap this "Rundeck" process tightly inside a Systemd `.service` file.

### Step 3.1: Create the Hardened Service File
We will restrict this massive script to a meager **50 Megabytes** of RAM using the modern Systemd `MemoryMax` limit (equivalent to `MemoryLimit` on older systems).

```bash
cat << 'EOF' | sudo tee /etc/systemd/system/fake-rundeck.service
[Unit]
Description=Rundeck Simulation Service

[Service]
Type=simple
ExecStart=/tmp/fake-rundeck.py

# 🛡️ THE FIX: Restrict memory globally through cgroups
MemoryMax=50M

# Log securely
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=fake-rundeck

[Install]
WantedBy=multi-user.target
EOF
```

### Step 3.2: Reload and Start the Hardened Service
```bash
sudo systemctl daemon-reload
sudo systemctl start fake-rundeck.service
```

---

## ✅ Phase 4: Verify the Hardening Worked!

### Step 4.1: Check Service Status
Wait about 3 seconds for the script to hit the 50MB limit, then check the status:

```bash
sudo systemctl status fake-rundeck.service
```
**Expected Output:**
```text
● fake-rundeck.service - Rundeck Simulation Service
     Active: failed (Result: oom-kill) since Tue 2026-09-06 14:10:00 UTC; 4s ago
    Process: 5104 ExecStart=/tmp/fake-rundeck.py (code=killed, signal=KILL)
```
> 🎉 **Success!** Look at `Result: oom-kill`. The Linux *Kernel* didn't kill this process—**Systemd's Cgroup** killed it gracefully as soon as it touched exactly 50MB. The host OS's 8GB of RAM was completely unaffected!

### Step 4.2: Audit the Cgroup Logs Safely
Check the pristine OS logs. You'll see Systemd cleanly logging the breach instead of a full kernel panic.

```bash
journalctl -u fake-rundeck.service --no-pager
```

## 🧠 Summary of What You Just Proved:
1. Running software loosely (`nohup`, `&`, `init.d`) allows memory leaks to steal 100% of host RAM, threatening other critical services (like SSH, Databases).
2. Creating a `.service` file with `MemoryMax=` invokes Linux **cgroups**, drawing a hard sandbox around the application.
3. When the Sandbox limit is breached, Systemd elegantly kills the containerized process while the Host continues operating normally!
