# 🔄 SRE Lab: Advanced Logrotate System

**Scenario:** Standard OS components log heavily to `/var/log` (e.g., `boot.log`, `messages`, `secure`). Unchecked, these text files will grow infinitely until they crash the server. 

**Objective:** Deploy a custom application log stream and master the Linux `logrotate` service to strictly enforce log rotation, compression, and automated deletion sequences without dropping file handles.

---

## 🏛️ The Architecture of `logrotate`

`logrotate` is natively installed on RHEL and CentOS. It is executed automatically every day by a standard Linux `cron` job located in `/etc/cron.daily/logrotate`.

It utilizes a split architecture:
1. **The Global Config (`/etc/logrotate.conf`)**: Defines the base configurations (e.g., rotate logs weekly by default, keep 4 weeks of backlogs, compress them).
2. **The Modular Drop-ins (`/etc/logrotate.d/`)**: SREs and package managers drop individual application specs here (e.g., `/etc/logrotate.d/nginx`, `/etc/logrotate.d/syslog`). These override the global config explicitly for that application.

Before beginning, check your version:
```bash
logrotate --version
```

---

## 🛠️ Execution & Labs

We have provided three bash scripts to safely automate and demonstrate this architecture.

### 1. Scaffolding the Application ([`setup_lab.sh`](setup_lab.sh))
Execute `./setup_lab.sh` to scaffold the environment. 
* It creates a dummy application root at `/var/log/my_app/my_app.log`.
* It automatically deploys our aggressive config into `/etc/logrotate.d/my_app`.

**Let's analyze the configuration we injected (The Magic of Logrotate):**
Unlike the previous Rundeck Lab where we had to write custom bash scripts with `find -mtime` to zip files and run scheduled crontabs to delete them, `logrotate` handles ALL of this natively through two simple parameters:

```text
/var/log/my_app/*.log {
    size 10M            # Trigger rotation if file hits 10 Megabytes (ignores daily cron limit)
    rotate 4            # THE CLEANUP: Keep a maximum of 4 historical logs. The 5th is permanently deleted automatically!
    compress            # THE ZIPPING: GZIP all rotated logs natively (No manual bash scripts required!)
    delaycompress       # Delay compression of yesterday's log until tomorrow's rotation. (Great for active debugging).
    missingok           # Do not throw alerts if no log file exists.
    notifempty          # Do not rotate if the file is completely empty.
    create 0644 root root # Create the brand-new log file immediately so the app has somewhere to write.
}
```

### 2. Simulating Log Growth ([`simulate_growth.sh`](simulate_growth.sh))
Since `logrotate` usually only happens daily via Cron, we need to artificially break the thresholds to witness it.
Execute `./simulate_growth.sh`. 
* This blasts 15 Megabytes of Base64 encoded entropy into `/var/log/my_app/my_app.log`, explicitly breaching our `size 10M` rule.

### 3. The SRE Diagnostics ([`test_rotation.sh`](test_rotation.sh))
Whenever an SRE modifies a configuration file in `/etc/logrotate.d/`, they **must** test it. If the syntax is broken, logs stop rotating globally!

Run `./test_rotation.sh` which executes two critical commands:

**Diagnostic 1: The Dry-Run (`-d`)**
```bash
man logrotate
logrotate -d /etc/logrotate.d/my_app
```
*   The `-d` flag tells logrotate to read the file, calculate what it *would* do, print the output, but actually touch nothing on disk.

**Diagnostic 2: The Force Execution (`-f`)**
```bash
logrotate -vf /etc/logrotate.d/my_app
```
*   Because `logrotate` records its last execution in a state file (`/var/lib/logrotate/logrotate.status`), it usually refuses to run twice in one day. 
*   The `-f` (force) flag overrides the state file, instructing logrotate to execute immediately regardless of time. This is critical for lab testing size thresholds!

---

## 🏢 Phase 4: Advanced Enterprise SRE Configurations

In a production Kubernetes or Fortune 500 bare-metal environment, the standard logrotate config isn't enough. Here are three highly advanced enterprise configurations you **must** know for interviews and architectures.

### 🛡️ Enterprise Scenario 1: The Multi-Worker Trap (`sharedscripts`)
**The Problem:** NGINX or Apache might have 50 different log files (`access.log`, `error.log`, `ssl.log`). If you tell `logrotate` to gracefully reload the NGINX daemon in a `postrotate` block, it will reload NGINX **50 times** (once for every single file it rotated), destroying your CPU!
**The SRE Fix:** Inject `sharedscripts`. This forces `logrotate` to wait until *all* logs are rotated, and then executes the daemon reload exactly **once**.

```text
/var/log/nginx/*.log {
    daily
    rotate 14
    sharedscripts       # CRITICAL: Ensures postrotate executes ONLY ONCE for all 50 files.
    postrotate
        /bin/systemctl reload nginx.service > /dev/null 2>/dev/null || true
    endscript
}
```

### 📅 Enterprise Scenario 2: SOC2 Compliance Auditing (`dateext`)
**The Problem:** Standard logrotate renames files sequentially (`app.log.1`, `app.log.2`). When an auditor asks for the logs from "August 12th", correlating `.14.gz` is a nightmare.
**The SRE Fix:** Inject `dateext`. Instead of indexing via numbers, logrotate magically stamps the exact rotation date into the file string! (`app.log-20270812.gz`).

```text
/var/log/my_app/*.log {
    daily
    dateext             # Morph 'app.log.1' into 'app.log-20270812'
    dateformat -%Y%m%d  # Standardize the timestamp format
}
```

