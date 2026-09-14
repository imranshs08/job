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

### 1. Scaffolding the Application (`setup_lab.sh`)
Execute `./setup_lab.sh` to scaffold the environment. 
* It creates a dummy application root at `/var/log/my_app/my_app.log`.
* It automatically deploys our aggressive config into `/etc/logrotate.d/my_app`.

**Let's analyze the configuration we injected:**
```text
/var/log/my_app/*.log {
    size 10M            # Trigger rotation if file hits 10 Megabytes (ignores daily cron limit)
    rotate 4            # Keep a maximum of 4 historical logs. The 5th is permanently deleted.
    compress            # GZIP all rotated logs natively.
    delaycompress       # Delay compression of yesterday's log until tomorrow's rotation. (Great for active debugging).
    missingok           # Do not throw alerts if no log file exists.
    notifempty          # Do not rotate if the file is completely empty.
    create 0644 root root # Create the brand-new log file immediately so the app has somewhere to write.
}
```

### 2. Simulating Log Growth (`simulate_growth.sh`)
Since `logrotate` usually only happens daily via Cron, we need to artificially break the thresholds to witness it.
Execute `./simulate_growth.sh`. 
* This blasts 15 Megabytes of Base64 encoded entropy into `/var/log/my_app/my_app.log`, explicitly breaching our `size 10M` rule.

### 3. The SRE Diagnostics (`test_rotation.sh`)
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

## 🔁 Verification
After running the test script, execute `ls -lh /var/log/my_app`.

1. `my_app.log` will be entirely empty (0 bytes).
2. `my_app.log.1` will exist uncompressed (15MB) due to the `delaycompress` parameter.
3. If you run the `simulate` and `test` scripts **again**, `my_app.log.1` will natively morph into `my_app.log.2.gz` and shrink to practically nothing via compression, proving the rotation cycle is fully functional!

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
