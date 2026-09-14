# 🚨 SRE Lab: Rundeck Disk Exhaustion & Auto-Remediation

**Scenario:** A rogue application (or highly verbose logging mechanism) is rapidly filling up the `/var/log` directory on a Linux virtual machine hosting Rundeck. As the disk hits 100% capacity, OS daemons crash, databases lock up, and Rundeck fails to execute automation.
**Objective:** Deploy Rundeck, forcefully consume the disk, and trigger a self-healing bash script to alert the team (SEV-1 Email) and automatically archive/gzip the oldest log files to restore production stability.

---

## 🛠️ Phase 1: Install Free Rundeck on YUM-Based Linux (RHEL 8/9, AlmaLinux)

Before simulating the crash, we must install Rundeck cleanly.

```bash
# 1. Install Java 11 (Rundeck requirement)
sudo yum install -y java-11-openjdk-devel

# 2. Add the official Rundeck YUM repository
curl -s https://packages.rundeck.com/pagerduty/rundeck/api/repo/rpm | sudo bash

# 3. Install Rundeck Community Edition
sudo yum install -y rundeck

# 4. Start and enable the Rundeck service natively
sudo systemctl enable --now rundeckd

# 5. Verify Rundeck is healthy before the attack
sudo systemctl status rundeckd
```
*Note: Rundeck operates on port `4440` by default. You can hit `http://<VMS-IP>:4440` (admin/admin).*

---

## 💥 Phase 2: The Attack (Simulating Disk Exhaustion)

When `/var/log` fills up unexpectedly (e.g., a looping application dumping stack traces), it eventually consumes all available blocks or inodes. When `du` hits 100%:
*   `rundeckd` will fail to write to `rundeck.audit.events.log` and crash.
*   The underlying database (H2 or MySQL) will lock horizontally, failing all jobs.

**Run the simulation script to starve the server:**
```bash
# Make the generator executable
chmod +x generate_logs.sh

# Run it. This will forcefully generate hundreds of Megabytes/Gigabytes of logs.
./generate_logs.sh

# Validate the damage
df -h /
```

---

## 🩹 Phase 3: The Auto-Remediation Sequence

To fix this, we've deployed a self-healing script `disk_monitor.sh` coupled with a Python notification mechanism `mail_notifier.py`. 

**The Remediation Logic:**
1.  **Metric Extraction:** Uses `df -h / | awk` to cleanly extract the integer percentage of disk capacity.
2.  **Threshold Detection:** If capacity > 80%, the crisis response triggers.
3.  **SEV-1 Dispatch:** Executes the Python script to send a beautifully styled HTML email bounding into your inbox using your `smtp-relay.brevo.com` service.
4.  **Graceful Compression:** Executes `find /var/log/rundeck_lab_sim -type f -name "*.log" -exec gzip {} \+`. This targets raw logs and archives them in place, massively reducing their footprint (up to 95% reduction depending on entropy) without deleting the underlying evidence for post-mortems!

**Execute the heal:**
```bash
chmod +x disk_monitor.sh mail_notifier.py
./disk_monitor.sh
```

---

## 🏛️ Phase 4: Enterprise Constraints & "Gotchas"

In a real enterprise production environment, running cleanup scripts blindly on `/var/log` will get you fired.

### ⚠️ Constraint 1: Active File Handles (The `rm -rf` trap)
You should **never** just run `rm -rf /var/log/app.log` if the application is still writing to it! 
**Why?** In Linux, if a process has an open file handle, deleting the file removes the pointer, but **does not free the disk space**. The disk will still show 100% full until the process (like Rundeck or Docker) is manually restarted.
* **The SRE Fix:** Always use log rotation (`logrotate`), or safely truncate the file in place via `> /var/log/app.log`.

### ⚠️ Constraint 2: Inode Exhaustion
Sometimes `df -h` shows 50% capacity, but applications are still crashing with "No space left on device".
**Why?** A rogue process generated millions of tiny 1-byte files, consuming all the filesystem's **Inodes**, even though raw space remains.
* **The SRE Fix:** Check inode capacity natively using `df -i`.

### 🧹 Phase 5: Long-Term Enterprise Cleanup (Automated CronJob)
While `disk_monitor.sh` dynamically compresses the logs to save space, we still need to permanently delete those `.gz` archives eventually, otherwise the disk will still fill up over a span of months. 

We deployed `cleanup_logs.sh` to target `.gz` files older than 7 days and successfully `rm` them. This script is designed to run automatically in the background using Linux **Cron**.

**How to schedule the automated cleanup via Cron:**
```bash
# 1. Make the script executable
chmod +x cleanup_logs.sh

# 2. Open the crontab editor for the root user (or Rundeck user)
sudo crontab -e

# 3. Add the following line to execute the cleanup completely autonomously every night at 2:00 AM
0 2 * * * /path/to/11-Labs-and-Validation/05-Rundeck-Log-Exhaustion/cleanup_logs.sh >> /var/log/rundeck_cleanup.log 2>&1
```

---

### 💥 Phase 6: Lab Teardown
Restore your workspace back to zero:
```bash
sudo rm -rf /var/log/rundeck_lab_sim
sudo crontab -l | grep -v 'cleanup_logs.sh' | sudo crontab - # Remove just the cronjob
sudo systemctl stop rundeckd
sudo yum remove -y rundeck
```