### 🚢 Enterprise Scenario 3: Log Shipping & Legal Retention (`olddir` & `maxage`)
**The Problem:** You must keep logs for 90 days for legal compliance, but you absolutely cannot afford them cluttering up the primary application directory while FileBeat is trying to ship them to Elasticsearch.
**The SRE Fix:** Use `olddir` to automatically move them to a separate deep-storage network mount, and `maxage 90` to strictly enforce a physical 90-day execution order.

```text
/var/log/my_app/*.log {
    daily
    rotate 365          # Keep 365 copies maximum
    maxage 90           # OVERRIDE: Delete anything strictly older than 90 days for compliance!
    olddir /mnt/deep_archive/logs/  # Move the gzipped logs off the fast SSD to a cheaper NFS mount block
}
```
👉 **[View the Complete SRE Guide: Securely Mounting Azure File Share (NFS 4.1) for Logrotate](Azure-NFS-Setup.md)**

### 📩 Enterprise Scenario 4: Emailing the Archives (`mail`)
**The Problem:** You must permanently delete logs to save space, but upper management mandates a hardcopy of all logs be shipped to an auditing email address before deletion.
**The SRE Fix:** Inject the `mail` parameter. Logrotate will automatically calculate which `.gz` file is about to cross the threshold for deletion, extract it, attach it to an email using the local `/usr/bin/mail` agent, and dispatch it exactly one millisecond before `rm -rf` executes.

```text
/var/log/my_app/*.log {
    daily
    rotate 5
    mail audit-logs@yourcompany.com   # Eject the 6th archive to this email before deletion!
}
```
👉 **[View the Complete SRE Guide: Enabling Logrotate's `mail` Directive (Postfix MTA Setup)](Mail-Setup.md)**

### ⚖️ Enterprise Scenario 5: `size` vs `maxsize`
These two directives seem identical, but function entirely differently in production!
*   **`size 100M`**: Forcefully rotates the log *only* if it is larger than 100MB. It completely ignores cron schedules like `daily` or `weekly`.
*   **`maxsize 100M`**: Enforces time intervals (e.g. `weekly`), rotating exactly once a week, *UNLESS* the log breaches 100MB early, in which case it rotates instantly to save the server from crashing.

---

## 🧹 Phase 5: Modern Systemd Binary Logs (`journalctl`)

While `logrotate` handles raw `text` files, modern Linux OS's use `systemd` which writes core kernel and daemon logs in a raw **Binary format** inside `/var/log/journal/`. Logrotate **cannot** read or clean these!

To prevent your binary journaling system from exhausting disk space, SREs employ the explicit `vacuum` commands:
```bash
# 1. Check exactly how much disk space your binary systemd logs are taking up globally
journalctl --disk-usage

# 2. Hard-delete any binary logs older than 7 days
sudo journalctl --vacuum-time=7d

# 3. Aggressively delete older binary logs until the total folder is shrunk to 500MB
sudo journalctl --vacuum-size=500M
```

---

## 🔁 Verification
After running the test script, execute `ls -lh /var/log/my_app`.

1. `my_app.log` will be entirely empty (0 bytes).
2. `my_app.log.1` will exist uncompressed (15MB) due to the `delaycompress` parameter.
3. If you run the `simulate` and `test` scripts **again**, `my_app.log.1` will natively morph into `my_app.log.2.gz` and shrink to practically nothing via compression, proving the rotation cycle is fully functional!

---

## 🧽 Phase 6: Lab Teardown
Once you are done experimenting with configurations, you must remove the `.conf` file so it doesn't perpetually trigger via crontab in the background of your system!

Execute the teardown script to wipe the configurations safely:
```bash
chmod +x cleanup_lab.sh
./cleanup_lab.sh
```

---

## ⚠️ Production Gotchas & Interview Traps
*   **The Gotcha (Log Bloat between Crons):** The `size 10M` parameter does *not* mean the file is instantly cut the exact second it hits 10MB! Because `logrotate` only wakes up once per day (usually 2:00 AM via cron), if a runaway application writes 50 Gigabytes of data in 4 hours, it will still crash the server before `logrotate` ever gets a chance to awake and verify the `size` rule! For hyper-active logs, you must manually run logrotate via a custom 5-minute cronjob (as demonstrated in the previous Rundeck lab).
*   **The Interview Trap:** "An engineer deleted a 50GB log file via `rm -rf`, but the disk is still 100% full. Why?"
    *   *The SRE Answer:* The application (like Docker or Tomcat) still holds an active file handle to the inode. The name pointer is gone, creating a "Ghost File". You must restart the application to free the inode, or use `> file.log` / `copytruncate` to properly empty it in-place.
*   **Copytruncate CPU Overhead:** `copytruncate` involves reading the entire file and writing a raw copy to disk before truncating. On an extremely hot 50GB log file, this can cause massive I/O spikes and bring down an undersized Virtual Machine. 

## 🔍 SRE Debugging (Where to look when it fails)
If your Linux disk is exhausted and you suspect logrotate failure:

1.  **Read the daily cron execution logs:**
    ```bash
    cat /var/log/cron | grep logrotate
    ```
2.  **Ensure you didn't create a syntax error in your config:**
    ```bash
    # SREs ALWAYS run this after modifying drop-in configs
    logrotate -d /etc/logrotate.conf
    ```
3.  **Check for "Ghost Files" taking up unseen space:**
    ```bash
    sudo lsof | grep deleted
    ```
