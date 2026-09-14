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

**Execute the heal manually:**
```bash
chmod +x disk_monitor.sh mail_notifier.py
./disk_monitor.sh
```

**Automating the heal via Cron (Every 5 minutes):**
To ensure the system heals itself automatically before Rundeck even realizes there is a storage issue, we can schedule the monitor script to check the drive every 5 minutes continuously:
```bash
# 1. Open the crontab editor
sudo crontab -e

# 2. Add this line to execute the monitor script every 5 minutes
*/5 * * * * /path/to/11-Labs-and-Validation/05-Rundeck-Log-Exhaustion/disk_monitor.sh >> /var/log/rundeck_disk_monitor.log 2>&1
```

---

## 🏛️ Phase 4: Enterprise Constraints & "Gotchas"

In a real enterprise production environment, running cleanup scripts blindly on `/var/log` will get you fired.

### ⚠️ Constraint 1: Active File Handles (The `rm -rf` trap)
You should **never** just run `rm -rf /var/log/app.log` if the application is still writing to it! 

**Why?** In Linux file systems, a file is only truly deleted when *both* its directory link is removed AND no active processes have it open (run `lsof` to see). If you `rm` a log file that Rundeck, Java, or Docker is currently streaming to, you only remove the name pointer. The OS keeps the data blocks allocated on the disk resulting in a "ghost file". The disk will still show 100% full, but you won't be able to see the file to delete it! Space is only reclaimed when you restart the application service.

**The SRE Fixes (Detailed Examples):**

👉 **Method 1: Safe In-Place Truncation (Emergency Response)**
If you are in the middle of a SEV-1 incident and need disk space *immediately* without crashing the app, empty the file natively. This keeps the active file handle completely intact:
```bash
# Safely clears the file content to 0 bytes instantly (The optimal SRE method)
> /var/log/rundeck/rundeck.log

# Alternative using the truncate command
truncate -s 0 /var/log/rundeck/rundeck.log
```

👉 **Method 2: Standard Log Rotation (`logrotate`)**
For long-term permanent fixes, SREs configure the Linux `logrotate` daemon to handle cutting, zipping, and managing files gracefully without manual bash scripts. 
*Example `/etc/logrotate.d/rundeck` configuration:*
```text
/var/log/rundeck/*.log {
    daily               # Rotate every day
    rotate 7            # Keep exactly 7 days of history
    compress            # gzip the rotated files natively
    missingok           # Don't error out if the file is missing
    copytruncate        # CRITICAL: Copies the file and truncates the original in place (prevents handle breaking!)
}
```

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
